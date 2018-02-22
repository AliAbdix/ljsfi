#
#	Copyright, February 2005, Saul Youssef
#
from Base        import *
from Environment import *
import ShellCommand,Cache,Package,Platform,cPickle,Trust,Registry
import time,shelve,whichdb

if os.path.exists(os.path.join(pacmanDir,'ii3.1')): oversion = '3.19'
else:                                               oversion = version[:]

def specStr(spec,status,indent=0):
	installable,installed,update = status
	s = indent*' '
	if         installed: s = s + '[*]'
	else:                 s = s + '[ ]'
	s = s + ' ' + spec.str()
	if update: s = s + '  << UPDATE AVAILABLE >>'
	return s
	
def pathsub(a,b):
	sub = 0
	a2 = a[:]; b2 = b[:]
	if len(a2)>0 and len(b2)>0:
		if not a2[-1]=='/': a2 = a2 + '/'
		if not b2[-1]=='/': b2 = b2 + '/'
		
		if len(b2)>len(a2):
			if b2[:len(a2)]==a2[:len(a2)]: sub = 1
	return sub
	
def fileify2(x): return `abs(hash(x))`

_dbs = {}
_dbfileDB = {}
_spfileDB = {}
_exfileDB = {}
_shfileDB = {}

class InstallationCache(Cache.Cache):
	def __init__(self,directory='.'):
		self._dbfile = os.path.join(fullpath(directory),pacmanDir,'ii'+oversion[:3])
		self._spfile = os.path.join(fullpath(directory),pacmanDir,'is'+oversion[:3])
		self._exfile = os.path.join(fullpath(directory),pacmanDir,'ie'+oversion[:3])
		self._shfile = os.path.join(fullpath(directory),pacmanDir,'sh'+oversion[:3])
		self._dafile = os.path.join(fullpath(directory),pacmanDir,'da'+oversion[:3])
		self._db       = {}
		self._sp       = {}
		self._ex       = {}
		self._quotient = {}
		self._init = 0
		self._mode = 'r'
		self._location = fullpath(directory)
		if writeable(self._location): self._mode = 'rw'
		else:                         self._mode = 'r'
		self.UCL = self._location
		self.type = 'installation'
		self._date = ''
		
		self._cacheDB = {}

	def in_get_key(self,key):
		if self._cacheDB.has_key(key):
			p = self._cacheDB[key]
		else:
			if verbo('io'): print 'Reading ['+key+']...'
			try:
				p = self._db[key]
			except:
				abort("Error reading from ["+os.path.join(self._dbfile,fileify2(key))+"] in Pacman database.")
			if verbo('io'): print 'Done reading ['+p.str()+']...'
			self._cacheDB[key] = p
		return p
		
	def in_put_key(self,key,p):
		if verbo('io'): print 'Writing ['+p.str()+'] to ['+key+']...'
		try:
			self._db[key] = p
		except KeyboardInterrupt:
			del self._db[key]
			raise
		except:
			del self._db[key]
			abort("Error writing to Pacman database.")
		if verbo('io'): print 'Done writing ['+p.str()+']...'
		self._cacheDB[key] = p
	
	def in_remove_key(self,key):
		try:
			del self._db[key]
		except KeyboardInterrupt:
			del self._db[key]
			raise
		except (IOError,OSError,EOFError):
			abort("Error writing to Pacman database.")
		if self._cacheDB.has_key(key): del self._cacheDB[key]
	
	def display(self,indent=0):
		r,ps = self.getAll(Package.Spec(),[])
		r.require()
		def le(p,q): return p._spec.name<=q._spec.name
		sort(ps,le)
		print indent*' '+`self`
		for p in ps: p.display(indent+4)

	def qinit(self):
		self._quotient = {}
		for k,spec in self._sp.items(): self.qadd(spec)
	def qadd(self,spec):
		if self._quotient.has_key(spec.name): 
			if not (`spec._id()` in self._quotient[spec.name]):
				self._quotient[spec.name].append(`spec._id()`)
		else:                                 
			self._quotient[spec.name] =     [`spec._id()`]
	def qrem(self,spec):
		r = Reason()
		if self._quotient.has_key(spec.name):
			try:
				self._quotient[spec.name].remove(`spec._id()`)
				if len(self._quotient[spec.name])==0: del self._quotient[spec.name]
			except ValueError:
				r = Reason("Installation has been corrupted.")
		else:
			r = Reason("Installation has been corrupted.")
		return r

	def platform(self):
		r = Reason()
		pf = fullpath(os.path.join(self.UCL,pacmanDir,'platform'))
		r = Reason("Can't read ["+pf+"].",not readAccess(pf))
		if r.ok(): platform = get(pf)
		else:      platform = Platform.Platform()
		return r,platform

	def init(self):
		r = Reason()
		if self._init==0:
			r,platform = self.platform()
			if r.ok(): r = Reason("Cache ["+`self`+"] installed on ["+`platform`+"].",not allow('any-platform') and not platform==Platform.Platform())
			if r.ok():
				if os.path.exists(self._dbfile): 
					if os.path.isdir(self._dbfile): r = Reason("Installation made with Pacman < 3.2.")
				else:
					verbo.log('io','Opening ['+self._dbfile+']...')
					dbp = dbpath(self._dbfile)
					if whichdb.whichdb(dbp)=='gdbm': 
						r = Reason('Default gdbm database has problems.  Use -allow old-database')
			if r.ok():
				try:
					verbo.log('io','Reading ['+self._dbfile+'], database type ['+`whichdb.whichdb(self._dbfile)`+']...')
					if not _dbfileDB.has_key(self._dbfile):
						t = open(self._dbfile,self._mode)
						verbo.log('io','Reading installation database...')
						_dbfileDB[self._dbfile] = cPickle.load(t)
						t.close()
					self._db = _dbfileDB[self._dbfile]
					
					if not _spfileDB.has_key(self._spfile):
						s = open(self._spfile,self._mode)
						_spfileDB[self._spfile] = cPickle.load(s)
						s.close
					self._sp = _spfileDB[self._spfile]
					
					if not _exfileDB.has_key(self._exfile):
						x = open(self._exfile,self._mode)
						_exfileDB[self._exfile] = cPickle.load(x)
						x.close()
					self._ex = _exfileDB[self._exfile]
					
					if not _shfileDB.has_key(self._shfile):
						y = open(self._shfile,self._mode)
						_shfileDB[self._shfile] = cPickle.load(y)
						y.close()
					xdb = _shfileDB[self._shfile]
						
					if os.path.exists(self._dafile):
						z = open(self._dafile,'r')
						lines = z.readlines()
						z.close()
						self._date = lines[0][:-1]
					else:
						self._date = time.ctime(time.time())
					ShellCommand.ShellCommand._executed.update(xdb)
					self.qinit()
					self._init = 1
				except (IOError,OSError,EOFError):
