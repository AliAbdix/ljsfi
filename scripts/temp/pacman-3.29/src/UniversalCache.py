#
#	Copyright, 2004,2005, Saul Youssef
#
from Base        import *
from Environment import *
import UniversalAccess,Package,Registry,CD,Directory,Execution,Download,Platform
#import Cache,SourceCache,InstallationCache,SnapshotCache,Home,Trust,MirrorCache,RelPath
import Cache,SourceCache,InstallationCache,SnapshotCache,Trust,MirrorCache,RelPath
import time,cPickle,whichdb,os,string

excluded = []

def leqCache(cache,c):  return c==cache._name or Registry.registry.equiv(cache.UCL,c)

def equivalentCaches(c1,c2): return Registry.registry.equiv(c1,c2)

def meqSpec(cache,c,spec):
	meq = 0
	if hasattr(spec,'_mirrors'):
		if spec._mirrors.has_key(c):
			specMirror,specTime,specSnapshot = spec._mirrors[c]
			if    hasattr(cache,'_mirror'): m = cache
			elif  hasattr(cache,'_cache' ): m = cache._cache
			else:  abort('Error in Pacman.  Please contact http://physics.bu.edu/pacman/ ')
			
			r = m.init()
			if r.ok():
				mirror   = m._mirror
				time     = m._updateTime
				snapshot = m._snapshot
			
				meq = Registry.registry.equiv(specMirror,mirror) and specTime==time and specSnapshot and snapshot
	return meq

_eqMirrorDB = {}
def getTypeMirrorTimeSnapshot(c):
	r,mirror,time,snapshot = Reason('Not a mirror or snapshot.'),'',0.0,0
	cache = UniversalCache(c)._cache
	ctype = cache.type
	if ctype=='mirror':
		if not _eqMirrorDB.has_key(cache.UCL):
			r = cache.init()
			if r.ok(): mirror,time,snapshot = cache._mirror,cache._updateTime,cache._snapshot
			_eqMirrorDB[cache.UCL] = (ctype,r,mirror,time,snapshot,)
		ctype,r,mirror,time,snapshot = _eqMirrorDB[cache.UCL]
	return ctype,r,mirror,time,snapshot

def equivalentCaches2(c1,c2):
	eq = Registry.registry.equiv(c1,c2)
	if not eq:
		t1,r1,mirror1,time1,snapshot1 = getTypeMirrorTimeSnapshot(c1)
		t2,r2,mirror2,time2,snapshot2 = getTypeMirrorTimeSnapshot(c2)
		
		if t1=='mirror' and t2=='mirror' and r1.ok() and r2.ok() and snapshot1 and snapshot2 and time1 and time2 \
		   and Registry.registry.equiv(mirror1,mirror2): 
		   	eq = 1
			if eq: verbo.log('snap','Snapshots ['+c1+'] and ['+c2+'] are equivalent.')
			else:  verbo.log('snap','Snapshots ['+c1+'] and ['+c2+'] are not equivalent.')
	return eq
 
def selectFun(E,f):
	sel = []
	if   E.type=='AND' or E.type=='OR':
		for e in E: sel.extend(selectFun(e,f))
	elif E.type=='lazy package':
		pass
	elif f(E):
		sel.append(E)
	return sel

def snap(e,identity):
	if   e.type=='package':
		r,environ = snap(e._environ,identity)
		E = copy.deepcopy(e)
		E._environ = copy.deepcopy(environ)
	elif e.type=='AND':
		r,E = Reason(),AND()
		for ee in e:
			r,ee2 = snap(ee,identity)
			if r.ok(): E.append(ee2)
			else: break
	elif e.type=='OR':
		r,E = Reason,OR()
		for ee in e:
			r,ee2 = snap(ee,identity)
			if r.ok(): E.append(ee2)
			else: break
	elif e.type=='download':
		downloadIdentity = `abs(hash(e._url+'-'+time.ctime(time.time())))`
		downdir = os.path.join(pac_anchor,pacmanDir,'downloads',identity,downloadIdentity)
		r = Execution.execute('rm -r -f '+downdir+'; mkdir '+downdir)
		if r.ok(): 
			cwd = os.getcwd()
			os.chdir(downdir)
			down = copy.deepcopy(e)
			verbo.log('snap','Adding ['+e._url+'] to snapshot...')
			if '$' in down._url: r = Reason("Unresolved environment variable.  Can't download ["+down._url+"].")
			else:                r = down.satisfy()
			os.chdir(cwd)
		E = copy.deepcopy(e)
		E._url = os.path.join('$PAC_ANCHOR',pacmanDir,'snapshots',identity,downloadIdentity,os.path.basename(e._url))
	elif e.type=='downloadUntarzip':
		downloadIdentity = `abs(hash(e._download._url+'-'+time.ctime(time.time())))`
		downdir = os.path.join(pac_anchor,pacmanDir,'downloads',identity,downloadIdentity)
		r = Execution.execute('rm -r -f '+downdir+'; mkdir '+downdir)
		if r.ok():
			cwd = os.getcwd()
			os.chdir(downdir)
			down = copy.deepcopy(e._download)
			verbo.log('snap','Adding ['+e._download._url+'] to snapshot...')
			if '$' in down._url: r = Reason("Unresolved environment variable.  Can't download ["+down._url+"].")
			else:                r = down.satisfy()
			os.chdir(cwd)
		E = copy.deepcopy(e)
		E._download._url = os.path.join('$PAC_ANCHOR',pacmanDir,'snapshots',identity,downloadIdentity,os.path.basename(e._download._url))
	else:
		r,E = Reason(),e
	return r,E
	
