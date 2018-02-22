#
#	Copyright, Saul Youssef, August 2003
#
from Access     import *
from Base       import *
from Computer   import *

def cacheToComp(cachename):
	username,computer,location = '','',''
	l1 = string.split(cachename,'@')
	if len(l1)>1:
		username = l1[0]
		name2 = ''
		for s in l1[1:]: name2 = name2 + s
		
		l2 = string.split(s,':')
		if len(l2)==2:
			host  = l2[0]
			location = l2[1]
		else:
			abort('['+cachename+'] is an illegal SSH cache.')
	else:
		username = getusername()
		if ':' in cachename:
			l2 = string.split(cachename,':')
			if len(l2)==2:
				host     = l2[0]
				location = l2[1]
			else:
				abort('['+cachename+'] is an illegal SSH cache.')
		else:
			abort('['+cachename+'] is an illegal SSH cache.')
	return host,location,username

class SSHAccess(Access):
	type = 'ssh directory'
	
	def __init__(self,location):
		self.location = location
		host,loc,username = cacheToComp(location)
		if username=='': username = getusername()
		self.computer = Computer(host,loc,username)
		
	def __repr__(self): return self.location
	def equal(self,x): return self.location==x.location
	
	def access(self): 
		r,files = self.names()
		return r.ok()
		
#	def names(self): return self.computer.listdir('.')
	def names(self): return self.namesPath()
	
	def namesPath(self,path='.'): return self.computer.listdir(path)
	
	def getFile(self,name,target=''):
		if target=='': target2 = name
		else:          target2 = target
		
		return self.computer.get(name,target2)
		
