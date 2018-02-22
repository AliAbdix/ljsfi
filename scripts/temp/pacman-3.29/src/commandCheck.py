#
#	Copyright Saul Youssef, 2005
#
from Platform   import *
from Registry   import *
from Base       import *
import FileMode
import webbrowser,sys,Execution,time,getpass
	
def launchwebdisplayPython(start=os.path.join(pac_anchor,pacmanDir,'/htmls/index.html')):
		if not os.path.exists(start) and not isURL(start): abort("Missing ["+start+"].  Can't display web page.")
		try:
			webbrowser.open(start,new=0)
		except:
			print 'Warning: Failed to launch web browser viewing ['+start+']...'

def launchwebdisplay(file=fullpath(os.path.join('$PACMAN_LOCATION','htmls/index.html'))):
	if not os.path.exists(file) and not isURL(file): 
		if verbo('browser'): print "Missing ["+file+"].  Can't display web page."
		abort("Missing ["+file+"].  Can't display web page.")
	path = file
	
	if browser('mozilla'):
		if qInpath('mozilla'): 
			if verbo('browser'): print 'About to execute ['+'mozilla '+path+' &'+']...'
			os.system('mozilla '+path+' &')
		else:
			print 'mozilla not found.  Trying netscape...'
			if verbo('browser'): print 'About to execute ['+'netscape file:'+path+' &'+']...'
			os.system('netscape '+path+' &')
	elif browser('galeon'):
		if qInpath('galeon'): 
			if verbo('browser'): print 'About to execute ['+'galeon '+path+' &'+']...'
			os.system('galeon '+path+' &')
		else:
			print 'galeon not found.  Trying netscape...'
			if verbo('browser'): print 'About to execute ['+'netscape file:'+path+' &'+']...'
			os.system('netscape '+path+' &')
	elif browser('netscape'):
		if qInpath('netscape'): 
			if verbo('browser'): print 'About to execute ['+'netscape file:'+path+' &'+']...'
			os.system('netscape '+path+' &')
		else:
			print 'netscape not found.  Trying mozilla...'
			if verbo('browser'): print 'About to execute ['+'mozilla file:'+path+' &'+']...'
			os.system('mozilla '+path+' &')
	elif browser('lynx'):
		if qInpath('lynx'): 
			if verbo('browser'): print 'About to execute ['+'lynx '+path+']...'
			os.system('lynx '+path)
		else:
			print 'lynx not found.  Trying w3m...'
			if qInpath('w3m'): 
				if verbo('browser'): print 'About to execute ['+'w3m '+path+']...'
				os.system('w3m '+path)
			else: abort("Can't find a browser.")
	elif browser('w3m'):
		if qInpath('w3m'): 
			if verbo('browser'): print 'About to execute ['+'w3m '+path+']...'
			os.system('w3m '+path)
		else:
			print 'w3m not found.  Trying lynx...'
			if verbo('browser'): print 'About to execute ['+'lynx '+path+']...'
			os.system('lynx '+path)
	else:
		if verbo('browser'): print 'About to launch default browser...'
		launchwebdisplayPython(path)

