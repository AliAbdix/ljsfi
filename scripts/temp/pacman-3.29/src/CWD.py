#
#	Copyright, Saul Youssef, January 2005
#
from Environment  import *
from StringAttr   import *

class CWD(Environment):
	type   = 'cwd'
	title  = 'CWDs'
	action = 'show cwd'
	
	def __init__(self): 
		self.acquired = 0
		self.cwd = '- unset -'
#-- Set
	def  equal(self,c): return self.cwd == c.cwd
	def  str(self):     return self.cwd
	
#-- Compatible 
	def compatible(self,c): return Reason()
	
#-- Satisfiable
	def satisfied (self): 
		if self.acquired: return Reason()
		else:             return Reason('CWD not evaluated.')
	def satisfiable(self): return Reason()
	
#-- Action
	def acquire(self):
		self.cwd = os.getcwd()
		return Reason()
	def retract(self):
		self.cwd = '- unset -'
		return Reason()
		
class CWDCheck(StringAttr):
	type   = 'check cwd'
	title  = 'Check CWDs'
	action = 'check cwd'
	
	def satisfied  (self): return Reason("CWD is not ["+self.value+"].",not fullpath(self.value)==cwdd())
	def satsifiable(self): return Reason()
	def satisfy    (self): return self.satisfied()
	def restore    (self): return Reason()

class Location(CWD):
	type   = 'location'
	title  = 'Installation Locations'
	action = 'locate'
	
class SetCWD(Environment):
	type   = 'setcwd'
	title  = 'SetCWD'
	action = 'set cwd'
	
	def __init__(self,location): self.location = location
	def str(self): return self.location
	def equal(self,x): return self.location==x.location
	
	def satisfied (self): 
		if self.acquired: return Reason()
		else:             return Reason('Installation contains uninstalled packages.  See % pacman -lc.')
#	def satisfied(self): return Reason("CWD has not been set.",not self.acquired)
	def satisfiable(self): return Reason()
	def acquire(self):
		reason = Reason()
		try:
			self.location = fullpath(self.location)
			os.chdir(self.location)
		except (OSError,IOError):
			reason = Reason("Can't set directory to ["+self.location+"].")
		return reason
	def retract(self):
		reason = Reason()
		if os.path.isdir(self.location):
			try:
				os.chdir(self.location)
			except (OSError,IOError):
				reason = Reason("Can't set directory to ["+self.location+"].")
		return reason
