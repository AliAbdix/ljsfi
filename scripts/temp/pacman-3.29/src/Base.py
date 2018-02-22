#
#	Copyright Saul Youssef, January, 2005
#
from Abort import *
import sys,os,string,commands,copy,time,popen2,cPickle,pwd,grp,socket,anydbm,shutil

version        = '3.29'
oversion       = '3.19'
version_extra  = ''
pacmanDir      = 'o..pacman..o'
try:
	pac_anchor     = os.getcwd()
	if os.environ.has_key('PWD'): pwd_anchor = os.environ['PWD']
	else:                         pwd_anchor = ''
except OSError:
	print 'Current working directory does not exist.'
	sys.exit(1)
os.environ['PAC_ANCHOR'] = pac_anchor

pre_316_database = 0

def baseErrorMessage(): return string.strip(str(sys.exc_info()[1]))

def sublist(a,b): return sublistEQ(a,b,lambda x,y: x==y)
	
def sublistEQ(a,b,eq):
	aa = a[:]; bb = b[:]
	while len(aa)>0 and len(bb)>0:
		x = aa.pop()
		while len(bb)>0:
			y = bb.pop()
			if eq(x,y): break
	return len(aa)==0

def shellHeader(csh,sh,py,pl,ksh):
	lines = ['#','#-- Setup script made by Pacman '+version+' and is often regenerated.  DO NOT EDIT',"#"]
	for line in lines:
		csh.write(line+'\n')
		sh .write(line+'\n')
		py .write(line+'\n')
		pl .write(line+'\n')
		ksh.write(line+'\n')
		
	csh.write('#\n')
	csh.write('#-- begin pre-setup\n')
	csh.write('#\n')
	csh.write('setenv PAC_ANCHOR "%s"\n' % pac_anchor)
	csh.write('if (-d "${PAC_ANCHOR}/pre-setup") then\n')
	csh.write('    foreach PACMANi (`/usr/bin/env find "${PAC_ANCHOR}/pre-setup" -maxdepth 1 -type f -name \'*.csh\' | sort`)\n')
	csh.write('        source "${PACMANi}"\n')
	csh.write('    end\n')
	csh.write('    unsetenv PACMANi\n')
	csh.write('endif\n')
	csh.write('#\n')
	csh.write('#-- end pre-setup\n')
	csh.write('#\n')

	sh.write('#\n')
	sh.write('#-- begin pre-setup\n')
	sh.write('#\n')
	sh.write('export PAC_ANCHOR="%s"\n' % pac_anchor)	
	sh.write('if [ -d "${PAC_ANCHOR}/pre-setup" ]; then\n')
	sh.write('    for PACMANi in `/usr/bin/env find "${PAC_ANCHOR}/pre-setup" -maxdepth 1 -type f -name \'*.sh\' | sort`; do\n')
	sh.write('        source "${PACMANi}"\n')
	sh.write('    done\n')
	sh.write('    unset PACMANi\n')
	sh.write('fi\n')
	sh.write('#\n')
	sh.write('#-- end pre-setup\n')
	sh.write('#\n')
	
def shellFooter(csh,sh,py,pl,ksh):
	csh.write('#\n')
	csh.write('#-- begin post-setup\n')
	csh.write('#\n')
	csh.write('setenv PAC_ANCHOR "%s"\n' % pac_anchor)
	csh.write('if (-d "${PAC_ANCHOR}/post-setup") then\n')
	csh.write('    foreach PACMANi (`/usr/bin/env find "${PAC_ANCHOR}/post-setup" -maxdepth 1 -type f -name \'*.csh\' | sort`)\n')
	csh.write('        source "${PACMANi}"\n')
	csh.write('    end\n')
	csh.write('    unsetenv PACMANi\n')
	csh.write('endif\n')
	csh.write('#\n')
	csh.write('#-- end post-setup\n')
	csh.write('#\n')

	sh.write('#\n')
	sh.write('#-- begin post-setup\n')
	sh.write('#\n')
	sh.write('export PAC_ANCHOR="%s"\n' % pac_anchor)
	sh.write('if [ -d "${PAC_ANCHOR}/post-setup" ]; then\n')
	sh.write('    for PACMANi in `/usr/bin/env find "${PAC_ANCHOR}/post-setup" -maxdepth 1 -type f -name \'*.sh\' | sort`; do\n')
	sh.write('        source "${PACMANi}"\n')
	sh.write('    done\n')
	sh.write('    unset PACMANi\n')
	sh.write('fi\n')
	sh.write('#\n')
	sh.write('#-- end post-setup\n')
	sh.write('#\n')

def forall(x,f):
	q = 1
	for xx in x:
		if not f(xx):
			q = 0
			exit
	return q
		
def exists(x,f):
	q = 0
	for xx in x:
		if f(xx):
			q = 1
			exit
	return q	
		
class Set: pass
#	def __eq__(self,x): abort('Missing == in Set.')

class PreOrder(Set):
	def __le__(self,x): abort('Missing __le__ in PreOrder.')
	
	def __ge__(self,x): return x<=self
	def __lt__(self,x): return self<=x and not self==x
	def __gt__(self,x): return self>=x and not self==x

class PartialOrder(Set):
	def __le__(self,x): abort('Missing __le__ in PreOrder.')
	
	def __eq__(self,x): return x<=self and self<=x
	def __ge__(self,x): return x<=self
	def __lt__(self,x): return self<=x and not self==x
	def __gt__(self,x): return self>=x and not self==x
	
class PreOrderAlpha(PreOrder):
	def __init__(self,*x): self._list = [xx for xx in x]

	def __len__(self): return len(self._list)
	def __le__(self,x): return self._list <= x._list
		
class PreOrderVector(PreOrder):
	def __init__(self,*x): self._list = [xx for xx in x]
	
	def __len__(self): return len(self._list)
	def __le__(self,x):
		return len(self)==len(x) and forall(range(len(self)),lambda i: self._list[i]<=x._list[i])
		
class PrintOut:
	def __repr__(self): abort('Missing __repr__ function in Set.')
	def display(self,ind=0):
		print ind*' '+`self`
	
class Monoid(Set):
	def __add__(self,x): abort('Missing + in Monoid.')
	
class List(Monoid):
	def __getitem__(self,i): abort('Missing index in List object.')
	def __len__    (self):   abort('Missing len in List object.')
	def append     (self,x): abort('Missing append in List.')
	def extend     (self,xs):
		for x in xs: self.append(x)
	def pop        (self,i): abort('Missing pop in List.')
	def empty      (self):
		while len(self)>0: self.pop(0)
	
class ShellOut:
	def  shellOut(self,csh,sh,py,pl,ksh): abort('Missing shellOut in ShellOut.')
	
def cwdd():
	try:            
		c = os.getcwd()
	except OSError: 
		c = '- undefined -'
	return c
	
def get(path):
	try:
		f = open(path,'r')
		obj = cPickle.load(f)
		f.close()
	except(IOError,OSError): 
		abort("Failure reading from file ["+path+"].")
	return obj
	
class IOAble:
	def put(self,path):
		try:
			removeFile(path)
			f = open(path,'w')
			cPickle.dump(self,f)
			f.close()
		except (IOError,OSError):
			abort("Failure writing to file ["+path+"].")
	
class HtmlOut(Set,PrintOut): 
	def htmlLine(self,w): self.htmlOut(w)
	
class Reason(Set,HtmlOut,IOAble):
	def __init__(self,reason='ok',flag=-1): 
		if flag==-1:
			self._reason = reason
		else:
			if flag!=0: self._reason = reason
			else:       self._reason = 'ok'
	def __repr__(self): return self._reason
	def __eq__(self,x): return self._reason == x._reason
	def _display(self,indent=0): self.display(indent)
	def display(self,indent=0): 
		if not self.ok(): 
			if hasattr(self,'_package'): print (indent*' ')+'Error in package ['+self._package._spec.name+']:'
			print indent*' '+'    '+`self`
	def isNull(self): return self._reason=='ok'
	def     ok(self): return self.isNull()
	
	def reason(self,reas): self._reason = reas
	def append(self,r): self._reason = r._reason
	
	def htmlOut(self,w,bullet=1): w.text(`self`) 
	
	def require(self):
		if not self.ok(): 
			abort(`self`)
		else:             
			return 1
	def inquire(self):
		if not self.ok(): self.display()
		return self.ok()
	def _packages(self,ps):
		if hasattr(self,'_package'): 
			if not self._package._spec in [p._spec for p in ps]: ps.append(self._package)
		if isinstance(self,AllReason):
			for r in self._reasons: r._packages(ps)
		
