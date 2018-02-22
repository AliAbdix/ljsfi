#
#	Copyright Saul Youssef, July 2003
#
from Environment import *
from Base        import *
from Execution   import *
import os,shutil,tempfile

class Copy(Environment):
	type   = 'copy'
	title  = 'Copies'
	action = 'copy'
	
	def __init__(self,copyFrom,copyTo,substring='',replacement=''):
		self._from   = copyFrom
		self._to     = copyTo
		self._target = ''
		self._substring = substring
		self._replace = replacement
		if '*' in copyFrom or '*' in copyTo:
			abort('Wildcards not allowed in copy from ['+copyFrom+'] to ['+copyTo+'].')

#-- Set
	def equal(self,c): return self._from==c._from and self._to==c._to and self._substring==c._substring and self._replace==c._replace
	def str(self): return self._from+' -> '+self._to

#-- Compatible
	def compatible(self,c): return Reason()
	
#-- Satisfiable
#	def satisfied(self):
#		reason = Reason()
#			
#		if self.acquired: reason = Reason("["+self._target+"] is missing.",not os.path.exists(self._target))	
#		else:             reason = Reason("Copy ["+`self`+"] has not been executed.",not os.path.exists(self._target))
#		
#		return reason
	def satisfiable(self): return Reason()
			
#-- Action
	def acquire(self):
		reason = Reason()
		try:
			if os.path.isdir(fullpath(self._from)): 
				execute('cp -r '+fullpath(self._from)+' '+fullpath(self._to))
#				shutil.copytree(fullpath(self._from),fullpath(self._to))
			else:                                   
				shutil.copy    (fullpath(self._from),fullpath(self._to))
				
			if os.path.isdir(fullpath(self._to)):
				self._target = os.path.join(fullpath(self._to),os.path.basename(fullpath(self._from)))
				if not os.path.exists(self._target): abort('Error in Copy.')
			else:
				self._target = fullpath(self._to)
				
			if self._substring!='':
				tmp = tempfile.mktemp()
				self._replace = os.path.expandvars(self._replace)
				f = open(self._target,'r')
				g = open(tmp,'w')
				for line in f.readlines():
					g.write(string.replace(line,self._substring,self._replace))
				f.close()
				g.close()
				execute('cp -f '+tmp+' '+self._target)
				execute('rm -f '+tmp)
		except (IOError,OSError):
			reason.reason("Copy ["+`self`+"] has failed.")
		return reason
		
	def retract(self):
		reason = Reason()
		if not os.path.exists(self._target):
			reason.append(Reason("Can't undo ["+`self`+"] because target ["+self._target+"] doesn't exist."))
		if os.path.isdir(self._target):
			reason.append(execute('rm -r -f '+self._target))
		else:
			reason.append(execute('rm -f '+self._target))
		self._target ==''
		return reason

class CopyAndReplace(Copy):
	type   = 'copy with string replacement'
	title  = 'Copy with String Replacements'
	action = 'copy with string replacment'
	
	def str(self): 
		return self._from+' -> '+self._to+' replacing ['+self._substring+'] with ['+self._replace+']'
		
