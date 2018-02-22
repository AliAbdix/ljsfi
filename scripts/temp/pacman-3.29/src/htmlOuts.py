#
#	Copyright, August 2003, Saul Youssef
#
from Environment    import *
from History        import *
from Domain         import *
from WebPage        import *
from TrustedCaches  import *
from Base           import *
from Selector       import *
from Platform       import *
from Registry       import *
from htmlOutlook    import *

import Selector,Collections

def equivPackage(p,q): return p.name==q.name
def leqPackage  (p,q): return p.name<=q.name
	
subd = Collections.SubDisplay()

dep_message_saved = {}

class CountPackages(Application):
	def __init__(self): self.count = 0
	def __call__(self,E): 
		if E.title=='Packages': self.count = self.count + 1
		return Reason()
		
def subdisplay(E):
	if           E.type=='package': return 1
	elif  hasattr(E,'__getitem__'): return exists(E,lambda e: subdisplay(e))
	else:                           return 0
		
class Dephack:	
	def __init__(self,dep_total,npackages):
		self.dep_processed = 0
		self.dep_total     = dep_total
		self.verb  = verbo('web') and npackages>10

	def htmlDeps(self,E,w,base,first=0,depth=999999):
		if E.title=='Packages':
			if self.verb: 
				message = 'Package ['+E.name+'] written to dependency page...'
				if not dep_message_saved.has_key(message):
					print 'Package ['+E.name+'] written to dependency page...'
					dep_message_saved[message] = ''
			if not first: w.text('<br>')
			if not base.has_key(E._hash): abort('Hash error for package ['+E.name+'] in htmlOuts.')
			w.append(base[E._hash][4])
			w.append(base[E._hash][5])
			self.dep_processed = self.dep_processed + 1
			if exists(E,lambda e: subdisplay(e)):
				self.htmlDepsBase(E,w,base,depth-1)
		elif E.type=='AND':
			if exists(E,lambda e: subdisplay(e)):
				if not first: w.text('<br>')
				w.text('AND')
				self.htmlDepsBase(E,w,base,depth)
		elif E.type=='OR':
			if exists(E,lambda e: subdisplay(e)):
				if not first: w.text('<br>')
				w.text('OR')
				self.htmlDepsBase(E,w,base,depth)

	def htmlDepsBase(self,E,w,base,depth=999999):
		w.cr()
		E2 = filter(lambda e: e.title=='Packages' or e.type=='AND' or e.type=='OR',E)
		count = 0
		w.text('<ul>')
		first = 1
		lastlength = 0
		if depth>0:
			for e in E2:
				self.htmlDeps(e,w,base,first or lastlength>0,depth-1)
				lastlength=exists(e,lambda ee: subdisplay(ee))
				first = 0
		else:
			w.strongText('...etc...')
		w.text('</ul>')
		w.cr()
		
def htmlOuts(E,r=Reason()):
	if not os.path.isdir('E/htmls'):
		print 'Repairing missing E/htmls directory...'
		execute('mkdir -p E/htmls').require()
		execute('cp $PACMAN_LOCATION/htmls/*.gif htmls').require()
		
	if quiet('web'):
		pass
	elif os.path.isdir('E/htmls'):
		execute('rm -r -f E/htmls/menubar.w')
		
		i = open('E/htmls/index.html','w')
		i.write('<html>\n')
		i.write('<head><title>Pacman Environment at '+os.getcwd()+'</title></head>\n')
		i.write('<frameset cols="75%,25%">\n')
		i.write('<frame src="outlook.html" name="mainwindow">\n')
		i.write('<frame src="menubar.html"     name="sidemenu">\n')
		i.write('</frameset>\n')
		i.write('</html>\n')
		i.close()
#-- Menu
		menu = WebPage()
		menu.head = []
		menu.foot = []
		menu.put('E/htmls/menubar.w')
		
		H = Historian(E.getHistory())
	
		countPackage = Collections.CountPackage()
		numPackages = countPackage(E)
		
		pwp = Package.PackageWebPages()
		if numPackages>10 and verbo('log'): print 'Preparing web pages...'
		E.apply(pwp)
#		subd.gotten = copy.deepcopy(pwp.pages)
		
#		if verbo('web') and len(pwp.pages)>100: m = Meter(len(pwp.pages)-1,'Writing package html...')
		count = 0
		pp = WebPage('Packages')
		keys = pwp.pages.keys()
		keys.sort()
		for key in keys:
			count = count + 1
			
			qq = WebPage(pwp.pages[key][2].title)
			qq.append(pwp.pages[key][4])
			qq.append(pwp.pages[key][2])
