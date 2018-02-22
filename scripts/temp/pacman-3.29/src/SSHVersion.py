#
#	Copyright, Saul Youssef, January 2004
#
from StringAttr import *
import commands

def sshversion():
	if fileInPath('ssh'):
		status,output = commands.getstatusoutput('ssh -V')
		if status==0:
			l = string.split(output,',')
			if len(l)>1: 
				ll = string.split(l[0],'_')
				if len(ll)>=2:
					return ll[1]
				else:
					return '- unknown ssh version -'
			else:
				return '- unknown ssh version -'
		else:
			return '- unknown ssh version -'
	else:
		return '- no ssh in $path -'
		

class SSHVersion(StringAttr):
	type   = 'ssh version'
	title  = 'Python Versions'
	action = 'ssh version'
			
	def str(self): return '['+self.value+'], actually ['+sshversion()+'].'
	def satisfied  (self): 
		pv = sshversion()
		if pv=='- no ssh in $path -':
			r = Reason("[ssh] is not in the installer's path.")
#			return Reason("[ssh] is not in the installer's path.")
		else:
			r = Reason('ssh version is ['+sshversion()+']. It must be ['+self.value+'].',not sshversion() == self.value)	
#			return Reason('ssh version is ['+sshversion()+']. It must be ['+self.value+'].',not sshversion() == self.value)	
		self.satset(r.ok())
		return r
	
	def satisfiable(self): return self.satisfied()	

	def acquire(self): return self.satisfied()
	def restore(self): return Reason()	
	
class SSHVersionLE(SSHVersion):
	type   = 'ssh version <='
	title  = 'ssh version <=s'
	action = 'ssh version <='
	
	def satisfied(self): 
		pv = sshversion()
		if pv=='- no ssh in $path -':
			r = Reason("[ssh] is not in the installer's path.")
#			return Reason("[ssh] is not in the installer's path.")
		else:
			r = Reason('ssh version ['+sshversion()+'] must be <= ['+self.value+'].',not sshversion() <= self.value) 
#			return Reason('ssh version ['+sshversion()+'] must be <= ['+self.value+'].',not sshversion() <= self.value) 
		self.satset(r.ok())
		return r
	
class SSHVersionLT(SSHVersion):
	type   = 'ssh version <'
	title  = 'ssh version <s'
	action = 'ssh version <'
	
	def satisfied(self):
		pv = sshversion()
		if pv=='- no ssh in $path -':
			r = Reason("[ssh] is not in the installer's path.")
#			return Reason("[ssh] is not in the installer's path.")
		else:
 			r = Reason('ssh version ['+sshversion()+'] must be < ['+self.value+'].',not sshversion() < self.value) 
# 			return Reason('ssh version ['+sshversion()+'] must be < ['+self.value+'].',not sshversion() < self.value) 
		self.satset(r.ok())
		return r
	
class SSHVersionGE(SSHVersion):
	type   = 'ssh version >='
	title  = 'ssh version >=s'
	action = 'ssh version >='
	
	def satisfied(self): 
		pv = sshversion()
		if pv=='- no ssh in $path -':
			r = Reason("[ssh] is not in the installer's path.")
#			return Reason("[ssh] is not in the installer's path.")
		else:
			r = Reason('ssh version ['+sshversion()+'] must be >= ['+self.value+'].',not sshversion() >= self.value) 
#			return Reason('ssh version ['+sshversion()+'] must be >= ['+self.value+'].',not sshversion() >= self.value) 
		self.satset(r.ok())
		return r
	
class SSHVersionGT(SSHVersion):
	type   = 'ssh version >'
	title  = 'ssh version >s'
	action = 'ssh version >'
	
	def satisfied(self): 
		pv = sshversion()
		if pv=='- no ssh in $path -':
			r = Reason("[ssh] is not in the installer's path.")
#			return Reason("[ssh] is not in the installer's path.")
		else:
			r = Reason('ssh version ['+sshversion()+'] must be > ['+self.value+'].',not sshversion() > self.value) 
#			return Reason('ssh version ['+sshversion()+'] must be > ['+self.value+'].',not sshversion() > self.value) 
		self.satset(r.ok())
		return r
