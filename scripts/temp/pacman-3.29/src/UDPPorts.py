#
#	Copyright Saul Youssef, June 2003
#
from Environment  import *
from scanPorts    import *

class UDPPorts(Environment):
	type = 'udpPorts'
	action = 'test UDP ports'
	title = 'UDP Ports'
	
	def __init__(self,portFirst,portLast=0,host=socket.gethostname()):
		self.__host  = host
		self.__first = portFirst
		self.__last  = portLast
		if self.__last == 0: self.__last = self.__first

#-- Set
	def equal(self,upr): return self.__host  == upr.__host  and \
	                            self.__first == upr.__first and \
				    self.__last  == upr.__last 
	def str(self): return '['+`self.__first`+','+`self.__last`+'] to '+self.__host

#-- Compatible	
	def compatible(self,upr): return Reason()

#-- Satisfiable
	def satisfied(self): return Reason(`self`+" has not been tested yet.",not self.acquired)
#	def satisfiable(self): return Reason()
	def acquire(self):
		reason = Reason()
		r = range(self.__first,self.__last+1)
		notopen = []
		for port in r:
			verbo.log('tcp','Checking UDP port '+`port`+'...')
			if not checkUDPPort(self.__host,port): notopen.append(port)
			
		if len(notopen)>0: reason.reason('UDP ports '+`notopen`+' are not open to '+self.__host+'.')
		return reason
	def retract(self): return Reason()
			