#				except:
					r = Reason("Can't open Pacman database ["+self._dbfile+"].")
			if r.ok():
				if not (len(self._sp)==len(self._ex)):
					r = Reason("Installation ["+`self`+"] has been corrupted.")
		return r
	def save(self):
		r = self.writeable()
		if r.ok():
			try:
				verbo.log('io','Saving ['+`self`+']...')
#				self._db.close()
				removeFile(self._dbfile+'.tmp')
				t = open(self._dbfile+'.tmp','w')
				cPickle.dump(self._db,t)
				t.close()
				os.system('mv -f '+self._dbfile+'.tmp '+self._dbfile)
				s = open(self._spfile,'w')
				cPickle.dump(self._sp,s)
				s.close()
				x = open(self._exfile,'w')
				cPickle.dump(self._ex,x)
				x.close()
				y = open(self._shfile,'w')
				cPickle.dump(ShellCommand.ShellCommand._executed,y)
				y.close()
				z = open(self._dafile,'w')
				z.write(time.ctime(time.time())+'\n')
				z.close()
			except (IOError,OSError):
				r = Reason("Error writing to ["+self._spfile+"].")
		return r
	def writeable(self):
		r = self.init()
		if r.ok() and self._mode!='rw': r = Reason("No write access to ["+`self`+"].")
		return r
		
	def extra(self,p):
		r = self.init()
		if r.ok(): t = p.status()
		else:      t = (0,0,0,'.',)
		return t
