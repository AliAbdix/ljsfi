#
#	Copyright Saul Youssef, 2005
#
from Base            import *
from Environment     import *
from FileGetter      import *
from Execution       import *
from UniversalAccess import *
import urlparse
import time,os
import Untarzip
import Platform

# BEGIN Code added by Scot Kronenfeld 2/2009
# This is to make @@PLATFORM@@ macros work

# Globals that will get populated the first time an @@PLATFORM@@ macro is encountered
archMap = {}
osMap = {}
loaded_mapping = 0

# Load the platform mappings from the file
def load_platform_mappings():
        lines = None
        if os.path.exists('pacman-platform-mapping'):
                try:
                        f = open('pacman-platform-mapping','r')
                        lines = f.readlines()
                        f.close()
                except:
                        return
        else:
                return
        
        for line in lines:
                if line.find("#") == 0: continue    # skip comments
                arr = line.rstrip().split(" ");
                if len(arr) != 3: continue  # We only want well-formed lines
                
                if arr[0] == "arch":
                        archMap[arr[1]] = arr[2]
                elif arr[0] == "os":
                        osMap[arr[1]] = arr[2]

        return


def resolve_url_macro(url):
        global archMap
        global osMap
        global loaded_mapping

        # Resolve the macro, if it exists
        if url.find("@@PLATFORM@@") >= 0:
                # Load the arch and OS mappings
                if loaded_mapping == 0 and len(archMap) == 0:
                        load_platform_mappings()
                        loaded_mapping = 1
                        
                platform_string = None

                if len(archMap) == 0:
                        print "ERROR: No platform mapping exists"
                        return url

                # Get mapped architecture
                mapped_arch = None
                arch = Platform.thisArch()
                if archMap.has_key(arch):
                        mapped_arch = archMap[arch]
                else:
                        mapped_arch = arch  # best guess?
                        print "ERROR: No mapping for this architecture - " + arch

                # Get mapped OS
                for opsys in Platform.equivalentOSes():
                        if osMap.has_key(opsys):
                                platform_string = mapped_arch + "_" + osMap[opsys]
                                break

                # Make the substitution
                if platform_string == None:
                        print "ERROR: No mapping for this OS"
                        return url
                else:
                        return url.replace("@@PLATFORM@@", platform_string)

        return url
# END Code added by Scot Kronenfeld 2/2009

class Download(Environment):
	type   = 'download'
	title  = 'Downloads'
	action = 'download'
	
	def __init__(self,url,deletable=0):
		self._url = url
		self._download = '- unset -'
		self._deletable = deletable
#-- Set
	def equal(self,dd): return self._url == dd._url
		
	def str(self):
		if self._download == '- unset -':
			s = os.path.basename(self._url)+' from '+self._url
		else:
			s = os.path.basename(self._url)+' from '+self._url+' => '+self._download 
		if self._deletable: s = s + ' (deletable)'
		return s
	def downfile(self): return os.path.basename(self._url)
	def getDeletable(self):
		if hasattr(self,'_deletable'): return self._deletable
		else:                          return 1

#-- Compatible	
	def compatible(self,d): return Reason()
	
#-- Satisfiable 
	def satisfied(self): return Reason('['+self._url+'] has not yet been downloaded.',not self.acquired)

	def satisfiable(self):
		r = Reason()
		if not self._url==os.path.expanduser(self._url):
			r = Reason("Download ["+self._url+"] refers to a user home directory.")
		elif '$' in self._url and not allow('non-snapshottable-downloads'):
			r = Reason("Download ["+self._url+"] contains an environment variable and can't be resolved for snapshots or mirrors (see -allow to override).")
		return r

	def headtails(self):
		head,tail = os.path.split(os.path.expanduser(self._url))
		hts = []
		if   0 and os.environ.has_key('PAC_CACHE_LOCATION'):
			prefix = os.environ['PAC_CACHE_LOCATION']
			if isURL(head): hts.append((                     head,tail,))
			else:           hts.append((os.path.join(prefix,head),tail,))
		else:
			hts.append((head,tail,))
		return hts
		
	def acquire(self):
		reason = self.satisfiable()
                self._url = resolve_url_macro(self._url) # added by Scot Kronenfeld 2/2009
		if reason.ok():
			for head,tail in self.headtails():
				try:
					cwd = os.getcwd()
					accessor = UniversalAccess(head)
					if isURL(head): 
						reason = ask.re('download','OK to download ['+tail+'] from ['+head+']?')
						verbo.log('download','Downloading ['+tail+'] from ['+head+']...')
						if verbo('download-brief'): flicker('  Downloading '+tail+'...')
					else:         
						reason = ask.re('download','OK to download ['+tail+'] from ['+head+']?')
						verbo.log('download','Downloading ['+tail+'] from ['+head+']...')
						if verbo('download-brief'): flicker('  Downloading '+tail+'...')
					if reason.ok():
						reason = accessor.getFile(tail)
				except OSError:
					reason = Reason("Current directory does not exist.  Can't download.")
				if reason.ok(): 
					self._remove = fullpath(tail)
