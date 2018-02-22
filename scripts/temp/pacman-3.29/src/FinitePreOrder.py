#
#	Copyright, Saul Youssef, 2004
#
from Base import *

class FinitePreOrder:
	def __init__(self,pairs):
		self._pairs = pairs
		self._le = {}
		for p in pairs:
			if not p[0] in self._le.keys(): self._le[p[0]] = {p[0]:''}
			if not p[1] in self._le.keys(): self._le[p[1]] = {p[1]:''}
			if self._le[p[0]].has_key(p[1]): self._le[p[0]][p[1]] = ''
			
		while 1:
			got_one = 0
			for p in self._pairs:
				x,y = p[0],p[1]
				prelen = len(self._le[x])
				self._le[x].update(self._le[y])
				if len(self._le[x])>prelen: got_one = 1
			if not got_one: break
			
	def le(self,p,q):
		if p==q: 
			leq = 1
		elif self._le.has_key(p) and self._le.has_key(q):
			leq = self._le[p].has_key(q)
		else:
			leq = 0
		return leq

	def ge(self,p,q): return self.le(q,p)
	def eq(self,p,q): return self.le(p,q) and     self.le(q,p)
	def lt(self,p,q): return self.le(p,q) and not self.eq(p,q)
	def gt(self,p,q): return self.lt(q,p)
			
	def items(self): return self._le.keys()
	def classes(self):
		c = Clusters(self.items())
		return c.cluster(lambda x,y: self.le(x,y) and self.le(y,x))

