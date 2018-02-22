#
#	Copyright, August 2003, Saul Youssef
#
from Environment import *
from Username    import *
import socket

class Selector:
	def title(self): return 'selector'
	def sel(self,E): abort('Missing sel in Selector.')

	def select(self,E):
		if hasattr(E,'__getitem__'):
			Es = copy.deepcopy(E)
			Es.empty()
			for e in E: 
				F = self.select(e)
				if hasattr(F,'__len__'):
					if len(F)>0: Es.extend(F)
				else:
					Es.extend(F)
		else:
			if self.sel(E): Es = copy.deepcopy(E)
			else:           Es = AND()
		return Es
		
	def select2(self,E):
		if self.sel(E):
			Es = copy.deepcopy(E)
		elif hasattr(E,'__getitem__') and not hasattr(E,'attach'):
			Es = AND()
			for e in E:
				Es.extend(self.select2(e))
		else:
			Es = AND()
		return Es
			
	def reduceBase(self,E,F):
		if self.sel(E): 
			E2 = copy.deepcopy(E)
			F.extend(E2)
		if hasattr(E,'__getitem__') and not hasattr(E,'attach'):
			for e in E: self.reduceBase(e,F)
			
	def reduce(self,E):
		F = AND()
		self.reduceBase(E,F)
		
		return F.removeDuplicates()
		
class UsernameSelector(Selector):
	def title(self): return 'Usernames'
	
	def sel(self,E):
		if ( E.type=='username' and not E==Username('*') and not E==Username()) or \
		   ( E.type=='cu'       and not E.username=='-pop-' and not E.username==getusername() ):
			return 1
		else:
			return 0

def impliesAccess(E): return exists(E,lambda e: e.type=='SSH access'    or \
                                                e.type=='Globus access' or \
						e.type=='add group'     or \
						e.type=='add user'      or \
						e.type=='work space')
def getPackages(E,select):
	Pacs = AND()
	if hasattr(E,'__getitem__') and not hasattr(E,'attach'):
		for e in E:
			if e.type=='package' or e.type=='depends':
				if select(e): Pacs.append(e)
			Pacs.extend(getPackages(e,select))
	return Pacs
	
class RemoteSelector(Selector):
	def title(self): return 'Remotes'
	def sel(self,E): return E.type=='remote installation' or E.type=='passive remote installation' or \
				E.type=='remote package' or E.type=='remote group'

class ShellSelector(Selector):
	def title(self): return 'Shell Commands'
	def sel(self,E): return E.type=='shell' or E.type=='shell dialogue' or E.type=='uinstall shell command'
	
class QuestionSelector(Selector):
	def title(self): return 'Questions'
	def sel(self,E): 
		return E.type=='choice' or \
		       ( E.type=='cd' and (len(E.path)>1 and E.path[0]=='?') )
	
class TypeSelector(Selector):
	type = ''
	def title(self): return self.type
	def sel(self,E): return E.type==self.type
	
class PackageSelector(TypeSelector):
	type = 'package'
	def title(self): return self.type
	def sel(self,E): return E.title=='Packages'
	
class NewUserSelector(TypeSelector):
	type = 'add user'
	def title(self): return 'Accounts'
	
class RegistrySelector(TypeSelector):
	type = 'register'
	def title(self): return 'Registry Entries'
	
class SSHAccessSelector(TypeSelector):
	type = 'SSH access'
	def title(self): return 'SSH access'
	
class GlobusAccessSelector(TypeSelector):
	type = 'Globus access'
	def title(self): return 'Globus access'
	
class NewGroupSelector(TypeSelector):
	type = 'add group'
	def title(self): return 'Groups'
	
class UserChosenDirectorySelector(TypeSelector):
	type = 'chosen directory'
	def title(self): return 'Work Areas'
	
class WorkSpaceSelector(TypeSelector):
	type = 'work space'
	def title(self): return 'Work Spaces'
	
class ContactSelector(TypeSelector):
	type = 'contact'
	def title(self): return 'Contacts'
	
#	
#class LocationSelector(TypeSelector):
#	type = 'location'
#	def title(self): return 'Extra Locations'
#
class ShellExecutedAsUserSelector(Selector):
	def title(self): return self.user+' shell commands'
	
	userstack = []
	currentUser = getusername()
	user = 'root'
	
	def sel(self,E):
		if E.type=='username': self.currentUser = E.str()
		if E.type=='cu': 
			if    E.username=='-' and len(self.userstack)>0: self.userstack.pop()
			else: self.userstack.append(E.username)
		
		if E.type=='shell' or E.type=='shell dialogue':
			if self.currentUser==self.user or (len(self.userstack)>0 and self.userstack[-1]==self.user):
				return 1
			else:
				return 0
		else:
			return 0

class ShellExecutedNotAsUserSelector(Selector):
	def title(self): return 'non-'+self.user+' shell commands'
	
	currentUser = getusername()
	userstack = []; userstack.append(getusername())
	user = 'root'
	
	def sel(self,E):
		if E.type=='username': 
			if     E.str()=='*': 
				pass
			elif   E.str()=='nonroot':
				if self.currentUser=='root': self.currentUser = 'nonroot'
				else: pass
			elif   E.str()=='non-root':
				if self.currentUser=='root': self.currentUser = 'non-root'
				else: pass
			else:
				self.currentUser = E.str()
		if E.type=='cu': 
			if    E.username=='-' and len(self.userstack)>0: self.userstack.pop()
			else: 
				if   E.username=='*':                  self.userstack.append(self.userstack[-1])
				elif E.username=='nonroot':
					if self.userstack[-1]=='root': self.userstack.append('nonroot')
					else:                          self.userstack.append(self.userstack[-1])
				elif E.username=='non-root':
					if self.userstack[-1]=='root': self.userstack.append('non-root')
					else:                          self.userstack.append(self.userstack[-1])
				else:
					self.userstack.append(E.username)
		
		if E.type=='shell' or E.type=='shell dialogue':
			if self.currentUser!=self.user and (len(self.userstack)>0 and self.userstack[-1]!=self.user):
				return 1
			else:
				return 0
		else:
			return 0
		
class UpdateAvailableSelector(Selector):
	def title(self): return 'Updates'
	
	def sel(self,E):
		if E.title=='Packages': return E.upd().hasupdate
		else:                   return 0
			
class UpdateImpliedSelector(Selector):
	def title(self): return 'Updates Implied'
	
	def sel(self,E):
		if E.type=='package' or E.type=='depends':
			return E.updateimplied
		else:
			return 0
