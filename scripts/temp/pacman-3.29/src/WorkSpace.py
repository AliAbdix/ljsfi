#
#	Copyright, Saul Youssef, December 2003
#
from Directory             import *
from EnvironmentVariable   import *
from FileAccess            import *
from Chown                 import *
from FreeMegs              import *

class WorkSpace(Environment):
	type   = 'work space'
	title  = 'Work Spaces'
	action = 'create workspace'
	
	def __init__(self,name,env,minmegs=100,owner='- any -',options='ownerWrite temporary'):
		self.name      = name
		self.env       = env
		self.minmegs   = minmegs
		self.owner     = owner
		self.options   = options
		
		self.directory = Directory('?Choose a location for workspace ['+self.name+']: ')
		self.enviro    = Setenv(self.env,'')
		self.access    = FileAccess('',self.options,'on')
#		self.own       = OwnedBy('',self.owner)
		self.own       = Chown('',self.owner)
		self.megs      = FreeMegs(self.minmegs,'')
		
	def str(self):
		s = self.name+': '+self.env
		if self.satisfied().ok():
			s = s + ' ( '+`localmegs(self.directory.path)`+' > '+`self.minmegs`+' Megs)'
		else:
			s = s + ' (>'+`self.minmegs`+' Megs)'
		if self.owner!='- any -':
			s = s + ', owned by ['+self.owner+']'
		s = s + ', options ['+self.options+']'
		if self.satisfied().ok():
			s = s + ', ' + self.directory.path
		return s
		
	def equal(self,x):
		return  self.name ==x.name and \
			self.env  ==x.env and \
			self.minmegs == x.minmegs and \
			self.owner == x.owner and \
			self.options == x.options 
		       
	def satisfied(self):
		reason = self.directory.satisfied()
		if not reason.ok(): self.directory = Directory('?Choose a location for workspace ['+self.name+']: ')
		if reason.ok(): reason = self.enviro. satisfied()
		if reason.ok(): reason = self.access. satisfied()
		if reason.ok(): reason = self.own.    satisfied()
		if reason.ok(): reason = self.megs.   satisfied()
		return reason
		
	def setup(self): return self.enviro.setup()
		
	def acquire(self):
		reason = self.directory.satisfy()
		if reason.ok():
			self.enviro = Setenv(self.env,self.directory.path)
			self.access = FileAccess(self.directory.path,self.options,'on')
#			self.own    = OwnedBy(self.directory.path,self.owner)
			self.own    = Chown(self.directory.path,self.owner)
			self.megs   = FreeMegs(self.minmegs,self.directory.path)
			
			reason = self.access.satisfy()
			if reason.ok(): reason = self.own.    satisfy()
			if reason.ok(): reason = self.megs.   satisfy()
			if reason.ok(): reason = self.enviro. satisfy()
		return reason
		
	def retract(self):
		reason = self.enviro.retract()
		if reason.ok(): reason = self.megs.      retract()
		if reason.ok(): reason = self.own.       retract()
		if reason.ok(): reason = self.access.    retract()
		if reason.ok() and not contains(self.options,'permanent','nocase') and \
		                   not contains(self.options,'permanant','nocase'): reason = self.directory. retract()
		return reason

	def shellOut(self,csh,sh,py,pl,ksh):
		if self.acquired:
			self.enviro.shellOut(csh,sh,py,pl,ksh)
