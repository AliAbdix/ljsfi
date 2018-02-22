#
#	Copyright February 2004, Saul Youssef
#
from Base        import *
from Environment import *
from Execution   import *
import UniversalAccess,Package,Source,TrustedCaches
import time

save_remotes = {}

class MonitorRemotePackage(Environment):
	type   = 'monitor remote package'
	title  = 'Monitor Remote Package'
	action = 'monitor remote package'
	
	def __init__(self,packageSpec,universalAccess):
		self.packageSpec = packageSpec
		self.package = Package.Package(packageSpec)
		self.access = UniversalAccess.UniversalAccess(os.path.join(universalAccess,'E'))
		code = Source.Source(self.package.guardstring); code.parse()
		self.guard = code.evaluate()
		
	def str(self):     return self.package.str()+' @ '+`self.access`
	def equal(self,x): return self.package==x.package and self.access==x.access
	
	def identity(self): return self.package.str()+' @ '+`self.access`
	
	def getObjE(self): 
		iden = self.identity()
		if not save_remotes.has_key(iden): save_remotes[iden] = self.access.getObj('E')
		return save_remotes[iden]

	def getRemoteHits(self):
		reason = Reason('Remote location ['+`self.access`+'] is inaccessible.',not self.access.access())
		if reason.ok(): reason,E = self.getObjE()
		hits = []
		if reason.ok():
			reason = Reason('Unable to access remote package ['+`self`+'].',not E.type=='installation')
			if reason.ok():
				hits = []
				if E.hasPackage(self.package.name):
					for status,p in E.pl._packages:
						if p.name==self.package.name: hits.append((status,p,))
				else:
					reason = Reason('Remote site at ['+`self.access`+'] does not contain ['+self.package.name+'].')
		return reason,hits
		
	def getRemotePackage(self):
		reason,hits = self.getRemoteHits()
		pac = Package.Package()
		if reason.ok():
			got_one = 0
			pac = Package.Package()
			reason = Reason("Remote installation ["+`self`+"] does not contain ["+self.package.str()+"] at the top level.")			
			for status,p in hits:
				if p.name==self.package.name and \
				   (self.package.cachename=='' or TrustedCaches.cacheNameEq(self.package.cachename,p.cachename)) and \
				   p.satisfies(self.guard):
					reason = status.installed
					pac = p
					break
		return reason,pac
		
	def satisfied(self):
		reason,pac = self.getRemotePackage()
		return reason
		
	def satisfiable(self): return Reason()
	def     acquire(self): return self.satisfied()
#	def     retract(self): return Reason("Monitoring only.  Can't uninstall at ["+`self`+"].")
	def     retract(self): return Reason()
	
	def satisfies(self,E):
		got_one = 0
		reason,hits = getRemotePackages(self)
		if reason.ok():
			for status,p in hits:
				if p.name==self.package.name and p.satisfies(self.guard) and p.satisfies(E): got_one = 1; break
		return got_one
		
	def uniFile(self): return str2file(`self.package`+'_'+`self.access`)

	def htmlOut(self,w):
		w.text('monitor ')
		w.text('<b>')
		self.htmlLine(w)
		w.text('</b>')
		reason,p = self.getRemotePackage()

		menubar = get(fullpath('$PAC_ANCHOR/E/htmls/menubar.w'))
		menubar.text('<b>')
		
		self.bullet(menubar)
		ident = `abs(p.hash().__hash__())`
		target = os.path.join(fullpath('$PAC_ANCHOR/E/htmls'),ident,ident+'.html')
		if reason.ok(): 
			menubar.linktarget('<font color="0000FF">'+self.packageSpec+'</font>',target)
			menubar.text(' @ '+`self.access`)
		else:                      
			menubar.text('<font color="0000FF">'+self.packageSpec+'</font>'+' @ '+`self.access`)
		menubar.text('<br>')
		menubar.text('</b>')
		menubar.put(fullpath('$PAC_ANCHOR/E/htmls/menubar.w'))		

	def htmlLine(self,w):
		reason,p = self.getRemotePackage()
		if reason.ok():
			ident = `abs(p.hash().__hash__())`
			u = UniversalAccess.UniversalAccess(os.path.join(self.access.location,'htmls'))
			subdir = fullpath(os.path.join('$PAC_ANCHOR/E/htmls',ident))
#			subdir = fullpath(os.path.join('$PAC_ANCHOR/E/htmls',`time.time()`))
			execute('rm -r -f '+subdir).require()
			execute('mkdir '+subdir).require()
			u.getDirectory(subdir,lambda n: tail(n,'.html')).require()
			execute('cp $PAC_ANCHOR/E/htmls/*.gif '+subdir).require()
			execute('cp '+os.path.join('$PAC_ANCHOR/E/htmls',subdir,'strat.gif')+' '+os.path.join('$PAC_ANCHOR/E/htmls',subdir,'sky.gif')).require()
#			w.linktarget('<font color="0000FF">'+self.packageSpec+'</font>',os.path.join(p._hash,p._hash+'.html'))
			w.linktarget('<font color="0000FF">'+self.packageSpec+'</font>',os.path.join(ident,ident+'.html'))
			w.text(' @ '+`self.access`)
		else:
			w.text('<font color="0000FF">'+self.packageSpec+'</font>')
			w.text(' @ '+`self.access`)
		verbo.log('web',self.errorMessage(w))
		
