#
#	Copyright July 2004, Saul Youssef
#
from Base             import *
from Abort            import *
from Environment      import *
from AtomUtils        import *
from AtomParser       import *
import Registry,Collections

import string,copy

def pop(line):
	if len(line)==0: abort('error')
	return line[0],line[1:]
	
def curlyMatch(line):
	got_one = 0
	if len(line)>2:
		if line[0]=='{' and line[-1]=='}':
			got_one = 1
			level = 0
			for i in range(len(line)):
				if   line[i]=='{': level = level + 1
				elif line[i]=='}': level = level - 1
				
				if level==0 and not i==len(line)-1:
					got_one = 0
					break
	return got_one

#def neutral(line,bra,ket):
#	count = 0
#	line2 = line[:]
#	while len(line2)>0:
#		c,line2 = pop(line2)
#		if c==bra: count = count + 1
#		if c==ket: count = count - 1
#	return count==0
#
#-- speedup from Alain Roy follows (S.Y.)
#
#def neutral(line,bra,ket):
#	count = 0
#	for c in line:
#		if c==bra: count = count + 1
#		if c==ket: count = count - 1
#	return count==0
def neutral(line,square,paren,curly):
	is_neutral = 0
	for c in line:
		if c=='[': square = square + 1
		if c==']': square = square - 1
		if c=='(': paren = paren + 1
		if c==')': paren = paren - 1
		if c=='{': curly = curly + 1
		if c=='}': curly = curly - 1
	if square == 0 and paren == 0 and curly == 0:
		is_neutral = 1
	return (square,paren,curly,is_neutral)

def rawparse(rawSource):
	r1 = []
	for line in rawSource: r1.append(string.replace(line,'\n',''))

#-- Comments
#	r2 = []
#	for line in r1:
#		line2 = ''
#		quote1,quote2 = 0,0
#		while len(line)>0:
#			c,line = pop(line)
#			if   c=="'":
#				if quote1==0: quote1 = 1
#				else        : quote1 = 0
#			elif c=='"':
#				if quote2==0: quote2 = 1
#				else        : quote2 = 0
#			if c=='#' and quote1==0 and quote2==0: break
#			else: 
#				line2 = line2 + c
#		r2.append(line2)
#-- speedup from Alain Roy follows.  (S.Y.)
#
	r2 = []
	for line in r1:
		count = 0
		quote1,quote2=0,0
		for c in line:
			if   c=="'":
				if quote1==0: quote1 = 1
				else        : quote1 = 0
			elif c=='"':
				if quote2==0: quote2 = 1
				else        : quote2 = 0
			if c=='#' and quote1==0 and quote2==0:
				break
			else:
				count = count + 1
		r2.append(line[0:count])

#-- Line continuation	
	r3 = []
	while len(r2)>0:
		t = r2.pop(0); 
		if len(t)>0 and t[-1]=='\\': line = t[:-1]
		else:           line = t
#		line = string.replace(t,'\\','')
		while len(t)>1 and t[-1]=='\\' and len(r2)>0:
			t = r2.pop(0)
			if t[-1]=='\\': line = line + t[:-1]
#			line = line + string.replace(t,'\\','')
		r3.append(string.strip(line))
		
#-- Neutralize
	r4 = []
	while len(r3)>0:
		line = r3.pop(0)
		square,paren,curly,is_neutral=neutral(line,0,0,0)
		if is_neutral == 1:
			r4.append(line)
		else:
			full_line = line
			while len(r3)>0 and is_neutral==0:
				line = r3.pop(0)
				square,paren,curly,is_neutral=neutral(line,square,paren,curly)
				full_line = full_line + ' ' + line
				if is_neutral == 1:
					r4.append(full_line)
					break
		if is_neutral == 0: 
			abort('Unbalanced [] () or {} in ['+line+'].')
	
#-- Syntax	
	source = []
	while len(r4)>0:
		line = string.strip(r4.pop(0))
		if len(line)>0 and line[0]!='{':
			while not syntaxOK(line) and len(r4)>0:
				t = r4.pop(0)
				line = line + string.replace(t,'\\','')
				
		if len(line)>0 and line[0]!='{' and not syntaxOK(line):
			abort('Syntax error in ['+line+'].')
		else:
			source.append(string.strip(line))
	return source	
	
