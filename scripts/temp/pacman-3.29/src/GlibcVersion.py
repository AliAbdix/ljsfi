
#	Copyright, Saul Youssef, August 2003
#
from StringAttr import *
import Execution
import commands,os,string

def glibcversion(): 
	v = ''
	if not os.path.exists(os.path.join(pac_anchor,pacmanDir,'glibcversion')):
		try:
			f = open(os.path.join(pac_anchor,pacmanDir,'glibcversion.c'),'w')
			f.write('#include <stdio.h>\n')
			f.write('#include <gnu/libc-version.h>\n')
			f.write('int main (void) { puts (gnu_get_libc_version()); return 0; }\n')
			f.close()
			r = Execution.execute('cd '+os.path.join(pac_anchor,pacmanDir)+'; gcc glibcversion.c')
			if r.ok(): r = Execution.execute('cd '+os.path.join(pac_anchor,pacmanDir)+'; ./a.out > glibcversion')
			removeFiles(os.path.join(pac_anchor,pacmanDir,'a.out'),os.path.join(pac_anchor,pacmanDir,'glibcversion.c'))
		except (IOError,OSError):
			removeFiles(os.path.join(pac_anchor,pacmanDir,'a.out'),os.path.join(pac_anchor,pacmanDir,'glibcversion.c'))

	try:
		f = open(os.path.join(pac_anchor,pacmanDir,'glibcversion'),'r')
		line = f.readline()
		f.close()
		if len(line)>1: v = string.strip(line[:-1])
	except (IOError,OSError):
		pass
	return v

class GlibcVersion(StringAttr):
	type   = 'glibc version'
	title  = 'Glibc Versions'
	action = 'glibc version'
			
	def __init__(self,value=glibcversion()):
		self.value = value
			
	def str(self): return 'must be equal to ['+self.value+'], actually ['+glibcversion()+'].'
	
	def satisfied  (self): 
		pv = glibcversion()
		if pv=='':
			r = Reason("gcc is not available in your path.")
		else:
			r = Reason('glibc version is ['+glibcversion()+']. It must be ['+self.value+'].',not glibcversion() == self.value)
		self.satset(r.ok())
		return r
#	def satisfiable(self): return self.satisfied()	

	def acquire(self): 
		r = self.satisfied()
		self.satset(r.ok())
		return r
	def retract(self): return Reason()	
	
class GlibcVersionLE(GlibcVersion):
	type   = 'glibc version <='
	title  = 'glibc version <=s'
	action = 'glibc version <='
	
	def str(self): return '['+self.value+'], actually ['+glibcversion()+'].'
	def satisfied(self): 
		pv = glibcversion()
		if pv=='':
			r = Reason("gcc is not available in your path.")
		else:
			r = Reason('glibc version ['+glibcversion()+'] must be <= ['+self.value+'].',not glibcversion() <= self.value) 
		self.satset(r.ok())
		return r
	
class GlibcVersionLT(GlibcVersion):
	type   = 'glibc version <'
	title  = 'glibc version <s'
	action = 'glibc version <'
	
	def str(self): return '['+self.value+'], actually ['+glibcversion()+'].'
	def satisfied(self):
		pv = glibcversion()
		if pv=='':
			r = Reason("gcc is not available in your path.")
		else:
 			r = Reason('glibc version ['+glibcversion()+'] must be < ['+self.value+'].',not glibcversion() < self.value) 
		self.satset(r.ok())
		return r
	
class GlibcVersionGE(GlibcVersion):
	type   = 'glibc version >='
	title  = 'glibc version >=s'
	action = 'glibc version >='
	
	def str(self): return '['+self.value+'], actually ['+glibcversion()+'].'
	def satisfied(self): 
		pv = glibcversion()
		if pv=='':
			r = Reason("gcc is not available in your path.")
		else:
			r = Reason('glibc version ['+glibcversion()+'] must be >= ['+self.value+'].',not glibcversion() >= self.value) 
		self.satset(r.ok())
		return r
	
class GlibcVersionGT(GlibcVersion):
	type   = 'glibc version >'
	title  = 'glibc version >s'
	action = 'glibc version >'
	
	def str(self): return '['+self.value+'], actually ['+glibcversion()+'].'
	def satisfied(self): 
		pv = glibcversion()
		if pv=='':
			r = Reason("gcc is not available in your path.")
		else:
			r = Reason('glibc version ['+glibcversion()+'] must be > ['+self.value+'].',not glibcversion() > self.value) 
		self.satset(r.ok())
		return r
