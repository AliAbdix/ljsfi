#
#	Copyright Saul Youssef, January 2004
#
from Environment import *

class CommandLineSwitch(Environment):
	type  = 'command line switch'
	title = 'Command Line Switch'
	action = 'test for command line switch'
	
	def __init__(self,switch):
		self._switch = switch
		
	def str(self): return self._switch
	def equal(self,x): return self._switch==x._switch
	
	def satisfied   (self): return Reason('Command line switch ['+self._switch+'] not used.',not switch(self._switch))
	def satisfiable (self): return self.satisfied()
	
	def acquire     (self): return self.satisfied()
	def retract     (self): return Reason()
	
