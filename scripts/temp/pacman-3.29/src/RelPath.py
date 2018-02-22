
from Base import *
import Registry
	
def relPath(path):
	if isURL(path) or not Registry.registry.trans(path)==path:
		rp = 0
	elif isPath(path) and not (front(path,'/') or ('$' in path) or ('~' in path) or ('@' in path)):
		rp = 1
	else:
		rp = 0
	return rp
		
