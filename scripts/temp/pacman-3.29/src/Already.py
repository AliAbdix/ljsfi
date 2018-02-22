#
#	Copyright, Saul Youssef, November 2004
#
from Base        import *
from Environment import *

import StringAttr,UniversalCache,Package

class AlreadyInstalled(StringAttr.StringAttr):
	type   = 'already installed package'
	title  = 'Already Installed Package'
	action = 'check for an already installed package'
	
	def satisfied(self):
		r = Reason()
		home = UniversalCache.UniversalCache('home')
		r,p = home.get(Package.Spec(self.value))
		if r.ok(): 
			if p.lastfail: 
				r = Reason('Package ['+p.str()+'] is present but failed to install.')
			elif not p.lastsat:
				r = Reason('Package ['+p.str()+'] is fetched but has not been installed.')
		else:
			r = Reason('Package ['+self.value+'] is not already installed.')
		return r

	def satisfiable(self): return self.satisfied()
	def acquire    (self): return self.satisfied()
	def retract    (self): return Reason()
