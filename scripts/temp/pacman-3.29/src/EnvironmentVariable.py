#
#	Copyright Saul Youssef, April 2004
#
import os
from Environment import *
from StringAttr  import *
import Pookie

class Unsetenv(Environment):
	type   = 'unsetenv'
	title  = 'Unsetenvs'
	action = 'unsetenv'

	def __init__(self,env):
		self.value   = env
		self._retract = '- unset -'
	def str(self): 
		if self._retract=='- unset -': return self.value
		else:                  return self.value+' restore to '+self._retract
	def equal(self,x): return self.value==x.value and self._retract==x._retract

	def satisfied   (self): return Reason('['+`self`+'] has not been executed.',not self.acquired)
	def satisfiable (self): return Reason()
	def setup       (self): return self.satisfy()
	def acquire     (self): 
		reason = Reason()
		if os.environ.has_key(self.value):
			verbo.log('env','About to unset ['+self.value+' => '+os.environ[self.value]+']...')
			reason = ask.re('env','OK to unset ['+self.value+' => '+os.environ[self.value]+']?')
			if reason.ok():
				self._retract = os.environ[self.value]
				del os.environ[self.value]
		return reason
	def retract     (self):
		reason = Reason()
		if self._retract!='- unset -':
			if os.environ.has_key(self.value):
				reason = Reason("Can't restore environment variable.")
			else:
				verbo.log('env','Restoring ['+self.value+' => '+self._retract+']...')
				reason = ask.re('env','OK to restore ['+self.value+' => '+self._retract+']?')
				if reason.ok():
					os.environ[self.value] = self._retract
					self._retract = '-'
		return reason		

class Env(Environment):
	type   = 'environment variable'
	title  = 'Environment Variables'
	action = 'record environment variable'
	
	def __init__(self,name): 
		self.name = name
		self.valu = '- unset -'

	def equal(self,x): return self.name == x.name
	
	def eval(self):
		if os.environ.has_key(self.name): return os.environ[self.name]
		else:                             return '- unset -'

	def str(self): return self.name+' => '+self.eval()
	
	def satisfiable(self): return Reason()
	def satisfied  (self): return Reason('['+self.name+'] has not been tested.',not self.acquired)
	def acquire    (self): 
		self.valu = self.eval()
		return Reason()
	def retract    (self): 
		self.valu = '- unset -'
		return Reason()
		
	def shellOut(self,csh,sh,py,pl,ksh):
		if self.acquired:
			csh.write('setenv '+self.name+' "'+self.valu+'"\n')
			sh.write(self.name+'="'+self.valu+'"\n')
			sh.write('export '+self.name+'\n')
			py.write('os.environ["'+self.name+'"] = "'+self.valu+'"\n')
			pl.write('$ENV{"'+self.name+'"} = "'+self.valu+'";\n')
			ksh.write(self.name+'="'+self.valu+'"\n')
			ksh.write('export '+self.name+'\n')
	
class EnvIsSet(Env):
	type   = 'environment variable is set'
	title  = 'Environment Variables Set'
	action = 'test if environment variable is set'
	
	def satisfiable(self): return Reason()
	def satisfied  (self): return Reason('Environment variable ['+self.name+'] has not been tested.',not self.acquired)
	def acquire    (self): return Reason('Environment variable ['+self.name+'] has not been set.',self.eval()=='- unset -')
	def retract    (self): return Reason()
	def shellOut(self,csh,sh,py,pl,ksh): pass
		
class EnvHasValue(EnvIsSet):
	type   = 'environment variable set to'
	title  = 'Environment Variables Set To Particular Values'
	action = 'test if environment variable has a particular value'
	
	def __init__(self,name,value='',query=''):
		self.name = name
		self.valu = value
		self._query = query
		
	def evalval(self):
		if   self.valu=='.': 
			val = fullpath('.')
		elif self.valu== '':
			if switch('ignore-cookies'):
				val = raw_input('Choose a value for ['+self.name+']: ')
			elif self._query=='': 
				c = Pookie.CookieQuestion('Choose a value for ['+self.name+']',lambda x: x)
				val = c.answer()
			else:
				c = Pookie.CookieQuestion(self._query,lambda x: x)
				val = c.answer()
		else:              
			val = self.valu
		return os.path.expandvars(os.path.expanduser(val))

	def str(self): return self.name+' => '+self.valu
	
	def satisfiable(self): return Reason()
	def satisfied  (self): 
		reason = Reason()
		if self.acquired: 
			if os.environ.has_key(self.name):
