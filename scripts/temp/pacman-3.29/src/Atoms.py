#
#	Copyright Saul Youssef, January, 2005
#
import string,os
from types                          import *
from Environment                    import *
from Base                           import *

from EnvironmentVariable            import *
from FileExists                     import *
from InPath                         import *
from Directory                      import *
#from PersistentDirectory            import *
from Platform                       import *
from Username                       import *
from URL                            import *
from ShellCommand                   import *
from UninstallShellCommand          import *
from Description                    import *
from FreeMegs                       import *
from FreeDiskMegs                   import *
from Cp                             import *
from CD                             import *
from CU                             import *
from LS                             import *
from MV                             import *
from Download                       import *
from Chown                          import *
from ChownR                         import *
from RunningProcess                 import *
from TCPPorts                       import *
from UDPPorts                       import *
#from Env                            import *
from DirectoryChoice                import *
from URLvisible                     import *
from URLbare                        import *
from Untarzip                       import *
from PackageName                    import *
from Setup                          import *
from TarballRoot                    import *
from RPM                            import *
from Paths                          import *
from RPMinstalled                   import *
from CWD                            import *
from Anchor                         import *
from WriteProtect                   import *
from TextFile                       import *
from PackageRevision                import *
from Version                        import *
from Choice                         import *
from Message                        import *
from Computer                       import *
from GccVersion                     import *
from PerlVersion                    import *
from PythonVersion                  import *
from PacmanVersion                  import *
from LinuxKernel                    import *
from SSHVersion                     import *
from UserExists                     import *
from PythonScript                   import *
from Alias                          import *
from SoftLink                       import *
from IntAttr                        import *
from TimeErrorMaximum               import *
from TrueFalse                      import *
from SystemExtras                   import *
from TextLine                       import *
from Mail                           import *
from WorkSpace                      import *
from FileAccess                     import *
#from Registry                       import *
#from InstalledPackage               import *
from FileTransferSpeed              import *
#from RemoteGroup                    import *
from CommandLineSwitch              import *

from AtomUtils                      import *
#import Package,Installation,Cat
import Package,Cat,Already,Watch,SaveRestore,Md5sumCheck,Registry,AbsPath
import GlibcVersion

from AtomDoc import *

catd = AtomDoc('cat','path')

def absPath(path='.'):
	strArg(path,'absPath')
	return AbsPath.AbsPath(path)

def md5check(path,md5string):
	strArg(path,'md5check')
	strArg(md5string,'md5check')
	return Md5sumCheck.Md5sumCheck(path,md5string)

def restore(filename):
	strArg(filename,'restore')
	return SaveRestore.RestoreFromUninstall(filename)

def cat(path):
	strArg(path,'cat')
	return Cat.Cat(path)
	
def alreadyInstalled(packageSpecification):
	strArg(packageSpecification,'already')
	return Already.AlreadyInstalled(packageSpecification)

def commandLineSwitch(switch):
	strArg(switch,'commandLineSwitch')
	return CommandLineSwitch(switch)

def emptyDirectory(dirpath):
	strArg(dirpath,'emptyDirectory')
	return DirectoryEmpty(dirpath)

def directoryContains(dirpath,files=[]):
	strArg(dirpath,'directoryContains')
	if not hasattr(files,'__len__') and hasattr(files,'__getitem__'):
		abort('Syntax error: Second argument to directoryContains is not a list.')
	return DirectoryContains(dirpath,files)

#
#def monitorRemotePackage(packageSpec,location):
#	strArg(  packageSpec, 'monitorRemotePackage')
#	strArg(     location, 'monitorRemotePackage')
#	return MonitorRemotePackage.MonitorRemotePackage(packageSpec,location)

#def remoteGroup(groupName,packageSpec):
#	strArg(   groupName,  'remoteGroup')
#	strArg( packageSpec,  'remoteGroup')
#	return RemoteGroup(groupName,packageSpec)
#
#def remoteSite(host,location,username=getusername(),shell='sh'):
#	strArg(        host,  'passiveRemote')
#	strArg(    location,  'passiveRemote')
#	strArg(    username,  'passiveRemote')
#	strArg(       shell,  'passiveRemote')
#	return Installation.PassiveRemoteInstallation(Computer(host,location,username,shell))
#
#def remotePackage(packageSpec,host,location,username=getusername(),shell='sh'):
#	strArg(packageSpec,'remoteInstallation')
#	strArg(host,'remoteInstallation')
#	strArg(location,'remoteInstallation')
#	strArg(username,'remoteInstallation')
#	strArg(shell,'remoteInstallation')
#	return Installation.RemotePackage(Package.Package(packageSpec),Computer(host,location,username,shell))
#
def launchWebBrowser(url):
	strArg(url,'launchWebBrowser')
	return LaunchBrowser(url)

def downloadTime(path,maximumSeconds):
	strArg(path,'timedDownload')
	argchk(maximumSeconds,FloatType,'timedDownload')
	return DownloadTime(path,maximumSeconds)

def fileCopyMinimumMegsPerSecond(minimumMegsPerSecond,fileSizeInMegs=1000,path='.'):
	strArg(path,'fileTransferMinimumMegsPerSecond')
	intArg(fileSizeInMegs,'fileTransferMinimumMegsPerSecond')
#	argchk(minimumMegsPerSecond,FloatType,'fileTransferMinimumMegsPerSecond')
	return FileTransferSpeedMinimum(path,minimumMegsPerSecond,fileSizeInMegs)

#def alreadyInstalled(packageString):
#	strArg(packageString,'alreadyInstalled')
#	return InstalledPackage(packageString)

