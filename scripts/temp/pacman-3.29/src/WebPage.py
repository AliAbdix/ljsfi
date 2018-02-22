#
#	Copyright, August 2003, Saul Youssef
#
import os,time,socket
from Base         import *
from PlatformBase import *
#import Platform	

def docstring():
	if os.environ.has_key('PACMAN_LOCATION'):
		return '<a href="'+fullpath('$PACMAN_LOCATION/doc/index.html')+'" target="_blank">Docs</a>'
	else:
		return '<a href="http://physics.bu.edu/pacman/" target="_blank">Docs</a>'

class WebPageBase(IOAble):
	def __init__(self,title=''):
		self.windowtitle = title
		self.title = ''
		self.head = ['<a href="outlook.html"><font color=#000000>Outlook</font></a>'+                   ' | '+  \
			     '<a href="dependence.html"><font color=#000000>Dependence</font></a>'+           ' | '+  \
		             '<a href="packages.html"><font color=#000000>Packages</font></a>'+                 ' | '+  \
		             '<a href="full.html"><font color=#000000>Details</font></a>'+                      ' | '+  \
		             '<a href="domain.html"><font color=#000000>Domain</font></a>'+                     ' | '+  \
		             '<a href="trustedcaches.html"><font color=#000000>Trusted Caches</font></a>'+      ' | '+  \
		             '<a href="registry.html"><font color=#000000>Registry</font></a>'+                 ' | '+  \
		             '<a href="history.html"><font color=#000000>History</font></a>'+                   ' | '+  \
		             '<a href="docs.html"><font color=#000000>Docs</font></a>'+                         ' | '+  \
		             '<a href="about.html" target="_blank"><font color=#000000>About</font></a>' \
			    ]
		self.foot = []
		self.strong     = '#0000FF'
		self.on         = '#003200'
		self.off        = '#000000'
		self.background = '#CFCFCF'
		self.broken     = '#7FFF4D'
		self.backgroundImage = 'sky.gif'
		self.lines      = []
		self.lastline   = ''
	
	def bullet(self,on,err):
		if     on: self.text('<img src="green.gif"   height=15 width=15> ')
		elif  err: self.text('<img src="redstar.gif" height=15 width=15> ')
		else:      self.text('<img src="bullet1.gif" height=15 width=15> ')
	def bulletcross(self):
		self.text('<img src="bulletcross.gif" height=15 width=15> ')
	def text(self,text,q=-1):
		if    q==1: self. onText(text)
		elif  q==0: self.offText(text)
		else      : self.lastline = self.lastline + text
	def bold   (self,text): self.lastline = self.lastline + '<b>'+text+'</b>'
	def onText (self,text): self.lastline = self.lastline + '<font color="'+self.on +'">'+text+'</font>'
	def offText(self,text): self.lastline = self.lastline + '<font color="'+self.off+'">'+text+'</font>'		
	def backgroundText(self,n):
		self.lastline = self.lastline + '<font color="'+self.background+'">'+text+'</font>'
	def cr(self):
		self.lines.append(self.lastline)
		self.lastline = ''
	def strongText(self,text): 
		self.lastline = self.lastline + '<b><font color="'+self.strong+'">'+text+'</font></b>'		
	def strongLink(self,txt,url):
		self.text('<a href="'); self.text(url); self.text('">')
		self.text('<font color='+self.strong+'>')
		self.text(txt)
		self.text('</font>')
		self.text('</a>')
	def link(self,txt,url):
		self.text('<a href="'); self.text(url); self.text('">')
		self.text('<font color=#000000>')
		self.text(txt)
		self.text('</font>')
		self.text('</a>')
	def linkbare(self,txt,url):
		self.text('<a href="'); self.text(url); self.text('">')
		self.text(txt)
		self.text('</a>')
	def linktarget(self,txt,url,target='_blank'):
		self.text('<a href="'); self.text(url); 
		self.text('" target="'); self.text(target); self.text('">')
		self.text('<font color=#000000>')
		self.text(txt)
		self.text('</font>')
		self.text('</a>')
	def linkbaretarget(self,txt,url,target='_blank'):
		self.text('<a href="'); self.text(url); 
		self.text('" target="'); self.text(target); self.text('">')
		self.text(txt)
		self.text('</a>')
	def color(self,text,color):
		self.text('<font color="'+color+'">'+text+'</font>')
	def brokenText(self,text): self.color('<b><i>'+text+'</i></b>',self.broken)
	def append(self,w):
		if self.lastline!='': 
			self.lines.append(self.lastline)
			self.lastline = ''
		for line in w.lines:
			self.lines.append(line)
		self.lastline = w.lastline[:]
#		self.lastline = self.lastline + w.lastline		
	def out(self,path):
		try:
			f = open(path,'w')
			if self.windowtitle!='': f.write('<title>'+self.windowtitle+'</title>\n')
			
			if self.backgroundImage!='':
				f.write('<body bgcolor="'+self.background+'" background="'+self.backgroundImage+'">\n')
			else:
				f.write('<body bgcolor="'+self.background+'">\n')
		
			for line in self.head: f.write(line+'\n')
			if self.title!='':
				f.write('<h2>'+self.title+'</h2>\n')
				f.write('<hr size= 4>\n')
				f.write('<p>\n')
			if self.lastline!='': 
				self.lines.append(self.lastline)
				self.lastline = ''
			for line in self.lines: f.write(line+'\n')
			for line in self.foot:  f.write(line+'\n')
			f.write('</body>\n')
			f.close()
		except (IOError,OSError):
			abort('Error writing to ['+path+'].')

class WebPage(WebPageBase):
	def __init__(self,title=''):
		self.windowtitle = title
		self.title = title
		self.head = ['<a href="outlook.html"><font color=#000000>Outlook</font></a>'+                   ' | '+  \
			     '<a href="dependence.html"><font color=#000000>Dependence</font></a>'+           ' | '+  \
		             '<a href="packages.html"><font color=#000000>Packages</font></a>'+                 ' | '+  \
		             '<a href="domain.html"><font color=#000000>Domain</font></a>'+                     ' | '+  \
		             '<a href="trustedcaches.html"><font color=#000000>Trusted Caches</font></a>'+      ' | '+  \
		             '<a href="registry.html"><font color=#000000>Registry</font></a>'+                 ' | '+  \
		             '<a href="history.html"><font color=#000000>History</font></a>'+                   ' | '+  \
		             '<a href="full.html"><font color=#000000>Details</font></a>'+                      ' | '+  \
		             '<a href="docs.html"><font color=#000000>Docs</font></a>'+                         ' | '+  \
		             '<a href="about.html" target="_blank"><font color=#000000>About</font></a>' \
			    ]
		self.foot = ['<hr size=4>',                                            \
		             '<i>creator:</i> '+getusername()+'<br>',                  \
		             '<i>location:</i> '+os.getcwd()+'<br>',                   \
			     '<i>host:</i> '+socket.gethostname()+'<br>',              \
			     '<i>platform:</i> '+findPlatform()[0]+'<br>',             \
			     '<i>last modified:</i> '+time.ctime(time.time())+' with '+ \
		             '<a href="http://physics.bu.edu/pacman/" target="_blank"><font color=#000000>Pacman version '+version+version_extra+'</font></a><br>\n'
		            ]
		self.strong     = '#0000FF'
		self.on         = '#003200'
		self.off        = '#000000'
		self.background = '#CFCFCF'
		self.broken     = '#A52A2A'
		self.lines      = []
		self.lastline   = ''
		self.backgroundImage = 'sky.gif'
