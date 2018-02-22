#
#	Copyright, Saul Youssef, July 2003
#
from Base        import *
from Environment import *
from Execution   import *
import os

class MV(Environment):
	type = 'mv'
	title = 'Moves'
	action = 'mv'
	
	def __init__(self,source,target): self.__source,self.__target = source,target
#-- Set
	def equal(self,x): return self.__source==x.__source and self.__target==x.__target
	def str(self):         return self.__source+' to '+self.__target
	
#-- Compatible
	def compatible(self,mv): return Reason()
	
#-- Satisfiable
	def satisfied(self): 
		if self.acquired: return Reason()
		else:             return Reason("Move ["+`self`+"] has not been made.")
	def satisfiable(self): return Reason()
	
#-- Action
	def acquire(self):
		reason = Reason()
		if os.path.exists(fullpath(self.__source)):
			if os.path.exists(fullpath(self.__target)):
				reason.reason("Can't move to ["+fullpath(self.__target)+"].  File exists.")
			else:
				reason = execute('mv '+fullpath(self.__source)+' '+fullpath(self.__target))
				if reason.ok():
					self.__source = fullpath(self.__source)
					self.__target = fullpath(self.__target)
		else: 
			reason.reason("["+fullpath(self.__source)+"] doesn't exist.  Can't move.")
		return reason
		
	def retract(self):
		reason = Reason()
		if os.path.exists(self.__target):
			if os.path.exists(self.__source):  reason.reason("Can't undo ["+`self`+"] because ["+self.__source+"] exists.")
			else:                              reason = execute('mv '+self.__target+' '+self.__source)
		else: reason.reason("Can't undo ["+`self`+"] because ["+self.__target+"] doesn't exist.")
		return reason
