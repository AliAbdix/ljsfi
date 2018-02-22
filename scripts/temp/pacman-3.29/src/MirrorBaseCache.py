	
from Base import *
import Execution,Cache,UniversalAccess,UniversalCache,Environment,Trust,Package,Registry,Download,RelPath
import time,cPickle,string,os,copy

def mirrorDownloadReplace(accessString,e):
	r = Reason()
	
	if    e.type=='package':
		E = copy.deepcopy(e)
		E._environ = mirrorDownloadReplace(accessString,e._environ)
	elif  e.type=='AND':
		E = Environment.AND()
		for ee in e: E.append(mirrorDownloadReplace(accessString,ee))
	elif  e.type=='OR':
		E = Environment.OR()
		for ee in e: E.append(mirrorDownloadReplace(accessString,ee))
	elif  e.type=='download':
#		downloadIdentity = 'o'+`hash(e._url)`
		downloadIdentity = 'o..'+phash(e._url)
		E = copy.deepcopy(e)
		E._url = os.path.join(accessString,downloadIdentity,os.path.basename(e._url))
		if debug('mirror-download'): print E
	elif  e.type=='downloadUntarzip':
#		downloadIdentity = 'o'+`hash(e._download._url)`
		downloadIdentity = 'o..'+phash(e._download._url)
		E = copy.deepcopy(e)
		E._download._url = os.path.join(accessString,downloadIdentity,os.path.basename(e._download._url))
		if debug('mirror-download'): print E
	else:
		E = e
	return copy.deepcopy(E)

_downloads = {}

def mirrorDownload(location,e):
	r = Reason()
	if    e.type == 'package':
		r,environ = mirrorDownload(location,e._environ)
		E = copy.deepcopy(e)
		E._environ = copy.deepcopy(environ)
	elif  e.type== 'AND':
		r,E = Reason(),Environment.AND()
		for ee in e:
			r,ee2 = mirrorDownload(location,ee)
			if r.ok(): E.append(ee2)
			else: break
	elif  e.type=='OR':
		r,E = Reason(),Environment.OR()
		for ee in e:
			r,ee2 = mirrorDownload(location,ee)
			if r.ok(): E.append(ee2)
			else: break
	elif  e.type=='download':
#		downloadIdentity = 'o'+`hash(e._url)`
		if '@@' in e._url: r = Reason('['+e._url+"] contains an @@ macro. Can't mirror/pacball/snapshot")
		downloadIdentity = 'o..'+phash(e._url)
		downdir = os.path.join(location,downloadIdentity)
		if r.ok() and not _downloads.has_key(downdir):
			r = Execution.execute('rm -r -f '+downdir+'; mkdir '+downdir)
			if r.ok():
				cwd = os.getcwd()
				down = copy.deepcopy(e)
				if RelPath.relPath(down._url): down._url = os.path.abspath(down._url) # for paths with ".." in them
				os.chdir(downdir)
				verbo.log('mirror','Adding ['+e._url+'] to mirror cache...')
				r = down.satisfy()
				if r.ok(): _downloads[downdir] = ''
				os.chdir(cwd)
		E = copy.deepcopy(e)
		E._url = os.path.join(location,downloadIdentity,os.path.basename(e._url))
	elif e.type=='downloadUntarzip':
#		downloadIdentity = 'o'+`hash(e._download._url)`
		if '@@' in e._download._url: r = Reason('['+e._download._url+"] contains an @@ macro.  Can't mirror/pacball/snapshot")
		downloadIdentity = 'o..'+phash(e._download._url)
		downdir = os.path.join(location,downloadIdentity)
		if not _downloads.has_key(downdir):
			downdir = os.path.join(location,downloadIdentity)
			r = Execution.execute('rm -r -f '+downdir+'; mkdir '+downdir)
			if r.ok():
				cwd = os.getcwd()
				down = copy.deepcopy(e._download)
				if RelPath.relPath(down._url): down._url = os.path.abspath(down._url) # for paths with ".." in them
				os.chdir(downdir)
 				verbo.log('mirror','Adding ['+e._download._url+'] to mirror cache...')
				r = down.satisfy()
				if r.ok(): _downloads[downdir] = ''
				os.chdir(cwd)
		E = copy.deepcopy(e)
		E._download._url = os.path.join(location,downloadIdentity,os.path.basename(e._download._url))
	else:
		r,E = Reason(),e
	return r,E	