class AllReason(Reason):
	headline0 = 'All of the following are problems:'
	def __init__(self,headline='All of the following are problems:'): 
		self._reasons = []
		self.headline = headline
			
	def __repr__(self): 
		if self.ok(): return 'ok'
		else:
			s = self.headline+' '
			for r in self._reasons:
				s = s + `r` + ' '
			return s
			
	def __len__(self): return len(self._reasons)
		
	def display(self,indent=0):
		self._display(indent)
		ps = []
		self._packages(ps)
		for p in ps:
			if hasattr(p,'_optionErrorMessage'): lines = p._optionErrorMessage()
			else                               : lines = []
			for line in lines: print indent*' '+line
		L = []
		for p in ps:
			if hasattr(p,'_cacheErrorMessage'):
				lines = p._cacheErrorMessage()
				if not lines in L: L.append(lines)
		for lines in L:
			for line in lines: print indent*' '+line[:-1]
#		for p in ps:
#			if hasattr(p,'_cacheErrorMessage'): lines = p._cacheErrorMessage()
#			else                              : lines = []
#			for line in lines: print indent*' '+line[:-1]
		
	def _display(self,indent=0):
		if self.ok(): print indent*' '+'ok'
		else:
			if self.headline=='' or self.headline=='All of the following are problems:':
				for r in self._reasons: r._display(indent)
			else:
				print indent*' '+self.headline
				for r in self._reasons: r._display(indent+4)
			
	def reason(self,reas): 
		if reas!='ok' and reas!='': self._reasons.append(Reason(reas))
	def append(self,r):
		if not r.ok(): 
			self._reasons.append(r)
		
	def isNull(self): return len(self._reasons)==0
	
	def htmlOut(self,w,bullet=1):
		if len(self)==0:
			w.text('ok')
		elif len(self)==1 and self.headline==self.headline0:
			self._reasons[0].htmlOut(w)
		else:
			w.text(self.headline); w.cr()
			w.text('<ul>')
			count = 0
			for r in self._reasons:
				count = count + 1
				r.htmlOut(w)
				if count!=len(self._reasons): w.text('<br>')
			w.text('</ul>'); w.cr()
			
	def flatten(self):
		reasonLists = []
		if self.headline != 'All of the following are problems:':
			reasonLists.append(Reason(self.headline))
		for r in self._reasons:
			if hasattr(r,'_reasons'): reasonLists.extend(r.flatten())
			else:                     reasonLists.append(r)
		return reasonLists
		
	def nodups(self):
		rl = self.flatten()
		return removedups(rl,lambda x,y: x==y)
		
def reasonDisplay(reason,mode=0):
	if not reason.ok() or mode:
		r = AllReason()
		r.append(reason)
		rl = r.nodups()
		for rr in rl: print rr
		if len(rl)==0: print 'ok'

class ExistsReason(AllReason):
	headline = 'One of the following prevents installation:'
		
def allReason(L,f):
	reasons = AllReason()
	for x in L: reasons.append(f(x))
	return reasons

def allReasonQ(L,f):
	reason = Reason()
	for x in L:
		reason = f(x)
		if not reason.ok(): break
	return reason
	
def allReasonQB(L,f):
	reason = Reason()
	for i in range(len(L)-1,-1,-1):
		reason = f(L[i])
		if not reason.ok(): break
	return reason
	
def existsReason(L,f):
	reasons = ExistsReason()
	for x in L:
		r = f(x)
		if r.ok(): reasons = ExistsReason(); break
		else:      reasons.append(r)
	return reasons
	
def existsReason2(L,f):
	reasons = ExistsReason()
	ex = 0
	for x in L:
		r = f(x)
		if not r.ok(): reasons.append(r)
		else: ex = 1
	if     ex: return ExistsReason()
	else:      return reasons
	
class RememberReason:
	def __init__(self,f):
		self._f = f
		self._tested = 0
		self._reason = Reason()
		
	def rememberReason(self):
		if not self._tested:
			self._reason = self._f()
			self._tested = 1
		return self._reason
			
	def currentReason (self):
		self._tested = 0
		return self.rememberReason()
		
	def reset(self):
		self._tested = 0
	
def multiTry(f,maxTry=3):
	r = f()
	f_try = 1
	while not r.ok() and f_try<maxTry:
		r = f()
		f_try = f_try + 1
	return r
	
def makeFileFixedSize(sizeInMegs,path):
	reason = Reason()
	try:
		f = open(path,'w')
		for i in range(sizeInMegs):
			for x in range(10):
				for y in range(10):
					for z in range(10):
						f.write(`z`)
			f.write('\n')
		f.close()
	except (IOError,OSError):
		reason = Reason("Error creating temporary file ["+path+"].")
	return reason

class History:
	__directory = pacmanDir+'/logs'
	__path      = pacmanDir+'/logs/history.txt'
	__warned    = 0
	def history(self,*x):
		if os.path.exists(self.__directory) and os.path.isdir(self.__directory):
			try:
				if os.path.exists(self.__path): f = open(self.__path,'a')
				else:                           f = open(self.__path,'w')
				for xx in x: f.write(xx); f.write('...')
				f.write('\n')
				f.close()
				self.__path = fullpath(self.__path)
			except (IOError,OSError):
				if self.__warned: 
					self.warned = 1
					print "Warning: can't write to history file..."
				
	def getHistory(self):
		h = []
		if os.path.exists(self.__directory) and os.path.isdir(self.__directory):
			try:
				f = open(self.__path,'r')
				lines = f.readlines()
				f.close()
				self.__path = fullpath(self.__path)
				for line in lines: h.append(string.split(line,'...'))
			except (IOError,OSError):
				print "Can't read history file..."
		return h

class FixedNames(List):
	def __init__(self):
		self._names = []
		self.__title = ''
		
	def __eq__(self,x):  return self._names == x._names
	def display(self):
		print self.title
		for name in self._names: print '    '+name
		
	def __getitem__(self,i):  return self._names[i]
	def __len__(self):        return len(self._names)
	def containsAll(self,xs): return forall(xs,lambda x: self.contains(x))

class Equiv:
	def __init__(self,pairs):
		self._pairs = []; self._items = []
		for p in pairs: 
			self._pairs.append((p[0],p[1],))
			if not p[0] in self._items: self._items.append(p[0])
			if not p[1] in self._items: self._items.append(p[1])
		i = 0
		self._class = {}
		for x in self._items:
			self._class[x] = i
			i = i + 1
		got_one = 1
		while got_one:
			got_one = 0
			for x,y in self._pairs:
				if not self._class[x]==self._class[y]:
					p,q,got_one = x,y,1; break
			if got_one: 
				x = min(self._class[p],self._class[q])
				self._class[p],self._class[q] = x,x
	def equiv(self,x,y):
		if x==y: 
			eq = 1
		elif self._class.has_key(x) and self._class.has_key(y):
			eq = self._class[x]==self._class[y]
		else:
			eq = 0
		return eq
		
	def items(self): return self._items
	def classes(self):
		l = self.items()
		def leq(x,y): return self._class[x]<=self._class[y]
		sort(l,leq)
		cls = []
		while len(l)>0:
			x = l.pop(0)
			if                    cls==[]: cls.    append([x])
			elif self.equiv(cls[-1][0],x): cls[-1].append( x )
			else:                          cls.    append([x])
		return cls
	
class Clusters:
	def __init__(self,items): self.__items = items
	def cluster(self,equiv):
		c = []
		while len(self.__items)>0:
			x = self.__items.pop()
			cc = [x]; remains = []
			for y in self.__items:
				if equiv(x,y): cc.append(y)
				else:          remains.append(y)
			self.__items = remains[:]
			c.append(cc)
		return c
		
