#
#	Copyright, Saul Youssef, August 2003
#
from Environment import *

class Anchor(Environment):
	type   = 'anchor'
	title  = 'Anchors'
	action = 'fix location'
	
	def __init__(self): self.location = '- unset -'
#-- Set
	def equal(self,a): return self.location == a.location
	def str(self):     return self.location
	
#-- Compatible
	def compatible(self): return Reason()
	
#-- Satisfiable
	def satisfied(self): 
		if self.acquired: 
			if os.getcwd()==self.location: return Reason()
			else:  return Reason('Current directory ['+os.getcwd()+'] does not satisfy ['+`self`+'].')
		else:             
			return Reason('Anchor not set.')
	def satisfiable(self): 
		return Reason("Pacman installation has been moved.",self.location!='- unset -' and self.location!=os.getcwd())

#-- Action
	def acquire(self):
		reason = Reason()
		try:
			self.location = os.getcwd()
		except (OSError,IOError):
			reason.reason("Current directory does not exist.")
		return reason
	def retract(self): return Reason()	
	
	
