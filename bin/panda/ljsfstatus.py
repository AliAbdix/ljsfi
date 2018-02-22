#!/usr/bin/env python
###########################
# Get the status of a job
# A. De Salvo - 2013
# LJSFi framework v2.0.0

import os, sys
import ljsfbkk
from ljsfutils import *
from pandatools import Client
import getopt

minproxy=14400
maxproxy=86400
gridproxyhours=200
if (os.environ.has_key('LJSF_MINPROXY_LT')):
  minproxy=int(os.environ['LJSF_MINPROXY_LT'])
if (os.environ.has_key('LJSF_MAXPROXY_LT')):
  maxproxy=int(os.environ['LJSF_MAXPROXY_LT'])
if (os.environ.has_key('LJSF_MAXMYPROXY_LT')):
  myproxyhours=int(os.environ['LJSF_MAXMYPROXY_LT'])
if (os.environ.has_key('LJSF_MAXGRIDPROXY_LT')):
  gridproxyhours=int(os.environ['LJSF_MAXGRIDPROXY_LT'])

__HELP__ = """
Usage: ljsfstatus.py [OPTIONS] <jobfile 1> <jobfile 2> ... <jobfile n>
       OPTIONS:
            -d|--debug          Output debug messages.
            -h|--help           Display this help.
            -n|--nocheck        Do not check for a valid proxy.
            -N|--noout          Suppress output.
"""

class ljsfStatus:
    debug = False
    proxyCheck = True
    utils = None
    bkk   = None
    noout = False

    def __init__(self):
        self.bkk = ljsfbkk.ljsfBKK()
        self.bkk.openDB()

    def setDebug (self, mode):
        # Set the debug mode
        self.debug = mode

    def setProxyCheck (self, mode):
        # Set the proxy check mode
        self.proxyCheck = mode

    def setNoout (self, mode):
        # Set the output verbosity mode
        self.noout = mode

    def getStatus (self, jobs):
        rc = 0
        status = None
        if (not self.utils): self.utils=ljsfUtils()
        if (self.proxyCheck):
            # Check the proxy status
            dn = self.utils.checkProxy(minproxy,maxproxy,myproxyhours,gridproxyhours)
            if (not dn): rc = 1
        if (rc == 0):
            for job in jobs:
                pandaID = None
                jobname = os.path.basename(job)
                if (jobname[-4:] == ".job"): jobname = jobname[:-4]
                if (os.path.exists(job)):
                    jobfile = open(job, "r")
                    jobdata = jobfile.read()
                    if (jobfile):
                        for line in jobdata.split("\n"):
                            if (line[:8] == "PandaID="):
                                pandaID = line[8:]
                                break
                        jobfile.close()
                    if (pandaID):
                        statusInfo = self.getStatusInfo(pandaID)
                        if (statusInfo and not self.noout):
                            print "========== %-50s ==========" % jobname
                            print "%-50s: %s" % ("%s status" % jobname, statusInfo["status"])
                            print "%-50s: %s" % ("%s destination" % jobname, statusInfo["destination"])
                            print "%-50s: %s" % ("%s reached at" % jobname, statusInfo["reachtime"])
                            if (statusInfo.has_key("exitcode")): print "%-50s: %s" % ("%s exit code" % jobname, statusInfo["exitcode"])
        return rc, status

    def getStatusInfo(self, jobID):
        statusInfo = {}
        s,o = Client.getJobStatus([jobID])
        if (s == 0):
            statusInfo["status"] = o[0].jobStatus
            statusInfo["destination"] = o[0].computingSite
            statusInfo["reachtime"] = o[0].creationTime
            if (o[0].transExitCode != "NULL"): statusInfo["exitcode"] = o[0].transExitCode
            self.bkk.reset()
            self.bkk.setJobID(jobID)
            self.bkk.setReachTime(statusInfo["reachtime"])
            self.bkk.setStatus(statusInfo["status"])
            self.bkk.setStatusReason(statusInfo["status"])
            self.bkk.setDestination(statusInfo["destination"])
            self.bkk.setCS(statusInfo["destination"])
            if (statusInfo.has_key("exitcode")): self.bkk.setExitCode(statusInfo["exitcode"])
            self.bkk.writeDB()
        return statusInfo

if __name__ == "__main__":
    ljsfstatus = ljsfStatus()
    short_options = "dhn"
    long_options = ["debug", "help", "nocheck", "noout"]

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                     short_options,
                     long_options,
                     )
    except getopt.GetoptError:
        # Print the help
        print __HELP__ % rm.protocol
        sys.exit(1)
    for cmd, arg in opts:
        if (cmd in ('--help',) or cmd in ('-h',)):
            print __HELP__
            sys.exit(0)
        elif (cmd in ('--debug',) or cmd in ('-d',)):
            ljsfstatus.setDebug(True)
        elif (cmd in ('--nocheck',) or cmd in ('-n',)):
            ljsfstatus.setProxyCheck(False)
        elif (cmd in ('--noout',) or cmd in ('-N',)):
            ljsfstatus.setNoout(True)

    rc, status = ljsfstatus.getStatus(sys.argv[1:])
    sys.exit(rc)