def _exsat(e):
	r = e.satisfy()
	if not r.ok():
		print r
		if yesno('Download has failed.  Continue? (y/n):'): r = Reason()
	r.require()
	
	
def extractDownPackage(e):
	if    e.type=='package': 
		extractDownPackage(e._environ)
	elif  e.type=='AND' or e.type=='OR':
		for ee in e: extractDownPackage(ee)
	elif e.type=='download':
		if os.path.exists(os.path.basename(e._url)) and not allow('extract-downloads-overwrite'):
			print 'WARNING: ['+os.path.basename(e._url)+'] already exists.'
			if allow('extract-overwrite') or yesno('Download and overwrite anyway? (use -allow extract-overwrite to avoid this question)'): 
				print 'Overwriting ['+os.path.basename(e._url)+']...'
				_exsat(e)
			else:
				print 'Skipping ['+os.path.basename(e._url)+']...'
		else:
			_exsat(e)
	elif e.type=='downloadUntarzip':
		if os.path.exists(os.path.basename(e._download._url)) and not allow('extract-downloads-overwrite'): 
			print 'WARNING: ['+os.path.basename(e._download._url)+'] already exists.'
			if allow('extract-overwrite') or yesno('Download and overwrite anyway? (use -allow extract-overwrite to avoid this question)'):
				print 'Overwriting ['+os.path.basename(e._download._url)+']...'
				_exsat(e._download)
			else:
				print 'Skipping ['+os.path.basename(e._download._url)+']...'
		else:
			_exsat(e._download)
		
_cached_caches = {}
_source_error_messages = {}
		
