#!/usr/bin/env python

from SOAPpy import *
import sys, os
import ConfigParser
import signal
import getopt
import thread
import socket
import commands
import random
import string
import cgi
import time
import struct
import re
from mailsend import *
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from ljsfutils import *
from ljsflog import LJSFlog
from gbbc import gBBc


#####################################################################
# AutoInstall agent                                                 #
# LJSFi Framework 1.9.0                                             #
# Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it> - 20090717 #
#####################################################################

__version__ = "$Revision: 1 $"[11:-1]

HELP="""AutoInstall agent %s.
Usage: autoinstall.py [OPTION]

Options:
  --help                      display this help and exit.
  --debug | -d                debug mode
  --drain | -D                draining mode

Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>.
"""

__GET_OUTPUT__               = 'get-output -n -u %s'
#__GET_OUTPUT_COMPRESS__      = 'get-output -n -u -z %s'
__GET_OUTPUT_COMPRESS__      = 'multi-get-output %s'
__GET_AUTO_REQUESTS__        = 'ljsfreq.py --query --status=%s --grid-name=%s --facility=%s'
__GET_RELEASE_DATA__         = {
                                1: 'ljsfreq.py --queryrel --rel="%s" --create-conf="%s" --ns="%s" --lb="%s" --ld="%s" --wmproxy="%s" --myproxy="%s" --create-wmsvoconf="%s" --create-wmscmdconf="%s"'
                               ,2: 'ljsfinfo.py --queryrel="%s" --create-conf="%s" --ns="%s" --lb="%s" --ld="%s" --wmproxy="%s" --myproxy="%s" --create-wmsvoconf="%s" --create-wmscmdconf="%s"'
                               }
__GET_JOB_NAME__             = 'ljsfbkk.py --select=job.name --request="%s" --validation=pending --quiet --last=1'
__SUBMIT_JOB__               = {
                                1: 'release-manager -s -A %s -r %s -c %s %s %s %s'
                               ,2: 'release-manager -s -a -A %s -r %s -c %s %s %s %s'
                               }
__SUBMIT_JOB_TRIAL__         = {
                                1: 'release-manager -A %s -r %s -c %s %s %s %s'
                               ,2: 'release-manager -a -A %s -r %s -c %s %s %s %s'
                               }
__CANCEL_JOB__               = 'cancel-job -y %s'
__SUBMIT_JOB_NOCHECK__       = {
                                1: 'release-manager -s -n -A %s -r %s -c %s %s %s %s'
                               ,2: 'release-manager -s -n -a -A %s -r %s -c %s %s %s %s'
                               }
__SUBMIT_JOB_NOCHECK_TRIAL__ = {
                                1: 'release-manager -n -A %s -r %s -c %s %s %s %s'
                               ,2: 'release-manager -a -n -A %s -r %s -c %s %s %s %s'
                               }
__CHANGE_REQ_STAT__          = 'ljsfreq.py --update --reqid="%s" --status="%s" --comments="%s"'
__TASKMAP__                  = {
                                1: {'validation'   : 4
                                   ,'installation' : 5
                                   ,'test'         : 6
                                   ,'removal'      : 7
                                   ,'cleanup'      : 8
                                   ,'publish-tag'  : 9
                                   ,'remove-tag'   : 10}
                               ,2: {}
                               }
__COUNT_PENDING_JOBS__       = 'ljsfbkk.py --select="count" --validation=pending --quiet'
__COUNT_INSTANCE_JOBS__      = 'ljsfbkk.py --select="count(*)" --validation=pending --quiet --user="%s"'
__GET_TASK_TOKENS__          = 'ljsfinfo.py --show-task-tokens'

# Print a message
def msgOut (message):
    print "[%s] %s: %s" % (time.asctime(),"AutoInstaller",message)
    sys.stdout.flush()

