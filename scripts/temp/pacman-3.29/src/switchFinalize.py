#
#  -- switch Finalize
#
#  -- a hack to get the switches to save their information in the case where
#  no pacman installation exists on the first command
#
from Base import *
import os
import Untarzip

def switchFinalize():
	verbo.save()
	debug.save()
	browser.save()
	allow.save()
	upOptions.save()
#	domainMode.save()
	displayMode.save()
	ask.save()
	allow.save()
	
	# Save the pretend-platform to a file
	pre,plat = switchpar('pretend-platform')
	if not pre and len(switchItems('pretend-platform'))>0:
		pre,plat = 1,switchItems('pretend-platform')[0]
	if pre:
		ppl = os.path.join(pac_anchor,pacmanDir,'ppl')
		try:
			removeFile(ppl)
			f = open(ppl,'w')
			f.write(string.strip(plat)+'\n')
			f.close()
		except:
			print "WARNING: Can't write to ["+ppl+"]..."

        # pretend-arch was added by Scot Kronenfeld 2/2009
        # Save the pretend-arch to a file
	pre,arch = switchpar('pretend-arch')
	if not pre and len(switchItems('pretend-arch'))>0:
		pre,arch = 1,switchItems('pretend-arch')[0]
	if pre:
		parch = os.path.join(pac_anchor,pacmanDir,'parch')
		try:
			removeFile(parch)
			f = open(parch,'w')
			f.write(string.strip(arch)+'\n')
			f.close()
		except:
			print "WARNING: Can't write to ["+parch+"]..."

	Untarzip._tarSave.save()
	
	if switch('debug'): removeFile(os.path.join(pac_anchor,pacmanDir,'lock'))
	
	if switch('bell'): print '\a'
