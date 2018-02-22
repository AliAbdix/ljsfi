"""
A Cupboard is basically a direct product of dictionaries
"""

import Basics
import os,cPickle

class BigDictionaryError(Basics.Eggception): pass

class BigDictionary(object):
	def __init__(self,maxAll=None,maxOne=None): raise BigDictionaryError('Not implemented.')
	def __setitem__  (self,key,value): raise BigDictionaryError('Not implemented.')
	def __len__      (self          ): raise BigDictionaryError('Not implemented.')
	def __getitem__  (self,i        ): raise BigDictionaryError('Not implemented.')
	def __setitem__  (self,key,value): raise BigDictionaryError('Not implemented.')
	def has_key      (self,key      ): raise BigDictionaryError('Not implemented.')
	def keys         (self          ): raise BigDictionaryError('Not implemented.')
	def __contains__ (self,value    ): return Basics.exists(self,lambda v: v==value)

	def full  (self     ): raise BigDictionaryError('Not implemented')
	def maxOne(self     ): raise BigDictionaryError('Not implemented')
	def size  (self     ): raise BigDictionaryError('Not implemented')
	def read  (self,path): raise BigDictionaryError('Not implemented')
	def write (self,path): raise BigDictionaryError('Not implemented')
	
class BigDirDictionary(BigDictionary):
	def __init__(self,path,maxAll=None,maxOne=None):
		self._maxOne = maxOne
		self._maxAll = maxAll
		self._size   = 0
		self._keys   = {}
		self._path   = os.path.abspath(path)
		if os.path.isdir(self._path): self.read (self._path)
		else:                         self.write(self._path)
			
	def __del__(self):
		self.write(self._path)
		BigDictionary.__del__(self)
						
	def _keyhash(self,key): return `abs(key.__hash__())`
	
	def read(self,path):
		if os.path.isdir(path) and os.path.exists(os.path.join(path,'bdd')):
			self._path  = os.path.abspath(path)
			try:
				f = open(os.path.join(self._path,'bdd'),'r')
				self = cPickle.load(f)
				f.close()
			except:
				raise BigDictionaryError("Can't read ["+self._path+"].")
		else:
			raise BigDictionaryError("["+path+"] does not contain a BigDirDictionary.")
	
	def write(self,path):
		if os.path.exists(path):
			raise BigDictionaryError("File ["+path+"] already exists. Can't write BigDirDictionary.")
		else:
			try:
				os.system('mkdir '+path)
				f = open(os.path.join(path,'keys'),'w')
				cPickle.dump(f,self)
				f.close()
			except:
				 raise BigDictionaryError("Can't write to ["+path+"].")

class BigMemDictionary(dict,BigDictionary):
	def __init__(self,maxAll=None,maxOne=None):
		dict.__init__(self)
		self._maxOne = maxOne
		self._maxAll = maxAll
		self._size   = 0
		
	def __setitem__(self,key,value):
		if not self._maxOne==None and len(value)>self._maxOne:
			raise DictionaryError('Length '+`len(value)`+' of ['+value[:10]+'...] is too large for Dictionary.')
		elif not self._maxAll==None and self._size>self._maxAll:
			raise DictionaryError('Dictionary sized ['+self._size+'] is full.')
		else:
			dict.__setitem__(self,key,value)
			self._size = self._size + len(value)
			
	def full  (self): return self._maxAll!=None and self._size>self._maxAll
	def maxOne(self): return self._maxOne
	def size  (self): return self._size
	
	def write (self,path):
		try:
			f = open(path,'w')
			p = cPickle.dump(self,f)
			f.close()
		except KeyError:
			Basics.remPath(path)
			raise
		except:
			raise BigDictionaryError('Error writing BigDictionary to ['+path+'].')

	def read  (self,path):
		try:
			f = open(path,'r')
			d = cPickle.load(f)
			f.close()
		except KeyError:
			raise
		except:
			raise BigDictionaryError('Error reading BigDictionary from ['+path+'].')


#class SumDictionary(object):
#	def __init__(self,*ds):
#		self._ds = ds
#
#	def has_key(self,key): return exists(self,lambda d: d.has_key(key))
#	
#	def put(self,key,x):
#		got_one = 0
#		for d in self._ds:
#			if not d.full(): 
#				d[key] = x
#				got_one = 1
#		if not got_one: raise CubboardError('Cupboard ['+`self`+'] is full.')
		

