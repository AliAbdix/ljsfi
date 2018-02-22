"""
Basic utility functions for Egg.

  - S.Y.
"""

import string

def none(x): return x.__class__ == None.__class__

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

def bubbleSort(l,le):
	got_one = 1
	while got_one:
		got_one = 0
		for i in range(len(l)-1):
			if not le(l[i],l[i+1]):
				temp = l[i+1]; l[i+1] = l[i]; l[i] = temp
				got_one = 1

def listStr(l,sep=','):
	p = []
	x = ''
	count = 0
	for ll in l: 
		count = count + 1
		x = x + `ll`
		if not count==len(l): x = x + sep
	return x

#def yesno(message):
#	while 1:
#		answer = raw_input(message+' (y or n): ')
#		if answer == 'y' or answer == 'yes' or answer == 'n' or answer == 'no': break
#	if answer == 'y' or answer == 'yes': return 1
#	return 0
	
class Yesno(object):
	def __init__(self): self._yall = False
	def __call__(self,message):
		if self._yall: return True
		else:
			while 1:
				answer = raw_input(message+' (y/n/yall): ')
				if answer in ['y','yes','n','no','yall']: break
			if answer=='yall': self._yall = True
			if    answer in ['yall','y','yes']: return True
			else                              : return False
	def yall(self): return self._yall	
yesno = Yesno()		

def getFile(path,exception=None):
	try:
		f = open(path,'r')
		x = f.read()
		f.close()
	except (IOError,OSError):
		if exception==None: x = ''
		else: raise exception
	return x
	
def getLines(path,exception=None):
	lines = []
	try:
		f = open(path,'r')
		lines = f.readlines()
		f.close()
		for i in range(len(lines)): lines[i] = lines[i][:-1]
	except (IOError,OSError):
		if exception==None: pass
		else: raise exception
	return lines
	
def putFile(path,x,exception=None):
	try:
		f = open(path,'w')
		f.write(x)
		f.close()
	except (IOError,OSError):
		if exception==None: pass
		else: raise exception

def remPath(path,exception=None):
	try:
		if os.isdir(path): os.removedirs(path)
		else:              os.remove    (path)
	except (IOError,OSError):
		if exception==None: pass
		else: raise exception

def tail(str,t):
	found = 0
	if len(str)>= len(t):
		if str[len(str)-len(t):len(str)]==t:
			found = 1
	return found
	
def relativePath(path):
	if ':' in path: rel = 0
	else:
		if len(path)>1 and path[0]=='/': rel = 0
		else:                            rel = 1
	return rel

def fileProperties(path):
	t = os.stat(path)

class Dio(object):
	def __init__(self,maxdepth=999999999):
		self.depth    = 0
		self.maxdepth = maxdepth
		self.maxlen   = 10
		self.maxwidth = 132
		self.indent   = 4
		assert maxdepth>=0
		
	def __str__(self): return `[self.depth,self.maxdepth,self.maxlen,self.maxwidth]`

	def inc(self): 
		self.depth = self.depth+1
		return self
		
	def pr(self,x):
		if self.depth<=self.maxdepth: 
			if forall(x,lambda xx: xx in string.printable): 
				s = (self.depth*self.indent)*' '+x
				if len(s)>self.maxwidth: print s[:self.maxwidth]+'...'
				else:                    print (self.depth*self.indent)*' '+x
			else:             
				print (self.depth*self.indent)*' '+'<not printable>'

	def done(self): return self.depth>=self.maxdepth