def removedups(l,equiv):
	l2 = []
	for ll in l:
		allneq = 1
		for x in l2:
			if equiv(x,ll): allneq = 0; break
		if allneq: l2.append(ll)
	return l2
	
def removeDups(l):
	l2 = []
	for ll in l:
		allneq = 1
		for x in l2:
			if x==ll: allneq = 0; break
		if allneq: l2.append(ll)
	return l2
	
		
def sort(l,le):
	got_one = 1
	while got_one:
		got_one = 0
		for i in range(len(l)-1):
			if not le(l[i],l[i+1]):
				temp = l[i+1]; l[i+1] = l[i]; l[i] = temp
				got_one = 1

def transitiveClosure(x,y,E):
	got_one = 0
	for e in E:
		if e[0]==x:
			if e[1]==y: 
				got_one = 1
			else:
				F = E[:]; F.remove(e)
				got_one = transitiveClosure(e[0],y,F) or transitiveClosure(e[1],y,F)
		if got_one: break
	return got_one

def prefix(path):
	if '.' in path: 
		l = string.split(path,'.')
		s = ''
		for i in range(len(l)-1):
			s = s + l[i] + '.'
		return s
	else:
		return path
		
def joinurl(head,tail):
	if tail=='': return head
	else:
		if   head[-1]=='/' and tail[0]=='/': return head+tail[1:]
		elif head[-1]=='/' and tail[0]!='/': return head+tail
		elif head[-1]!='/' and tail[0]=='/': return head+tail
		elif head[-1]!='/' and tail[0]!='/': return head+'/'+tail
		else: abort('error.')

def ln(filename,host=socket.gethostname(),location=cwdd()):
	return str2file(host+'_'+location+'_'+filename)

def removeFile(path):
	if os.path.exists(path): 
		if verbo('io'): print 'Removing ['+path+']...'
		try:
			os.remove(path)
		except OSError:
			pass
	
def removeFiles(*paths):
	for path in paths: removeFile(path)
	
def saveFiles(*paths):
	for path in paths: saveFile(path)
	
def saveFile(path):
	if os.path.exists(path):
		if verbo('io'): print 'Saving ['+path+']...'
		try:
			os.system('cp '+path+' '+path+'.sav')
		except (OSError,IOError):
			print "Can't mv ["+path+"].  Setup scripts not saved."
	
def writeable(path):
	try:
		f = open(os.path.join(path,'zxzytmpfoo'),'w')
		f.write('  ')
		f.close()
		removeFile(os.path.join(path,'zxzytmpfoo'))
		return 1
	except (IOError,OSError):
		return 0

def writeAccess(path): return os.access(path,os.W_OK)
	
def readAccess(path):  return os.access(path,os.R_OK)

# The fileInPath function was fixed by Scot Kronenfeld 2/2009
# Previously, with GNU which v2.16 (common in many Linux distros), this function
# would always return true, even if the supplied app was not in the path
#
# Now, the code with crawl through the PATH manually, looking for app, and
# not rely on the system 'which' command
def fileInPath(app):
#	verbo.log('shell-all','About to execute [which '+app+']...')

        if "PATH" in os.environ:
                for directory in os.environ["PATH"].split(os.pathsep):
                        exe = os.path.join(directory, app)
                        if os.path.exists(exe) and os.access(exe, os.X_OK):
                                return Reason()
                return Reason("["+app+"] is not in your path.")
        else:
                status,output = commands.getstatusoutput('which '+app)
        
                if sys.platform[:6]=='cygwin':
                        return Reason("["+app+"] is not in your path.",string.count(output,'not found')>0)
                elif len(output)>2 and output[:2]=='no':
                        return Reason("["+app+"] is not in your path.")
                else:
                        return Reason()

def appendNew(x,l):
	if l.count(x)==0: l.append(x)

class Meter:
	def __init__(self,maximum,message='',minimum=0):
		self.maximum = maximum
		self.minimum = max(minimum,0)
		if maximum>minimum and verbo('meter') or verbo('tarfiles'):
			if not message=='': print message
			sys.stdout.write("   0    10   20   30   40   50   60   70   80   90   100\n")
			sys.stdout.write("   +----+----+----+----+----+----+----+----+----+----+  \n")
			sys.stdout.write("   |    |    |    |    |    |    |    |    |    |    |    ")
		
	def meter(self,count):
		if self.maximum>self.minimum and not switch('quiet') and not switch('q'):
			fraction = int((float(count)/float(self.maximum))*50.0)
			sys.stdout.write('\r   #'+'#'*fraction)
			if count==self.maximum: sys.stdout.write('\n')

def meter(i,maximum,message='',front='    '): 
	x = `i`+'/'+`maximum`
	maxx = 12
	if len(x)<maxx: x = (maxx-len(x))*' '+x
	flash(x+' '+message)

def terminalWxH():
	"""Return terminal width and height.

	If stdout is a tty, return the tuple of ints (width,height).  If it is not 
	a tty or there is any other error determining the size, return (80,80).
	"""
	import fcntl, termios, struct
	if not sys.stdout.isatty(): return 80, 80
	try:
		cr = struct.unpack('hh', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, 'abcd'))
		return cr[1], cr[0]
	except KeyboardInterrupt:
		raise
	except:
		return 80, 80

class Writer(object):
	def __init__(self, writer):
		#writer should be any object with a write method that takes a string
		self.writer = writer
		self.lastFlickered = False
		self.lastLen = 0
	def write(self, text):
		self.clear()
		self.writer.write(text)
		self.lastFlickered = text.endswith('\r')
		self.lastLen = len(text.split('\n')[-1])
	def clear(self):
		if self.lastFlickered:
			self.writer.write(' '*(self.lastLen-1)+'\r')
			self.writer.flush()
	def __getattr__(self, name):
		return getattr(self.writer, name)

class Flicker(object):
	def __call__(self, line):
		if sys.stdout.isatty(): line = line[:terminalWxH()[0]]+'\r'
		else: line = line+'\n'
		sys.stdout.write(line)
		sys.stdout.flush()
		
flicker = Flicker()
	
def flash(line='',maxline=60):
	if       line == '':     sys.stdout.write('\n')
	elif len(line)>=maxline: sys.stdout.write(line[:maxline]+'\r')
	else:                    sys.stdout.write(line+(maxline-len(line))*' '+'\r')
	
def flash2(line):
	sys.stdout.write('\r'+line+'\r')
		
def niceListOut(l):
	count = 0
	for x in l:
		count = count + 1
		sys.stdout.write(x)
		if not count==len(l): sys.stdout.write(', ')
	
def dlMeter(a,b,c):
	mil = 1000000.0; k = 1000.0; 
	meg = float(a)*float(b)/mil; kbytes = float(a)*float(b)/k
	
	if verbo('meter'):
		if meg < 2.0:
			if min(int(kbytes),int(float(c)/k))==0 and int(float(c)/k)==0: 
			   	meter(1,1,'kB downloaded...')
			else:
				meter(min(int(kbytes),int(float(c)/k)),int(float(c)/k),'kB downloaded...')
		else:
			meter(min(int(meg),int(float(c)/mil)),int(float(c)/mil), 'MB downloaded...','       ')
		
def fullpath(p):
	if len(p)>0 and p[0]=='$' and os.environ.has_key(p[1:]):
		val = os.environ[p[1:]]
	else:
		val = os.path.abspath(os.path.expanduser(os.path.expandvars(p)))
	return val
#	return os.path.abspath(os.path.expanduser(os.path.expandvars(p)))

def fullpath2(p):
	x = fullpath(p)
	if tail(p,'/') and not tail(x,'/'): x = x + '/'
	return x

from Abort import *
def abort(message='Unrecoverable error. Contact Saul.'):
	raise AbortException,message

def pr(x): x.out(sys.stdout)

def htmlColor(hout,yesno,f):
	if yesno: 
		f.write('<b><font color="green">')
		hout.htmlOut(f)
		f.write('</font></b>')
	else:
		f.write('<b><font color="red">')
		hout.htmlOut(f)
		f.write('</font></b>')
		
