#
#	Copyright, Saul Youssef, June 2003
#
from Base         import *
from Environment  import *
import os

class Username(Environment):
	type   = 'username'
	action = 'username'
	title  = 'Usernames'
	
	def __init__(self,username=getusername()): self.__username = username
#-- Set
	def equal(self,u):  return self.__username == u.__username
	def str(self): return self.__username
	
#-- Compatible
	def compatible(self,u):
		comp = 0
		if   self.__username=='*':        comp = 1
		elif self.__username=='nonroot':  comp = u.__username != 'root'
		elif self.__username=='non-root': comp = u.__username != 'root'
		else:                             comp = self==u
		if comp==0: return Reason()
		else:       return Reason('Username ['+`self`+'] and  ['+`u`+'] are incompatible.')

#-- Satisfiable
	def satisfied(self):
		reason = Reason()
		name = getusername()
		if   self.__username==      '*': pass   
		elif self.__username=='nonroot': 
			if   name=='root'   : reason.reason('Username is root.  nonroot is required.')
			else:  pass
		elif self.__username=='non-root':
			if   name=='root'   : reason.reason('Username is root.  nonroot is required.')
			else:  pass
		else:
			if self.__username==name: pass
			else: reason.reason('Username ['+name+'] does not satisfy username ['+self.__username+'].')			
		return reason
#	def satisfiable(self): return self.satisfied()

#-- Action
	def acquire(self): return Reason("Can't change username to ["+self.__username+"].")
	def retract(self): return Reason("Can't change username to ["+self.__username+"].")

#-- SatisfyOrder
	def satisfies(self,x):
		if        not x.type==self.type:  return 0
		elif  x.__username ==       '*':  return 1
		elif  x.__username == 'nonroot':  return self.__username != 'root'
		elif  x.__username == 'non-root': return self.__username != 'root'
		else:  return self==x
		

	
