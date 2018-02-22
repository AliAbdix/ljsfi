#
#	Copyright Saul Youssef, July 2003
#
from Base import *
import string,sys

class CookieQuestion(Set):
	def __init__(self,question,qanswer=lambda s: '',cookiejar=os.path.join(pac_anchor,pacmanDir,'cookies')):
		self.question  = question
		self.qanswer   = qanswer
		self.cookiejar = cookiejar
		self._parentPackageName = ''
		self._ignored  = 0
		
	def ask(self):
		while 1:
			answer = raw_input(self.question+': ')
			r = self.qanswer(answer)
			if not r=='': break
			else: sys.stdout.write(r)
		return answer
		
	def hasCookie(self):
		return os.path.exists(os.path.join(self.cookiejer,self._parentPackageName+'-'+self.question+'.cookie'))
		
	def cookieFile(self):
		return `abs(hash(self.question+self._parentPackageName))`
		
	def answer(self):
		try:
			if not self._ignored and switch('ignore-cookies'): 
				self._ignored = 1
				raise OSError
#			f = open(os.path.join(pac_anchor,pacmanDir,self.cookiejar,str2file(os.getcwd()+'-'+self.question+'.cookie')),'r')
			f = open(os.path.join(pac_anchor,pacmanDir,self.cookiejar,self.cookieFile()),'r')
			line = f.readline()
			f.close()
			answer = line[:-1]
		except (OSError,IOError):
			answer = self.ask()
			try:
#				f = open(os.path.join(pac_anchor,pacmanDir,self.cookiejar,str2file(os.getcwd()+'-'+self.question+'.cookie')),'w')
				f = open(os.path.join(pac_anchor,pacmanDir,self.cookiejar,self.cookieFile()),'w')
				f.write(answer+'\n')
				f.close()
				print 'Saving answer for future use.  Use -ignore-cookies to re-choose...'
			except (OSError,IOError):
				pass
#				print 'Warning: Failure writing to cookie jar ['+self.cookiejar+'].'
		return answer
	def erase(self):
#		removeFile(os.path.join(pac_anchor,pacmanDir,self.cookiejar,str2file(os.getcwd()+'-'+self.question+'.cookie')))
		removeFile(os.path.join(pac_anchor,pacmanDir,self.cookiejar,self.cookieFile()))

class Cookie(Set):
	def __init__(self,name,directory,items,cmin=1,cmax=1):
		self.name,self.directory,self.items = name,directory,items
		self.vals = []
		self.cmin,self.cmax = cmin,cmax
		
	def __eq__(self,x):
		return self.name==x.name and self.directory==x.directory and self.items==x.items and \
		       self.vals==x.vals and self.cmin==x.cmin and self.cmax==x.cmax
	def __repr__(self):
		return self.name+' '+self.directory+' '+`self.items`+' '+`self.vals`
		
	def get(self):
		if os.path.exists(os.path.join(self.directory,self.name)) and not switch('ignore-cookies'):
			try:
				f = open(os.path.join(self.directory,self.name))
				lines = f.readlines()
				f.close()
			except (IOError,OSError):
				abort('Error reading cookie file ['+self.name+'].')
				
			for line in lines:
				l = string.split(line)
				if len(l)!=len(self.items):
					print 'Error in cookie file ['+os.path.join(self.directory,self.name)+'].'
					abort('Wrong number of items ['+self.line+'].')
				self.vals.append(l)
		else:
			if self.cmin==0:
				if yesno('Do you want any '+self.name+'(s) ?'):  self.getvals()
				else:                                            self.vals = []
			else:
				self.getvals()
			if yesno('Do you want to save these answers for future use?'):
				try:
					f = open(os.path.join(self.directory,self.name),'w')
					for v in self.vals:
						for vv in v: f.write(vv+' ')
						f.write('\n')
					f.close()
				except (IOError,OSError):
					abort('Error writing to cookie file ['+self.name+'].')
										
				print 'Answers saved in cookie file ['+os.path.join('cookies',self.name)+'].'
				
	def getvals(self):
		print 'Initializing ['+self.name+']...'
		if self.cmax>3: 
			if yesno('Do you want to enter values by hand?'): self.userInput()
			else:                                             self.fileInput()
		else:
			self.userInput()
			
	def itemString(self,f,endline=1,header='Enter '):
		f.write(header)
		count = 0
		for i in self.items: 
			count = count + 1
			f.write(i)
			if count==len(self.items): f.write(': ')
			else:                      f.write(', ')
		f.write('\n')
		if endline: f.write('Enter "." when finished.\n')
		
	def fileInput(self):
		got_it = 0
		while not got_it:
			self.itemString(sys.stdout,1,'Input from a file containing ')
			filename = getFilename('Enter file name: ')
			try:
				f = open(filename,'r')
				lines = f.readlines()
				f.close()
			except (IOError,OSError):
				print 'Error reading from ['+fullpath(filename)+'].  Try again...'
				break	
					
			got_it = 1
			for line in lines: 
				if len(string.split(line))!=len(self.items):
					print 'Error in line ['+line+'] in file ['+filename+'].'
					print 'Each line must contain '+`len(self.items)`+' items.'
					got_it = 0
			if got_it:
				for line in lines: self.vals.append(string.split(line))

	def userInput(self):
		count = 0
		done  = 0
		while (not done or count<=self.cmin) and count < self.cmax:
			if count==0:
				if           self.cmax==1:  self.itemString(sys.stdout,0,'Enter ')
				elif self.cmin==self.cmax:  self.itemString(sys.stdout,0,'Enter '+`self.cmin`+' ')
				elif         self.cmin==1:  self.itemString(sys.stdout)
				else                     :  self.itemString(sys.stdout,1,'Enter at least '+`self.cmin`+' ')
				
			while 1:
				while 1:
					line = raw_input()
					if (line=='.' or string.strip(line)=='') and count<self.cmin: 
						print 'At least '+`self.cmin`+' required...'
					else:				  
						break
					
				if line[0]=='.':
					done = 1
					break
				elif len(string.split(line))==len(self.items):
					self.vals.append(string.split(line))
					break
				else:
					print 'You must input '+`len(self.items)`+' per line.  Try again...'
			
			count = count + 1
