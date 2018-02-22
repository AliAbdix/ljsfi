
#	Copyright, Saul Youssef, August 2003
#
from StringAttr import *
import commands

def pacmanversion(): return version

class PacmanVersion(StringAttr):
	type   = 'pacman version'
	title  = 'Pacman Versions'
	action = 'pacman version'
			
	def __init__(self,value=pacmanversion()):
		self.value = value
			
	def str(self): return 'must be equal to ['+self.value+'], actually ['+pacmanversion()+'].'
	
	def satisfied  (self): 
		pv = pacmanversion()
		if pv=='- no pacman in $path -':
			r = Reason("[pacman] is not in the installer's path.")
#			return Reason("[pacman] is not in the installer's path.")
		else:
			r = Reason('pacman version is ['+pacmanversion()+']. It must be ['+self.value+'].',not pacmanversion() == self.value)
#			return Reason('pacman version is ['+pacmanversion()+']. It must be ['+self.value+'].',not pacmanversion() == self.value)
		self.satset(r.ok())
		return r
	def satisfiable(self): return self.satisfied()	

	def acquire(self): 
		r = self.satisfied()
		self.satset(r.ok())
		return r
#		return self.satisfied()
	def retract(self): return Reason()	
	
class PacmanVersionLE(PacmanVersion):
	type   = 'pacman version <='
	title  = 'pacman version <=s'
	action = 'pacman version <='
	
	def str(self): return '['+self.value+'], actually ['+pacmanversion()+'].'
	def satisfied(self): 
		pv = pacmanversion()
		if pv=='- no pacman in $path -':
			r = Reason("[pacman] is not in the installer's path.")
#			return Reason("[pacman] is not in the installer's path.")
		else:
			r = Reason('pacman version ['+pacmanversion()+'] must be <= ['+self.value+'].',not pacmanversion() <= self.value) 
#			return Reason('pacman version ['+pacmanversion()+'] must be <= ['+self.value+'].',not pacmanversion() <= self.value) 
		self.satset(r.ok())
		return r
	
class PacmanVersionLT(PacmanVersion):
	type   = 'pacman version <'
	title  = 'pacman version <s'
	action = 'pacman version <'
	
	def str(self): return '['+self.value+'], actually ['+pacmanversion()+'].'
	def satisfied(self):
		pv = pacmanversion()
		if pv=='- no pacman in $path -':
			r = Reason("[pacman] is not in the installer's path.")
#			return Reason("[pacman] is not in the installer's path.")
		else:
 			r = Reason('pacman version ['+pacmanversion()+'] must be < ['+self.value+'].',not pacmanversion() < self.value) 
# 			return Reason('pacman version ['+pacmanversion()+'] must be < ['+self.value+'].',not pacmanversion() < self.value) 
		self.satset(r.ok())
		return r
	
class PacmanVersionGE(PacmanVersion):
	type   = 'pacman version >='
	title  = 'pacman version >=s'
	action = 'pacman version >='
	
	def str(self): return '['+self.value+'], actually ['+pacmanversion()+'].'
	def satisfied(self): 
		pv = pacmanversion()
		if pv=='- no pacman in $path -':
			r = Reason("[pacman] is not in the installer's path.")
#			return Reason("[pacman] is not in the installer's path.")
		else:
			r = Reason('pacman version ['+pacmanversion()+'] must be >= ['+self.value+'].',not pacmanversion() >= self.value) 
#			return Reason('pacman version ['+pacmanversion()+'] must be >= ['+self.value+'].',not pacmanversion() >= self.value) 
		self.satset(r.ok())
		return r
	
class PacmanVersionGT(PacmanVersion):
	type   = 'pacman version >'
	title  = 'pacman version >s'
	action = 'pacman version >'
	
	def str(self): return '['+self.value+'], actually ['+pacmanversion()+'].'
	def satisfied(self): 
		pv = pacmanversion()
		if pv=='- no pacman in $path -':
			r = Reason("[pacman] is not in the installer's path.")
#			return Reason("[pacman] is not in the installer's path.")
		else:
			r = Reason('pacman version ['+pacmanversion()+'] must be > ['+self.value+'].',not pacmanversion() > self.value) 
#			return Reason('pacman version ['+pacmanversion()+'] must be > ['+self.value+'].',not pacmanversion() > self.value) 
		self.satset(r.ok())
		return r
