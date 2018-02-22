#!/usr/bin/env python2.5

from agis.api.AGIS import AGIS
import sys, getopt
import pycurl

class Data:
    def __init__(self):
        self.contents = ''

    def body_callback(self, buf):
        self.contents = self.contents + buf

    def reset(self):
        self.contents = ''


d = Data()

# initialize AGIS
a=AGIS(hostp='atlas-agis-api-dev.cern.ch:80')

short_options = ""
long_options = ["site=",]

try:
    opts, args = getopt.getopt(sys.argv[1:],
                   short_options,
                   long_options,
                   )
except getopt.GetoptError:
    sys.exit(-1)

siteinfo = "https://atlas-install.roma1.infn.it/atlas_install/exec/siteinfo.php?%s"
sitename = None

for cmd, arg in opts:
    if cmd in ('--site',):
        sitename = arg

# get the list of sites
sites=a.list_sites(site=sitename, extra_fields=['cloud', 'tier_level', 'rc'])

c = pycurl.Curl()
c.setopt(c.SSL_VERIFYPEER, 0)
c.setopt(c.WRITEFUNCTION, d.body_callback)
for cloud in sites.keys():
    for site in sites[cloud]:
        tier_level = int(site.tier_level)
        site_name = str(site.name)
        print "NAME: %s" % site_name
        hascvmfs = "showfs&sitename=%s" % site_name
        showfs = siteinfo % hascvmfs
        c.setopt(c.URL, showfs)
        d.reset()
        c.perform()
        if (len(d.contents) > 1):
            entries = d.contents.split("\n")
        else:
            entries = None
        if (entries):
            cvmfs = False
            for entry in entries:
                if (entry):
                    (site,fstype) = entry.split()
                    if (fstype == "cvmfs"): cvmfs = True
            getattr_data = "T%s" % tier_level
            if (cvmfs): getattr_data = "%s,CVMFS" % getattr_data
            getattr_query = "getattr=%s" % getattr_data
            getattr = siteinfo % getattr_query
            d.reset()
            c.setopt(c.URL, getattr)
            c.perform()
            attr = int(d.contents)
            print "ATTR: %s (%d)" % (getattr_data,attr)
            showattr_query = "showattr&sitename=%s" % site_name
            showattr = siteinfo % showattr_query
            c.setopt(c.URL, showattr)
            d.reset()
            c.perform()
            try:
                (sitename,currattr,desc) = d.contents.split()
                print "CURR_ATTR: %s (%d)" % (desc,int(currattr))
            except:
                print "CURR_ATTR: None (0)"
            setattr_query = "setattr=%d&sitename=%s" % (attr,site_name)
            setattr = siteinfo % setattr_query
            print "SET_ATTR: %s (%d)" % (getattr_data,attr)
            c.setopt(c.URL, setattr)
            d.reset()
            c.perform()
            print d.contents
c.close()
