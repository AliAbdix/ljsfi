#
#	copyright Saul Youssef, August 2003
#
from Environment   import *
from FileExists    import *
from Env           import *
from ShellCommand  import *
from RPMinstalled  import *
from WebPage       import *

def process(d):
	ens = AND()
	for ty,val in d.items():
		if   ty=='inpath':
			for x in val: ens.append(FileExists(x))
		elif ty=='enviros':
			for x in val: ens.append(Env(x))
		elif ty=='scripts':
			for x in val: ens.append(ShellCommand(x))
		elif ty=='commands':
			for x in val: ens.append(ShellCommand(x))
		elif ty=='rpms':
			for x in val: ens.append(RPMinstalled(x))
		elif ty=='exists':
			for x in val: ens.append(FileExists(x))
		else:
			abort('Unknown entry in nativelyInstalled.')
	return ens

class NativelyInstalled(Environment):
	type   = 'native'
	title  = 'Natives'
	action = 'natively install'
	
	def __init__(self,d): 
		self.di = d
		self.environ = process(d)
#-- Set		
	def equal(self,n): return self.di==n.di
	def str(self): return `self.di`
	def display(self,indent=0):
		print indent*' '+`self`
		self.environ.display(indent+4)
		
	def __len__(self): return len(self.environ)
	def __getitem__(self,i): return self.environ[i]
		
#-- Satisfiable
	def satisfied  (self): return self.environ.satisfied()
	def satisfiable(self): return self.environ.satisfiable()
	def satisfy    (self): return self.environ.satisfy()
	
#-- SatisfyOrder
	def satisfies(self,E): return self.environ.satisfies(E)
	
#-- HtmlOut
#	def htmlOut(self,w,depth=999999):
#		if depth>=0:
#			w.text(`self`); w.cr()
#			self.environ.htmlOut(w,depth)
#-- Select
#	def select(self,q): return self.environ.select(q)

