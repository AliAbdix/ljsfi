#
#  Copyright by Saul Youssef, 2003
#
import sys,os
from Environment           import *
from Source                import *
from Base                  import *


def spath(path):
	if tail(path,'.pacman'): return path
	else:                    return path+'.pacman'
	
def epath(path):
	if tail(path,'.e'):   return path
	else:                 return path+'.e'
	
def compiler():
	cwd = os.getcwd()
	if len(params)==0: abort('Use [% pac {switches} <pacfile1> <pacfile2>...].')

	for path in params:
		if switch('display') or switch('d'):
			if not os.path.exists(epath(path)): abort("File ["+epath(path)+"] doesn't exist.")

			E = get(epath(path))
			E.display()
		elif switch('satisfied'):
			if not os.path.exists(epath(path)): abort("File ["+epath(path)+"] doesn't exist.")

			E = get(epath(path))
			print E.satisfied()
		elif switch('satisfiable'):	
			if not os.path.exists(epath(path)): abort("File ["+epath(path)+"] doesn't exist.")

			E = get(epath(path))
			print E.satisfiable()
		elif switch('satisfy'):
			if not os.path.exists(epath(path)): abort('File ['+epath(path)+'] does not exist.')

			E = get(epath(path))
			print E.satisfy()
			os.chdir(cwd)
			E.put(epath(path))
		elif switch('r') or switch('restore'):
			if not os.path.exists(epath(path)): abort("File ["+epath(path)+"] doesn't exist.")

			E = get(epath(path))
			print E.restore()
			os.chdir(cwd)
			E.put(epath(path))
		elif not (switch('display') or switch('d')):
			try:
				f = open(spath(path),'r'); source = f.readlines(); f.close()
			except (IOError,OSError):
				abort('Error reading from file ['+spath(path)+'].')
	
			if verbose: print 'Compiling ['+spath(path)+']...'
			E = SourceFile(source).evaluate()
			if not switch('c'): print E.satisfy()
			os.chdir(cwd)
			E.put(prefix(path)+'.e')

