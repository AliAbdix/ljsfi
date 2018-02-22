#
#	Copyright, Saul Youssef, August 2003
#
from Access     import *
from Execution  import *
from FileGetter import *
import urlAccess2

url_directory_cache = {}

def has_wget():
	import commands
	status,output = commands.getstatusoutput('wget --help')
	return status==0

if      allow('urllib2')     : _use_wget = False
elif               has_wget(): _use_wget = True
#elif  fileInPath('wget').ok(): _use_wget = True
else:
	if not os.path.exists(os.path.join(pac_anchor,pacmanDir,'wgetmess')):
		print "wget is not in your path. Using python modules as a backup..."
		try:
			f = open(os.path.join(pac_anchor,pacmanDir,'wgetmess'),'w')
			f.write('done')
			f.close()
		except:
			pass
	_use_wget = False
#
#_use_wget = commands.getstatusoutput('which wget')[0]==0
#if not _use_wget and not allow('urllib2'): print "Can't find wget.  Using python urllilb2 as a backup..."
#		
class URLAccess(Access):
	type = 'url'
	
	def __init__(self,url): 
		self.url = url
		self.location = url
#-- Set
	def __repr__(self): return self.url
	def equal(self,x): return self.url==x.url
	
	def names(self): return self.namesPath()
			
	def namesPath(self,path=''):
		reason = Reason()
		url2 = os.path.join(self.url,path)
		if url_directory_cache.has_key(url2):
			files = url_directory_cache[url2]
		else:
			reason,files = urlAccess2.urlFiles(url2)
			if reason.ok(): 
				url_directory_cache[url2] = files[:]
		return reason,files
			
	def access(self):
		r,files = self.namesPath()
		return r.ok()
	def getFile(self,name2,target=''):
		reason = Reason()
		
		self.url,name = os.path.split(os.path.join(self.url,name2))
		if target=='': target2 = name
		else:          target2 = target
	
		g = InternetFileGetter(self.url,name)
		
		tmpdir = os.path.join(pac_anchor,pacmanDir,'tmp')
		removeFile(os.path.join(tmpdir,name))

#		if (switch('wget') or allow('wget')) and not allow('urllib2'):
		if not allow('urllib2') and _use_wget:
			tries   = httpGetRetries    ()
			pause   = httpGetPause      ()
			timeout = downloadTimeoutGet()
			ver   = verbo('http')
			logfile = os.path.join(pac_anchor,pacmanDir,'logs','wget.log')
			if allow('no-http-cache'): no_cache = '--no-cache'
			else                     : no_cache = ''
			
			verbo.log('http','About to execute [wget '+no_cache+' --tries='+`tries`+' --waitretry='+`pause`+' --timeout='+`timeout`+' '+os.path.join(self.url,name)+']...')
			if ver: status = os.system('cd '+tmpdir+'; wget '+no_cache+' --tries='+`tries`+' --waitretry='+`pause`+' --timeout='+`timeout`+' '+os.path.join(self.url,name))
			else:   status = os.system('cd '+tmpdir+'; wget '+no_cache+' --append-output='+logfile+' --tries='+`tries`+' --waitretry='+`pause`+' --timeout='+`timeout`+' '+os.path.join(self.url,name))
			
			if not status==0:
				import signal
				if os.WIFEXITED(status):
					estatus = os.WEXITSTATUS(status)
					esignal = None
					msg = 'Failure downloading ['+os.path.join(self.url,name)+'].'
				else:
					estatus = None
					esignal = os.WTERMSIG(status)
					if esignal==signal.SIGINT: msg = 'Download of ['+os.path.join(self.url,name)+'] interrupted by ^C.'
					else                     : msg = 'Download of ['+os.path.join(self.url,name)+'] killed by signal ['+str(esignal)+'].'
				reason = Reason(msg)

				try:
					f = open(logfile,'r')
					lines = f.readlines()
					f.close()
#					if len(lines)>0 and not string.strip(lines[-1])=='':
					if len(lines)>0 and 'error' in lines[-1].lower():
						reason = Reason('Error downloading '+os.path.join(self.url,name)+' ['+lines[-1][:-1]+'].')
				except:
					pass
			if False and reason.ok() and (tail(name,'.tgz') or tail(name,'.gz') or tail(name,'Z')) and not front(name,'CMT'):
#			if False and reason.ok() and (tail(name,'.tgz') or tail(name,'.gz') or tail(name,'Z')) and not front(name,'CMT'):
#				status = commands.getstatus('zcat '+os.path.join(tmpdir,name))
#				status = os.system('zcat '+os.path.join(tmpdir,name)+' > /dev/null 2> /dev/null')
				status = os.system('gzip -c '+os.path.join(tmpdir,name)+' > /dev/null 2> /dev/null')
				if not status==0: reason = Reason('Downloaded file ['+name+'] is not in gzip format.')
		else:
			reason = g.get(tmpdir)
		if reason.ok(): 
			try:
				execute('mv '+os.path.join(tmpdir,name)+' '+target2)
			except (IOError,OSError):
				reason = Reason("Failure writing ["+name+"] to ["+target2+"].")					
		return reason

class URLAccessSource(URLAccess):
	cache_cache = {}
	
	def getFile(self,name2,target=''):
		if target=='': target2 = name2
		else:          target2 = target
		
		url,name = os.path.split(os.path.join(self.url,name2))		
		if os.path.isdir(target2): target2 = os.path.join(target2,name)

		reason = Reason()
		if self.cache_cache.has_key((name,url,)):
			lines = self.cache_cache[(name,url,)]
			try: 
				f = open(target2,'w')
				for line in lines: f.write(line)
				f.close()
			except (OSError,IOError):
				reason = Reason("Can't put ["+name+"] in ["+target2+"].")
		else:
			g = InternetFileGetter(url,name)
			tmpdir = os.path.join(pac_anchor,pacmanDir,'tmp')
			removeFile(os.path.join(tmpdir,name))
			
			reason = g.get(tmpdir)
			if reason.ok(): 
				try:
					execute('mv '+os.path.join(tmpdir,name)+' '+target2)
				except (IOError,OSError):
					reason = Reason("Can't put ["+name+"] in ["+target2+"].")
					
			if reason.ok() and tail(name,'.pacman'):
				try:
					f = open(target2,'r')
					lines = f.readlines()
					f.close()
					self.cache_cache[(name,url,)] = lines
				except (IOError,OSError):
					reason = Reason("Can't read ["+target2+"].")
		return reason
	