def htmlColorStr(string,yesno,f):
	if yesno:
		f.write('<b><font color="#009900">')
		f.write(string)
		f.write('</font></b>')
	else:
		f.write('<b><font color="red">')
		f.write(string)
		f.write('</font></b>')

def isUrl(x):
	if len(x)>4: return x[0:4]=='http' or x[0:4]=='ftp:'
	else:        return 0
	
def fullNonURL(x):
	if isUrl(x): return x
	else:        return fullpath(x)
	
def isURL(x): return isUrl(x)

def equivURL(x,y): return x==y or x+'/'==y or x==y+'/'

def isPath(x): return not (':' in x or '@' in x or "\\" in x or ' ' in x)

def front(x,s): return len(x)>=len(s) and x[:len(s)]==s[:len(s)]

def phas(d,x):
	if d.count(x)>0: 
		return 1
	else:
		return 0

def python2():
	if sys.version[0]=='2':
		return 1
	else:
		return 0

def shx(str):
	if   shell()=='sh' or shell()=='ksh':
		return string.replace(str,'SHELL','sh')
	elif shell()=='csh':
		return string.replace(str,'SHELL','csh')
	else:
		if string.find(str,'SHELL')==-1:
			return str
		else:
			print 'Unknown unix shell.'
			sys.exit()

def shell():
	try:
		x = pwd.getpwnam(getusername())[-1]
		if   x == '/bin/csh':   sh = 'csh'
		elif x == '/bin/sh':    sh = 'sh'
		elif x == '/bin/tcsh':  sh = 'csh'
		elif x == '/bin/bash':  sh = 'sh'
		elif x == '/bin/bash2': sh = 'sh'
		elif x == '/bin/bsh':   sh = 'sh'
		elif x == '/bin/ash':   sh = 'sh'
		elif x == '/bin/ksh':   sh = 'ksh'
		else:                   sh = 'sh'
	except:
		sh = 'sh'
	return sh

def qInpath(com):
	if python2():
		t1,t2,t3 = os.popen3('which '+com)
		return t3.readline()==''
	else:
		return os.system('which '+com) == 0

def parseTarZ(tarZfile):
	try:
		if sys.platform[:6]=='cygwin':
#			f = os.popen('gunzip --stdout '+tarZfile+' | tar -t -f -')
			f = os.popen('gunzip --stdout '+tarZfile+' | '+gnuTarName()+' -t -f -')
			lines = f.readlines()
			if len(lines)>0: line = lines[0]
			else: line = ''
			f.close()
		else:
#			if ask('shell-all','About to execute ['+'gunzip --stdout '+tarZfile+' | tar -t -f -'+'].  OK?'):
			if ask('shell-all','About to execute ['+'gunzip --stdout '+tarZfile+' | '+gnuTarName()+' -t -f -'+'].  OK?'):
#				verbo.log('shell','gunzip --stdout '+tarZfile+' | tar -t -f -')
				verbo.log('shell','gunzip --stdout '+tarZfile+' | '+gnuTarName()+' -t -f -')
#				childout,childin,childerr = popen2.popen3('gunzip --stdout '+tarZfile+' | tar -t -f -')
				childout,childin,childerr = popen2.popen3('gunzip --stdout '+tarZfile+' | '+gnuTarName()+' -t -f -')
				line = childout.readline()
				childout.close()
				childin.close()
				childerr.close()
			else:
				abort("Permission to execute ["+'gunzip --stdout '+tarZfile+' | tar -t -f -] has been declined.')
	except (IOError,OSError):
		return Reason('Failure reading ['+tarZfile+'].'),''
	if line=='': return Reason('Tarball ['+tarZfile+'] does not untar to a single subdirectory.'),''
	else:
		got_root,root = parseTarLine(line)
		if got_root: return Reason(),root
		else:        return Reason('Tarball ['+tarZfile+'] does not untar to a single subdirectory.'),''
	
def parseTar(tarfile):
	try:
		if sys.platform[:6]=='cygwin':
#			f = os.popen('tar -t -f '+tarfile)
			f = os.popen(gnuTarName()+' -t -f '+tarfile)
			lines = f.readlines()
			if len(lines)>0: line = lines[0]
			else:            line = ''
			f.close()
		else:
#			if ask('shell-all','About to execute ['+'tar -t -f '+tarfile+'].  OK?'):
			if ask('shell-all','About to execute ['+gnuTarName()+' -t -f '+tarfile+'].  OK?'):
				verbo.log('shell','tar -t -f '+tarfile)
#				childout,childin,childerr = popen2.popen3('tar -t -f '+tarfile)
				childout,childin,childerr = popen2.popen3(gnuTarName()+' -t -f '+tarfile)
				line = childout.readline()
				childout.close()
				childin.close()
				childerr.close()
			else:
				abort("Permission to execute ["+'tar -t -f '+tarfile+'] has been declined.')
		
	except (IOError,OSError):
		return Reason('Failure reading ['+tarfile+'].'),''
		
	if line=='': return Reason('Tarball ['+tarfile+'] does not untar to a single subdirectory.'),''
	else:
		got_root,root = parseTarLine(line)
		if got_root: return Reason(),root
		else:        return Reason('Tarball ['+tarfile+'] does not untar to a single subdirectory.'),''
	
def parseTarLine(line0):
	if not '/' in line0:
		return 1,fullpath(os.getcwd())
	else:
		line = line0[:]
		while len(line)>1 and line[0]=='.' or line[0]=='/': line = line[1:]
		while len(line)>1 and line[-1]=='\n': line = line[:-1]
		
		if string.strip(line)=='':  got_root = 0; root = ''
		else:
			if line[0] in string.printable: 
				got_root = 1; 
				line = string.strip(line)
				root = string.split(line,'/')[0]
			else:                           got_root = 0; root = ''

		return got_root,root

params   = filter(lambda x: len(x)>0 and not x[0]=='-' and not x[-6:]=='pacman' and not x[-3:]=='pac',sys.argv)
switches = filter(lambda x: len(x)>0 and     x[0]=='-',sys.argv)

def switchItems(sw):
	items = []
	p2 = sys.argv[:]
	while len(p2)>0:
		par = p2.pop(0)
		if par=='-'+sw:
			while len(p2)>0 and len(p2[0])>0 and not p2[0][0]=='-': items.append(p2.pop(0))
	return items	

def pcl():
	s = '% pacman '
	for i in range(1,len(sys.argv)):
		s = s + ' '+sys.argv[i]
	return s

def switchpar(sw):
	for s in switches:
		if s[:string.find(s,':')]=='-'+sw:
			return 1,s[string.find(s,':')+1:]
	return 0,''
	
def switchInt(sw):
	q,par = switchpar(sw)
	val = 0
	if q:
		try:
			val = int(par)
		except ValueError:
			abort('Command line error with switch ['+sw+':'+`par`+'].')
	return q,val

def switchItem(sw,item):
	swq,text = switchpar(sw)
	if swq:
		return item in string.split(text,',')
	else:
		return 0

def param(i):
	if i < 0: 
		print 'Hard error.'
		sys.exit()
	if i>len(params): return ('')
	else:             return (params[i])
	
def switch(arg):
	return switch0(arg)
#	return switch0(arg) or switchpar(arg)[0]
	
def switch0(arg):
	if switches.count('-'+arg)>0: return 1
	else:                         return 0
		
verbose = switch('v') or switch('verbose')

def intBits(x,nbits):
	bits = []
	for i in range(nbits):
		if (x/2)*2==x: bits.append(0)
		else:          bits.append(1)
		x = x/2
	return bits
	
def bits2Int(bits):
	x = 0
	p = 0
	for i in range(len(bits)):
		x = x + bits[i]*(2**i)
	return x

def owner(path):
	try:
		u = user(os.stat(fullpath(path))[4])[0]
	except (IOError,OSError):
		abort('Error attempting to examine ['+path+'].')
	return u
	
