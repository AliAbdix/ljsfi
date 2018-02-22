#
#	Copyright Saul Youssef, July 2003
#
from StringAttr  import *
from WebPage     import *

class URL(Environment):
	type   = 'url'
	action = 'url'
	title  = 'URLs'
	
	def __init__(self,name,url,target='_blank'): 
		self.name,self.url,self.target = name,url,target
	
#-- Set
	def equal(self,u):  return self.name==u.name and self.url==u.url
	def __repr__(self): return self.str()
	def str(self): 
		return self.url+' ('+self.name+')'
#		if self.target=='': 
#			if self.url!='': return '<a href="'+self.url +'"><font color=#000000>'+self.name+'</font></a>'
#			else:            return '<a href="'+self.name+'"><font color=#000000>'+self.name+'</font></a>'
#		else:               
#			if self.url!='': return '<a href="'+self.url +'" target="'+self.target+'"><font color=#000000>'+self.name+'</font></a>'
#			else:            return '<a href="'+self.name+'" target="'+self.target+'"><font color=#000000>'+self.name+'</font></a>'

	def satisfiable(self): return Reason()
	def satisfied  (self): return Reason('url has not been acquired.',not self.acquired)
	def acquire    (self): 
		if isUrl(self.url): self.url = os.path.expandvars(self.url)
		else:               self.url = fullpath(self.url)
		self.target = os.path.expandvars(self.target)
		self.name = os.path.expandvars(self.name)
		return Reason()
	def retract(self): return Reason()

class Author(URL):
	type   = 'author'
	title  = 'Authors'
	action = 'author'
	
	def __init__(self,name,url):
		self.name = name
		if not isURL(url) and '@' in url: 
			self.url = 'mailto:'+url
		else:
			self.url = url
		self.target=''
		
	def __repr__(self): return 'author: '+self.str()

class Contact(Author):
	type   = 'contact'
	title  = 'Contacts'
	action = 'contact'

	def __repr__(self): return 'contact: '+self.str()