def front(environs,typename):
	e2 = AND()
	for e in environs: 
		if e.type==typename: e2.extend(e)
	for e in environs:
		if e.type!=typename: e2.extend(e)
	return e2
	
def frontF(environs,f):
	e2 = AND()
	for e in environs:
		if     f(e): e2.extend(e)
	for e in environs:
		if not f(e): e2.extend(e)
	return e2
	
def lastInstall(environs):
	e2 = AND()
	for e in environs:
		if not (e.type=='OR' and len(e)>0 and e[0].type=='AND' and len(e[0])>0 and e[0][0].type=='username'): 
			e2.append(e)
	for e in environs:
		if      e.type=='OR' and len(e)>0 and e[0].type=='AND' and len(e[0])>0 and e[0][0].type=='username': 
			e2.append(e)
	return e2
	
def downloadOldStyle(e):
	if e.type=='OR' and len(e)>0 and e[0].type=='AND' and len(e[0])>0 and e[0][0].type=='platform': 
		return 1
	else: 
		return 0
		
def pathsOldStyle(e):
	if e.type=='OR' and len(e)>0 and e[0].type=='AND' and len(e[0])>0 and e[0][0].type=='platform': 
		return 1
	else: 
		return 0
	
def frontOld(environs,typename):
	e2 = AND()
	for e in environs: 
		if       e.type==typename and hasattr(e,'old'): e2.extend(e)
	for e in environs:
		if not ( e.type==typename and hasattr(e,'old') ): e2.extend(e)
	return e2
		
def standardOrder(environs):
	es = AND()
	for e in environs:
		if not hasattr(e,'_seq'): e._seq = 99999
		es.append(e)
	sort(es,lambda x,y: x._seq<=y._seq)
	return es
		
def standardOrder2(environs):
	e1 = front(environs,'download source')
	e2 = frontOld(e1,'package')
#	e3 = front(e2,'url')
	e3 = front(e2,'description')
	e4 = front(e3,'packageName')
	e5 = lastInstall(e4)
	return e5
	
def setShellSignatures(environ,packageName,sig=()):
	if hasattr(environ,'__getitem__') and not hasattr(environ,'attach'):
		count = 0
		for e in environ:
			count = count + 1
			sig2 = sig + (count,)
			setShellSignatures(e,packageName,sig2)
	else:
		if environ.type=='shell' or environ.type=='shell dialogue':
			environ.signature = (environ.command,packageName,sig,)
			
class SourceFile(Set):
#	def __init__(self,source='',packagename='',cachename='',filename=''):
	def __init__(self,source='',spec=None,cachename='',filename=''):
		self.rawsource    = source
		self._spec        = spec
		self.packagename  = spec.name
		self.cachename    = cachename
		self.filename     = filename
		self.source = rawparse(source)
		
	def __repr__(self): return `self.rawsource`
	def display(self,indent=0): 
		for line in self.rawsource: print indent*' '+line
		
	def prefix(self,subdirectory=''):
		ens = AND()
		ens.extend(CacheOfOrigin(self.cachename))
		ens.extend(SourceCode(self.filename,self.rawsource))
		return ens
		
	def suffix(self):
		ens = AND()
		return ens
		
	def comp(self):
		env = OR(); reason = Reason()
		try:
			env = self.evaluate()
		except AbortException,message:
			reason = Reason("Error compiling ["+`self`+"].")
			
		return reason,env
		
	def compN(self):
		reason,env = self.comp()
		return reason,env,self.packagename

	def evaluate(self):
		verbo.log('comp','Compiling ['+self.filename+']...')
		environs = AND()
		for line in self.source:
