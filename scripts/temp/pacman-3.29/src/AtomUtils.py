#
#	Copyright Saul Youssef, July 2003
#
import os,string
from types import *
from Base  import *

newAttributes = ['setenv','exists','inpath','which','packageName', \
                 'mkdir','mkdirPersistent','username',\
		 'platform','platformLE','platformLT','platformGE','platformGT',\
		 'url','urlVisible','updateUrl','cat',\
		 'shell','shellDialogue','shellOutputContains','shellOutputLE','shellOutputEQ','shellOutputGE',\
		 'shellOutputLT','shellOutputGT',\
		 'uninstallShell','pythonScript',\
		 'workspace','fail','alreadyInstalled',\
		 'setenvTemp','unsetenv','envIsSet','envHasValue',\
		 'userExists','userAdd','author','contact',\
		 'alias','softLink','workspace','restore',\
		 'groupExists','groupAdd','ownedBy',\
		 'timeErrorMaximum','textFileContainsText','grep',\
		 'cpuSecondsSoft','cpuSecondsHard','cpuSeconds',\
		 'fileSizeSoft','fileSizeHard','fileSize',\
		 'heapSize','stackSize','imageSize',\
		 'openFileDescriptorsSoft','openFileDescriptorsHard','openFileDescriptors',\
		 'remoteInstallation','description',\
		 'freeMegsMinimum','freeMegs','copy','cp','copyReplace','ls','cu',\
		 'cd','download','downloadUntar','downloadUntarzip','downloadUntarZip','cwd','locate',\
		 'export','package','packageDirectory','watch',\
		 'yes','no','choice','insertLine','freeDisk',\
		 'md5check',\
		 'message','echo','mail',\
		 'remoteSite','remotePackage','remoteGroup',\
		 'monitorRemotePackage',\
		 'tarballRoot','tarZipRoot','rpm','rpmInstalled',\
		 'askUntilFileExists',\
		 'path','textFile','sshAccess','globusAccess',\
		 'hasSshAccess','hasGlobusAccess',\
		 'chown','chownR','runningProcess','tcpPorts','udpPorts',\
		 'untar','untarzip','writeProtect',\
                  # Added by Scot Kronenfeld 2/2009
                 'packageRevision',\
		 'version','versionLE','versionGE','versionLT','versionGT',\
		 'release','releaseLE','releaseGE','releaseLT','releaseGT',\
		 'patch','patchLE','patchGE','patchLT','patchGT',\
		 'option','optionLE','optionGE','optionLT','optionGT',\
		 'versionTuple','versionTupleLE','versionTupleGE','versionTupleLT','versionTupleGT',\
		 'gccBinary','gccBinaryLE','gccBinaryGE','gccBinaryGT','gccBinaryLT',\
		 'systemRelease','systemReleaseLE','systemReleaseGE','systemReleaseGT','systemReleaseLT',\
		 'systemVersion','systemVersionLE','systemVersionGE','systemVersionGT','systemVersionLT',\
		 'byteOrder','systemWordSize','processor','systemVersion',\
		 'tag','tagLE','tagGE','tagLT','tagGT',\
		 'gccVersion','gccVersionLE','gccVersionLT','gccVersionGE','gccVersionGT',\
		 'glibcVersion','glibcVersionLE','glibcVersionLT','glibcVersionGE','glibcVersionGT',\
		 'pythonVersion','pythonVersionLE','pythonVersionLT','pythonVersionGE','pythonVersionGT',\
		 'sshVersion','sshVersionLE','sshVersionLT','sshVersionGE','sshVersionGT',\
		 'perlVersion','perlVersionLE','perlVersionLT','perlVersionGE','perlVersionGT',\
		 'pacmanVersion','pacmanVersionLE','pacmanVersionLT','pacmanVersionGE','pacmanVersionGT',\
		 'linuxKernel','linuxKernelLE','linuxKernelLT','linuxKernelGE','linuxKernelGT',\
		 'true','false','packageName','setup',\
		 'setenvShell','setenvShellTemp',\
		 'env','installerChosenWorkSpace','directUntarzip',\
		 'worldRead','worldWrite','worldExecute',\
		 'groupRead','groupWrite','groupExecute',\
		 'ownerRead','ownerWrite','ownerExecute',\
		 'worldReadable','worldWriteable','worldExecutable',\
		 'groupReadable','groupWriteable','groupExecutable',\
		 'ownerReadable','ownerWriteable','ownerExecutable',\
		 'register','alreadyInstalled','launchWebBrowser',\
		 'fileCopyMinimumMegsPerSecond','downloadTime',\
		 'commandLineSwitch','emptyDirectory','directoryContains',\
		 'configure','commandLineSwitch',\
		 'isWorldRead','isWorldWrite','isWorldExecute',\
		 'isGroupRead','isGroupWrite','isGroupExecute',\
		 'isOwnerRead','isOwnerWrite','isOwnerExecute',\
		 'isWorldRead','isWorldWrite','isWorldExecute',\
		 'isGroupRead','isGroupWrite','isGroupExecute',\
		 'isOwnerReadable','isOwnerWriteable','isOwnerExecuteable',\
		                   'isOwnerWritable','isOwnerExecutable',\
		 'isWorldReadable','isWorldWriteable','isWorldExecuteable',\
		                   'isWorldWritable','isWorldExecutable',\
		 'isGroupReadable','isGroupWriteable','isGroupExecuteable',\
		                   'isGroupWritable','isGroupExecutable',\
		 'isOwnerReadable','isOwnerWriteable','isOwnerExecuteable',\
		                   'isOwnerWritable','isOwnerExecutable',\
		 'isWorldReadable','isWorldWriteable','isWorldExecuteable',\
		                   'isWorldWritable','isWorldExecutable',\
		 'isGroupReadable','isGroupWriteable','isGroupExecuteable',\
		                   'isGroupWritable','isGroupExecutable',\
		 'isOwnerReadable','isOwnerWriteable','isOwnerExecuteable',\
		                   'isOwnerWritable','isOwnerExecutable',\
		 'setWorldRead','setWorldWrite','setWorldExecute',\
		 'setGroupRead','setGroupWrite','setGroupExecute',\
		 'setOwnerRead','setOwnerWrite','setOwnerExecute',\
		 'setWorldRead','setWorldWrite','setWorldExecute',\
		 'setGroupRead','setGroupWrite','setGroupExecute',\
		 'setOwnerRead','setOwnerWrite','setOwnerExecute',\
		 'setWorldReadable','setWorldWriteable','setWorldExecuteable',\
		                    'setWorldWritable','setWorldExecutable',\
		 'setGroupReadable','setGroupWriteable','setGroupExecuteable',\
		                    'setGroupWritable','setGroupExecutable',\
		 'setOwnerReadable','setOwnerWriteable','setOwnerExecuteable',\
		                    'setOwnerWritable','setOwnerExecutable',\
		 'setWorldReadable','setWorldWriteable','setWorldExecuteable',\
		                    'setWorldWritable','setWorldExecutable',\
		 'setGroupReadable','setGroupWriteable','setGroupExecuteable',\
		                    'setGroupWritable','setGroupExecutable',\
		 'setOwnerReadable','setOwnerWriteable','setOwnerExecuteable',\
		                    'setOwnerWritable','setOwnerExecutable',\
		 'absPath','usePort',\
		 'directUntar','chooseDirectory']

