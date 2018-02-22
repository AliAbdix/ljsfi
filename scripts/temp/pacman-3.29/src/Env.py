#
#	Copyright Saul Youssef, June 2003
#
from StringAttr import *

class Env(StringAttr):
	type   = 'env set'
	title  = 'Environment Variables Set'
	action = 'check if env is set'
	
	def str(self):
		if os.environ.has_key(self.value): return self.value+'='+os.environ[self.value]
		else:                              return self.value+'='+'- unset -'

#-- Satisfiable
	def satisfied(self): 
		return Reason('Environment variable ['+self.env+'] has not been set.',not os.environ.has_key(self.value))
	def satisfiable(self): return Reason()
	def acquire    (self): return self.satisfied()
	def retract    (self): return self.satisfied()	
#
#   tests whether an environment variable has been set ( Env(env) ) or whether it has been set to a particular value
#   Env(env,value).
#
class Env(Environment):
	type   = 'env'
	title  = 'Environment Variables Set'
	action = 'check environment variable value'
	
	def __init__(self,env,value=''):
		self.env = env
		self.value = value
		
	def str(self): 
		if self.value=='': 
			if os.environ.has_key(self.env): return self.env+' = '+os.environ[self.env]
			else:                            return self.env+' = '+'- unset -'
		else:
			if os.environ.has_key(self.env): 
				if os.environ[self.env]==self.value: return self.env+' = '+self.value
				else:                                return self.env+' != '+self.value
			else:
				return self.env+' = '+'- unset -'
	def equal(self,x):
		return self.env==x.env and self.value==x.value
		
	def satisfied(self):
		if os.environ.has_key(self.env):
			return Reason('['+`self`+'] does not have the prescribed value.',not self.value==os.environ[self.env])
		else:
			return Reason('['+`self`+'] has not been set.')
	def satisfiable(self): return Reason()
	def acquire    (self): return self.satisfied()
	def retract    (self): return Reason()
	
	
