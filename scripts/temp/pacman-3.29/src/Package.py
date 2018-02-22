#
#	Copyright, 2005, Saul Youssef
#
from Base        import *
from Environment import *
import Cache,Source,CD,CWD,Directory,UniversalCache,EnvironmentVariable,Registry,RelPath,Platform
import os,copy,string,time

def reduceCaches(E,caches):
	if E.type=='AND':
		for e in E: reduceCaches(e,caches)
	elif E.type=='OR':
		for e in E: reduceCaches(e,caches)
	elif E.type=='lazy package':
		if sublistEQ(caches,E._spec.caches,lambda c1,c2: Registry.registry.equiv(c1,c2)):
			E._spec.caches = caches[:]
			
def equivCachesSpec(specCache,cDB,c):
	eq = Registry.registry.equiv(specCache,c)
	if not eq:
		specType,r,specMirror,specTime,specSnap = UniversalCache.getTypeMirrorTimeSnapshot(specCache)
		ucl = UniversalCache.UniversalCache(c).UCL
		if r.ok() and specType=='mirror' and specSnap and cDB.has_key(ucl):
			cMirror,cTime,cSnap = cDB[ucl]
			if cSnap and Registry.registry.equiv(cMirror,specMirror) and cTime==specTime:
				eq = 1
	return eq
	
def clred(cl):
	cs = []
	for c in cl:
		if not tail(c,'.caches'): cs.append(c)
	return cs

def satisfiedByCaches(caches,db,pcaches):
	ok = 1
	c2 = caches[:]; p2 = pcaches[:]
	if len(caches)>0:
		if len(pcaches)>0:
			ok = equivCachesSpec(caches[0],db,pcaches[0])
			pmir = UniversalCache.UniversalCache(caches[0]).type=='mirror'
			if ok:
				caches. pop(0)
				pcaches.pop(0)
				ok = satisfiedByCaches(caches,db,pcaches)
			elif pmir:
				pcaches.pop(0)
				ok = satisfiedByCaches(caches,db,pcaches)
			else:
				ok = 0
		else:
			ok = 0
	return ok
		
def specParse(text):
	caches = []
	front,back = specSplit(text)
	while not back=='':
		caches.append(front)
		front,back = specSplit(back)
	
	if not '|' in front:
		prefix = front; guardstring = ''
	else:
		prefix      = string.strip(front[:string.find(front,'|')   ])
		guardstring = string.strip(front[ string.find(front,'|')+1:])
		
	subdirectory,name = os.path.split(prefix)
	return caches,name,subdirectory,guardstring
	
def sshtest(text):
	ssh = 0
	l = string.split(text,':')
	if len(l)>0 and '@' in l[0] and text.count(':')>1: ssh = 1
	return ssh
		
def specSplit(text):
	front = ''; back = text
	while 1:
		if     len(back)==0: 
			break
		elif  back[:5]=='http:': 
			front = front + back[:5]
			back  =         back[5:]
		elif  back[:6]=='https:':
			front = front + back[:6]
			back  =         back[6:]
		elif  back[:4]=='ftp:':
			front = front + back[:4]
			back  =         back[4:]
		elif  back[:7] =='gsiftp:':
			front = front + back[:7]
			back  =         back[7:]
		elif  sshtest(back):
			i = back.find(':')
			if i>0:
				front = front + back[:i] + ':'
				back  =         back[i+1:]
			i = back.find(':')
			if i>0:
				front = front + back[:i]
				back  =         back[i:]
		elif  back[0]==':':
			back = back[1:]
			break
		else:
			front = front + back[:1]
			back  =         back[1:]
	return front,back

def cacheMatch(specs,cs):
	if   len(specs)==0: m = 1
	elif len(cs   )==0: m = 0
	else:
		if UniversalCache.equivalentCaches(specs[0],cs[0]):
			specs.pop(0); cs.pop(0)
			m = cacheMatch(specs,cs)
		else:
			cs.pop(0)
			m = cacheMatch(specs,cs)
	return m


# The getPackageRevision and getPackageRevisionHelper functions were added by
# Scot Kronenfeld 2/2009.  They are used to implement the packageRevision atom

# Look through all the atoms and find packageRevision atoms with matching architectures
def getPackageRevision(atoms):
        matchingOSes = Platform.equivalentOSes()
        return getPackageRevisionHelper(atoms, matchingOSes)[0]

# Recursive function to find the first packgeRevision atom
# match - the current packageRevision atom we have found
# level - The 'level' of the match.
#         1 is a specific match
#         2 and 3 are left for future use with half wildcards
#         4 is a full wildcard match (*, *)
def getPackageRevisionHelper(atoms, OSes):
        match = None
        level = None
        for atom in atoms:
                if atom.type == 'AND' or atom.type == 'OR':
                        # Process the atoms inside the AND or OR statement, and update our current match
                        # if it is more specific than the current match
                        (submatch, sublevel) = getPackageRevisionHelper(atom, OSes)
                        if submatch != None and sublevel != None:
                                if sublevel == 1: return [submatch, sublevel]
                                elif level == None or sublevel < level:
                                        match = submatch
                                        level = sublevel
                elif atom.type == 'packageRevision':
                        if atom.os == '*' or OSes.get(atom.os, None):
                                if atom.arch == '*' or atom.arch == Platform.thisArch():
                                        # At this point, we have a match.  Check if it is specific or a wildcard
                                        if atom.os == '*' and atom.arch == '*':
                                                # If we get the wildcard match '*', then keep looking through
                                                # all the atoms to try to find a more specific match
                                                match = atom
                                                level = 4
                                        elif atom.os == '*' or atom.arch == '*':
                                                # This is currently not possible.  packageRevision.py will
                                                # cause a syntax error for this condition
                                                # If this is ever allowed, levels 2 and 3 can be used here
                                                abort("Syntax error: OS and Arch must both be '*' or neither can be '*'")
                                        else:
                                                # Specific match for this platform, stop looking
                                                return [atom, 1]
        return [match, level]

