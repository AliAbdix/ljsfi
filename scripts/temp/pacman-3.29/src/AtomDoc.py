#
#	Copyright 2004, Saul Youssef
#

class AtomDoc:
	def __init__(self,name,args,req=0):
		self.name = name
		self.args = args
		self.req  = req
		self.text = ''
	
	def __repr__(self): return self.name

		
	
