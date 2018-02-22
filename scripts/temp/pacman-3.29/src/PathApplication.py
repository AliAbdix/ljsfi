#
#	Copyright August 2003, Saul Youssef
#
from Environment import *

class PathApplication(Environment):
	type   = 'file tree application'
	title  = 'File Tree Applications'
	action = 'apply to file tree'
	
	def __init__(self,path):  self.path = path
	def equal(self,x): return self.path == x.path
	def str(self): return self.path

#-- Satisfiable
	def satisfied(self): return Reason('['+`self`+'] has not been applied',not self.acquired)
	def satisfiable(self): return Reason()
	
#-- Action
	def fileApp(self,filename): abort('Missing fileApp in PathApplication.')
	def direApp(self,direname): abort('Missing direApp in PathApplication.')
	def fileInv(self,filename): abort('Missing fileInv in PathApplication.') 
	def direInv(self,direname): abort('Missing direInv in PathApplication.')
	
	def acquire(self):
		def app(arg,dirname,names):
			arg = ''
			try:
				 self.direApp(dirname)
				 for filename in names: 
				 	try:
						self.fileApp(os.path.join(dirname,filename))
					except (IOError,OSError):
						arg = os.path.join(dirname,filename)
			except (IOError,OSError):
				arg = dirname
		arg = ''
		os.path.walk(fullpath(self.path),app,arg)
		
		if arg!='': 
			self.path = fullpath(self.path)	
			return Reason('Failure attempting ['+`self`+'] at ['+arg+'].')
		else:
			return Reason()
	
	def retract(self):
		def inv(arg,dirname,names):
			arg = ''
			try:
				self.direInv(dirname)
				for filename in names:
					try:
						self.fileInv(os.path.join(dirname,filename))
					except (IOError,OSError):
						arg = os.path.join(dirname,filename)
			except (IOError,OSError):
				arg = dirname
				
		arg = ''
		os.path.walk(self.path,inv,arg)
		
		if arg!='': return Reason('Failure attempting to retract ['+`self`+'] at ['+arg+'].')
		else:       return Reason()
		
