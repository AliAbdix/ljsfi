#
#	Copyright Saul Youssef, June 2003
#
from Environment  import *
from scanPorts    import *

class UsePortNumber(Environment):
	type   = 'bind a socket to port'
	action = 'test if a socket can be bound to a given port'
	title  = 'Bind a Socket to Port'
	
	def __init__(self,port):
		self._port = port
		
	def equal(self,x): return self._port == x._port
	def str(self): return `self._port`
	
	def satisfied  (self): return Reason(`self`+" has not been tested yet.",not self.acquired)
#	def satisfiable(self): return Reason()
	
	def acquire(self):
		verbo.log('tcp','Try binding a socket to TCP port '+`self._port`+'...')
		msg = tryServerSocket(self._port)
		if msg == '': r = Reason()
		else:         r = Reason(msg)
		return r
		
	def retract(self): return Reason()
	def verify (self): return self.acquire()

class TCPPorts(Environment):
	type = 'tcpPorts'
	action = 'test TCP port range'
	title = 'TCP Port Ranges'
	
	def __init__(self,portFirst,portLast=0,host=socket.gethostname()):
		self.__host  = host
		self.__first = portFirst
		self.__last  = portLast
		if self.__last == 0: self.__last = self.__first
#-- Set
	def equal(self,tpr): return self.__host  == tpr.__host  and \
	                            self.__first == tpr.__first and \
				    self.__last  == tpr.__last 
	def str(self): return '['+`self.__first`+','+`self.__last`+'] to '+self.__host

#-- Compatible	
	def compatible(self,tpr): return Reason()

#-- Satisfiable
	def satisfied  (self): return Reason(`self`+" has not been tested yet.",not self.acquired)
#	def satisfiable(self): return Reason()
	
	def acquire(self):
		reason = Reason()
		r = range(self.__first,self.__last+1)
		notopen = []
		for port in r:
			verbo.log('tcp','Checking TCP port '+`port`+'...')
			if not checkTCPPort(self.__host,port): notopen.append(port)
			
		if len(notopen)>0: reason.reason('TCP ports '+`notopen`+' are not open to '+self.__host+'.')
		return reason

	def retract(self): return Reason()	
	
