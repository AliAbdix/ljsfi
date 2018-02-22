#
#	Copyright, August 2004, Saul Youssef
#
from Base        import *
from Environment import *
import Cache,InstallationCache,InstallationBase,Platform,ShellCommand,LastVersion,UniversalCache
import os,anydbm

if os.path.exists(os.path.join(pacmanDir,'ii3.1')): oversion = '3.19'
else:                                               oversion = version[:]

class Home(Cache.Cache):
	_home = Cache.Cache()
	_init = 0
	
	def __init__(self):
		self.type = 'home'
		if not Home._init: 
			UCL = os.getcwd()
			os.environ['PAC_ANCHOR'] = pac_anchor
			if os.path.exists(os.path.join(pacmanDir,'platform')):
				plat = get(os.path.join(pacmanDir,'platform'))
				if not allow('any-platform') and not plat==Platform.Platform():
					print 'Installation at ['+pac_anchor+'] was made on ['+plat.str()+'].'
					print 'Attempt to access installation ['+pac_anchor+'] from ['+Platform.Platform().str()+'].'
					import lock
					lock.unlock()
					sys.exit(1)
				try:
					f = open(os.path.join(pac_anchor,pacmanDir,'anchor'),'r')
					lines = f.readlines()
					f.close()
					if len(lines)==1 and len(lines[0])>1 and lines[0][:-1]==pac_anchor: pass
					else:
						print "Pacman installation has been moved from ["+lines[0][:-1]+"]."
						sys.exit(1)
				except (IOError,OSError):
					print "Pacman installation has been moved."
					sys.exit(1)
			else:
				InstallationBase.installationBase(UCL).satisfy().require()
				if os.path.isdir(pacmanDir): Platform.Platform().put(os.path.join(pacmanDir,'platform'))
				try:
					f = open(os.path.join(pac_anchor,pacmanDir,'anchor'),'w')
					f.write(pac_anchor+'\n')
					f.close()
					f = open(os.path.join(pac_anchor,pacmanDir,'version'),'w')
					f.write(version+'\n')
					f.close()
				except (IOError,OSError):
					print "Error writing to ["+os.path.join(pac_anchor,pacmanDir)+"]."
					removeFile(os.path.join('pac_anchor','pacmanDir','lock'))
					sys.exit(1)
				lv = LastVersion.lastVersion()
				if verbo('http'): print 'version ['+lv+']'
				if not lv=='' and lv>version: print 'Pacman ['+lv+'] is available at http://physics.bu.edu/pacman/...'
				
			if os.path.exists(os.path.join(pac_anchor,pacmanDir,'version')):
				try:
					f = open(os.path.join(pac_anchor,pacmanDir,'version'),'r')
					lines = f.readlines()
					f.close()
				except (IOError,OSError):
					abort("Can't read ["+os.path.join(pac_anchor,pacmanDir,'version')+"].")
				if len(lines)>0 and len(lines[0])>1:
					ver = string.strip(lines[0][:-1])
					if ver>version: 
						print "This Pacman installation was created with Pacman version ["+ver+"]."
						print "You are using Pacman version ["+version+"]."
						print "Pacman version must be >= ["+ver+"]."
						removeFile(os.path.join(pac_anchor,pacmanDir,'lock'))
						sys.exit(1)
				
			if os.path.isdir(os.path.join(pac_anchor,pacmanDir,'ii3.1')) or use_old_database:
				verbo.log('io','Using old database for home installation.')
				Home._home = InstallationCache.OldInstallationCache(UCL)
			else:

#			Home._home = UniversalCache.UniversalCache(UCL)._cache
				
				Home._home = InstallationCache.   InstallationCache(UCL)
			Home._home.init()
			Home._init = 1
			self.UCL = Home._home.UCL
		if not os.path.isdir(os.path.join(pac_anchor,pacmanDir)):
			print 'Pacman installation area ['+os.path.join(pac_anchor,pacmanDir)+'] is missing.'
			abort('Pacman installation area ['+os.path.join(pac_anchor,pacmanDir)+'] is missing.')
		r,line = firstLine(os.path.join(pac_anchor,pacmanDir,'version'))
		if r.ok() and version<string.strip(line) and not contains(line,'pre-release'): 
			print "Pacman installation was created with Pacman version ["+string.strip(line)+"] but"
			print "you are using Pacman version ["+version+"]."
			print "You must use Pacman version ["+string.strip(line)+"] or greater for this installation."
			import lock
			lock.unlock()
			sys.exit(1)
#			abort("You must use Pacman version ["+version+"] or greater for this installation.")
		if not os.path.exists(os.path.join(pac_anchor,pacmanDir,'ie'+oversion[:3])):
			print 'This Pacman installation was made with Pacman < '+oversion[:3]+'.'
			print 'To use Pacman version ['+version+'], you must re-install.'
			import lock
			lock.unlock()
			sys.exit(1)
		os.environ['TMP'] = os.path.join(pac_anchor,pacmanDir,'tmp')
			
	def save(self):
		if self._init and not self._home==Cache.Cache():
			Home._home.save()
			Home._init = 0
			
	def __repr__(self): return `self._home`
	def __eq__(self,x): return self._type()==x._type() and self._home==x._home
	def display(self,indent=0): self._home.display(indent)
	def displaySpecs(self,specs,mode='',depth=99999): return self._home.displaySpecs(specs,mode,depth)
	def displayTops(self,mode='',depth=99999): return self._home.displayTops(mode,depth)

	def getAll        (self,spec,used): return self._home.getAll(spec,used)
	def contents      (self,used     ): return self._home.contents(used)
	def put           (self,package  ): return self._home.put(package)
	def remove        (self,spec     ): return self._home.remove(spec)
	def topSpecs      (self          ): return self._home.topSpecs()
	def refreshParents(self          ): return self._home.refreshParents()
	def getLocation   (self,location ): return self._home.getLocation(location)

home = Home()