# The updateLog function was added by Scot Kronenfeld 2/2009
# Add things to the update log
# If "-v up" was specified, print them to the screen
def updateLog(verbosity, msg):
        if verbo(verbosity): print msg
        if not os.path.exists(os.path.join(pac_anchor,pacmanDir,'logs','update.log')):
                verbo.log('io','Creating update.log...')
                try:
                        f = open(os.path.join(pac_anchor,pacmanDir,'logs','update.log'),'w')
                        f.write('- Update information log\n')
                        f.close()
                except:
                        return
        try:
                f = open(os.path.join(pac_anchor,pacmanDir,'logs','update.log'),'a')
                if verbo('io'): print 'Writing to update.log...'
                f.write(time.strftime("%Y/%m/%d %H:%M:%S") + " - " + msg + '\n')
                f.close()
        except (IOError,OSError):
                return
        return
        
class Spec(PreOrder,HtmlOut):
	def __init__(self,specstring='',location=''):
		self.specstring,self.location = specstring,location
		self.caches,self.name,self.subdirectory,self.guard = specParse(specstring)
		self.location = location
		self.lazyOK = 1
		self.file = ''
		if tail(self.name,'.pacman'):
			self.file = self.name
			self.name = '' # self.name[:-7]
		if specstring=='.': self.name,self.cacheName = '','.'
		self.mayBeModifiedBy = ['']
		self._mirrors = {}
			
	def _id (self): return `clred(self.caches),self.name,self.subdirectory,self.file`
	def __eq__(self,x):  return self.name==x.name and self.file==x.file and \
			self.subdirectory==x.subdirectory and clred(self.caches)==clred(x.caches) and self.location==x.location
			
	def strip(self,c):
		spec = copy.deepcopy(self)
		while len(spec.caches)>0 and Registry.registry.equiv(spec.caches[0],c): spec.caches.pop(0)
		return spec
	def equalUp(self,x): return self._equalUp(self.strip(pac_anchor),x.strip(pac_anchor))
	def _equalUp(self,spec1,spec2):
		eq = spec1.name==spec2.name and spec1.file==spec2.file and spec1.subdirectory==spec2.subdirectory and spec1.location==spec2.location and len(spec1.caches)==len(spec2.caches)
		if eq:
			for i in range(len(spec1.caches)):
				c1,c2 = spec1.caches[i],spec2.caches[i]
				eq = c1==c2 or (tail(c1,'.caches') and tail(c2,'.caches'))
		return eq		
	def __le__(self,x):
		q = x.name=='*' or x.name=='' or x.name          ==  self.name
		if q: q = x.subdirectory==''  or x.subdirectory  ==  self.subdirectory
		if q: q = x.file==''          or x.file          ==  self.file
		return q
	def match(self,caches):
		cs2 = []
		for c in self.caches:
			if not tail(c,'.mirror'): cs2.append(c)
		caches2 = []
		for c in caches:
			if not tail(c,'.mirror'): caches2.append(c)
		return cacheMatch(cs2,caches2)
	def satisfiedBy (self,p): return self.satisfiedByR(p).ok()
	def satisfiedByR(self,p):
		r = Reason()
		specCaches = clred(self.caches[:])
		pCaches    = clred(p._spec.caches[:])
		if hasattr(p._spec,'_mirrors'): m = p._spec._mirrors
		else:                           m = {}
		if satisfiedByCaches(specCaches,m,pCaches):
			q = p._spec<=self
			if q:
				if not self.guard=='':
					r,guard = Source.Source(self.guard,Spec()).comp()
					if r.ok():
						if not p._environ.satisfies(guard):
							r = Reason("Package specification ["+self.str()+"] fails |... requirements of ["+p._spec.str()+"].")
			else:
				r = Reason("Package ["+p._spec.str()+"] does not satisfy ["+self.str()+"].")
		else:
			r = Reason("Package ["+p._spec.str()+"] does not match the cache specified by ["+self.str()+"].")
		if verbo('ptest') and not self.name=='' and not self.name=='*':
			if r.ok(): print "Package ["+p._spec.str()+"] satisfies ["+self.str()+"]."
			else:      print r
		return r
	def __repr__(self): return 'spec: '+self.str()
	def str(self): 
		s = ''
		for cache in self.caches:  s = s + Registry.registry.short(cache) + ':'
		if self.subdirectory !='': s = s + self.subdirectory + '/'
		s = s + self.name
		if self.guard        !='': s = s + ' | '+self.guard
		if self.location     !='': s = s + ' at '+self.location
		return s
	def filenameEqu(self,filename):
		if self.name=='*': 
			comp = 1
		else:
			fname = os.path.basename(filename)
			comp = 0
			if tail(fname,'.pacman'):
				if self.file =='': comp = self.name==fname[:len(self.name)]
				else:              comp = fname==self.file
		return comp
	def envEqu(self,e): return e.satisfies(Source.Source(self.guard).compile())
	def cachesPop(self):
		if self.caches==[]: abort("Error in Pacman.")
		cache = self.caches.pop(0)
		if len(self.caches)>0 and RelPath.relPath(self.caches[0]): 
			self.caches[0] = os.path.join(cache,self.caches[0])
		return cache
	def locate(self,e):
		if self.location=='': 
			e2 = AND(CWD.SetCWD('.'),EnvironmentVariable.SetenvTemp('PACMAN_INSTALLATION','.'))
			e2.extend(e)
			e2.append(CWD.SetCWD('.'))
		else:
			e2 = AND(Directory.Directory(self.location),CWD.SetCWD(self.location))
			e2.extend(e)
			e2.extend(CWD.SetCWD('.'))
		return e2
	def getAll(self,used=[]):
		r,ps = Reason(),[]
		if len(self.caches)==0: r = Reason("Can't find ["+self.str()+"].")
		if r.ok():
			spec = copy.deepcopy(self)
			c0 = spec.caches.pop(0)
			c = UniversalCache.UniversalCache(c0)
			r,qs = c.getAll(spec,used)
			ps = []
			for q in qs: ps.append(q)
		return r,ps
	def get(self):
		r,ps = self.getAll([])
		if r.ok() and len(ps)>0: return r,ps[0]
		else:                    return r,Package()
	def put(self,package):
		if len(self.caches)==0:
			r = Reason("Can't save ["+package.str()+"].")
		else:
			c = UniversalCache.UniversalCache(self.caches[0])
			r = c.put(package)
		return r
		
