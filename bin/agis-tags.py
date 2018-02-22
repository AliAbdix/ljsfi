#!/usr/bin/env python
#####################################################################
# AGIS tags tool                                                    #
# LJSFi Framework 1.9.0                                             #
# Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it> - 20160120 #
#####################################################################

__version__ = "$Revision: 1.6 $"[11:-1]

__HELP__="""LJSFi AGIS tags tool %s.
Usage: agis-tags [OPTION]

Options:
  --help                       display this help and exit.
  --add                        add tags
  --api                        use AGIS API interface
  --ce= | -c <CE FQDN>         CE FQDN
  --clean | -C                 Clean all tags in a resource
  --cmtconfig=<CMTCONFIG>      Force using <CMTCONFIG> to set data
  --old-cmtconfig=<CMTCONFIG>  Use <CMTCONFIG> to get data
  --debug | -d                 debug mode
  --full-site | -f             consider the full site
  --list | -l                  list tags
  --rawlist | -L               list raw tag info
  --panda-resource= | -R <res> panda resource
  --project= | -p <prj>        project name
  --query <panda|cs>           query panda or cs resources
  --quiet                      quiet mode
  --rel= | -r <release>        release name
  --remove                     remove tags
  --show-cmtconfig             show the cmtconfig value when listing tags
  --show-panda-resource | -S   show the panda queue associated to the resource
  --site= | -s <site name>     site name
  --tags= | -t <tags>          comma-separated list of tags
  --tag-new=<tag>              update the tag with <tag>
  --trial | -T                 trial run
  --update-release | -u        update the release data
  --verbose | -v               turn verbosity on

Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>.
"""

try:
    import json
except:
    import simplejson as json
import os, sys, commands
import time
import getopt
from agis.api.AGIS import AGIS
import pycurl
import string

class Data:
    def __init__(self):
        self.contents = ''

    def body_callback(self, buf):
        self.contents = self.contents + buf

    def reset(self):
        self.contents = ''

def getPandaResources(resource,panda_resources=[]):
    if (not agis_site_data or not resource): return []
    if (debug): print "RESOURCE: %s | PANDA RESOURCES: %s" % (resource,panda_resources)
    for res in agis_site_data:
        if (debug): print res
        ce_endpoints = []
        for site_queues in res["queues"]: ce_endpoints.append(site_queues["ce_endpoint"].split(':')[0])
        if (resource in ce_endpoints):
            if (res["panda_resource"] not in panda_resources):
                panda_resources.append(res["panda_resource"])
                ce_endpoints = getCEendpointsFromPandaResource(res["panda_resource"])
                for ce_endpoint in ce_endpoints:
                    panda_resources = getPandaResources(ce_endpoint,panda_resources)
    return panda_resources

def getCEendpointsFromPandaResource(panda_resource):
    ce_endpoints = []
    for res in agis_site_data:
        if (res["panda_resource"] == panda_resource):
            for queue in res["queues"]:
                ce_endpoint = queue["ce_endpoint"].split(':')[0]
                if (ce_endpoint not in ce_endpoints): ce_endpoints.append(ce_endpoint)
    return ce_endpoints

