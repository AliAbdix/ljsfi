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
import getopt


__version__ = "$Revision: 1 $"[11:-1]

HELP="""LJSFi panda job info interface v%s.
Usage: panda-job-info.py [OPTIONS] <jobID>

Options:
  --help                      display this help and exit.
  --config | -s <config-file> use an alternate config file
  --debug | -d                debug mode
  --server | -s <server>      specify an alternate server

Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>.
"""

aSrvID = None
short_options = "c:dhs"
long_options = ["config=", "debug", "help", "server="]

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
        debug = True
    elif (cmd in ('--server',) or cmd in ('-s',)):
        aSrvID = arg
    elif (cmd in ('--config',) or cmd in ('-c',)):
        config = arg

if (len(sys.argv) < 2):
    print "Please supply a job ID"
    sys.exit(1)

jobIDs = args[-1]
s,o = Client.killJobs(jobIDs.split(","))
sys.exit(s)
