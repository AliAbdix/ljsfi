import re, string, os, sys, commands, subprocess, shutil, socket

auth_init_cmd      = { 'grid':    'voms-proxy-init',
                       'voms':    'voms-proxy-init',
                       'myproxy': 'myproxy-init' }
auth_init_file_cmd = { 'grid':    'voms-proxy-init -out %s',
                       'voms':    'voms-proxy-init -out %s',
                       'myproxy': 'myproxy-init -out %s' }
auth_info_cmd      = { 'grid':    'grid-proxy-info',
                       'voms':    'voms-proxy-info',
                       'myproxy': 'voms-proxy-info' }
#auth_info_file_cmd = { 'grid':    'voms-proxy-info --file %s --dont-verify-ac',
auth_info_file_cmd = { 'grid':    'voms-proxy-info --file %s',
                       'voms':    'voms-proxy-info --file %s',
                       'myproxy': 'voms-proxy-info --file %s' }
auth_renew_cmd     = { 'myproxy': 'myproxy-get-delegation' }
auth_destroy_cmd   = { 'grid':    'grid-proxy-destroy',
                       'voms':    'voms-proxy-destroy',
                       'myproxy': 'myproxy-destroy' }
auth_ext_cmd       = { 'voms':    'voms-proxy-init -noregen -cert %s -voms %s -valid %d:%d' }
wmsdelegate        =   'glite-wms-job-delegate-proxy -d %s -e %s'

