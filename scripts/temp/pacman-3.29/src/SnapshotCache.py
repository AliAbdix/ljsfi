#
#	Copyright 2004, Saul Youssef
#
from Base        import *
from Environment import *
import Trust,UniversalAccess,Cache,Package,Execution,Registry

_packagesdb = {}

class SnapshotCache(Cache.Cache):
	def __init__(self,cache):
		self.UCL     = cache
		self.type    = 'snapshot'
		self._access,self._filename = UniversalAccess.UniversalAccess(os.path.dirname(self.UCL)),os.path.basename(self.UCL)
		if os.path.exists(os.path.join(pac_anchor,pacmanDir,'snapshots',fileify(Registry.registry.trans(self.UCL)))):
			try:
				f = open (os.path.join(pac_anchor,pacmanDir,'snapshots',fileify(Registry.registry.trans(self.UCL))),'r')
				lines = f.readlines()
				f.close()
				self._identity          = string.strip(lines[0][:-1])
				self._snapUCL           = string.strip(lines[1][:-1])
				self._snapTime          = string.strip(lines[2][:-1])
				self._snapUsername      = string.strip(lines[3][:-1])
				self._snapInstallation  = string.strip(lines[4][:-1])
				self._snapPlatform      = string.strip(lines[5][:-1])
				self._snapPacVersion    = string.strip(lines[6][:-1])
				
				packagesPath = os.path.join(pac_anchor,pacmanDir,'snapshots',self._identity,'packages')
				if _packagesdb.has_key(packagesPath):
					self._packages = _packagesdb[packagesPath]
				else:
					f = open(packagesPath,'r')
					self._packages = cPickle.load(f)
					f.close()
					_packagesdb[packagesPath] = self._packages
				
				self._loaded = 1
			except (IOError,OSError,IndexError):
				abort("Snapshot ["+self.UCL+"] has been damaged.")
		else:
			self._identity         = ''
			self._snapUCL          = ''
			self._snapTime         = ''
			self._snapUsername     = ''
			self._snapInstalation  = ''
			self._snapPlaform      = ''
			self._root             = ''
			self._packages         = []
			self._loaded = 0
			
	def display(self,indent=0):
		self.load().require()
		if verbo('snap'):
			print indent*' '+'                               Original cache: '+self._snapUCL
			print indent*' '+'                             Time of creation: '+self._snapTime
			print indent*' '+'                User who created the snapshot: '+self._snapUsername
			print indent*' '+'                   Snapshot creation platform: '+self._snapPlatform
			print indent*' '+'            Location of the snapshot creation: '+self._snapInstallation
			print indent*' '+'                     Made with Pacman version: '+self._snapPacVersion
		print indent*' '+`self`
		used = []
#		r,ps = self.getAll(Package.Spec(''),used)
		r,ps = self.contents(used)
		def le(p,q): return p._spec.name<=q._spec.name
		sort(ps,le)
		for p in ps: p.display(indent+4)
#		for p in ps: p.display(indent)

	def load(self):
		r = Reason()
		if not self._loaded:
			targetdir = os.path.join(pac_anchor,pacmanDir,'snapshots')
			if verbo('snap') or verbo('cache') or verbo('down'): print 'Loading snapshot ['+self.UCL+']...'
			r = self._access.getFile(self._filename,os.path.join(targetdir,self._filename))
			if not r.ok(): r = Reason('Snapshot ['+self.UCL+'] is not accessible.')
			if '@@' in self.UCL: r = Reason('['+self.UCL+'] contains an @@ macro.  Cannot make a snapshot.')
			if r.ok():
				r,root = parseTar(os.path.join(targetdir,self._filename))
				self._root = root
#				if r.ok(): r = Execution.execute('cd '+targetdir+'; tar xf '+self._filename)
				if r.ok(): r = Execution.execute('cd '+targetdir+'; '+gnuTarName()+' xf '+self._filename)
				if r.ok(): r = Execution.execute('cd '+targetdir+'; rm -f  '+self._filename)
				if r.ok():
					try:
						f = open(os.path.join(targetdir,self._root,'identity'),'r')
						lines = f.readlines()
						f.close()
						self._identity          = string.strip(lines[0][:-1])
						self._snapUCL           = string.strip(lines[1][:-1])
						self._snapTime          = string.strip(lines[2][:-1])
						self._snapUsername      = string.strip(lines[3][:-1])
						self._snapInstallation  = string.strip(lines[4][:-1])
						self._snapPlatform      = string.strip(lines[5][:-1])
						self._snapPacVersion    = string.strip(lines[6][:-1])
				
						f = open(os.path.join(targetdir,self._root,'packages'),'r')
						self._packages = cPickle.load(f)
						f.close()
						
						self._loaded = 1
						f = open(os.path.join(pac_anchor,pacmanDir,'snapshots',fileify(Registry.registry.trans(self.UCL))),'w')
						f.write(self._identity          +'\n')
						f.write(self._snapUCL           +'\n')
						f.write(self._snapTime          +'\n')
						f.write(self._snapUsername      +'\n')
						f.write(self._snapInstallation  +'\n')
						f.write(self._snapPlatform      +'\n')
						f.write(self._snapPacVersion    +'\n')
						f.close()
					except (IOError,OSError,IndexError):
						r = Reason("Error reading snapshot ["+self.UCL+"] identity.")
		return r
			
	def contents(self,used):
		r,ps = self.getAll(Package.Spec('*'),[])
		for i in range(len(ps)): ps[i]._spec.caches.insert(0,self.UCL)
		return r,ps

	def getAll(self,spec,used):
		r,ps = Trust.trust.add(self.UCL),[]
		if r.ok(): self.load()
		if r.ok(): self.check(spec,used)
		if r.ok() and len(self._packages)==0: r = Reason("Cache ["+self.UCL+"] is empty.")
		if r.ok():
			if spec==Package.Spec('*'):
				for p in self._packages: ps.append(p)
			else:
				for p in self._packages:
					if spec.satisfiedBy(p): 
						p._inCache = self.UCL
						p._spec.caches = spec.caches[:]
						Package.reduceCaches(p._environ,p._spec.caches)
						ps.append(p)
		if len(ps)==0: r = Reason("Can't find ["+spec.str()+"] in ["+self.UCL+"].")
		if len(ps)>0 and not switch('l') and not switch('lc') and not switch('update') and not switch('update-check'):
			verbo.log('cache','Package ['+ps[0]._spec.str()+'] found in ['+`self`+']...')
		return r,ps
