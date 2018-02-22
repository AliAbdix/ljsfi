#!/usr/bin/env python

import getopt
import os, sys
import string
import time
import stat
import signal
import commands
import re
import gfal, lcg_util
import errno, stat
import gzip


#
#########################################################
# GRID BigBrother client module                         #
# Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it #
# v1.0 - 20090725                                       #
#########################################################
#

__version__ = "$Revision: 1 $"[11:-1]
__author__  = "Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>"

HELP="""
gBB - Grid Big Brother client %s.
Usage: gbbc [OPTIONS] <jobid> ...

Options:
  -c|--clean                   clean up the files from the SE.
  -C|--count                   count the partial output files.
  -d|--debug                   print debug messages.
  -g|--get                     retrieve the output (default).
  -h|--help                    display this help and exit.
  -l|--list                    list the partial output files.
  -o|--output <file>           write the output in <file>.
  -r|--request                 request a partial output for this jobid.
  -R|--check-request           check if a partial output has been requested
  -S|--stats                   print the stats of the running processes.
  -s|--surl <SURL>             use <SURL> to dump the partial output.
  -t|--tail <num>              only retrieve the last <num> fragments.
  -T|--temp-dir <path>         use <path> to store temporary files.
  -v|--verbose                 be verbose.
  -z|--compress                compress output files.

%s
"""

__PROXY_INFO__    = "voms-proxy-info -identity --dont-verify-ac 2>/dev/null"
__PARTIALOUT__    = "out.part.*"
__PARTIALSTATS__  = "stats.part.*"
__TMPFILE__       = "%s/gbbc.%d.tmp"