class AutoInstall:

    short_options = "dDh"
    long_options = ["debug", "drain", "help"]

    protocol       = 2
    wsport         = None
    ui             = None
    uiport         = None
    debug          = False
    drain          = False
    shutdown       = False
    status         = 'starting'
    proxyTimeLeft  = 0
    partialReq     = True

    ident          = os.getlogin() + "@" + socket.gethostname()

    numrequests    = 0
    numjobs        = 0

    max_inst_jobs  = 4000

    mode           = "production"
    adminEmail     = None

    # Initialization function
    def __init__(self):
        # Parse the command line options
        try:
            opts, args = getopt.getopt(sys.argv[1:],
                         self.short_options,
                         self.long_options,
                         )
        except getopt.GetoptError:
            # Print the help
            self.help()
            sys.exit(-1)
        for cmd, arg in opts:
            if (cmd in ('--help',) or cmd in ('-h',)):
                self.help()
                sys.exit()
            elif (cmd in ('--debug',) or cmd in ('-d',)):
                self.setDebug(True)
                msgOut("Starting in debug mode")
            elif (cmd in ('--drain',) or cmd in ('-D',)):
                self.setDrain(True)
                msgOut("Starting in draining mode")

    # Start auto installer
    def start (self, maxproxy, timeleft, interval, compress, dirs, sitechecks, wmsns, wmslb, wmsld,wmswmproxy, wmsmyproxy, mode, adminEmail, gridName, facility):
        auth_type = ['grid',None]
        self.mode = mode
        self.adminEmail = adminEmail
        if (os.environ.has_key('LJSFAUTHTYPE')):
            ljsfauth=os.environ['LJSFAUTHTYPE'].lower().split(':')
            auth_type[0]=ljsfauth[0]
            if (len(ljsfauth) > 1): auth_type[1]=ljsfauth[1]
        utils=ljsfUtils()
        ljsflog = LJSFlog()
        gbbc = gBBc()
        gbbc.compress = True
        if (self.debug): msgOut("Interval time = %d s" % interval)
        if (self.protocol > 1):
            # Use a dynamic map for protocols higher that v1
            (s,o) = commands.getstatusoutput(__GET_TASK_TOKENS__)
            if (s == 0):
                for tokenData in o.split("\n"):
                    tokens = tokenData.split(":")
                    __TASKMAP__[self.protocol][tokens[0].strip()] = tokens[1].strip()
                if (self.debug): msgOut("TASKMAP: %s" % __TASKMAP__[self.protocol])
            else:
                msgOut("Cannot load task map. Exiting")
                sys.exit(10)
        # Count the pending jobs
        self.countPendingJobs()
        # Start the infinite loop
        while not self.shutdown:
            self.status = 'checking proxy'
            self.proxyTimeLeft = utils.getProxyLifetime()
            if (self.debug): msgOut("Proxy time left: %d (%d)" % (self.proxyTimeLeft,timeleft))
            if (self.proxyTimeLeft > timeleft):
                if (self.debug): msgOut("Proxy is good")
            elif (self.proxyTimeLeft > 0 and (auth_type[0] == 'myproxy' or (auth_type[0] == 'grid' and auth_type[1] == 'voms'))):
                if (self.debug): msgOut("Renewing proxy")
                self.status = 'renewing proxy'
                rc = utils.renewProxy(auth_type,maxproxy,timeleft)
                tl = utils.getProxyLifetime()
                fromAddress   = "LJSFi AutoInstall agent <%s>" % self.ident
                notifySubject = "[LJSFi AI] Proxy renewal"
                notifyMessage = "LJSFi AutoInstall agent %s\nProxy time left is %d s, renewing proxy.\nNew proxy lifetime is %d s." % (self.ident,self.proxyTimeLeft,tl)
                if (rc == 0):
                    notifyMessage = "%s\nRenewal successful" % notifyMessage
                else:
                    notifyMessage = "%s\nRenewal failed, see logfile for details" % notifyMessage
                mailSend(fromaddr=fromAddress,toaddr=self.adminEmail,subj=notifySubject, msg=notifyMessage)
                if (self.debug): msgOut("Notification mail sent")
            else:
                if (self.debug): msgOut("Proxy is running out, sending the notification mail")
                fromAddress   = "LJSFi AutoInstall agent <%s>" % self.ident
                notifySubject = "[LJSFi AI] Proxy time left is %d" % self.proxyTimeLeft
                notifyMessage = "LJSFi AutoInstall agent %s\nProxy time left is %d s" % (self.ident,self.proxyTimeLeft)
                mailSend(fromaddr=fromAddress,toaddr=self.adminEmail,subj=notifySubject, msg=notifyMessage)
                if (self.debug): msgOut("Notification mail sent")
            self.proxyTimeLeft = utils.getProxyLifetime()
            if (self.proxyTimeLeft > timeleft):
                if not self.drain:
                    # Get the number of jobs handled by this instance
                    cmd = (__COUNT_INSTANCE_JOBS__ % self.ident)
                    if (self.debug): msgOut("Executing %s" % __COUNT_INSTANCE_JOBS__)
                    (s,o) = commands.getstatusoutput(cmd)
                    if (s==0): instance_jobs = int(o)
                    else:      instance_jobs = 0
                    if (instance_jobs <= self.max_inst_jobs):
                        # Get the autorun requests
                        self.status = 'getting autorun requests'
                        requests = self.getRequests(wmsns, wmslb, wmsld, wmswmproxy, wmsmyproxy, 'autorun', gridName, facility)
                        if (self.debug): msgOut("Got %d autorun requests for grid type '%s' [%s]" % (len(requests),gridName,facility))
                        reqindx = 0
                        for request in requests:
                            reqindx+=1
                            self.status = 'processing autorun requests (%d/%d)' % (reqindx,self.numrequests)
                            if (self.debug): msgOut("Processing autorun request for %s %s %s" % (request['type'], request['rel'], request['ce']))
                            # Define and submit the jobs
                            s = self.submitJob(sitechecks, request)
                            if (s==0):
                                self.changeRequestStatus(request,'accepted')
                    else:
                        self.status = 'draining (%d jobs)' % instance_jobs
                        if (self.debug): msgOut("Number of handled jobs: %d. Draining." % instance_jobs)
                else:
                    if (self.debug):
                        msgOut("Not processing new autorun requests because the drain mode is active.")
                # Get the autoabort requests
                self.status = 'getting autoabort requests'
                requests = self.getRequests(wmsns, wmslb, wmsld, wmswmproxy, wmsmyproxy, 'autoabort', gridName, facility)
                if (self.debug): msgOut("Got %d autoabort requests for grid type '%s' [%s]" % (len(requests),gridName,facility))
                reqindx = 0
                for request in requests:
                    reqindx+=1
                    self.status = 'processing autoabort requests (%d/%d)' % (reqindx,self.numrequests)
                    if (self.debug): msgOut("Processing autoabort request for %s %s %s" % (request['type'], request['rel'], request['ce']))
                    # Cancel the jobs associated to this request
                    s = self.cancelJob(dirs,request)
                    if (s==0):
                        self.changeRequestStatus(request,'aborting')
                # Get the partial log dump requests
                if (self.partialReq):
                    try:
                        logreqs = ljsflog.sendData('logreq')
                        if (self.debug): msgOut("%d partial log request(s) found" % len(logreqs))
                        for logreq in logreqs:
                            parts = logreq.split(",")
                            if (len(parts) <= 2):
                                if (self.debug): msgOut("No job id associated to the partial log request")
                            else:
                                lrfrags = int(logreq.split(",")[1])
                                lrjobid = logreq.split(",")[2]
                                if (self.debug): msgOut("Partial log request for job id %s" % lrjobid)
                                gbbc.action = 'checkreq'
                                gbbc.jobID  = lrjobid
                                if (not gbbc.execute()):
                                    msgOut("Requesting partial log for job id %s" % lrjobid)
                                    gbbc.action = 'request'
                                    rc = gbbc.execute()
                                    if (rc == 0):
                                        msgOut("Partial log requested successfully")
                                    else:
                                        msgOut("Cannot request partial log")
                                else:
                                    gbbc.action = 'count'
                                    currfrags = gbbc.execute()
                                    if (currfrags > lrfrags):
                                        fragsToGo = currfrags - lrfrags
                                        msgOut("%d new fragment(s) available for job id %s" % (fragsToGo,lrjobid))
                                        gbbc.action = 'get'
                                        gbbc.tail = fragsToGo
                                        msgOut("Getting the last %d log fragment(s) of job id %s" % (fragsToGo,lrjobid))
                                        gbbc.outputFileName = "/tmp/gbbc.dump.%d.gz" % os.getpid()
                                        rc = gbbc.execute()
                                        if (rc == 0 and os.path.exists(gbbc.outputFileName)):
                                            msgOut("Uploading the last %d log fragment(s) of job id %s" % (fragsToGo,lrjobid))
                                            ljsflog.set('jobid',lrjobid)
                                            ljsflog.set('logfile',gbbc.outputFileName)
                                            ljsflog.set('fragment',currfrags)
                                            ljsflog.sendData('upload')
                                            ljsflog.unset('jobid')
                                            ljsflog.unset('logfile')
                                            ljsflog.unset('fragment')
                                        if (os.path.exists(gbbc.outputFileName)): os.remove(gbbc.outputFileName)
                                        gbbc.tail = 0
                                        gbbc.outputFileName = None
                                    else:
                                        if (self.debug): msgOut("No new fragments available for job id %s (current: %d, sent: %d)" % (lrjobid, currfrags, lrfrags))
                    except:
                        msgOut("Cannot handle partial dump requests")
                # Count the pending jobs
                self.countPendingJobs()
                # Get the job output
                self.status = 'getting output'
                self.getOutput(compress,dirs)
                # Count the pending jobs
                self.countPendingJobs()

            self.proxyTimeLeft = utils.getProxyLifetime()
            if (self.proxyTimeLeft > interval):
                self.status = 'waiting'
                if (self.debug): msgOut("Sleeping %d seconds..." % interval)
                intervals = int(interval/0.5)
                for num in range(0,intervals):
                    time.sleep(0.5)
                    if self.shutdown: break
            else:
                self.status = 'exiting'
                msgOut("Proxy time left is %d s." % self.proxyTimeLeft)
                msgOut("Exiting AutoInstall agent...")
                self.shutdown = True
        if (self.debug): msgOut("Exiting AutoInstall agent...")

    def getRequests(self, ns, lb, ld, wmproxy, myproxy, reqtype='autorun', gridName='ALL', facility='ALL'):
        requests=[]
        cmd = __GET_AUTO_REQUESTS__ % (reqtype,gridName,facility)
        if (self.debug):
            msgOut("Executing %s" % cmd)
        (s,o) = commands.getstatusoutput(cmd)
        if (s==0):
            for req in o.split("\n"):
                request={}
                if (self.debug):
                    msgOut("REQ [%s]: %s" % (reqtype,req))
                if (len(req.split(",")) >= 5):
                    request['id']      = req.split(",")[0]
                    request['type']    = req.split(",")[2]
                    request['rel']     = req.split(",")[3]
                    request['ce']      = req.split(",")[4]
                    request['cs']      = req.split(",")[5]
                    request['ns']      = req.split(",")[11]
                    request['lb']      = req.split(",")[12]
                    request['ld']      = req.split(",")[13]
                    request['wmproxy'] = req.split(",")[14]
                    request['myproxy'] = req.split(",")[15]
                    request['adminid'] = req.split(",")[17]
                    if (not request.has_key('ns')): request['ns'] = ns
                    if (not request.has_key('lb')): request['lb'] = lb
                    if (not request.has_key('ld')): request['ld'] = ld
                    if (not request.has_key('wmproxy')): request['wmproxy'] = wmproxy
                    if (not request.has_key('myproxy')): request['myproxy'] = myproxy
                    requests.append(request)
            self.numrequests = len(requests)
        else:
            msgOut("Cannot get requests")
            self.numrequests = 0
        return requests

    def submitJob(self, sitechecks, request):
        if (self.debug):
            msgOut("Installing release %s in %s" % (request['rel'],request['ce']))
        tmpconf = ("/tmp/install.conf.%d" % int(random.random()*100000))
        tmpwmsvoconf = ("/tmp/wmsvo.conf.%d" % int(random.random()*100000))
        tmpwmscmdconf = ("/tmp/wmscmd.conf.%d" % int(random.random()*100000))
        (s,o) = commands.getstatusoutput(__GET_RELEASE_DATA__[self.protocol] % (request['rel'],tmpconf,request['ns'],request['lb'],request['ld'],request['wmproxy'],request['myproxy'],tmpwmsvoconf,tmpwmscmdconf))
        msgOut (__GET_RELEASE_DATA__[self.protocol] % (request['rel'],tmpconf,request['ns'],request['lb'],request['ld'],request['wmproxy'],request['myproxy'],tmpwmsvoconf,tmpwmscmdconf))
        reldata = o.split("\n")[0].split(",")
        if (s==0 and __TASKMAP__[self.protocol].has_key(request['type'])):
            if (self.protocol == 1):
                # Get the task data for protocol v1
                task = reldata[__TASKMAP__[self.protocol][request['type']]]
            else:
                # Get the task data for protocols higher than v1
                task = None
                p = re.compile('"%s=([^"]*)"' % __TASKMAP__[self.protocol][request['type']])
                for relinfo in reldata:
                    m = p.search(relinfo)
                    if (m): task = m.group(1)
            if (sitechecks):
                if (self.mode == "trial"):
                    cmd = (__SUBMIT_JOB_TRIAL__[self.protocol] % (request['adminid'],request['id'],tmpconf,task,request['rel'],request['cs']))
                else:
                    cmd = (__SUBMIT_JOB__[self.protocol] % (request['adminid'],request['id'],tmpconf,task,request['rel'],request['cs']))
            else:
                if (self.mode == "trial"):
                    cmd = (__SUBMIT_JOB_NOCHECK_TRIAL__[self.protocol] % (request['adminid'],request['id'],tmpconf,task,request['rel'],request['cs']))
                else:
                    cmd = (__SUBMIT_JOB_NOCHECK__[self.protocol] % (request['adminid'],request['id'],tmpconf,task,request['rel'],request['cs']))
            if (self.mode == "trial"): msgOut("TRIAL MODE: %s" % cmd)
            if (self.debug): msgOut("Executing %s" % cmd)
            (s,o) = commands.getstatusoutput(cmd)
            print o
            if (s!=0):
                msgOut("Failed to submit job")
        else:
            msgOut("Unable to get release data. Last command:")
            msgOut(__GET_RELEASE_DATA__[self.protocol] % (request['rel'],tmpconf,request['ns'],request['lb'],request['ld'],request['wmproxy'],request['myproxy'],tmpwmsvoconf,tmpwmscmdconf))

        try:
            pass
            os.remove(tmpconf)
            os.remove(tmpwmsvoconf)
            os.remove(tmpwmscmdconf)
        except:
            pass

        return s

    def cancelJob(self, dirs, request):
        if (self.debug):
            msgOut("Canceling the jobs associated to the request ID %s" % request['id'])
        (s,o) = commands.getstatusoutput(__GET_JOB_NAME__ % request['id'])
        jobname = o.split("\n")[0]
        if (s==0):
            jobfile = None
            for dir in dirs.split(":"):
                jobfn = os.path.expandvars("%s/%s" % (dir,jobname))
                if (os.path.exists(jobfn)): jobfile = jobfn
            if (jobfile):
                msgOut("Canceling job from file %s" % jobfile)
                cmd = __CANCEL_JOB__ % jobfile
                if (self.debug): msgOut("Executing %s" % cmd)
                (s,o) = commands.getstatusoutput(cmd)
                print o
                if (s!=0):
                    msgOut("Failed to cancel job")
            else:
                msgOut("No job file found for %s in %s" % (jobname,dirs))
                s = 1
        else:
            msgOut("Unable to get the job name. Last command:")
            msgOut(__GET_JOB_NAME__ % request['id'])

        return s

    def changeRequestStatus(self, request, status):
        if (self.debug):
            msgOut('Changing request status to "%s"' % status)
        cmd = (__CHANGE_REQ_STAT__ % (request['id'], status, "Processing request"))
        if (self.debug):
            msgOut("Executing %s" % cmd)
        (s,o) = commands.getstatusoutput(cmd)
        print o
        if (s!=0 and self.debug):
            msgOut("Failed to change the request status")
        return s

    def getOutput(self, compress, dirs):
        if (self.debug): msgOut('Scanning directories:')
        for dir in dirs.split(":"):
            jobs = "%s/*" % dir
            if (self.debug): msgOut("Scanning %s..." % dir)
            cmd = ""
            if (compress):
                cmd = (__GET_OUTPUT_COMPRESS__ % jobs)
            else:
                cmd = (__GET_OUTPUT__ % jobs)
            if (self.debug): msgOut("Executing %s" % cmd)
            (s,o) = commands.getstatusoutput(cmd)
            print o

    def countPendingJobs(self):
        if (self.debug): msgOut('Counting pending jobs')
        cmd = (__COUNT_PENDING_JOBS__)
        if (self.debug): msgOut("Executing %s" % __COUNT_PENDING_JOBS__)
        (s,o) = commands.getstatusoutput(cmd)
        if (s==0):
            try:
                self.numjobs=int(o)
            except:
                msgOut('Error counting jobs: %s' % o)
                self.numjobs=0
        else:
            self.numjobs=0

    # Set the debug mode
    def setDebug (self, mode):
        self.debug = mode

    # Set the draining mode
    def setDrain (self, mode):
        self.drain = mode

    def startWebService (self, port):
        # Start the control web service
        self.wsport = port
        tid = thread.start_new_thread(self.webService,())

    def webService (self):
        ws = SOAPServer(("", self.wsport))
        if (self.debug):
            msgOut("AutoInstall WebService started at %s:%d" % (socket.gethostname(),self.wsport))
        # Register the functions
        ws.registerFunction(self.close)
        # Loop over the requests
        ws.serve_forever()

    def startWebUI (self, port):
        # Start the control web UI
        self.uiport = port
        tid = thread.start_new_thread(self.webUI,())

    def webUI (self):
        self.ui = StoppableHTTPServer(('', self.uiport), AutoInstallWebHandler)
        if (self.debug):
            msgOut("AutoInstall WebUI started at %s:%d" % (socket.gethostname(),self.uiport))
        self.ui.serve()
        if (self.debug):
            msgOut("AutoInstall WebUI stopped")

    def close (self):
        if (self.debug):
            msgOut("Shutting down")
        self.shutdown = True
        if (self.ui): self.ui.run = False
        return 0


