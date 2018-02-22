#
#	Copyright Saul Youssef, October, 2003
#
from Environment import *
from Execution   import *

class SoftLink(Environment):
	type   = 'soft link'
	title  = 'Soft Links'
	action = 'soft link'
	
	def __init__(self,linkFrom,linkTo):
		self.linkFrom  = linkFrom
		self.linkTo    = linkTo
		
	def equal(self,x): return self.linkFrom==x.linkFrom and self.linkTo==x.linkTo
	def str(self): return self.linkFrom+' -> '+self.linkTo
	
	def satisfied(self): return Reason("Soft link ["+self.str()+"] has not been created.",not self.acquired)
	def satisfiable(self): return Reason()
	def acquire(self):
		reason = Reason()
		if os.path.exists(self.linkTo):
			reason = Reason("File ["+self.linkTo+"] exists.  Can't create link.")
		else:
			self.linkFrom = fullpath(self.linkFrom)
			self.linkTo   = fullpath(self.linkTo)
			reason = execute('ln -s '+self.linkFrom+' '+self.linkTo)
		return reason
	def retract(self): return execute('rm -f '+self.linkTo)
	

				
