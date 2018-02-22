#
#	Copyright, December 2003, Saul Youssef
#
import TrustedCaches,Source
import Package,Cache,Base
from Environment import *

def pacsource(E):
	for e in E:
		if e.type=='pacman source code': return e
	return AND()
	
class Update(Base.HtmlOut):
	def __init__(self,cache=Cache.Cache(),pre=AND(),post=AND()):
		self.cache  = cache
		self.pre    = pre
		self.post   = post
		self.hasupdate = not cache.cachename()==''
		
	def __repr__(self): return `self.cache`+' '+`self.hasupdate`
		
	def htmlOut(self,w):
		w.text('<table>'); w.cr()
		
		w.text('<tr>')
		w.text('<td>')
		w.text('<h2>Current Package</h2>')
		w.text('</td>')
		w.text('<td>')
		w.text('<h2>Update</h2>')
		w.text('</td>')		
		w.text('</tr>')
		
		w.text('<tr>')
		w.text('<td>')
		pacsource(self.pre).htmlOut(w)
		w.text('</td>')
		w.text('<td>')
		pacsource(self.post).htmlOut(w)
		w.text('</td>')
		
		w.text('</tr>')		
		w.text('</table>'); w.cr()
	
class UpdateApplication(Application):
	def __init__(self,mode='self'): self.uc = UpdateCheckApplication(mode)
		
	def __call__(self,E):
		reason = Reason()
		if E.title=='Packages':
			up = E.upd()
			if not up.hasupdate: reason = self.uc(E)
			if reason.ok():
				if up.hasupdate:
					verbo.log('up','Updating ['+E.name+'] from ['+up.cache.cachename()+']...')
					
					sat = E.satisfied().ok()
					reason = E.restore()
					if reason.ok():
						Package.Package._base[E._hash] = [copy.deepcopy(up.post),Update(),copy.deepcopy(up.post),Package.Package._base[E._hash][3]]
						reason = E.resolve()
						if reason.ok() and sat: reason = E.satisfy()
		return reason

class UpdateCheckApplication(Application):
	def __init__(self,mode='self'):
		self._done = {}
		usermode,ucache = switchpar('cache')
		
		if usermode:
			if ucache=='trust' or ucache=='trusted':
				self.cache = TrustedCaches.getTrustedCaches()
				self.mode  = 'trusted'
			else:
				self.cache = TrustedCaches.cacheNameToCache(ucache)
				self.mode  = 'user'
		else:
			self.cache = None
			self.mode  = 'self'
	
	def __call__(self,E):
		reason = Reason()
		up = 0
		if E.title=='Packages':
			if self.mode=='self': 
				if E.cachename=='': cache = TrustedCaches.getTrustedCaches()
				else:               cache = TrustedCaches.cacheNameToCache(E.cachename)
			else:                 
				cache = self.cache
			
			E2 = copy.deepcopy(E)
			reason,env = cache.resolve(E2)
				
			if reason.ok():
				if not E.resolved or not env==E.getOriginal():
					code = Source.Source(E.guardstring); code.parse()
					guard = code.evaluate()
					if env.satisfies(guard):
						up = 1
						verbo.log('up',"Package ["+E.name+"] has an update from cache ["+cache.cachename()+"].")
					else:
						up = 0
						if verbo('up'):
							print "Package ["+E.name+"] has an update from cache ["+cache.cachename()+"]."
							print "However, the update no longer satisfies ["+E.guardstring+"]."
					if up: E.setUpdate(Update(cache,E.bdy(),env))
				else:
					verbo.log('up',"Package ["+E.name+"] is up to date.")
			else:  
				E.setUpdate(Update())
		return reason

	def quit(self,E):
		q = 0
		if E.type=='package' and E.check():
			if self._done.has_key(E._hash): q = 1
			else:
				self._done[E._hash] = ''
		return q