#-- Cache
	def put(self,p2): 
		pspec = copy.deepcopy(p2._spec)
		while len(pspec.caches)>0 and Registry.registry.equiv(pspec.caches[0],self.UCL):
			pspec.caches.pop(0)
		if self._cacheDB.has_key(`pspec._id()`):
			return Reason('ok')
		p = copy.deepcopy(p2)
		p._spec = pspec
		r = self.writeable()
		if r.ok(): r = ask.re('package-add','About to add ['+p.str()+'] to ['+`self`+']. OK?')
		if r.ok():
			if verbo('inst'): print 'Putting ['+p._spec.name+'] in ['+`self`+']...'
			p._inCache = self.UCL
			idd = p._spec._id()
			try:
				self.in_put_key(`idd`,p)
				self._sp [`idd`] = copy.deepcopy(p._spec)
				self._ex [`idd`] = self.extra(p)
				self.qadd(p._spec)
			except:
				r = Reason('Error writing to Pacman database.')
		return r
	
	def contents(self,used):
		r,ps = self.getAll(Package.Spec(),[])
		return r,ps
		
	def getLocation(self,location):
		r,ps = Trust.trust.add(self.UCL),[]
		if r.ok(): r = self.init()
		
		if r.ok():
			keys = self._ex.keys()
			for key in keys:
				if location==os.path.commonprefix([location,self._ex[key][3]]): 
					p = self.in_get_key(key)
					self.prependTemp(p)
					ps.append(p)
		return r,ps
	
	def prependTemp(self,p):
		self.prependTempBase(p._environ,'foo')
		self.prependTempBase(p._source ,'foo')
		p._spec.caches.insert(0,Registry.registry.short(self.UCL))
		
	def prependTempBase(self,e,cache):
		if e.type=='AND' or e.type=='OR':
			for i in range(len(e)): self.prependTempBase(e[i],cache)
		elif e.type=='lazy package':
			e._spec.caches.insert(0,Registry.registry.short(self.UCL))

	def getAll(self,spec,used):
		r,ps = Trust.trust.add(self.UCL),[]
		if r.ok(): r = self.init()
		if r.ok(): r,used = self.check(spec,used)
		
		if r.ok():
			if string.strip(spec.name)=='' or string.strip(spec.name)=='*':
				keys = self._sp.keys()
				for key in keys:
					p = self.in_get_key(key)
					if spec.satisfiedBy(p): ps.append(p)
			else:
				if self._quotient.has_key(spec.name):
					for idd in self._quotient[spec.name]:
						if not self._sp.has_key(idd): abort("Old Pacman database is incompatible with Pacman ["+version+"].")
						if self._sp[idd]<=spec:
							p = self.in_get_key(idd)
							p._inCache = self.UCL
							pspeccopy = copy.deepcopy(p._spec)
							if len(pspeccopy.caches)>0 and Registry.registry.equiv(pspeccopy.caches[0],self.UCL):
								pspeccopy.caches.pop(0)
							spec2 = copy.deepcopy(spec)
							if len(spec2.caches)>0 and Registry.registry.equiv(spec2.caches[0],self.UCL):
								spec2.caches.pop(0)
							doit=0
							if spec2.satisfiedBy(p):
								doit=1
							else:
								old_spec = p._spec
								p._spec = pspeccopy
								if spec2.satisfiedBy(p):
									doit=1
								p._spec = old_spec
							if doit:
								if not pac_anchor==fullpath(self.UCL): 
									p._neutered=1
									p._parents = []
									for i in range(len(p._modifiers)): p._modifiers[i].caches.insert(0,self.UCL)
								if verbo('inst'):
									print 'Getting package ['+spec.str()+'] from ['+self.UCL+']:'
									p.display(4)
								ps.append(p)
			if   len(self._sp.keys())==0: r = Reason("Installation ["+`self`+"] is empty.")
			elif len(             ps)==0: r = Reason("Can't find ["+spec.str()+"] in ["+`self`+"].")
		if len(ps)>0 and not self.UCL==pac_anchor and not switch('l') and not switch('lc') and not switch('update') and not switch('update-check'): 
			if verbo('cache'): print 'Package ['+ps[0]._spec.str()+'] found in ['+`self`+']...'
		if r.ok(): ps   = self.prependTop(ps)
		if r.ok(): r,ps = self.prepend   (ps)
		return r,ps

	def topSpecs(self):
		topspecs = []
		Trust.trust.add(self.UCL).require()
		self.init().require()
		
		keys = self._sp.keys()
		nkeys = len(keys)
		goList  = verbo('io')
		goMeter = not goList and verbo('meter') and nkeys>200
		if goMeter: m = Meter(nkeys,'Reading database...')

		count = 0
		for key in keys:
			count = count + 1
			p = self.in_get_key(key)
			if   goList : print 'Reading ['+p._spec.str()+']...'
			elif goMeter: m.meter(count)
			if len(p.parents())==0: topspecs.append(p._spec)
			del p
		return topspecs
			
	def refreshParents(self):
		used = []
		r = self.init()
		
		if r.ok():
			keys = self._sp.keys()
			nkeys = len(keys)
			goList  = verbo('io')
			goMeter = not goList and verbo('meter') and nkeys>200
			if goMeter: m = Meter(nkeys,'Reading database...')
			count = 0
			for key in keys:
				count = count + 1
				p = self.in_get_key(key)
				if   goList : print 'Reading ['+p._spec.str()+']...'
				elif goMeter: m.meter(count)
				
				if not p.type=='lazy package':
					pars = []
					for par in p._parents:
						rr,pp = self.get(par)
						if rr.ok(): pars.append(par)
					p._parents = pars[:]
					mods = []
					for mod in p._modifiers:
						rr,pp = self.get(mod)
						if rr.ok(): mods.append(mod)
					p._modifiers = mods[:]
					self.put(p).require()
		return r
	def _cleanUpParents(self,spec):
		keys = self._sp.keys()
		for key in keys:
			p = self.in_get_key(key)
			parents,modifiers = [],[]
			for sp in p._parents:
				if not spec<=sp: parents.append(sp)
			for sp in p._modifiers:
				if not spec<=sp: modifiers.append(sp)
			p._parents   = parents
			p._modifiers = modifiers
			self.put(p).require()
	def remove(self,spec):
		r = self.writeable()
		if r.ok():
			tspec = copy.deepcopy(spec)
			if len(tspec.caches)>0 and Registry.registry.equiv(tspec.caches[0],self.UCL): tspec.caches.pop(0)
			for idd in self._sp.keys():
				spec2 = self._sp[idd]