class MirrorBaseCache(Cache.Cache):
	def __init__(self,cache,mirror=''):
		self.type        = 'basemirror'
		self._access     = UniversalAccess.UniversalAccess(cache)
		self.UCL         = `self._access`
		self._init       = 0
		self._location   = ''
		if self._access.accessor.type=='local directory': self._location = `self._access`
		self._mirror  = mirror
		self._packages   = {}
		self._updates    = {}
		self._name = self.UCL[:]

	def str(self): return Registry.registry.short(self.UCL)
	def display(self,indent=0):
		Cache.Cache.display(self,indent)
		if verbo('up'):
			if len(self._updates)>0:
				print (indent+4)*' '+'=> Updates of ['+Registry.registry.short(self._mirror)+'] are available:'
				qs = []
				for idd,p in self._updates.items(): qs.append(p)
				sort(qs,Cache.plle)
				for q in qs: q.display(indent+8)

	def display2(self,indent=0):
		r,ps = self.contents([])
		if not r.ok():
			print (indent+4)*' '+`r`
		else:
			sort(ps,Cache.plle)
			for p in ps: p.display(indent+4)
		if verbo('up'):
			if len(self._updates)>0:
				print (indent+4)*' '+'=> Updates of ['+Registry.registry.short(self._mirror)+'] are available:'
				qs = []
				for idd,p in self._updates.items(): qs.append(p)
				sort(qs,Cache.plle)
				for q in qs: q.display(indent+8)		

	def init(self):
		r = Reason()
		if not self._init:
			r = self._access.lockCheck()
			if r.ok():
				r,tup = self._access.getObj('o..basemirror..o')
				if r.ok():
					if len(tup)>3:
						self._mirror        = tup[0]
						self._packages      = tup[1]
						self._updates       = tup[2]
						self._name          = tup[3]
						self._init = 1
					else:
						r = Reason('Mirror ['+self.str()+'] is unreadable.')
		return r
				
	def save(self):
		r = Reason()
		if not self._location=='' and self._init:
			try:
				removeFile(os.path.join(self._location,'o..basemirror..o'))
				f = open(os.path.join(self._location,'o..basemirror..o'),'w')
				tup = (self._mirror,self._packages,self._updates,self._name,)
				cPickle.dump(tup,f)
				f.close()
			except (IOError,OSError):
				r = Reason("Failure attempting to save ["+self.str()+"].")
		else:
			r = Reason("Can't save ["+self.str()+"].")
		return r
		
	def getUpdates(self): 
		updates = []
		for idd,p in self._updates.items(): updates.append(p)
		return updates
		
	def readme(self):
		r = Reason()
		try:
			f = open(os.path.join(self._location,'README'),'w')
			f.write('#\n')
			f.write('#  DO NOT MODIFY THE CONTENTS OF THIS DIRECTORY\n')
			f.write('#      - This is a Pacman mirror cache    - \n')
			f.write('#      - Created and Modified by Pacman   - \n')
			f.write('#      - see http://physics.bu.edu/pacman - \n')
			f.write('#\n')
			f.close()
		except (IOError,OSError):
			r = Reason("Can't write to ["+self._location+"].")
		return r

	def create(self):
		r = Reason("Can't create ["+self.str()+"] from a remote location.",self._location=='')
		if r.ok(): r = Reason("Mirror cache ["+self.str()+"] has not been assigned a cache to mirror.",self._mirror=='')
#		if r.ok(): r = Reason("["+self._location+"] already exists.",os.path.exists(self._location))
		if r.ok(): r = Execution.execute('rm -r -f '+self._location+'; mkdir '+self._location)
		if r.ok(): r = self.readme()
		if r.ok(): 
			self._packages      = {}
			self._updates       = {}
			self._init = 1
			r = self.update()
		if r.ok(): r = self.save()
		return r
		
	def isUpdate(self,u):
		uname,uid = u._spec.name,u._id()
		up = 1
		
		if not switch('snap') and not switch('snapshot'): verbo.log('up','Checking ['+u.str()+'] for an update...')
		qs = self._packages.get(self.pid(u._spec),[])
		if exists(qs,lambda q: q.upEqual(q._source,u._source)): up = 0
		else: 
			already = exists(qs,lambda q: Cache.plle(u,q) and Cache.plle(q,u))
			if already: verbo.log('up','=> Update of package ['+u.str()+'] found...')
		return up

	def updateCheck(self):
		r = self.init()
		if r.ok():
			self._updates = {}
			r,ps = UniversalCache.UniversalCache(self._mirror).contents([])
			if r.ok():
				for p in ps:
					if p.lastsat or p.lastfail: 
						r = Reason("Package ["+p._spec.str()+"] is installed.  Can't update from an installed package.")
						break
					if self.isUpdate(p):
