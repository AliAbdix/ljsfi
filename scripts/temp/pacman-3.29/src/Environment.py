#
#	Copyright Saul Youssef, July 2004
#
from Base    import *
from WebPage import *

class Consistent(Set):
	def consistent(self):  abort('Missing consistent function.')
	
class Satisfiable(Set):
	lastsat  = 0
	lastfail = 0
	def satisfied    (self): abort('Missing satisfied function.'   )
	def satisfiable  (self): abort('Missing satisfiable function.' )
	def satisfy      (self): abort('Missing satisfy function.'     )
	def setup        (self): return self.satisfied()
	def restore      (self): abort('Missing restore function.'     )
	
class SatisfyOrder(Set):
	def satisfies(self,x): return self==x
	
class Action(Set):
	def acquire(self): return Reason('Cannot acquire ['+`self`+'].')
	def retract(self): return Reason('Cannot retract ['+`self`+'].')
	acquired = 0

class Collectable:
	def collect(self,q): 
		if q(self): return AND(self)
		else:       return AND(    )
		
class Application:
	def __call__(self,E): abort('Missing call in Application.')
	
class Collection:
	def __call__(self,E): abort('Missing call in Collection.')
		
class Applicable:
	def apply(self,app): return app(self)
	
class ApplySettable:
	def applySet(self,app): pass

class HtmlEnv(HtmlOut): 
	def bullet(self,w):
		if   self.satisfied().ok(): w.bullet(1,1)
		else:
			if  not self.satisfiable().ok(): w.bulletcross()
			else:
				if    self.lastsat:  w.bullet(0,1)
				elif  self.lastfail: w.bulletcross()
				else:                w.bullet(0,0)
				
	def errorMessage(self,w):
		satreason = self.satisfied()
		if   satreason.ok(): pass
		else:
			reason = self.satisfiable()
			if not reason.ok(): w.brokenText(' '+`reason`)
			else:
				if     self.lastsat: w.brokenText(' '+`satreason`)
				elif  self.lastfail: w.brokenText(' '+`satreason`)
				else:                    pass
		return `satreason`
				
	def htmlSelect(self,w,q):
		if q(self): self.htmlLine(w)

class Environment(Satisfiable,Action,SatisfyOrder, Collectable,Applicable,ApplySettable, HtmlEnv,IOAble,ShellOut,  History):
	type     = ''
	title    = ''
	action   = ''
	export   = 0
	acquired = 0
	_parentPackageName = ''
	
#-- Set
	def __eq__(self,x):
		if self.type==x.type: return self.equal(x)
		else:                 return 0
	def equal(self,x): abort('equal missing in Environment.')
	def display(self,indent=0): print indent*' '+self.statusStr()+' '+`self`
	def str(self): abort('Missing str in Environment.')
	def __repr__(self): return self.type+' '+self.str()
	def statusStr(self):
		if        self.lastsat:                                 s = '[*]'
		elif      self.lastfail or not self.satisfiable().ok(): s = '[X]'
		else:                                                   s = '[ ]'
		return s
	def satset(self,q):
		if q:
			self.lastsat  = 1
			self.lastfail = 0
		else:
			self.lastsat  = 0
			self.lastfail = 1

#-- Satisfiable
	def satisfiable(self): return Reason()
	def satisfied(self): return Reason(`self`+" hasn't been attempted yet.",not self.acquired)
	def satisfy(self):
		verbo.log('action','Attempt to satisfy ['+`self`+']...')
		reason = Reason()
		if self.satisfied().ok():
			self.lastsat = 1
			if not self.type in ['AND','OR']:
				verbo.log('action',`self`+' satisfied...')
				self.history(time.ctime(time.time()),'satisfied',cwdd(),getusername(),`self`)
		else:
			verbo.log('action',`self`+' is not satisfied...')
			self.acquired = 0
			if self.type=='AND' or self.type=='OR' or ask('action','OK to attempt ['+`self`+']?'):
				if reason.ok():
					reason = self.acquire()
					if reason.ok():
						self.acquired = 1
						self.lastsat  = 1
						if not self.type in ['AND','OR']:
							verbo.log('action',`self`+' attempt succeeded...')
							self.history(time.ctime(time.time()),'acquired',      cwdd(),getusername(),`self`)
					else:
						self.lastfail = 1
						if not self.type in ['AND','OR']:
							verbo.log('action',`self`+' attempt failed...')
							self.history(time.ctime(time.time()),'acquire failed',cwdd(),getusername(),`self`)
			else:
				reason.reason('Permission to do ['+`self`+'] has been refused.')
		return reason

	def restore(self):
		reason = Reason()
		if self.acquired:
			if self.type=='AND' or self.type=='OR' or ask('action','OK to attempt to undo ['+`self`+']?'):
				reason = self.retract()
				if reason.ok():
					self.acquired = 0
					self.lastsat  = 0
					self.lastfail = 0
					if not self.type in ['AND','OR']:
						verbo.log('action',`self`+' retracted...')
						self.history(time.ctime(time.time()),'retracted',        cwdd(),getusername(),`self`)
				else:
					if not self.type in ['AND','OR']:
						verbo.log('action',`self`+' retraction failed...')
						self.history(time.ctime(time.time()),'retraction failed',cwdd(),getusername(),`self`)
			else:
				reason.reason('Permission to undo ['+`self`+'] has been refused.')
		return reason
		
