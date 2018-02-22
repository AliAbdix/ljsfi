#
#	Copyright Saul Youssef, April 2004
#
from Environment import *
from WebPage     import *
import os

class TextFile(Environment):
	type   = 'text file'
	action = 'create text file'
	title  = 'Text Files'
	
	def __init__(self,path,lines,trans=0): 
		self.path,self.lines = path,lines
		self._trans = trans
		while len(self.lines)>0 and string.strip(self.lines[-1])=='': self.lines.pop()
#-- Set
	def equal(self,t): return fullpath(self.path)==fullpath(t.path) and self.lines==t.lines
	def str(self): return self.path
#	def display(self,indent=0):
#		print indent*' '+`self`
#		for line in self.lines: print (indent+2)*' '+line
#-- Compatible
	def compatible(self,t): Reason('['+`self`+'] and ['+`t`+'] are incompatible.',fullpath(self.path)==fullpath(t.path))

#-- Satisfiable
	def satisfied(self): return Reason('File ['+self.str()+'] has not been attempted.',not self.acquired)
#	def satisfied(self): return Reason('File ['+self.path+'] does not exist.',not os.path.exists(self.path))
	def satisfiable(self): return Reason()
	
#-- Action
	def acquire(self):
		reason = Reason()
		path = fullpath(self.path)
		if self._trans:
			ls = []
			for line in self.lines: ls.append(os.path.expandvars(line))
			self.lines = ls[:]
		try:
			f = open(path,'w')
			for line in self.lines: f.write(line+'\n')
			f.close()
			self.path = path
		except (IOError,OSError):
			reason.reason("Failure attempting to write ["+`self`+"].")
		return reason
		
	def retract(self):
		reason = Reason()
		if os.path.exists(self.path):
			try:
				os.remove(self.path)
			except (IOError,OSError):
				reason.reason("Failure attemting to remove ["+`self`+"].")
		return reason	
	
class PersistentTextFile(TextFile): 
	type    = 'Persistent text files'
	title   = 'Persistent Text Files'
	action  = 'make persistent text file'
	def retract(self): return Reason()

class SourceCode(TextFile):
	type    = 'pacman source code'
	title   = 'Pacman Sources'
	action  = 'pacman source code'
	
	def satisfied(self): return Reason()
	def satisfiable(self): return Reason()
#	def display(self,indent=0): return self.type

	def htmlOut(self,w):
		w.text(`self`,1); w.text('<ol>')
		count = 0
		w.text('<pre>'); w.cr()
		for line in self.lines: 
			count = count + 1
			num = `count`+'.   '
#			w.text((5-len(num))*' '+num)
			w.text('<font color="#8B0000"><b>'+line+'</b></font>')
#			if count!=len(self.lines): w.text('<br>')
		w.text('</pre>'); w.cr()
		w.text('</ol>')