#			pst = Source(line,self.packagename,self.cachename)
			pst = Source(line,self._spec,self.cachename)
			pst.parse()
			ens = pst.evaluate()
			environs.extend(ens)
			
		dnc = Collections.CollectTypeExcept('download source',    'package')
		dwc = Collections.CollectTypeExcept('download',           'package')
		swc = Collections.CollectTypeExcept('systems',            'package')
		dwc2= Collections.CollectTypeExcept('downloadUntarzip',   'package')
		srcs = environs.collect(dnc)
		srcs = filter(lambda en: en.type==    'download source',environs)
		pacs = filter(lambda en: en.type==        'packageName',environs)
		sufs = filter(lambda en: en.type==    'suffix handling',environs)
		uprs = filter(lambda en: en.type==   'use package root',environs)
		nats = filter(lambda en: en.type==             'native',environs)
		dwns = environs.collect(dwc)
		swns = environs.collect(swc)
		dwns2= environs.collect(dwc2)
		pdrs = filter(lambda en: en.type==  'package directory',environs)
		
		if len(srcs)==0: download    = ''
		else:            download    = srcs[0].value
		if self.filename=='':
			if len(pacs)==0: packageName = ''
			else:            packageName = pacs[0].value
		elif len(self.filename)>=8:
			if len(pacs)==0: packageName = self.filename[:-7]
			else:            packageName = pacs[0].value
		else:
			abort('Unexpected filename ['+self.filename+'] in Source.')
		self.packagename = packageName
		
		if len(sufs)==0:   suffixHandling = 1
		else:              suffixHandling = sufs[0].value

		if len(uprs)>0: usePackageRoot = uprs[0].value
		else:           usePackageRoot = 1
#		
#		if    len(dwns)==0 and len(dwns2)==0: usePackageRoot = 0
#		elif  len(uprs)>0:                    usePackageRoot = uprs[0].value
#		else:                                 usePackageRoot = 1
		
		useDownloads = len(dwns)>0 or len(swns)>0 or len(dwns2)>0
	
#-- Parse for real
		environs  = AND()
		environs2 = AND()
		for line in self.source:
#			pst = Source(line,self.packagename,self.cachename,download,suffixHandling,usePackageRoot,useDownloads)
			pst = Source(line,self._spec,self.cachename,download,suffixHandling,usePackageRoot,useDownloads)
			
			pst.parse()
			en = pst.evaluate()
			if en.type!='native': environs2.extend(en)
			
		if len(nats)==0: 
			environs.extend(environs2)
		else:   
			l = filter(lambda en: en.type!='native',environs2)
			environs3 = AND()
			for ll in l: environs3.extend(ll)
			environs.extend(OR(nats[0],standardOrder(environs3)))

		setShellSignatures(environs,self.packagename)

		package = AND()
		
		if packageName!='': package.extend(PackageName(packageName))
		if packageName!='': 
			if len(pdrs)==0: package.extend(self.prefix())
			else:            package.extend(self.prefix(pdrs[0].value))
		
		if packageName!='':
			for e in standardOrder(environs): 
				if not e.type=='packageName': package.append(e)
		else:
			package.extend(standardOrder(environs))
		
		if packageName!='': package.extend(self.suffix())
		
		return package

class Source(Set,List):
#	def __init__(self,text,packagename='',cachename='',downloadsource='',suffixHandling=1,usePackageRoot=1,useDownloads=1):
	def __init__(self,text,spec=None,cachename='',downloadsource='',suffixHandling=1,usePackageRoot=1,useDownloads=1):
		self.type           = 'source'
		self.valu           = copy.copy(text)
		self.subs           = []
		self._spec          = spec
#		self.packagename    = packagename
		self.packagename    = spec.name
		self.cachename      = cachename
		self.downloadsource = downloadsource
		self.suffixHandling = suffixHandling
		self.usePackageRoot = usePackageRoot
		self.useDownloads   = useDownloads
#		self.attParser = AtomParser(self.packagename,cachename,downloadsource,suffixHandling,usePackageRoot,useDownloads)
		self.attParser = AtomParser(self._spec,cachename,downloadsource,suffixHandling,usePackageRoot,useDownloads)
		
	def __eq__(self,x): return self.type==x.type and self.valu==x.valu and \
	                           self.subs==x.subs
	def len(self): return len(self.subs)
	def __getitem__(self,i): return self.subs[i]
	def __repr__(self): return self.type+' '+self.valu+' '+`self.subs`

	def comp(self):
		env = OR(); reason = Reason()
		try:
			s2 = copy.deepcopy(self)
			s2.parse()
			env = s2.evaluate()
		except AbortException,message:
			reason = Reason("Error compiling ["+`self`+"].")
			
		return reason,env

	def parse(self):
		ormatch,substrs = self.orMatch()
		if ormatch:
			self.type = 'OR'
			self.valu = ''
			for s in substrs:
