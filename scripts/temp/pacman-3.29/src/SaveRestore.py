#
#	Copyright, Saul Youssef, December 2004
#
from Base        import *
from Environment import *
import Package,Execution

class RestoreFromUninstall(Environment):
	type   = 'restore'
	title  = 'Restore'
	action = 'restore saved files'
	
	def __init__(self,filename):
		if not os.path.basename(filename)==filename: abort('Syntax error ['+filename+'] must be a filename, not a path.')
		self._filename = filename
		self._par      = Package.Spec()
		self._dir      = ''
		
	def str  (self  ): return self._filename
	def equal(self,x): return self._filename==x._filename
	
	def satisfied(self): return Reason(`self`+' has not been restored.',not self.acquired)
	
	def acquire(self):
		r = Reason()
		if self._par == Package.Spec(): abort('Error in RestoreFromUninstall.')
		self._id  = `abs(hash(self._par._id()))`
		self._dir = os.path.join(pac_anchor,pacmanDir,'saves',self._id)
		
		if os.path.isdir(self._dir):
			if os.path.exists(os.path.join(self._dir,self._filename)):
				r = ask.re('restore','About to restore ['+self._filename+'].  OK?')
				if r.ok(): 
					verbo.log('restore','Restoring ['+self._filename+']...')
					r = Execution.execute('cp -r -f '+os.path.join(self._dir,self._filename)+' .')
		return r

	def retract(self):
		r = Reason()
		if self._par == Package.Spec(): abort('Error in RestoreSave.')
		
		if os.path.isdir(os.path.join(pac_anchor,pacmanDir,'saves')):
			if not os.path.exists(self._dir): r = Execution.execute('mkdir '+self._dir)
			if r.ok(): 
				r = ask.re('restore','About to save ['+self._filename+']. OK?')
				if r.ok(): 
					verbo.log('restore','Saving ['+self._filename+']...')
					rr = Execution.execute('cp -r -f '+self._filename+' '+self._dir)
		return r

	def removeSave(self):
		r = Reason()
		if not self._dir=='': 
			r = ask.re('restore','About to remove saved ['+self._filename+'] from the installation.  OK?')
			if r.ok(): 
				verbo.log('restore','Removing saved ['+self._filename+'] from the installation...')
				r = Execution.execute('rm -r -f '+os.path.join(self._dir,self._filename))
		return r

			