class UniversalCache(Cache.Cache):
	def __init__(self,UCL):
		self.UCL = UCL
		cn = Registry.registry.trans(UCL)
		
		if 0 and contains(UCL,'..'): cn = fullpath(UCL)
		
		if _cached_caches.has_key(cn):
			self._cache = _cached_caches[cn]
		else:
			if                                  cn==           'null': self._cache = Cache.NullCache                        ()
			elif                                cn==           'home': 
				import Home
				self._cache = Home.home                                
			elif                                cn== 'trusted.caches': self._cache = CacheList          ('trusted.caches',0,1)
			elif                                tail(cn,'.mirror'   ): self._cache = MirrorCache.MirrorCache              (cn)
			elif                                tail(cn,'.mirror/'  ): self._cache = MirrorCache.MirrorCache              (cn)
			elif                                tail(cn,'.snapshot' ): 
				self._cache = MirrorCache.MirrorCache(cn)
				self._cache._snapshot = 1
			elif                                tail(cn,'.snapshot/'): 
				self._cache = MirrorCache.MirrorCache(cn)
				self._cache._snapshot = 1
			elif                                tail(cn,'.snap'     ): self._cache = SnapshotCache.SnapshotCache          (cn)
			elif                                tail(cn,'.caches'   ): self._cache = CacheList                            (cn)
			else:
				xpath = fullpath(cn)
				xinst = 1
				try:
					xl = os.listdir(xpath)
					for l in xl: 
						if tail(l,'.pacman'): 
							if xpath==pac_anchor and not _source_error_messages.has_key(l):
								_source_error_messages[l]=''
								print "Move Pacman source files from the current working directory if you're trying to install them."
								print 'Ignoring Pacman source file ['+l+'] in current working directory.'
							else:
								xinst = 0; break
				except:
					pass
				if xinst:
					if os.path.isdir(os.path.join(fullpath(cn),pacmanDir)):
						if os.path.isdir(os.path.join(fullpath(cn),pacmanDir,'ii3.1')):
							verbo.log('io','Using vanilla db.')
							self._cache = InstallationCache.OldInstallationCache (cn)
						elif whichdb.whichdb(os.path.join(fullpath(cn),pacmanDir,'ii3.1'))=='dbhash':
							abort('Old Pacman installation.  Please re-install to use Pacman >= 3.18.')
						else:
							verbo.log('io','Using standard db.')
							self._cache = InstallationCache.InstallationCache  (cn)
					else:
						self._cache = SourceCache.SourceCache(cn)
				else:
					self._cache = SourceCache.SourceCache(cn)														
			_cached_caches[cn] = self._cache
			if debug('cache'): print 'Cache ['+self.UCL+'] translated to ['+cn+'] type ['+self._cache.type+']...'
		self.type = self._cache.type
		if hasattr(self._cache,'_name'): self._name = self._cache._name
		elif self.UCL=='.': self._name = pac_anchor
		else:               self._name = Registry.registry.short(self.UCL)
		
	def display (self,indent=0): 
		if hasattr(self,'_name'): self._cache._name = self._name
		self._cache.display(indent)
		
	def getAll  (self,spec,used   ): return self._cache.getAll  (  spec,used)
	def put     (self,package     ): return self._cache.put     (    package) 
	def remove  (self,spec        ): return self._cache.remove  (       spec)
	def contents(self,used        ): return self._cache.contents(       used)
	def snapshot(self,outfile2=''):
		identity = `abs(hash(self.UCL+'-'+time.ctime(time.time())))`
		if outfile2=='': outfile = identity+'.snap'
		else:            outfile = outfile2
		
		if   len(switchItems('o'  ))>0: outfile = switchItems('o'  )[0]
		elif len(switchItems('out'))>0: outfile = switchItems('out')[0]
		
		outdir = '../../'
		if not os.path.dirname(outfile)=='':
			outdir  = outfile
			outfile = os.path.basename(outfile)
		
		snapdir = os.path.join(pac_anchor,pacmanDir,'downloads',identity)
		r,ps = self.contents([])
		if r.ok():
			verbo.log('snap','Creating snapshot of ['+self.UCL+']...')
			if r.ok(): r = Execution.execute('rm -r -f '+snapdir)
			if r.ok(): r = Execution.execute('mkdir '   +snapdir)
			if r.ok():
				qs = []
				for p in ps:
					if p.lastsat or p.lastfail:
						r = Reason("Can't snapshot installed package ["+p.str()+"].")
						break
					p._parents   = []
					p._modifiers = []
					p._neutered  =  0
					p.lastsat    =  0
					p.lastfail   =  0
					r,q = snap(p,identity)
					if r.ok(): qs.append(q)
					else: break
				if r.ok():
					f = open(os.path.join(snapdir,'identity'),'w')
					f.write(identity+'\n')
					f.write(self.UCL+'\n')
					f.write(time.ctime(time.time())+'\n')
					f.write(getusername()+'\n')
					f.write(pac_anchor+'\n')
					f.write(`Platform.Platform()`+'\n')
					f.write(version+'\n')
					f.close()
					f = open(os.path.join(snapdir,'packages'),'w')
					cPickle.dump(qs,f)
					f.close()
				if r.ok(): r = Execution.execute('cd '+os.path.join(pac_anchor,pacmanDir,'downloads')+'; tar cf '+outfile+' '+identity)
				if r.ok(): r = Execution.execute('cd '+os.path.join(pac_anchor,pacmanDir,'downloads')+'; mv '+outfile+' '+outdir)
				if r.ok(): r = Execution.execute('cd '+os.path.join(pac_anchor,pacmanDir,'downloads')+'; rm -r -f '+identity)
		return r
	def extractSources(self):
		r,ps = self.contents([])
		r.require()
		count = 0
		for p in ps:
			count = count + 1
			filename = p._spec.file
			if filename=='': filename = 'no-file-name-'+`count`+'.pacman'
			if os.path.exists(filename): abort('File ['+filename+'] already exists.')
			f = open(filename,'w')
			for line in p._sourceCode: f.write(line)
			f.close()
		return r
	def extractDownloads(self):
		r,ps = self.contents([])
		r.require()
		for p in ps: extractDownPackage(p)
		return r
	def domain(self):
		r,ps = self.contents([])
		r.require()
		
		if r.ok():
			atoms = []
			for p in ps: atoms.extend(selectFun(p._environ,lambda e:          1))
			
			cl = Clusters(atoms)
			def equiv(a,b): return a.title==b.title
			def leq(x,y): return x[0].title<=y[0].title
			classes = cl.cluster(equiv)
			sort(classes,leq)
			for c in classes:
				sort(c,lambda x,y: string.lower(x.str())<=string.lower(y.str()))
				print '- '+c[0].title+' - '
				for x in c: x.display(8)
		return r

_prependDB = {}

