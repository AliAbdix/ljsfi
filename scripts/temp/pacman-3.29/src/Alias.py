#
#	Copyright, Saul Youssef, October 2003
#
from Environment import *

def alias(text):
	text2 = text[:]
	for key,val in Alias._aliases.items():
		if string.count(text2,key+' ')>0:
			text2 = string.replace(text2,key,val)
			break
	return text2

class Alias(Environment):
	type   = 'alias'
	title  = 'Aliases'
	action = 'alias'
	
	_aliases = {}
	
	def __init__(self,aliasFrom='',aliasTo=''):
		self.aliasFrom = aliasFrom
		self.aliasTo   = aliasTo
		
	def str(self): return self.aliasFrom+' -> '+self.aliasTo
	def equal(self,x): return self.aliasFrom==x.aliasFrom and self.aliasTo==x.aliasTo
	
	def satisfied(self): 
		reason = Reason()
		if self._aliases.has_key(self.aliasFrom): 
			if self._aliases[self.aliasFrom]==os.path.expandvars(self.aliasTo):
				pass
			else:
				reason = Reason("Alias ["+`self`+"] has been assigned ["+self._aliases[self.aliasFrom]+" Can't overwrite.")
		else:
			return Reason("Alias ["+`self`+"] has not been set.")
		return reason
	def satisfiable(self): return Reason()
	def setup(self): self.satisfy()
	def acquire(self): 
		self.aliasTo = os.path.expandvars(self.aliasTo)
		self._aliases[self.aliasFrom] = self.aliasTo
		return Reason()
	def retract(self):
		if self._aliases.has_key(self.aliasFrom):
			del self._aliases[self.aliasFrom]
		else:
			reason = Reason("Can't retract ["+`self`+"].  Alias has not been set.")
		return Reason()
		
	def shellOut(self,csh,sh,py,pl,ksh):
		csh.write('alias '+self.aliasFrom+' "'+self.aliasTo+'"\n')
		sh. write('alias '+self.aliasFrom+'="'+self.aliasTo+'"\n')
		py. write('Alias._aliases["'+self.aliasFrom+'"]="'+self.aliasTo+'"\n')
		ksh. write('alias '+self.aliasFrom+'="'+self.aliasTo+'"\n')

	
