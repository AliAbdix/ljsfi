#
#	Copyright Saul Youssef, December 2003
#
#       Major mods by John Brunelle.
#       Minor additional mods by Saul
#
from Base      import *
from FloatAttr import *
from Platform  import *

def timeDiff(host='tick.mit.edu',timeout='10.0'):
	return Reason('timeErrorMaximum is no longer available'),0.0  # this doesn't work anymore S.Y.
	#adapted from Python Cookbook by Martelli, Ravenscroft, & Asher (O'Reilly)
	import socket, struct, time

	client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
#	client.settimeout(10.0)    # not available in Python 2.2.3  S.Y.

	data = '\x1b' + 47 * '\0'		#48-byte UDP datagram to query timeserver

	before_sys_time = time.time()
	try:
		verbo.log('http','Sending UDP datagram to ['+host+']...')
		client.sendto(data, (host, 123))
		data, address = client.recvfrom(1024)
	except:
		data = None
		return Reason('NTP timeserver query error.'),0.0
	after_sys_time = time.time()
	sys_time =  (before_sys_time + after_sys_time)/2.0

	ntp_time = struct.unpack('!12I', data)[10]	#server answers with 48-byte UDP datagram of 12 network-order longwords (4 bytes each)
							#we only want the 11th longword, the time in seconds
	ntp_time -= 2208988800L				#time returned by timeserver is measured from a different epoch than python's 1970-based time
							#subtract this number from the returned time in order to be consistent

	dTime = sys_time - ntp_time	#(so a negative number means the system is slow)

	return Reason(),dTime

class TimeErrorMaximum(FloatAttr):
	type   = 'time error maximum'
	title  = 'Time Error Maximum'
	action = 'time error maximum'

	def str(self): 
		if self.acquired:
			s = '%2.2f' % self._dtime
			return '['+`self.value`+'] seconds.  The actual system time is off by ['+s+'] seconds compared to [tick.mit.edu].'
		else:
			return `self.value`+' seconds.'

	def satisfied(self): return Reason("["+self.str()+"] has not been tested yet.",not self.acquired)

	def acquire(self):
		reason,dTime = timeDiff()
		self._dtime = dTime
		if reason.ok():
#			s = '%g' % dTime
			s = '%2.2f' % dTime
			if abs(dTime)>abs(self.value): reason = Reason('System clock is off by ['+s+'] seconds.  This exceeds maximum of ['+`self.value`+'] seconds.')
		return reason
#	def satisfiable (self): return Reason()
	def retract     (self): return Reason()

if __name__=='__main__':
	print timeDiff()
