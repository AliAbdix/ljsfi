import sys, socket
from Base import *

def tryServerSocket(port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	msg = ''
	try:
		sock.bind((socket.gethostname(),port))
		sock.listen(5)
	except socket.error, msg:
		if msg=='': msg = "Can't bind to port ["+`port`+"]."
	sock.close()
	return msg		

def checkTCPPort(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        return 1
    except socket.error, reason:
        return 0

def checkUDPPort(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect((host, port))
        return 1
    except socket.error, reason:
        return 0
    
def getOpenPorts(hostname):

    port_range = range(65536)
    TCPOpenPorts = []
    UDPOpenPorts = []
    for port in port_range:
        if checkTCPPort(hostname, port):
            print port
            TCPOpenPorts.append(port)
        #if checkUDPPort(hostname, port):
            #UDPOpenPorts.append(port)
    return [TCPOpenPorts, UDPOpenPorts]

if __name__ == "__main__":
    if len(sys.argv) == 2:
        print "Open ports:",  getOpenPorts(sys.argv[1])
    else:
        print "Usage: python scan hostname"
 