# -arch and -pretend-arch options added by Scot Kronenfeld 2/2009
def pacmanCommands():
	message = '\
% pacman -<switch1> <arg1> <arg2>... -<switch2> <arg1> <arg2>\n\
Operations on packages:\n\
  -l       <p1> <p2>...      List installed or remote packages, -d for options.\n\
  -get     <p1> <p2>...      Fetch, install and setup the indicated packages.\n\
  -fetch   <p1> <p2>...      Fetch the indicated packages.\n\
  -install <p1> <p2>...      Install the indicated packages.\n\
  -resume  <p1> <p2>...      Resume an installation after ^C.\n\
  -remove  <p1> <p2>...      Remove the indicated packages recursively.\n\
  -update-check              Check if the indicated packages have updates.\n\
  -update  <p1> <p2>...      Update the indicated packages recursively.\n\
  -update-remove             Remove potential updates.\n\
  -setup                     Setup all packages in the installation.\n\
  -remove-all                Remove all packages and the installation entirely.\n\
  -verify                    Verify the status of the indicated packages.\n\
  -pacball <p1>              Make a self-contained pacball from package p1.\n\
Operations on caches:\n\
  -lc     <c1> <c2>...       List caches c1, c2,... Use -d for options.\n\
  -domain <c1> <c2>...       Display the entire domain of a list of caches.\n\
  -extract-sources <c1>...   Extracts source code files from a list of caches.\n\
  -extract-downloads <c1>... Extracts all the downloads from a list of caches.\n\
  -snap    <c1>              Make a local snapshot of caches c1.\n\
  -mirror  <c1>              Make a local mirror of cache c1.\n\
  -update-check <m1>         Check mirror <m1> for updates.\n\
  -update <m1>               Check and update mirror <m1>.\n\
Optional switches with saved defaults (do "-<switch> help" to see the options):\n\
  -v                         Verbose messages.\n\
  -d                         Display options for -l or -lc.\n\
  -ask                       Ask permission before certain operations.\n\
  -allow                     Allow certain normally prevented operations.\n\
  -retry                     Set http retries and pause between retries.\n\
  -setups                    Choose the kinds of setup scripts produced.\n\
  -dom                       Display options for -domain.\n\
Miscellaneous:\n\
  -help,-h                   This message.\n\
  -info                      View documentation in a browser.\n\
  -bell                      Beep when finished.\n\
  -version                   Show version, platform, and arch information.\n\
  -registry                  List registry symbolic names.\n\
  -def                       Display current command line defaults.\n\
  -single                    Single package option for remove/uninstall/update.\n\
  -clear-registry	     Remove all entries from the local registry.\n\
  -clear-preferences         Restore original command line defaults.\n\
  -oldsnap <c1>              Make an old-style snapshot of c1 (deprecated).\n\
  -clear-snapshots           Clears loaded snapshots to save disk space.\n\
  -clear-lock                Unlocks a locked installation.\n\
  -http-proxy <url>          Use <url> <username> for authenticated proxies.\n\
  -ignore-cookies	     Ignore saved answers to questions.\n\
  -last,-history             Prints history of commands and results.\n\
  -platforms                 Lists all supported platforms.\n\
  -platform <plat>           Lists information about platform <plat>.\n\
  -pretend-platform <plat>   Pretend that your computer is platform <plat>.\n\
  -arch                      Lists your current architecture.\n\
  -pretend-arch <arch>       Pretend that your architecture is <arch>.\n\
  -lock-override             Override a locked cache.\n\
  -tar-overwrites            Lists any files which have been overwritten by untarring.\n\
  -o or -out                 Specify an output file for snapshots or mirrors.\n\
  -browser                   Web browser choice.\n\
  -default                   Specify a default package for a pacball to install.\n\
  -license                   Prints the README file.'
	print message

legalswitches = ['tar-overwrites','help','h','info','version','v','V','quiet','ask','wget','remove-all','removeall','mirror','snapshot','oldsnap',
   'fetch','install','uninstall','remove','snap','verify','pretendPlatform','license','def','history','last','bell',
   'trust-all-caches','ignore-cookies','clear-registry','allow','cache','browser','extract-sources','downloadtimeout',
   'extract-downloads','single','no-compatibility','clear-snapshots','domain','dom','retry','clear-lock','tarpause',
   'clear-preferences','no-download-access-check','debug','l','setup','registry','lc','d','get','o','out','resume','pacball',
   'platforms','update-remove','update-check','update','lock-override','pretend-platform','arch','pretend-arch','http-proxy',
   'setups','platform','default']
   
mutableswitches = ['remove-all','fetch','install','uninstall','remove','verify','clear-registry','setup','get','resume','update','update-check',
                   'update-remove','http-proxy','setups']
		   
mutable = exists(mutableswitches,lambda x: switch(x))

platformCheck()

def saveCommand(r):
	if os.path.isdir(os.path.join(pac_anchor,pacmanDir)) and mutable:
		try:
			pathr = os.path.join(pac_anchor,pacmanDir,'logs','results')
			pathc = os.path.join(pac_anchor,pacmanDir,'logs','commands')
			
			if os.path.exists(pathr):
				f = open(pathr,'r')
				rs = cPickle.load(f)
				f.close()
			else:
				rs = []
				
			rs.append(r)
			f = open(pathr,'w')
			cPickle.dump(rs,f)
			f.close()

			com = ''
			for x in sys.argv: com = com + ' ' + x
			f = open(os.path.join(pac_anchor,pacmanDir,'logs','commands'),'a')
			f.write('% '+string.strip(com)+' finished at '+time.ctime(time.time())+'\n')
			f.close()
		except:
			print "Can't write to ["+pac_anchor+"] installation."

