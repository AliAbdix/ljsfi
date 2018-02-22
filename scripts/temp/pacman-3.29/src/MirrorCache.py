#
#
from Base import *
import Execution,Cache,UniversalAccess,UniversalCache,MirrorBaseCache,Trust,Package,Registry,Platform,Access
import time,socket,os,string,sys

ESC = '!'

def mirrorCreate(clist,mirrorfile):
	if    switch('mirror')                      : suffix = '.mirror'
	elif  switch('snap'  ) or switch('snapshot'): suffix = '.snapshot'
	if    len(clist)==0:
		r = Reason("No mirror specified.")
	elif len(clist)>1:
		r = Reason("You can only mirror one cache at a time.")
	else:
		if   len(switchItems('o'  ))>0: mirrorfile2 = switchItems('o'  )[0]
		elif len(switchItems('out'))>0: mirrorfile2 = switchItems('out')[0]
		else:                           mirrorfile2 = mirrorfile[:]
		
		if not tail(mirrorfile2,'.mirror'): mirrorfile2 = mirrorfile2+suffix
		r = Reason("File ["+mirrorfile2+"] already exists.",os.path.exists(mirrorfile2))
		if r.ok():
			Execution.execute('rm -r -f zzztmp'+suffix)
			cache = clist[0]
			if len(cache)>=2 and cache[:2]=='..': cache = fullpath(cache)
			if ESC in cache:
				r = Reason("Can't mirror or snapshot a cache with ["+ESC+"] in it's name ["+cache+"].")
			else:
				mirror = MirrorCache('zzztmp'+suffix,cache)
				if suffix=='.snapshot': mirror._snapshot = 1
				r = mirror.create()
			if r.ok(): r = Execution.execute('mv zzztmp'+suffix+' '+mirrorfile2)
			else:      print r
			if os.path.exists('zzztmp'+suffix) and not switch('debug'): Execution.execute('rm -r -f zzztmp'+suffix)
	return r
	
_shown     = {}
_messageDB = {}

