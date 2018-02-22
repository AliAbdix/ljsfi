#!/usr/bin/env python
#####################################################################
# AGIS infosys tool via AGIS                                        #
# LJSFi Framework 1.9.0                                             #
# Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it> - 20130318 #
#####################################################################

__version__ = "$Revision: 1.0 $"[11:-1]

__HELP__="""LJSFi infosys tool %s.
Usage: ljsf-infosys [OPTION]

Options:
  --help                       Display this help and exit.
  --cache                      Use cache engine
  --cache-timeout=<seconds>    Cache timeout, in seconds
  --dbhost=<DB hostname>       DB Hostname
  --dbname=<DB name>           DB name
  --dbpass=<DB password>       DB password
  --dbconf=<DB config file>    ALternate DB config file
  --debug | -d                 Debug mode
  --flavor | -f <grid-flavor>  Select only <grid-flavor> resources
                               (comma separated list of names)
  --gen-parser                 Generate parser
  --info | -i                  Show the resource info
  --is-cvmfs                   Select only CVMFS sites
  --jdl <filename>             Use <filename> to match resources
  --no-cvmfs                   Select only non CVMFS sites
  --list-match | -m            List matching resources
  --list-resource              List all resources
  --panda-resource | -r <res>  Use the panda resource <res>
  --show-last-update           Show the last database update time
  --status | -s status>        Select sites with status <status>
  --tags=<CSV tag list>        Tag list to match (use ! to negate)
  --tier-level | -l <1|2|3>    Specify the Tier level of the sites
  --type <resource-type>       Select only <resource-type> resources
  --update                     Update infosys tables
  --verbose | -v               Verbose mode

Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>.
"""

try:
    import json
except:
    import simplejson as json
import os, sys, commands
import time
import getopt
import MySQLdb
import string
import re
try:
    import hashlib
except:
    import md5 as hashlib
try:
    import memcache
except:
    memcache = None

__TMPFILE__     = "/tmp/ljsf-broker-info.%s.tmp" % os.getpid()
__AGIS_SITE_INFO__ = "http://atlas-agis-api.cern.ch/request/pandaqueue/query/list/index.php?json&preset=schedconf.all&vo_name=atlas"
__AGIS_TAG_INFO__  = "http://atlas-agis-api.cern.ch/jsoncache/list_presource_sw.schedconf.json"
__CURL_EXEC__ = "curl -S --connect-timeout 60 -o '%s' '%s'"

__SELECT__   = {
                 "ALL_SITES"      : "SELECT DISTINCT(name) FROM panda_resource p"
                ,"TAGGED_SITES"   : "SELECT DISTINCT(name) FROM panda_resource p"
                ,"TAGS_IN_SITE"   : "SELECT DISTINCT(tag) AS tag FROM release_data rd"
                ,"FRESH_DATA"     : "SELECT COUNT(*) FROM info"
                ,"PANDA_RESOURCE" : "SELECT DISTINCT(p.atlas_site), p.site, p.name, p.tier_level, ros.osname, ros.osversion, ros.osrelease, f.name AS flavor, rt.name AS rtype, p.is_cvmfs, p.is_default, p.corecount, p.lfcpath, p.lfcprodpath, p.sepath, p.seprodpath FROM panda_resource p"
                ,"ALL_RESOURCE"   : "SELECT DISTINCT(p.name) FROM panda_resource p"
                ,"PARSER"         : "SELECT rt.name AS rtype, p.lfcpath, p.lfcprodpath, p.sepath, p.seprodpath FROM panda_resource p"
                ,"DB_LAST_UPDATE" : "SELECT last_update FROM info"
               }
__JOIN__     = {
                 "TAGGED_SITES"   : "JOIN release_stat rs ON rs.resourcefk = p.ref JOIN release_data rd ON rs.releasefk = rd.ref"
                ,"TAGS_IN_SITE"   : "JOIN release_stat rs ON rs.releasefk = rd.ref JOIN panda_resource p ON rs.resourcefk = p.ref"
                ,"PANDA_RESOURCE" : "JOIN resource_os ros ON p.osfk = ros.ref JOIN resource_flavor f ON p.flavorfk = f.ref JOIN resource_type rt ON p.typefk = rt.ref"
                ,"PARSER"         : "JOIN resource_type rt ON p.typefk = rt.ref"
               }
