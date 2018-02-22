#
#	FileGetter, Copyright Saul Youssef, May 2003.
#
import os,shutil,urllib2,urlparse,time,httplib
from Base import *

class FileGetter(Set):
	def get(self,target_directory): abort('Missing get in FileGetter class.')
	def getFile(self):              abort('Missing getText in FileGetter class.')
	def getAsFile(self):            abort('Missing getAsFile in FileGetter class.')
	def gettable(self):             abort('Missing gettable in FileGetter.')
	
class LocalFileGetter(FileGetter):
	def __init__(self,basedirectory,file): self.directory,self.filename = basedirectory,file
	def __repr__(self): return 'File Getter: ['+os.path.join(self.directory,self.filename)+']'		
	def __eq__(self,g): return fullpath(self.directory)==fullpath(g.directory) and self.filename==g.filename
		
	def gettable(self):
		r = Reason()
		if not os.access(os.path.join(fullpath(self.directory),self.filename),os.R_OK):
			r.reason("Can't find ["+os.path.join(fullpath(self.directory),self.filename)+"].")
		return r
		
	def getFile(self):
		r = Reason()
		full = os.path.join(fullpath(self.directory),self.filename)
		try:
			f = open(full,'r')
			file = f.readlines()
			f.close()
		except (IOError, OSError):
			r.reason("Can't read ["+full+"].")
			file = []
		return r,file
		
	def getAsFile(self):
		r = Reason()
		full = os.path.join(fullpath(self.directory),self.filename)
		try:              
			f = open(full,'r')
		except (IOError, OSError):   
			r.reason("No read access to ["+full+"].")
			f = None
		return r,f
		
	def get(self,target_directory):
		r = Reason()
		if os.path.isdir(target_directory):
			full = os.path.join(fullpath(self.directory),self.filename)
			if os.path.exists(full):
				try: 
					shutil.copyfile(full,os.path.join(target_directory,self.filename))
				except (IOError, OSError):
					removeFile(os.path.join(target_directory,self.filename))
			else:
				r = Reason("Can't copy ["+full+"] to ["+target_directory+"].  File doesn't exist.")
		else:
			r.reason("Can't copy ["+full+"] to ["+target_directory+"]. Directory doesn't exist.")
		return r
			
	def source(self): return self.directory

def er(file,url):
	if file=='':
		return "Can't reach ["+urlparse.urlparse(url)[1]+"] via the internet."
	else:
		return "Can't reach ["+urlparse.urlparse(url)[1]+"] via the internet.  Can't download ["+file+"]."

import re

