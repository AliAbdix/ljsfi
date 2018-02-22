#
#	Copyright Saul Youssef, December 2004
#
from ShellCommand import *
from Execution    import *
import os

class UninstallShellCommand(ShellCommand):
	type   = 'uninstall shell command'
	title  = 'Uninstall Shell Commands'
	action = 'uninstall shell'
		
	def satisfied(self): return Reason(`self`+' not installed yet.',not self.acquired)
	def acquire(self): return Reason()
	def retract(self):
		reason = execute(self.command)
		if reason.ok(): 
			self.executed = 1
			if not allow('uninstall-shell-stop'): reason = Reason()
		else: 
			self.executed = 1
#			print 'WARNING: Uninstall shell command ['+self.command+'] has failed ['+`reason`+'].  Ignoring...'
		return reason
