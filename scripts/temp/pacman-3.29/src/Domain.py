#
#	Copyright, Saul Youssef, August 2003
#
from Environment import *
from WebPage     import *
import Collections

excluded = ['Packages','Cat','URLs','Current Directories','Choices','Unsetenvs','Change Usernames','User Messages',
  'File Copy Speeds','Moves','File Exists Onces','ORs','ANDs','Temporary Environment Variable']

def domainHtml(E,w):
	def equiv(a,b): return a.title==b.title
	
#	domain = E.pl.collect(lambda e: e.acquired)
	domain = E.pl.collect(Collections.AcquiredCollection())
	
	dl = []
	for dom in domain: dl.append(dom)
	
	cl = Clusters(dl)
	classes = cl.cluster(equiv)
	w.text('<title>Domain</title>'); w.cr()
	
	def le(c1,c2): return c1[0].title <= c2[0].title
	sort(classes,le)
	
	for c in classes:
		if not c[0].title in excluded:
			w.text('<h2>'+c[0].title+'</h2>'); w.cr()
			w.text('<ul>'); w.cr()
			for x in c: 
				x.bullet(w); w.text(x.str())
				w.text('<br>'); w.cr()
			w.text('</ul>'); w.cr()