class InternetFileGetter(FileGetter):
	def __init__(self,baseURL,file):
		self.filename = file
		self._maxtry = httpGetRetries() + 1
		self._pause  = httpGetPause  ()
		if len(baseURL)>0 and not baseURL[-1]=='/': self.url = urlparse.urljoin(baseURL+'/',file)
		else:                                       self.url = urlparse.urljoin(baseURL,    file)
		self.url = re.sub('(?<!:)/+','/',self.url)
		
	def __repr__(self): return 'file Getter: ['+self.url+']'
		
	def __eq__(self,g): return self.filename==g.filename and self.url==g.url
	
	def gettable(self):
		r = Reason()
		verbo.log('http','Attempting to open ['+self.url+']...')
		ntry = 0
		while ntry<self._maxtry:
			ntry = ntry + 1
			r = Reason()
			try:
				f = urllib2.urlopen(self.url)
				line = f.readline()
				f.close()
			except (IOError, OSError):
				r = Reason(er(self.filename,self.url))
			if not r.ok():
				if not ntry==self._maxtry:
					verbo.log('retry','Attempt to open ['+self.url+'] has failed.  Retrying '+`ntry`+'/'+`self._maxtry-1`+'...')
					time.sleep(self._pause)
			else:
				break
		return r

	def getAsFile(self):
		r = Reason()
		verbo.log('http','Attempting to open ['+self.url+']...')
		ntry = 0
		while ntry<self._maxtry:
			ntry = ntry + 1
			r = Reason()
			try:
				f = urllib2.urlopen(self.url)
			except (IOError, OSError):
				r = Reason(er(self.filename,self.url))
			if not r.ok():
				if not ntry==self._maxtry:
					verbo.log('retry','Attempt to open ['+self.url+'] has failed.  Retrying '+`ntry`+'/'+`self._maxtry-1`+'...')
					time.sleep(self._pause)
			else:
				break
		return r,f
		
	def getFile(self):
		r = Reason()
		verbo.log('http','Attempting to open ['+self.url+']...')
		ntry = 0
		while ntry<self._maxtry:
			ntry = ntry + 1
			r = Reason()
			try:
				f = urllib2.urlopen(self.url)
				file = f.readlines()
				f.close()
			except (IOError, OSError):
				r = Reason(er(self.filename,self.url))
				file = []
			if verbo('http'):
				if r.ok(): print 'Successfully read from ['+self.url+']...'
				else:      print 'Error attempting to read from ['+self.url+']...'
			
			if not r.ok():
				if not ntry==self._maxtry:
					verbo.log('retry','Attempt to get ['+self.url+'] has failed.  Retrying '+`ntry`+'/'+`self._maxtry-1`+'...')
					time.sleep(self._pause)
			else:
				break
		return r,file
		
	def errorHtml(self,fname):
		maxline = 10
		ok = 0
		try:
			f = open(fname,'r')
			for i in range(maxline):
				line = f.readline()
				if line=='': break
				elif contains(line,'not found on this server'): 
					ok = 1; break
				elif contains(line,'Error 404: File Not Found'):
					ok = 1; break
				elif contains(line,'<TITLE>403 Forbidden</TITLE>'):
					ok = 1; break
			f.close()
		except (IOError,OSError):
			ok = 1
		return ok
		
	def get(self,target_directory):
		r = Reason()
		if os.path.isdir(target_directory):
			ntry = 0
			errorhtml = 0
			r = ask.re('http','OK to download ['+self.filename+'] from ['+urlparse.urlparse(self.url)[1]+']?')
			if r.ok():
				while ntry<self._maxtry:
					ntry = ntry + 1
					try:
						verbo.log('http','Downloading ['+self.filename+'] from ['+urlparse.urlparse(self.url)[1]+']...')
					
						f = urllib2.urlopen(self.url)
						fname = os.path.join(target_directory,self.filename)
						g = open(fname,'w')
						
						size = 0
						if verbo('meter'):
							d = f.info().dict
							if d.has_key('content-length'): 
								try:
									size = int(d['content-length'])
								except:
									size = 0
						block = 10000
						_meter = verbo('meter')
						if size>block and size>10000:
							total = 0
							while 1:
								x = f.read(block)
								total = total + len(x)
								if x=='': break
								if _meter: dlMeter(1,total,size)
								g.write(x)
							flash()
						else:
							x = f.read()
							g.write(x)
						f.close()
						g.close()
					
						if self.errorHtml(fname):
							errorhtml = 1
							removeFile(os.path.join(target_directory,self.filename))
							r.reason('Download of ['+self.filename+'] from ['+self.url+'] has failed.')
					except (IOError, OSError):
						verbo.log('http',"Error during download of ["+self.filename+"] from ["+urlparse.urlparse(self.url)[1]+"]...")
						removeFile(os.path.join(target_directory,self.filename))
						r.reason("Error during download of ["+self.filename+"] from ["+urlparse.urlparse(self.url)[1]+"].")
					except KeyboardInterrupt:
						verbo.log('http',"Download interrupted by ^C...")
						removeFile(os.path.join(target_directory,self.filename))
						raise KeyboardInterrupt
					except httplib.InvalidURL:
						verbo.log('http',"Invalid http proxy...")
						r.reason("Invalid http proxy.")
						abort("Invalid http proxy.")
					except socket.error:
						verbo.log('http',"Download of ["+self.filename+'] from ['+urlparse.urlparse(self.url)[1]+'] failed.  Connection interrupted...')
						removeFile(os.path.join(target_directory,self.filename))
						r.reason("Download of ["+self.filename+'] from ['+urlparse.urlparse(self.url)[1]+'] failed.  Connection interrupted')
					verbo.log('http','Successfully read ['+self.filename+'] from ['+urlparse.urlparse(self.url)[1]+']...')
					
					if not r.ok() and not errorhtml:
						if not ntry==self._maxtry:
							verbo.log('retry','Attempt to get ['+self.url+'] has failed.  Retrying '+`ntry`+'/'+`self._maxtry-1`+'...')
							time.sleep(self._pause)
					else:
						break
		else:
			r = Reason("Can't download ["+self.filename+"] to ["+target_directory+"] directory doesn't exist.")
		return r

	def source(self): return urlparse.urlparse(self.url)[1]