#						p._parents,p._modifiers = [],[]
						self._updates[p._spec._id()] = p
		if r.ok(): r = self.save()
		return r

	def update(self):
		r = self.init()
		if r.ok(): r = self.local()
		if r.ok(): self._updateTime = time.time()
		if r.ok(): r = self.updateCheck  ()
		if r.ok(): r = self.updateResolve()
		if r.ok(): r = self.updateTrans  ()
		if r.ok(): self._updates = {}
		if r.ok(): r = self.save()
		return r
		
	def local(self):
		r = self.init()
		if r.ok(): 
			if self._location=='': r = Reason("Cache ["+self.str()+"] is not in the local file system.")
		return r
		
#	def pid(self,spec): return 'o'+`hash(spec.subdirectory+'$$'+spec.name)`
	def pid(self,spec): return 'o..'+phash(spec.subdirectory+'$$'+spec.name)
		
	def updateResolve(self):
		r = self.local()
		if r.ok(): r = Execution.execute('rm -r -f '+os.path.join(self._location,'o..tmp..o'))
		if r.ok(): r = Execution.execute('mkdir '+   os.path.join(self._location,'o..tmp..o'))
		if r.ok():
			keys = self._updates.keys()
			for key in keys:
				p = self._updates[key]
				r,e = mirrorDownload(os.path.join(self._location,'o..tmp..o'),p)
				if r.ok():
					ps = self._packages.get(self.pid(p._spec),[])
					qs = []; already = 0
					for pp in ps:
						if p._id()==pp._id(): 
							already = 1; qs.append(p)
						else:
							qs.append(pp)
					if already:
						verbo.log('up','Updating ['+p.str()+']...')
					else:
						if switch('snap') or switch('snapshot'): verbo.log('up','Snapshotting ['+p.str()+']...')
						else:                                    verbo.log('up','Mirroring ['+p.str()+']...')
						qs.append(p)
					
					sort(qs,Cache.plle)
					self._packages[self.pid(p._spec)] = qs[:]
					del self._updates[key]	
				else:
					break
		if r.ok(): r = self.save()
		return r
		
	def updateTrans(self):
		r = self.local()
		if r.ok():
			try:
				filenames = os.listdir(os.path.join(self._location,'o..tmp..o'))
			except (IOError,OSError):
				r = Reason("Can't access ["+os.path.join(self._location,'o..tmp..o')+"].")
			if r.ok():
				for fn in filenames:
					Execution.execute('rm -r -f '+os.path.join(self._location,fn)).require()
					Execution.execute('mv '+os.path.join(self._location,'o..tmp..o',fn)+' '+ \
					                        os.path.join(self._location,            fn)).require()
				r = Execution.execute('rm -r -f '+os.path.join(self._location,'o..tmp..o'))
		return r					
							
	def contents(self,used):
		r,ps = self.init(),[]
		skipreplace = (switch('l') or switch('lc')) and not displayMode('cmp')
		if r.ok(): 
			for idd,qs in self._packages.items(): 
				for q in qs:
					if skipreplace: qD = q
					else:           qD = mirrorDownloadReplace(`self._access`,q)
					ps.append(qD)
			sort(ps,Cache.plle)
		if r.ok(): ps   = self.prependTop(ps)
		if r.ok(): r,ps = self.prepend(ps)
		for i in range(len(ps)): 
			ps[i].setParent()
			ps[i]._parents   = []
			ps[i]._modifiers = []
		return r,ps

	def getAll(self,spec,used):
		r,ps = self.init(),[]
		skipreplace = (switch('l') or switch('lc')) and not displayMode('cmp')
		if r.ok(): self.check(spec,used)
		if r.ok() and len(self._packages)==0: r = Reason("Cache ["+self.UCL+"] is empty.")
		if r.ok():
			if spec==Package.Spec():
				r,ps = self.contents([])
			else:
				qs = self._packages.get(self.pid(spec),[])
				qs.reverse()
				for p in qs:
					if spec.satisfiedBy(p):
						p._inCache = self.UCL
						if skipreplace: pD = p
						else:           pD = mirrorDownloadReplace(`self._access`,p)
						ps.append(pD)
						break
		if r.ok(): ps   = self.prependTop(ps)
		if r.ok(): r,ps = self.prepend(ps)
		for i in range(len(ps)): 
			ps[i].setParent()
			ps[i]._parents   = []
			ps[i]._modifiers = []
		return r,ps
