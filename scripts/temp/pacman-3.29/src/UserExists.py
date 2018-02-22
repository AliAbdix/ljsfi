#
#	Copyright, August 2003, Saul Youssef
#
from Environment import *
from StringAttr  import *
from Execution   import *
import pwd,grp,socket

def groupexists(name):
	gotit = 0
	try:
		grp.getgrnam(name)
		gotit = 1
	except KeyError:
		gotit = 0
	return gotit

class GroupExists(StringAttr):
	type    = 'group exists'
	title   = 'Groups Exist'
	action  = 'test if group exists'
	
	def satisfied  (self): return Reason('The user group ['+self.value+'] has not been created on ['+socket.gethostname()+'].',not groupexists(self.value))
#	def satisfiable(self): return self.satisfied()
	def acquire    (self): return self.satisfied()
	def retract    (self): return Reason()
	
class GroupAdd(GroupExists):
	type   = 'add group'
	title  = 'Add User Groups'
	action = 'add user group'
	
#	def satisfiable(self): 
#		if self.satisfied(): return Reason()
#		else:                return fileInPath('groupadd')
	def acquire    (self): 
		verbo.log('users','About to add user group ['+self.value+']...')
		reason = ask.re('acc','OK to add user group ['+self.value+']?')
		if reason.ok(): reason = execute('groupadd '+self.value)
		return reason
	def retract    (self): 
		reason = Reason()
		if groupexists(self.value): 
			verbo.log('users','About to remove user group ['+self.value+']...')
			reason = ask.re('acc','OK to remove user group ['+self.value+']?')
			if reason.ok(): reason = execute('groupdel '+self.value)
		return reason
		
class UserAdd(Environment):
	type    = 'add user'
	title   = 'Add Users'
	action  = 'add user if necessary'
	
	def __init__(self,username,group='- any -',shell='/bin/sh',hdir='',homedir=1):
		self.username = username
		self.group    = group
		self.shell    = shell
		self.hdir     = hdir
		self.homedir  = homedir
	def str(self): 
		if self.group=='- any -': s = 'username: '+self.username
		else:   
			s = 'username: '+self.username+', group: '+self.group+', shell: '+self.shell               
		return s
	def equal(self,x):  return self.username==x.username and self.group==x.group
	
#-- Satisfiability
	def satisfied(self): 
		gotit,uid,gid = userids(self.username)
		if gotit:
			try:
				groupname = grp.getgrgid(gid)[0]
			except KeyError:
				return Reason('User ['+self.username+'] group does not exist.')
				
			if groupname==self.group or self.group=='- any -': return Reason()
			else:
				return Reason('User ['+self.username+'] exists but is not in group ['+self.group+'].')	
		else:
			return Reason('No user ['+self.username+'] has an account.')
			
#	def satisfiable(self): 
#		if self.satisfied(): return Reason()
#		else:                return fileInPath('groupadd')

	def acquire(self): 
		reason = Reason()
		if self.group=='- any -': 
			if self.homedir: 
				if groupExists(self.username):
					verbo.log('users','About to create user account ['+self.username+']...')
					reason = ask.re('acc','OK to create user account ['+self.username+']?')
					if reason.ok():
						if self.hdir=='': reason = execute('useradd -m -c pacman -g '+self.username+' -s '+self.shell+' '+self.username)
						else:             reason = execute('useradd -m -c pacman -d '+self.hdir+' -g '+self.username+' -s '+self.shell+' '+self.username)
				else:
					reason = Reason("Group ["+self.username+"] doesn't exist.")
			else:            
				return execute('useradd -M -c pacman -g '+self.username+' -s '+self.shell+' '+self.username)
		else:                     
			if self.homedir: 
				if groupExists(self.group):
					verbo.log('users','About to create user account ['+self.username+']...')
					reason = ask.re('acc','OK to create user account ['+self.username+']?')
					if reason.ok():
						if self.hdir=='': reason = execute('useradd -m -c pacman -g '+self.group+   ' -s '+self.shell+' '+self.username)
						else:             reason = execute('useradd -m -c pacman -d '+self.hdir+' -g '+self.group+   ' -s '+self.shell+' '+self.username)
				else:
					reason = Reason("Group ["+self.group+"] doesn't exist.")
			else:            
				reason = execute('useradd -M -c pacman -g '+self.group+   ' -s '+self.shell+' '+self.username)
		if reason.ok(): print 'New user account ['+`self`+'] created...'
		return reason
		
	def retract(self): 
		reason = Reason()
		verbo.log('users','About to remove user account ['+self.username+']...')
		reason = ask.re('acc','OK to remove user account ['+self.username+']?')
		if reason.ok():
			if self.homedir: reason = execute('userdel -r '+self.username)
			else:            reason = execute('userdel '+   self.username)
		return reason

class UserExists(UserAdd):
	type   = 'user exists'
	title  = 'User Exists'
	action = 'check for user'
	
#	def satisfiable(self): return self.satisfied()
	def satisfy    (self): return self.satisfied()
	def restore    (self): return Reason()
	

	
