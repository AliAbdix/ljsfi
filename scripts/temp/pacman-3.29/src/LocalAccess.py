#
#	Copyright, August 2003, Saul Youssef
#
from Access import *

class LocalAccess(Access):
	type = 'local directory'
	def __init__(self,location): self.location = fullpath(location)

#-- Set
	def __repr__(self): return self.location
	def equal(self,x): return self.location==x.location
	
	def access(self): 
		return os.path.isdir(os.path.expanduser(self.location))
	def names(self): return self.namesPath('')
		
	def namesPath(self,path=''):
		reason = Reason()
		try:
			filenames = os.listdir(os.path.join(self.location,path))
		except (IOError,OSError):
			filenames = []
			if os.path.exists(os.path.join(self.location,path)):
				reason = Reason("Can't read ["+os.path.join(self.location,path)+"].")
			else:
				reason = Reason("Local file ["+os.path.join(self.location,path)+"] doesn't exist.")
		return reason,filenames
		
	def getFile(self,name,target=''):
		if target=='': target2 = name
		else:          target2 = target
		
		return safeCopy(os.path.join(self.location,name),fullpath(target2))
#		reason = Reason()
#		try:
#			if verbo('io'): print 'Copying ['+name+'] to ['+target2+']...'
#			shutil.copyfile(os.path.join(self.location,name),fullpath(target2))
#		except (IOError,OSError):
#			reason = Reason("Error copying file ["+os.path.join(self.location,name)+"] to ["+fullpath(target2)+"].")
#
#		return reason
