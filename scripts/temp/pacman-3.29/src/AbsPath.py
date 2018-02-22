#
#	Copyright, Saul Youssef, August 2005
#
from Base         import *
from Environment  import *
import Execution
import os

class AbsPath(Environment):
	type   = 'absolute path'
	action = 'check that the current path is absolute'
	title  = 'Absolute Path'
	
	def __init__(self,path='.'): self._path = path
	def str(self): return self._path
	def equal(self,x): return self._path==x._path
	
	def satisfied(self): return Reason('['+`self`+'] is not satisfied.',not self.acquired)	
	def acquire(self):
		self._path = fullpath(self._path)
		r = Reason()
		if not localPathEqual(self._path,os.path.realpath(self._path)):
			r = Reason('Path ['+self._path+'] is really ['+os.path.realpath(self._path)+'] - not an absolute path.')
		return r
	def retract(self): return Reason()
		
