#
#	Copyright, November 2004, Saul Youssef
#
from Base        import *
from Environment import *

class CookieString:
	def __init__(self,identity):
		self._identity = `abs(hash(identity))`
		self._path     = os.path.join(pac_anchor,pacmanDir,'cookies',self._identity)
		self._ignore   = switch('ignore-cookies')
		
	def init(self):
		r,ans = Reason(),''
		if self._ignore: 
			r = Reason('Ignoring cookies')
			try:
				removeFile(self._path)
			except (IOError,OSError):
				pass
			self._ignore = 0
		if r.ok(): r = Reason('No cookie file.',not os.path.exists(self._path))
		if r.ok():
			try:
				f = open(self._path,'r')
				lines = f.readlines()
				f.close()
			except (IOError,OSError):
				lines = []
				r = Reason("Error reading from ["+self._path+"].")

			if r.ok():
				if len(lines)>0 and len(lines[0])>0:
					ans = lines[0][:-1]
				else:
					r = Reason("Contents of ["+self._path+'] has been corrupted.')
		return r,ans
		
	def save(self,text):
		r = Reason()
		try:
			f = open(self._path,'w')
			f.write(text+'\n')
			f.close()
		except (IOError,OSError):
			r = Reason("Can't write ["+text+"] to ["+self._path+"].")
		return r
	
class Choice(Environment):
	type    = 'choice'
	title   = 'Choices'
	action  = 'choose'
	
	def __init__(self,answer,question,*answers):
		self._question,self._answer = question,answer
		self._answers = [x for x in answers]
		self._useranswer = '- unanswered -'
		self._identity = ''
		self._parentPackageName = ''
		self._init = 0
		
	def init(self):
		if not self._init:
			self._identity = self._question+`self._answers`+self._parentPackageName
			self._cookieAns = CookieString(self._identity)
			self._init = 1
#-- Set
	def equal(self,x): return self._question==x._question and self._answers==x._answers
	def str(self): return 'Asked ['+self._question+'] chosen ['+self._answer+'] from '+`self._answers`+' user chose ['+self._useranswer+'].'
	
	def satisfiable(self): return Reason()
	def satisfied(self): 
		self.init()
		r,self._useranswer = self._cookieAns.init()
		if r.ok():
			r = Reason('Option ['+self._answer+'] in answer to ['+self._question+'] has been declined.',not self._useranswer==self._answer)
		else:
			r = Reason('['+self._question+"] hasn't been asked.")
		return r
	def acquire(self):
		self.init()
		r,ans = self._cookieAns.init()
		if r.ok():
			r = Reason('Option ['+self._answer+'] in answer to ['+self._question+'] has been declined.',not ans==self._answer)
		else:
			while 1:
				ans = raw_input(self._question+': ')
				if ans in self._answers: break
				else:
					print 'You must choose from '+`self._answers`+'.  Try again...'
			r = self._cookieAns.save(ans)
			r = Reason('Option ['+self._answer+'] in answer to ['+self._question+'] has been declined.',not ans==self._answer)
			self._useranswer = ans
		return r
	def retract(self):
		self._useranswer = '- unanswered -'
		return Reason()			
			
