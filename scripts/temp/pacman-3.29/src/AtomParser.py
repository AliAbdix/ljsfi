#
#	Copyright Saul Youssef, November 2004
#
from Base                   import *
from Environment            import *
from Registry               import *
from OldAttributes          import *

from DownloadSource         import *
from Platform               import *
from EnvironmentVariable    import *
from FileExists             import *
from InPath                 import *
from ShellCommand           import *
from Username               import *
from PackageName            import *
from URLbare                import *
from Download               import *
from Description            import *
from RPM                    import *
from SuffixHandling         import *
from UsePackageRoot         import *
from LocalDoc               import *
from Setup                  import *
from SystemSetenv           import *
from Paths                  import *
from Demo                   import *
from UninstallShellCommand  import *
from NativelyInstalled      import *

from AtomUtils              import *
from Atoms                  import *
from AtomsExec              import *

import Package
import dictParser
import string
import RelPath
from types import *

def get_src(source,file,cachename):
	if isURL(source):
		src = os.path.join(source,file)
	else:
		src = os.path.join(registry.trans(cachename),source)
		src = os.path.join(src,file)
	return src
	
def shelly(text):
	if 0 and contains(text,'patch condor/condor'): sh = shellDialogue(text+'; pwd')
	else:                                          sh = shellDialogue(text        )
	if not switch('no-compatibility'): sh.mode = 'compatibility'
	return sh

