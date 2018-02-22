#
#	Copyright Saul Youssef, July 2003
#
from Environment import *
from Base        import *
import time

class StringAttr(Environment):
	type   = 'string attribute'
	action = 'string attribute'
	title  = 'string attribute'
	
	def __init__(self,string): self.value = string
#-- Set
	def equal(self,n):  return self.value == n.value
	def str(self):      return self.value
	def leq(self,x):
		if len(x)<=len(self.value):
			q = self.value<=x[:len(self.value)]
		else:
			q = self.value[:len(x)]<x
		return q
	def eq (self,x): return self.value==x
	def lt (self,x): return self.leq(x) and not self.eq(x)
	def geq(self,x): return not self.leq(x)
			
#-- Satisfied
	def satisfied  (self): return Reason()
	def satisfiable(self): return Reason()
	
#-- SatisfyOrder
	def satisfies(self,x): return self==x
	
class StringEQ(StringAttr):
	type   = 'string equality'
	title  = 'String Equality'
	action = 'compare string'

	def satisfied(self): return Reason(`self`+" hasn't been attempted yet.",not self.acquired)
	def str(self): return 'Test that '+self.type+' ['+self.val()+'] is equal to ['+self.value+'].'
	def val(self): abort('Missing val in StringEqual.')
	def acquire(self):
		return Reason(self.type+' ['+self.val()+'] is not equal to ['+self.value+'].',not self.val()==self.value)
	def retract(self): return Reason()
	
class StringLE(StringAttr):
	type   = 'string LE'
	title  = 'String LE'
	action = 'test string LE'
	
	def satisfied(self): return Reason(`self`+" hasn't been attempted yet.",not self.acquired)
	def str(self): return 'Test that '+self.type+' ['+self.val()+'] is less than or equal to ['+self.value+'].'
	def val(self): abort('Missing val in StringLE.')
	def acquire(self):
		return Reason(self.type+' ['+self.val()+'] is not less than or equal to ['+self.value+'].',not self.val()<=self.value)
	def retract(self): return Reason()
	
class StringLT(StringAttr):
	type   = 'string LT'
	title  = 'String LT'
	action = 'test string LT'
	
	def satisfied(self): return Reason(`self`+" hasn't been attempted yet.",not self.acquired)
	def str(self): return 'Test that '+self.type+' ['+self.val()+'] is less than ['+self.value+'].'
	def val(self): abort('Missing val in StringLT.')
	def acquire(self):
		return Reason(self.type+' ['+self.val()+'] is not less than ['+self.value+'].',not self.val()<self.value)
	def retract(self): return Reason()
	
class StringGE(StringAttr):
	type   = 'string GE'
	title  = 'String GE'
	action = 'test string GE'
	
	def satisfied(self): return Reason(`self`+" hasn't been attempted yet.",not self.acquired)
	def str(self): return 'Test that '+self.type+' ['+self.val()+'] is greater than or equal to ['+self.value+'].'
	def val(self): abort('Missing val in StringGE.')
	def acquire(self):
		return Reason(self.type+' ['+self.val()+'] is not greater than or equal to ['+self.value+'].',not self.val()>=self.value)
	def retract(self): return Reason()
	
class StringGT(StringAttr):
	type   = 'string GT'
	title  = 'String GT'
	action = 'test string GT'
	
	def satisfied(self): return Reason(`self`+" hasn't been attempted yet.",not self.acquired)
	def str(self): return 'Test that '+self.type+' ['+self.val()+'] is greater than ['+self.value+'].'
	def val(self): abort('Missing val in StringGT.')
	def acquire(self):
		return Reason(self.type+' ['+self.val()+'] is not greater than ['+self.value+'].',not self.val()>self.value)
	def retract(self): return Reason()

class Location(StringAttr):
	type   = 'location'
	action = 'locate'
	title  = 'Locations'
	
	def satisfy(self): 
		self.value = cwdd()
		return Reason()
		
	def satisfied(self): return Reason('Location not chosen yet.',len(self.value)>1 and self.value[0]=='?')

class UpdateURL(StringAttr):
	type   = 'update url'
	title  = 'Update URLs'
	action = 'update url'
 
class PackageDirectory(StringAttr):
	type   = 'package directory'
	title  = 'Package Directories'
	action = 'package directory'
	
class DateOfCreation(StringAttr):
	type   = 'date of creation'
	title  = 'Date of Creations'
	action = 'date of creation'
	
	def __init__(self): self.value = time.ctime(time.time())

class CacheOfOrigin(StringAttr):
	type  = 'cache of origin'
	title = 'Caches of Origin'
	action = 'cache of origin'
 
	def equal(self,n):
		a = self.value[:]
		b = n.value[:]
		while len(a)>0 and a[-1]=='/': a = a[:-1]
		while len(b)>0 and b[-1]=='/': b = b[:-1]
		return a==b