class ljsfUtils:

  gridproxy = "proxy";
  if (os.environ.has_key("LJSF_SECURITY")): gridproxy = "%s/%s" % (os.environ["LJSF_SECURITY"],gridproxy)

  def checkProxy(self,timeleft=0,maxtime=86400,myproxyhours=100,gridproxyhours=200):
    # Check if the proxy is valid
    dn=""
    tl=""
    # Get the athentication mode from the environment or use a default one if nothing is supplied
    auth_type=['grid',None]
    if (os.environ.has_key('LJSFAUTHTYPE')):
        ljsfauth=os.environ['LJSFAUTHTYPE'].lower().split(':')
        auth_type[0]=ljsfauth[0]
        if (len(ljsfauth) > 1): auth_type[1]=ljsfauth[1]
    #proxy=os.popen("which %s 2>&1" % auth_init_cmd[auth_type[0]])
    #rc = proxy.close()
    #if (rc != None):
    #  print "Your grid setup is incomplete."
    #  sys.exit(-1)
    (s,o) = commands.getstatusoutput("which %s 2>&1" % auth_init_cmd[auth_type[0]])
    if (s != 0):
      print "Your grid setup is incomplete."
      sys.exit(1)
    valid_proxy=False
    while not valid_proxy:
      try:
        ttyname=os.ttyname(0)
        is_interactive=True
      except:
        is_interactive=False
      tl=self.getProxyLifetime()
      hours = int(maxtime/3600.)
      minutes = int((maxtime-hours*3600)/60.)
      if (tl > timeleft):
        #proxyinfo=os.popen("%s -identity 2>&1" % auth_info_cmd[auth_type[1]])
        #dn=proxyinfo.readline().strip().replace('/CN=proxy','')
        #rc=proxyinfo.close()
        #if (rc == None): valid_proxy=True
        (s,proxyinfo) = commands.getstatusoutput("%s -identity 2>&1" % auth_info_cmd[auth_type[1]])
        if (s==0):
          dn=proxyinfo.split('\n')[0].strip().replace('/CN=proxy','')
          valid_proxy=True
      elif ((auth_type[0]=='myproxy' and tl>0) or (auth_type[0]=='grid' and auth_type[1]=='voms')):
        rc=self.renewProxy(auth_type,maxtime,timeleft)
        if (rc!= 0 and is_interactive):
          rc = self.openProxy(auth_type,timeleft,maxtime,myproxyhours,gridproxyhours)
          if (rc != 0):
            print "Cannot open proxy"
            break
      elif (is_interactive):
        print "You grid credentials are missing or outdated"
        rc = self.openProxy(auth_type,timeleft,maxtime,myproxyhours,gridproxyhours)
        if (rc != 0):
          print "Cannot open proxy"
          break
    return dn

  def getProxyLifetime(self,auth_type=None,proxyfile=None):
    if (not auth_type):
        auth_type=['grid','grid']
        if (os.environ.has_key('LJSFAUTHTYPE')):
            ljsfauth=os.environ['LJSFAUTHTYPE'].lower().split(':')
            auth_type[0]=ljsfauth[0]
            if (len(ljsfauth) > 1): auth_type[1]=ljsfauth[1]
    if (proxyfile):
        #proxy=os.popen("%s -timeleft 2>&1" % (auth_info_file_cmd[auth_type[0]] % proxyfile))
        (s,proxy) = commands.getstatusoutput("%s -timeleft 2>&1" % (auth_info_file_cmd[auth_type[0]] % proxyfile))
    else:
        #proxy=os.popen("%s -timeleft 2>&1" % auth_info_cmd[auth_type[0]])
        (s,proxy) = commands.getstatusoutput("%s -timeleft 2>&1" % auth_info_cmd[auth_type[0]])
    #tl = proxy.readline()
    #rc = proxy.close()
    #if (rc != None):
    #  return -1
    if (s != 0):
      return -1
    else:
      tl = proxy.split('\n')[0]
      return int(tl)

  def getProxyTimestamp(self,auth_type=None,proxyfile=None):
    if (not auth_type):
        auth_type=['grid','grid']
        if (os.environ.has_key('LJSFAUTHTYPE')):
            ljsfauth=os.environ['LJSFAUTHTYPE'].lower().split(':')
            auth_type[0]=ljsfauth[0]
            if (len(ljsfauth) > 1): auth_type[1]=ljsfauth[1]
    if (proxyfile):
        #proxy=os.popen("%s -path 2>&1" % (auth_info_file_cmd[auth_type[0]] % proxyfile))
        (s,proxy) = commands.getstatusoutput("%s -path 2>&1" % (auth_info_file_cmd[auth_type[0]] % proxyfile))
    else:
        #proxy=os.popen("%s -path 2>&1" % auth_info_cmd[auth_type[0]])
        (s,proxy) = commands.getstatusoutput("%s -path 2>&1" % auth_info_cmd[auth_type[0]])
    #proxyfile = proxy.readline().split("\n")[0]
    #rc = proxy.close()
    #if (rc != None):
    #    proxyts = 0
    proxyfile = proxy.split('\n')[0]
    if (s != 0):
        proxyts = 0
    else:
        if (os.path.exists(proxyfile)):
            proxyts = os.stat(proxyfile).st_mtime
        else:
            proxyts = 0
    return proxyts

  def proxyInfo(self,auth_type=None,proxyfile=None,options=None):
    if (not auth_type):
        auth_type=['grid',None]
        if (os.environ.has_key('LJSFAUTHTYPE')):
            ljsfauth=os.environ['LJSFAUTHTYPE'].lower().split(':')
            auth_type[0]=ljsfauth[0]
            if (len(ljsfauth) > 1): auth_type[1]=ljsfauth[1]
    if (auth_type[0] == 'grid' and auth_type[1] == 'voms'):
        (s,pxinfo) = commands.getstatusoutput("%s" % (auth_info_file_cmd[auth_type[0]] % self.gridproxy))
        print "LJSFi long %s proxy info:" % auth_type[0]
        print "-------------------------"
        print pxinfo
        print
        if (s != 0): return s
    
    if (auth_type[1]):
        auth = auth_type[1]
    else:
        auth = auth_type[0]
    if (proxyfile):
        (s,pxinfo) = commands.getstatusoutput("%s %s" % (auth_info_file_cmd[auth] % proxyfile, string.join(options,' ')))
    else:
        (s,pxinfo) = commands.getstatusoutput("%s %s" % (auth_info_cmd[auth], string.join(options,' ')))
    print "LJSFi %s proxy info:" % auth
    print "-------------------------"
    print pxinfo
    return s

  def openProxy(self,auth_type=None,timeleft=0,maxtime=86000,myproxyhours=100,gridproxyhours=200):
    # Get the athentication mode from the environment or use a default one if nothing is supplied
    if (not auth_type):
        auth_type=['grid','grid']
        if (os.environ.has_key('LJSFAUTHTYPE')):
            ljsfauth=os.environ['LJSFAUTHTYPE'].lower().split(':')
            auth_type[0]=ljsfauth[0]
            if (len(ljsfauth) > 1): auth_type[1]=ljsfauth[1]
    hours = int(maxtime/3600.)
    minutes = int((maxtime-hours*3600)/60.)
    # Open the proxy
    print "Opening a new %s proxy" % auth_type[0]
    if (auth_type[0]=='voms'):
        cmd = ["%s" % auth_init_cmd[auth_type[0]], "-voms", os.environ['VOMS'], "-valid",  "%d:%d" % (hours,minutes)]
        print string.join(cmd)
        rc = subprocess.call(cmd)
    elif (auth_type[0]=='grid' and auth_type[1]=='voms'):
        #cmd    = "%s -valid %d:0 -out %s" % (auth_init_cmd['grid'],gridproxyhours,self.gridproxy)
        cmd    = [ "%s" % auth_init_cmd['grid'], "-valid", "%d:0" % gridproxyhours, "-out", "%s" % self.gridproxy ]
        cmdext = auth_ext_cmd['voms'] % (self.gridproxy,os.environ['VOMS'],hours,minutes)
        print string.join(cmd)
        rc = subprocess.call(cmd)
        if (rc == 0 or rc == 1):
            #(rc,o) = commands.getstatusoutput("%s -path 2>/dev/null" % auth_info_cmd['voms'])
            #print o
            #shutil.copy(o,self.gridproxy)
            print cmdext
            (rc,o) = commands.getstatusoutput(cmdext)
            print o
            if (rc != 0):
                print "Cannot extend the grid proxy with the VOMS extensions"
                print "Error: %s" % o
            else: 
                self.delegateProxyToWMS()
        else:
            print "Cannot open the grid proxy"
    elif (auth_type[0]=='myproxy'):
        if (auth_type[1]=='grid'):
            (rc,o) = commands.getstatusoutput("%s -valid %d:%d" % (auth_init_cmd['grid'],hours,minutes))
        else:
            (rc,o) = commands.getstatusoutput("%s -voms %s -valid %d:%d" % (auth_init_cmd['voms'], os.environ['VOMS'],hours,minutes))
        print o
        (rc,o) = commands.getstatusoutput("%s -s %s -d -n -t %d -c %d" % (auth_init_cmd[auth_type[0]], os.environ['LJSF_MYPROXYSERVER'],hours,myproxyhours))
        print o
    else:
        (rc,o) = commands.getstatusoutput("%s -valid %d:%d" % (auth_init_cmd[auth_type[0]],hours,minutes))
        print o
    return rc

  def renewProxy(self,auth_type=['myproxy','grid'],maxtime=172800,timeleft=0):
    pxpath = None
    hours = int(maxtime/3600.)
    minutes = int((maxtime-hours*3600)/60.)
    rc = 0
    if (auth_type[0] == "myproxy"):
        print "Renewing proxy from %s" % os.environ['LJSF_MYPROXYSERVER']
        if (auth_type[1]=='grid'):
            #proxypath=os.popen("%s -path 2>/dev/null" % auth_info_cmd['grid'])
            (s,proxypath) = commands.getstatusoutput("%s -path 2>/dev/null" % auth_info_cmd['grid'])
        elif (auth_type[1]=='voms'):
            (rc,proxypath) = commands.getstatusoutput("%s -path 2>/dev/null" % auth_info_cmd['voms'])
        pxpath=proxypath.split("\n")[0].strip()
        if (rc == None):
          (rc,proxyrenew)=commands.getstatusoutput("%s -s %s -d -a %s -t %d" % (auth_renew_cmd[auth_type[0]], os.environ['LJSF_MYPROXYSERVER'],pxpath,hours))
    elif (auth_type[0] == "grid" and (auth_type[1] == "voms")):
        pxpath = self.gridproxy
    if (self.getProxyLifetime(proxyfile=pxpath) <= timeleft):
      if (auth_type != ['grid','voms']):
        print "Cannot renew proxy. Destroying the outdated"
        print "Proxy lifetime is %d and timeleft is %d" % (self.getProxyLifetime(proxyfile=pxpath), timeleft)
        os.system("%s" % (auth_destroy_cmd[auth_type[1]]))
      else:
        print "Cannot renew proxy."
        rc=1
    else:
      if (auth_type[1]=='voms'):
        print "Extending proxy with VOMS informations"
        (rc,proxyext) = commands.getstatusoutput(auth_ext_cmd['voms'] % (pxpath,os.environ['VOMS'],hours,minutes))
        if (rc == 0): self.delegateProxyToWMS()
    print
    return rc

  def delegateProxyToWMS(self):
    rc = 0
    if (os.environ.has_key('LJSF_CMDSET') and os.environ["LJSF_CMDSET"].lower() in ["edg", "glite", "lcg"]):
        delegation_host = socket.gethostname().split('.')[0]
        wmslistpath = "%s_active_wms.list" % delegation_host
        if (os.environ.has_key("CONFPATH")): wmslistpath = "%s/%s" % (os.environ["CONFPATH"],wmslistpath)
        os.system("ljsfinfo.py --show-active-wmproxy > %s" % wmslistpath)
        wmshostfile = open(wmslistpath)
        p = re.compile("https://([^:]*):.*")
        for wmproxy in wmshostfile:
            wmproxy = wmproxy.split("\n")[0]
            wmshostm = p.match(wmproxy)
            if (wmshostm):
                wmshost = wmshostm.groups(0)[0]
                delegation_name = "%s_%s_proxy" % (os.getlogin(),delegation_host)
                wmslist = socket.gethostbyname_ex(wmshost)[2]
                for wmshaddr in wmslist:
                    wmshname = socket.getfqdn(wmshaddr)
                    wmproxyurl = re.sub(r"https://([^:]*):(.*)",r"https://%s:\2" % wmshname,wmproxy)
                    delegation_timestamp = "%s.%s.ld" % (delegation_host,wmshname)
                    if (os.environ.has_key("LJSF_SECURITY")): delegation_timestamp = "%s/%s" % (os.environ["LJSF_SECURITY"],delegation_timestamp)
                    if (os.path.exists(delegation_timestamp)):
                        dtsf = open(delegation_timestamp)
                        dts  = dtsf.readline().split("\n")[0]
                        if (dts): dts = int(dts)
                        else:     dts = 0
                        dtsf.close()
                    else:
                        dts = 0
                    pts = self.getProxyTimestamp()
                    if (dts < pts):
                        print "Delegating proxy to %s with delegation ID %s" % (wmshname,delegation_name)
                        (rctmp,proxydelegate) = commands.getstatusoutput(wmsdelegate % (delegation_name,wmproxyurl))
                        if (rctmp == 0):
                            dtsf = open(delegation_timestamp,"w")
                            dtsf.write("%d" % pts)
                            dtsf.close()
                        else:
                            print "Proxy delegation to %s FAILED" % wmproxyurl
                            print wmsdelegate % (delegation_name,wmproxyurl)
                            print proxydelegate
                            rc = rc + rctmp
                    else:
                        print "Proxy already delegated to %s" % wmshname
        wmshostfile.close()
    return rc

  def destroyProxy(self,auth_type=None):
    rc = 0
    # Get the athentication mode from the environment or use a default one if nothing is supplied
    if (not auth_type):
        auth_type=['grid',None]
        if (os.environ.has_key('LJSFAUTHTYPE')):
            ljsfauth=os.environ['LJSFAUTHTYPE'].lower().split(':')
            auth_type[0]=ljsfauth[0]
            if (len(ljsfauth) > 1): auth_type[1]=ljsfauth[1]
    # Destroy the proxy
    if (auth_type[1]):
        auth = auth_type[1]
    else:
        auth = auth_type[0]
    if (auth_type != ['grid','voms']):
        print "Destroying the %s proxy" % auth
        (rc,o) = commands.getstatusoutput(auth_destroy_cmd[auth])
        if (rc !=0): print o
    if (auth_type[0]=='grid' and auth_type[1]=='voms'):
        if (os.path.exists(self.gridproxy)):
            print "Destroying the long %s proxy" % auth_type[0]
            os.remove(self.gridproxy)
    return rc
