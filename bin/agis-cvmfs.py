#!/usr/bin/env python
#####################################################################
# AGIS cvmfs tool                                                   #
# LJSFi Framework 1.9.0                                             #
# Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it> - 20120821 #
#####################################################################

__version__ = "$Revision: 1.3 $"[11:-1]

__HELP__="""LJSFi AGIS cvmfs tool %s.
Usage: agis-cvmfs [OPTION]

Options:
  --api                         use AGIS API interface
  --help                        display this help and exit.
  --ce= | -c <CE FQDN>          CE FQDN
  --debug | -d                  debug mode
  --panda-resource= | -R <res>  use Panda resource <res>
  --site= | -s <site name>      site name
  --trial | -T                  trial run
  --verbose | -v                increase verbosity

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
__CACHE_EXPIRY__ = 3600
__CACHE_FILE__   = "/tmp/agis-cvmfs-site-info.tmp"
#__AGIS_SITE_INFO__ = "http://atlas-agis-api-dev.cern.ch/request/pandaqueue/query/list/index.php?json&preset=full&ceaggregation"
#__AGIS_SITE_INFO__ = "http://atlas-agis-api.cern.ch/request/pandaqueue/query/list/index.php?json&preset=full&ceaggregation"
__AGIS_SITE_INFO__ = "http://atlas-agis-api.cern.ch/request/pandaqueue/query/list/index.php?json&preset=schedconf"
__AGIS_REST_URL__  = "https://atlas-agis-api.cern.ch/request/pandaqueue/update/set_attributes/?json&panda_resource=%s&is_cvmfs=%d"
__LJSF_FS_RES_INFO__ = "%s/siteinfo.php?showfs&quiet&cs=%s"
__LJSF_FS_SITE_INFO__ = "%s/siteinfo.php?showfs&quiet&sitename=%s"
refresh = True
short_options = "c:dhqr:R:s:t:Tv"
long_options = ["api", "ce=", "debug", "help", "panda-resource=", "site=", "trial", "verbose"]
debug = False
verbose = False
resource = None
site = None
reldata = None
panda_resources = None
trial = False
mode = 'rest'

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
    elif (cmd in ('--api',)):
        mode = 'api'
    elif (cmd in ('--ce',) or cmd in ('-c',)):
        resource = arg.split(":")[0]
        cs = arg
    elif (cmd in ('--debug',) or cmd in ('-d',)):
        debug = True
    elif (cmd in ('--panda-resource',) or cmd in ('-R',)):
        panda_resources = [arg]
    elif (cmd in ('--site',) or cmd in ('-s',)):
        site = arg
    elif (cmd in ('--trial',) or cmd in ('-T',)):
        trial = True
    elif (cmd in ('--verbose',) or cmd in ('-v',)):
        verbose = True

if (not resource and not site and not panda_resources):
    print "No resource or site specified"
    print __HELP__
    sys.exit(2)

# initialize AGIS
#a=AGIS(hostp='atlas-agis-api-dev.cern.ch:80')
a=AGIS(hostp='atlas-agis-api.cern.ch:80')

c = pycurl.Curl()
c.setopt(c.SSL_VERIFYPEER, 0)
c.setopt(c.WRITEFUNCTION, d.body_callback)
c.setopt(c.CONNECTTIMEOUT, 60)
c.setopt(c.TIMEOUT, 120)

if (os.environ.has_key("LJSFDBURL")): LJSFDBURL="%s/exec" % os.path.dirname(os.environ["LJSFDBURL"])
else:                                 LJSFDBURL="https://atlas-install.roma1.infn.it/atlas_install/exec"
if (not panda_resources):
    # Get the json file from AGIS
    if (os.path.exists(__CACHE_FILE__)):
        now = time.time()
        st = os.stat(__CACHE_FILE__)
        if ((now - st.st_mtime) < __CACHE_EXPIRY__): refresh = False

    if (refresh):
        try:
            c.setopt(c.URL, __AGIS_SITE_INFO__)
            d.reset()
            c.perform()
            outfile = open(__CACHE_FILE__,'w')
            outfile.write(d.contents)
            outfile.close()
        except:
            print "Cannot get AGIS data"
            sys.exit(1)

try:
    if (resource or site or panda_resources):
        d.reset()
        if (panda_resources):
            fsurl = __LJSF_FS_RES_INFO__ % (LJSFDBURL, panda_resources[0])
        elif (resource and not site):
            fsurl = __LJSF_FS_RES_INFO__ % (LJSFDBURL, cs)
        elif (site):
            fsurl = __LJSF_FS_SITE_INFO__ % site
        c.setopt(c.URL, fsurl)
        c.perform()
        fsdata = d.contents.split("\n")
except:
    print "Cannot get LJSFi data"
    sys.exit(1)
c.close()

if (not panda_resources):
    agis_site_info = open(__CACHE_FILE__,'r')
    json_site_data = agis_site_info.read()
    agis_site_info.close()
    agis_site_data = json.loads(json_site_data)
    panda_resources = getPandaResources(resource)
    if (not panda_resources):
        print "agis-cvmfs: WARNING - no Panda resources found for %s" % resource
        sys.exit(1)

for m_panda_resource in panda_resources:
    if (verbose): print "Processing Panda resource %s" % m_panda_resource
    for fs in fsdata:
        if (verbose and fs): print "FS: %s" % fs
        if (fs and fs.lower() == 'cvmfs'):
            if (mode == 'api'):
                if (trial):
                    print ("set_panda_resource(id = %s, is_cvmfs = True)" % m_panda_resource)
                else:
                    if (verbose): print "set_panda_resource(id = %s, is_cvmfs = True)" % m_panda_resource
                    a.set_panda_resource(id = m_panda_resource, is_cvmfs = True)
            else:
                resturl = __AGIS_REST_URL__ % (m_panda_resource, 1)
                if (trial):
                    print (resturl)
                else:
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
                    if (res[0][2]): print res[0][2]
                    c.close()