def owner2(path):
	reason = Reason()
	try:
		u = user(os.stat(fullpath(path))[4])[0]
	except (IOError,OSError):
		u = ''
		reason = Reason('Error attempting to examine ['+path+'].')
	return reason,u
	
def getusername():
	euid = os.geteuid()
	return user(euid)[0]
		
def user(uid):
	try:
		username = pwd.getpwuid(uid)
	except KeyError:  
		username = 'unknown'
		print 'Warning: unknown userid ['+`uid`+'].'
#		abort('No such uid ['+`uid`+'].')
	return username

def userids(username):
	try:
		t = pwd.getpwnam(username)
		return 1,t[2],t[3]
	except KeyError:
		return 0,0,0
		
def userexists(username):
	try:
		t = pwd.getpwnam(username)
		return 1
	except KeyError:
		return 0
		
def groupExists(group):
	try:
		t = grp.getgrnam(group)
		return 1
	except KeyError:
		return 0

def fncat(a,b):
	if a=='':
		return b
	else:
		if a[len(a)-1]=='/':
			if b=='':
				return (a[:-1])
			else:
				return (a+b)
		else:
			return (a+'/'+b)
def tail(str,t):
	found = 0
	if len(str)>= len(t):
		if str[len(str)-len(t):len(str)]==t:
			found = 1
	return found

def yesdash(s):
	if    s >= 1: return ('yes')
	elif  s == 0: return ('-')
	else:
		print 'Unexpected argument to yesdash.'
		print s
		sys.exit(1)

def firstLine(path):
	r = Reason()
	px = fullpath(path)
	line = ''
	if os.path.exists(px):
		try:
			f = open(px,'r')
			lines = f.readlines()
			f.close()
		except:
			r = Reason("Can't read ["+px+"].")
		if len(lines)>0 and len(lines[0])>0:
			line = lines[0][:-1]
		else:
			r = Reason("File ["+px+"] does not contain a line of text.")
	else:
		r = Reason('['+px+'] is missing.')
	return r,line	

def envFile(env,file):
	if os.environ.has_key(env):
		return fncat(os.environ[env],file)
	else:
		print '** Environment variable ['+env+'] is not defined.'
		sys.exit(1)
		
def envval(env):
	if os.environ.has_key(env): return os.environ[env]
	else: return ''

def substr(sub,base):
	for i in range(len(base)):
		if sub==base[i:i+len(sub)]: return 1
	return 0
	
def safeCopy(source,target):
	r = Reason()
	if verbo('io'): print 'Copying ['+source+'] to ['+target+']...'
	try:
#		shutil.copyfile(source,target)
		os.system('cp '+source+' '+target)		
	except (IOError,OSError):
		if   not os.path.exists(source):
			r = Reason("Error copying ["+source+"] to ["+target+"].  File ["+source+"] does not exist.")
		elif not os.path.isdir(target) and not os.path.isdir(os.path.dirname(target)):
			r = Reason("Error copying ["+source+"] to ["+target+"].  Target directory does not exist.")
		else:
			r = Reason("Error copying ["+source+"] to ["+target+"].  You may be out of disk space.")
	return r
		
def listStrPrt(l):
	s = ''
	count = 0
	for ll in l: 
		count = count + 1
		s = s + ll
		if count!=len(l): s = s + ', '
	return s

def rpm_installed(rpm_name):
	if not fileInPath('rpm').ok():
		return 0
	else:
		rpmTmp = rpm_name
		if tail(rpmTmp,'.rpm'): rpmTmp = rpmTmp[:-4]
		status,output = commands.getstatusoutput('rpm -q '+rpmTmp)
		return status==0 and not contains(output,'not installed')
		
def yesno(message):
	while 1:
		try:
			answer = raw_input(message+' (y or n): ')
		except EOFError:
			answer = 'eof'
		if answer == 'y' or answer == 'yes' or answer == 'n' or answer == 'no': break
	if answer == 'y' or answer == 'yes': return 1
	return 0
	
def getFilename(message):
	while 1:
		filename = string.strip(raw_input(message))
		if os.path.exists(fullpath(string.strip(filename))): 
			break
		print "File ["+fullpath(filename)+"] doesn't exist. Try again..."
	return fullpath(filename)
	
def contains(a,b,case='case sensitive'): 
	if case=='case sensitive': return string.count(a,b)>0
	else:                      return string.count(string.upper(a),string.upper(b))>0
	
def str2file(text):
	t = ''
	for i in range(len(text)):
		if text[i] in string.letters or text[i] in string.digits: t = t + text[i]
		else:                                                     t = t + '_'
	return t
	
def cookieDirectory(message,dire2='$PAC_ANCHOR/'+pacmanDir+'/cookies'):
	dire = fullpath(dire2)
	try:
		if switch('ignore-cookies'): raise OSError
		f = open(os.path.join(dire,str2file(message+'-'+os.getcwd())),'r')
		lines = f.readlines()
		f.close()
		dirname = lines[0][:-1]
	except (OSError,IOError):
		dirname = chooseDirectory(message)
		try:
			f = open(os.path.join(dire,str2file(message+'-'+os.getcwd())),'w')
			f.write(dirname+'\n')
			f.close()
			print 'Saving answer to a cookie.  Use -ignore-cookies to re-choose...'
		except (OSError,IOError):
			print 'Warning: Failure writing cookie file to ['+os.path.join(dire,str2file(message))+']...'
	return dirname
			
def chooseDirectory(message):
	while 1:
		path = string.strip(raw_input(message))
		filename = os.path.dirname(path)
		if path=='' or filename=='':
			print path+" doesn't exist.  Try again..."
		elif not os.path.exists(fullpath(filename)):
			print fullpath(filename)+" does not exist.  Try again..."
		elif not os.path.isdir(fullpath(filename)):
			print fullpath(filename)+" is not a directory.  Try again..."
		elif not writeable(fullpath(filename)):
			print fullpath(filename)+" is not writeable.  Try again..."
		else:
			break
	return os.path.join(path)
	
class Switch:
	def __init__(self,name,options,default='on'):
		self.name       = name
		self.options    = options
		self.always_on  = 0
		self.off        = 0
		self.pref = fullpath(os.path.join(pac_anchor,pacmanDir,'preferences',self.name))
		self.default = default
		self.useropts = []
				
		for opt in switchItems(self.name):
			if opt=='help' or not self.options.has_key(opt):
				self.display()
				if not self.options.has_key(opt) and not opt=='help':
					print 'Unknown option -'+self.name+' '+opt+' on command line.'
					sys.exit(1)
				sys.exit(0)
		if switch(self.name) and len(switchItems(self.name))==0 and not self.name=='debug':
			self.display()
			print 'No option for -'+self.name+' specified on the command line.'
			sys.exit(1)

		if switch(self.name) and os.path.exists(pacmanDir) and len(switchItems(self.name))>0:
			try:
				g = open(self.pref,'w')
				for opt in switchItems(self.name): g.write(' '+opt)
				g.write('\n')
				g.close()
			except (IOError,OSError):
				abort('Error reading ['+self.pref+'].')
		
		if switch(self.name):
			self.useropts = switchItems(self.name)
		else:
			if os.path.exists(pacmanDir):
				if os.path.exists(self.pref):
					try:
						f = open(self.pref,'r')
						lines = f.readlines()
						f.close()
						if switch('def'): 
							sys.stdout.write('default: -'+self.name)
							for opt in string.split(lines[0][:-1],' '): 
								opt = string.strip(opt)
								if not opt=='': sys.stdout.write(' '+string.strip(opt))
							sys.stdout.write('\n')
						for opt in string.split(lines[0][:-1],' '):
							opt = string.strip(opt)
							if not opt=='': self.useropts.append(opt)
					except (IOError,OSError):
						abort('Error reading ['+self.pref+'].')
			elif self.name=='v':
				self.useropts.extend(['download-brief','cache-brief','tar-brief','up','retry'])
			elif self.name=='retry':
				self.useropts.extend(['10','pause-30-seconds'])
			elif self.name=='ask':
				self.useropts.extend(['tar-overwrite'])
			elif self.name=='setups':
				self.useropts.extend(['csh','sh'])
			
		self.off       = 'none' in self.useropts
		self.always_on = '*' in self.useropts or 'all' in self.useropts
		
	def save(self):
		if switch(self.name) and os.path.exists(os.path.join(pac_anchor,pacmanDir)) and len(switchItems(self.name))>0:
			try:
				g = open(self.pref,'w')
				for opt in switchItems(self.name): g.write(' '+opt)
				g.write('\n')
				g.close()
			except (IOError,OSError):
				abort('Error reading ['+self.pref+'].')
				
	def __repr__(self): return `self.always_on`+' '+`self.useropts`
	def display(self,indent=0):
		print indent*' '+'Available options for -'+self.name+':'
		keys = self.options.keys()
		keys.sort()
		for key in keys:
			print indent*' '+'  -'+self.name+' '+key+' '+self.options[key]
		if len(self.options)>1:
			print indent*' '+'Use -'+self.name+' <opt1> <opt2> <opt3>... for multiple options.'
	def any(self): 
		q,val = switchpar(self.name)
		return q or switch(self.name)
				
	def __call__(self,option): return (option=='*' or self.always_on or option in self.useropts) and not self.off
		
	def log(self,option,message,logfile='$PAC_ANCHOR/'+pacmanDir+'/logs/pacman.log'):
		if os.path.isdir(os.path.dirname(fullpath(logfile))):
			try:
				f = open(fullpath(logfile),'a')
				f.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())+' '+message+' -- by ['+option+'].\n')