d = Data()
__AGIS_URL__        = 'atlas-agis-api.cern.ch:80'
__CACHE_EXPIRY__    = 3600
__CACHE_FILE__      = "/tmp/agis-site-info.tmp"
__RELCACHE_FILE__   = "/tmp/agis-rel-info.tmp"
__AGIS_SITE_INFO__  = "http://atlas-agis-api.cern.ch/request/pandaqueue/query/list/index.php?json&preset=schedconf"
__AGIS_REL_INFO__   = "http://atlas-agis-api.cern.ch/jsoncache/list_presource_sw.schedconf.json"
__AGIS_LSR_REST__   = "http://atlas-agis-api.cern.ch/request/swrelease/query/?json&pandaqueueobject=1&project=%s&release=%s&cmtconfig=%s"
__AGIS_LPSR_REST__  = "http://atlas-agis-api.cern.ch/request/swrelease/query/list_presource_sw/?json&pandaqueueobject=1&release=%s&project=%s&cmtconfig=%s&major_release=%s"
__AGIS_LPSR2_REST__ = "http://atlas-agis-api.cern.ch/request/swrelease/query/list_presource_sw/?json&pandaqueueobject=1&panda_resource=%s"
__AGIS_ADD_REST__   = "https://atlas-agis-api.cern.ch/request/swreleases/update/add_panda_swrelease/?json&major_release=%s&cmtconfig=%s&force_create=%s&project=%s&tag=%s&release=%s&panda_resource=%s"
__AGIS_REM_REST__   = "https://atlas-agis-api.cern.ch/request/swreleases/update/remove_panda_swrelease/?json&cmtconfig=%s&project=%s&tag=%s&release=%s&panda_resource=%s"
__AGIS_UPDSW_REST__ = "https://atlas-agis-api.cern.ch/request/swreleases/update/set_swrelease/?json&id=%s&project=%s&release=%s&cmtconfig=%s&major_release=%s&tag=%s"
__LJSF_REL_INFO__   = "%s/rellist.php?rel=%s&showtarget&showdeps&panda"
__LJSF_TAG_INFO__   = "%s/rellist.php?tag=%s&showtarget&showdeps&panda&showrel"
sitecache_refresh   = True
relcache_refresh    = True
short_options       = "c:CdfhlLp:qr:R:Ss:t:Tuv"
long_options        = ["add", "api", "ce=", "clean", "cmtconfig=", "debug", "full-site", "help", "list", "old-cmtconfig=", "project=", "rawlist", "rel=", "remove", "panda-resource=", "query=", "quiet", "show-cmtconfig", "show-panda-resource", "site=", "tags=", "tag-new=", "trial", "update-release", "verbose"]
cmtconfig           = None
oldcmtconfig        = None
debug               = False
fullsite            = False
panda_resources     = None
resource            = None
site                = None
rel                 = None
tags                = None
tagnew              = None
project             = None
ljsfrel             = False
showcmtconfig       = False
reldata             = None
quiet               = False
mode                = None
trial               = False
verbose             = False
maxAttempts         = 10
agismode            = 'rest'


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
    elif (cmd in ('--add',)):
        mode = "add"
    elif (cmd in ('--api',)):
        agismode = "api"
    elif (cmd in ('--ce',) or cmd in ('-c',)):
        resource = arg.split(":")[0]
    elif (cmd in ('--clean',) or cmd in ('-C',)):
        mode = "clean"
    elif (cmd in ('--cmtconfig',)):
        cmtconfig = arg
    elif (cmd in ('--debug',) or cmd in ('-d',)):
        debug = True
    elif (cmd in ('--full-site',) or cmd in ('-f',)):
        fullsite = True
    elif (cmd in ('--list',) or cmd in ('-l',)):
        mode = "list"
    elif (cmd in ('--old-cmtconfig',)):
        oldcmtconfig = arg
    elif (cmd in ('--rawlist',) or cmd in ('-L',)):
        mode = "rawlist"
    elif (cmd in ('--panda-resource',) or cmd in ('-R',)):
        panda_resources = [arg]
    elif (cmd in ('--project',) or cmd in ('-p',)):
        project = arg
    elif (cmd in ('--quiet',)):
        quiet = True
    elif (cmd in ('--query',)):
        mode = "query"
        query = arg.lower()
    elif (cmd in ('--rel',) or cmd in ('-r',)):
        rel = arg
    elif (cmd in ('--remove',)):
        mode = "remove"
    elif (cmd in ('--show-cmtconfig',)):
        showcmtconfig = True
    elif (cmd in ('--show-panda-queue',) or cmd in ('-S',)):
        mode = "showPandaQueue"
    elif (cmd in ('--site',) or cmd in ('-s',)):
        site = arg
    elif (cmd in ('--tags',) or cmd in ('-t',)):
        tags = arg
    elif (cmd in ('--tag-new',)):
        tagnew = arg
    elif (cmd in ('--trial',) or cmd in ('-T',)):
        trial = True
    elif (cmd in ('--update-release',) or cmd in ('-u',)):
        mode = "updaterel"
    elif (cmd in ('--verbose',) or cmd in ('-v',)):
        verbose = True