class Update:
	_updateChecked = 0
	_updated       = 0
	def updateCheck   (self): abort('missing updateCheck'           )
	def updateWaiting (self): abort('missing updateWaiting'         )
	def updateRemove  (self): abort('missing updateRemove'          )
	def update        (self): abort('missing update function.'      )

class Verify:
	def verify        (self): abort('missing verify function.'      )
	def repair        (self): abort('missing repair function.'      )
	
class Package(Environment,Update,Verify):
	type   = 'package'
	title  = 'Packages'
	action = 'install package'
	
	def __init__(self,spec=Spec(),cache='trust.caches',environ=OR()):
		self._spec        = spec
		self._inCache     = ''
		self._environ     = environ
		self._source      = AND()
		self._sourceCode  = []
		self._sourceCache = ''
		for e in environ: 
			ee = copy.deepcopy(e)
			self._source.append(ee)
		self._update           = OR()
		self._updateSourceCode = []
		
		self._lazy = 0
		self._parents   = []
		self._modifiers = []
		self.lastsat = 0
		self.lastfail= 0
		
		self._neutered = 0
		self._lastSatisfiable = Reason()
		
	def _id(self): return `self._spec.name,self._sourceCache,self._spec.subdirectory,self._spec.file`
	def setParent(self):
		self.setParentBase(self._environ)
		self.setParentBase(self._source )
	def setParentBase(self,e):
		if   e.type=='AND' or e.type=='OR':
			for i in range(len(e)): self.setParentBase(e[i])
		elif e.type=='lazy package':
			spec = Spec(self._spec.name)
			e._parent = copy.deepcopy(spec)
#-- Set
	def equal(self,p):                     return \
		self._spec        == p._spec      and \
		self._environ     == p._environ   and \
		self._source      == p._source 

        # The upEqual function has been modified by Scot Kronenfeld on 2/2009
        # The original upEqual code is now in upEqualHelper, a new function.
        # The purpose of upEqual is to determine if two version of a package are identical,
        # and if an update is necessary.  upEqual now has code to compare packageRevision
        # atoms.  If the packageRevision atoms are not present, or if they are not equal
        # the code "falls through" to the original upEqual code (in upEqualHelper)
	def upEqual(self,es1,es2):
                # Check packageRevision atoms to see if we do not want to update this package
                v1 = getPackageRevision(es1)
                v2 = getPackageRevision(es2)

                # Information logging
                if v1 or v2:
                        v1Rev = "Undefined"
                        v2Rev = "Undefined"
                        if v1: v1Rev = v1.getRevision()
                        if v2: v2Rev = v2.getRevision()
                        updateLog('up-check', "    Old Revision: " + v1Rev)
                        updateLog('up-check', "    New Revision: " + v2Rev)

                # If we got packageRevision atoms, and their revisions are
                # equal then we do not want to do an update on this package
                if v1 and v2 and v1.satisfies(v2):
                        updateLog('up-check', "    The revisions are equal, no update necessary.")
                        return 1

                # Call out to pacman's original way of determining if a package needs updating
                return self.upEqualHelper(es1, es2)

        # This is a recursive function to compare the contents of a pacman file and return
        # if they are the same (same atoms, same contents in each atom)
        def upEqualHelper(self, es1, es2):
		if len(es1)==len(es2):
			eq = 1
			for i in range(len(es1)):
				e1,e2 = es1[i],es2[i]
				if e1.type=='pacman source code' and e2.type=='pacman source code':
					pass
				else:
					if e1.type=='lazy package' and e2.type=='lazy package':
						eq = e1._spec.equalUp(e2._spec)
					elif e1.type=='OR' and e2.type=='OR':
						eq = self.upEqualHelper(e1,e2)
					elif e1.type=='AND' and e2.type=='AND':
						eq = self.upEqualHelper(e1,e2)
					else:
						eq = e1==e2
				if not eq: 
					if debug('up'): 
						print self
						print e1
						print e2
					break
		else:
			eq = 0
		return eq

