#
#	DownloadArea, Copyright Saul Youssef, May, 2003
#
import os,urlparse
import pickle,copy
from Base       import *
from FileGetter import *

class DownloadArea:
	def __init__(self,dire):
		if     os.path.isfile(dire): abort("Can't download to ["+dire+"]. It's a file, not a directory.")
		if not os.path.exists(dire): abort("Can't download to ["+dire+"]. Directory doesn't exist.")
		
		self.__dir   = dire
		self.__fir   = self.__dir
		self.__ddb   = {}
			
	def __repr__(self): return 'Download Area ['+self.__fir+'] contains '+`self.__ddb`
	def display(self):
		print 'Download Area ['+self.__fir+'] contains:'
		for filename,g in self.__ddb.items():
			print filename,g
			
	def download(self,fileGetter):
		r = Reason()
		self.get()
		if self.__ddb.has_key(fileGetter.filename):
			r.reason("File to be downloaded ["+fileGetter.filename+"] already exists.")
		else:
			if not switch('quiet'): print 'Downloading ['+fileGetter.filename+'] from ['+fileGetter.source()+']...'
			r = fileGetter.get(self.__fir)
			if r.isNull(): self.__ddb[fileGetter.filename] = fileGetter
		self.put()
		return r
		
	def getPath(self,filename):
		if self.__ddb.has_key(filename): return 1,os.path.join(self.__fir,filename)
		else:                            return 0,''
		
	def getGetter(self,filename):
		if self.__ddb.has_key(filename): return 1,self.__ddb[filename]
		else:                            return 0,FileGetter()
		
	def has(self,filename): 
		got_it,path = self.getPath(filename)
		if got_it: return os.path.exists(path)
		else:      return 0
		
	def remove(self,filename):
		reason = Reason()
		self.get()
		if self.__ddb.has_key(filename): 
			try: 
				os.remove(os.path.join(self.__fir,filename))
				del self.__ddb[filename]
			except (IOError, OSError): 
				reason.reason("Failed to remove ["+os.path.join(self.__fir,filename)+"].")
		self.put()
		return reason
		
	def removeAll(self):
		for file,getter in self.__ddb.items(): 
			if not self.remove(file).isNull(): abort("Can't remove file ["+file+"].")
		
	def updateAll(self):
		for file,getter in self.__ddb.items():
			self.remove(file)
			self.download(getter)
			
	def put(self):
		db = open(os.path.join(self.__fir,'download.db'),'w')
		pickle.dump(self,db)
		db.close()

	def get(self):
		if os.path.exists(os.path.join(self.__fir,'download.db')):
			db = open(os.path.join(self.__fir,'download.db'),'r')
			foo = pickle.load(db)
			self.__dir = foo.__dir
			self.__fir = foo.__fir
			self.__ddb = foo.__ddb
			db.close()
			return 1
		else:   
			return 0
			
