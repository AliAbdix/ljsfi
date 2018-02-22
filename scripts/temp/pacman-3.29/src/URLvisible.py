#
#	Copyright Saul Youssef, July 2003
#
from Environment  import *
from FileGetter   import *
from commandCheck import *

class URLvisible(Environment):
	type   = 'urlVisible'
	action = 'URL visibility test'
	title  = 'Visible URLs'
	
	def __init__(self,url): self._url = url
#-- Set
	def equal(self,x):  return self._url==x._url
	def str(self): return self._url
	
#-- Compatible
	def compatible(self,x): return Reason()

#-- Satisfiable
	def satisfied(self): 
		g = InternetFileGetter(self._url,'')
		return g.gettable()
	def satisfiable(self): return self.satisfied()

class LaunchBrowser(URLvisible):
	type   = 'launch web browser'
	title  = 'Launch Web Browser'
	action = 'launch web browser'
	
	def satisfiable(self): 
		g = InternetFileGetter(self._url,'')
		return g.gettable()
	def satisfied(self):
		return Reason("Web browser hasn't been launched yet.",not self.acquired)
	def acquire(self):
		launchwebdisplay(self._url)
		return Reason()
	def retract(self): return Reason()
