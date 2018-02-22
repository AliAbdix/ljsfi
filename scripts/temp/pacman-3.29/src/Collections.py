#
#	Copyright, 2004, Saul Youssef
#
from Environment import *
from Username    import *
	
def packageSub(E):
	q = 0
	if hasattr(E,'__getitem__'): q = exists(E,lambda e: e.title=='Packages' or packageSub(e))
	return q

class SubDisplay(Collection):
	def __init__(self): self._checked = {}
		
	def __call__(self,E): return E.title=='Packages'
		
	def quit(self,E):
		q = 0
		if E.title=='Packages' or E.type=='AND' or E.type=='OR':
			if E.title=='Packages':
				if self._checked.has_key(E._hash):
					q = self._checked[E._hash]
				else:
					q = not packageSub(E)
					self._checked[E._hash] = q
			else:
				q = not packageSub(E)
		return q


class ResetCacheNameApplication(Application):
	def __init__(self,newCacheName): 
		self._done = {}
		self._toquit = {}
		self.newCacheName = newCacheName
		
	def __call__(self,E):
		reason = Reason()
		if E.type=='package':
			if E.check():
				if not self._done.has_key(E._hash):
					reason = E.resetCacheName(self.newCacheName)
					if reason.ok(): self._done[E._hash] = ''
			else:
				reason = E.resetCacheName(self.newCacheName)
		return reason
		
	def quit(self,E):
		q = 0
		if E.type=='package' and E.check():
			if self._toquit.has_key(E._hash): 
				q = 1
			else:
				self._toquit[E._hash] = ''
		return q

class AcquiredCollection(Collection):
	def __init__(self):
		self._done = {}
		
	def __call__(self,E): 
		return not (E.type=='package' or E.type=='AND' or E.type=='OR') and E.acquired
		
	def quit(self,E):
		q = 0
		if E.type=='package' and E.check():
			if self._done.has_key(E._hash): 
				q = 1
			else:
				self._done[E._hash] = ''
		return q
		
class Atomize(Collection):
	def __call__(self,E): return not (E.type=='package' or E.type=='AND' or E.type=='OR' or E.type=='package list' or E.type=='installation')
	def quit(self,E): return E.type=='package'

class CollectTypeExcept(Collection):
	def __init__(self,cType,qType=''):
		self.ctype = cType
		self.qtype = qType
		
	def __call__(self,E): return E.type==self.ctype
	def quit(self,E): return self.qtype!='' and E.type==self.qtype

class CountPackage:
	def __init__(self): 
		self._count = {}
		
	def __call__(self,E):
		if hasattr(E,'__getitem__'):
			if E.type=='package':
				if self._count.has_key(E._hash):
					count = self._count[E._hash]
				else:
					count = 1
					for e in E: count = count + self(e)
					self._count[E._hash] = count
			else:
				count = 0
				for e in E: count = count + self(e)
		else:
			count = 0
		return count

class CollectTypeListExcept(Collection):
	def __init__(self,tList,qType=''):
		self.ctype = tList
		self.qtype = qType
		
	def __call__(self,E):
		return E.type in self.ctype
	def quit    (self,E):
		return (not self.qtype=='') and E.type==self.qtype
		
class CollectFromPackage(Collection):
	def __init__(self,*tList): self.ctype = tList
	def __call__(self,E): return E.type in self.ctype
	def quit(self,E): return E.type=='package'
#
#class ImpliesAccessCollection(Collection):
#	def __init__(self):
#		self._done = {}
#		self.subcol = CollectFromPackage('SSH access','Globus access','add group','add user','work space')
#	def __call__(self,E): 
#		return E.type=='package' and len(E.collect(self.subcol))>0
#	def     quit(self,E): 
#		q = E.type=='package'
#		return q

class WebApplication(Application):
	def __init__(self):
		self._done = {}
		self.userstack = []
		self.currentUser = getusername()
		
		self.priviledged = ['root']
		
		self.updates            = AND()
		self.usernames          = AND() 
		self.questions          = AND()
		self.priviledgedShells  = AND()
		self.shells             = AND()
		self.impliesAccess      = AND()
		self.sshAccess          = AND()
		self.globusAccess       = AND()
		self.groups             = AND()
		self.groupadd           = AND()
		self.useradd            = AND()
		self.workspaces         = AND()
		self.remotes            = AND()
		self.emails             = AND()
		
#		self.verb = verbo('web')
		self.verb = 0
		
	def remoteSelector(self,E):
		if E.type=='remote installation' or E.type=='passive remove installation' or \
		   E.type=='remote package' or E.type=='remote group' or \
		   E.type=='monitor remote package':
			self.remotes.append(E)
		
	def updatesAvailableSelector(self,E):
		if E.title=='Packages':
			if E.upd().hasupdate:
				self.updates.append(E)
		
	def usernameSelector(self,E):
		if ( E.type=='username' and not E==Username('*') and not E==Username()) or \
		   ( E.type=='cu'       and not E.username=='-pop-' and not E.username==getusername()):
		   	self.usernames.append(E)
			
	def questionSelector(self,E):
		if E.type=='choice' or \
			( E.type=='cd' and (len(E.path)>1 and E.path[0]=='?' ) ):
			self.questions.append(E)
			
	def impliesAccessSelector(self,E):
		if E.type=='package':
			Es = E.env().collect(CollectFromPackage('SSH access','Globus access','add group','add user','work space'))
			if len(Es)>0: 
				self.impliesAccess.append(E)
		
	def sshAccessSelector(self,E):
		if E.type=='SSH access': self.sshAccess.append(E)
		
	def globusAccessSelector(self,E):
		if E.type=='Globus access': self.globusAccess.append(E)
		
	def groupaddSelector(self,E):
		if E.type=='add group': self.groupadd.append(E)
		
	def useraddSelector(self,E):
		if E.type=='add user': self.useradd.append(E)
		
	def workspaceSelector(self,E):
		if E.type=='work space': self.workspaces.append(E)
		
	def outgoingEmailSelector(self,E):
		if E.type=='mail': self.emails.append(E)
	
	def __call__(self,E):
		reason = Reason()
		
		if not (E.type=='package' and E.check() and self._done.has_key(E._hash)):
			if E.type=='username': self.currentUser = E.str()
			if E.type=='cu':
				if 	E.username=='-' and len(self.userstack)>0: self.userstack.pop()
				else: self.userstack.append(E.username)
			if E.type=='shell' or E.type=='shell dialogue' or \
			   E.type=='shell output contains' or E.type=='shell output LE' or \
			   E.type=='shell output EQ' or E.type=='shell output GE':
				if ( self.currentUser in self.priviledged ) or (len(self.userstack)>0 and self.userstack[-1] in self.priviledged):
					self.priviledgedShells.append(E)
				else:
					self.shells.append(E)

			self.updatesAvailableSelector(E)
			self.        usernameSelector(E)	
			self.        questionSelector(E)
			self.   impliesAccessSelector(E)
			self.       sshAccessSelector(E)
			self.    globusAccessSelector(E)
			self.        groupaddSelector(E)
			self.         useraddSelector(E)
			self.       workspaceSelector(E)
			self.          remoteSelector(E)
			self.   outgoingEmailSelector(E)
		
			if self.verb and E.type=='package': print 'Outlook ['+E.name+']...'
		
		return reason
		
	def quit(self,E): 
		q = 0
		if E.type=='package' and E.check():
			if self._done.has_key(E._hash):
				q = 1
			else:
				self._done[E._hash] = ''
				q = 0
		return q
		
