#
#	Copyright Saul Youssef, June 2003
#
#     Removed non-standard switch on ps.  S.Y. Feb. 2006
#
from Environment import *
import os

def processList():
	processes = []
	try:
		lines = os.popen('ps -eal').readlines()
		for line in lines:
			line.replace('\t',' ')
			p1 = line.split(' ')
			p2 = []
			for p in p1:
				if len(p)>0: p2.append(p)
			if len(p2)>0 and len(p2[-1])>0:
				processes.append(p2[-1][:-1])
	except:
		raise
		print 'Ignoring error executing [ps -eal]...'
	return processes

def processListOld():
	try:
		lines = os.popen('ps -ealf').readlines()
	except:
		print "[ps -ealf] fails to execute."
		lines = []
	plist = []
	first = 1
	for line in lines:
		if len(line)>1:	
			items = []
			item  = ''
			x = line[:-1]+' '
			while len(x)>0:
				xx = x[0]; x = x[1:]
				if not xx in string.whitespace:
					item = item+xx
				else:
					if len(item)>0: items.append(item)
					item = ''
			if len(items)>0 and not items[14]=='CMD':
				plist.append(os.path.basename(items[14]))
	return plist

class RunningProcess(Environment):
	type = 'runningProcess'
	title = 'Running Processes'
	
	def __init__(self,pname): self.__pname = pname
#-- Set
	def equal(self,rp): return self.__pname==rp.__pname
	def str(self):      return self.__pname
	
#-- Compatible
	def compatible(self,g): return Reason()

#-- Satisfiable
	def satisfied(self): return Reason('Process ['+self.__pname+'] has not been tested.',not self.acquired)
	def acquire(self): 
		if verbo('processes'):
			print 'Checking for running process ['+self.__pname+']...'
			for x in processList():
				if x==self.__pname:
   					print '------> ',x,' <---------- GOT ONE'
				else:
					print '        ',x
		if self.__pname in processList():
			return Reason()
		else:
			return Reason('Process ['+self.__pname+'] is not running.')
	def retract(self): return Reason()
	def verify(self): return self.satisfy()

	def satisfiable(self): return Reason()
	

			
