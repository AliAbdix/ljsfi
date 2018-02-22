#!/usr/bin/env python
import sys
import getopt
import dq2.info.TiersOfATLAS as ToA
fsquidmap=ToA.ToACache.fsquidmap

def getFrontierEnv(gocname):
  # Build the FRONTIER_SERVER env from the mapped servers and squids
  # Eg.
  # FRONTIER_SERVER="(serverurl=http://atlassq1-fzk.gridka.de:8021/fzk)
  #  (serverurl=http://squid-frontier.usatlas.bnl.gov:23128/frontieratbnl)
  #  (proxyurl=http://atlasvobox.lcg.cscs.ch:3128)
  #  (proxyurl=http://lcg-lrz-vobox.grid.lrz-muenchen.de:3128)"
  #
  fenv=''
  if fsquidmap.has_key(gocname):
    # First the frontier server(s)   
    for frontier in fsquidmap[gocname]['frontiers']:
      if (type(frontier) != type([])): flist = [frontier]
      else:                      flist = frontier
      for f in flist:
        if (f[0] != '+'):
          if (f[0] == '-'): f=f[1:]
          if f.find('http') == 0:
            fenv+='(serverurl=%s)'%f
          else:
            sys.stderr.write("Frontier url does not start with http...: %s\n" % f)

    # Then the Squid(s)
    loadbalance=False
    failover=False
    if (not fsquidmap[gocname].has_key('squids')): fsquidmap[gocname]['squids'] = ['local']
    if ('local' not in fsquidmap[gocname]['squids']):
      nsm = ['local']
      for sm in fsquidmap[gocname]['squids']: nsm.append(sm)
      fsquidmap[gocname]['squids'] = nsm
    for s in fsquidmap[gocname]['squids']:
      surls=[]  
      if s=='local':
        if fsquidmap[gocname].has_key('mysquids'):
          for surl in fsquidmap[gocname]['mysquids']:
            if (surl == 'loadbalance'):
              loadbalance=True
            else:
              if   (surl[0] == "-"): surls.append(surl[1:])
              elif (surl[0] == "+"): pass
              else: surls.append(surl)
        elif fsquidmap[gocname].has_key('mysquid'):
          surls.append(fsquidmap[gocname]['mysquid'])
        else:
          sys.stderr.write("Configured local Squid site %s has no squid\n!" % s)
        if (len(surls) > 1): failover=True
        if (len(surls) < 2 and loadbalance): loadbalance=False
      else:
        if (not loadbalance and not failover):
          if fsquidmap[s].has_key('mysquids'):
            for surl in fsquidmap[s]['mysquids']:
              if (surl == 'loadbalance'):
                loadbalance=True
              else:
                if   (surl[0] == "-"): surls.append(surl[1:])
                elif (surl[0] == "+"): pass
                else: surls.append(surl)
          elif fsquidmap[s].has_key('mysquid'):
            surls.append(fsquidmap[s]['mysquid'])
          else:
            sys.stderr.write("Configured remote Squid site %s has no squid\n!" % s)

      for surl in surls:
        if surl.find('http') == 0:
          fenv+='(proxyurl=%s)'%surl
        else:
          sys.stderr.write("Squid url does not start with http...: %s\n" % surl)
    if (loadbalance): fenv+='(loadbalance=proxies)'
  return fenv

# 

short_options = "dlp:rsh"
long_options  = ["debug", "help", "list-proto", "proto=", "regexp", "setype"]
__HELP__="""Frontier Setup helper %s.
Usage: getFrontierEnv.py [OPTION] [sitename]

Options:
  --help                        display this help and exit.
  --debug         | -d          debug mode
  --list-proto    | -l          display the supported SE protocols
  --proto=<proto> | -p <proto>  use the <proto> protocol
  --regexp        | -r          display the SURL to TURL regexp
                                for a specific protocol (needs --proto)
  --setype        | -s          display the SE type

Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>.
"""

__version__ = "$Revision: 1 $"[11:-1]

debug = False

def help():
  print __HELP__ % (__version__.strip()) 

if __name__ == "__main__":

  mode = 'frontier'
  location = None
  proto = None
  try:
      opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
  except getopt.GetoptError:
      help()
      sys.exit(-1)
  for cmd, arg in opts:
      if (cmd in ('--help',) or cmd in ('-h',)):
          help()
          sys.exit()
      elif (cmd in ('--debug',) or cmd in ('-d',)):
          debug = True
      elif (cmd in ('--setype',) or cmd in ('-s',)):
          mode = 'setype'
      elif (cmd in ('--list-proto',) or cmd in ('-l',)):
          mode = 'listproto'
      elif (cmd in ('--proto',) or cmd in ('-p',)):
          proto = arg
      elif (cmd in ('--regexp',) or cmd in ('-r',)):
          mode = 'regexp'

  if (len(sys.argv) > 1): location = sys.argv[len(sys.argv)-1]
  if (mode == 'frontier'):
      if (location):
          fe=getFrontierEnv(location.upper())  
          print fe
      else:
          for gn in fsquidmap.keys():
              fe=getFrontierEnv(gn)  
              print gn,fe
  elif (mode == 'listproto'):
      if (location):
          seinfo = ToA.getSiteProperty(location.upper(), 'seinfo')
          if (seinfo and seinfo.has_key('protocols')):
              for p in seinfo['protocols']:
                  print p[0]
  elif (mode == 'regexp'):
      if (location):
          seinfo = ToA.getSiteProperty(location.upper(), 'seinfo')
          if (seinfo and seinfo.has_key('protocols')):
              for p in seinfo['protocols']:
                  if (p[1].has_key('regexp')):
                      if (proto):
                          if (proto == p[0]):
                              print p[1]['regexp']
                              break
                      else:
                          print "%s:%s" % (p[0],p[1]['regexp'])
  else:
      seinfo = ToA.getSiteProperty(location.upper(), 'seinfo')
      if (seinfo): print seinfo['setype']