#			qq.out('E/htmls/'+key+'.html')
			qq.out('E/htmls/'+`abs(key.__hash__())`+'.html')
			
			pp.append(pwp.pages[key][4])
			pp.append(pwp.pages[key][3])
			pp.text('<br>')
		if len(keys)>0: pp.text('<br>')
		pp.out('E/htmls/packages.html')
		
		if verbo('web') and len(pwp.pages)>0: 
			print '    '+`len(pwp.pages)`+' packages in the installation...'
			print '    '+`numPackages`+' nodes in the dependency tree...'
		
		deps = WebPage('Dependence')
		dephack = Dephack(numPackages,len(pwp.pages))
		deps.text('<ul>')
		processed = 0
		count = 0
		depthswitch,maxstring = switchpar('webdepth')
		if depthswitch:   maxdepth=int(maxstring)
		else:             maxdepth=6
		for e in E: 
			count = count + 1
			w = WebPage()
			dephack.htmlDeps(e,w,pwp.pages,1,maxdepth)
			deps.append(w)
			if count!=len(E):
				deps.text('<br>')
				deps.text('<br>')
		deps.text('</ul>')
		deps.out('E/htmls/dependence.html')
	
		full = WebPage('Environment Details')
		E.bullet(full)
		E.htmlOut(full)
		full.out('E/htmls/full.html')
	
		hist = WebPage('History')
		H.htmlOut(hist)
		hist.out('E/htmls/history.html')
	
		dom = WebPage('Domain')
		domainHtml(E,dom)
		dom.out('E/htmls/domain.html')
		
		doc = WebPage('Pacman '+version+version_extra+': <i>Software Environment Computing</i>')
		doc.windowtitle = 'Pacman Documentation'
		doc.text('<p>' ); doc.cr()
		doc.text('<h3>'); doc.cr()
		doc.text('<ol>'); doc.cr()
		doc.text('<li>'); doc.link('Overview','doc/overview.html'); doc.cr()
		doc.text('<li>'); doc.link('Main concepts, glossary','doc/main-concepts.html'); doc.cr()
		doc.text('<li>'); doc.link('Tutorials','doc/tutorials.html'); doc.cr()
		doc.text('<ol>'); doc.cr()
		doc.text('<li>'); doc.link('Getting started I','doc/getting-started.html'); doc.cr()
		doc.text('<li>'); doc.link('Getting started II','doc/getting-started-II.html'); doc.cr()
		doc.text('<li>'); doc.link('Getting started III','doc/getting-started-III.html'); doc.cr()
		doc.text('<li>'); doc.link('Getting started IV','doc/getting-started-IV.html'); doc.cr()
#		doc.text('<li>'); doc.link('Making and using snapshots','doc/snapshots.html'); doc.cr()
		doc.text('<li>'); doc.link('Package specification, dependency, versions','doc/packages-and-dependency.html'); doc.cr()
		doc.text('<li>'); doc.link('Modifying the registry','doc/registry.html'); doc.cr()
		doc.text('<li>'); doc.text('Multi-site environments','doc/multiSite.html'); doc.cr()
		doc.text('</ol>'); doc.cr()
		doc.text('<li>'); doc.link('The Language','doc/language.html'); doc.cr()
		doc.text('<ol>');
		doc.text('<li>'); doc.link('Basic commands','doc/basic-shell-like-commands.html')
		doc.text('<li>'); doc.link('Files and directory manipulation','doc/files-and-directory-manipulation.html')
		doc.text('<li>'); doc.link('Questions, messages, email','doc/questions-messages-email.html')
#		doc.text('<li>'); doc.link('Packages and dependency','doc/packages-and-dependency.html')
		doc.text('<li>'); doc.link('Testing system properties','doc/system-properties.html')
		doc.text('<li>'); doc.link('Multi-user installations and remote sites','doc/multi-user-and-remote-installations.html')
		doc.text('<li>'); doc.link('Accounts, Groups, SSH and Globus Access, Workspaces','doc/ssh-and-globus-access-workspaces.html')
		doc.text('<li>'); doc.link('Compatibility with Pacman 2','doc/compatibility.html')
		doc.text('</ol>');
		doc.text('<li>'); doc.text('How to make and manage your own caches','doc/cacheManager.html'); doc.cr()
		doc.text('<li>'); doc.link('FAQ','doc/FAQ.html'); doc.cr()
		doc.text('<li>'); doc.link('Release Notes','doc/release-notes.html'); doc.cr()
		doc.text('<li>'); doc.link('Platforms','platforms.html'); doc.cr()
		doc.text('</ol>')
		doc.text('</h3>'); doc.cr()
		doc.out('E/htmls/docs.html')

#-- Trusted caches
#		verbo.log('web','Computing trusted caches...')
		caches = getTrustedCaches()
		cp = WebPage('Trusted Caches')
		caches.htmlOut(cp)
		cp.out('E/htmls/trustedcaches.html')
#-- Registry
#		verbo.log('web','Computing registry...')
		reg = WebPage('Registry')
		registry.htmlOut(reg)
		reg.text('<p>')
		reg.out('E/htmls/registry.html')
		
		wap = Collections.WebApplication()
		E.pl.apply(wap)
#-- Outlook
#		if len(pwp.pages)>10 and verbo('web'): print 'Outlook page...'
		preview = WebPage('Outlook')
		htmlOutlook(E.pl,r,preview,pwp,len(pwp.pages),numPackages,wap)
		preview.out('E/htmls/outlook.html')
#-- Platforms 
#		verbo.log('web','Platform page...')
		if not os.path.exists('E/htmls/platforms.html'):
			plat = WebPage('Platforms')
			platformHtmlOut(plat)
			plat.out('E/htmls/platforms.html')
		
		menu = get('E/htmls/menubar.w')
		menu.out('E/htmls/menubar.html')
	
		if len(wap.remotes)==0: execute('cp E/htmls/outlook.html E/htmls/index.html').require()
	else:
		print "Warning.  Can't find E/htmls subdirectory.  No html output written..."
