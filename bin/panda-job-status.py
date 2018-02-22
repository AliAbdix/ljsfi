#!/usr/bin/env python
import sys
import os
import time
import commands
from pandatools import Client
from taskbuffer.JobSpec import JobSpec
from taskbuffer.FileSpec import FileSpec
try:
    import json
except:
    import simplejson as json
import string
import getopt


__version__ = "$Revision: 1 $"[11:-1]

HELP="""LJSFi panda job info interface v%s.
Usage: panda-job-info.py [OPTIONS] <jobID>

Options:
  --help                      display this help and exit.
  --config | -s <config-file> use an alternate config file
  --csv                       use csv output format
  --debug | -d                debug mode
  --server | -s <server>      specify an alternate server

Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>.
"""

aSrvID = None
jobIDs = None
csv    = False
csvout = None
short_options = "c:dj:hs"
long_options = ["config=", "csv", "debug", "jobids=", "help", "server="]

try:
    opts, args = getopt.getopt(sys.argv[1:],
                 short_options,
                 long_options,
                 )
except getopt.GetoptError:
    # Print the help
    print HELP % __version__
    sys.exit(-1)
for cmd, arg in opts:
    if (cmd in ('--help',) or cmd in ('-h',)):
        print HELP % __version__
        sys.exit()
    elif (cmd in ('--csv',)):
        csv = True
    elif (cmd in ('--debug',) or cmd in ('-d',)):
        debug = True
    elif (cmd in ('--server',) or cmd in ('-s',)):
        aSrvID = arg
    elif (cmd in ('--config',) or cmd in ('-c',)):
        config = arg
    elif (cmd in ('--jobids',) or cmd in ('-j',)):
        jobIDs = arg.split(',')

if (len(sys.argv) < 2 and not jobIDs):
    print "Please supply at least a job ID"
    sys.exit(1)

if (not jobIDs): jobIDs = [args[-1]]

s,o = Client.getJobStatus(jobIDs)
for js in o:
    try:
        if (not csv):
            print "JobStatus: %s" % js.jobStatus
            print "ComputingSite: %s" % js.computingSite
            print "CreationTime: %s" % js.creationTime
        else:
            csvout = "%s,%s,%s,%s" % (js.PandaID,js.jobStatus,js.computingSite,js.creationTime)
        if (js.transExitCode != "NULL"):
            if (not csv):
                print "TransExitCode: %s" % js.transExitCode
            else:
                csvout += ",%s" % js.transExitCode
        else:
            if (csv): csvout += ","
        if (js.jobStatus == "failed"):
            diag = []
            if (js.brokerageErrorDiag != "NULL"):     diag.append("[brokerage] %s" % js.brokerageErrorDiag)
            if (js.ddmErrorDiag != "NULL"):           diag.append("[ddm] %s" % js.ddmErrorDiag)
            if (js.jobDispatcherErrorDiag != "NULL"): diag.append("[dispatcher] %s" % js.jobDispatcherErrorDiag)
            if (js.exeErrorDiag != "NULL"):           diag.append("[exe] %s" % js.exeErrorDiag)
            if (js.pilotErrorDiag != "NULL"):         diag.append("[pilot] %s" % js.pilotErrorDiag)
            if (js.supErrorDiag != "NULL"):           diag.append("[sup] %s" % js.supErrorDiag)
            if (js.taskBufferErrorDiag != "NULL"):    diag.append("[taskBuffer] %s" % js.taskBufferErrorDiag)
            if (diag):
                if (not csv):
                    print "ErrorDiag: %s" % string.join(diag,",")
                else:
                    csvout += ",%s" % string.join(diag,"|")
        if (csv and csvout): print csvout
    except:
        if (not csv):
            print "JobStatus: failed"
            print "ErrorDiag: No job info"
        else:
            raise

sys.exit(s)
