#
#	Copyright, Saul Youssef, December 2003
#
from Abort import *
from StringAttr import *
import Source
import Package 
import TrustedCaches
from Registry import *

class InstalledPackage(StringAttr):
	type   = 'already installed package'
	title  = 'Already Installed Packages'
	action = 'check for already installed package'
	
	def satisfied(self):
		reason = Reason()
		try:
			path = fullpath('$PAC_ANCHOR/E/E')
			E = get(path)
			package = Package.Package(self.value)
			reason,p = E.getInstalledPackage(package.name)
			if reason.ok() and (package.cachename=='' or TrustedCaches.cacheNameEq(package.cachename,p.cachename)):
				code = Source.Source(package.guardstring); code.parse()
				guard = code.evaluate()
				if not p.satisfies(guard):
					reason = Reason("Installation contains ["+package.name+"] but it does not satisfy ["+package.guardstring+"].")
			else:
				reason = Reason("You must install ["+self.value+"] first.")
		except AbortException,message:
			reason = Reason("Can't find installation environment in ["+path+"].")
			
		return reason
		
	def satisfiable (self): return self.satisfied()
	def acquire     (self): return self.satisfied()
	def retract     (self): return Reason()

