#
#	Copyright, December 2003, Saul Youssef
#
from StringAttr import *
from Execution  import *
from FileMode   import *
import os

class FileAccess(Environment):
	type   = 'file access'
	title  = 'File Access'
	action = 'set file access'
	
	def __init__(self,path,mode,action='on'):
		self._path   = path
		self._mode   = mode
		self._action = action
		self._savemode = None
		self.lastsat  = 0
		self.lastfail = 0
		
	def str(self): return '['+self._path+'] set to ['+self._mode+' '+self._action+']'
	def equal(self,fa):
		return self._path    == fa._path and \
		       self._mode    == fa._mode and \
		       self._action  == fa._action

	def satisfied(self): return Reason(`self`+' has not been attempted yet.',not self.acquired)

	def sat(self):
		path = fullpath(self._path)
		reason = Reason('['+path+'] does not exist.',not os.path.exists(path))
		if reason.ok(): 
			m = FileMode(path)
			if   self._mode=='worldExecute':
				if self._action=='on':
					reason = Reason('['+path+'] is not ['+self._mode+' on].',not m.worldExecute  ())
				else: 
					reason = Reason('['+path+'] is not ['+self._mode+' off].',    m.worldExecute  ())
			elif self._mode=='worldWrite':
				if self._action=='on':
					reason = Reason('['+path+'] is not ['+self._mode+' on].',not m.worldWrite    ())
				else:
					reason = Reason('['+path+'] is not ['+self._mode+' off].',    m.worldWrite    ())
			elif self._mode=='worldRead':
				if self._action=='on':
					reason = Reason('['+path+'] is not ['+self._mode+' on].',not m.worldRead     ())
				else:
					reason = Reason('['+path+'] is not ['+self._mode+' off].',    m.worldRead     ())
			elif self._mode=='groupExecute':
				if self._action=='on':
					reason = Reason('['+path+'] is not ['+self._mode+' on].',not m.groupExecute  ())
				else:
					reason = Reason('['+path+'] is not ['+self._mode+' off].',    m.groupExecute  ())
			elif self._mode=='groupWrite':
				if self._action=='on':
					reason = Reason('['+path+'] is not ['+self._mode+' on].',not m.groupWrite    ())
				else:
					reason = Reason('['+path+'] is not ['+self._mode+' off].',    m.groupWrite    ())
			elif self._mode=='groupRead':
				if self._action=='on':
					reason = Reason('['+path+'] is not ['+self._mode+' on].',not m.groupRead     ())
				else:
					reason = Reason('['+path+'] is not ['+self._mode+' off].',    m.groupRead     ())
			elif self._mode=='ownerExecute':
				if self._action=='on':
					reason = Reason('['+path+'] is not ['+self._mode+' on].',not m.ownerExecute  ())
				else:
					reason = Reason('['+path+'] is not ['+self._mode+' off].',    m.ownerExecute  ())
			elif self._mode=='ownerWrite':
				if self._action=='on':
					reason = Reason('['+path+'] is not ['+self._mode+' on].',not m.ownerWrite    ())
				else:
					reason = Reason('['+path+'] is not ['+self._mode+' off].',    m.ownerWrite    ())
			elif self._mode=='ownerRead':
				if self._action=='on':
					reason = Reason('['+path+'] is not ['+self._mode+' on].',not m.ownerRead     ())
				else:
					reason = Reason('['+path+'] is not ['+self._mode+' off].',    m.ownerRead     ())
			else:
				reason = Reason('Unknown file access self._mode ['+self._mode+'].')
		return reason
	def verify(self): 
		r = self.sat()
		if not r.ok(): 
			self.lastsat  = 0
			self.acquired = 0
		return r
	def satisfiable(self): return Reason()
	def acquire(self):
		path = fullpath(self._path)
		reason = Reason('['+path+'] does not exist.',not os.path.exists(path))
		if reason.ok():
			self._path = path
			self._savemode = FileMode(self._path)
			m = FileMode(self._path)
			
			if   self._mode=='worldExecute':
				if m.setWorldExecute(self._action): pass
				else:                      reason = Reason(`self`+' attempt has failed.')
			elif self._mode=='worldWrite':
				if m.setWorldWrite(self._action): pass
				else:                      reason = Reason(`self`+' attempt has failed.')
			elif self._mode=='worldRead':
				if m.setWorldRead(self._action): pass
				else:                      reason = Reason(`self`+' attempt has failed.')
			
			if   self._mode=='groupExecute':
				if m.setGroupExecute(self._action): pass
				else:                      reason = Reason(`self`+' attempt has failed.')
			elif self._mode=='groupWrite':
				if m.setGroupWrite(self._action): pass
				else:                      reason = Reason(`self`+' attempt has failed.')
			elif self._mode=='groupRead':
				if m.setGroupRead(self._action): pass
				else:                      reason = Reason(`self`+' attempt has failed.')
				
			if   self._mode=='ownerExecute':
				if m.setOwnerExecute(self._action): pass
				else:                      reason = Reason(`self`+' attempt has failed.')
			elif self._mode=='ownerWrite':
				if m.setOwnerWrite(self._action): pass
				else:                      reason = Reason(`self`+' attempt has failed.')
			elif self._mode=='ownerRead':
				if m.setOwnerRead(self._action): pass
				else:                      reason = Reason(`self`+' attempt has failed.')
		return reason

	def retract(self):
		if   self._savemode==None: return Reason()
		elif self._savemode.set():
			self._savemode = None
			return Reason()
		else:
			return Reason()
