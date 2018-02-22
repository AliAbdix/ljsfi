#
#	Copyright, Saul Youssef, Dec. 2004
#
#       Added undocumented SOURCE for Nate.
#
from StringAttr import *
import os

class Setup(StringAttr):
	type   = 'setup'
	title  = 'Setup Commands'
	action = 'put command in setup.csh(sh)(bash)'
	
	def __init__(self,string): 
		self.value = string
	
	def shellOut(self,csh,sh,py,pl,ksh):
		if self.acquired:
			cshtxt = string.replace(string.replace(self.value,'SHELL','csh'),'SOURCE','source')
			shtxt  = string.replace(string.replace(self.value,'SHELL','sh'),'SOURCE','.')
			shtxt  = string.replace(shtxt,'source ','. ')
			csh.write (cshtxt +'\n')
			sh. write ( shtxt +'\n')
			ksh.write ( shtxt +'\n')
		
	def satisfied(self):
		return Reason('['+`self`+'] has not been established yet.',not self.acquired)
	def acquire(self):
		self.value = os.path.expandvars(self.value)
		return Reason()
	def retract(self): return Reason()