#				if spec2<=tspec:
				if spec2==tspec:
					if tspec.guard=='':
						self.in_remove_key(idd)
						del self._sp[idd]
						del self._ex[idd]
						self.qrem(spec2)
					else:
						p = self.in_get_key(idd)
						if spec.satisfiedBy(p) or tspec.satisfiedBy(p):
							self.in_remove_key(idd)
							del self._sp[idd]
							del self._ex[idd]
							self.qrem(spec2)
			self._cleanUpParents(spec)			
		return r

class OldInstallationCache(InstallationCache):
	def in_get_key(self,key):
		if self._cacheDB.has_key(key):
			p = self._cacheDB[key]
		else:
			if verbo('io'): print 'Reading ['+os.path.join(self._dbfile,fileify2(key))+']...'
			try:
				f = open(os.path.join(self._dbfile,fileify2(key)),'r')
				p = cPickle.load(f)
				f.close()
			except (IOError,OSError,EOFError):
				abort("Error reading from ["+os.path.join(self._dbfile,fileify2(key))+"] in Pacman database.")
			if verbo('io'): print 'Done reading ['+os.path.join(self._dbfile,fileify2(key))+']...'
			self._cacheDB[key] = p
		return p
		
	def in_put_key(self,key,p):
		if verbo('io'): print 'Writing ['+os.path.join(self._dbfile,fileify2(key))+']...'
		try:
			path = os.path.join(self._dbfile,fileify2(key))
			removeFile(path)
			f = open(path,'w')
			cPickle.dump(p,f)
			f.close()
		except:
			removeFile(os.path.join(self._dbfile,fileify2(key)))
			abort("Error writing to ["+os.path.join(self._dbfile,fileify2(key))+"] in Pacman database.")
		if verbo('io'): print 'Done writing ['+os.path.join(self._dbfile,fileify2(key))+']...'
		self._cacheDB[key] = p
		
	def in_remove_key(self,key):
		path = os.path.join(self._dbfile,fileify2(key))
		removeFile(path)
		if self._cacheDB.has_key(key): del self._cacheDB[key]

	def init(self):
		r = Reason()
		if self._init==0:
			r,platform = self.platform()
			if r.ok(): r = Reason("Cache ["+`self`+"] installed on ["+`platform`+"].",not platform==Platform.Platform())
			if r.ok():
				if os.path.exists(self._dbfile):
					if readAccess(self._dbfile):
						self._mode = 'r'
						if writeAccess(self._dbfile): self._mode = 'rw'
					else:
						r = Reason("No read access to ["+`self`+"].")
				else:
					r = Reason("Installation ["+`self`+"] does not exist.")
			if r.ok():
				try:
					verbo.log('io','Reading ['+`self`+']...')
					if not os.path.exists(self._dbfile) and contains(self._mode,'w'):
						os.system('mkdir '+self._dbfile)