__CRITERIA__ = {
                 "TAG"            : "tag = '%s'"
                ,"PANDA_RESOURCE" : "p.name = '%s'"
                ,"IS_CVMFS"       : "p.is_cvmfs = 1"
                ,"NO_CVMFS"       : "p.is_cvmfs = 0"
                ,"STATUS"         : "p.statusfk = (SELECT ref FROM status WHERE name='%s')"
                ,"NOT_STATUS"     : "p.statusfk <> (SELECT ref FROM status WHERE name='%s')"
                ,"TIER_LEVEL"     : "p.tier_level = %s"
                ,"FRESH_DATA"     : "last_update >= DATE_SUB(NOW(),INTERVAL 480 MINUTE)"
                ,"RESFLAVOR"      : "p.flavorfk IN (SELECT ref FROM resource_flavor WHERE name IN (%s))"
                ,"RESTYPE"        : "p.typefk = (SELECT ref FROM resource_type WHERE name='%s')"
                ,"PARSER"         : "p.name = '%s'"
               }
__ORDERBY__  = {
                 "ALL_SITES"    : "name"
                ,"TAGGED_SITES" : "name"
                ,"TAGS_IN_SITE" : "tag"
                ,"ALL_RESOURCE" : "name"
               }
__GROUPBY__  = {
                 "PANDA_RESOURCE" : "atlas_site, site, name, flavor"
                ,"PARSER"         : "rtype, lfcpath, lfcprodpath, sepath, seprodpath"
               }
__REPORT__   = {
                 "PANDA_RESOURCE" : "ATLAS_SITENAME=%s\nSITENAME=%s\nRESOURCE=%s\nTIER_LEVEL=%s\nOSNAME=%s\nOSVERSION=%s\nOSRELEASE=%s\nGRID=%s\nSITETYPE=%s\nIS_CVMFS=%s\nIS_DEFAULT=%s\nCORECOUNT=%s\nLFCPATH=%s\nLFCPRODPATH=%s\nSEPATH=%s\nSEPRODPATH=%s"
                ,"ALL_RESOURCE"   : "%s"
                ,"PARSER"         : "s#@INFOSYS_SITETYPE@#%s#g\ns#@INFOSYS_LFCPATH@#%s#g\ns#@INFOSYS_LFCPRODPATH@#%s#g\ns#@INFOSYS_SEPATH@#%s#g\ns#@INFOSYS_SEPRODPATH@#%s#g"
                ,"DB_LAST_UPDATE" : "%s"
               }
__VALUES__   = {
                 "PANDA_RESOURCE" : (("atlassitename",0),("sitename",1),("resource",2),("osname",3),("osversion",4),("osrelease",5),("grid",6),("sitetype",7),("is_cvmfs",8),("lfcpath",9),("lfcprodpath",10),("sepath",11),("seprodpath",12))
                ,"PARSER"         : (("@INFOSYS_SITETYPE@",0),("@INFOSYS_LFCPATH@",1),("@INFOSYS_LFCPRODPATH@",2),("@INFOSYS_SEPATH@",3),("@INFOSYS_SEPRODPATH@",4))
               }
__UPDATE_TIMESTAMP__ = "INSERT INTO info (ref,last_update) VALUES (1, '%s') ON DUPLICATE KEY UPDATE last_update=VALUES(last_update)"
short_options = "dhf:ij:l:mr:s:uv"
long_options = ["cache", "cache-timeout=", "dbhost=", "dbname=", "dbpass=", "dbconf=", "debug", "flavor=", "gen-parser", "help", "info", "is-cvmfs", "jdl=", "list-match", "list-resource", "no-cvmfs", "panda-resource=", "show-last-update", "status=", "tags=", "tier-level=", "type=", "update", "verbose"]

