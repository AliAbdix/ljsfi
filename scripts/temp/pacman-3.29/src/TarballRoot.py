#
#	Copyright, Saul Youssef, November 2004
#
from Environment import *
from Execution   import *

#gunzip_in_path = fileInPath('gunzip').ok()
#tar_in_path    = fileInPath('tar'   ).ok()
gunzip_in_path = 1
tar_in_path    = 1

class TarballRoot(Environment):
	type   = 'tarball root directory'
	title  = 'Tarball Root Directories'
	action = 'set tarball root environment variable'

	def __init__(self,tarzipfile,path='',logfile=''): 
		self._file = tarzipfile
		self._path = path
		self._logfile = logfile
		self._root = ''
		self.export = 1
#-- Set
	def equal(self,t): return self._file == t._file
	def str(self):
		if self._root =='': return 'of '+os.path.join(self._path,self._file)+': $PAC_TARBALLROOT= - unset -'
		else:               return 'of '+os.path.join(self._path,self._file)+': $PAC_TARBALLROOT='+self._root
			
#-- Compatible
	def compatible(self,t): return Reason()
	
#-- Satisfiable
	def satisfied(self): 
		if self.acquired:
			return Reason("Untar directory ["+self._root+"] is missing.",not os.path.exists(fullpath(self._root)))
		else: 
			return Reason("["+`self`+"] has not been set.")
	def satisfiable(self):
		reason = Reason()
#		if   not fileInPath('gunzip').ok():  reason.reason("Can't find [gunzip] in the installer's path.")
#		elif not fileInPath('tar').   ok():  reason.reason("Can't find [tar] in the installer's path.")
		if   not gunzip_in_path: reason.reason("[gunzip] is not in the installer's path.")
		elif not    tar_in_path: reason.reason("[tar] is not in the installer's path.")
		return reason

#-- Action
	def acquire(self):
		reason = self.satisfiable()
		if reason.ok():
			fpath = fullpath(os.path.join(self._path,self._file))
			file = self._file
			if self._logfile!='': flog = fullpath(self._logfile)
			else:                 flog = ''
		unzip = tail(file,'.tar.gz') or tail(file,'.tgz') or tail(file,'.tar.Z') or tail(file,'.tar.z')
		untar = tail(file,'.tar')
		
		if os.path.exists(fpath):
			if   unzip:
				reason,root = parseTarZ(fpath)
				froot = fullpath(root)
				if reason.ok():
					self._root = froot
					self.__hasroot = 1
					verbo.log('env','About to set [PAC_TARBALLROOT => '+froot+']...')
					os.environ['PAC_TARBALLROOT'] = froot
				else:
					self._root    = ''
					self.__hasroot = 0
			elif untar:
				reason,root = parseTar(fpath)
				froot = fullpath(root)
				if reason.ok():
					self._root = froot
					self.__hasroot = 1
					verbo.log('env','About to set [PAC_TARBALLROOT => '+froot+']...')
					os.environ['PAC_TARBALLROOT'] = froot
				else:
					self._root    = ''
					self.__hasroot = 0
		else:
			reason.reason("File ["+fpath+"] doesn't exist.  Can't determine root directory.")
		return reason

	def retract(self):
		self._root = ''
		self.__hasroot = 0
		if os.environ.has_key('PAC_TARBALLROOT'): 
			verbo.log('env','About to delete [PAC_TARBALLROOT => '+os.environ['PAC_TARBALLROOT']+']...')
			del os.environ['PAC_TARBALLROOT']
		return Reason()
#-- shellOut
	def shellOut(self,csh,sh,py,pl,ksh):
		if self.acquired:
			csh. write('setenv '+'PAC_TARBALLROOT'+' "'+self._root+'"\n')
			sh.  write('PAC_TARBALLROOT'+'="'+self._root+'"\n')
			sh.  write('export PAC_TARBALLROOT \n')
			py.  write('os.environ["PAC_TARBALLROOT"] = "'+self._root+'"\n')
			pl.  write('$ENV{PAC_TARBALLROOT} = "'+self._root+'";\n')
			ksh. write('PAC_TARBALLROOT'+'="'+self._root+'"\n')
			ksh. write('export PAC_TARBALLROOT \n')

class TarballRootDeletable(TarballRoot):
	type = 'tarball root directory vdt'
	title = 'Tarball Root Directories vdt'
	action = 'set tarball root environment variable vdt'
	def satisfied(self): 
		if self.acquired:
			return Reason()
#				A hack for VDT
#			return Reason("Untar directory ["+self._root+"] is missing.",os.path.exists(fullpath(self._root)))
		else: 
			return Reason("["+`self`+"] not set.")