if (not panda_resources and not resource and not site and not (mode == "updaterel" or mode == "query" or mode == "clean")):
    print "No resource or site specified"
    print __HELP__
    sys.exit(2)

if (not mode):
    print "No action specified, please specify add, remove or update-release"
    print __HELP__
    sys.exit(3)

if (not rel and not tags and mode != "list" and mode != "rawlist" and mode != "showPandaQueue" and mode != "clean"):
    print "No release or tags specified"
    print __HELP__
    sys.exit(4)

if (mode == "clean" and not panda_resources):
    print "No panda resource specified"
    print __HELP__
    sys.exit(5)

# initialize AGIS
a=AGIS(hostp=__AGIS_URL__)

# LJSF URL
if (os.environ.has_key("LJSFDBURL")): LJSFDBURL="%s/exec" % os.path.dirname(os.environ["LJSFDBURL"])
else:                                 LJSFDBURL="https://atlas-install.roma1.infn.it/atlas_install/exec"
if (verbose): print "Using LJSFi URL %s" % LJSFDBURL

# Initialize cURL
c = pycurl.Curl()
c.setopt(c.SSL_VERIFYPEER, 0)
c.setopt(c.WRITEFUNCTION, d.body_callback)
c.setopt(c.CONNECTTIMEOUT, 20)
c.setopt(c.TIMEOUT, 30)

if (mode != "updaterel"):
    # Get the json files from AGIS
    if (os.path.exists(__CACHE_FILE__)):
        now = time.time()
        st = os.stat(__CACHE_FILE__)
        if ((now - st.st_mtime) < __CACHE_EXPIRY__): sitecache_refresh = False

    if (sitecache_refresh):
        try:
            c.setopt(c.URL, __AGIS_SITE_INFO__)
            d.reset()
            if (debug): print "Getting AGIS site data from %s" % __AGIS_SITE_INFO__
            c.perform()
            outfile = open(__CACHE_FILE__,'w')
            outfile.write(d.contents)
            outfile.close()
        except:
            print "Cannot get AGIS site data"
            sys.exit(1)

if (debug): print "Start"
try:
    if (rel or tags):
        d.reset()
        if (rel and not tags):
            relurl = __LJSF_REL_INFO__ % (LJSFDBURL, rel)
        elif (tags):
            relurl = __LJSF_TAG_INFO__ % (LJSFDBURL, tags)
        if (debug or verbose): print "Getting LJSF release data from %s" % relurl
        c.setopt(c.URL, relurl)
        c.perform()
        reldata = d.contents.split("\n")
        if (debug): print "[RELDATA] %s " % reldata
        if (debug): print "[RELDATA] %s,%s,%s,%s,%s" % (reldata, tags, project, rel, cmtconfig)
        if ((not reldata or reldata == ['']) and tags and project and rel and cmtconfig):
            reldata = ["%s,,,%s,%s,%s" % (tags,project,rel,cmtconfig)]
except:
    print "Cannot get LJSFi data"
    sys.exit(1)
c.close()

if (debug): print reldata

if (mode != "updaterel" and mode != "query"):
    agis_site_info = open(__CACHE_FILE__,'r')
    json_site_data = agis_site_info.read()
    agis_site_info.close()
    agis_site_data = json.loads(json_site_data)
    if (not panda_resources): panda_resources = getPandaResources(resource)

if (mode == "showPandaQueue"):
    panda_resources.sort()
    for pandaResource in panda_resources: print pandaResource
    sys.exit(0)
if (not panda_resources and not (mode == "updaterel" or mode == "query")):
    if (not quiet): print "agis-tags: WARNING - no Panda queue found for %s [sitename = %s]" % (resource,site)
    if (mode == "showPandaQueue"): sys.exit(1)

