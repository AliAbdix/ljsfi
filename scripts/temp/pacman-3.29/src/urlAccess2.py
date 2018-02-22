#
#     Get list of remote files
#
import urllib2
from sgmllib import SGMLParser
from Base import *

class URLHelper(SGMLParser):
	def reset(self):
		SGMLParser.reset(self)
		self.urls = []
		
	def start_a(self,attrs):
		href = [v for k, v in attrs if k=='href']
		if href:
			self.urls.extend(href)
import re

def urlFiles(path,dirs=0):
	reason = Reason()
	filenames = []
	verbo.log('http','About to open url directory ['+path+']...')
	try:
		path2 = re.sub('(?<!:)/+','/',path)
		opener = urllib2.build_opener()
		if allow('no-http-cache'): opener.addheaders = [('Pragma', 'no-cache')]
		sock = opener.open(path2)
		text = sock.read()
		sock.close()
#	except AssertionError:
#		abort("Internal Python error attempting to access ["+path+"].")
	except KeyboardInterrupt:
		reason = Reason("Download interrupted by ^C.")
	except urllib2.URLError, e:
		msg = "Can't access [%s]" % path
		if hasattr(e, 'reason'):
			#some common e.reason values:
			#	(-2, 'Name or service not known')
			#	(113, 'No route to host')
			try: msg += ": [%s]" % e.reason[1]
			except IndexError: pass
		if hasattr(e, 'code') and hasattr(e, 'msg'):
			#(in this case e is HTTPError, a subclass of URLError)
			#some common *e.code, e.msg) values:
			#	(404, 'Not Found')
			#	(403, 'Forbidden')
			#	(500, 'Internal Server Error')
			msg += ": HTTP error [%s, %s]" % (e.code, e.msg)
		msg += "."
		reason = Reason(msg)
	except:
		#(could be socket.error)
		reason = Reason("Can't access ["+path+"].")
	
	if reason.ok():
		parser = URLHelper()
		parser.feed(text)
		parser.close()
		
		for url in parser.urls:
			if len(url)>0 and not ( url[0]=='/' or contains(url,'?') or contains(url,'=') ):
				if url[-1]=='/':
					if dirs: filenames.append(url)
				else:
					filenames.append(url)
	return reason,filenames