class StoppableHTTPServer(HTTPServer):

    def server_bind(self):
        HTTPServer.server_bind(self)
        timeout=10.0
        #tv = struct.pack('ii', int(timeout), int((timeout-int(timeout))*1e6))
        #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, tv)
        #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, tv)
        self.socket.settimeout(timeout)
        self.run = True

    def get_request(self):
        while self.run:
            try:
                sock, addr = self.socket.accept()
                sock.setblocking(1)
                return (sock, addr)
            except:
                raise

    def stop(self):
        self.run = False

    def serve(self):
        while self.run:
            self.handle_request()
        self.socket.close()


class AutoInstallWebHandler(BaseHTTPRequestHandler):

    def show_page(self,code=200):
        if (self.path == "/"): self.path="/index.html"
        try:
            if (self.path.endswith(".html") or self.path.endswith(".css")):
                if (os.environ.has_key('LJSFWWWPATH')):
                    wwwhome = os.environ['LJSFWWWPATH']
                else:
                    wwwhome = curdir
                f = open(wwwhome + sep + self.path)
                self.send_response(code)
                if self.path.endswith(".html"):
                    self.send_header('Content-type','text/html')
                    self.end_headers()
                page = f.read()
                page = page.replace("@DATE@",time.asctime())
                page = page.replace("@JOBS@",str(agent.numjobs))
                page = page.replace("@REQUESTS@",str(agent.numrequests))
                page = page.replace("@STATUS@",agent.status)
                page = page.replace("@PROXYTL@",str(agent.proxyTimeLeft))
                page = page.replace("@IDENT@",agent.ident)
                self.wfile.write(page)
                f.close()
                return
            return

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

    def do_GET(self):
        self.show_page()

    def do_POST(self):
        global rootnode
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                query=cgi.parse_multipart(self.rfile, pdict)
            upfilecontent = query.get('upfile')
            stop_btn = query.get('stop')
            if (stop_btn): agent.close()
            self.show_page(301)

        except :
            pass