class MirrorCache(Cache.Cache):
	def __init__(self,cache,mirror=''):
		self.type           = 'mirror'
		self._access        = UniversalAccess.UniversalAccess(cache)
		self.UCL            = `self._access`
		self._init          = 0
		self._location      = ''
		if self._access.accessor.type=='local directory': self._location = `self._access`
		self._mirror        = mirror
		self._snapshot      = 0
		self._createTime    = time.time()
		self._checkTime     = copy.deepcopy(self._createTime)
		self._updateTime    = copy.deepcopy(self._createTime)
		self._creator       = getusername()
		self._pacmanVersion = version[:]
		self._hostname      = socket.gethostname()
		self._pythonVersion = sys.version.replace('\n','')
		self._platform      = Platform.Platform().str()
		self._registry      = Registry.registry
		if self._access.accessor.type=='local directory': self._location = `self._access`
		
		self._names    = []
		self._newcache = None
		self._cache    = None
		self._leaf     = None
		
		self._top      = 1
		
	def str(self): 
		if hasattr(self,'_name'): return self._name
		else:                     return self.UCL
		
	def display(self,indent=0):
		upd = self._top and (displayMode('up') or verbo('up'))
		r = self.init()
		if not r.ok(): print indent*' '+`r`
		else:
			if self.leaf():
				if self._top: 
					if self._snapshot: print indent*' '+self.str()+' || '+Registry.registry.short(self._mirror)
					else:              print indent*' '+self.str()+' <| '+Registry.registry.short(self._mirror)
					self._leaf.display2(indent)
				else:         
					self._leaf.display (indent)
			else:
				if self._top: 
					if self._snapshot: print indent*' '+self.str()+' || '+Registry.registry.short(self._mirror)
					else:              print indent*' '+self.str()+' <| '+Registry.registry.short(self._mirror)
				else:         print indent*' '+Registry.registry.short(self._mirror)
				for c in self._cache: c.display(indent+4)
	
			if upd:
				if self._snapshot: print (indent)*' '+'Snapshot of:                              '+Registry.registry.short(self._mirror)
				else:              print (indent)*' '+'Mirror of:                                '+Registry.registry.short(self._mirror)
					
				print (indent)*' '+'Created by:                               '+self._creator
				print (indent)*' '+'Created on host:                          '+self._hostname
				print (indent)*' '+'Platform:                                 '+self._platform
				print (indent)*' '+'Python version:                           '+self._pythonVersion
				print (indent)*' '+'Pacman version:                           '+self._pacmanVersion
				print (indent)*' '+'Time of creation:                         '+time.ctime(self._createTime)
				print (indent)*' '+'Start of last successful -update-check:   '+time.ctime(self._checkTime )
				if not self._snapshot:
					print (indent)*' '+'End of last successful -update:           '+time.ctime(self._updateTime)
			if displayMode('up') or verbo('up'):
				if hasattr(self._newcache,'type'):
					print (indent)*' '+'=> Update of ['+Registry.registry.short(self._mirror)+'] is available:'
					print (indent+4)*' '+'Current cache list:'
					for c in self._cache: print (indent+4)*' '+'     '+c._name
					print (indent+4)*' '+'Updated cache list:'
					for c in self._newcache: print (indent+4)*' '+'     '+c._name
			if self._top and not self._snapshot:
				updates = self.getUpdates()
				if len(updates)>0:
					print (indent)*' '+'=> Updates of ['+Registry.registry.short(self._mirror)+'] are available:'
					for p in updates: p.display(indent+8)
				newcaches = self.getNewCaches()
				if len(newcaches)>0:
					print (indent)*' '+'=> These cache lists have been modified:'
					for c in newcaches: print (indent+8)*' '+c
					print (indent)*' '+'=> Update available.'
				if len(updates)==0 and len(newcaches)==0:
					print (indent)*' '+'=> Up to date.'
					
	def leaf(self): return hasattr(self._leaf,'get')
		
	def local(self):
		r = self.init()
		if r.ok(): 
			if self._location=='': r = Reason("Cache ["+self.str()+"] is not in the local file system.")
		return r

	def init(self):
		r = Reason()
		if not self._init:
			r,files = self._access.namesPath()
			if r.ok():
				if 'lock' in files:
					r = self._access.lockCheck()
					if not r.ok(): r = Reason("Mirror ["+self.str()+"] is being updated.  Try again later...")
				elif 'o..basemirror..o' in files:
					self._leaf   = MirrorBaseCache.MirrorBaseCache(self.UCL)
				if r.ok() and 'o..mirror..o' in files:
					r,tup = self._access.getObj('o..mirror..o')
					if r.ok():
						if len(tup)>11:
							self._mirror        = tup[ 0]
							self._createTime    = tup[ 1]
							self._checkTime     = tup[ 2]
							self._updateTime    = tup[ 3]
							self._creator       = tup[ 4]
							self._pacmanVersion = tup[ 5]
							self._names         = tup[ 6]
							self._newcache      = tup[ 7]
							self._hostname      = tup[ 8]
							self._pythonVersion = tup[ 9]
							self._platform      = tup[10]
							self._registry      = tup[11]
							if len(tup)>12: self._snapshot = tup[12]
							else:           self._snapthos = 0
							if not self.leaf():
								self._cache         = UniversalCache.CacheList(self.UCL)
								for name in self._names:
									tname = name. replace(':','_')
									tname = tname.replace('/',ESC)
									c = MirrorCache(os.path.join(self.UCL,tname))
									c._name = name
									c._top  = 0
									self._cache.append(c)
								self._cache._init = 1
							self._init = 1
						else:
							r = Reason("["+self.str()+"] is unreadable.")
				elif r.ok():
					r = Reason("["+self.str()+"] is not available at this time.")
		return r
		
	def save(self):
		r = Reason()
		if not self._location=='' and self._init:
			if not os.path.isdir(self._location): r = Reason("Can't save ["+self.str()+"].")
			if r.ok():
				try:
					removeFile(os.path.join(self._location,'o..mirror..o'))
					f = open(os.path.join(self._location,'o..mirror..o'),'w')
					tup = (self._mirror,self._createTime,self._checkTime,self._updateTime,  \
					       self._creator,self._pacmanVersion,self._names,self._newcache,    \
					       self._hostname,self._pythonVersion,self._platform,self._registry,\
					       self._snapshot,)
					cPickle.dump(tup,f)
					f.close()
					if 0 and self._snapshot:
						import md5sum
						r,hexsum = md5sum.md5sum(os.path.join(self._location,'o..mirror..o'))
						if r.ok():
							f = open(os.path.join(self._location,'snapshot'),'w')
							f.write(hexsum+'\n')
							f.close()
				except (IOError,OSError):
					r = Reason("Failure attempting to save ["+self.str()+"].")
		else:
			r = Reason("Can't save ["+self.str()+"].")
		return r
		
	def getUpdates(self):
		r = self.init().require()
		updates = []
		if self.leaf(): updates.extend(self._leaf.getUpdates())
		else:
			for c in self._cache: 
				x = c.getUpdates()
				updates.extend(c.getUpdates())
		return updates
	def getNewCaches(self):
		newcaches = []
		if not self.leaf():
			if hasattr(self._newcache,'type'): newcaches.append(Registry.registry.short(self._mirror))
			else:
				for c in self._cache: newcaches.extend(c.getNewCaches())
		return newcaches
		
	def readme(self):
		r = Reason()
		try:
			f = open(os.path.join(self._location,'README'),'w')
			f.write('#\n')
			f.write('#  DO NOT MODIFY THE CONTENTS OF THIS DIRECTORY\n')
			if self._snapshot: f.write('#      - This is a Pacman snapshot cache    - \n')
			else:              f.write('#      - This is a Pacman mirror cache    - \n')
			f.write('#      - Created and Modified by Pacman   - \n')
			f.write('#      - see http://physics.bu.edu/pacman - \n')
			f.write('#\n')
			f.close()
		except (IOError,OSError):
			r = Reason("Can't write to ["+self._location+"].")
		return r

	def create(self,name=''):
		r = Reason("Can't create ["+self.str()+"] from a remote location.",self._location=='')
		if r.ok(): r = Reason("No cache specified for ["+self.str()+"].",self._mirror=='')

		if r.ok():
			mirror = UniversalCache.UniversalCache(self._mirror)._cache
			if mirror.type=='list':
				self._createTime = time.time()
				self._checkTime  = copy.deepcopy(self._createTime)
				r = Execution.execute('rm -r -f '+self._location+'; mkdir '+self._location)
				if r.ok(): r = self.readme()
				if r.ok():
					r = mirror.init()
					if r.ok():
						self._leaf   = None
						self._cache  = UniversalCache.CacheList(self.UCL)
						self._names  = []
						for c in mirror:
							if hasattr(c,'_name'): 
								self._names.append(c._name)
							else:                  
								r = Reason("Can't mirror trusted.caches."); break
							t = string.replace(c._name,'/',ESC)
							t = string.replace(t      ,':','_')
							loc = os.path.join(self._location,t)
							mir = MirrorCache(loc,c.UCL)
							mir._name = c._name[:]
							r = mir.create(c._name)
							if not r.ok(): break	
							self._cache.append(mir)
						self._cache._init = 1
			elif mirror.type=='mirror':
				r = Reason("You can't currently mirror/snapshot a mirror/snapshot.  Attempting to mirror or snapshot ["+self._mirror+"].")
			else:
				c = MirrorBaseCache.MirrorBaseCache(self._location,self._mirror)
				c._name = name[:]
				
				r = c.create()
				self._leaf   = c
				self._cache  = None
				self._names  = []
			if r.ok(): 
				self._updateTime = time.time()
				if r.ok(): self._init = 1
				if r.ok(): r = self.save()
		return r

	def getAll(self,spec,used):
		r,ps = self.getAllBase(spec,used)
		if self._top and r.ok(): ps   = self.prependTop(ps)
		if self._top and r.ok(): r,ps = self.prepend(ps)
		for i in range(len(ps)): ps[i].setParent()
		return r,ps
	def getAllBase(self,spec,used):
		r,ps = Trust.trust.add(self.UCL),[]
		if r.ok(): r = self.init()
		if r.ok():
			if spec==Package.Spec():
				r,ps = self.contents([])
			else:
				if self.leaf(): r,ps = self._leaf. getAll(spec,used)
				else:           r,ps = self._cache.getAll(spec,used)
		if r.ok() and len(ps)==0: r = Reason("Can't find ["+spec.str()+"] in ["+self.str()+"].")
		if self._top and len(ps)>0 and not switch('l') and not switch('lc') and not switch('update') and not switch('update-check') and not spec==Package.Spec(): 
			if not _shown.has_key(ps[0]._spec.str()):
				verbo.log('cache','  '+ps[0]._spec.name+' found in '+Registry.registry.short(self.UCL)+'...')
				if verbo('cache-brief'): flicker(ps[0]._spec.str()+'...')
				_shown[ps[0]._spec.str()] = ''
		return r,ps

	def contents(self,used):
		r,ps = self.contentsBase(used)
		if self._top and r.ok(): ps   = self.prependTop(ps)
		if self._top and r.ok(): r,ps = self.prepend(ps)
		for i in range(len(ps)): ps[i].setParent()
		return r,ps
	def contentsBase(self,used):
		r,ps = Trust.trust.add(self.UCL),[]
		if r.ok(): r = self.init()
		if r.ok():
			if self.leaf(): r,ps = self._leaf. contents(used)
			else:           r,ps = self._cache.contents(used)
		return r,ps

	def updateCheck(self):
		r = self.init()
		if r.ok(): r = self.local()
		if r.ok(): 
			t = time.time()
			if self.leaf():
				r = self._leaf.updateCheck()
			else:
				mirror = UniversalCache.UniversalCache(self._mirror)._cache
				if mirror.type=='list':
					mirror.init()
					self._newcache = UniversalCache.CacheList('')
					for c in mirror:
						loc = c._name.replace(':','_')
						loc = loc.    replace('/',ESC)
						loc = os.path.join(self._location,loc)
						mir = MirrorCache(loc,c.UCL)
						mir._name = c._name[:]
						self._newcache.append(mir)
					if len(self._cache)==len(self._newcache) and forall(range(len(self._cache)),lambda i: self._cache[i]._name==self._newcache[i]._name):
						self._newcache = None
					else:
						if self._snapshot:  
							verbo.log('up','=> Update of ['+Registry.registry.short(self._mirror)+'] exists.')
							verbo.log('up',"=> Snapshot ["+`self`+"] can't be updated, however.")
						elif not switch('update'):               
							verbo.log('up','=> Update of ['+Registry.registry.short(self._mirror)+'] found.')
							verbo.log('up',"=> Use -update to update ["+`self`+"].")
				for c in self._cache:
					r = c.updateCheck()
					if not r.ok(): break
			if r.ok(): 
				self._checkTime = t
				r = self.save()
		return r
		
	def updateResolve(self):
		r = self.init()
		if r.ok():
			if self.leaf():
				r = self._leaf.updateResolve()
			else:
				for c in self._cache:
					r = c.updateResolve()
					if not r.ok(): break
		return r
		
	def updateTrans(self):
		r = self.init()
		if r.ok():
			if self.leaf():
				r = self._leaf.updateTrans()
			else:
				for c in self._cache:
					r = c.updateTrans()
					if not r.ok(): break
		return r
		
	def newcaches(self):
		r = self.local()
		if hasattr(self._newcache,'type'):
			for c in self._newcache:
				if not c.init().ok():
					verbo.log('up','Adding ['+`c`+'] to mirror...')
					r = c.create(c._name)
					if not r.ok(): break
			#-- remove caches which are no longer in the cache list
			if r.ok():
				for c in self._cache:
					if not exists(self._newcache,lambda d: d._name==c._name):
						verbo.log('up','Removing ['+c._name+'] from mirror...')
						r = Execution.execute('rm -r -f '+c.UCL)
						if not r.ok(): break
				if r.ok():
					self._cache = copy.deepcopy(self._newcache)
					self._names = []
					for c in self._cache: self._names.append(c._name)
					self._updateTime = time.time()
					self._newcache = None
		if r.ok() and not self.leaf():
			for c in self._cache:
				r = c.newcaches()
				if not r.ok(): break
		if r.ok(): r = self.save()
		return r
		
	def update(self):
		r = self.init()
		if r.ok(): r = Reason("Snapshots can be checked for updates, but cannot be updated.  Can't update ["+`self`+"].",self._snapshot)
		if r.ok():
			bad = 0
			try:
				if r.ok(): r = self.local()
				if r.ok(): r = self.lock()
				if r.ok(): Access._freeLock[`self._access`] = ''
				if r.ok(): r = self.updateCheck()
				if r.ok(): r = self.newcaches()
				if r.ok(): r = self.updateResolve()
				if r.ok(): 
					r = self.updateTrans()
					if not r.ok(): bad = 1
				if r.ok(): 
					self._updateTime = time.time()
					r = self.save()
			except:
				if not bad: self.unlock()
				raise
			self.unlock()
		return r
		
	def lock(self,message='Cache is being modified...'):
		r = self.init()
		if r.ok(): 
			if self._location=='': r = Reason("Can't lock ["+self.str()+"] from remote location.")
			else:
				try:
					f = open(os.path.join(self._location,'lock'),'w')
					f.write(message)
					f.close()
				except (IOError,OSError):
					r = Reason("Can't write to ["+self.str()+"].")
		return r
	def unlock(self):
		if self._location=='': 
			r = Reason("Can't unlock ["+self.str()+"] from remote location.")
		else:
			r = Execution.execute('rm '+os.path.join(self._location,'lock'))
		return r