#				f.write(message+' -- by ['+option+'] at '+time.ctime(time.time())+'\n')
				f.close()
			except IOError,OSError:
				pass
#				print 'Error attempting to write to ['+fullpath(logfile)+']...'
		if self(option):  
			print message; 
			return 1
		else:                            
			return 0		

verbo = Switch('v', {                                                                      \
	'all':'            All verbose messages in this list.',                            \
	'action':'         Message when Pacman takes any action defined in the lanauge.',  \
	'pac':'            Message when searching for a package in a cache.',              \
	'pac-brief':'      Flickering installation messages.',                             \
	'tcp':'            Message when a TCP connection is tested.',                      \
	'shell-out':'      View all shell output.',                                        \
	'shell':'          Message when Pacman shell commands are executed.',              \
	'shell-all':'      Message when any shell command is executed.',                   \
	'registry':'       Message when a registry addition is made.',                     \
	'cu':'             Message when changing usernames.',                              \
	'download':'       Downloading message and progress.',                             \
	'download-brief':' Flickering download messages.',                                 \
	'cd':'             Message when changing directories.',                            \
	'ssh':'            Message on remote ssh commands.',                               \
	'tar':'            Message for tar/zip related operations.',                       \
	'tar-brief':'      Flickering tar messages',                                       \
	'tarfiles':'       Display the name of each file as it is untarred.',              \
	'env':'            Message on environment variable operations.',                   \
	'http':'           Message for each http operation.',                              \
	'up':'             Display update related messages.',                              \
	'gsi':'            Display gsi operations.',                                       \
	'up-check':'       Message when an update is checked.',                            \
	'snap':'           To view snapshot related messages.',                            \
	'mirror':'         View mirror related messages.',                                 \
	'comp':'           Messages when compiling Pacman source.',                        \
	'cache':'          Cache operations.',                                             \
	'cache-brief':'    Flickering cache messages.',                                    \
	'inst':'           Message when putting or getting from an installation.',         \
	'retry':'          Messages about retrying.',                                      \
	'processes':'      Show running processes when using runningProcess atom.',        \
	'io':'             Messages when doing file i/o',                                  \
	'none':'           No verbose messages.',                                          \
	'users':'          Message on user group or account operations.',                  \
	'src':'            Message each time a source file is opened.',                    \
        'ptest':'          Message each time a package is tested against requirements.',   \
	'meter':'          Use ascii meters and counters.',                                \
	'path':'           Messages related to path variables.',                           \
	'browser':'        Messages when launching web browsers.',                         \
	'restore':'        Message when restoring/saving files.',                          \
	'text':'           Messages related to text line insertions and testing.'          \
} )

quiet = Switch('q', {                                          \
	'down':'	Suppress downloading messages.',       \
	'web':'		Suppress updating web pages.',         \
	'none':'        Use no quietness options.'             \
} )

debug = Switch('debug',{                                                                     \
	'src':'             Source files',                                                   \
	'status':'          Package status',                                                 \
	'shell':'           Shell output',                                                   \
	'spec':'            Message each time a package specification is tested.',           \
	'cache':'           Cache comparison',                                               \
	'setup':'           Message on internal setup operations.',                          \
	'ref':'             Lazy package ref.',                                              \
	'none':'            Use no debug options.',                                          \
	'os.system':'       Execute shell commands with python os.system.',                  \
	'tar-save':'        Tar save.',                                                      \
	'mirror-download':' Mirror download translation.',                                   \
	'tar':'             Tar.',                                                           \
	'ignoreShellError':'Ignore shell error codes',                                       \
	'wget':'            wget feedback',                                                  \
	'up':'              Update.',                                                        \
	'inst':'            Installation operations.'                                        \
})

browser = Switch('browser',{                \
	'netscape':'   Netscape',           \
	'mozilla':'    Mozilla',            \
	'lynx':'       Lynx (text based)',  \
	'w3m':'        w3m (text based)',   \
	'galeon':'     galeon'              \
} )

allow = Switch('allow', {                                                                                               \
	 'any-username':'                  Allow any user to modify the installation (not recommended).',               \
	 'unsupported-platforms':'         Allow any os to modify the installation (not recommended).',                 \
	 'moveable-installation':'         Allow Pacman installations to be copied (not recommended).',                 \
	 'non-snapshottable-downloads':'   Allow downloads specified with environment variables.',                      \
         'tar-overwrite':'                 Allow untarring to overwrite files.',                                        \
	 'undefined-shell':'               Allow shell commands containing undefined environment variables.',           \
	 'none':'                          Use no allow options.',                                                      \
	 'no-http-cache':'                 Disable server side http caching.',                                          \
	 'lock-override':'                 Override locked source caches.',                                             \
	 'trust-all-caches':'              Trust ALL caches automatically.',                             \
	 'bad-paths':'                     Allow path variables to clash.',                                             \
	 'save-setup':'                    Allow out of date setup scripts to remain during updates (default for Pacman >= 3.19).',  \
         'urllib2':'                       Use the urllib2 python module instead of wget for downloading.',             \
	 'any-platform':'                  Ignore the platform used when creating installations.',                      \
	 'old-database':'                  Use the old Pacman database implementation.',                                \
	 'extract-overwrite':'             Allow overwriting downloaded files when using -extract-downloads.',          \
	 'non-gnu-tar':"                   Try using whatever non-gnu tar program is in the installer's path.",         \
	 'uninstall-shell-stop':"          Allow a failure of an uninstall shell command to cause an error rather than be ignored.",\
	 'bad-tar-filenames':'             Allow non-standard filename characters in untarring filenames'               \
} )


setupOptions = Switch('setups', {
       'csh':'    C-shell setup scripts.',\
       'none':'   No setup scripts',\
       'sh':'     Bourne shell setup scripts.',\
       'py':'     Python setup scripts.',\
       'ksh':'    ksh shell setup scripts.',\
       'pl':'     Perl setup scripts.'
} )
       

upOptions = Switch('up',{
         'none':'          Fetch with normal update paths.',       \
         'fixed':'         Fetch with hard-wired update paths.',   \
	 'normal':'        Fetch with normal update paths.'        \
} )

