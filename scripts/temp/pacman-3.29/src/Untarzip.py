#
#	Copyright, Saul Youssef
#
#       Saul Youssef, March 2005 - rewrite to handle tar-overwrites correctly.
#
#   Oct 2005, removing --no-same-owner options for TeraGrid
#
from Base        import *
from Environment import *
import EnvironmentVariable,Execution
import freedisk
import time
import Basics

gnuTarOK,tarName = gnuTarFinder()
	
class TarSave:
	def __init__(self):
		self._tarpath = os.path.join(pac_anchor,pacmanDir,'tr'+version[:3])
		if os.path.exists(self._tarpath):
			try:
				f = open(self._tarpath,'r')
				self._db = cPickle.load(f)
				f.close()
#			except (IOError,OSError):
			except:
				self._db = {}
		else:
			self._db = {}
		
	def save(self):
		r = Reason()
		try:
			f = open(self._tarpath,'w')
			cPickle.dump(self._db,f)
			f.close()
#		except (IOError,OSError):
		except:
			r = Reason("Can't write to ["+self._tarpath+"].")
		return r
		
	def has(self,tarball,path):
		return self._db.has_key(path) and tarball in self._db[path]
		
	def add(self,tarball,path):
		if self._db.has_key(path): self._db[path].append(tarball)
		else:                      self._db[path] = [tarball]
		if debug('tar-save'): print 'Tar saved added ['+path+'] from ['+tarball+'] total of ['+`len(self._db[path])`+']...'
		
	def rem(self,tarball,path):
		r = Reason()
		if self._db.has_key(path):
			for i in range(len(self._db[path])):
				self._db[path].pop(i)
				break
			if debug('tar-save'): print 'Tar save removing ['+path+'] from ['+tarball+'] total of ['+`len(self._db[path])`+']...'
		else:
			pass
		return r
		
	def num(self,path):
		if self._db.has_key(path): return len(self._db[path])
		else:                      return 0
	
_tarSave = TarSave()
if debug('tar-save'):
	print 'tar-save:'
	for key,val in _tarSave._db.items(): print key,val
	
if switch('tar-overwrites'):
	keys = _tarSave._db.keys()
	k2 = []
	for k in keys:
		if len(k)>0 and not k[-1]=='/' and len(_tarSave._db[k])>0: k2.append(k)
	if len(k2)>0:
		print 'File in this installation which have been overwritten by untarring:'
		k2.sort()
		for k in k2: print '  '+k
	else:
		print 'No files in this installation have been overwritten by untarring.'

