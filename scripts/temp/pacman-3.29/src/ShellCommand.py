#
#	Copyright Saul Youssef, June 2004
#
#       Modified, April 2006, S.Y.
#
from Environment import *
from Execution   import *
import os,time,CU,EnvironmentVariable

class ShellCommand(Environment):
	type   = 'shell'
	title  = 'Shell Commands'
	action = 'execute shell command'
	
	_executed = {}
	
	def __init__(self,command,signature=None):
		self.command   = command
		self.signature = signature
		self.verb      = ''
		self.output    = ''
		self.lasttry   = Reason()
#		self.mode      = ''
		self.mode      = 'noclear'
		
	def getLastTry(self): 
		if hasattr(self,'lasttry'): return self.lasttry
		else:                       return Reason()
	def shellMemoryAdd(self,signature):
		ShellCommand._executed[signature] = 'executed'
#-- Set
	def equal(self,c): return self.command==c.command and self.signature==c.signature
	def str  (self):   
		if contains(self.mode,'compatibility'): return os.path.expandvars(self.command)
		else:                                   return self.command

#-- Compatiblility
	def compatible(self,c): return Reason()
	
#-- Satisfiable
	def satisfied(self): return Reason('Shell command ['+self.command+'] has not been acquired.',not self.acquired)
	def satisfiable(self): return Reason()
	
#-- Action
	def acquire(self):
		reason = Reason()
		
		if self.signature==None: abort('Shell command ['+`self`+'] must be part of a package.')
		if 0 and '$' in self.command and '$' in os.path.expandvars(self.command) and not "'" in self.command and not '"' in self.command:
			verbo.log('*',"Shell command ["+self.command+"] contains undefined environment variables.")
			verbo.log('*',"Shell command translates to ["+os.path.expandvars(self.command)+"].  Execution not attempted.")
			verbo.log('*',"Use -allow-undefined-shell to force execution.")
			if not (switch('allow-undefined-shell') or allow('undefined-shell')):
				reason = AllReason()
				reason.reason("Shell command ["+self.command+"] contains undefined environment variables.")
				reason.reason("Shell command translates to ["+os.path.expandvars(self.command)+"].  Execution not attempted.")
				reason.reason("Shell command ["+self.command+"] contains undefined environment variables.  Execution not attempted.")
#
#-- commented due to an apparent bug in Python
#
		if 0 and '~' in self.command and '~' in os.path.expanduser(self.command) and not "'" in self.command and not '"' in self.command:
			verbo.log('*',"Shell command ["+self.command+"] contains an unknown user home directory.")
			verbo.log('*',"Use -allow-undefined-shell to force execution.")
			if not switch('allow-undefined-shell') or allow('undefined-shell'):
				reason = Reason("Shell command ["+self.command+"] refers to a user which does not exist. Execution not attempted.")
		if reason.ok(): 
			verbo.log('shell','About to execute ['+self.command+'] at ['+os.getcwd()+'] as user ['+CU.getCurrentUser()+']...')
			reason = ask.re('shell','OK to execute ['+self.command+'] at ['+os.getcwd()+'] as user ['+CU.getCurrentUser()+']?')
			if self.type=='shell dialogue': self.output = 'yes'			
			if reason.ok(): reason,self.output = executeBase(self.command,self.mode)
			if self.mode.count('yes')>0: print self.output
		if reason.ok(): 
			if ShellCommand._executed.has_key(self.signature) and 0: abort('Shell command ['+`self`+'] has already been executed.')
			else: 
				if len(self.signature)==3:
					a,b,c = self.signature
					self.signature = (a,b,c,os.getcwd(),CU.getCurrentUser(),)
				ShellCommand._executed[self.signature] = 'executed'
		self.lasttry = reason
		return reason
		
	def retract(self): 
		if ShellCommand._executed.has_key(self.signature): del ShellCommand._executed[self.signature]
		return Reason()
		
#-- ShellOut
	def shellOut(self,csh,sh,py,pl,ksh): pass

class ShellDialogue(ShellCommand): 
	type   = 'shell dialogue'
	title  = 'Shell Dialogues'
	action = 'execute dialogue shell'
	
	def __init__(self,command,signature=None):
		self.command   = command
		self.signature = signature
		self.verb      = 'verbose'
		self.output    = ''
		self.mode      = 'yes'

class ShellOutputContains(Environment):
	type   = 'shell output contains'
	title  = 'Shell Output Contains'
	action = 'execute and test shell command output'
		
	def strbase(self,middle):
		if self.output=='':
			return '['+self.command+'] '+middle+' ['+self.outstring+']'
		else:
			return '['+self.command+' => '+self.output+'] '+middle+' ['+self.outstring+']'
	def str(self): return self.strbase('output contains')
			
	def equal(self,x): return self.command==x.command and self.outstring==x.outstring and self.maxout==x.maxout
		
	def __init__(self,command,outstring,maxout=99999):
		self.command   = command
		self.outstring = outstring
		self.output    = ''
		if len(outstring)>0: self.maxout = len(outstring)
		else:                self.maxout = maxout
		self.mode      = ''
		
	def firstline(self,output):
		l = string.split(output,'\n')
		for ll in l:
			if not string.strip(ll)=='': 
				self.output = ll[:self.maxout]
				break
		
	def satisfiable(self): return Reason()
	def satisfied  (self): return Reason('Test that ['+self.command+'] contains ['+self.outstring+'] has not been performed.',not self.acquired)
        def acquire    (self):
		reason,self.output = executeBase(self.command)
		if reason.ok():
			reason = Reason('['+self.output+'] does not contain ['+self.outstring+'].',string.count(self.output,self.outstring)==0)
		return reason
		
	def retract   (self): return Reason()
	
