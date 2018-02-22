#!/usr/bin/env python
#####################################################################
# AGIS tags tool                                                    #
# LJSFi Framework 1.9.0                                             #
# Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it> - 20120808 #
#####################################################################

__version__ = "$Revision: 1.2 $"[11:-1]

__HELP__="""LJSFi AGIS tags tool %s.
Usage: agis-tags [OPTION]

Options:
  --help                       display this help and exit.
  --add                        add tags
  --ce= | -c <CE FQDN>         CE FQDN
  --debug | -d                 debug mode
  --full-site | -f             consider the full site
  --list | -l                  list tags
  --rel= | -r <release>        release name
  --remove                     remove tags
  --show-panda-queue | -S      show the panda queue associated to the resource
  --site= | -s <site name>     site name
  --tags= | -t <tags>          comma-separated list of tags
  --trial | -T                 trial run
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
from commands import getstatusoutput

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
__AGIS_URL__       = 'atlas-agis-api-dev.cern.ch:80'
__CACHE_EXPIRY__   = 3600
__RELCACHE_EXPIRY__ = 7200
__CACHE_FILE__     = "/tmp/agis-site-info.tmp"
__RELCACHE_FILE__  = "/tmp/agis-rel-info.tmp"
__AGIS_SITE_INFO__ = "http://atlas-agis-api-dev.cern.ch/request/pandaqueue/query/list/index.php?json&preset=full&ceaggregation"
__AGIS_REL_INFO__  = "http://atlas-agis-api-dev.cern.ch/jsoncache/list_presource_sw.schedconf.json"
__LJSF_REL_INFO__  = "https://atlas-install.roma1.infn.it/atlas_install/exec/rellist.php?rel=%s&showtarget&showdeps&panda"
__LJSF_TAG_INFO__  = "https://atlas-install.roma1.infn.it/atlas_install/exec/rellist.php?tag=%s&showtarget&showdeps&panda"
sitecache_refresh = True
relcache_refresh = True
short_options = "c:dfhlqr:Ss:t:Tv"
long_options = ["add", "ce=", "debug", "full-site", "help", "list", "rel=", "remove", "show-panda-queue", "site=", "tags=", "trial", "verbose"]
debug = False
fullsite = False
resource = None
site = None
rel = None
tags = None
reldata = None
mode = None
trial = False
verbose = False


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
    elif (cmd in ('--ce',) or cmd in ('-c',)):
        resource = arg.split(":")[0]
    elif (cmd in ('--debug',) or cmd in ('-d',)):
        debug = True
    elif (cmd in ('--full-site',) or cmd in ('-f',)):
        fullsite = True
    elif (cmd in ('--list',)):
        mode = "list"
    elif (cmd in ('--rel',) or cmd in ('-r',)):
        rel = arg
    elif (cmd in ('--remove',)):
        mode = "remove"
    elif (cmd in ('--show-panda-queue',) or cmd in ('-S',)):
        mode = "showPandaQueue"
    elif (cmd in ('--site',) or cmd in ('-s',)):
        site = arg
    elif (cmd in ('--tags',) or cmd in ('-t',)):
        tags = arg
    elif (cmd in ('--trial',) or cmd in ('-T',)):
        trial = True
    elif (cmd in ('--verbose',) or cmd in ('-v',)):
        verbose = True

if (not resource and not site):
    print "No resource or site specified"
    print __HELP__
    sys.exit(2)

if (not mode):
    print "No action specified, please specify add or remove"
    sys.exit(3)

if (not rel and not tags and mode != "list"and mode != "showPandaQueue"):
    print "No release or tags specified"
    sys.exit(4)

# initialize AGIS
a=AGIS(hostp=__AGIS_URL__)

# Get the json files from AGIS
if (os.path.exists(__CACHE_FILE__)):
    now = time.time()
    st = os.stat(__CACHE_FILE__)
    if ((now - st.st_mtime) < __CACHE_EXPIRY__): sitecache_refresh = False

if (os.path.exists(__RELCACHE_FILE__)):
    now = time.time()
    st = os.stat(__RELCACHE_FILE__)
    if ((now - st.st_mtime) < __RELCACHE_EXPIRY__): relcache_refresh = False

c = pycurl.Curl()
c.setopt(c.SSL_VERIFYPEER, 0)
c.setopt(c.WRITEFUNCTION, d.body_callback)

if (relcache_refresh and relmode != "list"):
    try:
        if (verbose): print "Getting AGIS rel data from %s" % __AGIS_REL_INFO__
        (s,o) = getstatusoutput("wget %s -q -Nc -O %s" % (__AGIS_REL_INFO__,__RELCACHE_FILE__))
        if (s != 0):
            print "Cannot get AGIS releases data"
            sys.exit(1)
    except:
        print "Cannot execute wget %s" % __AGIS_REL_INFO__
        sys.exit(1)

if (sitecache_refresh):
    try:
        c.setopt(c.URL, __AGIS_SITE_INFO__)
        d.reset()
        if (verbose): print "Getting AGIS site data from %s" % __AGIS_SITE_INFO__
        c.perform()
        outfile = open(__CACHE_FILE__,'w')
        outfile.write(d.contents)
        outfile.close()
    except:
        print "Cannot get AGIS site data"
        sys.exit(1)

try:
    if (rel or tags):
        d.reset()
        if (rel and not tags):
            relurl = __LJSF_REL_INFO__ % rel
        elif (tags):
            relurl = __LJSF_TAG_INFO__ % tags
        c.setopt(c.URL, relurl)
        if (verbose): print "Getting LJSF release data"
        c.perform()
        reldata = d.contents.split("\n")
except:
    print "Cannot get LJSFi data"
    sys.exit(1)
c.close()

agis_site_info = open(__CACHE_FILE__,'r')
json_site_data = agis_site_info.read()
agis_site_info.close()
agis_site_data = json.loads(json_site_data)
if (mode != "list"):
    agis_rel_info = open(__RELCACHE_FILE__,'r')
    json_rel_data = agis_rel_info.read()
    agis_rel_info.close()
    agis_rel_data = json.loads(json_rel_data)
panda_resources = getPandaResources(resource)

if (mode == "showPandaQueue"):
    panda_resources.sort()
    for pandaResource in panda_resources: print pandaResource
    sys.exit(0)
if (not panda_resources):
    print "agis-tags: WARNING - no Panda queue found for %s [sitename = %s]" % (resource,site)
    if (mode == "showPandaQueue"): sys.exit(1)
tag_list = []
for m_panda_resource in panda_resources:
    if (mode == "list"):
        rellist = a.list_panda_swreleases(panda_resource=m_panda_resource)
        for relitem in rellist[m_panda_resource]:
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
            if (tag not in tag_list): tag_list.append(tag)
    else:
        for r in reldata:
            if (r):
                rdata = r.split(",")
                if (len(rdata) >= 6):
                    m_project = rdata[3]
                    m_release = rdata[4]
                    m_cmtconfig = rdata[5]
                    # Major releases have 3 digits
                    majrelnum = rel.split('-')[0].split('.')[:3]
                    try:
                        for n in majrelnum: i = int(n)
                        m_major_release = string.join(majrelnum,'.')
                    except:
                        m_major_release = None
                    m_force_create = True
                else:
                    m_project = None
                    m_release = None
                    m_cmtconfig = "noarch"
                    m_major_release = None
                    m_force_create = False
                if (mode == "add"):
                    if (trial):
                        print ("add_panda_swrelease(panda_resource = %s, project = %s, release = %s, cmtconfig = %s, major_release = %s, force_create = %s)" % (m_panda_resource,m_project,m_release,m_cmtconfig,m_major_release,m_force_create))
                    else:
                        if (verbose): print ("add_panda_swrelease(panda_resource = %s, project = %s, release = %s, cmtconfig = %s, major_release = %s, force_create = %s)" % (m_panda_resource,m_project,m_release,m_cmtconfig,m_major_release,m_force_create))
                        a.add_panda_swrelease(panda_resource = m_panda_resource, project = m_project, release = m_release, cmtconfig = m_cmtconfig, major_release = m_major_release, force_create = m_force_create)
                elif (mode == "remove"):
                    if (trial):
                        print ("remove_panda_swrelease(panda_resource = %s, project = %s, release = %s, cmtconfig = %s, major_release = %s, force_create = %s)" % (m_panda_resource,m_project,m_release,m_cmtconfig,m_major_release,m_force_create))
                    else:
                        if (verbose): print ("remove_panda_swrelease(panda_resource = %s, project = %s, release = %s, cmtconfig = %s, major_release = %s, force_create = %s)" % (m_panda_resource,m_project,m_release,m_cmtconfig,m_major_release,m_force_create))
                        a.remove_panda_swrelease(panda_resource = m_panda_resource, project = m_project, release = m_release, cmtconfig = m_cmtconfig, major_release = m_major_release, force_create = m_force_create)

if (mode == "list"):
    tag_list.sort()
    for tag in tag_list:
        print tag
