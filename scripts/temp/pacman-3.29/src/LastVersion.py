#
#	Copyright Saul Youssef, January 2005
#
from Base        import *
#from Environment import *
#import UniversalAccess

def lastVersion():
#	a = UniversalAccess.UniversalAccess('http://physics.bu.edu/pacman/sample_cache/')
#	if a.access():
#		r,lines = a.getLines('Pacman3.pacman')
#	else:
#		r,lines = Reason("Can't access headquarters"),[]
		
	r = Reason('no')
	try:
		import commands
		status = commands.getstatus('wget --tries=1 --timeout=5 --output-document=.pmtmp http://physics.bu.edu/pacman/sample_cache/Pacman3.pacman')
		f = open('.pmtmp','r')
		lines = f.readlines()
		f.close()
		r = Reason()
	except:
		lines = []

	got_one = 0; ver = ''
	if r.ok():
		for line in lines:
			if len(line)>7 and line[:7]=='version':
				if   contains(line,"'"): 
					l = string.split(line,"'")
					if len(l)==3:
						ver = l[1]
						got_one = 1
						break
				elif contains(line,'"'): 
					l = string.split(line,'"')
					if len(l)==3:
						ver = l[1]
						got_one = 1
						break

	return ver