###################################################

agent = AutoInstall()

# Private signal handler
def signal_handler(signal, frame):
    agent.close()

try:
     MAXFD = os.sysconf('SC_OPEN_MAX')
except:
     MAXFD = 256

def createDaemon(logfile='/dev/null'):
    """Detach a process from the controlling terminal and run it in the
    background as a daemon.
    """

    try:
        pid = os.fork()
    except OSError, e:
        return ((e.errno, e.strerror))

    if (pid == 0):              # This is the first child
        # Become the session leader of this new session
        os.setsid()
        # Ignore the SIGHUP sent by the first child when closing
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        # Fork a second child, preventing the first child to acquire a terminal
        try:
            pid=os.fork()
        except OSError, e:
            return ((e.errno, e.strerror))

        if (pid == 0):          # This is the second child
            # Give the child complete control over permissions.
            os.umask(0)
            log = open(logfile, 'a+')
            fin = open('/dev/null', 'r')
            os.dup2(fin.fileno(), sys.stdin.fileno())
            os.dup2(log.fileno(), sys.stdout.fileno())
            os.dup2(log.fileno(), sys.stderr.fileno())
            for i in range(3, MAXFD):
                try:    os.close(i)
                except: pass
        else:
            sys.exit(0)      # Exit parent (the first child)
    else:
        sys.exit(0)          # Exit parent of the first child

    return (0)