#	def upEqual(self,es1,es2):
#		if len(es1)==len(es2):
#			eq = 1
#			for i in range(len(es1)):
#				e1,e2 = es1[i],es2[i]
#				if e1.type=='pacman source code' and e2.type=='pacman source code':
#					pass
#				else:
#					if e1.type=='lazy package' and e2.type=='lazy package':
#						eq = e1._spec.equalUp(e2._spec)
#					elif e1.type=='OR' and e2.type=='OR':
#						eq = self.upEqual(e1,e2)
#					elif e1.type=='AND' and e2.type=='AND':
#						eq = self.upEqual(e1,e2)
#					else:
#						eq = e1==e2
#				if not eq: 
#					if debug('up'): 
#						print self
#						print e1
#						print e2
#					break
#		else:
#			eq = 0
#		return eq
#	def upEqualOLD(self,es1,es2):
#		if len(es1)==len(es2):
#			eq = 1
#			for i in range(len(es1)):
#				e1,e2 = es1[i],es2[i]
#				if e1.type=='pacman source code' and e2.type=='pacman source code':
#					pass
#				else:
#					if e1.type=='lazy package' and e2.type=='lazy package':
#						eq = e1._spec.equalUp(e2._spec)
#					else:
#						eq = e1==e2
#				if not eq: 
#					if debug('up'): 
#						print self
#						print e1
#						print e2
#					break
#		else:
#			eq = 0
#		return eq
	def str(self): return self._spec.str()
	def location(self):
		if len(self._environ)>0 and self._environ[0].type=='setcwd':
			return self._environ[0].location
		else:
			return '.'
#-- Applies
	def status(self):
		if debug('status'):
			installed   = self.satisfied     ().ok()
			installable = self.satisfiable   ().ok()
			update      = self.updateWaiting ().ok()
			loc         = self.location()
		else:
			installed   = self.lastsat
			installable = installed or (self._lastSatisfiable.ok() and not self.lastfail)
			update      = self.updateWaiting().ok()
			loc         = self.location()
		return installable,installed,update,loc
	def getEs(self,typename):
		es = []
		def f(E):
			if E.type=='AND' or E.type=='OR':
				for e in E: f(e)
			elif E.type=='lazy package': 
				pass
			else:
				if E.type==typename: es.append(E)
		f(self._environ)
		return es
	def getLps(self):
		lps = []
		def f(E):
			if E.type=='AND' or E.type=='OR':
				for e in E: f(e)
			elif E.type=='lazy package':
				lps.append(E)
			else:
				pass
		f(self._environ)
		return lps
	def display(self,indent=0,tail=''): 
		installable,installed,update,loc = self.status()

		s = ''
		if         installed: s = s + '[*]'
		elif not installable: s = s + '[X]'
		else:                 s = s + '[ ]'
		t = ''
		if update: t = ' ==> UPDATE AVAILABLE '

		if not ( displayMode(  'revisions') or \
                         displayMode(        'req') or \
			 displayMode(         'up') or \
			 displayMode(         'in') or \
			 displayMode(     'subdir') or \
			 displayMode(        'src') or \
			 displayMode(       'file') or \
			 displayMode(        'loc') or \
			 displayMode(     'mirror') or \
			 displayMode(        'rel')  ):
			 s = s + ' ' + os.path.join(self._spec.subdirectory,self._spec.name)#+', in cache ['+self._inCache+']'  #+', from ['+self._spec.file+']'
		else:
			s = s + ' ' + os.path.join(self._spec.subdirectory,self._spec.name)
                        # The revisions display mode was added by Scot Kronenfeld 2/2009
                        # It will display the packageRevision of each package, if it contains one
                        if displayMode('revisions'):
                                prAtom = getPackageRevision(self.getEs("packageRevision"))
                                rev = None
                                if(prAtom):
                                        rev = prAtom.getRevision()
                                else:
                                        rev = "No revision defined"
                                s = s + "   revision '" + rev + "'"

			if displayMode(       'up'):
				cachesTemp = copy.deepcopy(self._spec.caches)
				if len(cachesTemp)>0: cachesTemp.pop(0)
				s = s + ', update from ['
				count = 0
#				for cache in self._spec.caches: 
				for cache in cachesTemp: 
					count = count + 1
