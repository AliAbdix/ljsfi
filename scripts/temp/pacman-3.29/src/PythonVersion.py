#
#	Copyright, Saul Youssef, August 2003
#
from StringAttr import *
import commands

def pythonversion():
	if fileInPath('python'):
		status,output = commands.getstatusoutput('python -V')
		if status==0:
			l = string.split(output,' ')
			if len(l)>1:
				if l[0]=='Python': return l[1]
				else: 
					return '- unknown python version -'
			else: 
				return '- unknown python version -'
		else: 
			return '- unknown python version < 2.0 -'
	else:
		return '- no python in $path -'

class PythonVersion(StringAttr):
	type   = 'python version'
	title  = 'Python Versions'
	action = 'python version'
			
	def str(self): return 'must be equal to ['+self.value+'], actually ['+pythonversion()+'].'
	def satisfied(self): return Reason('['+self.str()+'] has not been tested yet.',not self.acquired)
#	def satisfied  (self): 
	def acquire  (self): 
		pv = pythonversion()
		if pv=='- no python in $path -':
			r = Reason("[python] is not in the installer's path.")
		else:
			r = Reason('python version is ['+pythonversion()+']. It must be ['+self.value+'].',not pythonversion() == self.value)	
		self.satset(r.ok())
		return r
#	def satisfiable(self): return self.satisfied()	
	def satisfiable(self): return Reason()

#	def acquire(self): return self.satisfied()
#	def restore(self): return Reason()
	def retract(self): return Reason()
	
class PythonVersionLE(PythonVersion):
	type   = 'python version <='
	title  = 'python version <=s'
	action = 'python version <='
	
	def str(self): return '['+self.value+'], actually ['+pythonversion()+'].'
#	def satisfied(self): 
	def acquire(self): 
		pv = pythonversion()
		if pv=='- no python in $path -':
			r = Reason("[python] is not in the installer's path.")
		else:
			r = Reason('python version ['+pythonversion()+'] must be <= ['+self.value+'].',not pythonversion() <= self.value) 
		self.satset(r.ok())
		return r
	
class PythonVersionLT(PythonVersion):
	type   = 'python version <'
	title  = 'python version <s'
	action = 'python version <'
	
	def str(self): return '['+self.value+'], actually ['+pythonversion()+'].'
#	def satisfied(self):
	def acquire(self):
		pv = pythonversion()
		if pv=='- no python in $path -':
			r = Reason("[python] is not in the installer's path.")
		else:
 			r = Reason('python version ['+pythonversion()+'] must be < ['+self.value+'].',not pythonversion() < self.value) 
		self.satset(r.ok())
		return r
	
class PythonVersionGE(PythonVersion):
	type   = 'python version >='
	title  = 'python version >=s'
	action = 'python version >='
	
	def str(self): return '['+self.value+'], actually ['+pythonversion()+'].'
#	def satisfied(self): 
	def acquire(self): 
		pv = pythonversion()
		if pv=='- no python in $path -':
			r = Reason("[python] is not in the installer's path.")
		else:
			r = Reason('python version ['+pythonversion()+'] must be >= ['+self.value+'].',not pythonversion() >= self.value) 
		self.satset(r.ok())
		return r
	
class PythonVersionGT(PythonVersion):
	type   = 'python version >'
	title  = 'python version >s'
	action = 'python version >'
	
	def str(self): return '['+self.value+'], actually ['+pythonversion()+'].'
#	def satisfied(self): 
	def acquire(self): 
		pv = pythonversion()
		if pv=='- no python in $path -':
			r = Reason("[python] is not in the installer's path.")
		else:
			r = Reason('python version ['+pythonversion()+'] must be > ['+self.value+'].',not pythonversion() > self.value) 
		self.satset(r.ok())
		return r