# main class
if __name__ == '__main__':
    # Defaults
    protocol   = 2
    wsport     = None
    interval   = 300
    maxproxy   = 86400
    timeleft   = 300
    dirs       = "$JOBSPATH"
    compress   = False
    sitechecks = True
    conffile   = "autoinstall.conf"
    logfile    = "log/%s/autoinstall-%s.log" % (time.strftime("%Y%m%d-%H%M"),socket.gethostname())
    wmsns      = ""
    wmslb      = ""
    wmsld      = ""
    wmswmproxy = ""
    wmsmyproxy = ""
    mode       = "production"
    adminEmail = None
    gridName   = 'ALL'
    facility   = 'ALL'
    partialReq = True

    # Parse the configuration file
    config = ConfigParser.ConfigParser()
    if (os.environ.has_key('CONFPATH')):
        conffile = "%s/%s" % (os.environ['CONFPATH'],conffile)
    try:
        config.read(conffile)
        if (config.has_section("autoinstall")):
            if (config.has_option("autoinstall", "protocol")):
                if (config.get("autoinstall", "protocol") == "1"): protocol = 1
            if (config.has_option("autoinstall", "wsport")):
                wsport = int(config.get("autoinstall", "wsport"))
            if (config.has_option("autoinstall", "uiport")):
                uiport = int(config.get("autoinstall", "uiport"))
            if (config.has_option("autoinstall", "interval")):
                interval = int(config.get("autoinstall", "interval"))
            if (config.has_option("autoinstall", "minproxy")):
                timeleft = int(config.get("autoinstall", "minproxy"))
            if (config.has_option("autoinstall", "maxproxy")):
                maxproxy = int(config.get("autoinstall", "maxproxy"))
            if (config.has_option("autoinstall", "dirs")):
                dirs = config.get("autoinstall", "dirs")
            if (config.has_option("autoinstall", "compress")):
                if (config.get("autoinstall", "compress").lower() == "y"):
                    compress = True
            if (config.has_option("autoinstall", "sitechecks")):
                if (config.get("autoinstall", "sitechecks").lower() == "n"):
                    sitechecks = False
            if (config.has_option("autoinstall", "mode")):
                mode = config.get("autoinstall", "mode").lower()
            if (config.has_option("autoinstall", "adminEmail")):
                adminEmail = config.get("autoinstall", "adminEmail")
            if (config.has_option("autoinstall", "gridName")):
                gridName = config.get("autoinstall", "gridName")
            if (config.has_option("autoinstall", "facility")):
                facility = config.get("autoinstall", "facility")
            if (config.has_option("autoinstall", "partialReq")):
                partialReq = config.getboolean("autoinstall", "partialReq")
            if (config.has_option("wms", "ns")):
                wmsns = config.get("wms", "ns")
            if (config.has_option("wms", "lb")):
                wmslb = config.get("wms", "lb")
            if (config.has_option("wms", "ld")):
                wmsld = config.get("wms", "ld")
            if (config.has_option("wms", "myproxy")):
                wmsmyproxy = config.get("wms", "myproxy")
            if (config.has_option("wms", "wmproxy")):
                wmswmproxy = config.get("wms", "wmproxy")
    except:
        pass

    # Set up the logfile
    if (os.environ.has_key('LJSFVARPATH')):
        logfile = "%s/%s" % (os.environ['LJSFVARPATH'],logfile)
    if (not os.access(os.path.dirname(logfile),os.F_OK)):
        try:
            os.makedirs(os.path.dirname(logfile))
        except:
            msgOut("Cannot create %s" % os.path.dirname(logfile))

    # Run as a daemon
    res = createDaemon(logfile)
    # Write the pid into a file or stdout
    pidfn = "autoinstall-%s.pid" % socket.gethostname()
    if (os.environ.has_key('LJSFVARPATH')):
        pidfn = "%s/%s" % (os.environ['LJSFVARPATH'],pidfn)
    try:
        pidfile = open(pidfn, "w")
        pidfile.write(("%d" % os.getpid()))
        pidfile.close()
    except:
        msgOut("Cannot write the pid file %s" % pidfn)
        sys.exit(-1)

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Set the agent protocol
    agent.protocol = protocol

    # Set the agent partial request handling mode
    agent.partialReq = partialReq

    # Instantiate the web services and start the (infinite) accept loop
    if (wsport): agent.startWebService(wsport)
    if (uiport): agent.startWebUI(uiport)
    agent.start(maxproxy,timeleft,interval,compress,dirs,sitechecks,wmsns,wmslb,wmsld,wmswmproxy,wmsmyproxy,mode,adminEmail,gridName,facility)

    # Remove the pidfile
    try: os.remove(pidfn)
    except: pass
