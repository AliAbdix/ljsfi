#
#  sets up the python path to use Pacman
#
import sys,os

if os.environ.has_key('PACMAN_LOCATION'):
	top = os.environ['PACMAN_LOCATION']
else:
	print 'Pacman not setup.  See README.'
	sys.exit(1)
	
dirs = ['access','caches','compiler','change','package',
                      'environment/compatibility',
	              'environment/shell',
		      'environment/system',
		      'environment/base',
		      'environment/text',
	'installation','site','base','web','change']

if 1 or '-st' in sys.argv:
	sys.path.insert(1,os.path.join(top,'st'))
	for d in dirs: 
		path = os.path.join(top,os.path.join(top,'st',d))
		if not path in sys.path:
			sys.path.insert(1,path)
else:
	sys.path.insert(1,os.path.join(top,'st' ))
	sys.path.insert(1,os.path.join(top,'src'))

#import pythonVersionCheck
#pythonVersionCheck.pythonVersionCheck()

def src():
	print os.getcwd()
	if os.path.exists(os.path.join(top,'src')): os.system('rm -r -f $PACMAN_LOCATION/tmp; mv $PACMAN_LOCATION/src $PACMAN_LOCATION/tmp')
	os.system('mkdir $PACMAN_LOCATION/src')
	os.system('cp $PACMAN_LOCATION/st/path.py $PACMAN_LOCATION/src')
	os.system('cp $PACMAN_LOCATION/st/pacman $PACMAN_LOCATION/src')
	for d in dirs: 
		os.system('cp $PACMAN_LOCATION/st/'+d+'/*.py $PACMAN_LOCATION/src')

