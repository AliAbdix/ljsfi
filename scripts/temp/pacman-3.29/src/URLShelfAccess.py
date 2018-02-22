#
#	Copyright, Saul Youssef, October 2003
#
from FileGetter        import *
from LocalShelfAccess  import *
import tempfile

class URLShelfAccess(Access):
	type = 'url shelf'
	
	def __init__(self,url):
		head,tail = os.path.split(url)
		g = InternetFileGetter(head,tail)
		reason,file = g.getFile()
		reason.require()
		tmpfile = tempfile.mktemp()
		
		f = open(tmpfile,'w')
		for line in file: f.write(line)
		f.close()
		
		self.url = url
		self.location = url
		self.laccess = LocalShelfAccess(tmpfile)
		
	def __repr__(self): return self.url
	def equal(self,x):  return self.url==x.url
	
	def access(self): return self.laccess.access()
	def names(self):  return self.laccess.names ()
	def getFile(self,name,target2=''): return self.laccess.getFile(name,target2)