def proxyRefresh():
	url,username,password='','',''
	items = switchItems('http-proxy')
	if len(items)>=1: 
		url = items[0]
	if len(items)>=2:
		username = items[1]
		password = getpass.getpass()
	
	if url=='' and username=='' and password=='' and not switch('http-proxy'):
		url,username,password = proxyGet()
		if not (url=='' and username=='' and password==''):
			verbo.log('http','Using saved http proxy username/password from '+pacmanDir+'/http-proxy...')
		else:
			verbo.log('http','No http proxy in use...')
	else:
		if password=='' or yesno('Is it OK to save http proxy username/password as plain text in ['+pacmanDir+'/http-proxy]?'):
			verbo.log('http','Saving http proxy information in ['+pacmanDir+'/http-proxy]')
			proxyPut(url,username,password)
		else:
			print 'Http proxy password/username used but not saved...'
			
	if not url=='':
		if username=='' and password=='': set_plain_proxy(url)
		else:                             galang_set_auth_proxy(url,username,password)
	
def proxyPut(url,username,password):
	path = os.path.join(pac_anchor,pacmanDir,'http-proxy')
	try:
		removeFile(path)
		f = open(path,'w')
		f.write(url+' '+username+' '+password+'\n')
		f.close()
		fm = FileMode.FileMode(path)
		fm.setWorldRead ('off')
		fm.setWorldWrite('off')
		fm.setGroupRead ('off')
		fm.setGroupWrite('off')
		fm.setOwnerRead ('on')
		fm.setOwnerWrite('on')
	except (IOError,OSError):
		print 'Failed to save http proxy information in ['+pac_anchor+']...'
	
def proxyGet():
	path = os.path.join(pac_anchor,pacmanDir,'http-proxy')
	url,username,password = '','',''
	if os.path.exists(path):
		try:
			f = open(path,'r')
			line = f.readline()
			f.close()
			if len(line)>1: line = string.strip(line)
		
			items = string.split(line,' ')
			if len(items)>=1: url      = items[0]
			if len(items)>=2: username = items[1]
			if len(items)>=3: password = items[2]
		except (IOError,OSError):
			print 'Failed to read http proxy information from ['+pac_anchor+']...'
	return url,username,password

def galang_set_auth_proxy(auth_proxy,auth_proxy_user,auth_proxy_pass):
#
# -- Add authenticated proxy handling code courtesy of Gerson Garang.  S.Y. 2005.
#
	try:
		import urllib2
		proxy_handler = urllib2.ProxyHandler({"http" : 'http://'+auth_proxy})
		pass_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
		for passwd  in [ (None,           auth_proxy, auth_proxy_user, auth_proxy_pass),
		                 (None, 'http://'+auth_proxy, auth_proxy_user, auth_proxy_pass), ]:
			pass_mgr.add_password(*passwd)
		proxy_auth_handler = urllib2.ProxyBasicAuthHandler(pass_mgr)
		opener = urllib2.build_opener(proxy_handler, proxy_auth_handler, urllib2.HTTPHandler)
		urllib2.install_opener(opener)
	except:
		verbo.log('http','Failed to set authenticated proxy...')
		print 'Failed to set authenticated proxy...'
	
def set_plain_proxy(url):
	os.environ['http_proxy'] = url
	
def require_installation():
	if not os.path.exists(os.path.join(pac_anchor,pacmanDir)):
		print 'No installation at ['+pacmanDir+'].'
		sys.exit(1)

def commandCheck():
	if os.path.exists(os.path.join(pac_anchor,pacmanDir,'ii3.0')):
		print 'The installation at ['+pac_anchor+'] was created with Pacman 3.0.'
		print 'You are using Pacman '+version+'.'
		print 'You must remake the installation to use Pacman 3.1.'
		sys.exit(1)
	if os.path.exists('README.html') and os.path.exists('src'):
		print 'cd out of the untarred Pacman area before executing Pacman commands.'
		sys.exit(1)
	if os.path.exists('o..mirror..o') or os.path.exists('o..basemirror..o'):
		print 'Inside a mirror! cd out of this directory before executing Pacman commands.'
		sys.exit(1)
	proxyRefresh()
	if verbo('http-proxy'):
		if os.environ.has_key('http_proxy') and not len(os.environ['http_proxy'])==0:
			print 'Using http proxy ['+os.environ['http_proxy']+']...'
		else:
			print 'No http proxy is being used...'
	if switch('http-proxy'):
		require_installation()
	if switch('version') or switch('V'):
		print 'Pacman version:  '+version+version_extra
		print 'Python version: ',sys.version.split('\n')[0]
		Platform().display2()
                archDisplay()
		if switch('version'): sys.exit(0)
	if os.path.exists('README') and os.path.isdir('boot'):
		print '% cd to a new directory to start a Pacman installation.'
		sys.exit(1)