#					self._download = fullpath(tail)
#					self._download = os.path.abspath(os.path.expanduser(tail))
					break
		return reason
		
	def retract(self):
		if hasattr(self,'_remove'): reason = execute('rm -f '+self._remove  )
		else:                       reason = execute('rm -f '+self._download)
		return reason

class DownloadTime(Environment):
	type   = 'timed download'
	title  = 'Timed Download'
	action = 'time download'
	
	def __init__(self,url,maxtime):
		self._download = Download(url)
		self._maxtime = maxtime  # float
		self._time = 0.0
		self._url = url
		
	def equal(self,x): return self._download==x._download and self._maxtime==x._maxtime
	def str(self): 
		if self._time==0.0: return ' of '+self._download._url+' in at most '+('%g'%self._maxtime)+' seconds'
		else: return ' of '+self._download._url+' in '+('%g'%self._time)+' seconds, must be <= '+('%g'%self._maxtime)+' seconds'
	
	def satisfiable(self): return Reason()
	def satisfied(self):
		return Reason(`self`+' has not yet been attempted.',not self.acquired)
	def acquire(self):
		t1 = time.time()
		reason = self._download.satisfy()
		t2 = time.time()
		removeFile(self._download.downfile())
		self._time = t2 - t1
		if reason.ok():
			if t2-t1<=self._maxtime: pass
			else:
				reason = Reason(self._download.downfile()+' downloads in '+('%g'%self._time)+' but its not <= '+('%g'%self._maxtime)+' seconds.')
		return reason
	def retract(self):
		self._time = 0.0
		return Reason()

class DownloadUntarzip(Environment):
	type   = 'downloadUntarzip'
	title  = 'Download and Untar/zips'
	action = 'download and untar/zip'
	
	def __init__(self,url,enviro=''):
		self._url = url
		self._enviro = enviro
		self._download = Download(self._url)
		self._untar    = Untarzip.Untarzip(os.path.basename(self._url),self._enviro)
		
	def equal(self,x): return self._url==x._url and self._enviro==x._enviro
	def str(self): 
		if self._untar._env=='':
			return self._download.str()+' and untar/zip'
		else:
			if hasattr(self._untar,'_enviro') and hasattr(self._untar._enviro,'type'):
				return self._download.str()+' untar/zip with top directory ['+self._untar._enviro.str()+']'
			else:
				return self._download.str()+' untar/zip and set ['+self._untar._env+'] to top directory.'
	def display(self,indent=0):
		print indent*' '+self.statusStr()+' '+`self`
		if displayMode('tar'):
			for x in self._untar._contents:
				print (indent+8)*' '+x
		
	def satisfiable(self): return Reason()
	def satisfied  (self): return self._untar.satisfied()

	def acquire(self):
		nRetry = 0
#		mRetry = httpGetRetries()
		mRetry = 0  # turn off these retries as they just confuse users and don't work often enough.  S.Y. Feb. 2006
		while 1:
			reason = self._download.satisfy()
                        self._untar.setTarball(resolve_url_macro(self._untar.getTarball())) # Added by Scot Kronenfeld 2/2009
			if reason.ok(): 
				reason = self._untar.satisfy()
				removeFile(os.path.basename(self._url))
			if not reason.ok() and not contains(`reason`,'non-standard character') and nRetry<mRetry:
				r = ask.re('retry','OK to retry ['+`self`+']?')
				if r.ok():
					nRetry = nRetry + 1
					verbo.log('retry',`self`+' has failed with the following error:')
					verbo.log('retry',`reason`)
					verbo.log('retry','Retrying '+`nRetry`+'/'+`mRetry`+'...')
					verbo.log('retry','Pausing ['+`httpGetPause()`+'] seconds first (see -retry help to adjust this)...')
					time.sleep(httpGetPause())
				else:
					reason = copy.deepcopy(r)
					break
			else:
				if nRetry>0: verbo.log('retry','Retry of ['+`self`+'] has succeeded...')
				break
			self._untar._tarpause = nRetry*5
		self._untar._tarpause = 0
		return reason
		
	def retract(self): 
		self._download.retract().require()
		self._download = Download(self._url)
		r = self._untar.retract()
		self._untar = Untarzip.Untarzip(os.path.basename(self._url),self._enviro)
		return r
		
	def verify(self): return self._untar.verify()
