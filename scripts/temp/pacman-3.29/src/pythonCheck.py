#
#	Copyright, Saul Youssef, Jan. 2004
#
import sys

def pythonCheck(): 
	if not '-ignore-python-version' in sys.argv:
		minversion = [2,2,0]
		if not 'version_info' in dir(sys):
			print 'You are using Python version ['+sys.version+'].'
			print 'Pacman needs Python 2.2.0 or greater.'
			sys.exit(1)
		else:
			t = sys.version_info
			pt =          t[0]*100 +          t[1]*10 +          t[2]*1
			pm = minversion[0]*100 + minversion[1]*10 + minversion[2]*1
			if pm>pt: 
				print 'You are using Python version ['+sys.version+'].'
				print 'Pacman needs Python 2.2.0 or greater.'
				sys.exit(1)
			if sys.version_info[0] >= 3:
				print 'Pacman is not available with Python 3.0'
				sys.exit(1)

#
#  This section makes sure that Python's anydbm module (used by shelve) does not
#  use gdbm as it's default database if possible.
#
import anydbm
defaultdb = ''
for _name in anydbm._names:
	if not _name=='dumbdbm' and not _name=='gdbm' and not _name=='dbm':
		try:
			_mod = __import__(_name)
			anydbm._defaultmod = _mod
			defaultdb = _name
		except ImportError:
			continue
	if not defaultdb=='': break
