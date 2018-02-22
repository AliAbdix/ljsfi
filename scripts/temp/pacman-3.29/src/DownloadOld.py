#
#	Download, Copyright Saul Youssef, May 2003
#
from Environment  import *
from DownloadArea import *
from FileGetter   import *

import os

class Download(Environment):
	type = 'download'
	title = 'Downloads'
	action = 'download'
	def __init__(self,prefix,file,downLoadDirectory):
		self.__file   = file
		self.__prefix = prefix
		self.url      = isUrl(prefix)
		self.__downLoadDirectory = downLoadDirectory

	def getter(self):
		if self.url: g = InternetFileGetter(self.__prefix,self.__file)
		else:        g =    LocalFileGetter(self.__prefix,self.__file)
		return g
#-- Set		
	def equal(self,d): return self.__file == d.__file and self.__prefix == d.__prefix
	def str(self): return self.__file+' from '+self.__prefix+' to '+self.__downLoadDirectory

#-- Compatible
	def compatible(self,d): 
		if self.__file==d.__file and not self.__prefix==d.__prefix:
			return Reason('Downloads ['+`self`+'] and ['+`d`+'] are incompatible.')
		else:
			return Reason()
#-- Satisfiable
	def satisfied(self):
		reason = Reason()
		if os.path.exists(fullpath(self.__downLoadDirectory)):
			d = DownloadArea(fullpath(self.__downLoadDirectory)); d.get()
			if not d.has(self.__file): reason.reason('File ['+`self`+'] has not been downloaded.')
		else:
			reason.reason("Download area ["+fullpath(self.__downLoadDirectory)+"] doesn't exist.")
		return reason
		
	def satisfiable(self): 
		if self.satisfied().isNull(): reason = Reason()
		else:
			reason = self.getter().gettable()
			if not os.path.exists(fullpath(self.__downLoadDirectory)):
				reason.append(Reason("Can't download to ["+self.__downLoadDirectory+"].  Directory doesn't exist."))
			if os.path.isfile(fullpath(self.__downLoadDirectory)):
				reason.append(Reason("Can't download to ["+self.__downLoadDirectory+"].  It's a file, not a directory."))
			if os.path.exists(os.path.join(fullpath(self.__downLoadDirectory),self.__file)):
				reason.append(Reason("File ["+self.__file+"] already exists in ["+self.__downLoadDirectory+"].  Can't download."))
		return reason
#-- Action
	def acquire(self):
		d = DownloadArea(fullpath(self.__downLoadDirectory)); d.get()
		reason = d.download(self.getter())
		return reason
	def retract(self):
		d = DownloadArea(fullpath(self.__downLoadDirectory)); d.get()
		reason = d.remove(self.__file)
		return reason