def register(symbolicName,cacheUrl,infoString='',infoUrl='',contactString='',contactEmail=''):
	strArg(symbolicName,      'registry')
	strArg(cacheUrl,          'registry')
	strArg(infoString,        'registry')
	strArg(infoUrl,           'registry')
	strArg(contactString,     'registry')
	strArg(contactEmail,      'registry')
	r = Registry.Register(symbolicName,cacheUrl,infoString,infoUrl,contactString,contactEmail)
#	r.satisfy().require()
	r.satisfy()
	return r
#	return Register(symbolicName,cacheUrl,infoString,infoUrl,contactString,contactEmail)

def workspace(name,environmentVariable,minmegs,owner=getusername(),options='ownerWrite permanent'):
	strArg(name,'workspace')
	strArg(environmentVariable,'workspace')
	intArg(minmegs,'workspace')
	strArg(owner,'workspace')
	strArg(options,'workspace')
	
	return WorkSpace(name,environmentVariable,minmegs,owner,options)

def  isWorldRead   (path,action='on'):
	strArg(path,'isWorldRead'); strArg(action,'isWorldRead')
	return HasFileAccess(path,'worldRead',action)
def  isWorldWrite  (path,action='on'):
	strArg(path,'isWorldWrite'); strArg(action,'isWorldWrite')
	return HasFileAccess(path,'worldWrite',action)
def  isWorldExecute(path,action='on'):
	strArg(path,'isWorldExecute'); strArg(action,'isWorldExecute')
	return HasFileAccess(path,'worldExecute',action)
def  isGroupRead   (path,action='on'):
	strArg(path,'isGroupRead'); strArg(action,'isGroupRead')
	return HasFileAccess(path,'groupRead',action)
def  isGroupWrite  (path,action='on'):
	strArg(path,'isGroupWrite'); strArg(action,'isGroupWrite')
	return HasFileAccess(path,'groupWrite',action)
def  isGroupExecute(path,action='on'):
	strArg(path,'isGroupExecute'); strArg(action,'isGroupExecute')
	return HasFileAccess(path,'groupExecute',action)
def  isOwnerRead   (path,action='on'):
	strArg(path,'isOwnerRead'); strArg(action,'isOwnerRead')
	return HasFileAccess(path,'ownerRead',action)
def  isOwnerWrite  (path,action='on'):
	strArg(path,'isOwnerWrite'); strArg(action,'isOwnerWrite')
	return HasFileAccess(path,'ownerWrite',action)
def  isOwnerExecute(path,action='on'):
	strArg(path,'isOwnerExecute'); strArg(action,'isOwnerExecute')
	return HasFileAccess(path,'ownerExecute',action)

def  isWorldReadable   (path,action='on'):
	strArg(path,'isWorldRead'); strArg(action,'isWorldRead')
	return HasFileAccess(path,'worldRead',action)
def  isWorldWriteable  (path,action='on'):
	strArg(path,'isWorldWrite'); strArg(action,'isWorldWrite')
	return HasFileAccess(path,'worldWrite',action)
def  isWorldWritable  (path,action='on'):
	strArg(path,'isWorldWrite'); strArg(action,'isWorldWrite')
	return HasFileAccess(path,'worldWrite',action)
def  isWorldExecuteable(path,action='on'):
	strArg(path,'isWorldExecute'); strArg(action,'isWorldExecute')
	return HasFileAccess(path,'worldExecute',action)
def  isWorldExecutable(path,action='on'):
	strArg(path,'isWorldExecute'); strArg(action,'isWorldExecute')
	return HasFileAccess(path,'worldExecute',action)
def  isGroupReadable   (path,action='on'):
	strArg(path,'isGroupRead'); strArg(action,'isGroupRead')
	return HasFileAccess(path,'groupRead',action)
def  isGroupWriteable  (path,action='on'):
	strArg(path,'isGroupWrite'); strArg(action,'isGroupWrite')
	return HasFileAccess(path,'groupWrite',action)
def  isGroupWritable  (path,action='on'):
	strArg(path,'isGroupWrite'); strArg(action,'isGroupWrite')
	return HasFileAccess(path,'groupWrite',action)
def  isGroupExecuteable(path,action='on'):
	strArg(path,'isGroupExecute'); strArg(action,'isGroupExecute')
	return HasFileAccess(path,'groupExecute',action)
def  isGroupExecutable(path,action='on'):
	strArg(path,'isGroupExecute'); strArg(action,'isGroupExecute')
	return HasFileAccess(path,'groupExecute',action)
def  isOwnerReadable   (path,action='on'):
	strArg(path,'isOwnerRead'); strArg(action,'isOwnerRead')
	return HasFileAccess(path,'ownerRead',action)
def  isOwnerWriteable  (path,action='on'):
	strArg(path,'isOwnerWrite'); strArg(action,'isOwnerWrite')
	return HasFileAccess(path,'ownerWrite',action)
def  isOwnerWritable  (path,action='on'):
	strArg(path,'isOwnerWrite'); strArg(action,'isOwnerWrite')
	return HasFileAccess(path,'ownerWrite',action)
def  isOwnerExecuteable(path,action='on'):
	strArg(path,'isOwnerExecute'); strArg(action,'isOwnerExecute')
	return HasFileAccess(path,'ownerExecute',action)
def  isOwnerExecutable(path,action='on'):
	strArg(path,'isOwnerExecute'); strArg(action,'isOwnerExecute')
	return HasFileAccess(path,'ownerExecute',action)
	