httpRetry = Switch('retry',{                                                      \
	'1':'                 Http retry one times',                              \
	'2':'                 Http retry two times',                              \
	'3':'                 Http retry three times',                            \
	'5':'                 Http retry five times',                             \
	'10':'                Http retry ten times',                              \
	'20':'                Http retry twenty times',                           \
	'30':'                Http retry thirty times',                           \
	'100':'               Http retry one hundred times,',                     \
	'pause-1-second':'    Pause 1 second before retrying.',                   \
	'pause-3-seconds':'   Pause 3 seconds before retrying.',                  \
	'pause-10-seconds':'  Pause 10 seconds before retrying.',                 \
	'pause-30-seconds':'  Pause 30 seconds before retrying.',                 \
	'pause-60-seconds':'  Pause 60 seconds before retrying.',                 \
	'pause-2-minutes':'   Pause 2 minutes before retrying.',                  \
	'pause-5-minutes':'   Pause 5 minutes before retrying.',                  \
	'pause-10-minutes':'  Pause 10 minutes before retrying.',                 \
	'pause-20-minutes':'  Pause 20 minutes before retrying.',                 \
	'pause-30-minutes':'  Pause 30 minutes before retrying.',                 \
	'pause-1-hour':'      Pause 1 hour before retrying.',                     \
	'pause-5-hours':'     Pause 5 hours before retrying.'                     \
} )

tarPause = Switch('tarpause',{                                              \
	'1-second':'    Pause 1 second before retrying.',                   \
	'3-seconds':'   Pause 3 seconds before retrying.',                  \
	'10-seconds':'  Pause 10 seconds before retrying.',                 \
	'30-seconds':'  Pause 30 seconds before retrying.',                 \
	'60-seconds':'  Pause 60 seconds before retrying.',                 \
	'2-minutes':'   Pause 2 minutes before retrying.',                  \
	'5-minutes':'   Pause 5 minutes before retrying.',                  \
	'10-minutes':'  Pause 10 minutes before retrying.',                 \
	'20-minutes':'  Pause 20 minutes before retrying.',                 \
	'30-minutes':'  Pause 30 minutes before retrying.',                 \
	'1-hour':'      Pause 1 hour before retrying.',                     \
	'5-hours':'     Pause 5 hours before retrying.'                     \
} )

downloadTimeout = Switch('downloadtimeout',{                        \
	'1-second':'    Timeout after 1 second.',                   \
	'3-seconds':'   Timeout after 3 seconds.',                  \
	'10-seconds':'  Timeout after 10 seconds.',                 \
	'30-seconds':'  Timeout after 30 seconds.',                 \
	'60-seconds':'  Timeout after 60 seconds.',                 \
	'2-minutes':'   Timeout after 2 minutes.',                  \
	'5-minutes':'   Timeout after 5 minutes.',                  \
	'10-minutes':'  Timeout after 10 minutes.',                 \
	'20-minutes':'  Timeout after 20 minutes.',                 \
	'30-minutes':'  Timeout after 30 minutes.',                 \
	'1-hour':'      Timeout after 1 hour.',                     \
	'5-hours':'     Timeout after 5 hours.'                     \
} )

displayMode = Switch('d',{                                                          \
        'none':'           All display modes off.',                                 \
	'0':'              Display depth 0',                                        \
	'1':'              Display depth 1',                                        \
	'2':'              Display depth 2',                                        \
	'3':'              Display depth 3',                                        \
	'4':'              Display depth 4',                                        \
	'5':'              Display depth 5',                                        \
	'6':'              Display depth 6',                                        \
	'7':'              Display depth 7',                                        \
	'8':'              Display depth 8',                                        \
	'9':'              Display depth 9',                                        \
        'all':'            All displays on.',                                       \
	'description':'    Display package description atoms.',                     \
	'url':'            Display package url atoms.',                             \
	'config':'         Display package configurers.',                           \
	'version':'        Display package version strings, if any.',               \
	'release':'        Display package release strings, if any.',               \
	'tag':'            Display package tag strings, if any.',                   \
	'patch':'          Display package patch strings, if any.',                 \
	'option':'         Display package option strings, if any.',                \
	'par':'            Display package parents.',                               \
	'src':'            Display source code.',                                   \
	'cmp':'            Display compiled environmental conditions.',             \
	'req':'            Display requirements.',                                  \
	'up':'             Display update cache.',                                  \
	'ups':'            Display update source code.',                            \
	'tar':'            Display tarball contents in cmp display.',               \
	'file':'           Display source code file name.',                         \
	'subdir':'         Display cache subdirectory containing the source file.', \
	'mirror':'         Display extra mirror information.',                      \
	'snap':'           Display extra snapshot information.',                    \
	'in':'             Display the cache containing the package.',              \
	'none':'           No extra display options on.',                           \
	'loc':'            Display package starting location.',                     \
        # Revisions display mode added by Scot Kronenfeld 2/2009
        'revisions':'      Display Revisions.'                                      \
} )

def displayModeDepth():
	depth = 99999
	if    displayMode('0'): depth = 0
	elif  displayMode('1'): depth = 1
	elif  displayMode('2'): depth = 2
	elif  displayMode('3'): depth = 3
	elif  displayMode('4'): depth = 4
	elif  displayMode('5'): depth = 5
	elif  displayMode('6'): depth = 6
	elif  displayMode('7'): depth = 7
	elif  displayMode('8'): depth = 8
	elif  displayMode('9'): depth = 9
	return depth

def httpGetRetries():
	retry = 10
	if    httpRetry(  '1'): retry =   1
	elif  httpRetry(  '2'): retry =   2
	elif  httpRetry(  '3'): retry =   3
	elif  httpRetry(  '4'): retry =   4
	elif  httpRetry(  '5'): retry =   5
	elif  httpRetry(  '6'): retry =   6
	elif  httpRetry(  '7'): retry =   7
	elif  httpRetry(  '8'): retry =   8
	elif  httpRetry( '10'): retry =  10
	elif  httpRetry( '20'): retry =  20
	elif  httpRetry( '30'): retry =  30
	elif  httpRetry('100'): retry = 100
	return retry
	
def httpGetPause():
	pause = 60
	if    httpRetry('pause-1-second'    ): pause =     1
	elif  httpRetry('pause-3-seconds'   ): pause =     3
	elif  httpRetry('pause-10-seconds'  ): pause =    10
	elif  httpRetry('pause-30-seconds'  ): pause =    30
	elif  httpRetry('pause-60-seconds'  ): pause =    60
	elif  httpRetry('pause-2-minutes'   ): pause =   120
	elif  httpRetry('pause-5-minutes'   ): pause =   300
	elif  httpRetry('pause-10-minutes'  ): pause =   600
	elif  httpRetry('pause-20-minutes'  ): pause =  1200
	elif  httpRetry('pause-30-minutes'  ): pause =  1800
	elif  httpRetry('pause-1-hour'      ): pause =  3600
	elif  httpRetry('pause-5-hours'     ): pause = 18000
	return pause
	
def tarGetPause():
	pause = 0
	if    tarPause('1-second'    ): pause =     1
	elif  tarPause('3-seconds'   ): pause =     3
	elif  tarPause('10-seconds'  ): pause =    10
	elif  tarPause('30-seconds'  ): pause =    30
	elif  tarPause('60-seconds'  ): pause =    60
	elif  tarPause('2-minutes'   ): pause =   120
	elif  tarPause('5-minutes'   ): pause =   300
	elif  tarPause('10-minutes'  ): pause =   600
	elif  tarPause('20-minutes'  ): pause =  1200
	elif  tarPause('30-minutes'  ): pause =  1800
	elif  tarPause('1-hour'      ): pause =  3600
	elif  tarPause('5-hours'     ): pause = 18000
	return pause
	
def downloadTimeoutGet():
	timeout = 1800
	if    downloadTimeout('1-second'    ): timeout =     1
	elif  downloadTimeout('3-seconds'   ): timeout =     3
	elif  downloadTimeout('10-seconds'  ): timeout =    10
	elif  downloadTimeout('30-seconds'  ): timeout =    30
	elif  downloadTimeout('60-seconds'  ): timeout =    60
	elif  downloadTimeout('2-minutes'   ): timeout =   120
	elif  downloadTimeout('5-minutes'   ): timeout =   300
	elif  downloadTimeout('10-minutes'  ): timeout =   600
	elif  downloadTimeout('20-minutes'  ): timeout =  1200
	elif  downloadTimeout('30-minutes'  ): timeout =  1800
	elif  downloadTimeout('1-hour'      ): timeout =  3600
	elif  downloadTimeout('5-hours'     ): timeout = 18000
	return timeout

