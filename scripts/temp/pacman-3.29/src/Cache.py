#
#	Copyright, 2004, Saul Youssef
#
from Base import *
import Registry


def plle(p,q): return [p._spec.subdirectory,p._spec.name]<= \
                      [q._spec.subdirectory,q._spec.name]

_prepend = {}

class Cache(Set,HtmlOut):
	def __init__(self): 
		self.UCL = ''
		self.type = ''
		self._mirror = ''
#-- Set
	def __repr__(self  ): return Registry.registry.short(self.UCL)
	def __eq__  (self,x): return self.UCL==x.UCL
	
	def display(self,indent=0):
		r,ps = self.contents([])
		if hasattr(self,'_name') and not self._name=='': print indent*' '+self._name
		else:                                            print indent*' '+`self`
		if not r.ok():
			print (indent+4)*' '+`r`
		else:
			sort(ps,plle)
			for p in ps: p.display(indent+4)
	
#-- Cache
	def check(self,spec,used):
		r = Reason()
		if exists(used,lambda cache: Registry.registry.equiv(cache,self.UCL)):
			r = Reason("Loop in cache dependencies ["+self.UCL+"->"+self.UCL+"].")
		used.append(self.UCL)
		return r,used
	def getAll(self,spec,used): abort('Missing getAll.')
	def getAllL(self,spec,used): return self.getAll(spec,used)
	def contents(self,used): abort('Missing contents.')
	def get(self,spec):
		used = []
		r,ps = self.getAll(spec,used)
		p = None
		if r.ok():
			if len(ps)>0: p = ps[0]
			else:         r = Reason("Can't find ["+spec.str()+"] in ["+`self`+"].")
		return r,p
	def put(self,package): return Reason("Can't add package ["+`package`+"] to ["+`self`+"].")
	def remove(self,spec): raise NotImplementedError
	def save(self):        return Reason()
	       
        def prepend(self,ps):
		r,qs = Reason(),[]
	        for p in ps:
		        r =	       self.prependBase(p._environ)
		        if r.ok(): r = self.prependBase(p._source )
		        if r.ok(): qs.append(p)
		        else:	  qs = []; break
	        return r,qs
	def prependBase(self,e):
	        r = Reason()
	        if e.type=='AND' or e.type=='OR':
	 	       for i in range(len(e)):
			       r = self.prependBase(e[i])
			       if not r.ok(): break
	        elif e.type=='lazy package':
			if self.prependOK(e._spec): 
				if self.type=='mirror' and hasattr(e._spec,'_mirrors'):
					e._spec._mirrors[self.UCL] = (self._mirror,self._updateTime,self._snapshot,)

				if hasattr(self,'_name') and not self._name=='':
					if len(e._spec.caches)==0 or not Registry.registry.equiv(self._name,e._spec.caches[0]):
						e._spec.caches.insert(0,self._name)
				else:
					if len(e._spec.caches)==0 or not Registry.registry.equiv(self.UCL,e._spec.caches[0]):
						e._spec.caches.insert(0,Registry.registry.short(self.UCL))
	        return r
	def prependOK(self,spec):
	        if not _prepend.has_key(self.UCL+spec._id()):
	 	       r,ps = self.getAll(spec,[])
	 	       _prepend[self.UCL+spec._id()] = r.ok() and len(ps)>0
	        return _prepend[self.UCL+spec._id()]
	def prependTop(self,ps):
		for p in ps:
			if self.type=='mirror' and hasattr(p._spec,'_mirrors'):
				p._spec._mirrors[self.UCL] = (self._mirror,self._updateTime,self._snapshot,)
		
			if hasattr(self,'_name') and not self._name=='':
				if len(p._spec.caches)==0 or not Registry.registry.equiv(self._name,p._spec.caches[0]):
					p._spec.caches.insert(0,self._name)
			else:
				if len(p._spec.caches)==0 or not Registry.registry.equiv(self.UCL,p._spec.caches[0]):
					p._spec.caches.insert(0,Registry.registry.short(self.UCL))
		return ps
						
class NullCache(Cache):
	def __init__(self): 
		self.UCL  = 'null'
		self.type = 'null'
	def getAll(self,spec,used): return Reason(),[]
	def put(self,package): return Reason()