#				sc = Source(s,self.packagename,self.cachename,self.downloadsource)
				sc = Source(s,self._spec,self.cachename,self.downloadsource)
				sc.parse()
				self.subs.append(sc)
		else:
			substrs = self.andMatch()
			if len(substrs)<=1:
				self.type = 'token'
			else:
				self.type = 'AND'
				self.valu = ''
				for s in substrs:
#					sc = Source(s,self.packagename,self.cachename,self.downloadsource)
					sc = Source(s,self._spec,self.cachename,self.downloadsource)
					sc.parse()
					self.subs.append(sc)
		
	def evaluate(self):
		if   self.type == 'AND':
			environs = AND()
			for s in self: environs.extend(s.evaluate())
		elif self.type == 'OR':
			environs = OR ()
			for s in self: environs.extend(s.evaluate())
		elif self.type == 'token':
#			att = AtomParser(self.packagename,self.cachename,self.downloadsource,self.suffixHandling,self.usePackageRoot)
			att = AtomParser(self._spec,self.cachename,self.downloadsource,self.suffixHandling,self.usePackageRoot)
			environs = self.attParser.parse(self.valu)
		else:
			abort('Attempt to evaluate unparsed source ['+self.valu+'].')

		return environs
		
	def orMatch(self):
		line = string.strip(self.valu)
		while len(line)>0 and line[-1]==';': line = line[:-1]
#		if len(line)>1 and line[0]=='{' and line[-1]=='}':
		if len(line) and curlyMatch(line):
			got_one = 1
			substrs = []
			line = string.strip(line[1:-1])
			linelen=len(line)
			level=0
			clevel = 0
			inquote1 = 0
			inquote2 = 0
			text = ''
			prevblank = 0
			i = 0
			skip = 0
			for c in line:
				if skip:
					i = i + 1
					skip = 0
					continue
				if   c=='(': level = level + 1
				elif c==')': level = level - 1
				elif c=='{': clevel = clevel + 1
				elif c=='}': clevel = clevel - 1
				elif c=="'": 
					inquote1 = 1 - inquote1
				elif c=='"':
					inquote2 = 1 - inquote2
				
				if prevblank and clevel==0 and level==0 and inquote1==0 and inquote2==0 and \
				   linelen > i+1 and c=='O' and line[i+1]=='R' and line[i+2] in string.whitespace:
					substrs.append(string.strip(text))
					skip = 1
					text = ''
				else:
					text = text + c

				if c in string.whitespace: prevblank = 1
				else:                      prevblank = 0
				i = i + 1
				
			if text!='': substrs.append(string.strip(text))
		else:
			got_one = 0
			substrs = []

		#if got_one: 		
			#print "substrs = ", substrs, "\n"
		return got_one,substrs
			
	def andMatch(self):
		line = string.strip(self.valu)
		while len(line)>0 and line[-1]==';': line = line[:-1]
		substrs = []
		level = 0
		clevel = 0
		inquote1 = 0
		inquote2 = 0
		text = ''
		for c in line:
			if   c=='(': level = level + 1
			elif c==')': level = level - 1
			if   c=='{': clevel = clevel + 1
			elif c=='}': clevel = clevel - 1
			elif c=="'": 
				if    inquote1==0: inquote1 = 1
				else             : inquote1 = 0
			elif c=='"':
				if    inquote2==0: inquote2 = 1
				else             : inquote2 = 0
			
			if level==0 and clevel==0 and inquote1==0 and inquote2==0 and c==';':
				substrs.append(string.strip(text))
				text = ''
			else:
				text = text + c
		if text!='': substrs.append(string.strip(text))
		return substrs
		
