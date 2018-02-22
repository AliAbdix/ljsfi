#
#	Copyright, Saul Youssef, August 2003
#
from Environment import *
from WebPage     import *

class PackageSite(Environment):
	type    = 'remote package'
	title   = 'Remote Packages'
	action  = 'install remotely'
	
	def __init__(self,package,site):
		self.package = package
		self.package.resolve()
		self.site = site
		self.installed = 0
#-- Set
	def equal(self,x): return self.package==x.package and self.site==x.site
	def str(self): return `self.package`+' at '+`self.site`
	def display(self,indent=0):
		print indent*' '+self.str()
		self.site.display(indent+4)
	def htmlOut(self,w): 
		w.text('<b>')
		self.package.htmlLine(w); w.text(' @ ')
		self.site.htmlOut(w)
		w.text('</b>')
		menubar = get(fullpath('$PAC_ANCHOR/htmls/menubar.w'))
		menubar.text('<b>')
		self.site.htmlOut(menubar); menubar.text('<br>')
		menubar.text('</b>')
		menubar.put(fullpath('$PAC_ANCHOR/htmls/menubar.w'))
		
#-- Satisfiability
	def satisfied(self): 
		if self.installed: return self.site.satisfied()
		else: return Reason("["+`self.package`+"] has not been installed at ["+`self.site`+"].")
	def satisfiable(self): return self.site.satisfiable()
	
#-- Action
	def acquire(self):
		reason = self.site.satisfy()
		if reason.ok(): reason = self.site.addPackage(self.package)
		if reason.ok(): reason = self.site.satisfy()
		self.installed = 1
		return reason
		
	def retract(self): 
		self.installed = 0
		return self.site.removeInstallation()

