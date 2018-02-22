#
#	Copyright, Saul Youssef, 2004
#
from Base        import *
from Environment import *
import os

class CD(Environment):
	type   = 'cd'
	title  = 'Current Directories'
	action = 'cd'
	current = 'PWD'
	
	__stack = []
	
	def __init__(self,path='-'): 
		self.path      = path
		self.__retract = ''
			
#-- Set
	def equal(self,x): return self.path==x.path
	def str(self):
		if self.path=='-': 
			if self.__retract=='':	return '-pop-'
			else:                   return '-pop-, retract to '+self.__retract
		else:              
			if self.__retract=='':  return self.path
			else:                   return self.path+', retract to '+self.__retract
#-- Compatible
	def compatible(self,cd): return Reason()
	
#-- Satisfiable
	def satisfied(self): 
		if self.acquired: return Reason()
		else:             return Reason("["+`self`+"] hasn't been executed.")
	def satisfiable(self): return Reason()

#-- Action
	def satisfy(self):
		reason = Reason()
		if len(string.strip(self.path))>=1 and string.strip(self.path)[0]=='?': 
			self.path = cookieDirectory(self.path[1:])
		if self.path=='-':
			if len(self.__stack)==0: 
				reason.reason("Popped off the CD stack.")
			else:
				if ask('cd','About to cd to ['+self.__stack[-1]+'] from ['+os.getcwd()+'].'):
					verbo.log('cd','cd-ing from ['+os.getcwd()+'] to ['+self.__stack[-1]+']...')
					try:
						location = fullpath(os.getcwd())
						os.chdir(self.__stack[-1])
						os.environ[self.current] = os.getcwd()
						self.__stack.pop()
						if not self.acquired: self.__retract = location
						self.acquired = 1
						self.lastsat  = 1
#						self.__retract = location
					except OSError:
						self.lastfail = 1
						reason.reason("Failed [cd "+self.__stack[-1]+"].")
				else:
					reason.reason('No permission to cd to ['+self.path+'] from ['+os.getcwd()+'].')
		else:
			self.path = fullpath(self.path)
			if ask('cd','About to cd to ['+fullpath(self.path)+'] from ['+os.getcwd()+'].'):
				verbo.log('cd','cd-ing from ['+os.getcwd()+'] to ['+fullpath(self.path)+']...')
				try:
					location = fullpath(os.getcwd())
					os.chdir(fullpath(self.path))
					os.environ[self.current] = os.getcwd()
					self.__stack.append(location)
					if not self.acquired: self.__retract = location
					self.acquired = 1
					self.lastsat  = 1
#					self.__retract = location
				except OSError:
					self.lastfail = 1
					reason.reason('Failure attempting to ['+`self`+'] at ['+os.getcwd()+'].')
			else:
				reason.reason('No permission to cd to ['+self.path+'] from ['+os.getcwd()+'].')
		return reason
		
	def restore(self):
		reason = Reason()
		if self.acquired:
			if ask('cd','About to cd to ['+self.__retract+'] from ['+os.getcwd()+'].'):
				verbo.log('cd','cd-ing from ['+os.getcwd()+'] to ['+self.__retract+']...')
				try:
					if self.type=='location': print 'Changing location to ['+self.__retract+']...'
					os.chdir(self.__retract)
					os.environ[self.current] = os.getcwd()
					self.__retract = ''
					self.acquired  = 0
					self.lastsat   = 0
					self.lastfail  = 0
				except OSError:
					reason.reason("Failure attempting to cd to ["+self.__retract+"] at ["+os.getcwd()+"].")
			else:
				reason.reason('No permission to cd to ['+self.__retract+'] from ['+os.getcwd()+'].')
		if not reason.ok(): 
			if debug.any(): 'Warning: ',reason
			reason = Reason()
		return reason
