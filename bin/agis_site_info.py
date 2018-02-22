#!/usr/bin/env python
#####################################################################
# AGIS site info tool                                               #
# LJSFi Framework 2.0.0                                             #
# Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it> - 20130701 #
#####################################################################

__version__ = "$Revision: 1.0 $"[11:-1]

__HELP__="""AGIS site info tool %s.
Usage: agis-site-info [OPTION]

Options:
  --help                       Display this help and exit.
  --debug | -d                 Debug mode
  --endpoint | -e <name>       Endpoint name
  --fsconf | -f                Show frontier setup
  --id | -i                    Show the site id
  --setype | -S                Show the SE type of a give endpoint
  --site | -s <sitename>       Site name

Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>.
"""

try:
    import json
except:
    import simplejson as json
import os, sys, commands
import time
import getopt
import string
import re
try:
    import hashlib
except:
    import md5 as hashlib

__AGIS_SITE_INFO__ = "http://atlas-agis-api-0.cern.ch/request/site/query/list/?json"
__AGIS_SITE_INFO_SITE__ = "http://atlas-agis-api-0.cern.ch/request/site/query/list/?json&site=%s"
__AGIS_SITE_INFO_CACHE__ = "http://atlas-agis-api.cern.ch/jsoncache/list_sites.json"
__CURL_EXEC__ = "curl -S --connect-timeout 60 -o '%s' '%s' 2>/dev/null"
__CACHE_FILE__ = "/var/tmp/.agisinfo_%s/agis-site-info" % os.getuid()
__CACHE_EXPIRY__ = 3600
__TMPFILE__     = "%s.tmp" % __CACHE_FILE__

if (os.environ.has_key("VO_ATLAS_SW_DIR")):
    __DEFAULT_AGIS_SITE_INFO__ = "%s/local/etc/agis_site_info.json" % os.environ["VO_ATLAS_SW_DIR"]
    __AGIS_STATIC_SITE_INFO__ = "%s/local/etc/agis_static_site_info.json" % os.environ["VO_ATLAS_SW_DIR"]
else:
    sys.stderr.write("No VO_ATLAS_SW_DIR set, using /cvmfs/atlas.cern.ch/repo/sw\n")
    __DEFAULT_AGIS_SITE_INFO__ = "/cvmfs/atlas.cern.ch/repo/sw/local/etc/agis_site_info.json"
    __AGIS_STATIC_SITE_INFO__ = "/cvmfs/atlas.cern.ch/repo/sw/local/etc/agis_static_site_info.json"

short_options = "de:hfiSs:"
long_options = ["debug", "endpoint=", "fsconf", "help", "id", "setype", "site="]

