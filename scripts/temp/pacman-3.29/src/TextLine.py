#
#	Copyright Saul Youssef, April 2004
#
from Environment import *
from Execution   import *
from GridMap     import *
import tempfile,time,string

def lineFront(line,text,cc='#'):
	if len(line)>=len(text):
		if line[:len(text)]==text: 
			rest = line[len(text):]
			got_one = 0
			for i in range(len(rest)):
				if   rest[i]==cc:                  break
				elif rest[i] in string.whitespace: pass
				else:                              got_one = 1
			return not got_one
		else:
			return 0
	else:
		return 0
		
def lineFronts(lines,text,cc='#',justafter='back'): 
	if justafter=='back' or justafter=='front' or justafter=='':  
		return exists(lines,lambda line: lineFront(line,text,cc))
	else:
		lines2 = lines[:]
		while len(lines2)>0:
			line = lines2.pop(0)
			if string.count(line,justafter)>0: break
		if len(lines2)>0: return lineFront(lines2[0],text,cc)
		else:             return 0

class SSHUserAccess(Environment):
	type   = 'SSH access'
	action = 'grant SSH access'
	title  = 'SSH Access'
	
	def __init__(self,username,public_key):
		self._username   = username
		self._public_key = public_key
		self._insertion  = TextLineInsertion('~'+username+'/.ssh/authorized_keys',self._public_key,'back')
		
	def equal(self,ssh): return self._username == ssh._username and self._public_key == ssh._public_key
		
	def str(self): 
		remotename = string.split(self._public_key,' ')[-1]
		if '@' in remotename: s = remotename+' => '+self._username+', private key: '
		else:		      s = self._username+', private key: '
		if len(self._public_key)>15: s = s + self._public_key[:15]+'...'
		else:                        s = s + self._public_key
		return s
	def   satisfied(self): return self._insertion.satisfied  ()
	def satisfiable(self): return self._insertion.satisfiable()
	def     acquire(self): return self._insertion.acquire    ()
	def     retract(self): return self._insertion.retract    ()
	
class SSHUserHasAccess(SSHUserAccess):
	type   = 'SSH has access'
	action = 'test for SSH access'
	title  = 'SSH Has Access'
	
	def acquire(self): return self.satisfied()
	def retract(self): return self.satisfied()

class GlobusUserAccess(Environment):
	type   = 'Globus access'
	action = 'add DN to globus grid-mapfile'
	title  = 'Globus Access'
	
	def __init__(self,dnstring,localUsername,position=''):
		self._dn = dnstring
		self._username = localUsername
		self._position = position
		gm = '"'+self._dn+'"'+' '+self._username
		if position=='last': self._insertion = TextLineInsertion('/etc/grid-security/grid-mapfile',gm,'back' )
		else:                self._insertion = TextLineInsertion('/etc/grid-security/grid-mapfile',gm,'front')
			
	def equal(self,ga): return self._dn == ga._dn and self._username == ga._username
	def str(self):      return self._dn+' => '+self._username
	
	def satisfied(self): 
		reason = Reason('No /etc/grid-security/grid-mapfile exists.',not os.path.exists('/etc/grid-security/grid-mapfile'))
		if reason.ok():
			gridmap = GridMapFile()
			if not gridmap.hasDN(self._dn,self._username):
				reason = Reason('Grid map file does not contain ['+self._dn+'] mapped to ['+self._username+'].')
			else:
				if self._position=='first':
					if not gridmap.firstDN(self._dn,self._username):
						reason = Reason('['+self._username+'] is mapped to another user before ['+self._username+'].')
				elif self._position=='last':
					if not gridmap.lastDN(self._dn,self._username):
						reason = Reason('['+self._username+'] is mapped to another user after ['+self._username+'].')
				else:
					pass
		return reason
	def satisfiable(self): return self._insertion.satisfiable()
	def     acquire(self): return self._insertion.acquire    ()
	def     retract(self): return self._insertion.retract    ()
	
class GlobusUserHasAccess(GlobusUserAccess):
	type   = 'has Globus access'
	title  = 'Has Globus Access'
	action = 'test for Globus access'
	  
	def acquire(self): return self.satisfied()
	def retract(self): return self.satisfied()

