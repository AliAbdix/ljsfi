#
#	Copyright, Saul Youssef, November 2004
#
from Base import *
import Access,Execution,InPath
import string,urlparse

class GSIAccess(Access.Access):
	type = 'gsi'
	
	def __init__(self,url):
		self.url0 = url
		self.url  = self.url0[:]
		self.url  = string.replace(self.url,'gsiftp://','http://')
		self.scheme,self.machine,self.path,self.parameters,self.query,self.fragid = urlparse.urlparse(self.url)
		self.scheme = 'gsiftp'
		self.location = self.url0[:]
	
	def __repr__(self): return self.url0
	def equal(self,x): return self.url0==x.url0
	
	def names(self): return self.namesPath()
	
	def namesPath(self,path=''):
		r,files = InPath.Which('globus-job-run').satisfied(),[]
		if r.ok():
			com = 'globus-job-run '+self.machine+' '+'/bin/ls'+' '+os.path.join(self.path,path)
			r = ask.re('gsi','About to execute ['+com+'].  OK?')
			if r.ok():
				r,output = Execution.executeBase(com)
				if r.ok():	
					files = string.split(output,'\n')
				else:		
					r = Reason(output)
		return r,files
				
	def access(self):
		r,files = self.namesPath(self.path)
		return r.ok()
		
	def getFile(self,name,target=''):
		target2 = os.path.join(os.getcwd(),name)
		if not target=='': target2 = target

		com = 'globus-url-copy '+os.path.join(self.url0,name)+' '+'file://'+target2
		r = ask.re('gsi','Fetching cache item via ['+com+'].  OK?')
		if r.ok():
			verbo.log('gsi','Fetching cache item via ['+com+']...')
		
			r,output = Execution.executeBase(com)
			if not r.ok(): r = Reason(output)
		return r

		