class AtomParser:
#	def __init__(self,packagename='',cachename='',downloadSource='',suffixHandling=1,usePackageRoot=1,useDownloads=1):
	def __init__(self,spec,cachename='',downloadSource='',suffixHandling=1,usePackageRoot=1,useDownloads=1):
		self._spec          = spec
		self.packagename    = spec.name
		self.cachename      = cachename
		self.suffixHandling = suffixHandling
		self.usePackageRoot = usePackageRoot
		self.useDownloads   = useDownloads
		
		self.atts           = OldAttributes()
		self.downloadSource = downloadSource
		
	def attributeCheck(self,atts):
		ok = 1
		for a in atts:
			if a=='self' or a=='text' or a[0]=='_' or self.atts.isAtt(a): pass
			else: ok = 0; break
		return ok
		
	def attTypeError(self,attname):
		if   self.packagename=='' or self.packagename=='internal':
	     		abort('Syntax error. Unknown attribute in ['+attname+'].')
		else:
			abort('Syntax error. Unknown attribute in ['+attname+'] in package ['+self.packagename+'].')
		
	def syntaxCheck(self,o,ok,text):
		if not ok(o):
			if   self.packagename=='': abort('Syntax error in ['+text+'].')
			else:                      abort('Syntax error in ['+text+'] in package ['+self.packagename+'].')

	def newParse(self,text): 
		e = newAttributeExec(text)
		e = self.fixup(e)
		return e
	def fixup(self,e):
		if e.type=='lazy package':
			e._parent      = self._spec
			e._parent.caches = []
			e._parent.guard = ''
		elif e.type=='restore':
			e._par = Package.Spec(self.cachename+':'+self.packagename)
		elif e.type=='download':
			if RelPath.relPath(e._url): e._url = os.path.join(self.cachename,e._url)
		elif e.type=='timed download':
			if RelPath.relPath(e._url): e._download._url = os.path.join(self.cachename,e._download._url)
		elif e.type=='downloadUntarzip':
			if RelPath.relPath(e._url): e._download._url = os.path.join(self.cachename,e._download._url)
		e._parentPackageName = self.packagename
		return e

	def parse(self,text):
		if not newAttributeText(text) and string.strip(text)!='':
			try:
				exec text
				if not self.attributeCheck(dir()): self.attTypeError(text)
			except (SyntaxError,NameError,AttributeError):
				self.attTypeError(text)
		
		environs  = AND()
		thedir = dir()
		if   'depends' in thedir:
			self.syntaxCheck(depends,dependsOK,text)
			environs = AND()
			for d in depends: 
				spec = Package.Spec(d)
				p = Package.LazyPackage(spec)
				p = self.fixup(p)
				p._seq = 4
				environs.append(p)
			
		elif 'setup' in thedir:
			self.syntaxCheck(setup,dependsOK,text)
			for s in setup: 
				x = Setup(s); x._seq = 19
				environs.append(x)
			
		elif 'description' in thedir:
			self.syntaxCheck(description,strOK,text)
			x = Description(description); x._seq = 2
			environs.extend(x)
			
		elif 'systemSetenv' in thedir:
			self.syntaxCheck(systemSetenv,strOK,text)
			x = SystemSetenv(systemSetenv,os.getcwd()); x._seq = 18
			environs.extend(x)
			
		elif 'exists' in thedir:
			self.syntaxCheck(exists,dependsOK,text)
			for filename in exists: 
				x = FileExists(filename); x._seq = 6
				environs.extend(x)
			
		elif 'daemons' in thedir:
			self.syntaxCheck(daemons,dependsOK,text)
			for d in daemons: 
				x = RunningProcess(d); x._seq = 8
				environs.extend(x)
			
		elif 'inpath' in thedir:
			self.syntaxCheck(inpath,dependsOK,text)
			for x in inpath: 
				xx = InPath(x); xx._seq = 7
				environs.extend(xx)
			
		elif 'packageName' in thedir:	
			self.syntaxCheck(packageName,strOK,text)
			x = PackageName(packageName); x._seq = 1
			environs.extend(x)
			
		elif 'demo' in thedir:
			self.syntaxCheck(demo,strOK,text)
			x = Demo(demo); x._seq = 21
			environs.extend(x)
			
		elif 'url' in thedir:
			self.syntaxCheck(url,strOK,text)
			x = URLbare(url); x._seq = 3
			environs.extend(x)
			
		elif 'localdoc' in thedir:
			self.syntaxCheck(localdoc,strOK,text)
			x = URL('local docs',os.path.join('$PAC_TARBALLROOT',localdoc)); x._seq = 20
			environs.extend(x)
			
		elif 'suffixHandling' in thedir:
			self.syntaxCheck(suffixHandling,intOK,text)
			x = SuffixHandling(suffixHandling); x._seq = 9
			environs.extend(x)
			
		elif 'usePackageRoot' in thedir:
			self.syntaxCheck(usePackageRoot,intOK,text)
			x = UsePackageRoot(usePackageRoot); x._seq = 10
			environs.extend(x)
			
		elif 'nativelyInstalled' in thedir:
			x = NativelyInstalled(nativelyInstalled); x._seq = 5
			environs.extend(x)

		elif 'install' in thedir:
			self.syntaxCheck(install,installOK,text)
			eno = OR(); eno._seq = 15
			for user,commands in install.items():
				eu = AND()
				eu.extend(Username(user))
				for c in commands:
					ab,c2 = abcommand(c)
					if self.usePackageRoot and self.useDownloads: eu.extend(shelly('cd $PAC_TARBALLROOT; '+c2))
					else:                                         eu.extend(shelly(                        c2))
				eno.extend(eu)
			if len(eno)!=0: environs.extend(eno)
	
		elif 'enviros' in thedir:	
			self.syntaxCheck(enviros,envirosOK,text)
			for pair in enviros:
				ab,pc = abcommand(pair[1])
				if ab or contains(pair[1],'$'):
					en = Setenv(pair[0],pc)
				elif self.usePackageRoot:
					if self.useDownloads:
						if pair[1]=='':              en = Setenv(pair[0],             '$PAC_TARBALLROOT'         )
						else:                        en = Setenv(pair[0],os.path.join('$PAC_TARBALLROOT',pair[1]))
					else:
						if pair[1]=='': en = Setenv(pair[0],             '$PWD'         )
						else:           en = Setenv(pair[0],os.path.join('$PWD',pair[1]))
				else:
					if pair[1]=='': en = Setenv(pair[0],             '$PWD'         )
					else:           en = Setenv(pair[0],os.path.join('$PWD',pair[1]))
			
				en.export = 1
				en._seq = 13
				environs.extend(en)
				
		elif 'paths' in thedir:
			self.syntaxCheck(paths,envirosOK,text)
			for pair in paths:
				ab,pc = abcommand(pair[1])
				if ab or contains(pair[1],'$'):
					en = Path(pc,pair[0],'front','',1)
				elif self.usePackageRoot:
					if self.useDownloads: 
						if pair[1]=='':  en = Path(             '$PAC_TARBALLROOT',         pair[0],'front','',1)
						else:            en = Path(os.path.join('$PAC_TARBALLROOT',pair[1]),pair[0],'front','',1)
					else:    
						if pair[1]=='':  en = Path(             '$PWD',                     pair[0],'front','',1)
						else:            en = Path(os.path.join('$PWD',            pair[1]),pair[0],'front','',1)
				else:
					if pair[1]=='':  en = Path(             '$PWD',         pair[0],'front','',1)
					else:            en = Path(os.path.join('$PWD',pair[1]),pair[0],'front','',1)
			
				en.export = 1
				en._seq = 14
				environs.extend(en)
				
		elif 'uninstall' in thedir:
			self.syntaxCheck(uninstall,dependsOK,text)
			ens = AND()
			for i in range(len(uninstall)-1,-1,-1): 
				x = UninstallShellCommand(uninstall[i])
				x._seq = 17
				ens.extend(x)
			return ens

		elif 'source' in thedir:
			self.syntaxCheck(source,strOK,text)
			strOK(source)
			x = DownloadSource(source); x._seq = 11
			environs.extend(x)
		
		elif 'download' in thedir:
			self.syntaxCheck(download,downloadOK,text)
			downloads = dictParser.dictParser(text)
			eno = OR(); eno._seq = 12
			for platform,downfile in downloads:
				enp = AND()
				if downfile!='':
					enp.extend(PlatformGE(platform))
					src = get_src(self.downloadSource,downfile,self.cachename)
					if self.suffixHandling:
						if tail(downfile,'.rpm'):
							enp.extend(RPM(os.path.basename(src)))
						elif tail(downfile,'.tar') or tail(downfile,'.tar.gz') or tail(downfile,'.tgz') or tail(downfile,'tar.Z'):
							d = DownloadUntarzip(src,'PAC_TARBALLROOT')
							d._untar._check = 0
							enp.extend(d)
						else:
							enp.extend(Download(src,1))
					else:
						enp.extend(Download(src,1))
				eno.extend(enp)
			environs.extend(eno)
			
		elif 'systems' in thedir:
			self.syntaxCheck(systems,systemsOK,text)
			eno = OR(); eno._seq = 12
			got_one = 0
			for platform,pair in systems.items():
				downfile = pair[0]
				enp = AND()
				if downfile!='':
					enp.extend(PlatformGE(platform))
					src = get_src(self.downloadSource,downfile,self.cachename)
					if self.suffixHandling:
						if tail(downfile,'.rpm'):
							enp.extend(RPM(os.path.basename(src)))
						elif tail(downfile,'.tar') or tail(downfile,'.tar.gz') or tail(downfile,'.tgz') or tail(downfile,'tar.Z'):
							d = DownloadUntarzip(src,'PAC_TARBALLROOT')
							d._untar._check = 0
							enp.extend(d)
						else:
							enp.extend(Download(src,1))
					else:
						enp.extend(Download(src,1))
					if pair[1]=='.' or pair[1]=='./': got_one = 1
				eno.extend(enp)
			if got_one: 
				environs.extend(eno)
				environs.extend(UsePackageRoot(0))
			else:
				environs.extend(eno)
		else:
			if text=='': environs = AND()
			else:        environs = self.newParse(text)

		return environs