class agisSiteInfo:
    debug = False
    mode = None

    def setDebug(self, flag=False):
        self.debug = flag

    def getAgisData(self,site=None):
        # Get the json files from AGIS
        asinfo = None
        assinfo = None
        agis_site_data = []
        agis_static_site_data = []

        cachedir = os.path.dirname(__CACHE_FILE__)
        if (not os.path.exists(cachedir)): os.makedirs(cachedir)
        agisurl = __AGIS_SITE_INFO_CACHE__
        tmpfile = __TMPFILE__
        cachefile = __CACHE_FILE__
        cachebackup = "%s.%s" % (cachefile,time.strftime('%s'))

        refresh = True
        if (os.path.exists(cachefile)):
            now = time.time()
            st = os.stat(cachefile)
            if ((now - st.st_mtime) < __CACHE_EXPIRY__): refresh = False

        if (self.debug):
            if (refresh): sys.stderr.write("Refreshing AGIS data\n")
            else:         sys.stderr.write("Using cached AGIS data\n")

        try:
            if (self.debug): sys.stderr.write("Getting AGIS site data from %s\n" % agisurl)
            s,o = commands.getstatusoutput(__CURL_EXEC__ % (tmpfile, agisurl))
            if (s != 0):
                print o
                raise
            if (os.path.exists(cachefile)): os.rename(cachefile,cachebackup)
            os.rename(tmpfile,cachefile)
            asinfo = cachefile
        except:
            raise
            sys.stderr.write("Cannot retrieve AGIS site info\n")
            if (os.path.exists(__DEFAULT_AGIS_SITE_INFO__)): asinfo = __DEFAULT_AGIS_SITE_INFO__

        if (os.path.exists(__AGIS_STATIC_SITE_INFO__)): assinfo = __AGIS_STATIC_SITE_INFO__
        elif (os.path.exists(os.path.basename(__AGIS_STATIC_SITE_INFO__))): assinfo = os.path.basename(__AGIS_STATIC_SITE_INFO__)
        elif (os.path.exists("~/.%s" % os.path.basename(__AGIS_STATIC_SITE_INFO__))): assinfo = "~/.%s" % os.path.basename(__AGIS_STATIC_SITE_INFO__)

        if (assinfo):
            try:
                agis_static_site_info = open(assinfo,'r')
                json_static_site_data = agis_static_site_info.read()
                agis_static_site_info.close()
                if (self.debug): sys.stderr.write("Loading AGIS static_site data from %s\n" % assinfo)
                agis_static_site_data = json.loads(json_static_site_data)
                if (self.debug): sys.stderr.write("AGIS static site data loaded from %s\n" % assinfo)
            except:
                agis_static_site_data = []
                sys.stderr.write("Cannot read AGIS static site info\n")

        if (asinfo):
            try:
                if (self.debug): sys.stderr.write("Reading AGIS site data from %s\n" % asinfo)
                agis_site_info = open(asinfo,'r')
                json_site_data = agis_site_info.read()
                agis_site_info.close()
                if (self.debug): sys.stderr.write("Loading AGIS site data from %s\n" % asinfo)
                agis_site_data = json.loads(json_site_data)
                if (self.debug): sys.stderr.write("AGIS site data loaded from %s\n" % asinfo)
                if (type(agis_site_data) == type({}) and agis_site_data.has_key('error')): agis_site_data = []
            except:
                sys.stderr.write("Cannot read AGIS site info\n")
                raise

        if (agis_static_site_data): agis_site_data = agis_static_site_data + agis_site_data

        return agis_site_data

    def getFSConf(self, site=None):
        fsconf = ""
        agis_site_data = self.getAgisData(site)
        for site_data in agis_site_data:
            if (site_data["name"] == site):
                if (site_data.has_key("fsconf")):
                    fsconfdata = site_data["fsconf"]
                    if fsconfdata.has_key("frontier"):
                        for fserv in fsconfdata["frontier"]: fsconf += "(serverurl=%s)" % fserv[0]
                    if fsconfdata.has_key("squid"):
                        for fsquid in fsconfdata["squid"]: fsconf += "(proxyurl=%s)" % fsquid[0]
                    if (fsconf): break
        return fsconf

    def getID(self, site=None):
        id = None
        agis_site_data = self.getAgisData(site)
        patts = (
                  re.compile('.*_SCRATCHDISK')
                , re.compile('.*_DATADISK')
                )
        exclude_patt = re.compile('.*TAPE')
        last_ep = None
        for site_data in agis_site_data:
            if (site_data["name"] == site):
                if (site_data.has_key("ddmendpoints")):
                    for ep in site_data["ddmendpoints"].keys():
                        for p in patts:
                            if (p.match(ep)):
                                id = ep
                                break
                            else:
                                if (not exclude_patt.match(ep)): last_ep = ep
                        if (id): break
                if (id): break
        if (not id and last_ep): id = last_ep
        return id

    def getSEinfo(self, site=None, endpoint=None):
        seinfo = None
        if (site and endpoint):
            agis_site_data = self.getAgisData(site)
            for site_data in agis_site_data:
                if (site_data["name"] == site):
                    if (site_data.has_key("ddmendpoints")):
                        ddmepdata = site_data["ddmendpoints"]
                        if (ddmepdata.has_key(endpoint)):
                            seinfo = ddmepdata[endpoint]["se_impl"]
                    if (seinfo): break
        return seinfo


agisinfo = agisSiteInfo()
mode = None
site = None
endpoint = None
rc   = 0

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
        elif (cmd in ('--debug',) or cmd in ('-d',)):
            agisinfo.setDebug(True)
        elif (cmd in ('--endpoint',) or cmd in ('-e',)):
            endpoint = arg
        elif (cmd in ('--fsconf',) or cmd in ('-f',)):
            mode = "fsconf"
        elif (cmd in ('--id',) or cmd in ('-i',)):
            mode = "id"
        elif (cmd in ('--seinfo',) or cmd in ('-S',)):
            mode = "seinfo"
        elif (cmd in ('--site',) or cmd in ('-s',)):
            site = arg

    if (mode == "fsconf"):
        if (site):
            fsconf = agisinfo.getFSConf(site)
            if (fsconf): print fsconf
            else: rc = 10
        else:
            sys.stderr.write("No site specified\n")
            rc = 1

    if (mode == "seinfo"):
        if (site and endpoint):
            seinfo = agisinfo.getSEinfo(site, endpoint)
            if (seinfo): print seinfo
            else: rc = 10
        else:
            sys.stderr.write("No site or endpoint specified\n")
            rc = 1

    if (mode == "id"):
        if (site):
            id = agisinfo.getID(site)
            if (id): print id
            else: rc = 10
        else:
            sys.stderr.write("No site specified\n")
            rc = 1

    sys.exit(rc)
