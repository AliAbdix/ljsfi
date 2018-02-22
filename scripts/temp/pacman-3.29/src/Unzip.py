#
#	Copyright, Saul Youssef, September, 2003
#
from Environment import *
from Execution   import *

class Unzip(Environment):
	type   =  'unzip'
	title  =  'Unzips'
	action =  'unzip'

	def __init__(self,filename):
		self.filename = filename
		if   tail(self.filename,'.gz'):  self.suffix = '.gz'
		elif tail(self.filename,'.Z' ):  self.suffix = '.Z'
		elif tail(self.filename,'.z' ):  self.suffix = '.z'
		elif tail(self.filename,'.tgz'): self.suffix = '.tgz'
		else:                            self.suffix = ''
		
	def   str(self  ): return self.filename
	def equal(self,x): return self.filename==x.filename
	
#	def satisfied  (self): return Reason("["+`self`+"] hasn't been executed.",not self.acquired)
	def satisfiable(self): 
		if   not fileInPath('gunzip').ok(): return Reason("[gunzip] is not in your path.  Can't unzip.")
		elif  self.suffix=='':              return Reason("["+`self`+"] has the wrong suffix to unzip.")
		else:                               return Reason()
	def acquire(self):
		reason = Reason()
		if os.path.exists(fullpath(self.filename)):
			self.filename = fullpath(self.filename)
			verbo.log('tar','About to unzip ['+self.filename+']...')
			reason = ask.re('tar','OK to unzip ['+self.filename+']?')
			if reason.ok(): reason = execute('gunzip '+self.filename)
			if reason.ok():
				if   tail(self.filename,'.gz'):  self.unzip = self.filename[:-3]
				elif tail(self.filename,'.Z' ):  self.unzip = self.filename[:-2]
				elif tail(self.filename,'.z' ):  self.unzip = self.filename[:-2]
				elif tail(self.filename,'.tgz'): self.unzip = self.filename[:-3]+'tar'
				else:    abort('Error in Unzip.')
				
				if os.path.exists(fullpath(self.unzip)):
					self.unzip = fullpath(self.unzip)
				else:
					reason = Reason('Unzipped file ['+self.unzip+'] is missing.')
			else:
				reason = Reason("Unzipping ["+self.filname+"] returns with an error code.")
		else:
			reason = Reason("["+self.filename+"] is missing.  Can't unzip.")
		return reason
		
	def retract(self):
		reason = Reason()
		if os.path.exists(self.unzip):
			verbo.log('tar','About to zip ['+self.unzip+']...')
			reason = ask.re('tar','OK to zip ['+self.unzip+']?')
			if reason.ok(): reason = execute('gzip '+self.unzip)
			if reason.ok(): reason = execute('mv '+self.unzip+'.gz'+' '+self.filename)
		else:
			reason = Reason("["+self.unzip+"] unzipped file is missing.")
		return reason
		
