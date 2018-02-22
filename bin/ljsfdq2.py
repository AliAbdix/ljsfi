#!/usr/bin/env python
import sys, re
import getopt

__version__ = "$Revision: 1 $"[11:-1]

HELP="""LJSF DQ2 interface %s.
Usage: ljsfdq2.py <site name> [OPTION]...
                                                                                
Options:
  --help                      display this help and exit.
  --debug                     enable the debug mode
Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>.
"""

def help():
    print HELP % (__version__.strip(),)

try:
    from dq2.info import TiersOfATLAS
except:
    print "Please setup the DQ2 tools first."
    sys.exit(-1)

short_options = "dhs:"
long_options = ["debug", "help", "site="]
debug = False
input = {}

try:
    opts, args = getopt.getopt(sys.argv[1:],
                 short_options,
                 long_options,
                 )
except getopt.GetoptError:
    # Print the help
    help()
    sys.exit(-1)
for cmd, arg in opts:
    if (cmd in ('--help',) or cmd in ('-h',)):
        help()
        sys.exit()
    elif (cmd in ('--debug',) or cmd in ('-d',)):
        debug = True
        msgOut("Debug mode on")
if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        input = { arg : None }
        

if (input):
    output = TiersOfATLAS.resolveGOC(input)
    p = (
         re.compile('.*SCRATCHDISK')
       , re.compile('.*USERDISK')
       , re.compile('.*DATADISK')
       , re.compile('.*MCDISK')
       , re.compile('.*')
        )
    dq2sitename = [ None, None, None, None ]
    for site in output.keys():
        for name in output[site]:
            r = None
            for rank in range(0,3):
                if (p[rank].match(name)):
                    r = rank
                    break
            if (r is None): r = 3
            dq2sitename[r]=name
    for sn in dq2sitename:
        if (sn):
            print sn
            break
else:
    help()