#					self._db = shelve.open(self._dbfile,self._mode)
					s = open(self._spfile,self._mode)
					self._sp = cPickle.load(s)
					s.close
					x = open(self._exfile,self._mode)
					self._ex = cPickle.load(x)
					x.close()
					y = open(self._shfile,self._mode)
					xdb = cPickle.load(y)
					y.close()
					if os.path.exists(self._dafile):
						z = open(self._dafile,'r')
						lines = z.readlines()
						z.close()
						self._date = lines[0][:-1]
					else:
						self._date = time.ctime(time.time())
					ShellCommand.ShellCommand._executed.update(xdb)
					self.qinit()
					self._init = 1
				except (IOError,OSError,EOFError):
					r = Reason("Can't open ["+self._dbfile+"].")
			if r.ok():
				if not (len(self._sp)==len(self._ex)):
					r = Reason("Installation ["+`self`+"] has been corrupted.")
		return r
	def save(self):
#		r = Reason()
		r = self.writeable()
		if r.ok():
			try:
				verbo.log('io','Saving ['+`self`+']...')
#				self._db.close()
				s = open(self._spfile,'w')
				cPickle.dump(self._sp,s)
				s.close()
				x = open(self._exfile,'w')
				cPickle.dump(self._ex,x)
				x.close()
				y = open(self._shfile,'w')
				cPickle.dump(ShellCommand.ShellCommand._executed,y)
				y.close()
				z = open(self._dafile,'w')
				z.write(time.ctime(time.time())+'\n')
				z.close()
			except (IOError,OSError):
				r = Reason("Error writing to ["+self._spfile+"].")
		return r