#			return Reason("Can't retract ["+`self`+"].")
		
class HasFileAccess(FileAccess):
	type   = 'file access'
	title  = 'File Access'
	action = 'set file access'

	def str    (self): return '['+self._path+'] has ['+self._mode+' '+self._action+']'
	def acquire(self): return self.sat()
	def retract(self): return Reason()

def collect_paths(paths,dirname,names):
	for name in names:
		paths.append(fullpath(os.path.join(dirname,name)))

class DirTreeAccess(Environment):
	type   = 'directory tree access control'
	title  = 'Directory Tree Access Controls'
	action = 'set directory tree access'
	
	def __init__(self,path,mode,action='on'):
		self._path   = path
		self._mode   = mode
		self._action = action
		self._paths  = []
		self._accs   = []
		
	def str(self): return self._path+'/... set to '+self._mode+' '+self._action
	def equal(self,x): return \
		self._path   == x._path   and \
		self._mode   == x._mode   and \
		self._action == x._action and \
		self._paths  == x._paths
		
	def update_paths(self):
		self._paths = []
		os.path.walk(self._path,collect_paths,self._paths)
		
	def satisfied(self):
		if self.acquired: return Reason()
		else:
			reason = Reason('['+self._path+'] does not exist.',not os.path.exists(self._path))
			if reason.ok():
				reason = Reason('['+self._path+'] is not a directory.',not os.path.isdir(self._path))
			if reason.ok():
				self.update_paths()
				for path in self._paths:
					reason = FileAccess(path,self._mode,self._action).satisfied()
					if not reason.ok(): break
		return reason
		
	def acquire(self):
		reason = Reason()
		self._path = fullpath(self._path)
		self.update_paths()
		for path in self._paths:
			a = FileAccess(path,self._mode,self._action)
			reason = a.satisfy()
			if reason.ok(): self._accs.append(copy.deepcopy(a))
			else:           break
		return reason

	def retract(self):
		reason = Reason()
		for i in range(len(self._accs)-1,-1,-1):
			reason = self._accs[-1].restore()
			if reason.ok(): del self._accs[-1]
			else:           break
		return reason
		
class WriteProtectR(Environment):
	type   = 'write protect directory tree'
	title  = 'Write Protect Directory Trees'
	action = 'write protect directory tree' 
	
	def __init__(self,path): self.path = path
	def str(self): return self.path
	
	def equal(self,x): return self.path==x.path
	
	def satisfiable(self): return Reason()
	def satisfied(self): return Reason("Directory tree ["+self.path+"] has not yet been write protected.",not self.acquired)
	def acquire(self):
		path = fullpath(self.path)
		reason = Reason("Directory tree ["+path+"] does not exist.",not os.path.isdir(path))
		if reason.ok():
			self.path = path
			reason = execute('chmod -R a-w '+self.path)
		return reason
	def retract(self): return execute('chmod -R a+w '+self.path)
	
