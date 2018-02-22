#
#	Copyright, Saul Youssef, February 2004
#
from Environment import *

class Cat(Environment):
	type   = 'cat'
	title  = 'Cat'
	action = 'display a text file'

	def __init__(self,path):
		self.path = path
		
	def str(self): return self.path
	
	def equal(self,x): return self.path==x.path and fullpath(self.path)==fullpath(x.path)
	
	def satisfied(self): return Reason('File ['+self.path+'] has not been displayed yet.',not self.acquired)
	def satisfiable(self): return Reason()
	def acquire(self):
		reason = Reason()
		try:
			f = open(fullpath(self.path),'r')
			lines = f.readlines()
			f.close()
			for line in lines: print line[:-1]
		except (IOError,OSError):
			reason = Reason('Error attempting to read ['+fullpath(self.path)+'].')
			
		return reason				
	def retract(self): return Reason()
	
