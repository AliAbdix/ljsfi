#
#	Copyright, August 2003, Saul Youssef
#
from PathApplication import *

class LS(PathApplication):
	type   = 'ls'
	title  = 'LSs'
	action = 'ls'
	
	def fileApp(self,filename): 
		print filename
		return 1
		
	def direApp(self,direname):
		print direname+'/'
		return 1
		
	def fileInv(self,filename): return 1
	def direInv(self,direname): return 1
	
