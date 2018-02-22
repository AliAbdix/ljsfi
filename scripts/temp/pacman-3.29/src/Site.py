#
#	Copyright Saul Youssef, August 2003
#
from PackageCollection import *

class Site(PackageCollection):
	type   = 'remote installation'
	title  = 'Remote Installations'
	action = 'make remote installation'
	
	def __init__(self,c): self.computer = c

	def establish(self):
		reason,l = self.computer.listdir()
		reason.require()
		if 'E' in l and 'boot' in l: pass
		else: self.initialize()
		
	def initialize(self): 
		reason = Reason()
		if reason.ok(): reason = self.computer.put    ('boot/boot.tar.gz')
		if reason.ok(): reason = self.computer.execute('gunzip boot.tar.gz')
		if reason.ok(): reason = self.computer.execute('tar xf boot.tar')
		if reason.ok(): reason = self.computer.execute('rm boot.tar')
		if reason.ok(): reason = self.computer.execute(self.init()+'pacman -q')
		if reason.ok(): reason = self.computer.execute(self.init()+'cp pacman-'+version+'/htmls/*.gif htmls')
		return reason
		
	def precom(self):
		if self.computer.shell=='sh': return '. '
		else:                         return 'source '
	def init(self):
		return 'cd pacman-'+version+'; '+self.precom()+'setup.'+self.computer.shell+'; cd ..; '
	def getE(self):
		self.establish()
		reason = Reason()
		infile = 'logs/'+ln('E',self.computer.host,self.computer.location)
		if reason.ok(): reason = self.computer.get('E',infile)
		if reason.ok(): E = get(infile)
		if reason.ok(): 
			removeFile(infile)
			return reason,E
		else:    
			removeFile(infile)       
			return reason,OR()


	def rexswitch(self,switch):
		self.establish()
		reason = Reason()
		infile = '$PAC_ANCHOR/logs/'+ln(switch,self.computer.host,self.computer.location)
		infile = fullpath(infile)
		if reason.ok(): reason = self.computer.execute (self.init()+'pacman -trust-all-caches -'+switch)
		if reason.ok(): reason = self.computer.get     ('logs/'+switch,infile)
		if reason.ok(): reason = self.computer.execute (self.init()+'rm logs/'+switch)
		if reason.ok(): reason = get(infile)
		removeFile(infile)
		return reason

#-- PackageCollection
	def addPackage(self,p): 
		self.establish()
		reason = Reason()
		rfile = 'logs/'+self.computer.host+'_'+self.computer.location+'_'+'addpackage'
		p.put(fullpath('$PAC_ANCHOR/tmp/package.e'))
		if reason.ok(): reason = self.computer.put('$PAC_ANCHOR/tmp/package.e')
		removeFile(fullpath('$PAC_ANCHOR/tmp/package.e'))
		if reason.ok(): reason = self.computer.execute(self.init()+'pacman -trust-registry -addpackage:package.e')
		self.computer.execute(self.init()+'rm package.e')
		return reason

	def removePackage(self,packageName):
		reason = Reason()
		if reason.ok(): reason = self.computer.execute(self.init()+'pacman -remove '+packageName)
		if reason.ok(): reason = self.computer.get('logs/remove',\
		        fullpath('logs/'+ln('remove',self.computer.host,self.computer.location)) )
		if reason.ok(): reason = self.computer.execute(self.init()+'rm logs/remove')
		if reason.ok(): reason = get(fullpath('$PAC_ANCHOR/logs/'+ln('remove',self.computer.host,self.computer.location)))
		return reason

	def removeAll(self): return self.rexswitch('removeall')
	
	def removeInstallation(self):
		reason = self.removeAll()
		if reason.ok(): reason = self.computer.execute(self.init()+'pacman -removeinstallation')
		if reason.ok(): reason = self.computer.execute('rm -r -f pacman-'+version)
		return reason
		
#-- Set
	def equal(self,x):
		reason,E = self.getE()
		reason.require()
		return E==x
	def display(self,indent=0):
		reason,E = self.getE()
		reason.require()
		E.display(indent)
	def str(self): return `self.computer`
		
#-- List
	def __getitem__(self,index):
		reason,E = self.getE()
		reason.require()
		return E[index]
	def __len__(self):
		reason,E = self.getE()
		reason.require()
		return len(E)
	
#-- Satisfiable
	def satisfiable(self): return self.rexswitch('satisfiable')
	def satisfied  (self): return self.rexswitch('satisfied')
	def satisfy    (self): return self.rexswitch('satisfy')
	def restore    (self): return self.removeInstallation()
		
#-- HtmlOut
	def htmlOut(self,w): 
		subdir = fullpath('$PAC_ANCHOR/htmls/'+str2file(self.computer.host+'_'+self.computer.location))
		os.system('rm -r -f '+subdir)
		self.computer.getdir('htmls',subdir)
		w.linktarget(self.computer.host+':'+self.computer.location,subdir+'/index.html')
		
