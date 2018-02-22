#
#	Copyright Saul Youssef, November 2004
#
from Environment import *

class DirectoryChoice(Environment):
	type   = 'chosen directory'
	title  = 'Installer Chosen Directories'
	action = 'choose a directory'
#-- Set	
	def __init__(self,environmentVariable,subdirectory='workspace'):
		self.__env = environmentVariable
		self.__location = ''
		self.__subdirectory = subdirectory
		self.export  =  1
		
	def equal(self,icwd): return self.__env==icwd.__env and \
	                             self.__location == icwd.__location and \
				     self.__subdirectory == icwd.__subdirectory
	def str(self):
		if self.__location == '': return self.__env+'='+' - unset -'
		else:                     return self.__env+'='+self.__location
#-- Compatible
	def compatible(self,icwd):
		if self.__env!=icwd.__env: return Reason()
		else:
			if self.__location==icwd.__location and \
			   self.__subdirectory==icwd.__subdirectory: return Reason()
			else:
				return Reason(`self`+' and '+`icwd`+' are incompatible.')
#-- Satisfiable
	def satisfied(self): 
		reason = Reason()
		if os.environ.has_key(self.__env):
			path = os.environ[self.__env]
			self.__location = path
			path2 = fullpath(path)
			if   not os.path.exists(path2): reason.reason('Directory ['+self.__env+'='+path+'] does not exist.')
			elif not os.path.isdir (path2): reason.reason('Directory ['+self.__env+'='+path+'] is not a directory.')
			elif not    writeAccess(path2): reason.reason('Directory ['+self.__env+'='+path+'] is not writeable.')
		else:
			reason.reason('Environment variable ['+self.__env+'] is not defined.')
		return reason
			
	def satisfiable(self): return Reason()

#-- Action
	def acquire(self):
		location = cookieDirectory('Choose location for '+self.__env+': ','../cookies')
		self.__location = os.path.join(fullpath(location),self.__subdirectory)
		self.__wasSet = os.environ.has_key(self.__env)
		if    self.__wasSet: self.__oldval = os.environ[self.__env]
		else:                self.__oldval = ''
		os.environ[self.__env] = self.__location
		
		return Reason()
		
	def retract(self):
		if self.__wasSet: 
			os.environ[self.__env] = self.__oldval
		else:   
			if os.environ.has_key(self.__env): del os.environ[self.__env]
		return Reason()
		
	def shellOut(self,csh,sh,py,pl,ksh):
		if self.satisfied().isNull():
			csh.write('setenv '+self.__env+' "'+self.__location+'"\n')
			sh.write(self.__env+'="'+self.__location+'"\n')
			sh.write('export '+self.__env+'\n')
			py.write('os.environ["'+self.__env+'"] = "'+self.__location+'"\n')
			pl.write('$ENV{"'+self.__env+'"} = "'+self.__location+'";\n')
			ksh.write(self.__env+'="'+self.__location+'"\n')
			ksh.write('export '+self.__env+'\n')
			


			
