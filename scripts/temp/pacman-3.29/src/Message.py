#
#	Copyright, Saul Youssef, August 2003
#
from StringAttr import *
import os

class Message(StringAttr):
	type   = 'user message'
	title  = 'User Messages'
	action = 'show message'
	
	def str      (self): return '"'+self.value+'"'
	def satisfied(self): return Reason('Message has not been shown',not self.acquired)
	def acquire  (self): print os.path.expandvars(self.value); return Reason()
	def retract  (self): return Reason()

class Fail(StringAttr):
	type   = 'fail'
	title  = 'Fails'
	action = 'fail to install'
	
	def satisfied  (self): return Reason(self.value)
	def satisfiable(self): return self.satisfied()
	def acquire    (self): return Reason(self.value)
	def retract    (self): return Reason()
	

