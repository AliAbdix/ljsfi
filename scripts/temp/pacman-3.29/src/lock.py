#
#
#
from Base import *
import os

def lock():
	path = os.path.join(pac_anchor,pacmanDir,'lock')
	if os.path.exists(path):
		try:
			f = open(path,'r')
			lines = f.readlines()
			f.close()
		except (IOError,OSError):
			print 'Error reading Pacman directory area.'
			sys.exit(1)
		if len(lines)>0 and len(lines[0])>1:
			print 'Installation ['+pac_anchor+'] is currently locked by ['+lines[0][:-1]+"]."
			print 'Use [% pacman -clear-lock] to override.'
			sys.exit(1)
		else:
			print 'Error reading Pacman directory area.'
			sys.exit(1)
	elif os.path.isdir(os.path.join(pac_anchor,pacmanDir)):
		try:
			f = open(path,'w')
			f.write(getusername()+'\n')
			f.close()
		except (IOError,OSError):
			print 'Cannot write to ['+os.path.join(pac_anchor,pacmanDir)+'].'
			sys.exit(1)

def unlock():
	path = os.path.join(pac_anchor,pacmanDir,'lock')
	removeFile(path)	
