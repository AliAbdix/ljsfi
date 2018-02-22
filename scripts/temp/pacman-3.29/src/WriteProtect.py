#
#	Copyright, August 2003, Saul Youssef
#
from PathApplication import *
from Execution       import *

class WriteProtect(PathApplication):
	type   = 'write protect'
	title  = 'Write Protects'
	action = 'write protect' 
	
	def fileApp(self,filename): execute('chmod a-w '+filename).inquire()
	def direApp(self,direname): self.fileApp(direname)
	
	def fileInv(self,filename): execute('chmod a+w '+filename).inquire()
	def direInv(self,direname): self.fileInv(direname)
	
