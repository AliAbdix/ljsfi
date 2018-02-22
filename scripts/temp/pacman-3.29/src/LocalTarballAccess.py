#
#	Copyright, August 2003, Saul Youssef
#
from Access    import *
from Execution import *
import tempfile,commands

class LocalTarballAccess(Access):
	type = 'local tarball'
	def __init__(self,tarball): 
		self.tarball = fullpath(tarball)
		self.location = self.tarball
		self.prefix = './'
#-- Set
	def equal(self,x): return self.tarball==x.tarball
	def __repr__(self): return self.tarball
	
	def access(self): return os.path.exists(self.tarball)
	
	def names(self):
		status,output = commands.getstatusoutput('tar -t -f '+self.tarball)
		if    status==0: 
			nms = string.split(output,'\n')
			for i in range(len(nms)): 
				if nms[i][:2]=='./': 
					nms[i] = nms[i][2:]
					self.prefix = './'
			nms2 = []
			for nm in nms: 
				if not string.strip(nm)=='': nms2.append(nm)
			return Reason(),nms2
		else:            
			return Reason('['+self.tarball+'] is not a tarball.'),[]
			
	def getFile(self,name,target2=''):
		if target2=='': target = name
		else:           target = target2
		
		if not os.path.isdir('tmp'): newtmp = 1; execute('mkdir tmp')
		else:                        newtmp = 0
		removeFile(os.path.join('tmp',target))
		
		status,output = commands.getstatusoutput('cd tmp; tar -x -f '+self.tarball+' '+self.prefix+name)
		reason = Reason('Error reading from ['+self.tarball+':'+output+']',status!=0)
		if status==0 and os.path.join('tmp',name)!=target:
			try:
				execute('mv '   +os.path.join('tmp',name)+' '+target)
				execute('rm -f '+os.path.join('tmp',name))
				if newtmp: execute('rm -r -f tmp')
			except (IOError,OSError):
				reason = Reason("Can't copy ["+name+"] to ["+target+"].")
		return reason
			