#					if count==len(self._spec.caches): s = s + cache
					if count==len(cachesTemp): s = s + cache
					else:                      s = s + cache+':'
				s = s + ']'
			if displayMode(       'req'): s = s + ' | ' + self._spec.guard
			if displayMode(        'in'): s = s + ', in cache ['+self._inCache+']'
			if displayMode(       'src'): s = s + ', source cache ['+self._sourceCache+']'
			if displayMode(    'subdir'): s = s + ', subdirectory ['+ self._spec.subdirectory+']'
			if displayMode(      'file'): s = s + ', from [' + self._spec.file+']'
			if displayMode(       'loc'): s = s + ', installation starting from ['+loc+']'
			if displayMode(       'rel') and self._neutered: s = s + ' <=(relative)= '+self.caches
			
		print indent*' '+s+t+tail
		if displayMode('config') and len(self._modifiers)>0: 
			s = ''
			for sp in self._modifiers: s = s + ' ' + sp.str()
			print indent*' '+'       configured by:'+s
		if displayMode(   'par') and len(self._parents  )>0:
			s = ''
			for sp in self._parents: s = s + ' ' + sp.str()
			print indent*' '+'       parents:'+s
		if displayMode('version'):
			for e in self._environ: 
				if e.type=='version' or e.type=='version tuple': 
					print indent*' '+'           '+`e`
		if displayMode('release'):
			for e in self._environ: 
				if e.type=='release': 
					print indent*' '+'           '+`e`
		if displayMode('description'):
			for e in self._environ:
				if e.type=='description':
					print indent*' '+'           '+`e`
		if displayMode('url'):
			for e in self._environ:
				if e.type=='url':
					print indent*' '+'           '+`e`
		if displayMode('tag'):
			for e in self._environ: 
				if e.type=='tag': 
					print indent*' '+'           '+`e`
		if displayMode('patch'):
			for e in self._environ:
				if e.type=='patch':
					print indent*' '+'           '+`e`
		if displayMode('option'):
			for e in self._environ:
				if e.type=='option':
					print indent*' '+'           '+`e`
		if displayMode('mirror') or displayMode('snap'):
			if hasattr(self._spec,'_mirrors'):
				keys = self._spec._mirrors.keys()
				for key in keys:
					mirror,t,snapshot = self._spec._mirrors[key]
					if snapshot:
						print indent*' '+'           '+'...from cache ['+key+'], a snapshot of ['+mirror+'] taken at ['+time.ctime(t)+'].'
					else:
						print indent*' '+'           '+'...from cache ['+key+'], a mirror of ['+mirror+'] last updated ['+time.ctime(t)+'].' 
		if   displayMode('src'):
			for line in       self._sourceCode: print indent*' '+'         [src] '+line[:-1]
		if displayMode('cmp'):
			self._environ.display(indent+8)
		if displayMode('ups'):
			for line in self._updateSourceCode: print indent*' '+'         [ups] '+line[:-1]

	def displayM(self,depth=99999,indent=0):
		if depth==0: self.display(indent,'...')
		else:        self.display(indent)
		if depth>0: self._environ.displayM(depth-1,indent+4)
		return Reason()

	def locateRefresh(self):
		if len(self._environ)>0 and self._environ[0].type=='mkdir': self._spec.location = self._environ[0].str()
	def parents  (self): return self._parents
	def modifiers(self): return self._modifiers

#-- Environment
	def reasonFixup(self,r,action='installed'):
		if not r.ok():
			if hasattr(r,'headline'):
				if r.headline=='':
					rr = copy.deepcopy(r)
					rr.headline = 'Package ['+self.str()+'] not ['+action+']:'
				else:
					rr = AllReason()
					rr.headline = 'Package ['+self.str()+'] not ['+action+']:'
					rr.append(r)
			else:
				rr = AllReason()
				rr.headline = 'Package ['+self.str()+'] not ['+action+']:'
				rr.append(r)
		else:
			rr = r
		return rr
			
	def satisfied(self): 
		r = self._environ.satisfied()
		if r.ok(): 
			self.lastsat  = 1
		else:
			pass
#			self.lastfail = 1
		return self.reasonFixup(r)
	def satisfiable(self): 
		self._lastSatisfiable = self._environ.satisfiable()
		return self.reasonFixup(self._lastSatisfiable,'installable')
	def fetch(self):
		self._lastSatisfiable = self._environ.fetch()
		return self.reasonFixup(self._lastSatisfiable,'installable')
	def satisfy(self):
		verbo.log('pac','About to begin installing ['+self._spec.str()+']...')
		if verbo('pac-brief'): flicker('  Installing '+self._spec.name+'...')
		r = ask.re('pac','OK to begin installing ['+self._spec.str()+']?')
		if r.ok():
			if self._neutered:
				r = self.setup()
				if not r.ok():
					r.display()
					r = Reason("Package ["+self.str()+"] not installed at remote installation.")
					self.lastfail = 1
				else:
					self.lastsat  = 1
			else:
				r = self._environ.satisfy()
				if r.ok(): self.lastsat  = 1
				else:      self.lastfail = 1
				
				if r.ok(): 
					if verbo('pac-brief'): flicker('  '+self._spec.name+' has been installed.')
					verbo.log('pac','Package ['+self._spec.str()+'] successfully installed...')
					r = ask.re('pac','Package ['+self._spec.str()+'] has been successfully installed. Keep going?')
				else:      
					if verbo('pac-brief'): flicker('  '+self._spec.name+' has failed to install.')
					verbo.log('pac','Package ['+self._spec.str()+'] installation attempt has failed...')
		return self.reasonFixup(r)
	def setup(self): 
		idd = self._id()
		if not _setupBody.has_key(idd):
			debug.log('setup','Package ['+self._spec.str()+'] is being setup...')
			r = self._environ.setup()
			if not r.ok(): 
				print r
				r = Reason("Package ["+self._spec.str()+"] has not been installed.  Can't setup.")
			_setupBody[idd] = ''
		else:
			r = Reason()
		return self.reasonFixup(r)
	def restore(self):
		r = Reason()
		if not self._neutered:
			r = self._environ.restore()
			if r.ok():
				self.lastsat  = 0
				self.lastfail = 0
		return self.reasonFixup(r,'uninstalled')

