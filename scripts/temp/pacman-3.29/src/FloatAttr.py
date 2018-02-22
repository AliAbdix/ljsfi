#
#	Copyright Saul Youssef, July 2003
#
from Environment import *
from Base        import *

class FloatAttr(Environment):
	type   = 'float attribute'
	title  = 'Float Attributes'
	action = 'float attribute'
	def __init__(self,floatval): self.value   = floatval
	
#-- Set
	def equal(self,n):  return self.value == n.value
	def str(self): return `self.value`

#-- SatisfyOrder
	def satisfies(self,x): return self==x
