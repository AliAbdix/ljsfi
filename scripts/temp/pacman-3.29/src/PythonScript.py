#
#	Copyright, Saul Youssef, October 2003.
#
from StringAttr import *

class PythonScript(StringAttr):
	type   =  'python script'
	title  =  'Python Scripts Imported'
	action =  'import python script'
	
	def satisfied(self): return Reason("["+`self`+"] has not been imported.",not self.acquired)
	def satisfiable(self): return Reason()
	def acquire(self): 
		reason = Reason()
		return reason
	def retract(self): return Reason()
	
