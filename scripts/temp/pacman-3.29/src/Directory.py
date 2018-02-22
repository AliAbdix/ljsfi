#
#	Copyright Saul Youssef, November 2004
#
from Environment import *
from Execution   import *
#import Home,Package
import os

class Directory(Environment):
	type   = 'mkdir'
	title  = 'Directories'
	action = 'mkdir'
	
	def __init__(self,path): 
		self.path = string.strip(path)
		self.path0 = self.path
		self.created = 0
#-- Set	
	def equal(self,d):  return self.path==d.path	
	def str(self):      return self.path	
	def satisfied(self):
		reason = Reason()
		if len(self.path)>1 and self.path[0]=='?': reason = Reason(`self`+' has not yet been chosen.')
		else:
			if   os.path.isdir(fullpath(self.path )): self.path = fullpath(self.path)
			elif os.path.isdir(fullpath(self.path0)): self.path = fullpath(self.path0)
			else:
				reason = Reason('Directory ['+self.path+'] does not exist.')
		return reason	
#-- Action
	def acquire(self):
		reason = Reason()
		if len(self.path)>1 and self.path[0]=='?': 
			self.path = cookieDirectory(self.path[1:])

		if os.path.isdir(fullpath(self.path)):
			self.path = fullpath(self.path)
		elif os.path.exists(fullpath(self.path)):
			reason = Reason('['+fullpath(self.path)+'] is not a directory.')
		else:
			try:
				execute('mkdir '+fullpath(self.path))
				self.path = fullpath(self.path)
				self.created = 1
			except (IOError,OSError):
				reason.reason("Failure attempting to create ["+self.path+"].")
		return reason
		
	def retract(self): 
		reason = Reason()
		if self.created: 
			import Home,Package

			home = Home.Home()
			reason,ps = home.getLocation(self.path)
			if reason.ok():
				wd = os.getcwd()
				for p in ps:
					verbo.log('pac','Package ['+p._spec.str()+'] uninstall induced by ['+self.path+'] removal.')
					reason = Package.LazyPackage(p._spec).uninstall()
					if not reason.ok(): break
				os.chdir(wd)
			if reason.ok(): execute('chmod -R a+w '+self.path)
			if reason.ok(): reason = execute('rm -r -f '+self.path)
			if reason.ok(): self.created = 0
		return reason

class MkDirPersistent(Directory):
	type   = 'mkdir persistent'
	title  = 'Persisent Directories'
	action = 'mkdir persistent'
	
	def retract(self): return Reason()
	

class PersistentDirectory(Directory):
	type = 'mkdirPersistent'
	title = 'Persistent Directories'

#-- Action
	def retract(self): return Reason()
	
