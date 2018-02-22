#
#	Copyright 2004, Saul Youssef
#
from Base        import *
from Abort       import *
from Environment import * 
import UniversalAccess,Cache,Package,Source,Message,Trust,Registry

class SourceCache(Cache.Cache):
	def __init__(self,cache):
		self.UCL     = cache
		self.type    = 'source'
		self._access = UniversalAccess.UniversalAccess(self.UCL,'source')
			
	def filenames(self,spec):
		packageFilenames = []
		r,filenames = self._access.namesPath(spec.subdirectory)
		qlock,lock = 0,''
		
		if r.ok():
			for filename in filenames:
				if spec.filenameEqu(filename): packageFilenames.append(os.path.join(spec.subdirectory,filename))
				if filename=='lock' and not (switch('lock-override') or allow('lock-override') or 'lock-override' in switchItems('allow')):
					qlock = 1
					ac = UniversalAccess.UniversalAccess(os.path.join(self.UCL,spec.subdirectory))
					rr,lines = ac.getLines('lock')
					if rr.ok() and len(lines)>0 and len(lines[0])>1: lock = lines[0][:-1]
			packageFilenames.reverse()
		return r,packageFilenames,qlock,lock
		
	def packageSource(self,spec,path,source):
		tspec = copy.deepcopy(spec)
		try:
			r,environ,name = Source.SourceFile(source,tspec,self.UCL,os.path.basename(path)).compN()
		except AbortException,message:
			r,environ,name = Reason(message.value),OR(),spec.name
		spec2 = copy.deepcopy(spec)
		spec2.name = name
		spec2.subdirectory,spec2.file = os.path.split(path)
		p = Package.Package(spec2,self.UCL,spec.locate(environ))
		return r,p
	
	def contents(self,used):
		r,ps = self.getAll(Package.Spec(),[])
		if r.ok(): ps   = self.prependTop(ps)
		if r.ok(): r,ps = self.prepend   (ps)
		return r,ps
		
	def getAll(self,spec,used):
		r,ps = Reason(),[]
		if   len(spec.caches)==0: 
			pass
		elif len(spec.caches)==1: 
			if not Registry.registry.equiv(spec.caches[0],self.UCL):
				r = Reason("Package ["+spec.str()+"] not found in ["+Registry.registry.short(self.UCL)+"].")
		else:
			r = Reason("Package ["+spec.str()+"] not found in ["+Registry.registry.short(self.UCL)+"].")
		if r.ok(): r = Trust.trust.add(self.UCL)
		if r.ok(): r,used = self.check(spec,used)
		
		if r.ok():
			r,filenames,qlock,lock = self.filenames(spec)

			if qlock:
				if string.strip(lock)=='': r = Reason("Cache ["+`self`+"] has been locked by it's owner.")
				else:                      r = Reason('Cache ['+`self`+"] has been locked by it's owner with message ["+lock+"].")
						
			if r.ok():
				for filename in filenames:
					verbo.log('src','About to open source file ['+filename+']...')
					r,source = self._access.getLines(filename)
				
					if r.ok():
						r,p = self.packageSource(spec,filename,source)
						if not r.ok(): 
							if verbo('src'):
								verbo.log('src','Source code in ['+filename+'] from cache ['+`self`+'] has a compilation error.')
								verbo.log('src',`r`)
							else:
								print 'Compilation error in ['+filename+'] in cache ['+`self`+']...'
								print r
								print 'syntax error> '+filename+' from cache '+`self`
								for line in source:
									print 'syntax error> '+line[:-1]
							p._environ = AND(Message.Fail(`r`))
							p._spec.name = filename[:-7]
						p._sourceCode = source[:]
						p._inCache     = self.UCL
						p._sourceCache = self.UCL
						verbo.log('src','File ['+filename+'] contains ['+p._spec.name+']...')
						if verbo('src'):
							if spec.satisfiedBy(p): verbo.log('src','Package ['+p._spec.name+'] satisfies ['+spec.str()+']...')
							else:                   verbo.log('src','Package ['+p._spec.name+'] does not satisfy ['+spec.str()+']...')
						if spec==Package.Spec() or (r.ok() and spec.satisfiedBy(p)): ps.append(p)
					else:
						r = Reason("Can't access ["+filename+"] in cache ["+`self`+"].")	
			
			if r.ok() and len(ps)==0: 
				if string.strip(spec.str())=='':
					r = Reason("Can't find any .pacman source files in ["+`self`+"].")
				else:
					r = Reason("Can't find ["+spec.str()+"] in ["+`self`+"].")
			if len(ps)>0 and not switch('l') and not switch('lc') and not switch('update') and not switch('update-check') and not spec==Package.Spec(): 
				verbo.log('cache','Package ['+ps[0]._spec.str()+'] found in ['+Registry.registry.short(self.UCL)+']...')
				if verbo('cache-brief'): flicker('  '+ps[0]._spec.name+' found in '+Registry.registry.short(self.UCL)+'...')
		if r.ok(): ps   = self.prependTop(ps)
		if r.ok(): r,ps = self.prepend   (ps)
		return r,ps
