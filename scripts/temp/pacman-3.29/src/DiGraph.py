#
#	DiGraph
#
from Base    import *
from WebPage import *
		
class DiGraph:
	def __init__(self,pairs=[]): self.__pairs = pairs[:]
	def __repr__(self): return `self.__pairs`
	def display(self,indent=0):
		ms = [p[0] for p in self.__pairs]
		ms.sort()
		for m in ms: print indent*' '+m
	def pairs(self): return self.__pairs
	def elements(self):
		el = []
		for p in self.__pairs:
			if el.count(p[0])==0: el.append(p[0])
			if el.count(p[1])==0: el.append(p[1])
		return el
	def subs(self,x):
		subs = []
		for p in self.__pairs:
			if p[0]==x: subs.append(p[1])
		return subs
	def add(self,x,y): self.__pairs.append([x,y])
	def path(self,x,y): return x==y or transitiveClosure(x,y,self.__pairs)

	def htmlOut(self,w):
		w.text('<ul>'); w.cr()
		for p in self.__pairs:
			w.text('<li> '+p[0]+' => '+p[1]); w.cr()
		w.text('</ul>'); w.cr()