class Untarzip(Environment):
	type   = 'untar'
	title  = 'Untars'
	action = 'untar'
	
	def __init__(self,tarball,env=''):
		self._tarball  = tarball
		self._tarpath  = ''
		self._env      = env
		self._contents = []
		self._saved    = {}
		self._enviro   = None
		self._tarpause = 0
		
	def getSaved(self):
		if hasattr(self,'_saved'): return self._saved
		else:                      return {}
	def getEnviro(self):
		if hasattr(self,'_enviro'): return self._enviro
		else:                       return None
		
	def getTarpath(self):
		if hasattr(self,'_tarpath'): return self._tarpath
		else:                        return ''
		
	def getTarPause(self):
		if hasattr(self,'_tarpause'): return self._tarpause
		else:                         return tarGetPause()

        ###########
        # getTarball and setTarball added by Scot Kronenfeld 2/2009
        #
        # These are used from Download.py in order to fix the name of the
        # tarball when the @@PLATFORM@@ macro is being used
        def getTarball(self):
                if hasattr(self,'_tarball'): return self._tarball
                else:                        return None

        def setTarball(self, tarball):
                self._tarball = tarball

		
	def equal(self,u): return self._tarball==u._tarball and self._env==u._env
	def str(self):     
		s = self._tarball
		if not self._env=='':
			if hasattr(self,'_enviro') and hasattr(self._enviro,'type'):
				if self._enviro.satisfied():
					s = s + ', top directory: '+self._enviro.str()
				else:
					s = s + ', top directory: '+self._enviro.str()
			else:
				s = s + ', top directory to be set to '+self._env
		return s
	def unzip(self): return \
		tail(self._tarball,'.tar.gz') or tail(self._tarball,'.tgz'  ) or \
		tail(self._tarball,'.tar.Z' ) or tail(self._tarball,'.tar.z')
	def untar(self): return tail(self._tarball,'.tar')
	def unzipsuff(self):
		if    tail(self._tarball,'.tar.gz'): self._tarpath = self._tarball[:-3]
		elif  tail(self._tarball,'.tgz'   ): self._tarpath = self._tarball[:-3]+'tar'
		elif  tail(self._tarball,'.tar.Z' ): self._tarpath = self._tarball[:-2]
		elif  tail(self._tarball,'.tar.z' ): self._tarpath = self._tarball[:-2]
		else:                                self._tarpath = self._tarball[:  ]

	def getContents(self):
		c = []
		r = Reason()
		if self.unzip(): z = ' -z'
		else:            z = ''
		
		command = gnuTarName()+z+' -t -f '+self._tarball
		verbo.log('shell-all','About to execute ['+command+']...')
		r = ask.re('shell-all','OK to execute ['+command+']?')
		if r.ok(): r = ask.re('tar','OK to extract the contents of tarball ['+os.path.basename(self._tarball)+']?')
		if r.ok():
			if not self.getTarPause()==0: 
				verbo.log('tar','tarPause: sleeping for '+`self.getTarPause()`+' seconds...')
				time.sleep(self.getTarPause())
			status,output = commands.getstatusoutput(command)
			
			if status==0:
				t = string.split(output,'\n')
				c = []
				for tt in t:
					if len(tt)>1 and tt[:2]=='./': c.append(tt[2:])
					else:                          c.append(tt    )
			else:
				if len(output)>1000: output = '...<truncated by pacman>...'+output[len(output)-10000:]
				r = Reason('Error executing ['+command+'] returns status code ['+output+'].')
		return r,c

	def satisfied  (self): return Reason('Tarball ['+self._tarball+'] has not been untar/zipped',not self.acquired)
	def satisfiable(self): return Reason()

	def acquire(self):
		self.unzipsuff()
		self._tarball = fullpath(self._tarball)
		verbo.log('tar','Untarring ['+os.path.basename(self._tarball)+']...')
		if verbo('tar-brief'): flicker('  Untarring '+os.path.basename(self._tarball)+'...')
		r = Reason('Tarball ['+self._tarball+"] doesn't exist.",not os.path.exists(fullpath(self._tarball)))
		
		if r.ok():
			r,paths = self.getContents()
			if r.ok():
				if len(paths)>0 and contains(paths[0],'/'):
					self._root = string.split(paths[0],'/')[0]
					rootOk = forall(paths,lambda x: self._root==string.split(x,'/')[0])
					if rootOk: self._root = fullpath(self._root)
					else:      self._root = ''
				else:
					self._root = ''
				self._contents = []
				cdb = {}
				
				for x in paths:
					xsplit = string.split(x,'/')
					y = ''
					while len(xsplit)>0:
						y = y + xsplit.pop(0)
						if len(xsplit)>0: y = y + '/'
						if not cdb.has_key(y):
							cdb[y] = ''
							yy = fullpath2(y)
							self._contents.append(fullpath2(y))
					
		if r.ok(): 
			r = Reason()
			ver = verbo('tarfiles')
			bad = allow('bad-tar-filenames')
			for x in self._contents:
				if 0 and not bad and contains(x,'::'):
				   	r = Reason('File ['+x+'] from tarball ['+self._tarball+'] contains a file name with a non-standard character (see -allow to ignore).')
					break
			if r.ok():
				for x in self._contents:
					if ver: print x
					if tail(x,'/'):
						if os.path.exists(x):
							if not os.path.isdir(x):
								r = Reason('Untarring ['+self._tarball+'] would overwrite ['+x+'] with a directory.')
								break
							_tarSave.add(self.getTarpath(),x)
					else:
						if os.path.exists(x):
							if os.path.isdir(x):
								if allow('tar-overwrite'): pass
								elif Basics.yesno('Untarring ['+self._tarball+'] would overwrite directory ['+x+'] with a file of the same name. Is this OK?'): pass
								else: r = Reason('Untarring ['+self._tarball+'] would overwrite directory ['+x+'] with a file.')
								if r.ok():
									print 'WARNING: Untarring ['+self._tarball+'] will overwrite directory ['+x+'] with a file.'
							else:
								verbo.log('tarfiles','Untarring ['+self._tarball+'] will overwrite ['+x+'] saving...')
								if allow('tar-overwrite'): pass
								elif Basics.yesno('OK to overwrite ['+x+'] untarring ['+self._tarball+']?'): pass
								else: r = Reason('Untarring tarball ['+self._tarball+'] would overwrite ['+x+']')
								if r.ok():
									print 'WARNING: Untarring tarball ['+self._tarball+'] will overwrite ['+x+']...'
							_tarSave.add(self.getTarpath(),x)
					if not r.ok(): break

		if r.ok(): 
			r = ask.re('tar','OK to untar ['+os.path.basename(self._tarball)+']?')
			if r.ok():
				if self.unzip(): z = ' -z'
				else:            z = ''
				if not os.path.exists(os.path.basename(self._tarball)): r = Reason("Tarball ["+os.path.basename(self._tarball)+"] does not exist in ["+os.getcwd()+"].  Can't untar.")
				if debug('tar'): 
					print self._tarball
					os.system('ls')
				if r.ok():
				        if not self.getTarPause()==0: 
						verbo.log('tar','tarPause: sleeping for '+`self.getTarPause()`+' seconds...')
						time.sleep(self.getTarPause())