def setWorldRead(path,action='on'):
	strArg(path,  'setWorldReadable')
	strArg(action,'setWorldReadable')
	return FileAccess(path,'worldRead',action)
def setWorldWrite(path,action='on'):
	strArg(path,  'setWorldWriteable')
	strArg(action,'setWorldWriteable')
	return FileAccess(path,'worldWrite',action)
def setWorldExecute(path,action='on'):
	strArg(path,  'setWorldExecutable')
	strArg(action,'setWorldExecutable')
	return FileAccess(path,'worldExecute',action)
def setGroupRead(path,action='on'):
	strArg(path,  'setGroupReadable')
	strArg(action,'setGroupReadable')
	return FileAccess(path,'groupRead',action)
def setGroupWrite(path,action='on'):
	strArg(path,  'setGroupWriteable')
	strArg(action,'setGroupWriteable')
	return FileAccess(path,'groupWrite',action)
def setGroupExecute(path,action='on'):
	strArg(path,  'setGroupExecutable')
	strArg(action,'setGroupExecutable')
	return FileAccess(path,'groupExecute',action)
def setOwnerRead(path,action='on'):
	strArg(path,  'setOwnerReadable')
	strArg(action,'setOwnerReadable')
	return FileAccess(path,'ownerRead',action)
def setOwnerWrite(path,action='on'):
	strArg(path,  'setOwnerWriteable')
	strArg(action,'setOwnerWriteable')
	return FileAccess(path,'ownerWrite',action)
def setOwnerExecute(path,action='on'):
	strArg(path,  'setOwnerExecutable')
	strArg(action,'setOwnerExecutable')
	return FileAccess(path,'ownerExecute',action)
	
def setWorldReadable(path,action='on'):
	strArg(path,  'setWorldReadable')
	strArg(action,'setWorldReadable')
	return FileAccess(path,'worldRead',action)
def setWorldWriteable(path,action='on'):
	strArg(path,  'setWorldWriteable')
	strArg(action,'setWorldWriteable')
	return FileAccess(path,'worldWrite',action)
def setWorldWritable(path,action='on'):
	strArg(path,  'setWorldWriteable')
	strArg(action,'setWorldWriteable')
	return FileAccess(path,'worldWrite',action)
def setWorldExecuteable(path,action='on'):
	strArg(path,  'setWorldExecutable')
	strArg(action,'setWorldExecutable')
	return FileAccess(path,'worldExecute',action)
def setWorldExecutable(path,action='on'):
	strArg(path,  'setWorldExecutable')
	strArg(action,'setWorldExecutable')
	return FileAccess(path,'worldExecute',action)
def setGroupReadable(path,action='on'):
	strArg(path,  'setGroupReadable')
	strArg(action,'setGroupReadable')
	return FileAccess(path,'groupRead',action)
def setGroupWriteable(path,action='on'):
	strArg(path,  'setGroupWriteable')
	strArg(action,'setGroupWriteable')
	return FileAccess(path,'groupWrite',action)
def setGroupWritable(path,action='on'):
	strArg(path,  'setGroupWriteable')
	strArg(action,'setGroupWriteable')
	return FileAccess(path,'groupWrite',action)
def setGroupExecuteable(path,action='on'):
	strArg(path,  'setGroupExecutable')
	strArg(action,'setGroupExecutable')
	return FileAccess(path,'groupExecute',action)
def setGroupExecutable(path,action='on'):
	strArg(path,  'setGroupExecutable')
	strArg(action,'setGroupExecutable')
	return FileAccess(path,'groupExecute',action)
def setOwnerReadable(path,action='on'):
	strArg(path,  'setOwnerReadable')
	strArg(action,'setOwnerReadable')
	return FileAccess(path,'ownerRead',action)
def setOwnerWriteable(path,action='on'):
	strArg(path,  'setOwnerWriteable')
	strArg(action,'setOwnerWriteable')
	return FileAccess(path,'ownerWrite',action)
def setOwnerWritable(path,action='on'):
	strArg(path,  'setOwnerWriteable')
	strArg(action,'setOwnerWriteable')
	return FileAccess(path,'ownerWrite',action)
def setOwnerExecuteable(path,action='on'):
	strArg(path,  'setOwnerExecutable')
	strArg(action,'setOwnerExecutable')
	return FileAccess(path,'ownerExecute',action)
def setOwnerExecutable(path,action='on'):
	strArg(path,  'setOwnerExecutable')
	strArg(action,'setOwnerExecutable')
	return FileAccess(path,'ownerExecute',action)

def ownedBy(path,owner=getusername()):
	strArg(path,'ownedBy')
	strArg(owner,'ownedBy')
	return OwnedBy(path,owner)

def mail(mailto,subject='',body=[]):
	strArg(mailto,     'mail')
	strArg(subject,    'mail')
	return Mail(mailto,subject,body)

def globusAccess(dn,localusername,position='first'):
	strArg(dn,                'globusAccess')
	strArg(localusername,     'globusAccess')
	strArg(position,          'globusAccess')
	return GlobusUserAccess(dn,localusername,position)

def hasGlobusAccess(dn,localusername,position='first'):
	strArg(dn,               'hasGlobusAccess')
	strArg(localusername,    'hasGlobusAccess')
	strArg(position,         'hasGlobusAccess')
	return GlobusUserHasAccess(dn,localusername,position)

def sshAccess(username,public_key):
	strArg(username,        'sshAccess')
	strArg(public_key,      'sshAccess')
	return SSHUserAccess(username,public_key)

def hasSshAccess(username,public_key):
	strArg(username,'hasSshAccess')
	strArg(public_key,'hasSshAccess')
	return SSHUserHasAccess(username,public_key)

