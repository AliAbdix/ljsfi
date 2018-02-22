#
#	Copyright Saul Youssef, June 2003
#
from Environment import *
from Execution   import *
import os,popen2,commands

inPathcache = {}

class InPath(Environment):
	type = "inpath"
	title = "Files in the installer's $PATH"
	action = "test installer's $PATH for"
	def __init__(self,filename): self._filename = filename
#-- Set	
	def equal(self,p):  return self._filename == p._filename
	def str(self): return self._filename
	
#-- Compatible
	def compatible(self,x): return Reason()
	
#-- Satisfiable
	def satisfied  (self): 
		reason = Reason()
		if inPathcache.has_key(self._filename):
			pass
		else:
			reason = fileInPath(self._filename)
			if reason.ok(): inPathcache[self._filename] = ''
		return reason
	def satisfiable(self): return self.satisfied()
	
class Which(InPath):
	type   = 'which'
	title  = 'Whichs'
	action = "test installer's $Path for"
	
	def satisfiable(self): return Reason()
	def satisfied  (self): return fileInPath(self._filename)

	