class TextLineInsertion(Environment):
	type   = 'insert text'
	action = 'insert text line'
	title  = 'Text Line Insertions'
	
	def __init__(self,path,line,justAfterLineContaining='back',comment='#'):
		self._path      = path
		self._text      = line
		self._comment   = comment
		self._justAfter = justAfterLineContaining
		self._insert    = ''
		
	def equal(self,t):
		return self._path      == t._path       and \
		       self._text      == t._text       and \
		       self._comment   == t._comment    and \
		       self._justAfter == t._justAfter  and \
		       self._insert    == t._insert
		       
	def str(self):
		if self._justAfter == 'front':
			return "["+self._text+"] at the beginning of ["+self._path+"]"
		elif self._justAfter == 'back':
			return "["+self._text+"] at the end of ["+self._path+"]"
		else:
			return "["+self._text+"] in ["+self._path+"] just after line containing ["+self._justAfter+"]"

	def getLines(self):
		lines = []
		reason = Reason()
		reason = Reason("File ["+fullpath(self._path)+"] doesn't exist.",not os.path.exists(fullpath(self._path)))
		if reason.ok():
			self._path = fullpath(self._path)
			try: 
				f = open(self._path,'r')
				lines = f.readlines()
				f.close()
			except (IOError,OSError):
				reason = Reason('Error reading ['+self._path+'].')
		return reason,lines
		
	def satisfiable(self): return Reason()
	def satisfied(self):
		reason,lines = self.getLines()
		if self._justAfter=='back' or self._justAfter=='front' or self._justAfter=='':
			reason = Reason('['+self._path+'] does not contain ['+self._text+'].',not lineFronts(lines,os.path.expandvars(self._text),self._comment))
		else:
			reason = Reason('['+self._path+'] does not contain ['+self._text+'] just after ['+self._justAfter+'].',not lineFronts(lines,os.path.expandvars(self._text),self._comment))
		return reason
		
	def acquire(self):
		reason,lines = self.getLines()
		if reason.ok():
			self._text = os.path.expandvars(self._text)
			if self._comment=='':
				newline = self._text+'\n'
			else:
				if    os.environ.has_key('PAC_ANCHOR'): txt = os.environ['PAC_ANCHOR']
				else:                                   txt = getusername()
				newline = self._text+'   '+self._comment+' - Inserted from '+txt+' on '+time.ctime(time.time())+'.  Do not edit.\n'
				verbo.log('text','Inserting text ['+newline+'] into ['+self._path+']...')
			if    self._justAfter == 'front': lines.insert(0,newline)
			elif  self._justAfter == 'back' : lines.append(  newline)
			elif  self._justAfter == ''     : lines.append(  newline)
			else:
				got_one = 0
				lines2 = []
				for line in lines:
					lines2.append(line)
					if not got_one and string.count(line,self._justAfter)>0: 
						lines2.append(newline)
						got_one = 1
				if got_one: 
					lines = lines2[:]
				else:       
					reason = Reason('Cannot find ['+self._justAfter+'] in ['+self._path+'].',not got_one)
					lines = lines2[:]
		if reason.ok():
			reason = ask.re('text-insert','About to insert ['+newline+'] into ['+self._path+'].  OK?')
			if reason.ok():
				try:
					tmp = tempfile.mktemp()
					f = open(tmp,'w')
					for line in lines: f.write(line)
					f.close()
					self._insert = newline
				except (IOError,OSError):
					reason = Reason('Error writing to temporary file.')
			if reason.ok(): reason = execute('mv -f '+tmp+' '+self._path)
		return reason
		
	def retract(self): 
		reason,lines = self.getLines()
		if reason.ok():
			lines2 = []
			got_one = 0
			for line in lines:
				if line==self._insert: 
					verbo.log('text','Removing text ['+line+'] from ['+self._path+']...')  
					got_one = 1
				else:                
					lines2.append(line)
			lines = lines2
			if not got_one: 
				print "Warning: ["+self._insert+"] has been removed from ["+self._path+"]..."
#		if reason.ok():
			reason = ask.re('text-insert','About to remove ['+self._insert+'] from ['+self._path+"]. OK?")
			if reason.ok():
				try:
					tmp = tempfile.mktemp()
					f = open(tmp,'w')
					for line in lines: f.write(line)
					f.close()
				except (IOError,OSError):
					reason = Reason('Error writing to temporary file.')
			if reason.ok(): 
				reason = execute('mv -f '+tmp+' '+self._path)
				self._insert = ''
		else:
			reason = Reason()
		return reason

class TextFileContainsText(Environment):
	type   = 'contains text'
	action = 'test if file contains text'
	title  = 'File Contains Texts'

	def __init__(self,path,text,comment_character='#'):
		self._path = path
		self._text = text
		self._cc   = comment_character
	
	def equal(self,t): return fullpath(self._path)==fullpath(t._path) and self._text==t._text
	def str(self): return "["+self._text+"] in ["+self._path+"]"
	
	def satisfiable(self): return Reason()
	def satisfied(self): return Reason("["+`self`+"] has not been checked yet.",not self.acquired)
	def acquire(self):
		reason = Reason()
		if reason.ok(): reason = Reason("File ["+fullpath(self._path)+"] doesn't exist.", not os.path.exists(fullpath(self._path)))
		if reason.ok(): 
			self._path = fullpath(self._path)
			try:
				f = open(self._path,'r')
				lines = f.readlines()
				f.close()
			except (IOError,OSError):
				reason = Reason('Error reading ['+self._path+'].')
		if reason.ok():
			count = 0
			for line in lines:
				if len(line)>0 and not line[0]==self._cc:
					count = count + string.count(line,self._text)
					if count>0: break
			reason = Reason("File ["+self._path+"] does not contain ["+self._text+"].",count==0)
		return reason
		
	def retract(self): return self.satisfied()
