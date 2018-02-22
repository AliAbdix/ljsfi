#
#	Copyright, Saul Youssef, December 2003
#
from Environment import *
from Execution   import *
import tempfile

class Mail(Environment):
	type   = 'mail'
	title  = 'Mail'
	action = 'send email'
	
	def __init__(self,to,subject='',body=''):
		self.to      = to
		self.subject = subject
		self.body    = body
		
	def equal(self,m): return self.to==m.to and self.subject==m.subject and self.body==m.body
	def str(self): return 'to ['+self.to+'] subject ['+self.subject+'] body '+`self.body`+'.'

#-- Satisfiable
	def satisfied(self): return Reason('Mail has not been sent.',not self.acquired)
	def satisfiable(self):
		if not fileInPath('Mail').ok() and not fileInPath('mail').ok():
			return Reason("Neither [Mail] nor [mail] are in your path.  Can't send email.")
		else:
			return Reason()	
		
	def acquire(self): 
		tmp = tempfile.mktemp()
		f = open(tmp,'w')
		if hasattr(self.body,'__getitem__'):
			for line in self.body: line = os.path.expandvars(line)
			for line in self.body: f.write(line+'\n')
		else:
			self.body = os.path.expandvars(self.body)
			f.write(self.body)
		f.close()
		reason = fileInPath('Mail')
		self.subject = os.path.expandvars(self.subject)
		self.to      = os.path.expandvars(self.to)
		reason = ask.re('mail','About to ['+'Mail -s "'+self.subject+'" '+self.to+' < '+tmp+'].  OK?')
		if reason.ok(): 
			reason = execute('Mail -s "'+self.subject+'" '+self.to+' < '+tmp)
			execute('rm -f '+tmp)
		else:
			reason = fileInPath('mail')
			if reason.ok():
				reason = execute('mail -s "'+self.subject+'" '+self.to+' < '+tmp)
				execute('rm -f '+tmp)
		return reason
		
	def retract(self): return Reason()
	

		
	