#-- Verify
	def verify(self): 
		r = self.reasonFixup(self._environ.verify(),'verified')
		if not r.ok():
			self.lastsat = 0
			self.lastfail= 1
		return r
	def repair(self): return self.satisfy  ()

#-- Install
	def uninstall(self,depth=0):
		r = Reason()
		if verbo('pac'): print 'About to begin uninstalling ['+self._spec.str()+']...'
		if verbo('pac-brief'): flicker('  Uninstalling '+self._spec.name+'...')
		r = ask.re('pac','OK to begin uninstalling ['+self._spec.str()+']?')
		if r.ok():
			if self._neutered or depth<0:
				pass
			elif self.lastsat==1 or self.lastfail==1:
				if self.lastsat and len(self.getEs('uninstall shell command'))>0: self.setup()
				self.lastsat  = 0
				self.lastfail = 0
				
				if len(self._modifiers)>0: r = allReason(self._modifiers,lambda spec: LazyPackage(spec).uninstall())
				
				if r.ok():
					r = self.uninstallBody(depth)
					if not switch('update'): self.uninstallSet()
			
			if r.ok(): 
				if verbo('pac'): print 'Package ['+self._spec.str()+'] successfully uninstalled...'
				if verbo('pac-brief'): flicker('  '+self._spec.name+' has been uninstalled.')
				r = ask.re('pac','Package ['+self._spec.str()+'] has beed successfully uninstalled.  Keep going?')
			else:      
				if verbo('pac-brief'): flicker('  '+self._spec.name+' has failed to uninstall.')
				verbo.log('pac','Package ['+self._spec.str()+'] uninstallation attempt has failed...')
		return self.reasonFixup(r,'uninstall')
	def uninstallBody(self,depth=0):
		def f(e):
			r = Reason()
			if e.type=='AND' or e.type=='OR':
				r = allReasonQB(e,lambda e: f(e))
			elif e.type=='lazy package':
				if exists(e.modifiers(),lambda mod: mod.satisfiedBy(self)): r = e.uninstallBody(depth  )
				elif depth>0:                                               r = e.uninstall    (depth-1)
			else:
				r = e.restore()
			return r
		r = allReasonQB(self._environ,lambda e: f(e))
		self.lastsat  = 0
		self.lastfail = 0
		return r
	def uninstallSet(self):
		self.lastsat  = 0
		self.lastfail = 0
		r = allReasonQB(self.parents(),lambda spec: LazyPackage(spec).uninstallSet())
		return r
	def remove(self,depth=0):
		r = ask.re('pac','OK to remove package ['+self._spec.str()+']?')
		if depth>=0 and r.ok():
#			r = self.uninstall(0)
			self.uninstall(0)
			if r.ok(): r = self.desave()
			if r.ok(): r = self.descend(depth)
			if r.ok(): r = UniversalCache.UniversalCache('home').remove(self._spec)
		return self.reasonFixup(r,'remove')
	def desave(self):
		def f(E):
			r = Reason()
			if E.type=='AND' or E.type=='OR': 
				r = allReason(E,lambda e: f(e))
			elif E.type=='restore':           
				r = E.removeSave()
			return r
		return f(self._environ)
	def descend(self,depth=0):
		def f(E,depth):
			r = Reason()
			if E.type=='AND' or E.type=='OR':   
				r = allReason(E,lambda e: f(e,depth))
			elif E.type=='lazy package':
				r = E.removeParent(self._spec,depth)
			return r
		r = f(self._environ,depth)
		return r
#-- Update
	def updateCheck(self):
		self._update = OR()
		updateLog('up-check', 'Checking for update of ['+self._spec.str()+']...')

#--  S.Y. Feb. 20, 2006.  Bug fix Jan 19, 2007.  S.Y.
		spec2 = copy.deepcopy(self._spec)
		if len(spec2.caches)>0: 
			if equivSlash(spec2.caches[0],pac_anchor): spec2.caches.pop(0)
		r,p = spec2.get()
		
		if r.ok():
			if not self.upEqual(self._source,p._source):
				updateLog('up', 'Update of ['+self._spec.str()+'] found...')
				self._update           = p._environ
				self._updateSourceCode = p._sourceCode[:]
		else:
			updateLog('up', "Can't check for update. Package ["+self._spec.str()+"] not found...")
		if r.ok(): r = self._environ.updateCheck()
		return r
	def updateRemove (self): 
		self._update = OR()
		return self._environ.updateRemove()
	def updateWaiting(self): return Reason('No update waiting.',self._update == OR())
	def updateSelf(self):
		r = Reason()
		if r.ok():
			r = Reason("Can't update relative package ["+self.str()+"].",self._neutered)
			if r.ok():
				if not self._update==OR():
					upd = self.status()[1]
					if upd:
						r = self.setup()
						if r.ok(): 
							r = LazyPackage(self._spec).uninstall(0)
							if not r.ok(): self.lastfail = 1; self.lastsat =  0
					if r.ok():
						r = ask.re('up','OK to update ['+self._spec.str()+']?')
						if r.ok():
							updateLog('up','Updating ['+self._spec.name+']...')
							self._environ    = copy.deepcopy(self._update)
							self._source     = copy.deepcopy(self._update)
							self._sourceCode = self._updateSourceCode
							self._update = OR()
							if upd: 
								r = self.satisfy()
								if r.ok():  #-- S.Y. Feb. 2008
									c = UniversalCache.UniversalCache('home')
									c.put(self)
									r = allReason(self._modifiers,lambda spec: LazyPackage(spec).satisfy())
					else:
						updateLog('up',"Can't uninstall ["+self._spec.name+"].  Not updated...")
				else:
					r = self._environ.update()
		return r
	def update(self):
		r = Reason("Can't update relative package ["+self.str()+"].",self._neutered)
		if r.ok():
			inst = self.lastsat
			if self.updateWaiting():
				if not switch('single'): r = self._environ.update()
				if r.ok(): 
					pre = [lp._spec for lp in self.getLps()]
					r = self.updateSelf()
					pos = [lp._spec for lp in self.getLps()]
					# -- remove parents or modifiers if necessary.  S.Y. Feb. 2008.
					for spec in pre:
						if not exists(pos,lambda sp: sp<=spec): 
							c = UniversalCache.UniversalCache('home')
							r2,ps = c.getAll(spec,[])
							for p in ps:
								parents,modifiers = [],[]
								for sp in p._parents:
									if not self._spec<=sp: parents.append(sp)
								for sp in p._modifiers:
									if not self._spec<=sp: modifiers.append(sp)
								p._parents   = parents
								p._modifiers = modifiers
								c.put(p)
		return self.reasonFixup(r,'updated')