if (mode == "updaterel"):
    for r in reldata:
        if (r):
            rdata = r.split(",")
            if (len(rdata) >= 6):
                m_tag = rdata[0]
                m_project = rdata[3]
                m_release = rdata[4]
                if (cmtconfig):
                    m_cmtconfig = cmtconfig
                else:
                    m_cmtconfig = rdata[5]
                if (not rel and len(rdata) >= 7): rel = rdata[6]
                # Major releases have 3 digits
                majrelnum = rel.split('-')[0].split('.')[:3]
                try:
                    for n in majrelnum: i = int(n)
                    m_major_release = string.join(majrelnum,'.')
                except:
                    m_major_release = None
            else:
                m_tag = ""
                m_cmtconfig = "noarch"
                if (agismode == 'api'):
                    m_project = None
                    m_release = None
                    m_major_release = None
                else:
                    m_project = ""
                    m_release = ""
                    m_major_release = ""
            if (tagnew):
                m_tag = tagnew
                if (verbose): print "Using tag %s" % m_tag
            if (agismode == 'api'):
                swrels = a.list_swreleases(project = m_project, release = m_release, cmtconfig = m_cmtconfig)
                if (swrels):
                    if (verbose): print swrels
                    for swrel in swrels[m_release]:
                        m_id = swrel.id
                        if (trial):
                            print "set_swrelease(id = %s, project = %s, release = %s, cmtconfig = %s, major_release = %s, tag = %s)" % (m_id,m_project,m_release,m_cmtconfig,m_major_release,m_tag)
                        else:
                            if (verbose): print "set_swrelease(id = %s, project = %s, release = %s, cmtconfig = %s, major_release = %s, tag = %s)" % (m_id,m_project,m_release,m_cmtconfig,m_major_release,m_tag)
                            a.set_swrelease(id = m_id, project = m_project, release = m_release, cmtconfig = m_cmtconfig, major_release = m_major_release, tag = m_tag)
                else:
                    print "Release %s-%s-%s not defined in AGIS" % (m_project,m_release,m_cmtconfig)
            else:
                if (oldcmtconfig):
                    resturl = __AGIS_LSR_REST__ % (m_project, m_release, oldcmtconfig)
                else:
                    resturl = __AGIS_LSR_REST__ % (m_project, m_release, m_cmtconfig)
                if (debug): print resturl
                if (verbose): print resturl
                c = pycurl.Curl()
                c.setopt(c.SSL_VERIFYPEER, 0)
                c.setopt(c.WRITEFUNCTION, d.body_callback)
                c.setopt(c.CONNECTTIMEOUT, 60)
                c.setopt(c.TIMEOUT, 120)
                c.setopt(c.SSLCERT, os.environ['X509_USER_PROXY'])
                d.reset()
                c.setopt(c.URL, resturl)
                c.perform()
                try:
                    swrels = json.loads(d.contents)
                except:
                    swrels = None
                c.close()
                if (swrels):
                    for swrel in swrels:
                        m_id = swrel['id']
                        resturl = __AGIS_UPDSW_REST__ % (m_id,m_project,m_release,m_cmtconfig,m_major_release,m_tag)
                        if (trial):
                            print resturl
                        else:
                            if (verbose): print resturl
                            c = pycurl.Curl()
                            c.setopt(c.SSL_VERIFYPEER, 0)
                            c.setopt(c.WRITEFUNCTION, d.body_callback)
                            c.setopt(c.CONNECTTIMEOUT, 60)
                            c.setopt(c.TIMEOUT, 120)
                            c.setopt(c.SSLCERT, os.environ['X509_USER_PROXY'])
                            d.reset()
                            c.setopt(c.URL, resturl)
                            c.perform()
                            try:
                                res = json.loads(d.contents)
                            except:
                                res = None
                            c.close()
                            print res
                else:
                    print "Release %s-%s-%s not defined in AGIS" % (m_project,m_release,m_cmtconfig)
