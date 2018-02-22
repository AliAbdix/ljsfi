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

HELP="""LJSFi panda submit interface v%s.
Usage: panda-job-submit.py [OPTIONS] <jobdef file>

Options:
  --help                      display this help and exit.
  --config | -s <config-file> use an alternate config file
  --debug | -d                debug mode
  --noout | -n                suppress output
  --server | -s <server>      specify an alternate server
  --trial | -t                trial run, no submission

Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>.
"""

class ljsfPandaSubmit:

    aSrvID = None
    trial  = False
    noout  = False

    def jobSubmit(self,jobdef):
        if (not os.path.exists(jobdef)): return None
        jobdef_file = open(jobdef)
        jobdef_data = json.load(jobdef_file)
        jobdef_file.close()
        if (jobdef_data["JobDef"].has_key("Site")): site = jobdef_data["JobDef"]["Site"]
        else: site = None
        if (jobdef_data["JobDef"].has_key("JobName")):
            jobName = jobdef_data["JobDef"]["JobName"]
        else:
            jobName = os.path.basename(jobdef).replace(".jdl",".%s" % commands.getoutput("uuidgen"))
        if (jobdef_data["JobDef"].has_key("Executable")): jobExec = jobdef_data["JobDef"]["Executable"]
        else: jobExec = 'http://atlas-install.roma1.infn.it/atlas_install/agent/sw-mgr'
        if (jobdef_data["JobDef"].has_key("Arguments")): params = jobdef_data["JobDef"]["Arguments"]
        else: params = ""
        if (jobdef_data.has_key("ResDef")):
            restype   = None
            overrides = []
            if (jobdef_data["ResDef"].has_key("resource_type")): restype = jobdef_data["ResDef"]["resource_type"]
            if (restype == "production"):
                if (jobdef_data["ResDef"].has_key("lfcprodpath")): overrides.append("lfcpath='%s'" % jobdef_data["ResDef"]["lfcprodpath"])
                if (jobdef_data["ResDef"].has_key("seprodpath")):  overrides.append("sepath='%s'" % jobdef_data["ResDef"]["seprodpath"])
            if (overrides):
                if (params): params = "%s --overwriteQueuedata={%s}" % (params, string.join(overrides,","))
                else:        params = "--overwriteQueuedata={%s}" % string.join(overrides,",")

        datasetName = 'panda.install.%s' % jobName.replace("@","_")
        destName    = site

        job = JobSpec()
        job.jobDefinitionID   = int(time.time()) % 10000
        job.jobName           = "%s" % jobName.replace("@","_")
        job.transformation    = jobExec
        job.destinationDBlock = datasetName
        job.destinationSE     = destName
        job.currentPriority   = 4100
        job.prodSourceLabel   = 'install'
        job.computingSite     = site

        job.jobParameters = params

        fileOL = FileSpec()
        fileOL.lfn = "%s.job.log.tgz" % datasetName
        fileOL.destinationDBlock = datasetName
        fileOL.destinationSE     = destName
        fileOL.dataset           = datasetName
        fileOL.type = 'log'
        job.addFile(fileOL)

        if (self.trial):
            fakeJobID = commands.getoutput("uuidgen")
            print "PandaID=%s" % fakeJobID
            print "JobName=%s" % job.jobName
            print "DatasetName=%s" % job.destinationDBlock
            return (0, fakeJobID, job.jobName, job.destinationDBlock)
        else:
            s,o = Client.submitJobs([job])
            if (not self.noout):
                print s
                for x in o:
                    print "PandaID=%s" % x[0]
                    print "JobName=%s" % job.jobName
                    print "DatasetName=%s" % job.destinationDBlock
            return (s, x[0], job.jobName, job.destinationDBlock)

if __name__ == "__main__":
    agent = ljsfPandaSubmit()
    short_options = "c:dhnst"
    long_options = ["config=", "debug", "help", "noout", "server=", "trial"]

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
        elif (cmd in ('--debug',) or cmd in ('-d',)):
            agent.debug = True
        elif (cmd in ('--server',) or cmd in ('-s',)):
            agent.aSrvID = arg
        elif (cmd in ('--config',) or cmd in ('-c',)):
            agent.config = arg
        elif (cmd in ('--noout',) or cmd in ('-n',)):
            agent.noout = True
        elif (cmd in ('--trial',) or cmd in ('-t',)):
            agent.trial = True

    if (len(sys.argv) < 2):
        print "Please supply a valid job description file"
        sys.exit(1)

    rc = 0
    jobdef = args[-1]
    status = agent.jobSubmit(jobdef)
    if (status): rc = status[0]
    sys.exit(rc)
