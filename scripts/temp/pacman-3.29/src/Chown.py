#
#	Copyright Saul Youssef, July, 2003
#
from Environment import *
from Base        import *

class Chown(Environment):
	type   = 'change ownership'
	title  = 'Change Ownerships'
	action = 'change ownership'
	def __init__(self,path,owner=getusername()):
		self._owner         = owner
		self._path           = path
		self._originalOwner  = ''
#-- Set
	def equal(self,ch): return self._owner == ch._owner
	def str(self):      return ' of ['+self._path+'] by ['+self._owner+']'
	
#-- Satisfiable
	def satisfied  (self): return Reason('['+`self`+'] has not been attempted yet.',not self.acquired)			
	def satisfiable(self): return Reason()

#-- Action
	def acquire(self):
		reason = Reason()
		gotit,uid,gid = userids(self._owner)
		
		try:
			self._path = fullpath(self._path)
			self._originalOwner = owner(self._path)
			os.chown(self._path,uid,gid)
		except (IOError,OSError):
			reason.reason("Failed to change ownership of ["+self._path+"] to ["+self._owner+"].")
		return reason
		
	def retract(self): 
		reason = Reason()
		if self.acquired:
			gotit,uid,gid = userids(self._originalOwner)
			try:
				os.chown(self._path,uid,gid)
			except (IOError,OSError):
				reason.reason("Failed to restore ownership of ["+self._path+"] to ["+self._originalOwner+"].")
		return reason		

class OwnedBy(Chown):
	type   = 'test file ownership'
	title  = 'Test File Ownerships'
	action = 'test file ownership'
	
	def acquire(self): 
		self._path = fullpath(self._path)
		if self._owner=='- any -': return Reason()
		reason = Reason('File ['+self._path+'] does not exist.',not os.path.exists(self._path))
		if reason.ok():
			reason,own = owner2(self._path)
			if reason.ok():
				reason = Reason('File ['+self._path+'] is not owned by ['+self._owner+'].',not own==self._owner)
		return reason
	def retract(self): return Reason()
	
	
