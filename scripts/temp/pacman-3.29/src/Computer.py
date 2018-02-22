#
#	Copyright, Saul Yousef, August 2003
#
from Base      import *
from Execution import *
from WebPage   import *
import commands,tempfile

class Computer(Set,PrintOut):
	def __init__(self,host,location,username=getusername(),sh=shell()): 
		self.host      = host
		self.location  = location
		self.username  = username
		self.shell     = sh
		
	def __repr__(self)  : return 'Computer '+self.host+', location '+self.location+\
	                ', username '+self.username+', shell '+self.shell
	def __eq__  (self,c): return self.host==c.host and self.location==c.location \
	                         and self.username==c.username and self.shell==c.shell
	def htmlOut(self,w): w.text(`self`)
	
	def putObj(self,obj,path):
		filename = tempfile.mktemp()
		obj.put(filename)
		reason = self.put(filename,path)
		removeFile(filename)
		return reason
		
	def put(self,filename,path=''): 
		reason = Reason("Can't find file ["+filename+"].",not os.path.exists(fullpath(filename)))
		if reason.ok():
			com = 'scp '+fullpath(filename)+' '+self.username+'@'+self.host+':'+os.path.join(self.location,path)
			reason = ask.re('ssh','About to execute ['+com+'].  OK?')
			if reason.ok():
				verbo.log('ssh',com)
				status,output = commands.getstatusoutput(com)
				reason = Reason(output,status!=0)
		return reason
		
	def putdir(self,dirname,path=''):
		com = 'scp -r '+dirname+' '+self.username+'@'+self.host+':'+os.path.join(self.location,path)
		reason = ask.re('ssh','About to execute ['+com+'].  OK?')
		if reason.ok():
			if os.path.isdir(dirname):
				verbo.log('ssh',com)
				status,output = commands.getstatusoutput(com)
				reason = Reason(output,status!=0)
			else:
				reason = Reason("Can't putdir ["+dirname+"] to ["+self.host+"].  It's not a directory.")
		return reason
	
	def get(self,path,filename='.'): 
		com = 'scp '+self.username+'@'+self.host+':'+os.path.join(self.location,path)+' '+filename
		reason = ask.re('ssh','About to execute ['+com+'].  OK?')
		if reason.ok():
			verbo.log('ssh',com)
			status,output = commands.getstatusoutput(com)
			reason = Reason(output,status!=0)
		return reason
		
	def getdir(self,path,filename='.'):
		com = 'scp -r '+self.username+'@'+self.host+':'+os.path.join(self.location,path)+' '+filename
		reason = ask.re('ssh','About to execute ['+com+'].  OK?')
		if reason.ok():
			verbo.log('ssh',com)
			status,output = commands.getstatusoutput(com)
			reason = Reason(output,status!=0)
		return reason
	
	def listdir(self,path2='.'):
		if string.strip(path2)=='': path = '.'
		else:                       path = path2
		com = 'ssh '+self.username+'@'+self.host+' '+'"cd '+self.location+'; cd '+path+'; ls "'
		reason = ask.re('ssh','About to execute ['+com+'].  OK?')
		if reason.ok():
			verbo.log('ssh',com)
			status,output = commands.getstatusoutput(com)
			if status==0: 
				files = string.split(output,'\n')
				files = [string.strip(f) for f in files]
				return Reason(),files
#				return Reason(),string.split(output,'\n')
			else:          
				return Reason(output),[]
		else: 
			return reason,[]
		
	def access(self):
		reason,li = self.listdir()
		return reason
	def execute(self,command):
#		status,output = commands.getstatusoutput(sustr()+'ssh '+self.host+' '+'"cd '+self.location+'; '+command+'"')
		if self.username==getusername(): line = 'ssh '+self.host+' '+'"cd '+self.location+'; '+command+'"'
		else:                            line = 'ssh '+self.username+'@'+self.host+' '+'"cd '+self.location+'; '+command+'"'
		reason = ask.re('ssh','About to execute ['+line+'] at '+`self`+'.  OK?')
		if reason.ok():
			verbo.log('ssh',line)
			status = os.system(line)
			output = 'Error: '+command
			reason = Reason("Error executing ["+command+"].",status!=0)
		return reason
