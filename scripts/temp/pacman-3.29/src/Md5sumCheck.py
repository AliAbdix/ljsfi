#
#	Copyright, Saul Youssef, February 2005
#
from Base        import *
from Environment import *
import md5sum

class Md5sumCheck(Environment):
	type   = 'md5sum check'
	title  = 'Md5sum Check'
	action = 'md5sum check'
	
	def __init__(self,path,checkstring):
		self._path        = path
		self._checkstring = checkstring
		
	def equal(self,x): return self._path==x._path and self._checkstring==x._checkstring
	def str(self): return self._path+'='+self._checkstring+'?'

	def satisfied(self): return Reason('md5 check ['+self.str()+'] has not been attempted.',not self.acquired)
	def acquire(self):
		r = Reason()
		if os.path.exists(fullpath(self._path)):
			self._path = fullpath(self._path)
		else:
			r = Reason('File ['+fullpath(self._path)+"] does not exist.  Can't md5check.")
		if r.ok():
			r,md5string = md5sum.md5sum(self._path)
			if r.ok():
				r = Reason('File ['+self._path+'/'+md5string+'] does not have md5checksum ['+self._checkstring+'].',not self._checkstring==md5string)
		return r
	def retract(self): return Reason()

