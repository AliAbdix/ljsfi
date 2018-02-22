#
#	Copyright Saul Youssef, 2005
#
from Environment import *
import os

class AskUntilFileExists(Environment):
	type   = 'ask until file exists'
	title  = 'Ask Until File Exists'
	action = 'ask until file exists'
	
	def __init__(self,path): self._path = path
		
	def equal(self,x): return self._path==x._path
	def str(self): return self._path+' exists'
	
	def compatible(self,x): return Reason()
	
	def satisfiable (self): return Reason()
	def satisfied   (self): return Reason('File ['+self._path+'] existence has not yet been tested.',not self.acquired)
	
	def acquire(self):
		r = Reason()
		fp = fullpath(self._path)
		if not os.path.exists(fp):
			while 1:
				ans = raw_input('Enter "y" when ['+fp+'] is ready, "q" to quit: ')
				if os.path.exists(fp) or string.strip(ans)=='q': 
					break
				else:
					print "File ["+self._path+"] still does not exist.  Try again..."
			if os.path.exists(fp):
				self._path = fp
			else:
				r = Reason('File ['+fp+"] is missing and hasn't been provided by the installer.")
		return r
	def retract(self): return Reason()
	def satisfies(self,fe): return self==fe

class FileExists(Environment):
	type   = 'exists'
	title  = 'File Existences'
	action = 'check that a file exists'
	
	def __init__(self,filename): self._filename = filename
#-- Set
	def equal(self,x): return self._filename==x._filename
	def str(self):     return self._filename
	
#-- Compatible
	def compatible(self,x): return Reason()

#-- Satisfiable
	def satisfied  (self): 	
		if self.acquired:
			return Reason('File ['+self._filename+'] does not exist.',not os.path.exists(self._filename))
		else:
			return Reason('Existence of ['+self._filename+'] has not been tested.',not self.acquired)
	def satisfiable(self): return Reason()
	
	def acquire(self):
		if os.path.exists(fullpath(self._filename)):
			self._filename = fullpath(self._filename)
			return Reason()
		else:
			return Reason('File ['+fullpath(self._filename)+'] does not exist.')
			
	def retract(self): return Reason()
	
#-- SatisfyOrder
	def satisfies(self,fe): return self==fe
	
class FileExistsOnce(FileExists):
	type  = 'exists once'
	title = 'File Exists Onces'
	action = 'check that a file exists'
	
	def satisfied(self): return Reason('File ['+self._filename+'] existence has not yet been tested.',not self.acquired)
#	def satisfied  (self): 
#		if self.everfailGet():
#			return Reason('File ['+self._filename+'] does not exist.')
#		else:
#			return Reason('Existence of ['+self._filename+'] has not been tested.',not self.acquired)			

class DirectoryContains(Environment):
	type  = 'directory existence and contents'
	title = 'Directory Existence and Contents'
	action = 'check directory existence and contents'
	
	def __init__(self,dirname,contents=[]):
		self.dirpath = dirname
		self.contents = contents
		
	def equal(self,x): return self.dirpath==x.dirpath and self.contents==x.contents
	def str(self): 
		if len(self.contents)>0: return self.dirpath+' contains '+`self.contents`
		else:                    return self.dirpath
		
	def satisfiable(self): return Reason()
	def satisfied(self):
		reason = Reason()
		if self.acquired:
			if os.path.exists(fullpath(self.dirpath)):
				if os.path.isdir(fullpath(self.dirpath)):
					if not forall(self.contents, lambda x: os.path.exists(fullpath(x))):
						reason = Reason('Directory ['+fullpath(self.dirpath)+'] does not contain '+`self.contents`+'.')
				else:
					reason = Reason('File ['+fullpath(self.dirpath)+'] is not a directory.')
			else: 
				reason = Reason('Directory ['+fullpath(self.dirpath)+'] does not exist.')
		return reason
		
	def acquire(self): return self.satisfied()
	def retract(self): return Reason()

class DirectoryEmpty(Environment):
	type  = 'empty directory'
	title = 'Empty Directory'
	action = 'test that directory is empty'
	
	def __init__(self,dirname):
		self.dirpath = dirname
		
	def equal(self,x): return self.dirpath==x.dirpath
	def str(self): return self.dirpath
		
	def satisfiable(self): return Reason()
	def satisfied(self): 
		return Reason(`self`+' has not been satisfied.',not self.acquired)
	def acquire(self): 
		reason = Reason()
		if os.path.exists(fullpath(self.dirpath)):
			self.dirpath = fullpath(self.dirpath)
			if os.path.isdir(self.dirpath):
				reason = Reason('Directory ['+self.dirpath+'] is not empty.',len(os.listdir(self.dirpath))>0)
			else:
				reason = Reason('File ['+self.dirpath+'] is not a directory.')
		else: 
			reason = Reason('Directory ['+self.dirpath+'] does not exist.')
		return reason
	def retract(self): return Reason()

