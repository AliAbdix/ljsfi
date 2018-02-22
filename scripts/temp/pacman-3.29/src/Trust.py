#
#    Takes care of the trusted.caches file
#
from Base import *
import Registry
import string,os

import Basics

yn = Basics.Yesno()

class Trust:
	def __init__(self,trustfile='trusted.caches'):
		self._trustfile = fullpath(trustfile)
		self._trusted = {os.getcwd():''}
		if not os.path.exists('trusted.caches'):
			f = open('trusted.caches','w')
			f.write('#\n')
			f.write('#  Trusted Caches. \n')
			f.write('#\n')
			f.close()
		try:
			f = open(self._trustfile,'r')
			lines = f.readlines()
			f.close()
			for line in lines:
				if len(line)>0 and not line[0]=='#':
					cache = string.strip(line[:-1])
					self._trusted[cache] = ''
		except (IOError,OSError):
			abort("Error reading ["+self._trustfile+"].")
			
	def trusted(self,cache):
		if self._trusted.has_key(cache): 
			ok = 1
		else:
			keys = self._trusted.keys()
			ok = exists(keys,lambda key: Registry.registry.equiv(key,cache))
			if ok: self._trusted[cache] = ''
		return ok
		
	def add(self,cache,autotrust=0):
		r = Reason()
		if not cache=='trusted.caches' and not self.trusted(cache):
			if autotrust or switch('trust-all-caches') or allow('trust-all-caches') or yn('Do you want to add ['+cache+'] to [trusted.caches]?'):
				try:
					f = open(self._trustfile,'a')
					f.write(cache+'\n')
					f.close()
				except (IOError,OSError):
					r = Reason('Error writing to [trusted.caches] file.')
				self._trusted[cache] = ''
			else:
				r = Reason('Permission to trust cache ['+cache+'] has been declined.')
		return r

trust = Trust()