#				reason = Reason()
				reason = Reason('The value of ['+self.name+'='+os.environ[self.name]+'] has not been set to ['+self.valu+'].',not self.valu==os.environ[self.name] )
			else:
				reason = Reason('Environment variable ['+self.name+'] is no longer set.')
		else: 
			reason = Reason("The value of ["+self.name+"] hasn't been compared to ["+self.valu+"] yet.")
		return reason
	def setup      (self): return self.satisfy()
	def acquire    (self): 
		reason = Reason()
		self.valu = os.path.expandvars(self.valu)
		if os.environ.has_key(self.name):
			if os.environ[self.name]==self.valu: pass
#				self.valu = fullpath(self.valu)
			else:
				reason = Reason("Environment variable ["+self.name+'='+os.environ[self.name]+"] is not equal to ["+fullpath(self.valu)+"].")
		else:
			reason = Reason("Environment variable ["+self.name+"] hasn't been set.")			
		return reason
	def retract    (self): return Reason()
	def shellOut(self,csh,sh,py,pl,ksh):
		if self.acquired:
			csh.write('setenv '+self.name+' "'+self.valu+'"\n')
			sh.write(self.name+'="'+self.valu+'"\n')
			sh.write('export '+self.name+'\n')
			py.write('os.environ["'+self.name+'"] = "'+self.valu+'"\n')
			pl.write('$ENV{"'+self.name+'"} = "'+self.valu+'";\n')
			ksh.write(self.name+'="'+self.valu+'"\n')
			ksh.write('export '+self.name+'\n')
	
class EnvHasValueTemp(EnvHasValue):
	def satisfied(self): return Reason('['+self.name+' => '+self.valu+'] has not been tested.',not self.acquired)
	def shellOut(self,csh,sh,py,pl,ksh): pass

class Setenv(EnvHasValue):
	type   = 'setenv'
	title  = 'Set Environment Variables'
	action = 'set environment variable'
	
	def acquire(self):
		self.old = Env(self.name)
		self.old.satisfy().require()
		
		val = self.evalval()
		verbo.log('env','About to set ['+self.name+'] to value ['+val+']...')
		reason = ask.re('env','OK to set ['+self.name+'] to value ['+val+']?')
		if reason.ok(): 
			os.environ[self.name] = val
			self.valu = os.environ[self.name]
		return reason
		
	def retract(self):
		reason = Reason()
		if self.old.valu == '- unset -': 
			verbo.log('env','About to unset environment variable ['+self.name+']...')
			if os.environ.has_key(self.name): 
				reason = ask.re('env','OK to unset environment variable ['+self.name+']?')
				if reason.ok(): del os.environ[self.name]
		else:       
			verbo.log('env','About to restore ['+self.name+'] to ['+self.old.valu+']...')
			reason = ask.re('env','OK to restore ['+self.name+'] to ['+self.old.valu+']?')
			if reason.ok():  os.environ[self.name] = self.old.valu
		return reason
	def shellOut(self,csh,sh,py,pl,ksh):
		if self.acquired:
			csh.write('setenv '+self.name+' "'+self.valu+'"\n')
			sh.write(self.name+'="'+self.valu+'"\n')
			sh.write('export '+self.name+'\n')
			py.write('os.environ["'+self.name+'"] = "'+self.valu+'"\n')
			pl.write('$ENV{"'+self.name+'"} = "'+self.valu+'";\n')
			ksh.write(self.name+'="'+self.valu+'"\n')
			ksh.write('export '+self.name+'\n')
		
class SetenvTemp(Setenv):
	type   = 'setenv temporary'
	title  = 'Temporary Environment Variable'
	action = 'setenv temporary'
	
	def satisfied(self): return Reason('['+self.name+' => '+self.valu+'] has not been set.',not self.acquired)
	def shellOut(self,csh,sh,py,pl,ksh): pass

