#
#	Copyright Saul Youssef, June 2003
#
from Base         import *
from WebPage      import *
from Environment  import *
import time

class Historian(Set,PrintOut,HtmlOut,IOAble):
	def __init__(self,dom=[]): self.__dom = dom[:]

#-- Set
	def __eq__(self,x): return self.__dom == x.__dom
	def __repr__(self): return `self.__dom`
			
	def extend(self,h): self.__dom.extend(h.__dom)
			
	def htmlOut(self,w):
		w.text('<ol>'); w.cr()
		for l in self.__dom:
			if len(l)>4:
				tim,action,location,username,value = l[0],l[1],l[2],l[3],l[4]
				w.text('<li><b>')
			
				if   len(value)>8 and value[:8]=='package ': w.strongText(value)
				elif len(value)>8 and value[:8]=='% pacman': w.strongText(value)
				elif  action== 'acquired': w.text(value)
				elif  action=='retracted': w.text(value)
				else: w.text(value,0)

				w.text('</b> '+action+' at <b>'+os.path.basename(location)+'/'+'</b>, by '+username+', at time <i>'+tim+'</i>'); w.cr()
		w.text('</ol>');   w.cr()
		w.text('</body>'); w.cr()
