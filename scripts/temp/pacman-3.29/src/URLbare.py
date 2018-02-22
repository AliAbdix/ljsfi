#
#	Copyright Saul Youssef, July 2003
#
from StringAttr import *
from WebPage    import *
import os

class URLbare(StringAttr):
	type   = 'bare url'
	action = 'url'
	title  = 'Bare URLs'
	
	def __init__(self,value,target='_blank'): self.value,self.target = value,target

	def str(self):
		if self.target=='': return '<a href="'+os.path.expandvars(self.value)+'"><font color=#000000>'+os.path.expandvars(self.value)+'</font></a>'
		else:               return '<a href="'+os.path.expandvars(self.value)+'" target="'+os.path.expandvars(self.target)+'"><font color=#000000>'+self.value+'</font></a>'