def insertLine(line,filepath,justAfterLineContaining='back',comment='#'):
	strArg(line,'insertLine')
	strArg(filepath,'insertLine')
	return TextLineInsertion(filepath,line,justAfterLineContaining,comment)

def textFileContainsText(text,filepath,comment='#'):
	strArg(filepath,'textFileContainsText')
	strArg(text,'textFileContainsText')
	return TextFileContainsText(filepath,text,comment)
	
def grep(text,filepath,comment='#'): 
	strArg(filepath,'textFileContainsText')
	strArg(text,'textFileContainsText')
	return textFileContainsText(text,filepath,comment)

def timeErrorMaximum(sec):
	argchk(sec,FloatType,'timeErrorMaximum')
	return TimeErrorMaximum(sec)

def cpuSecondsSoft(sec):
	intArg(sec,'cpuSecondsSoft')
	return CPUSecondsMaximumSoftGE(sec)
	
def cpuSecondsHard(sec):
	intArg(sec,'cpuSecondsHard')
	return CPUSecondsMaximumHardGE(sec)
	
def cpuSeconds(sec):
	intArg(sec,'cpuSeconds')
	return CPUSecondsMaximumGE(sec)
	
def fileSizeSoft(size):
	return FileSizeMaximumSoftGE(size)
	
def fileSizeHard(size):
	return FileSizeMaximumHardGE(size)
	
def fileSize(size):
	return FileSizeMaximumGE(size)
	
def heapSize(size):
	return HeapSizeMaximumGE(size)
	
def stackSize(size):
	return StackSizeMaximumGE(size)
	
def imageSize(size):
	return HeapSizeMaximumGE(size)
	
def openFileDescriptorsSoft(size):
	intArg(size,'openFileDescriptorsSoft')
	return OpenFileDescriptorsMaximumSoftGE(size)
	
def openFileDescriptorsHard(size):
	intArg(size,'openFileDescriptorsHard')
	return OpenFileDescriptorsMaximumHardGE(size)
	
def openFileDescriptors(size):
	intArg(size,'openFileDescriptors')
	return OpenFileDescriptorsMaximumGE(size)

def systemWordSize(wordstring):
	strArg(wordstring,'systemWordSize')
	return SystemWordSize(wordstring)
	
def processor(text):
	strArg(text,'processor')
	return CPU(text)
	
def byteOrder(text):
	strArg(text,'byteOrder')
	return ByteOrder(text)

def systemVersion(text):
	strArg(text,'systemVersion')
	return SystemVersionEQ(text)
	
def systemVersionLE(text):
	strArg(text,'systemVersionLE')
	return SystemVersionLE(text)
	
def systemVersionLT(text):
	strArg(text,'systemVersionLT')
	return SystemVersionLT(text)
	
def systemVersionGE(text):
	strArg(text,'systemVersionGE')
	return SystemVersionGE(text)
	
def systemVersionGT(text):
	strArg(text,'systemVersionGT')
	return SystemVersionGT(text)
	
def systemRelease(text):
	strArg(text,'systemRelease')
	return SystemReleaseEQ(text)
	
def systemReleaseLE(text):
	strArg(text,'systemReleaseLE')
	return SystemReleaseLE(text)
	
def systemReleaseLT(text):
	strArg(text,'systemReleaseLT')
	return SystemReleaseLT(text)
	
def systemReleaseGE(text):
	strArg(text,'systemReleaseGE')
	return SystemReleaseGE(text)
	
def systemReleaseGT(text):
	strArg(text,'systemReleaseGT')
	return SystemReleaseGT(text)
	
def systemReleaseGT(text):
	strArg(text,'sytsemReleaseGT')
	return SystemReleaseGT(text)
	
def pythonCompilerCompiler(text):
	strArg(text,'pythonCompilerCompiler')
	return PythonCompiler(text)

# packageRevision atom added by Scot Kronenfeld 2/2009
def packageRevision(os='',arch='',rev='',comment=''):
	strArg(os,      'packageRevision')
	strArg(arch,    'packageRevision')
	strArg(rev,     'packageRevision')
	strArg(comment, 'packageRevision')
	return PackageRevision(os,arch,rev,comment)

def version(arg):
	strArg(arg,'version')
	return Version(arg)
	
def versionLE(arg):
	strArg(arg,'versionLE')
	return VersionLE(arg)
	
def versionLT(arg):
	strArg(arg,'versionLT')
	return VersionLT(arg)
	
def versionGE(arg):
	strArg(arg,'versionGE')
	return VersionGE(arg)
	
def versionGT(arg):
	strArg(arg,'versionGT')
	return VersionGT(arg)
	
def versionTuple(arg,separator='.'):
	strArg(arg,'versionTuple')
	strArg(separator,'versionTuple')
	return VersionTuple(arg,separator)
	
def versionTupleLE(arg,separator='.'):
	strArg(arg,'versionTupleLE')
	strArg(separator,'versionTupleLE')
	return VersionTupleLE(arg,separator)
	
def versionTupleLT(arg,separator='.'):
	strArg(arg,'versionTupleLT')
	strArg(separator,'versionTupleLT')
	return VersionTupleLT(arg,separator)
	
def versionTupleGE(arg,separator='.'):
	strArg(arg,'versionTupleGE')
	strArg(separator,'versionTupleGE')
	return VersionTupleGE(arg,separator)
	
def versionTupleGT(arg,separator='.'):
	strArg(arg,'versionTupleGT')
	strArg(separator,'versionTupleGT')
	return VersionTuple(arg,separator)
	