#					r = Execution.execute(gnuTarName()+z+' -xf '+os.path.basename(self._tarball))
					if gnuTarOK: r = Execution.execute(gnuTarName()+' --no-same-owner '+z+' -xf '+os.path.basename(self._tarball),'noclear')
					else:        r = Execution.execute(gnuTarName()+                    z+' -xf '+os.path.basename(self._tarball),'noclear')
					if not freedisk.enoughFreeDisk(100).ok(): r = freedisk.enoughFreeDisk(100)
					if r.ok() and not debug('tar-save'): removeFile(os.path.basename(self._tarball))
		if r.ok():
			if not self._env=='':
				if len(self._contents)==0:
					self._enviro = EnvironmentVariable.SetenvTemp(self._env,'.')
					r = self._enviro.satisfy()
				elif self._root=='':
					r = Reason("Tarball ["+self._tarball+"] does not untar into a single top level directory.  Can't set ["+self._env+"].")
				else:
					self._enviro = EnvironmentVariable.SetenvTemp(self._env,self._root)
					r = self._enviro.satisfy()
		return r

	def retract(self):
		r = Reason()
		if hasattr(self._enviro,'type'): self._enviro.restore()
		verbo.log('tar','Removing untarred contents from ['+self._tarball+']...')
		if verbo('tar-brief'): flicker('  Removing '+self._tarball+' contents...')
		
		for x in self._contents:
			if os.path.exists(x):
				if tail(x,'/'): 
#					_tarSave.rem(self.getTarpath(),x)
					if _tarSave.num(x)==0: 
#-- for speed
						r = Execution.execute('rm -r -f "'+x+'"','noclear')
						if not r.ok():
							r2 = Execution.execute('chmod -R a+w "'+x+'"','noclear')
							if r2.ok(): r2 = Execution.execute('rm -r -f "'+x+'"','noclear')
							if r2.ok(): r = r2
					_tarSave.rem(self.getTarpath(),x)
				else:
#					_tarSave.rem(self.getTarpath(),x)
					if _tarSave.num(x)==0: 
						r = Execution.execute('rm -f "'+x+'"','noclear')
						if not r.ok():
							r2 = Execution.execute('chmod a+w "'+x+'"','noclear')
							if r2.ok(): r2 = Execution.execute('rm -f "'+x+'"','noclear')
							if r2.ok(): r = r2
						if 0 and r.ok():
							if self._saved.has_key(x):
								r = ask.re('tar-overwrite','OK to restore ['+x+'] previously overwritten by ['+self._tarball+']?')
								if r.ok():
									verbo.log('tarfiles','Restoring ['+x+'] originally overwritten by untarring ['+self._tarball+']...')
									try:
										f = open(x,'w')
										f.write(self._saved[x])
										f.close()
										del self._saved[x]
									except (IOError,OSError):
										r = Reason("Can't restore saved file ["+x+"] from tarball ["+self._tarball+"].")
					_tarSave.rem(self.getTarpath(),x)
#			if not r.ok(): break
		return r
		
	def verify(self):
		v = verbo('tarfiles')
		if v:
			if len(self._contents)>1000: m = Meter(len(self._contents),'Verifying untarred content of ['+self._tarball+']...')
			else:  print 'Verifying untarred content of ['+self._tarball+']...'
			r = AllReason()
			count = 0
			for x in self._contents:
				count = count + 1
				if len(self._contents)>1000: m.meter(count)
				if not os.path.exists(x): r.append(Reason('Untarred file ['+x+'] from ['+self._tarball+'] is missing.'))
		else:
			r = allReason(self._contents,lambda x: Reason('Untarred file ['+x+'] from ['+self._tarball+'] is missing.',not os.path.exists(x)))
		return r

class UntarzipDeletable(Untarzip):
	type   = 'untar vdt'
	title  = 'Untars vdt'
	action = 'untar vdt'

	def satisfied(self): return Reason('['+`self`+']'+" hasn't been untarred.",not self.acquired)