elif (mode == "query"):
    reslist = []
    for r in reldata:
        if (r):
            rdata = r.split(",")
            if (len(rdata) >= 6):
                m_tag = rdata[0]
                m_project = rdata[3]
                m_release = rdata[4]
                if (cmtconfig):
                    m_cmtconfig = cmtconfig
                else:
                    m_cmtconfig = rdata[5]
                if (not rel and len(rdata) >= 7): rel = rdata[6]
                # Major releases have 3 digits
                majrelnum = rel.split('-')[0].split('.')[:3]
                try:
                    for n in majrelnum: i = int(n)
                    m_major_release = string.join(majrelnum,'.')
                except:
                    m_major_release = None
                m_force_create = True
            else:
                m_tag = ""
                m_cmtconfig = "noarch"
                if (agismode == 'api'):
                    m_project = None
                    m_release = None
                    m_major_release = None
                else:
                    m_project = ""
                    m_release = ""
                    m_major_release = ""
        if (query == "panda"):
            if (agismode == 'api'):
                try:
                    rellist = a.list_panda_swreleases(release=m_release, project=m_project, cmtconfig=m_cmtconfig, major_release=m_major_release)
                    for relres in rellist.keys():
                        if (relres not in reslist): reslist.append(relres)
                except:
                    pass
            else:
                resturl = __AGIS_LPSR_REST__ % (m_release, m_project, m_cmtconfig, m_major_release)
                if (verbose): print resturl
                c = pycurl.Curl()
                c.setopt(c.SSL_VERIFYPEER, 0)
                c.setopt(c.WRITEFUNCTION, d.body_callback)
                c.setopt(c.CONNECTTIMEOUT, 60)
                c.setopt(c.TIMEOUT, 120)
                c.setopt(c.SSLCERT, os.environ['X509_USER_PROXY'])
                d.reset()
                c.setopt(c.URL, resturl)
                c.perform()
                try:
                    rellist = json.loads(d.contents)
                    for rellist_item in rellist:
                        if (rellist_item['panda_resource'] not in reslist): reslist.append(rellist_item['panda_resource'])
                except:
                    pass
                c.close()
    if (reslist):
        reslist.sort()
        for r in reslist: print r
