#
#	Copyright, August 2003, Saul Youssef
#
from RPM import *

class RPMinstalled(RPM):
	type   = 'check if rpm installed'
	title  = 'RPMs installed'
	action = 'check if rpm installed'
	
	def __init__(self,rpmfile): self.rpmfile = rpmfile

#-- Satisfiable
#	def satisfiable(self): return self.satisfied()

	def satisfied(self): 
		return Reason("Testing if rpm ["+self.rpmfile+"] has been installed hasn't been performed yet.",not self.acquired)
	def acquire(self):
		r = Reason()
		if not rpm_installed(self.rpmfile): r = Reason("rpm ["+self.rpmfile+"] has not been installed.")
		return r
	def retract(self): return Reason()