class CacheList(List,Cache.Cache):
	def __init__(self,UFL,wrap=1,alwaysRefresh=0):
		self.UCL      = UFL
		self.type     = 'list'
		self._UFL     = UniversalAccess.UniversalFile(UFL)
		self._caches  = []
		self._ok      = 0
		self._wrap  = wrap
		self._refresh = alwaysRefresh
		self._lines   = []
		self._URL     = os.path.dirname(self.UCL)
		self._init    = 0
#-- List	
	def __len__(self): return len(self._caches)
	def __getitem__(self,i): return self._caches[i]
	def append(self,cache): self._caches.append(cache)
	def pop(self,i): return self._caches.pop(i)

	def display(self,indent=0):
		if hasattr(self,'._name'): print indent*' '+self._name
		else:                      print indent*' '+Registry.registry.short(self.UCL)

		r = Trust.trust.add(self.UCL)
		if r.ok(): r = self.init()
		if r.ok(): r = allReason(self._caches,lambda cache: Trust.trust.add(cache.UCL,1))

		if not r.ok(): 
			print (indent+4)*' '+`r`
		else:
			for cache in self: cache.display(indent+4)

	def listname(self,line):
		line2 = string.split(line,'#')[0]
		l = string.split(line2,'=>')
		if 0 and contains('=>',line2) and len(l)>=2:
			name  = string.strip(l[0])
			line2 = string.strip(l[1])
		else:
			name = line2
		name  = string.strip(name)
		line2 = string.strip(line2)
		return name,line2

	def init(self):
		r = Reason()
		if not self._init:
			r = Reason("Can't access ["+`self`+"].",not self._UFL.access())
			if r.ok() and not self._ok or self._refresh:
				r,self._lines = self._UFL.getLines()
				self._caches = []
				if r.ok():
					for line in self._lines:
						if len(line)>0 and line[-1]=='\n': line = line[:-1]
						if not (len(line)==0 or string.strip(line)=='' or line[0]=='#'):
							name,line = self.listname(line)
							if not line=='trusted.caches':
								if RelPath.relPath(line): line2 = os.path.join(self._URL,line)
								else:                     line2 = line
								cache = UniversalCache(line2)
								cache._name = name
								self._caches.append(cache)
					self._ok   = 1
					self._init = 1
				else:
					r = Reason("Can't find cache ["+`self`+"].")
		return r

	def refresh(self): 
		self._ok = 0
		return self.init()
		
	def getAll (self,spec,used): return self.getAllBase(spec,used,'quit')
	def getAllL(self,spec,used): return self.getAllBase(spec,used,'cont')
	
	def contents(self,used):
		r,ps = Trust.trust.add(self.UCL),[]
		if r.ok(): r = self.init()
		if r.ok(): r = allReason(self._caches,lambda cache: Trust.trust.add(cache.UCL,1))
		if r.ok():
			for cache in self:
				r2,ps2 = cache.contents(used)
				r.append(r2)
				if r2.ok(): ps.extend(ps2)
		if r.ok(): ps   = self.prependTop(ps)
		if r.ok(): r,ps = self.prepend   (ps)
		return r,ps
		
	def getAllBase(self,spec,used,mode='quit'):
		r,ps = Trust.trust.add(self.UCL),[]
		if r.ok(): r = self.init()
		if r.ok(): r = allReason(spec.caches,lambda cache: Trust.trust.add(cache,1))
		if r.ok(): r = allReason(self,lambda cache: Trust.trust.add(cache.UCL,1))
		if r.ok(): r,used = self.check(spec,used)
		if r.ok() and len(self)==0: r = Reason("Cache ["+self.UCL+"] is empty.")
		if r.ok():
			r = AllReason(); r.headline = "Can't find ["+spec.str()+"] in ["+self.UCL+"]:"
			for cache in self:
				spec2,used2 = copy.deepcopy(spec),used[:]
				if len(spec2.caches)==0: c0 = cache._name
				else:                    c0 = spec2.caches.pop(0)
				
				leq = leqCache(cache,c0)
				if not leq and cache.type=='mirror' and UniversalCache(c0).type=='mirror': 
					leq = meqSpec(cache,c0,spec2)

				if leq: rr,qs = cache.getAll(spec2,used2)
				else:   rr,qs = cache.getAll(spec ,used2)
					
				for q in qs:
					if len(q._spec.caches)==0 or not Registry.registry.equiv(q._spec.caches[0],c0):
						if leq: q._spec.caches.insert(0,c0)
					ps.append(q)
				r.append(rr)
				if rr.ok() and contains(mode,'quit'): r = rr; break
		if r.ok(): ps   = self.prependTop(ps)
		if r.ok(): r,ps = self.prepend   (ps)
		return r,ps

	def put(self,package): return existsReason(self,lambda cache: cache.put(package))
