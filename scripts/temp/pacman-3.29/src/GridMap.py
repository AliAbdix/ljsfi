#
#	Copyright Saul Youssef, December 2003
#
from Base     import *
from Username import *

def dnparse(dnstring):
	dns = []
	a1 = string.split(dnstring,'/')
	for s in a1:
		if s=='': pass
		else:
			a2 = string.split(s,'=')
			if   len(a2)==2:
				dns.append(DNItem(a2[0],a2[1]))
			elif string.count(s,'=')==0:
				dns.append(DNItem('CN',s))
			else:
				print "Warning: can't parse ["+dnstring+"] in grid-mapfile..."
	return dns

class DNItem(Set,PrintOut):
	def __init__(self,dntype,dnvalue):
		self._type  = dntype
		self._value = dnvalue
	def __repr__(self): return self._type+'='+self._value
	def __eq__(self,x): return self._type==x._type and self._value==x._value

class DN(Set,PrintOut):
	def __init__(self,dnstring):
		self._items = dnparse(dnstring)

	def __eq__(self,x): return \
		forall(self._items,lambda i: i in    x._items) and \
		forall(   x._items,lambda i: i in self._items)
		
	def __repr__(self):
		s = ''
		for i in range(len(self._items)):
			s = s + `self._items[i]`
			if not i==len(self._items)-1: s = s + '/'
		return s

	def cnMapsTo(self,cn,localuser):
		got_one = 0
		for item in self._items:
			if item._type=='CN' and item._value=='localuser':
				got_one = 1
				break
		return got_one
		
	def has(self,dni):
		got_one = 0
		for dn in self._items: 
			if dn==dni: got_one = 1; break
		return got_one
		
class GridMapFile(Set,PrintOut):
	def __init__(self,path='/etc/grid-security/grid-mapfile'):
		self._path = path
		self._dnus = []
		try:
			f = open(self._path,'r')
			lines = f.readlines()
			f.close()
			for line in lines:
				if len(line)>1:
					line2 = line[:-1]
					if len(line2)>1 and len(string.split(line2,'"'))>1:
						line2 = string.split(line2,'#')[0]
						dnstring = string.split(line2,'"')[1]
						userstring = string.strip(string.split(line2,'"')[-1])
						self._dnus.append([DN(dnstring),Username(userstring)])
		except (IOError,OSError):
			pass
		
	def __eq__(self,gmf):  self._dnus == gmf._dnus
	
	def __repr__(self): return 'grid-mapfile ['+self._path+'] '+`self._dnus`
	def display(self,indent=0):
		print indent*' '+'grid-mapfile ['+self._path+']:'
		for dnu in self._dnus:
			print indent*' '+'    '+`dnu[0]`+' => '+`dnu[1]`
			
	def hasDN(self,dnstring,localuser):
		for dnu in self._dnus:
			dn = dnu[0]
			un = dnu[1]
			if dn==DN(dnstring): return un==Username(localuser)
		return 0
			
	def firstDN(self,dnstring,localuser):
		got_one = 0
		for dnu in self._dnus:
			dn = dnu[0]
			un = dnu[1]			
			if dn==DN(dnstring): got_one = 1; break
		if got_one: return un==Username(localuser)
		else:       return 0
			
	def lastDN(self,dnstring,localuser):
		got_one = 0
		for i in range(len(self._dnus)-1,-1,-1):
			dnu = self._dnus[i]
			dn = dnu[0]
			un = dnu[1]			
			if dn==DN(dnstring): got_one = 1; break
		if got_one: return un==Username(localuser)
		else:       return 0
			
			
	def hasCN(self,cnstring,localuser):
		for dnu in self._dnus:
			dn = dnu[0]
			un = dnu[1]			
			if dn.has(DNItem('CN',cnstring)):
				if un==Username(localuser): return 1
		return 0
			
	def firstCN(self,cnstring,localuser):
		got_one = 0
		for dnu in self._dnus:
			dn = dnu[0]
			un = dnu[1]			
			if dn.has(DNItem('CN',cnstring)): got_one = 1; break
		if got_one: return un==Username(localuser)
		else:       return 0
			
	def lastCN(self,cnstring,localuser):
		got_one = 0
		for i in range(len(self._dnus)-1,-1,-1):
			dnu = self._dnus[i]
			dn = dnu[0]
			un = dnu[1]			
			if dn.has(DNItem('CN',cnstring)): got_one = 1; break
		if got_one: return un==Username(localuser)
		else:       return 0
			
