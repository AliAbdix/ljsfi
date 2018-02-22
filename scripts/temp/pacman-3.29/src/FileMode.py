
from Base import *
import Execution
import os

class FileMode(PrintOut):
	def __init__(self,path):
		self._path = fullpath(path)
		self._bits = intBits(os.stat(path)[0],16)
		
	def __repr__(self): return self._path+' '+`self._bits`
		
	def exists(self): return os.path.exists(self._path)
	def isdir(self):  return os.path.isdir (self._path)
	def owner(self):  return owner2(self._path)
	
#	def ownerExecute(self): return self._bits[0]
#	def ownerWrite  (self): return self._bits[1]
#	def ownerRead   (self): return self._bits[2]
#
#	def groupExecute(self): return self._bits[3]
#	def groupWrite  (self): return self._bits[4]
#	def groupRead   (self): return self._bits[5]
#		
#	def worldExecute(self): return self._bits[6]
#	def worldWrite  (self): return self._bits[7]
#	def worldRead   (self): return self._bits[8]
#
	def ownerExecute(self): return self._bits[8]
	def ownerWrite  (self): return self._bits[7]
	def ownerRead   (self): return self._bits[6]

	def groupExecute(self): return self._bits[5]
	def groupWrite  (self): return self._bits[4]
	def groupRead   (self): return self._bits[3]
		
	def worldExecute(self): return self._bits[2]
	def worldWrite  (self): return self._bits[1]
	def worldRead   (self): return self._bits[0]

	
	def setOwnerExecute(self,option):
#		if    option=='on': return Execution.execute('chmod o+x '+self._path).ok()
#		else:               return Execution.execute('chmod o-x '+self._path).ok()
#		if    option=='on': self._bits[0] = 1
#		else:               self._bits[0] = 0
		if    option=='on': self._bits[8] = 1
		else:               self._bits[8] = 0
		return self.set()
	def setOwnerWrite(self,option):
#		if    option=='on': return Execution.execute('chmod o+w '+self._path).ok()
#		else:               return Execution.execute('chmod o-w '+self._path).ok()
#		if    option=='on': self._bits[1] = 1
#		else:               self._bits[1] = 0
		if    option=='on': self._bits[7] = 1
		else:               self._bits[7] = 0
		return self.set()
	def setOwnerRead(self,option):
#		if    option=='on': return Execution.execute('chmod o+r '+self._path).ok()
#		else:               return Execution.execute('chmod o-r '+self._path).ok()
#		if    option=='on': self._bits[2] = 1
#		else:               self._bits[2] = 0
		if    option=='on': self._bits[6] = 1
		else:               self._bits[6] = 0
		return self.set()
		
	def setGroupExecute(self,option):
#		if    option=='on': return Execution.execute('chmod g+x '+self._path).ok()
#		else:               return Execution.execute('chmod g-x '+self._path).ok()
#		if    option=='on': self._bits[3] = 1
#		else:               self._bits[3] = 0
		if    option=='on': self._bits[5] = 1
		else:               self._bits[5] = 0
		return self.set()
	def setGroupWrite(self,option):
#		if    option=='on': return Execution.execute('chmod g+w '+self._path).ok()
#		else:               return Execution.execute('chmod g-w '+self._path).ok()
#		if    option=='on': self._bits[4] = 1
#		else:               self._bits[4] = 0
		if    option=='on': self._bits[4] = 1
		else:               self._bits[4] = 0
		return self.set()
	def setGroupRead(self,option):
#		if    option=='on': return Execution.execute('chmod g+r '+self._path).ok()
#		else:               return Execution.execute('chmod g-r '+self._path).ok()
#		if    option=='on': self._bits[5] = 1
#		else:               self._bits[5] = 0
		if    option=='on': self._bits[3] = 1
		else:               self._bits[3] = 0
		return self.set()

	def setWorldExecute(self,option):
#		if    option=='on': return Execution.execute('chmod a+x '+self._path).ok()
#		else:               return Execution.execute('chmod a-x '+self._path).ok()
#		if    option=='on': self._bits[6] = 1
#		else:               self._bits[6] = 0
		if    option=='on': self._bits[2] = 1
		else:               self._bits[2] = 0
		return self.set()
	def setWorldWrite(self,option):
#		if    option=='on': return Execution.execute('chmod a+w '+self._path).ok()
#		else:               return Execution.execute('chmod a-w '+self._path).ok()
#		if    option=='on': self._bits[7] = 1
#		else:               self._bits[7] = 0
		if    option=='on': self._bits[1] = 1
		else:               self._bits[1] = 0
		return self.set()
	def setWorldRead(self,option):
#		if    option=='on': return Execution.execute('chmod a+r '+self._path).ok()
#		else:               return Execution.execute('chmod a-r '+self._path).ok()
#		if    option=='on': self._bits[8] = 1
#		else:               self._bits[8] = 0
		if    option=='on': self._bits[0] = 1
		else:               self._bits[0] = 0
		return self.set()
	
	def set(self):
		try:
			os.chmod(self._path,bits2Int(self._bits))
			return 1
		except (IOError,OSError):
			return 0
