#
#	Copyright Saul Youssef, 2004
#
from Base         import *
from Environment  import *
import FileMode
import os

def getInpaths(path,pre='',expaths=[]):
	if os.path.isfile(os.path.join(path,pre)):
		try:
			if FileMode.FileMode(os.path.join(path,pre)).ownerExecute():
				expaths.append(os.path.join(pre))
		except OSError:
			print "Can't read ["+os.path.join(path,pre)+"].  Skipping..."
	elif os.path.isdir(os.path.join(path,pre)):
		try:
			filenames = os.listdir(os.path.join(path,pre))
		except OSError:
			print "Can't read ["+os.path.join(path,pre)+"].  Skipping..."
			filenames = []
		for filename in filenames: getInpaths(path,os.path.join(pre,filename),expaths)

class Path(Environment):
	type   = 'path'
	title  = 'Paths'
	action = 'add to path'
	
	_dirs = {}
	
	def __init__(self,path,env='PATH',option='front',filename='',force=allow('bad-paths')):
		self.value  = path
		self.env    = env
		self.file   = filename
		self.option = option
		if   contains(option,'front'): self.option = 'front'
		elif contains(option,'back' ): self.option = 'back'
		self._force = force
		if contains(option,'nocheck') or contains(option,'no-check') or contains(option,'overwrite'): self._force=1

	def equal(self,x): return self.env==x.env and self.value==x.value
	def str(self): 
		return self.value+' added to '+self.env
		
	def clashes(self):
		r = AllReason()
		newpaths = []
		getInpaths(self.value,'',newpaths)
		if not self._force and self._dirs.has_key(self.env):
			for d in self._dirs[self.env]:
				verbo.log('path','Checking if ['+`self`+'] clashes with ['+d+']...')
				if not fullpath(d)==fullpath(self.value):
					oldpaths = []
					getInpaths(d,'',oldpaths)
					for n in newpaths:
						if n in oldpaths: r.reason("Path ["+n+"] is also in ["+d+"].")
			if len(r)>0: r.headline = "Can't add ["+self.value+"] to path variable ["+self.env+"]"
		return r	

	def satisfied(self):
		r = Reason()
		if self.acquired:
			if os.environ.has_key(self.env):
				v = os.environ[self.env]
				vl = string.split(v,os.pathsep)
				if not self.value in vl: r.reason('['+self.value+'] is no longer in ['+self.env+'].')
			else:
				r = Reason('['+self.value+'] is no longer in ['+self.env+'].')
		else:
			r = Reason('Path variable ['+self.env+'] has not been set.')
		return r
	def satisfiable(self): return Reason()
	def setup      (self): return self.satisfy()
		
	def acquire(self):
		r = Reason()
		self.value = fullpath(self.value)
		if self._force or os.path.isdir(self.value):
			if not (self._dirs.has_key(self.env) and self.value in self._dirs[self.env]) and not self._force: r = self.clashes()

			if r.ok():
				if not self._dirs.has_key(self.env): self._dirs[self.env] = []
				self._dirs[self.env].append(self.value)

				if os.environ.has_key(self.env):
					verbo.log('path','About to add ['+self.value+'] to ['+self.env+']...')
					r = ask.re('path','OK to add ['+self.value+'] to ['+self.env+']?')
					if r.ok():
						v0 = os.environ[self.env]
						if contains(self.option,'back'): os.environ[self.env] =         v0 + os.pathsep + self.value
						else:                            os.environ[self.env] = self.value + os.pathsep + v0
#						if   self.option=='front': os.environ[self.env] = self.value + os.pathsep + v0
#						elif self.option== 'back': os.environ[self.env] =         v0 + os.pathsep + self.value
#						else: abort('Unknown option in Paths ['+self.option+"] must be 'front' or 'back'.")
						verbo.log('path',self.env+'='+os.environ[self.env]+'...')
				else:
					verbo.log('path','About to set ['+self.env+'] to ['+self.value+']...')
					r = ask.re('path','OK to set ['+self.env+'] to ['+self.value+']?')
					if r.ok():
						os.environ[self.env] = self.value
						verbo.log('path',self.env+'='+os.environ[self.env]+'...')
		else:
			if not self._force:
				verbo.log('path',"["+self.value+"] is not a directory.  Can't add to path variable ["+self.env+"].")
				r = Reason("["+self.value+"] is not a directory.  Can't add to path variable ["+self.env+"].")
		return r
		
	def retract(self):
		r = Reason()
		if self._dirs.has_key(self.env):
			if self.value in self._dirs[self.env]: self._dirs[self.env].remove(self.value)
			
		if os.environ.has_key(self.env):
			v = os.environ[self.env]
			vl = string.split(v,os.pathsep)
			if self.value in vl:
				verbo.log('path','About to remove ['+self.value+'] from ['+self.env+']...')
				r = ask.re('path','OK to remove ['+self.value+'] from ['+self.env+']?')
				if r.ok(): 
					s = ''; hit = 0
					for x in vl:
						if x==self.value and not hit: 
							hit = 1
						else:
							if s=='': s = s + x
							else:     s = s + os.pathsep + x
					os.environ[self.env] = s
					if os.environ[self.env]=='': 
						verbo.log('path','About to unset ['+self.env+']...')
						r = ask.re('path','OK to unsetenv ['+self.env+']?')
						if r.ok():
							del os.environ[self.env]
					else:
						verbo.log('path',self.env+'='+os.environ[self.env]+'...')
		return r

	def shellOut(self,csh,sh,py,pl,ksh):
		if self.acquired:
			csh.write('if ($?'+self.env+') then \n')
			if contains(self.option,'back'):
				csh.write('        setenv '+self.env+' '+'${'+self.env+'}'+os.pathsep+self.value+'\n')
			else:
				csh.write('        setenv '+self.env+' '+self.value+os.pathsep+'${'+self.env+'}\n')
			csh.write('else\n')
			csh.write('        setenv '+self.env+' '+self.value+'\n')
			csh.write('endif\n')
		
			if   contains(self.option,'back' ): sh.write(self.env+'="'+'$'+self.env+os.pathsep+self.value+'"\n')
			else:                               sh.write(self.env+'="'+self.value+os.pathsep+'$'+self.env+'"\n')
			sh.write('export '+self.env+'\n')
		
			if   contains(self.option,'back' ): ksh.write(self.env+'="'+'$'+self.env+os.pathsep+self.value+'"\n')
			else:                               ksh.write(self.env+'="'+self.value+os.pathsep+'$'+self.env+'"\n')
			ksh.write('export '+self.env+'\n')
		
			py.write('if os.environ.has_key("'+self.env+'"): os.environ["'+self.env+'"] = "'+os.path.expandvars(self.value)+os.pathsep+'"+'+'os.environ["'+self.env+'"]\n')
			py.write('else: os.environ["'+self.env+'"] = "'+os.path.expandvars(self.value)+'"\n')
			
			pl.write('$ENV{"'+self.env+'"} = defined $ENV{"'+self.env+'"} ? "'+os.path.expandvars(self.value)+os.pathsep+'" . $ENV{"'+self.env+'"} : "'+os.path.expandvars(self.value)+'";\n')
		