class ljsfInfosys:
    debug = False
    dbhost = None
    dbname = None
    dbuser = None
    dbpass = None
    dbconf = None
    db = None
    statusID = {}
    restypeID = {}
    resflavorID = {}
    cloudID = {}
    pandaResourceID = {}
    cmtconfigID = {}
    releaseID = {}
    requireTag = None
    excludeTag = None
    verbose = False
    isCVMFS = None
    status = None
    tags = []
    tierLevel = None
    pandaResource = None
    rtype = None
    rflavor = None
    mode = None
    noout = False
    ljsfDBURL = None
    memcacheServer = None
    memcacheClient = None
    cache = False
    cacheTimeout = 300


    def __init__(self):
        patt="http[s]*://([^/:]*)"
        if (os.environ.has_key("LJSFDBURL")): self.ljsfDBURL = os.environ["LJSFDBURL"]
        else: self.ljsfDBURL = "atlas-install.roma1.infn.it"
        m=re.search(patt,self.ljsfDBURL)
        if (m):
            self.memcacheServer = "%s:11211" % m.group(1)
            if (memcache):
                try:
                    self.memcacheClient = memcache.Client([self.memcacheServer], debug=0)
                except:
                    self.memcacheClient = None


    def setNoout(self,mode):
        self.noout = mode

    def setupDB(self):
        # Open the database
        dbconn = None
        if (self.debug): print "Opening the DB connection"
        if (self.dbhost and self.dbname and self.dbuser and self.dbpass):
            dbconn = MySQLdb.connect(host=self.dbhost,user=self.dbuser,passwd=self.dbpass,db=self.dbname)
        else:
            if (self.dbconf):
                db_conf = ("%s" % self.dbconf)
            else:
                db_conf = ("%s/.my-broker.cnf" % os.environ["CONFPATH"])
            if (self.debug): print "Using %s" % db_conf
            if (os.environ.has_key('LJSFBRKDBNAME')):
                db_name = os.environ["LJSFBRKDBNAME"]
            else:
                db_name = "ljsf_infosys"
                dbconn = MySQLdb.connect(read_default_file=db_conf,db=db_name)
                dbconn.autocommit(False)
            if (self.debug): print "DB connection opened"
        return dbconn

    def queryDB(self, query):
        if (not self.db): self.db = self.setupDB()
        try:
            cursor = self.db.cursor()
            cursor.execute(query)
        except (AttributeError, MySQLdb.OperationalError):
            self.db = self.setupDB()
            cursor = self.db.cursor()
            cursor.execute(query)
        return cursor

    def readDB(self,query,cache=None):
        if (cache == None): cache = self.cache
        key = None
        res = None
        if (cache and self.memcacheClient):
            key = hashlib.md5(query).hexdigest()
            res = self.memcacheClient.get(key)
            if (res and self.debug): print "Using cached data"
        if (not res):
            cursor = self.queryDB(query)
            res = cursor.fetchall()
            cursor.close()
            if (res and cache and self.memcacheClient and key):
                self.memcacheClient.set(key, res, self.cacheTimeout)
        return res


    def getStatusID(self, status):
        if (not self.statusID):
            query = "SELECT ref, name FROM status"
            res = self.readDB(query)
            for row in res: self.statusID[row[1]] = int(row[0])
        if (not self.statusID.has_key(status)):
            query = "INSERT INTO status SET name='%s'" % status
            cursor = self.queryDB(query)
            self.db.commit()
            cursor.close()
            query = "SELECT ref FROM status WHERE name='%s'" % status
            res = self.readDB(query)
            if (res): self.statusID[status] = int(res[0][0])
        if (self.statusID.has_key(status)):
            return self.statusID[status]
        return None

    def getResflavorID(self, resflavor):
        if (not self.resflavorID):
            query = "SELECT ref, name FROM resource_flavor"
            res = self.readDB(query)
            for row in res: self.resflavorID[row[1]] = int(row[0])
        if (not self.resflavorID.has_key(resflavor)):
            query = "INSERT INTO resource_flavor SET name='%s'" % resflavor
            cursor = self.queryDB(query)
            self.db.commit()
            cursor.close()
            query = "SELECT ref FROM resource_flavor WHERE name='%s'" % resflavor
            res = self.readDB(query)
            if (res): self.resflavorID[resflavor] = int(res[0][0])
        if (self.resflavorID.has_key(resflavor)):
            return self.resflavorID[resflavor]
        return None

    def getRestypeID(self, restype):
        if (not self.restypeID):
            query = "SELECT ref, name FROM resource_type"
            res = self.readDB(query)
            for row in res: self.restypeID[row[1]] = int(row[0])
        if (not self.restypeID.has_key(restype)):
            query = "INSERT INTO resource_type SET name='%s'" % restype
            cursor = self.queryDB(query)
            self.db.commit()
            cursor.close()
            query = "SELECT ref FROM resource_type WHERE name='%s'" % restype
            res = self.readDB(query)
            if (res): self.restypeID[restype] = int(res[0][0])
        if (self.restypeID.has_key(restype)):
            return self.restypeID[restype]
        return None

    def getCloudID(self, cloud):
        if (not self.cloudID):
            query = "SELECT ref, name FROM cloud"
            res = self.readDB(query)
            for row in res: self.cloudID[row[1]] = int(row[0])
        if (not self.cloudID.has_key(cloud)):
            query = "INSERT INTO cloud SET name='%s'" % cloud
            cursor = self.queryDB(query)
            self.db.commit()
            cursor.close()
            query = "SELECT ref FROM cloud WHERE name='%s'" % cloud
            res = self.readDB(query)
            if (res): self.cloudID[cloud] = int(res[0][0])
        if (self.cloudID.has_key(cloud)):
            return self.cloudID[cloud]
        return None

    def getCmtconfigID(self, cmtconfig):
        if (not self.cmtconfigID):
            query = "SELECT ref, id FROM release_cmtconfig"
            res = self.readDB(query)
            for row in res: self.cmtconfigID[row[1]] = int(row[0])
        if (not self.cmtconfigID.has_key(cmtconfig)):
            query = "INSERT INTO release_cmtconfig SET id='%s'" % cmtconfig
            cursor = self.queryDB(query)
            self.db.commit()
            cursor.close()
            query = "SELECT ref FROM release_cmtconfig WHERE id='%s'" % cmtconfig
            res = self.readDB(query)
            if (res): self.cmtconfigID[cmtconfig] = int(res[0][0])
        if (self.cmtconfigID.has_key(cmtconfig)):
            return self.cmtconfigID[cmtconfig]
        return None

    def getPandaResourceID(self, panda_resource):
        if (not self.pandaResourceID):
            query = "SELECT ref,name FROM panda_resource_tmp"
            res = self.readDB(query)
            for row in res:
                if (not self.pandaResourceID.has_key(row[1])): self.pandaResourceID[row[1]] = []
                self.pandaResourceID[row[1]] += [int(row[0])]
        if (not self.pandaResourceID.has_key(panda_resource)):
            query = "SELECT ref FROM panda_resource_tmp WHERE name='%s'" % panda_resource
            res = self.readDB(query)
            if (res):
                if (not self.pandaResourceID.has_key(panda_resource)): self.pandaResourceID[panda_resource] = []
                self.pandaResourceID[panda_resource] += [int(res[0][0])]
        if (self.pandaResourceID.has_key(panda_resource)):
            return self.pandaResourceID[panda_resource]
        return []

    def getReleaseID(self, release, major_release, project, cmtconfig, tag):
        if (tag):
            reltag = tag
        else:
            reltag = "%s_%s_%s" % (project,release.replace(".","_"),cmtconfig)
        if (not self.releaseID):
            query = "SELECT ref, release_name, major_release, project, cmtconfigfk, tag FROM release_data"
            if (self.debug): print query
            res = self.readDB(query)
            for row in res:
                n = row[1]
                p = row[3]
                c = row[4]
                t = row[5]
                if (t): reltag_tmp = t
                else: reltag_tmp = "%s_%s_%s" % (p,n.row.replace(".","_"),c)
                self.releaseID[reltag_tmp] = int(row[0])
        if (not self.releaseID.has_key(reltag)):
            query = "INSERT INTO release_data (release_name, major_release, project, cmtconfigfk, tag) VALUES ('%s', '%s', '%s', '%s', '%s')" % (release, major_release, project, self.getCmtconfigID(cmtconfig), reltag)
            if (self.debug): print query
            cursor = self.queryDB(query)
            self.db.commit()
            cursor.close()
            query = "SELECT ref FROM release_data WHERE release_name='%s' AND project='%s' AND cmtconfigfk=%d" % (release, project, self.getCmtconfigID(cmtconfig))
            if (self.debug): print query
            res = self.readDB(query)
            if (res): self.releaseID[reltag] = int(res[0][0])
        if (self.releaseID.has_key(reltag)):
            return self.releaseID[reltag]
        return None

    def update(self):
        # Get the json files from AGIS
        try:
            if (self.debug or self.verbose): print "Getting AGIS site data from %s" % __AGIS_SITE_INFO__
            s,o = commands.getstatusoutput(__CURL_EXEC__ % (__TMPFILE__, __AGIS_SITE_INFO__))
            if (s != 0):
                print o
                raise
            if (self.debug or self.verbose): print "Reading AGIS site data from %s" % __TMPFILE__
            agis_site_info = open(__TMPFILE__,'r')
            json_site_data = agis_site_info.read()
            agis_site_info.close()
            if (self.debug or self.verbose): print "Loading AGIS site data from %s" % __TMPFILE__
            agis_site_data = json.loads(json_site_data)
            os.remove(__TMPFILE__)
            if (self.debug or self.verbose): print "AGIS site data loaded from %s" % __TMPFILE__
        except:
            print "Cannot get AGIS site data"
            raise

        try:
            if (self.debug or self.verbose): print "Getting AGIS tags from %s" % __AGIS_TAG_INFO__
            s,o = commands.getstatusoutput(__CURL_EXEC__ % (__TMPFILE__, __AGIS_TAG_INFO__))
            if (s != 0):
                print o
                raise
            if (self.debug or self.verbose): print "Reading AGIS tags from %s" % __TMPFILE__
            agis_tag_info = open(__TMPFILE__,'r')
            json_tag_data = agis_tag_info.read()
            agis_tag_info.close()
            if (self.debug or self.verbose): print "Loading AGIS tags from %s" % __TMPFILE__
            agis_tag_data = json.loads(json_tag_data)
            os.remove(__TMPFILE__)
            if (self.debug or self.verbose): print "AGIS tags loaded from %s" % __TMPFILE__
        except:
            print "Cannot get AGIS tags"
            raise

        tables = ['panda_resource', 'compute_resource','release_stat']
        if (self.debug or self.verbose): print "Loading data into the infosys DB"
        try:
            if (len(agis_site_data) > 0):
                cursor = self.queryDB("SHOW TABLES")
                tableList = []
                for (table_name,) in cursor: tableList.append(table_name)
                cursor.close()
                for table in tables:
                    tmptable = "%s_tmp" % table
                    if (tmptable in tableList):
                        if (self.verbose): print "Dropping table %s" % tmptable
                        cursor = self.queryDB("DROP TABLE IF EXISTS `%s`" % tmptable)
                        cursor.close()
                    cursor = self.queryDB("CREATE TABLE %s LIKE %s" % (tmptable, table))
                    cursor.close()

            indx = 0
            siteIDs = agis_site_data.keys()
            siteIDs.sort()
            if (self.verbose): print "Adding Panda and Compute resources"
            for siteID in siteIDs:
                site_data = agis_site_data[siteID]
                site = site_data['panda_site']
                atlas_site = site_data['atlas_site']
                cloud = site_data['cloud']
                if (site_data['corecount']): corecount = site_data['corecount']
                else: corecount = 1
                is_analysis = site_data['is_analysis']
                is_production = site_data['is_production']
                is_cvmfs = site_data['is_cvmfs']
                is_default = site_data['is_default']
                lfcpath = site_data['lfcpath']
                lfcprodpath = site_data['lfcprodpath']
                sepath = site_data['sepath']
                seprodpath = site_data['seprodpath']
                if (not is_cvmfs): is_cvmfs = False
                tier_level = site_data['tier_level']
                name = site_data['panda_resource']
                queue = site_data['queue']
                status = site_data['status']
                if (site_data.has_key("cloud_for_panda")):
                    cloud_name = site_data['cloud_for_panda']
                else:
                    cloud_name = cloud
                if (cloud_name.upper() in ["US","OSG"]):
                    resflavor = "OSG"
                elif (site_data['system'].upper() == "ARC"):
                    resflavor = "ARC"
                else:
                    resflavor = "EGEE"
                restype = site_data['type']
                cloudfk = self.getCloudID(cloud)
                statusfk = self.getStatusID(status)
                restypefk = self.getRestypeID(restype)
                resflavorfk = self.getResflavorID(resflavor)
                query = "INSERT INTO panda_resource_tmp (atlas_site, site, name, queue, cloudfk, is_analysis, is_production, is_cvmfs, is_default, tier_level, corecount, statusfk, flavorfk, typefk, lfcpath, lfcprodpath, sepath, seprodpath) VALUES ('%s', '%s', '%s', '%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, '%s', '%s', '%s', '%s')" % (atlas_site, site, name, queue, cloudfk, is_analysis, is_production, is_cvmfs, is_default, tier_level, corecount, statusfk, resflavorfk, restypefk, lfcpath, lfcprodpath, sepath, seprodpath)
                if (self.debug): print query
                cursor = self.queryDB(query)
                cursor.close()
                query = "SELECT ref FROM panda_resource_tmp WHERE atlas_site='%s' AND site='%s' AND name='%s' AND queue='%s'" % (atlas_site, site, name, queue)
                cursor = self.queryDB(query)
                res = cursor.fetchall()
                if (res): panda_resourcefk = res[0][0]
                else: panda_resourcefk = None
                cursor.close()
                indx += 1

                if (panda_resourcefk):
                    for resource in site_data['queues']:
                        ce_endpoint = resource['ce_endpoint']
                        query = "INSERT INTO compute_resource_tmp (ce_endpoint, panda_resourcefk) VALUES ('%s', %d)" % (ce_endpoint, panda_resourcefk)
                        if (self.debug): print query
                        cursor = self.queryDB(query)
                        cursor.close()
            if (indx > 0): self.db.commit()

            if (self.verbose): print "Adding Releases"
            atd_indx = 0
            atd_ins_indx = 0
            atd_dupl_indx = 0
            atd_lock = 0
            atd_tot = len(agis_tag_data)
            query = ''
            rescheck = {}
            for tag_data in agis_tag_data:
                atd_indx += 1
                if (self.verbose):
                    atd_percdone = 100 * atd_indx / atd_tot
                    if (atd_percdone % 5 == 0):
                        if (atd_lock == 0):
                            print "   >>> %d%% done [%d rows] [%d duplicates]" % (atd_percdone, atd_ins_indx, atd_dupl_indx)
                            atd_lock = 1
                    else:
                        atd_lock = 0
                cmtconfig = tag_data["cmtconfig"]
                major_release = tag_data["major_release"]
                project = tag_data["project"]
                release = tag_data["release"]
                tag = tag_data["tag"]
                if (not tag): tag = "NULL"
                releasefk = self.getReleaseID(release, major_release, project, cmtconfig, tag)
                panda_resourcefk = self.getPandaResourceID(tag_data["panda_resource"])
                if (self.debug): print "%s" % panda_resourcefk
                if (releasefk):
                    for resourcefk in panda_resourcefk:
                        atd_ins_indx += 1
                        if (not rescheck.has_key(resourcefk)): rescheck[resourcefk] = []
                        if (releasefk not in rescheck[resourcefk]):
                            rescheck[resourcefk].append(releasefk)
                        else:
                            atd_dupl_indx += 1
                            if (self.debug): print "   --- Duplicate release [%d] in resource [%d]" % (resourcefk, releasefk)
                        if (query == ''):
                            query = "INSERT IGNORE INTO release_stat_tmp (resourcefk, releasefk) VALUES (%d, %d)" % (resourcefk, releasefk)
                        else:
                            query += ",(%d, %d)" % (resourcefk, releasefk)
                        if (atd_ins_indx % 10000 == 0):
                            if (self.debug): print query
                            cursor = self.queryDB(query)
                            cursor.close()
                            query = ''
                        if (atd_ins_indx % 100000 == 0):
                            if (self.verbose): print "   --> Commit data"
                            self.db.commit()
            if (query != ''):
                if (self.debug): print query
                if (self.verbose): print "Finalizing loop"
                cursor = self.queryDB(query)
                cursor.close()
            if (self.verbose): print "Commit release data"
            if (atd_indx > 0): self.db.commit()
            if (self.verbose): print "Number of tags processed: %d [%d rows] [%d duplicates]" % (atd_indx, atd_ins_indx, atd_dupl_indx)

            if (indx > 0):
                if (self.verbose): print "Renaming tables"
                query_tbl = []
                serial = time.strftime("%Y%m%d%H%M%S")
                for table in tables:
                    query_tbl.append(" %s TO %s_%s" % (table, table, serial))
                    query_tbl.append(" %s_tmp TO %s" % (table, table))
                query = "RENAME TABLE %s" % string.join(query_tbl,",")
                cursor = self.queryDB(query)
                cursor.close()
                for table in tables:
                    cursor = self.queryDB("DROP TABLE %s_%s" % (table, serial))
                    cursor.close()
                updtsqry = __UPDATE_TIMESTAMP__ % time.strftime("%Y-%m-%d %H:%M:%S")
                if (self.verbose): print "UPDATE> %s" % updtsqry
                cursor = self.queryDB(updtsqry)
                self.db.commit()
                cursor.close()
        except:
            self.db.rollback()
            raise

    def parser(self, resource=None):
        resparser = []
        if (resource and not self.pandaResource): self.pandaResource = resource
        if (self.pandaResource):
            criteria = __CRITERIA__["PARSER"] % self.pandaResource
            query = "%s %s WHERE %s GROUP BY %s" % (__SELECT__["PARSER"],__JOIN__["PARSER"], criteria, __GROUPBY__["PARSER"])
            if (self.debug): print query
            res = self.readDB(query)
            for row in res:
                if (not self.noout): print __REPORT__["PARSER"] % row
                for fieldInfo in __VALUES__["PARSER"]:
                    resparser.append((fieldInfo[0], row[fieldInfo[1]]))
        return resparser

    def info(self, resource=None):
        resinfo = {}
        if (resource and not self.pandaResource): self.pandaResource = resource
        if (self.pandaResource):
            criteria = __CRITERIA__["PANDA_RESOURCE"] % self.pandaResource
            query = "%s %s WHERE %s GROUP BY %s" % (__SELECT__["PANDA_RESOURCE"],__JOIN__["PANDA_RESOURCE"], criteria,__GROUPBY__["PANDA_RESOURCE"])
            res = self.readDB(query)
            for row in res:
                if (not self.noout): print __REPORT__["PANDA_RESOURCE"] % row
                for fieldInfo in __VALUES__["PANDA_RESOURCE"]:
                    resinfo[fieldInfo[0]] = row[fieldInfo[1]]
        return resinfo

    def lastUpdate(self):
        lastupd = None
        query = "%s" % (__SELECT__["DB_LAST_UPDATE"])
        res = self.readDB(query)
        for row in res:
            lastupd = __REPORT__["DB_LAST_UPDATE"] % row
            if (not self.noout): print lastupd
        return lastupd

    def listResource(self):
        criteria = []
        if (self.isCVMFS != None):
            if (self.isCVMFS): criteria.append(__CRITERIA__["IS_CVMFS"])
            else:              criteria.append(__CRITERIA__["NO_CVMFS"])
        if (self.status):
            if (self.status[0] == "!"):
                criteria.append(__CRITERIA__["NOT_STATUS"] % self.status[1:])
        if (self.tierLevel):   criteria.append(__CRITERIA__["TIER_LEVEL"] % self.tierLevel)
        if (self.rtype):       criteria.append(__CRITERIA__["RESTYPE"] % self.rtype)
        if (self.rflavor):
            rflavor_list = []
            for rflav in self.rflavor.split(","): rflavor_list.append("'%s'" % rflav)
            criteria.append(__CRITERIA__["RESFLAVOR"] % string.join(rflavor_list,","))
        if (criteria):
            query = "%s WHERE %s ORDER BY %s" % (__SELECT__["ALL_RESOURCE"],string.join(criteria," AND "),__ORDERBY__["ALL_SITES"])
        else:
            query = "%s ORDER BY %s" % (__SELECT__["ALL_RESOURCE"],__ORDERBY__["ALL_RESOURCE"])
        if (self.debug): print query
        res = self.readDB(query)
        for row in res: print __REPORT__["ALL_RESOURCE"] % row

    def listMatch(self):
        infosys = {}
        query = "%s WHERE %s" % (__SELECT__["FRESH_DATA"],__CRITERIA__["FRESH_DATA"])
        newdatares = self.readDB(query)
        if (newdatares and newdatares[0][0] >= 1):
            criteria = []
            if (self.isCVMFS != None):
                if (self.isCVMFS): criteria.append(__CRITERIA__["IS_CVMFS"])
                else:              criteria.append(__CRITERIA__["NO_CVMFS"])
            if (self.status):
                if (self.status[0] == "!"):
                    criteria.append(__CRITERIA__["NOT_STATUS"] % self.status[1:])
                else:
                    criteria.append(__CRITERIA__["STATUS"] % self.status)
            if (self.tierLevel):   criteria.append(__CRITERIA__["TIER_LEVEL"] % self.tierLevel)
            if (self.rtype):       criteria.append(__CRITERIA__["RESTYPE"] % self.rtype)
            if (self.rflavor):
                rflavor_list = []
                for rflav in self.rflavor.split(","): rflavor_list.append("'%s'" % rflav)
                criteria.append(__CRITERIA__["RESFLAVOR"] % string.join(rflavor_list,","))
            if (criteria):
                query = "%s WHERE %s ORDER BY %s" % (__SELECT__["ALL_SITES"],string.join(criteria," AND "),__ORDERBY__["ALL_SITES"])
            else:
                query = "%s ORDER BY %s" % (__SELECT__["ALL_SITES"],__ORDERBY__["ALL_SITES"])
            if (self.debug): print query
            res = self.readDB(query)
            for (name,) in res: infosys[name] = 0
            rank = 0
            for tag in self.tags:
                #sys.stderr.write("TAG> %s\n" % tag)
                if (tag[0] == "!"):
                    tagcriteria = __CRITERIA__["TAG"] % tag[1:]
                else:
                    rank += 1
                    tagcriteria = __CRITERIA__["TAG"] % tag
                query = "%s %s WHERE %s ORDER BY %s" % (__SELECT__["TAGGED_SITES"],
                                                        __JOIN__["TAGGED_SITES"],
                                                        tagcriteria,
                                                         __ORDERBY__["TAGGED_SITES"])
                if (self.debug): print query
                tagres = self.readDB(query)
                for (name,) in tagres:
                    if infosys.has_key(name):
                        if (tag[0] == "!"):
                            del infosys[name]
                            if (self.debug): print "Exclude resource %s" % name
                        else:
                            infosys[name] += 1
                            if (self.debug): print "Raise rank on resource %s" % name
        bkeys = infosys.keys()
        bkeys.sort()
        for bkey in bkeys:
            if (infosys[bkey] == rank): print bkey

