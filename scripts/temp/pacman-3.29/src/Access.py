#
#	Copyright 2004, Saul Youssef
#
from Base      import *
from WebPage   import *
from Execution import *
import tempfile

_freeLock = {}

class Access(Set,HtmlOut,PrintOut):
	location = ''
	def __repr__(self): 
		r,nms = self.names()
		s = ''
		for name in nms: s = s + name + ' '
		return s
	def names   (self     ): abort('Missing names in Access.')
	def access  (self     ): abort('Missing access in Access.')
	 
	def accessName(self): return `self`
	def accessGettable(self):
		return Reason(`self`+' is not accessible.',not self.access())
		
	def getLines(self,name): 
		tmpfile = tempfile.mktemp()
		tmpfile = os.path.join(pac_anchor,pacmanDir,'tmp',os.path.basename(tmpfile))
		reason  = self.getFile(name,tmpfile)
		if reason.ok():
			try:
				f = open(tmpfile,'r')
				lines = f.readlines()
				f.close()
				removeFile(tmpfile)
			except (IOError,OSError):
				lines = []
				reason = Reason("Error reading ["+name+"].")
			return reason,lines
		else:
			return reason,[]
	def getFile (self,name,target): abort('Missing getFile in Access.')
	def getDirectory(self,target,select=lambda n: 1): 
		reason = Reason()
		reason,names = self.names()
		if reason.ok():
			for name in names:
				if select(name): 
					reason = self.getFile(name,target)
					if not reason.ok(): break
		return reason
	def getObj  (self,name): 
		if not os.path.exists('tmp'):
			execute('mkdir tmp')
			newtmp = 1
		else:
			newtmp = 0
		tmpfile = os.path.join('tmp',name)
		removeFile(tmpfile)
		
		reason = self.getFile(name,tmpfile)
		obj = None
		if reason.ok():
			try:	
				obj = get (tmpfile)
				removeFile(tmpfile)
			except (IOError,OSError):
				reason = Reason("["+name+"] does not contain an object.")
		if newtmp: execute('rm -r -f tmp')
		return reason,obj
		
	def lockCheck(self):
		r,names = self.namesPath()
		if r.ok() and 'lock' in names and not _freeLock.has_key(`self`):
			r,lines = self.getLines('lock')
			message = ''
			for line in lines:
				if len(line)>0 and not string.strip(line[:-1])=='':
					message = line[:-1]
					break
			if not message=='': r = Reason(message)
			else:               r = Reason()
		else:
			r = Reason()
		return r
		
	def has     (self,name):
		r,names = self.names()
		return r,name in names
			
