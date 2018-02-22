#
#	Copyright, Saul Youssef, September, 2003
#
from Environment import *

def currentUser(): 
	c = CU()
	if len(c._stack)==0: return Reason("Too many cu()'s in Pacman source."),''
	else: 
		return Reason(),c._stack[-1]
		
def getCurrentUser():
	r,u = currentUser()
	r.require()
	return u

class CU(Environment):
	type    = 'cu'
	title   = 'Change Usernames'
	action  = 'change username'
	
	_stack = [getusername()]
	
	def __init__(self,username='-pop-'):
		if string.strip(username)=='': self.username = getCurrentUser()
		else:                          self.username = username
		self.__retract = ''
		
	def equal(self,x): return self.username==x.username and self.__retract==x.__retract
	def str(self): 
		if self.__retract == '': return self.username
		else:                    return self.username+' retract to '+self.__retract
	
	def satisfied(self):
		return Reason("["+`self`+"] hasn't been executed.",not self.acquired)
	def satisfiable(self): 
		if self.username=='-pop-' or self.username=='nonroot' or self.username=='non-root': return Reason()
		else:
			return Reason("Username ["+`self`+"] is not in the password file.",not userexists(self.username))
	def satisfy(self):
		reason = Reason()
		if self.username!='-pop-':
			if len(self._stack)==0: reason = Reason("Too many cu()'s in .pacman file source code.")
			else:
				self.userChooser()
				self.__retract = self._stack[-1]
				reason = ask.re('cu','OK to change from username ['+getusername()+'] to username ['+self.username+']?')
				if reason.ok():
					verbo.log('cu','Changing from username ['+getusername()+'] to username ['+self.username+']...')
					self._stack.append(self.username)
		else:
			if len(self._stack)==0: reason = Reason("Too many cu()'s in .pacman file source code.")
			else: self._stack.pop()
		self.acquired = 1
		return reason
	def restore(self):
		if self.__retract!= '': self._stack.append(self.__retract)
		self.acquired = 0
		return Reason()
		
	def userChooser(self):
		if    self.username=='*' or self.username=='': self.username = getusername()
		elif  self.username=='nonroot' or self.username=='non-root':
#-- first search the stack for an already chosen non-root user and take that automatically
			if getusername()=='root':
				got_one = 0
				for i in range(len(self._stack)-1,-1,-1):
					if self._stack[i]!='root' and \
					   self._stack[i]!='non-root' and \
					   self._stack[i]!='nonroot' and \
					   self._stack[i]!='*':
						self.username = self._stack[i]
						got_one = 1
						break
				if not got_one:
					user = 'root'
					while not (user!='root' and userexists(user)): 
						user = raw_input('Choose a non-root username: ')
						if not userexists(user): print 'User ['+user+'] does not exist.  Try again...'
					self.username = user
			else:
				self.username = getusername()
