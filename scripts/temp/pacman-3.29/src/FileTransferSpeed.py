#
#	Copyright, Saul Youssef, December 2003
#
from FloatAttr import *
from Base import *
from Execution import *
import time

class FileTransferSpeedMinimum(FloatAttr):
	type   = 'file copy speed'
	title  = 'File Copy Speeds'
	action = 'test file copy speed'

	def __init__(self,path,minimumMegsPerSecond,fileMegs):
		self.path = path
		self.fileMegs = float(fileMegs)
		self.transferRate = 0.0
		self.minimumMegsPerSecond = minimumMegsPerSecond
	def equal(self,x):
		return self.path==x.path and \
			self.fileMegs==x.fileMegs and \
			self.transferRate==x.transferRate and \
			self.minimumMegsPerSecond==x.minimumMegsPerSecond
	def str(self): 
		if self.transferRate==0.0: 
			return '> '+('%g' % self.minimumMegsPerSecond)+' megs per second from ['+os.getcwd()+'] to ['+self.path+']'
		else:
			return ('%g'% self.transferRate)+' Megs per second > '+('%g' % self.minimumMegsPerSecond)+' Megs per second from '+os.getcwd()+' to '+self.path			

	def satisfied(self): return Reason("File transfer speed test has not been attempted.",not self.acquired)	
	def satisfiable(self): return Reason()
	def acquire(self):
		reason = makeFileFixedSize(int(self.fileMegs),'zzz-tmp-file')
		if reason.ok(): 
			t1 = time.time()
			reason = execute('cp zzz-tmp-file '+os.path.join(fullpath(self.path),'zzz-tmp-file-c'))
			t2 = time.time()
			removeFile('zzz-tmp-file')
			removeFile(os.path.join(fullpath(self.path),'zzz-tmp-file-c'))
			
			if    t1==t2: mps = 2.0*self.minimumMegsPerSecond
			else:         mps = float(self.fileMegs)/(t2-t1)
			self.transferRate = mps
			s  = '%g' % mps
			s2 = '%g' % self.minimumMegsPerSecond
			if mps<self.minimumMegsPerSecond:
				reason = Reason('File transfer rate of '+s+' megs per second is less than the minimum: '+('%g' % self.minimumMegsPerSecond)+\
				                ' from '+os.getcwd()+' to '+self.path)
		return reason
	def retract(self): 
		self.transferRate = 0.0
		return Reason()
