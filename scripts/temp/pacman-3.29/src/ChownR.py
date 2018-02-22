#
#	Copyright Saul Youssef, July, 2003
#
from Environment import *
from Base        import *

class ChownR(Environment):
	type   = 'change ownership recursively'
	title  = 'Change Ownership Recursively'
	action = 'chownR'
	def __init__(self,directory,owner=getusername()):
		self.__owner          = owner
		self.__directory      = directory
		self.__originalOwners = []
		
	def str(self): return self.__directory+'/... to '+self.__owner

	def satisfied(self): return Reason('['+self.str()+'] has not been set yet.',not self.acquired)
	
	def satisfiable(self):
		def visit(arg,dirname,names):
			if not writeAccess(dirname): arg = 0
			for name in names:
				path = os.path.join(dirname,name)
				if not writeAccess(dirname): 
					arg = 0
					break
		arg = 1
		os.path.walk(self.__directory,visit,arg)
			
		if arg:
			return Reason()
		else:
			return Reason('Directory ['+self.__directory+'] contains files with no write access.')

#-- Action
	def acquire(self):
		reason = Reason()
		gotit,uid,gid = userids(self.__owner)
		
		self.__directory = fullpath(self.__directory)
		reason = Reason("File ["+self.__directory+"] doesn't exist.  Can't chownR.",not os.path.exists(self.__directory))
		if reason.ok():
			self.__directory = fullpath(self.__directory)
			def visit(arg,dirname,names):
				for filename in names:
					originalOwner = owner(os.path.join(dirname,filename))
					os.chown(os.path.join(dirname,filename),uid,gid)
					self.__originalOwners.append((originalOwner,dirname,filename,))
			if gotit:
				arg = 1
				try:
					os.path.walk(self.__directory,visit,arg)
				except (IOError,OSError):
					reason.reason('Failure chownging files in ['+self.__path+'/...].')
			else:
				reason.reason("User ["+self.__owner+"] no longer exists.")
		return reason
			
	def retract(self):
		reason = Reason()
		
		while len(self.__originalOwners)>0 and reason.isNull():
			own,dirname,filename = self.__originalOwners[-1]
			gotit,uid,gid = userids(own)
			
			if gotit:
				try:
					os.chown(os.path.join(dirname,filename),uid,gid)
					self.__originalOwners.pop()
				except (IOError,OSError):
					reason.reason("Can't restore ownership of file ["+fullpath(os.path.join(dirname,filename))+"].")
			else:
				reason.reason("User ["+own+"] no longer exists.")
				
		return reason
					
					
