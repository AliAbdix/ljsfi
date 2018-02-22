#!/usr/bin/env python

from SOAPpy import *
import sys, os
import ConfigParser
import signal
import getopt
import thread
import socket
import commands
from ljsfutils import *


#####################################################################
# AutoGet agent                                                     #
# LJSFi Framework 1.0.1                                             #
# Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it> - 20051116 #
#####################################################################

__version__ = "$Revision: 1 $"[11:-1]

HELP="""AutoGet agent %s.
Usage: autoget.py [OPTION]

Options:
  --help                      display this help and exit.
  --debug | -d                debug mode

Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>.
"""

class AutoGet:

    short_options = "dh"
    long_options = ["debug", "help"]

    wsport     = None
    debug      = False
    shutdown   = False

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

    # Start auto getting
    def start (self, maxproxy, timeleft, interval, compress, dirs):
        auth_type  = 'grid'
        if (os.environ.has_key('LJSFAUTHTYPE')):
            auth_type=os.environ['LJSFAUTHTYPE'].lower()
        utils=ljsfUtils()
        if (self.debug): print 'Interval time = %d s' % interval
        getCommand = "get-output -n -u"
        if (compress): getCommand += " -z"
        while not self.shutdown:
            proxyTimeLeft = utils.getProxyLifetime()
            if (self.debug):
                print 'Proxy time left: %d (%d)' % (proxyTimeLeft,timeleft)
            if (proxyTimeLeft > timeleft):
                if (self.debug): print 'Scanning directories:'
                for dir in dirs.split(":"):
                    jobs = "%s/*" % dir
                    if (self.debug): print 'Scanning %s...' % dir
                    cmd = "%s %s" % (getCommand,jobs)
                    if (self.debug): print 'Executing %s' % cmd
                    print commands.getoutput(cmd)
            elif (proxyTimeLeft > 0 and auth_type == 'myproxy'):
                utils.renewProxy(auth_type,maxproxy,timeleft)
            proxyTimeLeft = utils.getProxyLifetime()
            if (proxyTimeLeft > interval):
                time.sleep(interval)
            else:
                print 'Proxy time left is %d s.' % proxyTimeLeft
                print 'Exiting autoget agent...'
                self.shutdown = True
        if (self.debug): print 'Exiting autoget agent...'

    # Set debug mode
    def setDebug (self, mode):
        self.debug = mode

    def startWebService (self, port):
        # Start the control web service
        self.wsport = port
        tid = thread.start_new_thread(self.webService,())

    def webService (self):
        ws = SOAPServer(("", self.wsport))
        if (self.debug):
            print "AutoGet WebService started at %s:%d" % (socket.gethostname(),self.wsport)
        # Register the functions
        ws.registerFunction(self.close)
        # Loop over the requests
        ws.serve_forever()

    def close (self):
        self.shutdown = True
        return 0

###################################################

agent = AutoGet()

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
    wsport   = None
    interval = 300
    maxproxy = 86400
    timeleft = 300
    dirs     = "$JOBSPATH"
    compress = False
    conffile = "autoget.conf"
    logfile  = "log/%s/autoget-%s.log" % (time.strftime("%Y%m%d-%H%M"),socket.gethostname())

    # Parse the configuration file
    config = ConfigParser.ConfigParser()
    if (os.environ.has_key('CONFPATH')):
        conffile = "%s/%s" % (os.environ['CONFPATH'],conffile)
    try:
        config.read(conffile)
        if (config.has_section("autoget")):
            if (config.has_option("autoget", "wsport")):
                wsport = int(config.get("autoget", "wsport"))
            if (config.has_option("autoget", "interval")):
                interval = int(config.get("autoget", "interval"))
            if (config.has_option("autoget", "compress")):
                if (config.get("autoget", "compress").lower() == "y"):
                    compress = True
            if (config.has_option("autoget", "dirs")):
                dirs = config.get("autoget", "dirs")
            if (config.has_option("autoget", "minproxy")):
                timeleft = int(config.get("autoget", "minproxy"))
            if (config.has_option("autoget", "maxproxy")):
                maxproxy = int(config.get("autoget", "maxproxy"))
    except:
        pass

    # Set up the logfile
    if (os.environ.has_key('LJSFVARPATH')):
        logfile = "%s/%s" % (os.environ['LJSFVARPATH'],logfile)
    if (not os.access(os.path.dirname(logfile),os.F_OK)):
        try:
            os.makedirs(os.path.dirname(logfile))
        except:
            print "Cannot create %s" % os.path.dirname(logfile)

    # Run as a daemon
    res = createDaemon(logfile)
    # Write the pid into a file or stdout
    pidfn = "autoget-%s.pid" % socket.gethostname()
    if (os.environ.has_key('LJSFVARPATH')):
        pidfn = "%s/%s" % (os.environ['LJSFVARPATH'],pidfn)
    try:
        pidfile = open(pidfn, "w")
        pidfile.write(("%d" % os.getpid()))
        pidfile.close()
    except:
        print "Cannot write the pid file %s" % pidfn
        sys.exit(-1)

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


    # Instantiate the server and start the (infinite) accept loop
    if (wsport): agent.startWebService(wsport)
    agent.start(maxproxy,timeleft,interval,compress,dirs)

    # Remove the pidfile
    try: os.remove(pidfn)
    except: pass