#	if os.path.isdir('ii3.1'):
#		print 'This installation was created with Pacman < 3.18.'
#		print 'Either re-install or use an older version of Pacman.'
#		sys.exit(1)
#	if not writeable('.'):
#		print '% No write permission to current directory.'
#		sys.exit(1)
	if not writeable('.') and exists(['get','fetch','install','resume','remove','update-check','update','update-remove','setup','remove-all','verify','repair'],lambda x: switch(x)):
		print 'You need write permission for the attempted operation.'
		sys.exit(1)
	if os.path.exists('Pacman.db') or os.path.isdir('E'):
		print 'This is a Pacman 2 installation.  You are running Pacman '+version+'.'
		print 'cd to a new directory to start a new installation.'
		sys.exit(1)
	for sw in switches:
		sw2 = string.split(sw,':')[0]
		if not sw2[1:] in legalswitches:
			pacmanCommands()
			print 'Unknown command line switch ['+sw2+'].'
			sys.exit(1)		
	if switch('help') or switch('h') or switch('-help') or (len(switches)==0 and len(params)>0):
		pacmanCommands()
		sys.exit(0)
	if len(switchItems('single'))>0:
		print 'Error in [-single] placement on command line.  Try again...'
		sys.exit(0)
	if switch('license'):
		os.system('cat $PACMAN_LOCATION/README.html')
		sys.exit(0)
	if switch('clear-lock'):
		require_installation()
		removeFile(os.path.join(pac_anchor,pacmanDir,'lock'))
		sys.exit(0)
	if switch('def'):
		sys.exit(0)
	if switch('platforms'):
		platformDisplay()
		sys.exit(0)
        # Added by Scot Kronenfeld 2/2009
        if switch('arch'):
                archDisplay()
                sys.exit(0)
	if len(switchItems('platform'))>0: 
		platSat(switchItems('platform')[0])
		sys.exit(0)
	if switch('last') or switch('history'):
		path = os.path.join(pac_anchor,pacmanDir)
		if os.path.exists(path):
			try:
				f = open(os.path.join(pac_anchor,pacmanDir,'logs','results'),'r')
				rs = cPickle.load(f)
				f.close()
				
				f = open(os.path.join(pac_anchor,pacmanDir,'logs','commands'),'r')
				lines = f.readlines()
				f.close()
				
				if not len(lines)==len(rs): abort('commands file corrupted.')
				
				if switch('last') and len(lines)>0 and len(lines[0])>0:
					print lines[-1][:-1]
					rs[-1].display()
				else:
					while len(lines)>0:
						line = lines.pop(0)
						r    = rs.pop(0)
						print line[:-1]
						r.display()
			except:
				raise
				print 'New installation.'
		else:
			print 'No installation at ['+pac_anchor+'].'
		sys.exit(0)
	if switch('clear-registry'):
		require_installation()
		registry.clear_registry()
	if switch('clear-preferences'):
		require_installation()
		Execution.execute('rm -f '+pacmanDir+'/preferences/*')
		sys.exit(0)
	if switch('clear-snapshots'):
		require_installation()
		if os.path.isdir(os.path.join(pacmanDir,'snapshots')):
			print 'Clearing loaded snapshots from ['+pac_anchor+']...'
			Execution.execute('chmod -R a+w '+pacmanDir+'/snapshots/*; rm -r -f '+pacmanDir+'/snapshots/*')
		sys.exit(0)
	if switch('clear-cookies'):
		require_installation()
		if os.path.isdir(os.path.join(pacmanDir,'/cookies')):
			Execution.execute('rm -r -f '+os.path.join(pac_anchor,pacmanDir,'cookies/*'))
		sys.exit(0)
	if switch('info'): launchwebdisplay()
		
	pplat,par = switchpar('pretend-platform')
	if switch('pretend-platform') and os.path.exists(os.path.join(pac_anchor,pacmanDir)):
		print "Installation ["+pac_anchor+"] already exists."
		print "-pretend-platform can only be used when creating a new installation."
		print "Use [% pacman -version] to see your computed or assumed platform."
		sys.exit(0)

        # Added by Scot Kronenfeld 2/2009
	parch,par = switchpar('pretend-arch')
	if switch('pretend-arch') and os.path.exists(os.path.join(pac_anchor,pacmanDir)):
		print "Installation ["+pac_anchor+"] already exists."
		print "-pretend-arch can only be used when creating a new installation."
		print "Use [% pacman -arch] to see your computed or assumed arch."
		sys.exit(0)

	csw,par = switchpar('cache')
	if csw:
		try:
			g = open('trusted.caches','a')
			g.write(par+'\n')
			g.close()
			print 'Cache ['+par+'] added to trusted.caches file.'
		except (IOError,OSError):
			abort('Error writing to trusted.caches file.')
		sys.exit(0)
