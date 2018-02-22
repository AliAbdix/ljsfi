#
#	Copyright, Saul Youssef, September, 2003
#
from StringAttr import *
import commands,sys

def linuxkernelversion():
	if string.count(sys.version,'Red Hat Linux')>0:
		l = string.split(sys.version,'Red Hat Linux')
		ll = string.split(l[-1],' ')
		x = ll[-1]
		y = ''
		while len(x)>0:
			if x[0]==')' or x[0]=='(' or x[0]==']' or x[0]=='[':
				x = x[1:]
			else:
				y = y + x[0]
				x = x[1:]
		return y
	else:
		return '- not a linux system -'

class LinuxKernel(StringAttr):
	type   = 'Linux kernel'
	title  = 'Python Versions'
	action = 'Linux kernel'
			
	def str(self): return 'must be equal to ['+self.value+'], actually ['+linuxkernelversion()+'].'
	def satisfied  (self): 
		pv = linuxkernelversion()
		if pv=='- no python in $path -':
			return Reason("[python] is not in the installer's path.")
		else:
			return Reason('Linux kernel is ['+linuxkernelversion()+']. It must be ['+self.value+'].',not linuxkernelversion() == self.value)	
#	def satisfiable(self): return self.satisfied()	

	def acquire(self): return self.satisfied()
	def retract(self): return self.satisfied()
	
class LinuxKernelLE(LinuxKernel):
	type   = 'Linux kernel <='
	title  = 'Linux kernel <=s'
	action = 'Linux kernel <='
	
	def str(self): return '['+self.value+'], actually ['+linuxkernelversion()+'].'
	def satisfied(self): 
		pv = linuxkernelversion()
		if pv=='- no python in $path -':
			return Reason("[python] is not in the installer's path.")
		else:
			return Reason('Linux kernel ['+linuxkernelversion()+'] must be <= ['+self.value+'].',not linuxkernelversion() <= self.value) 
	
class LinuxKernelLT(LinuxKernel):
	type   = 'Linux kernel <'
	title  = 'Linux kernel <s'
	action = 'Linux kernel <'
	
	def str(self): return '['+self.value+'], actually ['+linuxkernelversion()+'].'
	def satisfied(self):
		pv = linuxkernelversion()
		if pv=='- no python in $path -':
			return Reason("[python] is not in the installer's path.")
		else:
 			return Reason('Linux kernel ['+linuxkernelversion()+'] must be < ['+self.value+'].',not linuxkernelversion() < self.value) 
	
class LinuxKernelGE(LinuxKernel):
	type   = 'Linux kernel >='
	title  = 'Linux kernel >=s'
	action = 'Linux kernel >='
	
	def str(self): return '['+self.value+'], actually ['+linuxkernelversion()+'].'
	def satisfied(self): 
		pv = linuxkernelversion()
		if pv=='- no python in $path -':
			return Reason("[python] is not in the installer's path.")
		else:
			return Reason('Linux kernel ['+linuxkernelversion()+'] must be >= ['+self.value+'].',not linuxkernelversion() >= self.value) 
	
class LinuxKernelGT(LinuxKernel):
	type   = 'Linux kernel >'
	title  = 'Linux kernel >s'
	action = 'Linux kernel >'
	
	def str(self): return '['+self.value+'], actually ['+linuxkernelversion()+'].'
	def satisfied(self): 
		pv = linuxkernelversion()
		if pv=='- no python in $path -':
			return Reason("[python] is not in the installer's path.")
		else:
			return Reason('Linux kernel ['+linuxkernelversion()+'] must be > ['+self.value+'].',not linuxkernelversion() > self.value) 
