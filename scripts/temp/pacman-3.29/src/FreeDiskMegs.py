#
#	Copyright Saul Youssef, July, 2003
#
from Environment import *
from freedisk    import *

class FreeDiskMegs(Environment):
	type   = 'freeMegs'
	title  = 'Free Megs of Disk Space'
	action = 'show free disk space'
	
	def __init__(self,path=os.getcwd()):
		self.__path = path[:]
		
	def equal(self,x): return self.__path==x.__path
	def str(self): 
		if os.path.exists(fullpath(self.__path)):
			return `int(localmegs(fullpath(self.__path)))`+' at '+fullpath(self.__path)
		else:
			return self.__path+' does not exist'
	
	def satisfied  (self): return Reason()
	def satisfiable(self): return Reason()
	def satisfies(self,x): return self==x