infosys = ljsfInfosys()

if __name__ == "__main__":
    # Get the CLI options
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                     short_options,
                     long_options,
                     )
    except getopt.GetoptError:
        # Print the help
        print __HELP__
        sys.exit(-1)
    for cmd, arg in opts:
        if (cmd in ('--help',) or cmd in ('-h',)):
            print __HELP__
            sys.exit()
        elif cmd in ('--cache',):
            infosys.cache = True
        elif cmd in ('--cache-timeout',):
            infosys.cacheTimeout = int(arg)
        elif (cmd in ('--dbconf',)):
            infosys.dbconf = arg
        elif (cmd in ('--dbhost',)):
            infosys.dbhost = arg
        elif (cmd in ('--dbname',)):
            infosys.dbname = arg
        elif (cmd in ('--dbuser',)):
            infosys.dbuser = arg
        elif (cmd in ('--dbpass',)):
            infosys.dbpass = arg
        elif (cmd in ('--debug',) or cmd in ('-d',)):
            infosys.debug = True
        elif (cmd in ('--flavor',) or cmd in ('-f',)):
            infosys.rflavor = arg
        elif (cmd in ('--gen-parser',)):
            mode = "parser"
        elif (cmd in ('--info',) or cmd in ('-i',)):
            mode = "info"
        elif (cmd in ('--is-cvmfs',)):
            infosys.isCVMFS = True
        elif (cmd in ('--jdl',) or cmd in ('-j',)):
            jobdef = arg
            jobdef_file = open(jobdef)
            jobdef_data = json.load(jobdef_file)
            jobdef_file.close()
            if (jobdef_data["JobDef"].has_key("Tags")): infosys.tags = jobdef_data["JobDef"]["Tags"]
            if (jobdef_data["JobDef"].has_key("CVMFS")): infosys.isCVMFS = bool(jobdef_data["JobDef"]["CVMFS"])
            if (jobdef_data["JobDef"].has_key("TierLevel")): infosys.tierLevel = int(jobdef_data["JobDef"]["TierLevel"])
            if (jobdef_data["JobDef"].has_key("Status")): infosys.status = jobdef_data["JobDef"]["Status"]
            if (jobdef_data["JobDef"].has_key("Flavor")): infosys.rflavor = jobdef_data["JobDef"]["Flavor"]
            if (jobdef_data["JobDef"].has_key("Type")): infosys.rtype = jobdef_data["JobDef"]["Type"]
        elif (cmd in ('--list-match',) or cmd in ('-m',)):
            mode = "list-match"
        elif (cmd in ('--list-resource',) or cmd in ('-l',)):
            mode = "list-resource"
        elif (cmd in ('--no-cvmfs',)):
            infosys.isCVMFS = False
        elif (cmd in ('--tags',)):
            infosys.tags = arg.split(",")
        elif (cmd in ('--exclude-tag',)):
            infosys.excludeTag = arg
        elif (cmd in ('--panda-resource',) or cmd in ('-r')):
            infosys.pandaResource = arg
        elif (cmd in ('--show-last-update',)):
            mode = "db-last-update"
        elif (cmd in ('--status',) or cmd in ('-s',)):
            infosys.status = arg
        elif (cmd in ('--type',)):
            infosys.rtype = arg
        elif (cmd in ('--update',) or cmd in ('-u',)):
            mode = "update"
        elif (cmd in ('--tier-level',) or cmd in ('-l',)):
            infosys.tierLevel = arg
        elif (cmd in ('--verbose',) or cmd in ('-v',)):
            infosys.verbose = True

    if (mode == "update"):
        infosys.update()
    if (mode == "parser"):
        infosys.parser()
    elif (mode == "info"):
        infosys.info()
    elif (mode == "db-last-update"):
        infosys.lastUpdate()
    elif (mode == "list-resource"):
        infosys.listResource()
    elif (mode == "list-match"):
        infosys.listMatch()
