#
#	Copyright Saul Youssef, July 2003
#
from Environment import *
from Base        import *

class IntAttr(Environment):
	type   = 'integer attribute'
	title  = 'Integer Attributes'
	action = 'integer attribute'
	def __init__(self,intval): self.value   = intval
	
#-- Set
	def equal(self,n):  return self.value == n.value
	def str(self): return `self.value`

#-- Satisfied
	def satisfied  (self): return Reason()
	def satisfiable(self): return Reason()
	
#-- SatisfyOrder
	def satisfies(self,x): return self==x