class Ask(Switch):
	def __call__(self,option,message):
		if self.always_on or option in self.useropts: return yesno(message)
		else:					      return 1

	def re(self,option,message):
		return Reason(message+' has been declined.',not self(option,message))
		
ask = Ask('ask', {                                                                                  \
	'cd':'             Ask before cd-ing to a new directory.',                                  \
	'ssh':'            Ask before executing a remote ssh command.',                             \
	'action':'         Ask before Pacman attempts any action defined in the language.',         \
	'shell':'          Ask before executing any Pacman shell command.',                         \
	'shell-all':'      Ask before executing any shell command.',                                \
	'shell-root':'     Ask before executing a shell command as root.',                          \
	'cu':'             Ask before changing usernames.',                                         \
	'up':'             Ask before updating a package.',                                         \
	'download':'       Ask before any download.',                                               \
	'env':'            Ask before modifying environment variables.',                            \
	'tar':'            Ask before tar operations.',                                             \
	'unzip':'          Ask before unzip operatinos.',                                           \
	'tar-overwrite':'  Ask permission before tar-overwriting (use with -allow tar-overwrite)',  \
	'mail':'           Ask before emailing.',                                                   \
	'http':'           Ask before downloading with http.',                                      \
	'gsi':'            Ask before executing each globus gsi operation',                         \
	'none':"           Don't ask permission before operations.",                                \
	'users':'          Ask before any user group or account operations.',                       \
	'package-add':'    Ask before adding a package to your installation.',                      \
	'restore':'        Ask before saving or restoring files.',                                  \
	'text-insert':'    Ask before inserting or removing lines from text files.',                \
	'registry':'       Ask before modifying the registry of symbolic cache names.',             \
	'retry':'          Ask before download retries.',                                           \
	'path':'           Ask before modifying path variables.',                                   \
	'pac':'            Ask before installing or uninstalling packages.',                        \
	'cache':'          Ask before determining cache properties.'                                \
} )

def dots(obj):
	s = `obj`
	if s[-3]=='...': print s
	else:            print s+'...'

def rpm_replace(rpm_name):
	if rpm_installed(rpm_name): 
		if switch('force-rpm'): return 1
		elif yesno('Package ['+rpm_name+'] is already installed.  Do you want to replace it?'): return 1
		else: return 0
	else: return 1
		
def deWhite(s):
	ss = string.strip(s)
	return ss
	
def deWhiten(s): return string.replace(s,' ','_')

def equivSlash(s,t):
	return s==t or (len(s)>1 and s[:-1]==t) or (len(t)>1 and s==t[:-1])		

def fileify(s): return s.replace('/','_').replace(':','_').replace('@','_AT_').replace(' ','_').replace('~','_').replace('.','_')
def phash(s):
	import md5
	MD5 = md5.md5()
	MD5.update(s)
	return MD5.hexdigest()

def emptyDirR(path):
	e = 0
	try:
		e = forall(os.listdir(path),lambda f: os.path.isdir(os.path.join(path,f)) and emptyDirR(os.path.join(path,f)))
	except (IOError,OSError):
		e = 0
	return e

def dbpath(x):
	directory,base = os.path.split(x)
	base2 = base
	for fn in os.listdir(directory):
		if fn[:len(base)]==base: 
			base2 = fn[:]
			break
	return os.path.join(directory,base2)	


def gnuTarCheck():
	r = Reason()
	ok,tar = gnuTarFinder()
	if not ok and not allow('non-gnu-tar'): r = Reason("Can't find GNU tar your path (tar/gtar/gnutar checked).  GNU tar is required for Pacman.")
	return r

def gnuTarCheck_old():
	r = Reason()
	if not fileInPath('tar').ok(): r = Reason('[tar] is not in your path.')
	
	if r.ok() and not allow('non-gnu-tar'):
		status,output = commands.getstatusoutput('tar --version')
		if not status==0:
			r = Reason('The [tar] in your path is not GNU tar.')
		else:
			if allow('non-gnu-tar'): pass
			else:
				if output[:13]=='tar (GNU tar)': pass
				else:
					r = Reason('The [tar] in your path is not GNU tar.')
	return r
	
def gnuTarFinder():
	tarOK,gtarOK,gnutarOK = 0,0,0
	
	status,output = commands.getstatusoutput('tar --version')
	outOK = 'generic tar'
	if status==0 and output[:13]=='tar (GNU tar)': 
		tarOK = 1
		outOK = output[:]

	status,output = commands.getstatusoutput('gtar --version')
	if status==0 and output[:13]=='tar (GNU tar)': 
		gtarOK = 1
		outOK = output[:]
	
	status,output = commands.getstatusoutput('gnutar --version')
	if status==0 and output[:13]=='tar (GNU tar)': 
		gnutarOK = 1
		outOK = output[:]
	
	if       tarOK: tar = 'tar'
	elif    gtarOK: tar = 'gtar'
	elif  gnutarOK: tar = 'gnutar'
	else:           tar = 'tar'
	l = string.split(outOK,'\n')
	debug.log('tar','Using ['+l[0]+'].')
	return tarOK or gtarOK or gnutarOK,tar

def gnuTarName():
	tarname = 'tar'
	lines = []
	try:
		f = open(os.path.join(pac_anchor,pacmanDir,'tar'),'r')
		lines = f.readlines()
		f.close()
	except:
		lines = []
	if len(lines)>0 and len(lines[0])>1: 
		line = 	string.strip(lines[0][:-1])
		tarname = line
	return tarname

def bounds(x):
	s = string.strip(x)
	if   s=='one':          return 1,1
	elif s=='two':          return 2,2
	elif s=='three':        return 3,3
	elif s=='at most one':  return 0,1
	elif s=='one or more':  return 1,999999
	elif s=='at least one': return 1,999999
	elif s=='at most two':  return 0,2
	elif s=='any number':   return 0,999999
	else: abort('Unknown local or remote installation multiplicity ['+s+'].')

class NullFile:
	def write(self,x): pass
	def read(self,x): pass
	def close(self): pass
	
#
#  This section makes sure that Python's anydbm module (used by shelve) does not
#  use gdbm as it's default database if possible.
#
#import anydbm
#defaultdb = ''
#for _name in anydbm._names:
#	if not _name=='dumbdbm' and not _name=='gdbm':
#		try:
#			_mod = __import__(_name)
#			anydbm._defaultmod = _mod
#			defaultdb = _name
#		except ImportError:
#			continue
#	if not defaultdb=='': break
#

import pythonCheck
#use_old_database = allow('old-database') or (pythonCheck.defaultdb=='')
#use_old_database = 0
use_old_database = allow('old-database')

#if use_old_database and not os.path.exists(os.path.join(pac_anchor,pacmanDir)):
#	print '** Python database modules are not installed.  Using old Pacman database...'
#	print '** This may cause i/o problems if your installation area is NFS mounted.'

def localPathEqual(p1,p2):
	if os.path.isdir(p1) and (len(p1)==0 or not p1[-1]=='/'): t1 = p1+'/'
	else:                                                     t1 = p1
	if os.path.isdir(p2) and (len(p2)==0 or not p2[-1]=='/'): t2 = p2+'/'
	else:                                                     t2 = p2
	return t1==t2
	
def uname():
	status,output = commands.getstatusoutput('uname -a')
	u = []
	if status==0: 
		ok = 1
		u = string.split(output)
	else:
		ok = 0
	return ok,u

def fileExistsAndContains(path,text):
	q = 0
	try:
		f = open(path,'r')
		lines = f.readlines()
		f.close()
	except:
		lines = []
	for line in lines: 
		if contains(line,x): 
			q = 1; break
	return q

def askOnce(question,answer):
	while answer=='':
		x = raw_input(question)
		if   x=='y' or x=='yes': 
			x = 'y'; break
		elif x=='n' or x=='no':  
			x = 'n'; break
		elif x=='yall':          
			x = 'yall'; break
		else:
			print 'Choose y/n/yall.  Try again...'
	return x		