else:
    tag_list = []
    swrel_list = []
    for m_panda_resource in panda_resources:
        if (debug): print "Processing %s" % m_panda_resource
        if (mode == "list" or mode == "rawlist" or mode == "clean"):
            if (agismode == 'api'):
                rellist = a.list_panda_swreleases(panda_resource=m_panda_resource)
                if (rellist.has_key(m_panda_resource)):
                    for relitem in rellist[m_panda_resource]:
                        if (mode == "rawlist" or mode == "clean"): swrel_list.append(relitem)
                        if (relitem.tag):
                            tag = relitem.tag
                        else:
                            if (relitem.project == 'AtlasOffline'):
                                prj = 'offline'
                            elif (relitem.project == 'AtlasProduction'):
                                prj = 'production'
                            elif (relitem.project == 'PoolCondPFC'):
                                prj = 'poolcond'
                            else:
                                prj = relitem.project
                            if (relitem.cmtconfig == 'noarch'):
                                if (relitem.project == relitem.release):
                                    tag = "VO-atlas-%s" % (prj)
                                else:
                                    tag = "VO-atlas-%s-%s" % (prj,relitem.release)
                            else:
                                tag = "VO-atlas-%s-%s-%s" % (prj,relitem.release,relitem.cmtconfig)
                        if (showcmtconfig): tag = "%s: %s" % (relitem.cmtconfig, tag)
                        if (not cmtconfig or (cmtconfig and relitem.cmtconfig == cmtconfig)):
                            if (tag not in tag_list): tag_list.append(tag)
            else:
                resturl = __AGIS_LPSR2_REST__ % (m_panda_resource)
                if (verbose): print resturl
                c = pycurl.Curl()
                c.setopt(c.SSL_VERIFYPEER, 0)
                c.setopt(c.WRITEFUNCTION, d.body_callback)
                c.setopt(c.CONNECTTIMEOUT, 60)
                c.setopt(c.TIMEOUT, 120)
                c.setopt(c.SSLCERT, os.environ['X509_USER_PROXY'])
                d.reset()
                c.setopt(c.URL, resturl)
                c.perform()
                try:
                    rellist = json.loads(d.contents)
                except:
                    pass
                c.close()
                for relitem in rellist:
                    if (mode == "rawlist" or mode == "clean"): swrel_list.append(relitem)
                    if (relitem['tag']):
                        tag = relitem['tag']
                    else:
                        if (relitem['project'] == 'AtlasOffline'):
                            prj = 'offline'
                        elif (relitem['project'] == 'AtlasProduction'):
                            prj = 'production'
                        elif (relitem['project'] == 'PoolCondPFC'):
                            prj = 'poolcond'
                        else:
                            prj = relitem['project']
                        if (relitem['cmtconfig'] == 'noarch'):
                            if (relitem['cmtconfig'] == relitem['release']):
                                tag = "VO-atlas-%s" % (prj)
                            else:
                                tag = "VO-atlas-%s-%s" % (prj,relitem['release'])
                        else:
                            tag = "VO-atlas-%s-%s-%s" % (prj,relitem['release'],relitem['cmtconfig'])
                    if (showcmtconfig): tag = "%s: %s" % (relitem['cmtconfig'], tag)
                    if (not cmtconfig or (cmtconfig and relitem['cmtconfig'] == cmtconfig)):
                        if (tag not in tag_list): tag_list.append(tag)
        else:
            for r in reldata:
                if (r):
                    rdata = r.split(",")
                    if (len(rdata) >= 6):
                        m_tag = rdata[0]
                        m_project = rdata[3]
                        m_release = rdata[4]
                        if (cmtconfig):
                            m_cmtconfig = cmtconfig
                        else:
                            m_cmtconfig = rdata[5]
                        if (not rel and len(rdata) >= 7): rel = rdata[6]
                        # Major releases have 3 digits
                        majrelnum = rel.split('-')[0].split('.')[:3]
                        try:
                            for n in majrelnum: i = int(n)
                            m_major_release = string.join(majrelnum,'.')
                        except:
                            m_major_release = None
                        m_force_create = True
                    else:
                        m_tag = ""
                        m_project = None
                        m_release = None
                        m_cmtconfig = "noarch"
                        m_major_release = None
                        m_force_create = False
                    if (agismode == 'api'):
                        if (mode == "add"):
                            if (trial):
                                print ("add_panda_swrelease(panda_resource = %s, project = %s, release = %s, cmtconfig = %s, major_release = %s, tag = %s, force_create = %s)" % (m_panda_resource,m_project,m_release,m_cmtconfig,m_major_release,m_tag,m_force_create))
                            else:
                                if (verbose): print ("add_panda_swrelease(panda_resource = %s, project = %s, release = %s, cmtconfig = %s, major_release = %s, tag = %s, force_create = %s)" % (m_panda_resource,m_project,m_release,m_cmtconfig,m_major_release,m_tag,m_force_create))
                                numAttempt = 0
                                while numAttempt < maxAttempts:
                                    try:
                                        a.add_panda_swrelease(panda_resource = m_panda_resource, project = m_project, release = m_release, cmtconfig = m_cmtconfig, major_release = m_major_release, tag = m_tag, force_create = m_force_create)
                                        break
                                    except:
                                        numAttempt += 1
                                        if (numAttempt > maxAttempts): raise
                                        print "Tag add failed [%d/%d]" % (numAttempt,maxAttempts)
                                        time.sleep(1)
                        elif (mode == "remove"):
                            if (trial):
                                print ("remove_panda_swrelease(panda_resource = %s, project = %s, release = %s, cmtconfig = %s, major_release = %s, force_create = %s)" % (m_panda_resource,m_project,m_release,m_cmtconfig,m_major_release,m_force_create))
                            else:
                                if (verbose): print ("remove_panda_swrelease(panda_resource = %s, project = %s, release = %s, cmtconfig = %s, major_release = %s, force_create = %s)" % (m_panda_resource,m_project,m_release,m_cmtconfig,m_major_release,m_force_create))
                                numAttempt = 0
                                while numAttempt < maxAttempts:
                                    try:
                                        a.remove_panda_swrelease(panda_resource = m_panda_resource, project = m_project, release = m_release, cmtconfig = m_cmtconfig, major_release = m_major_release, force_create = m_force_create)
                                        break
                                    except:
                                        numAttempt += 1
                                        if (numAttempt > maxAttempts): raise
                                        print "Tag removal failed [%d/%d]" % (numAttempt,maxAttempts)
                                        time.sleep(1)
                    else:
                        if (mode == "add"):
                            resturl = __AGIS_ADD_REST__ % (m_major_release,m_cmtconfig,m_force_create,m_project,m_tag,m_release,m_panda_resource)
                            if (trial):
                                print resturl
                            else:
                                if (verbose): print resturl
                                numAttempt = 0
                                while numAttempt < maxAttempts:
                                    c = pycurl.Curl()
                                    c.setopt(c.SSL_VERIFYPEER, 0)
                                    c.setopt(c.WRITEFUNCTION, d.body_callback)
                                    c.setopt(c.CONNECTTIMEOUT, 60)
                                    c.setopt(c.TIMEOUT, 120)
                                    c.setopt(c.SSLCERT, os.environ['X509_USER_PROXY'])
                                    d.reset()
                                    c.setopt(c.URL, resturl)
                                    c.perform()
                                    res = json.loads(d.contents)
                                    c.close()
                                    try:
                                        if (res[0][2]):
                                            numAttempt += 1
                                            if (numAttempt > maxAttempts): raise
                                            print "Tag add failed [%d/%d]: %s" % (numAttempt,maxAttempts,res[0][2])
                                            time.sleep(1)
                                        else:
                                            break
                                    except:
                                        numAttempt += 1
                                        if (numAttempt > maxAttempts): raise
                                        print "Tag add failed [%d/%d]: %s" % (numAttempt,maxAttempts,res)
                                        time.sleep(1)
                        elif (mode == "remove"):
                            resturl = __AGIS_REM_REST__ % (m_cmtconfig,m_project,m_tag,m_release,m_panda_resource)
                            if (trial):
                                print resturl
                            else:
                                if (verbose): print resturl
                                numAttempt = 0
                                while numAttempt < maxAttempts:
                                    c = pycurl.Curl()
                                    c.setopt(c.SSL_VERIFYPEER, 0)
                                    c.setopt(c.WRITEFUNCTION, d.body_callback)
                                    c.setopt(c.CONNECTTIMEOUT, 60)
                                    c.setopt(c.TIMEOUT, 120)
                                    c.setopt(c.SSLCERT, os.environ['X509_USER_PROXY'])
                                    d.reset()
                                    c.setopt(c.URL, resturl)
                                    c.perform()
                                    res = json.loads(d.contents)
                                    c.close()
                                    try:
                                        if (res[0][2]):
                                            numAttempt += 1
                                            if (numAttempt > maxAttempts): raise
                                            print "Tag removal failed [%d/%d]: %s" % (numAttempt,maxAttempts,res[0][2])
                                            time.sleep(1)
                                        else:
                                            break
                                    except:
                                        numAttempt += 1
                                        if (numAttempt > maxAttempts): raise
                                        print "Tag removal failed [%d/%d]: %s" % (numAttempt,maxAttempts,res)
                                        time.sleep(1)

