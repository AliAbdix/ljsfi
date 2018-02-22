#
#	Database
#
from Base         import *
from Environment  import *
#import shelve

class DB(Environment):
	type   = 'database'
	action = 'database'
	title  = 'Database'
	
	def __init__(self,filename): 
		self._filename = filename
		
	def equal(self,x): return self._filename == x._filename
	def str(self): return self._filename
	
	def satisfied(self):
		return Reason('Data base ['+`self`+'] does not exist.',not os.path.exists(fullpath(self._filename)))
	def satisfiable(self): return Reason()
	
	def acquire(self):
		reason = Reason()
		self._filename = fullpath(self._filename)
		abort('error')
		try:
#			db = shelve.open(self._filename)
			db.close()
		except (IOError,OSError):
			reason = Reason("Can't write ["+self._filename+"].")
		return reason
		
	def retract(self):
		removeFile(self._filename)
		return Reason()

class Dict(DB):
	type   = 'dictionary'
	action = 'dictionary'
	title  = 'Dictionary'
		
	def acquire(self):
		reason = Reason()
		self._filename = fullpath(self._filename)
		try:
			d = {}
			f = open(self._filename,'w')
			cPickle.dump(d,f)
			f.close()
		except (IOError,OSError):
			reason = Reason("Error writing ["+self._filename+"].")
		return reason

		