def release(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	strArg(text,'release')
	return Release(text)
	
def releaseLE(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	return ReleaseLE(text)
	
def releaseLT(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	return ReleaseLT(text)
	
def releaseGE(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	return ReleaseGE(text)
	
def releaseGT(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	return ReleaseGT(text)
	
def tag(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	strArg(text,'tag')
	return Tag(text)
	
def tagLE(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	return TagLE(text)
	
def tagLT(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	return TagLT(text)
	
def tagGE(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	return TagGE(text)
	
def tagGT(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	return TagGT(text)
	
def patch(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	strArg(text,'patch')
	return Patch(text)
	
def patchLE(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	return PatchLE(text)
	
def patchLT(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	return PatchLT(text)
	
def patchGE(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	return PatchGE(text)
	
def patchGT(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	return PatchGT(text)
	
def option(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	strArg(text,'option')
	return Option(text)
	
def optionLE(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	return OptionLE(text)
	
def optionLT(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	return OptionLT(text)
	
def optionGE(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	return OptionGE(text)
	
def optionGT(arg):
	if type(arg)==StringType: text = arg
	else:                     text = `arg`
	return OptionGT(text)

def gccVersion(arg):
	strArg(arg,'gccVersion')
	return GccVersion(arg)
	
def gccVersionLE(arg):
	strArg(arg,'gccVersionLE')
	return GccVersionLE(arg)
	
def gccVersionLT(arg):
	strArg(arg,'gccVersionLT')
	return GccVersionLT(arg)
	
def gccVersionGE(arg):
	strArg(arg,'gccVersionGE')
	return GccVersionGE(arg)
	
def gccVersionGT(arg):
	strArg(arg,'gccVersionGT')
	return GccVersionGT(arg)
	
def gccVersion(arg):
	strArg(arg,'gccVersion')
	return GccVersion(arg)
	
def glibcVersion(arg):
	strArg(arg,'gccVersion')
	return GlibcVersion.GlibcVersion(arg)
	
def glibcVersionLE(arg):
	strArg(arg,'gccVersionLE')
	return GlibcVersion.GlibcVersionLE(arg)
	
def glibcVersionLT(arg):
	strArg(arg,'gccVersionLT')
	return GlibcVersion.GlibcVersionLT(arg)
	
def glibcVersionGE(arg):
	strArg(arg,'gccVersionGE')
	return GlibcVersion.GlibcVersionGE(arg)
	
def glibcVersionGT(arg):
	strArg(arg,'gccVersionGT')
	return GlibcVersion.GlibcVersionGT(arg)

def gccBinary(path,ver):
	strArg(path,'gccBinaryEQ')
	strArg(ver,'gccBinaryEQ')
	return GccBinaryEQ(path,ver)
	
def gccBinaryLE(path,ver):
	strArg(path,'gccBinaryLE')
	strArg(ver,'gccBinaryLE')
	return GccBinaryLE(path,ver)
	
def gccBinaryLT(path,ver):
	strArg(path,'gccBinaryLT')
	strArg(ver,'gccBinaryLT')
	return GccBinaryLT(path,ver)
	
def gccBinaryGE(path,ver):
	strArg(path,'gccBinaryGE')
	strArg(ver,'gccBinaryGE')
	return GccBinaryGE(path,ver)
	
def gccBinaryGT(path,ver):
	strArg(path,'gccBinaryGT')
	strArg(ver,'gccBinaryGT')
	return GccBinaryGT(path,ver)
	
def pythonVersion(arg):
	strArg(arg,'pythonVersion')
	return PythonVersion(arg)
	
def pythonVersionLE(arg):
	strArg(arg,'pythonVersionLE')
	return PythonVersionLE(arg)
	
def pythonVersionLT(arg):
	strArg(arg,'pythonVersionLT')
	return PythonVersionLT(arg)
	
def pythonVersionGE(arg):
	strArg(arg,'pythonVersionGE')
	return PythonVersionGE(arg)
	
def pythonVersionGT(arg):
	strArg(arg,'pythonVersionGT')
	return PythonVersionGT(arg)

def sshVersion(arg):
	strArg(arg,'sshVersion')
	return SSHVersion(arg)
	
def sshVersionLE(arg):
	strArg(arg,'sshVersionLE')
	return SSHVersionLE(arg)
	
def sshVersionLT(arg):
	strArg(arg,'sshVersionLT')
	return SSHVersionLT(arg)
	
def sshVersionGE(arg):
	strArg(arg,'sshVersionGE')
	return SSHVersionGE(arg)
	
def sshVersionGT(arg):
	strArg(arg,'sshVersionGT')
	return SSHVersionGT(arg)

def perlVersion(arg):
	strArg(arg,'perlVersion')
	return PerlVersion(arg)
	
def perlVersionLE(arg):
	strArg(arg,'perlVersionLE')
	return PerlVersionLE(arg)
	
def perlVersionLT(arg):
	strArg(arg,'perlVersionLT')
	return PerlVersionLT(arg)
	
def perlVersionGE(arg):
	strArg(arg,'perlVersionGE')
	return PerlVersionGE(arg)
	
def perlVersionGT(arg):
	strArg(arg,'perlVersionGT')
	return PerlVersionGT(arg)

def linuxKernel(arg):
	strArg(arg,'linuxKernel')
#	return LinuxKernel(arg)
	return AND(PlatformGE('Linux'),SystemReleaseEQ(arg))
	
def linuxKernelLE(arg):
	strArg(arg,'linuxKernelLE')
#	return LinuxKernelLE(arg)
	return AND(PlatformGE('Linux'), SystemReleaseLE(arg))
	
def linuxKernelLT(arg):
	strArg(arg,'linuxKernelLT')
#	return LinuxKernelLT(arg)
	return AND(PlatformGE('Linux'), SystemReleaseLT(arg))
	
def linuxKernelGE(arg):
	strArg(arg,'linuxKernelGE')
#	return LinuxKernelGE(arg)
	return AND(PlatformGE('Linux'), SystemReleaseGE(arg))
	
def linuxKernelGT(arg):
	strArg(arg,'linuxKernelGT')
#	return LinuxKernelGT(arg)
	return AND(PlatformGE('Linux'), SystemReleaseGT(arg))

def pacmanVersion(arg):
	strArg(arg,'pacmanVersion')
	return PacmanVersion(arg)
	
def pacmanVersionLE(arg):
	strArg(arg,'pacmanVersionLE')
	return PacmanVersionLE(arg)
	
def pacmanVersionLT(arg):
	strArg(arg,'pacmanVersionLT')
	return PacmanVersionLT(arg)
	
def pacmanVersionGE(arg):
	strArg(arg,'pacmanVersionGE')
	return PacmanVersionGE(arg)
	
def pacmanVersionGT(arg):
	strArg(arg,'pacmanVersionGT')
	return PacmanVersionGT(arg)

def setenv(a1,a2=''):
	strArg(a1,'setenv'); strArg(a2,'setenv')
	return Setenv(a1,a2)
	
def setenvTemp(a1,a2=''):
	strArg(a1,'setenvTemp'); strArg(a2,'setenvTemp')
	return SetenvTemp(a1,a2)
	
def env(env):
	strArg(env,'env')
	return Env(env)
	
def envIsSet(env):
	strArg(env,'envIsSet')
	return EnvIsSet(env)
	
def envHasValue(env,value):
	strArg(env,'envHasValue')
	strArg(value,'envHasValue')
	return EnvHasValue(env,value)
	
def envHasValueTemp(env,value):
	strArg(env,'envHasValueTemp')
	strArg(value,'envHasValueTemp')
	return EnvHasValue(env,value)

def setenvShell(env,command):
	strArg(env,'setenvShell')
	strArg(command,'setenvShell')
	return SetenvShell(env,command)
	
def setenvShellTemp(env,command):
	strArg(env,'setenvShellTemp')
	strArg(command,'setenvShellTemp')
	return SetenvShellTemp(env,command)

#
#def alias(aliasFrom,aliasTo):
#	strArg(aliasFrom,'alias')
#	strArg(aliasTo,  'alias')
#	return Alias(aliasFrom,aliasTo)

def exists(filename):
	strArg(filename,'exists')
	return FileExists(filename)
	
def askUntilFileExists(path):
	strArg(path,'askUntilFileExists')
	return AskUntilFileExists(path)
	
def watch(path):
	strArg(path,'exists')
	return Watch.Watch(path)
	
def inpath(filename):
	strArg(filename,'inpath')
	return InPath(filename)
	
def which(filename):
	strArg(filename,'which')
	return Which(filename)

def rpm(filename):
	strArg(filename,'rpm')
	return RPM(filename)

def packageName(name):
	strArg(name,'packageName')
	name2 = deWhiten(string.strip(name))
	return PackageName(name2)
	
def packageDirectory(name):
	strArg(name,'packageDirectory')
	name2 = deWhiten(string.strip(name))
	return PackageDirectory(name2)
	
def mkdir(path):
	strArg(path,'mkdir')
	return Directory(path)
	
def mkdirPersistent(path):
	strArg(path,'mkdirPersistent')
	return MkDirPersistent(path)
	
def platform(plat):
	strArg(plat,'platform')
	return Platform(plat)
	
def platformLE(plat):
	strArg(plat,'platformLE')
	return PlatformLE(plat)
	
def platformLT(plat):
	strArg(plat,'platformLT')
	return PlatformLT(plat)
	
def platformGE(plat):
	strArg(plat,'platformGE')
	return PlatformGE(plat)
	
def platformGT(plat):
	strArg(plat,'platformGT')
	return PlatformGT(plat)
	
def message(line):
	strArg(line,'message')
	return Message(line)
	
def fail(line):
	strArg(line,'fail')
	return Fail(line)
	
def echo(line): return message(line)

def username(uname):
	strArg(uname,'username')
	return Username(uname)
	
def userExists(uname,ugroup='- any -'):
	strArg(uname,'userExists'); strArg(ugroup,'userExists')
	return UserExists(uname,ugroup)
	
def userAdd(uname,group='- any -',shell='/bin/sh',homedir=''):
	strArg(uname,  'userAdd')
	strArg(group,  'userAdd')
	strArg(shell,  'userAdd')
	strArg(homedir,'userAdd')
	return UserAdd(uname,group,shell,homedir)
	
def groupExists(gname):
	strArg(gname,'groupExists')
	return GroupExists(gname)
	
def groupAdd(gname):
	strArg(gname,'groupAdd')
	return GroupAdd(gname)
	
def url(name,urlval='',target='_blank'):
	strArg(name,'url'); strArg(urlval,'url'); strArg(target,'url')
	if urlval=='': return URL(name,name,target)
	else:          return URL(name,urlval,target)
	
def author(name,email):
	strArg(name,'author'); strArg(email,'author')
	return Author(name,email)
	
def contact(name,email):
	strArg(name,'contact'); strArg(email,'contact')
	return Contact(name,email)
	
def updateUrl(url):
	strArg(url,'updateUrl')
	return UpdateURL(url)
	
def urlVisible(url):
	strArg(url,'urlVisible')
	return URLvisible(url)
	
def pythonScript(path):
	strArg(path,'pythonScript')
	return PythonScript(path)

def shell(command):
	strArg(command,'shell')
	return ShellCommand(command)
	
def shellDialogue(command):
	strArg(command,'shellDialogue')
	sh = ShellDialogue(command)
	sh.mode = 'compatibility'
	return sh
	
def shellOutputContains(command,contains):
	strArg(command,'shellOutputContains')
	strArg(contains,'shellOutputContains')
	return ShellOutputContains(command,contains)
	
def shellOutputLE(command,text):
	strArg(command,'shellOutputLE')
	strArg(text,   'shellOutputLE')
	return ShellOutputLE(command,text)
	
def shellOutputLT(command,text):
	strArg(command,'shellOutputLT')
	strArg(text,   'shellOutputLT')
	return ShellOutputLT(command,text)
	
def shellOutputEQ(command,text):
	strArg(command,'shellOutputEQ')
	strArg(text,   'shellOutputEQ')
	return ShellOutputEQ(command,text)
	
def shellOutputGE(command,text):
	strArg(command,'shellOutputGE')
	strArg(text,   'shellOutputGE')
	return ShellOutputGE(command,text)
	
def shellOutputGT(command,text):
	strArg(command,'shellOutputGT')
	strArg(text,   'shellOutputGT')
	return ShellOutputGT(command,text)
	
def uninstallShell(command):
	strArg(command,'uinstallShell')
	return UninstallShellCommand(command)
	
def yes(question):
	strArg(question,'answerYes')
	return Choice('y',question,'y','n')
	
def no(question):
	strArg(question,'answerNo')
	return Choice('n',question,'y','n')
	
def choice(answer,question,c1,c2,c3='',c4='',c5='',c6='',c7='',c8='',c9='',c10=''):
	strArg(answer,'choice')
	strArg(question,'choice')
	strArg(c1,'choice')
	strArg(c2,'choice')
	strArg(c3,'choice')
	strArg(c4,'choice')
	strArg(c5,'choice')
	strArg(c6,'choice')
	strArg(c7,'choice')
	strArg(c8,'choice')
	strArg(c9,'choice')
	strArg(c10,'choice')
	if   c10!='': return Choice(answer,question,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10)
	elif  c9!='': return Choice(answer,question,c1,c2,c3,c4,c5,c6,c7,c8,c9)
	elif  c8!='': return Choice(answer,question,c1,c2,c3,c4,c5,c6,c7,c8)
	elif  c7!='': return Choice(answer,question,c1,c2,c3,c4,c5,c6,c7)
	elif  c6!='': return Choice(answer,question,c1,c2,c3,c4,c5,c6)
	elif  c5!='': return Choice(answer,question,c1,c2,c3,c4,c5)
	elif  c4!='': return Choice(answer,question,c1,c2,c3,c4)
	elif  c3!='': return Choice(answer,question,c1,c2,c3)
	else:         return Choice(answer,question,c1,c2)
	
def description(text,url=''):
	strArg(text,'description'); strArg(url,'description')
	if isURL(url): return AND(Description(text),URLbare(url))
	else:          return Description(text)
	
def package(specstring,location=''):
	strArg(specstring,'package')
	strArg(  location,'package')
	return Package.LazyPackage(Package.Spec(specstring,location))

def configure(specstring,location=''):
	strArg(specstring,'configure')
	strArg(  location,'configure')
	p = Package.LazyPackage(Package.Spec(specstring,location))
	p._modified = 1
	return p

def rpmInstalled(rpm): return RPMinstalled(rpm)
	
def freeMegsMinimum(freemin,path=''):
	if path=='': path2 = '.'
	else:        path2 = path
	strArg(path2,'freeMegsMinimum')
	if not type(freemin) is IntType: abort('Type error in argument to freeMegsMinimum.')
	return FreeMegs(freemin,path2)
	
def freeMegs(path=''):
	if path=='': path2 = '.'
	else:        path2 = path
	strArg(path2,'freeMegs')
	return FreeDiskMegs(path2)
	
def freeDisk(freemegs,path=''): return freeMegsMinimum(freemegs,path)
#	
#def freeDisk(freemegs,path='.'):
#	if not type(freemegs) is IntType: abort('Type error in argument to freeDisk.')
#	return FreeMegsMinimum(freemegs,path)
	
def copy(copyFrom,copyTo):
	strArg(copyFrom,'copy'); strArg(copyTo,'copy')
	return Copy(copyFrom,copyTo)
	
def cp(copyFrom,copyTo): return copy(copyFrom,copyTo)

def copyReplace(copyFrom,copyTo,matchstring,replacestring):
	strArg (copyFrom,       'copyReplace')
	strArg (copyTo,         'copyReplace')
	strArg (matchstring,    'copyReplace')
	strArg (replacestring,  'copyReplace')
	return CopyAndReplace(copyFrom,copyTo,matchstring,replacestring)

def cd(path='-'):
	strArg(path,'cd')
	return CD(path)

def cu(userfile='-pop-'):
	strArg(userfile,'cu')
	return CU(userfile)
#	
#def remoteSite(packagestring,host,location=cwdd(),username=getusername(),sh='sh'):
#	S = Site(Computer(host,location,username,sh))
#	p = Package.Package(packagestring)
#	return PackageSite(p,S)
#	
def locate(packagestring,location):
	strArg(packagestring,'locate'); strArg(location,'locate')
	p = Package.Package(packagestring)
	
	en = AND()
	en.extend(                 cd(location)                                 )
	en.extend(           Location(location)                                 )
	en.extend(             setenv( 'PAC_'+str2file(location),'$PAC_ANCHOR') )
	en.extend(         setenvTemp('PAC_ANCHOR','$PWD')                      )
	en.extend(    Package.Package(packagestring)         )
	en.extend(         setenvTemp('PAC_ANCHOR','$PAC_'+str2file(location))  )
	en.extend(                 cd()                                         )
	
	return en
	
def writeProtect(path):
	strArg(path,'writeProtect')
	return WriteProtect(path)
	
def ls(path=os.getcwd()):
	strArg(path,'ls')
	return LS(path)

def cwd(path=''): 
	strArg(path,'cwdCheck')
	if path=='': return CWD()
	else:        return CWDCheck(path)

def softLink(linkFrom,linkTo):
	strArg(linkFrom,'softLink'); strArg(linkTo,'softLink')
	return SoftLink(linkFrom,linkTo)

def textFile(filename,lines,trans=0):
	return TextFile(filename,lines,trans)

def download(url):
	strArg(url,'download')
	return Download(url)
	
def downloaduntarzipwrap(url,env):
	if tail(url,'.tar.gz') or tail(url,'.tgz') or tail(url,'.tar.Z') or tail(url,'.tar.z') or tail(url,'.tar'):
		D = DownloadUntarzip(url,env)
	else:
		D = Download(url)
	return D

def downloadUntar(url,env=''):
	strArg(url,'downloadUntar')
	strArg(env,'downloadUntar')
	return downloaduntarzipwrap(url,env)
	
def downloadUntarZip(url,env=''):
	return downloadUntarzip(url,env)
	
def downloadUntarzip(url,env=''):
	strArg(url,'downloadUntarzip')
	strArg(env,'downloadUntarzip')
	return downloaduntarzipwrap(url,env)
#	return DownloadUntarzip(url,env)

#	head,tail = os.path.split(url)
#	d1 = AND(FileExistsOnce(os.path.join('../downloads',tail)),MV(os.path.join('../downloads',tail),tail))
#	return OR(d1,Download(url))

def chown(path,username=getusername()):
	strArg(path,'chown'); strArg(username,'chown')
	return Chown(path,username)
	
def path(val,env='PATH',mode='front'): 
	strArg(val,'path')
	strArg(env,'path')
	strArg(mode,'path')
	return Path(val,env,mode)

def chownR(directory,username=getusername()):
	strArg(directory,'chownR'); strArg(username,'chownR')
	return ChownR(directory,username)

def runningProcess(processname):
	strArg(processname,'runningProcess')
	return RunningProcess(processname)

def tcpPorts(host,rangeStart,rangeEnd):
	strArg(host,'tcpPorts')
	argchk(rangeStart,IntType,'tcpPorts')
	argchk(rangeEnd  ,IntType,'tcpPorts')
	return TCPPorts(rangeStart,rangeEnd,host)
	
def udpPorts(host,rangeStart,rangeEnd=0):
	strArg(host,'udpPorts')
	argchk(rangeStart,IntType,'tcpPorts')
	argchk(rangeEnd,  IntType,'tcpPorts')
	return UDPPorts(rangeStart,rangeEnd,host)
	
def usePort(port):
	argchk(port,IntType,'usePort')
	return UsePortNumber(port)
	
def chooseDirectory(enviroName,directory):
	strArg(enviroName,'chooseDirectory')
	strArg(directory,'chooseDirectory')
	return DirectoryChoice(enviroName,directory)

def installerChosenWorkSpace(enviroName,minmegs=0,subdirectory='workspace',owner=getusername(),worldwrite=0):
	strArg(enviroName,'installerChosenWorkSpace')
	strArg(subdirectory,'installerChosenWorkSpace')
	strArg(owner,'installerChosenWorkSpace')
	argchk(minmegs,IntType,'installerChosenWorkSpace')
	argchk(worldwrite,IntType,'installerChosenWorkSpace')

	ens = AND()
	ens.append(DirectoryChoice(enviroName,subdirectory))
	ens.append(mkdir('$'+enviroName))
	if not owner==getusername(): ens.append(Chown('$'+enviroName,owner))
	ens.append(FreeMegs(minmegs,'$'+enviroName))
	ens.append(FreeDiskMegs('$'+enviroName))
	
	return ens

def  true(): return True ()
def false(): return False()
	
def setup(command):
	strArg(command,'setup')
	return Setup(command)

def untar(tarfile,env=''):
	strArg(tarfile,'untar')
	strArg(env,'untar')
	return Untarzip(tarfile,env)
#
#def untar(tarfile): 
#	strArg(tarfile,'untar')
#	return AND(Untarzip(tarfile),TarballRoot(tarfile))
#
#def untarzip(tarzipfile): 
#	return AND(Untarzip(tarzipfile),TarballRoot(tarzipfile))
#
def untarzip(tarzipfile,env=''):
	strArg(tarzipfile,'untarzip')
	strArg(env,'untarzip')
	return Untarzip(tarzipfile,env)

#
#def tarballRoot(tarfile,path='',logfile=''):
#	strArg(tarfile,'tarZipRoot'); strArg(path,'tarZipRoot'); strArg(logfile,'tarZipRoot')
#	return TarballRoot(tarfile,path,logfile)
#	
def tarZipRoot(tarfile,path='',logfile=''):
	strArg(tarfile,'tarZipRoot'); strArg(path,'tarZipRoot'); strArg(logfile,'tarZipRoot')
	return TarballRoot(tarfile,path,logfile)
	
	