if (mode == "list"):
    tag_list.sort()
    for tag in tag_list:
        print tag

if (mode == "rawlist"):
    if (agismode == 'api'):
        for item in swrel_list:
            print "%s,%s,%s,%s" % (item.tag,item.project,item.release,item.cmtconfig)
    else:
        for item in swrel_list:
            print "%s,%s,%s,%s" % (item['tag'],item['project'],item['release'],item['cmtconfig'])

if (mode == "clean"):
    swrels = {}
    if (agismode == 'api'):
        for item in swrel_list:
            swrels["%s_%s_%s_%s" % (item.tag,item.project,item.release,item.cmtconfig)] = item
        swrel_keys = swrels.keys()
        swrel_keys.sort()
        alltags = len(swrel_keys)
        print "%d tags to remove" % alltags
        CHECKPOINT=20
        indx = 0
        for key in swrel_keys:
            if (indx % CHECKPOINT == 0): print "Removing tags: %3.1f%% done" % (100*float(indx)/float(alltags))
            item = swrels[key]
            if (item.major_release):
                if (trial):
                    print ("remove_panda_swrelease(panda_resource = %s, project = %s, release = %s, cmtconfig = %s, major_release = %s, force_create = %s)" % (panda_resources[0],item.project,item.release,item.cmtconfig,item.major_release,False))
                else:
                    if (verbose): print ("remove_panda_swrelease(panda_resource = %s, project = %s, release = %s, cmtconfig = %s, major_release = %s, force_create = %s)" % (panda_resources[0],item.project,item.release,item.cmtconfig,item.major_release,False))
                    a.remove_panda_swrelease(panda_resource = panda_resources[0], project = item.project, release = item.release, cmtconfig = item.cmtconfig, major_release = item.major_release, force_create = False)
            else:
                if (trial):
                    print ("remove_panda_swrelease(panda_resource = %s, project = %s, release = %s, cmtconfig = %s, force_create = %s)" % (panda_resources[0],item.project,item.release,item.cmtconfig,False))
                else:
                    if (verbose): print ("remove_panda_swrelease(panda_resource = %s, project = %s, release = %s, cmtconfig = %s, force_create = %s)" % (panda_resources[0],item.project,item.release,item.cmtconfig,False))
                    a.remove_panda_swrelease(panda_resource = panda_resources[0], project = item.project, release = item.release, cmtconfig = item.cmtconfig, force_create = False)
            indx += 1
        if (alltags > 0): print "Removing tags: %3.1f%% done" % (100*float(indx)/float(alltags))
    else:
        for item in swrel_list:
            swrels["%s_%s_%s_%s" % (item['tag'],item['project'],item['release'],item['cmtconfig'])] = item
        swrel_keys = swrels.keys()
        swrel_keys.sort()
        alltags = len(swrel_keys)
        print "%d tags to remove" % alltags
        CHECKPOINT=20
        indx = 0
        for key in swrel_keys:
            if (indx % CHECKPOINT == 0): print "Removing tags: %3.1f%% done" % (100*float(indx)/float(alltags))
            item = swrels[key]
            if (item['major_release']): swmajor_release = item['major_release']
            else:                       swmajor_release = ""
            if (item['tag']):           swtag = item['major_release']
            else:                       swtag = ""
            resturl = __AGIS_REM_REST__ % (item['cmtconfig'],item['project'],swtag,item['release'],panda_resources[0])
            if (trial):
                print resturl
            else:
                if (verbose): print resturl
                c = pycurl.Curl()
                c.setopt(c.SSL_VERIFYPEER, 0)
                c.setopt(c.WRITEFUNCTION, d.body_callback)
                c.setopt(c.CONNECTTIMEOUT, 60)
                c.setopt(c.TIMEOUT, 120)
                c.setopt(c.SSLCERT, os.environ['X509_USER_PROXY'])
                d.reset()
                c.setopt(c.URL, resturl)
                c.perform()
                res = json.loads(d.contents)
                c.close()
                try:
                    if (res[0][2]): print "Tag removal failed: %s" % res[0][2]
                except:
                    print "Tag removal failed: %s" % res
            indx += 1
        if (alltags > 0): print "Removing tags: %3.1f%% done" % (100*float(indx)/float(alltags))
