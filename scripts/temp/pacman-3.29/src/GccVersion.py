#
#	Copyright, Saul Youssef, August 2003
#
from StringAttr import *
import commands,platform23

class GccBinaryEQ(Environment):
	type   = 'gcc binary gcc version'
	title  = 'Gcc Binary Gcc Version'
	action = 'test the gcc version of a binary'
	
	def __init__(self,path,gccversion):
		self._path = path
		self._gccversion = gccversion
		self._pathgccversion = ''
		
	def __repr__(self): return self.str()
	def str(self):
		if self.lastsat or self.lastfail:
			s = 'file '+self._path+' was made with gcc version '+self._pathgccversion+' must be '+self.type+' '+self._gccversion
		else:
			s = 'file '+self._path+' must be '+self.type+' '+self._gccversion
		return s
	
	def equal(self,x): return self._path==x._path and self._gccversion==x._gccversion
		
	def getReason(self,comp): return Reason('Binary ['+self._path+'] was not compiled with gccvesion ['+self._gccversion+'].',not comp==self._gccversion)
		
	def satisfied(self): return Reason('['+`self`+'] has not yet been tested.',not self.acquired)
	def acquire(self):
		r = Reason()
		self._path = fullpath(self._path)
		
		if os.path.exists(self._path):
			try:
				comp,self._pathgccversion = platform23.libc_ver(self._path)
			except (OSError,IOError):
				r = Reason('Error examining ['+self._path+'].')
			r = Reason("Binary ["+self._path+"] was not compiled with gcc.",not comp=='glibc')
			if r.ok(): r = self.getReason(comp)
		else:
			r = Reason('Binary ['+self._path+'] does not exist.')
		return r
		
	def retract(self):return Reason()

class GccBinaryLE(GccBinaryEQ):
	type  = 'gcc binary gcc version <='
	title = 'Gcc Binary Gcc Version <='
	action = 'test the gcc version of a binary <='
	
	def getReason(self,comp): return Reason('Binary ['+self._path+'] was not compiled with gccvesion <= ['+self._gccversion+'].',not comp<=self._gccversion)

class GccBinaryLT(GccBinaryEQ):
	type  = 'gcc binary gcc version <'
	title = 'Gcc Binary Gcc Version <'
	action = 'test the gcc version of a binary <'
	
	def getReason(self,comp): return Reason('Binary ['+self._path+'] was not compiled with gccvesion < ['+self._gccversion+'].',not comp<self._gccversion)

class GccBinaryGE(GccBinaryEQ):
	type  = 'gcc binary gcc version >='
	title = 'Gcc Binary Gcc Version >='
	action = 'test the gcc version of a binary >='
	
	def getReason(self,comp): return Reason('Binary ['+self._path+'] was not compiled with gccvesion >= ['+self._gccversion+'].',not comp>=self._gccversion)

class GccBinaryGT(GccBinaryEQ):
	type  = 'gcc binary gcc version >'
	title = 'Gcc Binary Gcc Version >'
	action = 'test the gcc version of a binary >'
	
	def getReason(self,comp): return Reason('Binary ['+self._path+'] was not compiled with gccvesion > ['+self._gccversion+'].',not comp >self._gccversion)

def gccversion():
	if fileInPath('gcc'):
		status,output = commands.getstatusoutput('gcc -v')
		if status==0:
			l = string.split(output,' ')
			got_one = 0
			count = 0
			for ll in l:
				if ll=='version':
					got_one = 1
					break
				count = count + 1
			if got_one and count+1<len(l): return l[count+1]
			else:                          return '- unknown gcc version -'
		else:
			return '- gcc unavailable -'
	else:
		return '- no gcc in $path -'

class GccVersion(StringAttr):
	type   = 'gcc version'
	title  = 'Gcc Versions'
	action = 'gcc version'
			
	def str(self): return 'must be equal to ['+self.value+'], actually ['+gccversion()+'].'
	def satisfied  (self): 
		pv = gccversion()
		if pv=='- no gcc in $path -':
			return Reason("[gcc] is not in the installer's path.")
		else:
			if gccversion()==self.value:
				self.lastsat = 1
				self.lastfail = 0
				return Reason()
			else:
				self.lastsat = 0
				self.lastfail = 1
				return Reason('gcc version is ['+gccversion()+']. It must be ['+self.value+'].')
#	def satisfiable(self): return self.satisfied()	

	def acquire(self): return self.satisfied()
	def retract(self): return Reason()	
	
class GccVersionLE(GccVersion):
	type   = 'gcc version <='
	title  = 'gcc version <=s'
	action = 'gcc version <='
	
	def str(self): return '['+self.value+'], actually ['+gccversion()+'].'
	def satisfied  (self): 
		pv = gccversion()
		if pv=='- no gcc in $path -':
			return Reason("[gcc] is not in the installer's path.")
		else:
			if gccversion()<=self.value:
				self.lastsat = 1
				self.lastfail = 0
				return Reason()
			else:
				self.lastsat = 0
				self.lastfail = 1
				return Reason('gcc version is ['+gccversion()+']. It must be <= ['+self.value+'].')
	
class GccVersionLT(GccVersion):
	type   = 'gcc version <'
	title  = 'gcc version <s'
	action = 'gcc version <'
	
	def str(self): return '['+self.value+'], actually ['+gccversion()+'].'
	def satisfied  (self): 
		pv = gccversion()
		if pv=='- no gcc in $path -':
			return Reason("[gcc] is not in the installer's path.")
		else:
			if gccversion()<self.value:
				self.lastsat = 1
				self.lastfail = 0
				return Reason()
			else:
				self.lastsat = 0
				self.lastfail = 1
				return Reason('gcc version is ['+gccversion()+']. It must be < ['+self.value+'].')
	
class GccVersionGE(GccVersion):
	type   = 'gcc version >='
	title  = 'gcc version >=s'
	action = 'gcc version >='
	
	def str(self): return '['+self.value+'], actually ['+gccversion()+'].'
	def satisfied  (self): 
		pv = gccversion()
		if pv=='- no gcc in $path -':
			return Reason("[gcc] is not in the installer's path.")
		else:
			if gccversion()>=self.value:
				self.lastsat = 1
				self.lastfail = 0
				return Reason()
			else:
				self.lastsat = 0
				self.lastfail = 1
				return Reason('gcc version is ['+gccversion()+']. It must be >= ['+self.value+'].')
	
class GccVersionGT(GccVersion):
	type   = 'gcc version >'
	title  = 'gcc version >s'
	action = 'gcc version >'
	
	def str(self): return '['+self.value+'], actually ['+gccversion()+'].'
	def satisfied  (self): 
		pv = gccversion()
		if pv=='- no gcc in $path -':
			return Reason("[gcc] is not in the installer's path.")
		else:
			if gccversion()>self.value:
				self.lastsat = 1
				self.lastfail = 0
				return Reason()
			else:
				self.lastsat = 0
				self.lastfail = 1
				return Reason('gcc version is ['+gccversion()+']. It must be > ['+self.value+'].')
