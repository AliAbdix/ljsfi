#
#	Copyright 2005, Saul Youssef
#
from         LocalAccess import *
from           URLAccess import *
from  LocalTarballAccess import *
from           SSHAccess import *
from            Registry import *

import GSIAccess

class UniversalAccess(Access):
	def __init__(self,pacmanAccessString,mode=''):
		s = registry.trans(pacmanAccessString)
		if 0 and tail(s,'.snapshot') or tail(s,'.bundle'):
			if ':' in s:
				if front(s,'gsiftp://'):  self.accessor = GSIAccess(s)
			else:
				self.accessor = LocalShelfAccess(s) 
		elif front(s,'gsiftp://'):
			self.accessor = GSIAccess.GSIAccess(s)
		elif ':' in s:
			if isURL(s): 
				if mode=='source': self.accessor = URLAccessSource(s)
				else:              self.accessor = URLAccess(s)
			else:        
				self.accessor = SSHAccess(s)
		else:
			if tail(s,'.tar'):  self.accessor = LocalTarballAccess(s)
			else:               self.accessor = LocalAccess(s)
		self.location = self.accessor.location
		
	def equal(self,x): return self.accessor==x.accessor
	def __repr__(self): return `self.accessor`
			
	def names(self): return self.accessor.names ()
	def access(self): return self.accessor.access()
	def getFile  (self,name,target=''): return self.accessor.getFile(name,target)
	def namesPath       (self,path=''): return self.accessor.namesPath(path)	

class UniversalFile(Set,PrintOut):
	def __init__(self,UFL):
		self._UFL = UFL
		self._ucl,self._file = os.path.split(self._UFL)
		self._access = UniversalAccess(self._ucl)
		
	def __eq__  (self,x): return self._UFL == x._UFL
	def __repr__(self  ): return self._UFL
	
	def access    (self): return self._access.access()
	def getLines  (self): return self._access.getLines(self._file)