#-- setup
	def shellOut(self,csh,sh,py,pl,ksh): 
		if self.lastsat:
			idd = self._id()
			if not _shellOut.has_key(idd):
				_shellOut[idd] = ''
				lines = ['#\n','#-- '+`self`+'\n','#\n']
				for line in lines: 
					csh.write(line); sh.write(line); py.write(line); pl.write(line); ksh.write(line)
				self._environ.shellOut(csh,sh,py,pl,ksh)

_updateCheck   = {}
_updateRemove  = {}
_updateSelf    = {}
_update        = {}

_satisfied     = {}
_satisfiable   = {}
_satisfy       = {}
_restore       = {}
_remove        = {}
_removeMode    = {}
_uninstallSet  = {}
_uninstallUp   = {}
_uninstall     = {}
_uninstallBody = {}
_fetch         = {}

_verify        = {}
_repair        = {}

_setup         = {}
_setupBody     = {}
_shellOut      = {}

_pardb         = {}
_moddb         = {}

class LazyPackage(Package):
	type   = 'lazy package'
	title  = 'Lazy Package'
	action = 'install lazy package'
	
	def __init__(self,spec=Spec()):
		self._spec      = spec
		self._modified  = 0
		self._parent    = Spec()
		self._lazy = 1

	def _cacheErrorMessage(self):
		c = UniversalCache.UniversalCache('home')
		r,p = c.get(self._spec)
		lines = []
		if hasattr(p,'_sourceCache'):
			u = UniversalCache.UniversalCache(p._sourceCache)
			if hasattr(u,'_cache') and hasattr(u._cache,'_access'):
				a = u._cache._access
				r,names = a.names()
				if r.ok() and 'error.txt' in names:
					r,lines = a.getLines('error.txt')
		return lines
	def _optionErrorMessage(self):
		c = UniversalCache.UniversalCache('home')
		r,p = c.get(self._spec)
		lines = []
		if r.ok():
			ops = p.getEs('option')
			for op in ops:
				txt = op.value
				if txt.startswith('error:'): 
					for line in txt[6:].split('\n'): lines.append(line)
		return lines
		
	def lazyApplyU(self,f=lambda p: Reason()):
		c = UniversalCache.UniversalCache('home')
		r,p = c.get(self._spec)
		if not r.ok(): r,p = self._spec.get()
		if r.ok():
			self.modifyApply(p)
			if r.ok(): r = f(p)
		else:
			p = Package()
		return r,p
	def lazyApplyR(self,f=lambda p: Reason()):
		c = UniversalCache.UniversalCache('home')
		r,p = c.get(self._spec)
		if r.ok() and hasattr(p,'_parents') and len(p._parents)>0: 
			L = [x.str() for x in p._parents]
			r = Reason("Package ["+p.str()+"] is required by package ["+listStrPrt(L)+"]. Can't remove.")
		if r.ok():
			self.modifyApply(p)
			if r.ok(): r = f(p)
		else:
			p = Package()
		return r,p
	def lazyApplyV(self,f=lambda p: Reason()):
		c = UniversalCache.UniversalCache('home')
		r,p = c.get(self._spec)
		if r.ok():
			self.modifyApply(p)
			if r.ok(): r = f(p)
		else:
			r = Reason()
			p = Package()
		return r,p
	def lazyApplyZ(self,f=lambda p: Reason()):
		r,p = self.lazyApplyU(f)
		if not p==Package():
			c = UniversalCache.UniversalCache('home')
			r,p2 = c.get(p._spec)
			if not (r.ok() and p2.satisfied()):
				r2 = c.put(p)
				if r.ok(): r = r2
		return r
	def lazyApplyM(self,f=lambda p: Reason()):
		r,p = self.lazyApplyU(f)
		if not p==Package(): 
			c = UniversalCache.UniversalCache('home')
			r2 = c.put(p)
			if r.ok(): r = r2
		return r
	def modifyApply(self,p):
		if not self._parent==Spec():
			if not (self._parent in p._parents): 
				p._parents.append(self._parent)
			if self._modified:
				if not (self._parent in p._modifiers): p._modifiers.append(self._parent)
		_pardb[self._spec._id()] = p._parents  [:]
		_moddb[self._spec._id()] = p._modifiers[:]
	def modifiers(self):
		r,p = self.lazyApplyU()
		return p._modifiers
	def parents(self):
		r,p = self.lazyApplyU()
		return p._parents
	def removeParent(self,spec,depth=0):
		def f(p):
			r = Reason()
			p._parents   = filter(lambda sp: not spec<=sp, p._parents  )
			p._modifiers = filter(lambda sp: not spec<=sp, p._modifiers)
			UniversalCache.UniversalCache('home').put(p)
			if p._parents==[] and p._modifiers==[]: r = p.remove(depth-1)
			return r
		return self.lazyApplyV(f)[0]
