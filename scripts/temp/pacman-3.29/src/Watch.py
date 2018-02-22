#
#	Copyright, Saul Youssef, November 2004
#
from Base import *
from Environment import *
import os,time

class Watch(Environment):
	type   = 'watch'
	title  = 'Watch'
	action = 'watches over files'
	
	def __init__(self,path):
		self._path = path
		self._mode = 'time'
		self._time = None
		self._children = AND()
	
	def equal(self,x): return self._path==x._path and self._mode==x._mode
	def str(self): return self._path
	def display(self,indent=0):
		if     self._mode=='': 
			print indent*' '+self.statusStr()+' '+self.str()
		elif   not self.acquired: 
			print indent*' '+self.statusStr()+' '+self.str()+' <time to be set> '
		else:                    
			print indent*' '+self.statusStr()+' '+self.str()+' '+time.ctime(self._time)
		for e in self._children:
			e.display(indent+4)
	
#	def satisfied(self): return Reason('File ['+self.str()+'] has not yet been tested for existence.',not self.acquired)
	def acquire(self):
		self._path = fullpath(self._path)
		r = Reason()
		if os.path.exists(self._path):
			self._time = os.path.getmtime(self._path)
			if r.ok() and os.path.isdir(self._path):
				for filename in os.listdir(self._path):
					path = os.path.join(self._path,filename)
					child = Watch(os.path.join(self._path,path))
					r = child.satisfy()
					if not r.ok(): break
					self._children.append(child)
		else:
			r = Reason('File ['+self.str()+'] does not exist.')		
		return r
			
	def retract(self):
		self._time = None
		return Reason()
		
	def verify(self):
		r = AllReason()
		if os.path.exists(self._path):
			if not self._mode=='':
				t = os.path.getmtime(self._path)
				if not t==self._time: r.append(Reason('File ['+self.str()+'] watched since ['+time.ctime(self._time)+'] was modified on ['+time.ctime(t)+'].'))
		else:
			r.append(Reason('File ['+self.str()+'] no longer exists.'))
			
		r.append(self._children.verify())
		
		return r
		
