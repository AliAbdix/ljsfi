#
#	Copyright Saul Youssef, July 2003
#
from Environment import *
from Base        import *

class True(Environment):
	type   = 'true'
	title  = 'True'
	action = 'true'
	
	def __init__(self):
		self.lastsat  = 1
		self.lastfail = 0
#-- Set
	def equal(self,n):  return 1
	def str(self): return ''
	def __repr__(self): return 'true'

#-- Action
	def satisfied(self): return Reason("True hasn't been tested.",not self.acquired)
	def satisfiable(self): return Reason()
	def acquire(self): return Reason()
	def retract(self): return Reason()
	
#	def satisfied  (self): return Reason()
#	def satisfiable(self): return Reason()
	
#-- SatisfyOrder
	def satisfies(self,x): return self==x

class False(Environment):
	type   = 'false'
	title  = 'False'
	action = 'false'
	
	def __init__(self):
		self.lastsat = 0
		self.lastfail = 1
	
	def equal(self,n): return 1
	def str(self): return ''
	
	def satisfied(self): return Reason('False cannot be satisfied.')
	def satisfiable(self): return self.satisfied()
	
	def satisfies(self,x): return self==x
	
 