def abcommand(c):
	if len(c)>2:
		if c[0]=='|' and c[-1]=='|': return  1,c[1:-1]
		else:			     return  0,c
	else:
		return 0,c

def newAttributeText(line):
	x = string.strip(line)
	if '(' in x and ')' in x:
		if string.strip(x[0:string.index(x,'(')]) in newAttributes:
			return 1
	return 0

def strArg(a,name): argchk(a,StringType,name)
def intArg(a,name): argchk(a,IntType,name)
		
def argchk(a,typeval,name):
	if not type(a) is typeval:
		abort('Wrong argument type ['+`a`+'] to '+name+'.')	
	
def syntaxOK(line):
	if newAttributeText(line): return 1
	try: 
		exec line
		ok = 1
	except:
		ok = 0
	return ok	
	
def strOK(x): return type(x) is StringType
def intOK(x): return type(x) is IntType
def envirosOK(e):
	if not type(e) is ListType: return 0
	for x in e:
		if not type(x) is ListType: return 0
		if not len(x)==2: return 0
		for y in x:
			if not type(y) is StringType: return 0
	return 1
def downloadOK(d):
	if not type(d) is DictionaryType: return 0
	for a,b in d.items():
		if not type(a) is StringType: return 0
		if not type(b) is StringType: return 0
	return 1
def installOK(x): 
	if not type(x) is DictionaryType: return 0
	for a,b in x.items():
		if not type(a) is StringType: return 0
		if not type(b) is ListType: return 0
		for bb in b: 
			if not type(bb) is StringType: return 0
	return 1
def systemsOK(x):
	if not type(x) is DictionaryType: return 0
	for a,b in x.items():
		if not type(a) is StringType: return 0
		if not type(b) is ListType: return 0
		if not len(b)==2: return 0
		for bb in b: 
			if not type(bb) is StringType: return 0
	return 1
def installationOK(x):
	if not type(x) is ListType: return 0
	if len(x)>4: return 0
	for xx in x: 
		if not type(xx) is StringType: 
			return 0
	return 1
def dependsOK(x):
	if not type(x) is ListType: return 0
	for xx in x: 
		if not type(xx) is StringType: return 0
	return 1
def nativelyInstalledOK(x): 
	if not type(x) is DictionaryType: return 0
	for a,b in x.items():
		if not type(a) is StringType:  return 0
		if not type(b) is ListType:    return 0
		for bb in b:
			if not type(bb) is StringType: return 0
		if a=='inpath' or a=='enviros' or a=='scripts' or a=='commands' or a=='rpms': pass
		else: return 0
	return 1