#-- Verify/Repair
	def verify(self): return self.satisfied()
	def repair(self): return self.satisfy  ()
		
#-- SatisfyOrder
	def satisfies(self,x): return self==x

#-- ShellOut
	def shellOut(self,csh,sh,py,pl,ksh): pass
	
#-- Update
	def updateCheck (self): return Reason()
	def update      (self): return Reason()
	def updateRemove(self): return Reason()
	def displayM(self,depth=99999,indent=0): return Reason()
	def remove      (self): return Reason()
	def fetch       (self): return self.satisfiable()

#-- HtmlOut
	def htmlOut  (self,w): 
		w.text(`self`)
		if verbo('web'): w.text(' '); self.errorMessage(w)
		if self.acquired and switch('showAcquired'): w.text(' @ ')
		
class EnvironmentList(Environment,List):
	type   = 'environment list'
	title  = 'Environment Lists'
	action = 'environment list'
	
	def display(self,indent=0):
		print indent*' '+self.statusStr()+' '+self.type
		for e in self: 
			if e.type=='lazy package': print (indent+8)*' '+self.statusStr()+' '+ 'package '+e.str()
			else: e.display(indent+8)
	
	def updateCheck (self): return allReason(self,lambda e: e.updateCheck ())
	def update      (self): return allReason(self,lambda e: e.update      ())
	def updateRemove(self): return allReason(self,lambda e: e.updateRemove())
	def displayM    (self,depth=99999,indent=0): return allReason(self,lambda e: e.displayM(depth,indent))
	def remove(self): return allReason(self,lambda e: e.remove())
#	def fetch (self): return allReason(self,lambda e: e.fetch ())

	def collect(self,q):
		if q(self): col = AND(self)
		else:       col = AND()
		
		if hasattr(q,'quit') and q.quit(self): pass
		else:
			for e in self: col.extend(e.collect(q))
		return col

	def apply(self,app): 
		reason = app(self)
		if reason.ok():
			if hasattr(app,'quit') and app.quit(self): pass
			else:
				for e in self:
					if reason.ok(): reason = e.apply(app)
					if not reason.ok(): break
		return reason
		
	def applySet(self,app):
		if hasattr(app,'quit') and app.quit(self): pass
		else:
			for i in range(len(self)):
				set,E = app(self[i])
				if set: self[i] = E
				self[i].applySet(app)
					
	def htmlLine(self,w): 
		self.bullet(w); w.text(self.type)
			
	def htmlOut(self,w):
		self.htmlLine(w)
		w.text('<ul>')
		count = 0
		for e in self:
			count = count + 1
			e.bullet(w)
			if e.title=='Packages': e.htmlOutf(w)
			else:                   e.htmlOut (w)
			if count!=len(self) and e.type!='AND' and e.type!='OR': w.text('<br>')
			w.cr()
		w.text('</ul>')
			
	def htmlPackages(self,w):
		self.bullet(w); self.htmlShortLine(w)
		pacs = filter(lambda e: e.title=='Packages',self)
		if len(pacs)>0:
			w.text('<ul>'); w.cr()
			pmax = 0
			for en in self: 
				if en.title=='Packages' or en.type=='AND' or en.type=='OR':
					pacs = filter(lambda e: e.title=='Packages',en)
				else:
					pacs = AND()
					
				if en.title=='Packages' or len(pacs)>0: 
					en.htmlPackages(w)
					if len(pacs)==0: w.text('<br>')
					w.cr()
			w.text('</ul>'); w.cr()	
		else:
			w.text('<br>'); w.cr()				
			
class AND(EnvironmentList):
	type   = 'AND'
	title  = 'ANDs'
	action = 'AND'
	def __init__(self,*environs): self.__environs = [E for E in environs]
	
#-- Set
	def equal(self,E):  return self.__environs == E.__environs
	def str(self): return `self.__environs`
		
#-- List
	def __getitem__(self,index): return self.__environs[index]
	def __setitem__(self,index,E): self.__environs[index] = E
	def __len__    (self):       return len(self.__environs)
	def append     (self,E):     self.__environs.append(E)
	def extend     (self,E):
		if E.type=='AND': self.__environs.extend(E.__environs)
		else:             self.__environs.append(E)
	def pop        (self,i):  return self.__environs.pop(i)

