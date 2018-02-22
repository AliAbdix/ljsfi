#
#	Copyright Saul Youssef, January 2005
#
from StringAttr import *

def leqVersionTuple(x,y):
	if len(x)>0:
		if len(y)>0: 
			q = x[0]<=y[0] and leqVersionTuple(x[1:],y[1:])
		else:
			q = 0
	else:
		q = 1
	return q

class VersionTuple(Environment):
	type  = 'version tuple'
	title = 'Version Tuple'
	action = 'Version Tuple'
	
	def __init__(self,versionString,separator='.'):
		self._versionString = versionString
		self._separator = separator
		self._tuple = []
		try:
			for x in string.split(self._versionString,self._separator):
				self._tuple.append(int(x))
		except ValueError:
			abort('Syntax error in ['+self._versionString+'].')
			
	def equal(self,x): return self._versionString==x._versionString and self._separator==x._separator
	def str(self): return self._versionString
	
	def satisfiable(self): return Reason()
	def satisfied  (self): return Reason()
		
	def satisfies(self,v):
		if self.type[:13]==v.type[:13]:
			if    v.type=='version tuple'    :  return self._tuple==v._tuple
			elif  v.type=='version tuple <=' :  return leqVersionTuple(self._tuple,v._tuple)
			elif  v.type=='version tuple <'  :  return leqVersionTuple(self._tuple,v._tuple) and not self._tuple==v._tuple
			elif  v.type=='version tuple >=' :  return leqVersionTuple(v._tuple,self._tuple)
			elif  v.type=='version tuple >'  :  return leqVersionTuple(v._tuple,self._tuple) and not self._tuple==v._tuple
			else:
				return 0
		else:
			return 0

class VersionTupleLE(VersionTuple):
	type   = 'version tuple <='
	title  = 'Version Tuple <='
	action = 'Version Tuple <='

class VersionTupleLT(VersionTuple):
	type   = 'version tuple <'
	title  = 'Version Tuple <'
	action = 'Version Tuple <'

class VersionTupleGE(VersionTuple):
	type   = 'version tuple >='
	title  = 'Version Tuple >='
	action = 'Version Tuple >='

class VersionTupleGT(VersionTuple):
	type   = 'version tuple >'
	title  = 'Version Tuple >'
	action = 'Version Tuple >'	

class Version(StringAttr):
	type   =  'version'
	title  =  'Version Strings'
	action =  'version'
	
	def str(self): return '= '+self.value
	
	def satisfies(self,v):
		if self.type[:7]==v.type[:7]:
			if    v.type=='version'    : return self.value==v.value
			elif  v.type=='version <=' : return self.value<=v.value
			elif  v.type=='version <'  : return self.value< v.value
			elif  v.type=='version >=' : return self.value>=v.value
			elif  v.type=='version >'  : return self.value> v.value
			else:
				return 0
		else:
			return 0
	
class VersionLE(StringAttr):
	type   = 'version <='
	title  = 'Version <=s'
	action = 'version <='
	
class VersionLT(StringAttr):
	type   = 'version <'
	title  = 'Version <s'
	action = 'version <'
	
class VersionGE(StringAttr):
	type   = 'version >='
	title  = 'Version >=s'
	action = 'version >='
	
class VersionGT(StringAttr):
	type   = 'version >'
	title  = 'Version >s'
	action = 'version >'

class Release(StringAttr):
	type   =  'release'
	title  =  'Release Strings'
	action =  'release'
	
	def str(self): return '= '+self.value
	
	def satisfies(self,v):
		if self.type[:7]==v.type[:7]:
			if    v.type=='release'    : return self.value==v.value
			elif  v.type=='release <=' : return self.value<=v.value
			elif  v.type=='release <'  : return self.value< v.value
			elif  v.type=='release >=' : return self.value>=v.value
			elif  v.type=='release >'  : return self.value> v.value
			else:
				return 0
		else:
			return 0
	
class ReleaseLE(StringAttr):
	type   = 'release <='
	title  = 'Release <=s'
	action = 'release <='
	
class ReleaseLT(StringAttr):
	type   = 'release <'
	title  = 'Release <s'
	action = 'release <'
	
class ReleaseGE(StringAttr):
	type   = 'release >='
	title  = 'Release >=s'
	action = 'release >='
	
class ReleaseGT(StringAttr):
	type   = 'release >'
	title  = 'Release >s'
	action = 'release >'

class Tag(StringAttr):
	type   =  'tag'
	title  =  'Tag Strings'
	action =  'tag'
	
	def str(self): return '= '+self.value
	
	def satisfies(self,v):
		if self.type[:3]==v.type[:3]:
			if    v.type=='tag'    : return self.value==v.value
			elif  v.type=='tag <=' : return self.value<=v.value
			elif  v.type=='tag <'  : return self.value< v.value
			elif  v.type=='tag >=' : return self.value>=v.value
			elif  v.type=='tag >'  : return self.value> v.value
			else:
				return 0
		else:
			return 0
	
class TagLE(StringAttr):
	type   = 'tag <='
	title  = 'Tag <=s'
	action = 'tag <='
	
class TagLT(StringAttr):
	type   = 'tag <'
	title  = 'Tag <s'
	action = 'tag <'
	
class TagGE(StringAttr):
	type   = 'tag >='
	title  = 'Tag >=s'
	action = 'tag >='
	
class TagGT(StringAttr):
	type   = 'tag >'
	title  = 'Tag >s'
	action = 'tag >'

class Patch(StringAttr):
	type   =  'patch'
	title  =  'Patch Strings'
	action =  'patch'
	
	def str(self): return '= '+self.value
	
	def satisfies(self,v):
		if self.type[:5]==v.type[:5]:
			if    v.type=='patch'    : return self.value==v.value
			elif  v.type=='patch <=' : return self.value<=v.value
			elif  v.type=='patch <'  : return self.value< v.value
			elif  v.type=='patch >=' : return self.value>=v.value
			elif  v.type=='patch >'  : return self.value> v.value
			else:
				return 0
		else:
			return 0
	
class PatchLE(StringAttr):
	type   = 'patch <='
	title  = 'Patch <=s'
	action = 'patch <='
	
class PatchLT(StringAttr):
	type   = 'patch <'
	title  = 'Patch <s'
	action = 'patch <'
	
class PatchGE(StringAttr):
	type   = 'patch >='
	title  = 'Patch >=s'
	action = 'patch >='
	
class PatchGT(StringAttr):
	type   = 'patch >'
	title  = 'Patch >s'
	action = 'patch >'

class Option(StringAttr):
	type   =  'option'
	title  =  'Option Strings'
	action =  'option'
	
	def str(self): return '= '+self.value
	
	def satisfies(self,v):
		if self.type[:6]==v.type[:6]:
			if    v.type=='option'    : return self.value==v.value
			elif  v.type=='option <=' : return self.value<=v.value
			elif  v.type=='option <'  : return self.value< v.value
			elif  v.type=='option >=' : return self.value>=v.value
			elif  v.type=='option >'  : return self.value> v.value
			else:
				return 0
		else:
			return 0
	
class OptionLE(StringAttr):
	type   = 'option <='
	title  = 'Option <=s'
	action = 'option <='
	
class OptionLT(StringAttr):
	type   = 'option <'
	title  = 'Option <s'
	action = 'option <'
	
class OptionGE(StringAttr):
	type   = 'option >='
	title  = 'Option >=s'
	action = 'option >='
	
class OptionGT(StringAttr):
	type   = 'option >'
	title  = 'Option >s'
	action = 'option >'