class gBBc:

    # Command line switches
    short_options = "hcCdglo:rRs:St:T:vV:z"
    long_options = ["help",       "check-request", "clean",
                    "compress",   "count",         "debug",
                    "get",        "list",          "output=",
                    "request=",   "stats",         "surl=",
                    "tail=",      "temp-dir=",     "verbose",
                    "vo="]

    # Defaults for actions
    action                   = 'get'
    maxRetries               = 5

    # Other defaults
    outputFileName           = None
    verbose                  = False
    debug                    = False
    SURL                     = None
    tempDir                  = os.getcwd()
    tmpfile                  = lambda self: __TMPFILE__ % (self.tempDir, os.getpid())
    jobID                    = None
    tail                     = 0
    T_FILE                   = 0
    T_DIR                    = 1
    compress                 = False


    def __init__ (self):
        if (os.environ.has_key("GBB_SURL")): self.SURL = os.environ["GBB_SURL"]


    def readOptions(self):
        # Get the command line options
        try:
            opts, args = getopt.getopt(sys.argv[1:],
                         self.short_options,
                         self.long_options,
                         )
        except getopt.GetoptError:
            # Print the help
            self.help()
            sys.exit(-1)

        # Local vars
        cmd=''
        arg=''
        for cmd, arg in opts:
            if cmd in ('--help','-h'):
                self.help()
                sys.exit()
            elif cmd in ('--check-request','-R'):
                self.action = 'checkreq'
            elif cmd in ('--clean','-c'):
                self.action = 'clean'
            elif cmd in ('--compress','-z'):
                self.compress = True
            elif cmd in ('--count','-C'):
                self.action = 'count'
            elif cmd in ('--debug','-d'):
                self.debug = True
            elif cmd in ('--get','-g'):
                self.action = 'get'
            elif cmd in ('--list','-l'):
                self.action = 'list'
            elif cmd in ('--output','-o'):
                self.outputFileName = arg
            elif cmd in ('--request','-r'):
                self.action = 'request'
            elif cmd in ('--stats','-S'):
                self.action = 'stat'
            elif cmd in ('--surl','-s'):
                self.SURL = arg
            elif cmd in ('--tail','-t'):
                self.tail = int(arg)
            elif cmd in ('--temp-dir','-T'):
                self.tempDir = arg
            elif cmd in ('--verbose','-v'):
                self.verbose = True

        if (len(args) > 0): self.jobID = args[0]


    def execute(self):
        if (self.verbose or self.debug):
            sys.stderr.write("GBBC> GriBB client v%s\n" % __version__)
        if (self.debug):
            sys.stderr.write("GBBC> Using temp file %s\n" % self.tmpfile())
        if (not self.SURL):
            sys.stderr.write("GBBC> no SURL specified\n")
            return 100
        if (not self.jobID):
            sys.stderr.write("GBBC> no jobid specified\n")
            return 101
        else:
            self.jobID = self.jobID.split('/')[-1]
        # Get the certificate subject and check if the proxy is valid
        (s,proxyid) = commands.getstatusoutput(__PROXY_INFO__)
        if (s != 0 or proxyid == ''):
            sys.stderr.write("GBBC> cannot retrieve the identity.\n")
            return 102
        identity = re.sub('^_','',re.sub('[^\w]','_',proxyid.replace("/CN=proxy","")))

        # Build the SE path
        SEpath=("%s/%s/%s" % (self.SURL,identity,self.jobID))

        # Check which action to take
        if (self.action == 'clean'):
            if (self.verbose):
                sys.stderr.write("GBBC> cleaning up %s\n" % SEpath)
                sys.stderr.write("GBBC> please wait, this may take a few minutes...\n")
            return self.clean(SEpath)
        elif (self.action == 'get'):
            if (self.verbose):
                sys.stderr.write("GBBC> getting partial output...\n")
            return self.getOutput(SEpath,__PARTIALOUT__)
        elif (self.action == 'count'):
            if (self.verbose):
                sys.stderr.write("GBBC> counting partial output fragments...\n")
            files = self.list(SEpath,__PARTIALOUT__)
            numfiles = 0
            if (files): 
                if (files[0]["status"] == 0):
                    if (files[0].has_key('subpaths')): numfiles = len(files[0]["subpaths"])
            if (self.verbose):
                sys.stderr.write("GBBC> number of partial output fragments: %d\n" % numfiles)
            return numfiles 
        elif (self.action == 'list'):
            if (self.verbose):
                sys.stderr.write("GBBC> listing partial output fragments...\n")
            files = self.list(path=SEpath)
            if (not files): return 1
            for file in files:
                if (file["status"] == 0):
                    if (file.has_key('subpaths')):
                        for subfile in file["subpaths"]:
                            if (subfile["status"] == 0): print subfile["surl"]
            return 0
        elif (self.action == 'request'):
            if (self.verbose):
                sys.stderr.write("GBBC> requesting partial output...\n")
            return self.request(SEpath)
        elif (self.action == 'checkreq'):
            rc = self.isRequested(SEpath)
            if (self.verbose):
                if (rc): sys.stderr.write("GBBC> partial output already requested\n")
                else:    sys.stderr.write("GBBC> no partial output request found\n")
            return rc
        elif (self.action == 'stat'):
            if (self.verbose):
                sys.stderr.write("GBBC> getting the stats of the running processes...\n")
            return self.getOutput(SEpath,__PARTIALSTATS__)
        else:
            sys.stderr.write("GBBC> unknown action.\n")
            return 103


    def getOutput (self, SURL, filter):
        bSURL = SURL.split("=")[0]
        fileList = self.list(path=SURL,filter=filter)
        files = []
        for file in fileList:
            for subpath in file["subpaths"]:
                files.append("%s=%s" % (bSURL,subpath["surl"]))
        if (self.verbose):
            sys.stderr.write("GBBC> %d fragments found.\n" % len(files))
        if (not files): return
        outfd = sys.stdout
        if (self.outputFileName):
            try:
                if (self.compress):
                    outfd = gzip.open(self.outputFileName,"wb",9)
                else:
                    outfd = open(self.outputFileName,'w')
            except:
                sys.stderr.write("GBBC> cannot open %s for writing\n" % self.outputFileName)
                sys.exit(-1)
        if (self.verbose):
            sys.stderr.write("GBBC> merging fragments.\n")
        files.sort()
        index = 0
        for file in files:
            index += 1
            if (index > (len(files)-self.tail) or self.tail == 0):
                tmpfile = self.tmpfile()
                self.get(file,"file:%s" % tmpfile)
                try:
                    infd = open(tmpfile,'r')
                    while 1:
                        line = infd.readline()
                        if (len(line) > 0):
                            outfd.write(line)
                        else:
                            break
                    infd.close()
                except:
                    pass
                try:
                    os.remove(tmpfile)
                except:
                    pass
            else:
                if (self.debug):
                    sys.stderr.write("GBBC> skipping fragment %d.\n" % index)
        if (self.outputFileName): outfd.close()
        return 0


    def clean(self, SURL):
        bSURL = SURL.split("=")[0]
        if (self.exists(SURL)):
            files = self.list(path=SURL)
            for file in files:
                if (file["status"] == 0):
                    # First remove all the files in the directory
                    if (file.has_key("subpaths")):
                        for subfile in file["subpaths"]:
                            if (subfile["status"] == 0):
                                fSURL = "%s=%s" % (bSURL,subfile["surl"])
                                if (stat.S_ISDIR(subfile["stat"][stat.ST_MODE])): self.clean(fSURL)
                                else: self.unlink(path=fSURL,type=self.T_FILE)
                # Now remove the directory or file itself
                fSURL = "%s=%s" % (bSURL,file["surl"])
                if (self.debug): sys.stderr.write("GBBC> removing SURL %s\n" % fSURL)
                if (stat.S_ISDIR(file["stat"][stat.ST_MODE])): unlinkType = self.T_DIR
                else:                                          unlinkType = self.T_FILE
                self.unlink(path=fSURL,type=unlinkType) 


    def isRequested(self, SURL):
        return self.exists(SURL)


    def request(self, SURL):
        if (self.exists(SURL)):
            sys.stderr.write("GBBC> Partial output already requested.\n")
            return 1
        if (self.mkdir(SURL) == 0):
            if (self.debug): sys.stderr.write("GBBC> Request successful.\n")
            return 0
        else:
            sys.stderr.write("GBBC> Unable to request partial output.\n")
            return 2


    def get(self,source,dest):
        nbstreams = 1
        (rc,errmsg) = lcg_util.lcg_cp3(source,dest,lcg_util.TYPE_NONE,lcg_util.TYPE_NONE,lcg_util.TYPE_NONE,0,None,nbstreams,None,0,0,200,None,None)
        if (rc != 0):
            sys.stderr.write("GBBC> copy failed: %s\n" % errmsg)
            return 1
        return 0


    def list(self,path,filter=None):
        gfalreq = {"srmv2_lslevels":1, "surls":[path]}
        if (self.debug): sys.stderr.write("GBBC> listing %s\n" % path)
        returnCode, gfalObj, errMsg = gfal.gfal_init(gfalreq)
        returnCode, gfalObj, errMsg = gfal.gfal_ls(gfalObj)
        returnCode, gfalObj, statuses = gfal.gfal_get_results(gfalObj)
        gfal.gfal_internal_free(gfalObj)
        listing = []
        if (filter):
            if (self.debug): sys.stderr.write("GBBC> filtering with %s\n" % filter)
            p = re.compile(filter)
        for status in statuses:
            sublisting = []
            if (status["status"] == 0):
                if (status.has_key("subpaths")):
                    for subpath in status["subpaths"]:
                        spSURL = os.path.basename(subpath["surl"])
                        if (not filter or (filter and p.match(spSURL))): sublisting.append(subpath)
            if (not filter or (filter and sublisting)):
                matchedlist = status
                if (sublisting): matchedlist["subpaths"] = sublisting
                listing.append(matchedlist)
        return listing

    def exists(self,path):
        if (self.debug): sys.stderr.write("GBBC> checking %s\n" % path)
        rc = gfal.gfal_access(path,os.F_OK)
        if (rc == 0):
            return True
        else:
            if (gfal.gfal_get_errno() == errno.ENOENT):
                return False
            else:
                return True

    def mkdir(self,dir):
        gfalreq = {}
        validSURL = False
        SURL = dir.split("=")
        SURLS = []
        while (not validSURL):
            newSURL = "%s=%s" % (SURL[0],SURL[1])
            if (self.exists(newSURL)):
                validSURL = True
            else:
                SURLS.append("%s=%s/" % (SURL[0],SURL[1]))
                newpath = os.path.dirname(SURL[1])
                if (newpath != SURL[1]):
                    SURL[1] = newpath
                else:
                    sys.stderr.write("GBBC> cannot find any suitable SURL\n")
                    break

        if (validSURL):
            SURLS.reverse()
            for SURL in SURLS:
                if (self.debug): sys.stderr.write("GBBC> creating %s\n" % SURL)
                rc = gfal.gfal_mkdir(SURL,0775)
                if (rc != 0):
                    sys.stderr.write("GBBC> cannot create %s\n" % SURL)
        return 0

    def unlink(self,path,type):
        attempt = 0
        while 1:
            if (type == self.T_FILE): rc = gfal.gfal_unlink(path)
            else:                     rc = gfal.gfal_rmdir(path)
            if (rc == 0):
                return rc
            elif (attempt < self.maxRetries):
                attempt = attempt + 1
                sys.stderr.write("GBBC> file unlink failed. Retrying [%d]\n" % attempt)
                sys.stderr.write("GBBC> last error: %d\n" % rc)
                time.sleep(1)
            else:
                sys.stderr.write("GBBC> file unlink failed, error code: %d\n" % rc)
                return rc

    def help(self):
        # Print the help
        print HELP % (__version__.strip(), __author__)