#-- Satisfiable
	def satisfied  (self): return allReasonQ (self,lambda en: en.satisfied   ( ))
	def satisfiable(self): return allReasonQ (self,lambda en: en.satisfiable ( ))
	def fetch      (self): return allReasonQ (self,lambda en: en.fetch       ( ))

#-- Action
	def satisfy    (self): 
		r = allReasonQ (self,lambda en: en.satisfy    ( ))
		if r.ok(): self.lastsat  = 1
		else:      self.lastfail = 1
		return r
	def setup      (self): return allReasonQ(self,lambda en: en.setup())
	def restore    (self): 
		r = allReason(self,lambda en: en.restore    ( ))
		self.lastsat  = 0
		self.lastfail = 0
		return r
	def verify     (self): 
		r = allReason (self,lambda en: en.verify())
		if not r.ok(): 
			self.lastsat = 0
			self.lastfail = 1
		return r
		
#-- SatisfyOrder
	def satisfies(self,E): 
		if    E.type=='AND': return forall(   E,lambda e: self.satisfies(e))
		elif  E.type=='OR' : return exists(   E,lambda e: self.satisfies(e))
		else:                return exists(self,lambda e: e.   satisfies(E))
#-- HtmlOut
	def htmlLine(self,w): 
		w.text(self.type); w.cr()
		if self.acquired and switch('showAcquired'): w.text(' @ ')
	
#-- ShellOut
	def shellOut(self,csh,sh,py,pl,ksh):
		for e in self: e.shellOut(csh,sh,py,pl,ksh)

class OR(EnvironmentList):
	type   = 'OR'
	title  = 'ORs'
	action = 'OR'
	def __init__(self,*environs): self.__environs = [E for E in environs]

#-- Set
	def equal(self,E): return self.__environs == E.__environs
	def str(self): return `self.__environs`
#-- List
	def __getitem__(self,index): return self.__environs[index]
	def __setitem__(self,index,E): self.__environs[index] = E
	def __len__    (self):       return len(self.__environs)
	def append     (self,E):     return self.__environs.append(E)
	def extend     (self,E):
		if E.type=='OR':  self.__environs.extend(E.__environs)
		else:             self.__environs.append(E)
	def pop        (self,i):     return self.__environs.pop(i)

#-- Satisfiable
	def satisfied  (self): 
		r = existsReason (self,lambda en: en.satisfied  ( ))
		if not r.ok(): r.headline = 'None of the following alternatives are satisfied:'
		return r
#		return existsReason (self,lambda en: en.satisfied  ( ))
	def verify     (self): 
		r = existsReason (self,lambda en: en.verify( ))
		if not r.ok(): 
			self.lastsat = 0
			self.lastfail= 1
			r.headline = 'None of the following alternatives are satisfied:'
		return r
	def satisfiable(self): 
		r = existsReason(self,lambda en: en.satisfiable( ))
		if not r.ok(): r.headline = 'None of the following alternatives can be satisfied:'
		return r
#		return existsReason (self,lambda en: en.satisfiable( ))
	def fetch      (self): 
		r = existsReason(self,lambda en: en.fetch())
		if not r.ok(): r.headline = 'None of the following alternatives can be satisfied:'
		return r
#		return existsReason2(self,lambda en: en.fetch      ( ))
	def setup      (self): 
		r = existsReason (self,lambda en: en.setup      ( ))
		if not r.ok(): r.headline = 'None of the following alternatives are satisfied:'
		return r
#		return existsReason (self,lambda en: en.setup      ( ))
	def uninstall  (self): return    allReason (self,lambda en: en.uninstall  ( ))
		
#-- Action
	def acquire    (self): 
		r = existsReason(self,lambda en: en.satisfy     ( ))
		if not r.ok(): r.headline = 'None of the following alternatives succeeded:'
		return r
#		return existsReason(self,lambda en: en.satisfy     ( ))
	def retract    (self): return    allReason(self,lambda en: en.restore     ( ))

#-- SatisfyOrder
	def satisfies(self,E): 
		if    E.type=='AND': return forall(   E,lambda e: self.satisfies (e))
		elif  E.type=='OR' : return exists(   E,lambda e: self.satisfies (e))
		else:                return forall(self,lambda e: e.   satisfies (E))
#-- HtmlOut
	def htmlLine(self,w): 
		w.text(self.type); w.cr()
		if self.acquired and switch('showAcquired'): w.text(' @ ')
#-- ShellOut
	def shellOut(self,csh,sh,py,pl,ksh):
		for e in self: e.shellOut(csh,sh,py,pl,ksh)	