class SetenvShell(ShellOutputContains):
	type  = 'setenv shell'
	title = 'Setenv Shell'
	action = 'sets environment variable to output of shell command'
	
	def __init__(self,env,command):
		ShellOutputContains.__init__(self,command,'')
		self._name = env
		self._env = EnvironmentVariable.Setenv('','')
		
	def equal(self,x):
		return self._env==x._env and self.command==x.command
		
	def str(self): 
		if self._env.name=='': return 'Setenv ['+self._name+'] to the output of ['+self.command+']'
		else                 : return self._env.str()+', output from ['+self.command+']'
	
	def acquire(self):
		reason,output = executeBase(self.command)
		self.firstline(output)
		if self.output=='': reason = Reason("Shell command ["+self.command+"] returns an empty string.")
		if reason.ok():
			self._env = EnvironmentVariable.Setenv(self._name,self.output)
			reason = self._env.satisfy()
		return reason
		
	def retract(self):
		if not self._env.name=='':
			self._env.restore().require()
			self._env = EnvironmentVariable.Setenv('','')
		return Reason()
		
	def shellOut(self,csh,sh,py,pl,ksh):
		if self.acquired: self._env.shellOut(csh,sh,py,pl,ksh)
		
class SetenvShellTemp(ShellOutputContains):
	type   = 'setenv shell temp'
	title  = 'Setenv Shell Temp'
	action = 'sets a temporary environment variable to output of a shell command'
	def __init__(self,env,command):
		ShellOutputContains.__init__(self,command,'')
		self._name = env
		self._env = EnvironmentVariable.SetenvTemp('','')
		
	def equal(self,x):
		return self._env==x._env and self.command==x.command
		
	def str(self): 
		if self._env.name=='': return 'Setenv ['+self._name+'] to the output of ['+self.command+']'
		else:                  return self._env.str()+', output from ['+self.command+']'
	
	def acquire(self):
		reason,output = executeBase(self.command)
		self.firstline(output)
		if self.output=='': reason = Reason("Shell command ["+self.command+"] returns an empty string.")
		if reason.ok():
			self._env = EnvironmentVariable.SetenvTemp(self._name,self.output)
			reason = self._env.satisfy()
		return reason
		
	def retract(self):
		if not self._env.name=='':
			self._env.restore().require()
			self._env = EnvironmentVariable.SetenvTemp('','')
		return Reason()	
	
class ShellOutputLE(ShellOutputContains):
	type   = 'shell output LE'
	title  = 'Shell Output LE'
	action = 'execute and test shell command output'
	
	def str(self): return self.strbase('output is <=')
	def acquire(self):
		reason,output = executeBase(self.command)
		self.firstline(output)
		if reason.ok():
			reason = Reason('['+self.output+'] is not <= ['+self.outstring+'].',not self.output<=self.outstring)
		return reason
	
class ShellOutputLT(ShellOutputContains):
	type   = 'shell output LT'
	title  = 'Shell Output LT'
	action = 'execute and test shell command output'
	
	def str(self): return self.strbase('output is <')
	def acquire(self):
		reason,output = executeBase(self.command)
		self.firstline(output)
		if reason.ok():
			reason = Reason('['+self.output+'] is not < ['+self.outstring+'].',not self.output<self.outstring)
		return reason

class ShellOutputEQ(ShellOutputContains):
	type   = 'shell output EQ'
	title  = 'Shell Output EQ'
	action = 'execute and test shell command output'
	
	def str(self): return self.strbase('output is equal to')
	def acquire(self):
		reason,output = executeBase(self.command)
		self.firstline(output)
		if reason.ok():
			reason = Reason('['+self.output+'] is not equal to ['+self.outstring+'].',not self.output==self.outstring)
		return reason

class ShellOutputGE(ShellOutputContains):
	type   = 'shell output GE'
	title  = 'Shell Output GE'
	action = 'execute and test shell command output'
	
	def str(self): return self.strbase('output is >=')
	def acquire(self):
		reason,output = executeBase(self.command)
		self.firstline(output)
		if reason.ok():
			reason = Reason('['+self.output+'] is not >= ['+self.outstring+'].',not self.output>=self.outstring)
		return reason

class ShellOutputGT(ShellOutputContains):
	type   = 'shell output GT'
	title  = 'Shell Output GT'
	action = 'execute and test shell command output'
	
	def str(self): return self.strbase('output is >')
	def acquire(self):
		reason,output = executeBase(self.command)
		self.firstline(output)
		if reason.ok():
			reason = Reason('['+self.output+'] is not > ['+self.outstring+'].',not self.output>self.outstring)
		return reason

