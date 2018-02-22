#
#	Copyright Saul Youssef, June 2003
#
from freedisk     import *
from Environment  import *

class FreeMegs(Environment):
	type   = 'freeMegsMinimum'
	title  = 'Minimum Free Megabytes of Disk Space'
	action = 'test for free disk space'
	def __init__(self,space,path='.'): self.path,self.megs = path,space
#-- Set
	def equal(self,x): return self.path==x.path and self.megs==x.megs
	def str(self): return `self.megs`+' free Megabytes at '+self.path
	
#-- Compatible
	def compatible(self,g): return Reason()
	
#-- Satisfiable
	def satisfied(self): 
		if os.path.isdir(fullpath(self.path)):
#			self.path = fullpath(self.path)
			if    long(self.megs) <= long(localmegs(fullpath(self.path))): return Reason()
			else: return Reason('['+`self`+'] is not available.')
		else:
			return Reason("Free megs ["+`self`+"] at directory ["+fullpath(self.path)+'].  Directory does not exist.')
	def satisfiable(self): return Reason()
	def     acquire(self): 
		if self.satisfied().ok():
			self.path = fullpath(self.path)
			return Reason()
		else:
			return self.satisfied()
	def     retract(self): return Reason()
	
#-- SatisfyOrder
	def satisfies(self,x): 
		if self.type==x.type: return x.megs <= self.megs
		else:                 return 0
		
