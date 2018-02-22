#
#	Written by Nick Wang
#
#	Modified by Saul
#
#   - fixed bug noticed by Jason Brechin.  S.Y. Sept. 22, 2005
#
import sys,os
from Platform import *
from Base     import *

class FreeDisk(Exception): 
	def __init__(self): Exception.__init__(self,"can't compute free disk space")

class FreeDiskOSError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return 'Cannot handle the operating system type.'
	
def enoughFreeDisk(minimumDisk,path=pac_anchor):
	r = Reason()
	if localmegs(path)<minimumDisk:
		r = Reason("Out of disk space at ["+path+"].")
	return r

def localmegs(path0):
    free = 999999999
    try:
    	path = fullpath(path0)
    	p = Platform()
    	if sys.platform == 'win32':
        	import win32file
        	sectorsPerCluster, bytesPerSector, numFreeClusters, totalNumClusters = win32file.GetDiskFreeSpace(path)
        	sectorsPerCluster = long(sectorsPerCluster)
        	bytesPerSector    = long(bytesPerSector)
        	numFreeClusters   = long(numFreeClusters)
        	totalNumClusters  = long(totalNumClusters)
		free = (numFreeClusters * sectorsPerCluster * bytesPerSector) / (1024*1024)
    	elif p.satisfies(PlatformGE('Darwin')):
    		pass
    	elif p.satisfies(PlatformGE('cygwin')):
        	import string
        	lines = os.popen('df -m '+path).readlines()
		try:
			free = int(string.split(lines[-1])[3])
		except IndexError:
			abort('Directory ['+path+'] does not exist.')
    	elif p.satisfies(PlatformGE('linux')) or p.satisfies(PlatformGE('sun')):
		if not hasattr(os,'statvfs'): raise FreeDisk()
        	import statvfs
        	nfree_blocks = os.statvfs(path)[statvfs.F_BAVAIL]
        	blocksize    = os.statvfs(path)[statvfs.F_BSIZE]
		free = ((nfree_blocks/1000)*blocksize)/1000
    	else:
		if not hasattr(os,'statvfs'): raise FreeDisk()
        	import statvfs
        	nfree_blocks = os.statvfs(path)[statvfs.F_BAVAIL]
       		blocksize    = os.statvfs(path)[statvfs.F_BSIZE]
		free = ((nfree_blocks/1000)*blocksize)/1000

    except KeyboardInterrupt:
    	raise
    except:
    	pass
    return free