#-- Set
	def equal(self,p): return self._spec==p._spec
	def str(self): return self._spec.str()
	def display(self,indent=0):
		def f(p): p.display(indent); return Reason()
		r,p = self.lazyApplyU(f)
		if not r.ok(): r.display(indent)
	def displayM(self,depth=99999,indent=0):
		def f(p): p.displayM(depth,indent); return Reason()
		r,p = self.lazyApplyU(f)
		if not r.ok(): r.display(indent)
		return Reason()
	def status(self):
		r,p = self.lazyApplyU()
		return p.status()
	def check(self,db,f):
		idd = self._spec._id()
		if not db.has_key(idd): db[idd] = f()
		elif _pardb.has_key(idd) and _moddb.has_key(idd):
			if (not self._parent in _pardb[idd]) or \
			  ((not self._parent in _moddb[idd]) and self._modified): db[idd] = f()
			else: pass
		else:
			db[idd] = f()
		if hasattr(db[idd],'ok') and not db[idd].ok(): db[idd]._package = self
		return db[idd]
	def check0(self,db,f):
		idd = self._spec._id()
		if not db.has_key(idd): db[idd] = f()
		if hasattr(db[idd],'ok') and not db[idd].ok(): db[idd]._package = self
		return db[idd]
		
#-- Environment
	def satisfiable  (self): return self.check(_satisfiable,lambda: self.lazyApplyM(lambda x: x.satisfiable      ())    )
	def fetch        (self): return self.check(_fetch,      lambda: self.lazyApplyM(lambda x: x.fetch            ())    )
	def satisfied    (self): 
		r = self.check(_satisfied,  lambda: self.lazyApplyU(lambda x: x.satisfied                            ())[0] )
		if r.ok(): self.lastsat  = 1
		else:      self.lastfail = 1
		return r
	def satisfy      (self): 
		r = self.check(_satisfy,    lambda: self.lazyApplyM(lambda x: x.satisfy                              ())    )
		if r.ok(): self.lastsat  = 1
		else:      self.lastfail = 1
		return r
	def setup      (self): return self.check(_setup,      lambda: self.lazyApplyU(lambda x: x.setup              ())[0] )
	def restore    (self): return self.check(_restore,    lambda: self.lazyApplyM(lambda x: x.restore            ())    )

#-- Install
	def uninstallSet (self        ): return self.check (_uninstallSet, lambda: self.lazyApplyM(lambda x: x.uninstallSet      ())    )
	def remove       (self,depth=0): return self.check0(_remove,       lambda: self.lazyApplyR(lambda x: x.remove       (depth))[0] )
	def uninstall    (self,depth=0): 
		c = UniversalCache.UniversalCache('home')
		r,p = c.get(self._spec)
		if r.ok(): 
			return self.check0(_uninstall,    lambda: self.lazyApplyM(lambda x: x.uninstall    (depth))    )
		else:
			return Reason()
	def uninstallBody(self,depth=0): return self.check0(_uninstallBody,lambda: self.lazyApplyM(lambda x: x.uninstallBody(depth))    )

#-- Verify
	def verify       (self): return self.check (_verify,       lambda: self.lazyApplyU(lambda x: x.verify        ())[0] )
	def verifySave   (self): return self.check (_verify,       lambda: self.lazyApplyM(lambda x: x.verify        ())    )
	def repair       (self): 
		r = self.verifySave()
		if not r.ok():
			r = self.check (_repair,       lambda: self.lazyApplyM(lambda x: x.repair        ())    )
		return r
	
#-- Update
	def updateCheck  (self): return self.check (_updateCheck,  lambda: self.lazyApplyM(lambda x: x.updateCheck   ())    )
	def updateRemove (self): return self.check (_updateRemove, lambda: self.lazyApplyM(lambda x: x.updateRemove  ())    )
	def updateSelf   (self): return self.check (_updateSelf,   lambda: self.lazyApplyM(lambda x: x.updateSelf    ())    )
#	def update       (self): return self.check (_update,       lambda: self.lazyApplyZ(lambda x: x.update        ())    )
	def update       (self): return self.check (_update,       lambda: self.lazyApplyM(lambda x: x.update        ())    )
	def updateWaiting(self): return self.lazyApplyU(lambda x: x.updateWaiting ())[0]

#-- Setup
	def shellOut(self,csh,sh,py,pl,ksh): return self.check(_shellOut,lambda: self.lazyApplyU(lambda x: x.shellOut(csh,sh,py,pl,ksh))[0])
