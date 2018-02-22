#
#	Copyright, August 2003, Saul Youssef
#
from Environment import *
from Execution   import *

class RPM(Environment):
	type   = 'rpm'
	title  = 'RPMs'
	action = 'install rpm'
	
	def __init__(self,rpmfile): self.rpmfile = rpmfile
#-- Set
	def equal(self,r):  return self.rpmfile == r.rpmfile
	def str(self):      return self.rpmfile
	
#-- Compatible
	def compatible(self,r): return Reason()
	
#-- Satisfiable
	def satisfied(self):
		r = Reason('rpm ['+self.rpmfile+'] is not installed.',not rpm_installed(self.rpmfile))
		self.satset(r.ok())
		return r
			
	def _satisfiable(self):
		reason = Reason()
		if getusername()=='root':
			rpmTmp = self.rpmfile
			if not tail(rpmTmp,'.rpm'): rpmTmp += '.rpm'
			if switch('rpmcheck'): reason = execute('rpm --checksig '+rpmTmp)
		else:
			reason.reason('You must be root to install rpms.')
		return reason		
#-- Action
	def acquire(self):
		reason = self._satisfiable()
		if reason.ok(): 
			if rpm_replace(self.rpmfile):
				rpmTmp = self.rpmfile
				if not tail(rpmTmp,'.rpm'): rpmTmp += '.rpm'
				reason = execute('rpm -i --force '+rpmTmp)
		return reason
		
	def retract(self):
		rpmTmp = self.rpmfile
		if tail(rpmTmp,'.rpm'): rpmTmp = rpmTmp[:-4]
		return execute('rpm -e --nodeps '+rpmTmp)
	
