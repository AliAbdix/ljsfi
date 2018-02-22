import sys
import re
import types
import os
import string

# findPlatform will return a list of platforms. They all describe the
# platform we are using, but the list is ordered from most-specific
# to least specific. For example, on Red Hat Linux 7.2, we get:
#     ['linux-redhat-7.2', 'linux-redhat', 'linux-i386', 'unix']
# For systems that we know less about, we return a shorter list, like:
#     ['sunos5', 'unix']
# In the future, we may expand the list to include kernel/libc versions
# in the list. The list will probably be ordered like:
#  [redhat-version, kernel-version, linux, unix]
#
def findPlatform():
	base_platform = sys.platform
	if re.match('linux', base_platform, re.IGNORECASE | re.DOTALL):
		full_linux_version, linux_version = findLinuxVersion()
		if full_linux_version != "":
			platforms = [full_linux_version, linux_version,
						 base_platform, 'linux', 'unix']
		elif linux_version != "":
			platforms = [linux_version, base_platform, 'linux', 'unix']
		else:		   
			platforms = [base_platform, 'linux', 'unix']
	elif base_platform=='aix4':
		platforms = ['AIX4']
        # AIX5 detection re-added by Scot Kronenfeld 2/2009
	elif base_platform=='aix5':
                full_aix_version = findAIXVersion();
                if full_aix_version:
                        platforms = [full_aix_version, 'AIX5', 'unix']
                else:
                        platforms = ['AIX5', 'unix']
        # Darwin detection re-added by Scot Kronenfeld 2/2009
	elif base_platform == 'darwin':
		darwin_version = findDarwinVersion();
                if darwin_version:
                        platforms = [darwin_version, base_platform, 'unix']
                else:
                        platforms = [base_platform, 'unix']
	else:
		platforms = [base_platform, 'unix']
	return platforms

def findLinux():
	platform = '*'
	try:
		if   os.path.exists('/etc/rocks-release' ): issue_file = '/etc/rocks-release'
		elif os.path.exists('/etc/redhat-release'): issue_file = '/etc/redhat-release'
		elif os.path.exists('/etc/SuSE-release'  ): issue_file = '/etc/SuSE-release'
		elif os.path.exists('/etc/gentoo-release'): issue_file = '/etc/gentoo-release'
		else:                                       issue_file = '/etc/issue'
		
		f = open(issue_file,'r'); text = f.read(); f.close()
		import etc_issue_parser
		
		OS,version = etc_issue_parser.parse(text)
		if not OS.strip()=='': platform = OS+'-'+version
	except:
		pass
	return platform
			

# This is used by findPlatform. It figures out which distribution of
# Linux we're running on. 
def findLinuxVersion():
	try:
		# It's important to look for rocks-releaes before
		# the others.  A ROCKS install might have redhat-release
		# as well.
		if os.path.exists('/etc/rocks-release'):
			issue_filename = '/etc/rocks-release'
		elif os.path.exists('/etc/redhat-release'):
			issue_filename = '/etc/redhat-release'
		elif os.path.exists('/etc/SuSE-release'):
			issue_filename = '/etc/SuSE-release'
		else:
			issue_filename = '/etc/issue'
			
		issue_file = open(issue_filename, 'r')
#		issue_file = open('/etc/issue', 'r')
		lines = issue_file.readlines()
		versions = ("", "")
		for line in lines:
			distro = None
			if   re.search('Red Hat Enterprise*', line):
				distro = 'rhel'
			elif re.search('Red Hat*',line):
				distro = 'redhat'
			elif re.search('Tao',line):
				distro = 'tao'
			elif re.search('Mandrake', line):
				distro = 'mandrake'
#			elif re.search('SuSE', line):
			elif re.compile('SuSE', re.IGNORECASE).search(line):
				distro = 'suse'
			elif re.search('Debian', line):
				distro = 'debian'
			elif re.search('Fedora', line):
				distro = 'fedora'
			elif re.search('Scientific Linux SL',line):
				distro = 'sl'
			elif re.search('Scientific Linux CERN',line):
				distro = 'sl-cern'
			elif re.search('Scientific Linux IFIC',line):
				distro = 'sl-ific'
			elif re.search('BU Linux',line):
				distro = 'BU'
#			elif re.search('Scientific Linux Release [\d\.]+ \(Fermi\)',line):
			elif re.compile('Scientific Linux Release [\d\.]+ \(Fermi\)',re.IGNORECASE).search(line):
				distro = 'sl-fermi'
				# Fermi doesn't have . in their version strings
				line = re.sub(r"(\d)(\d)(\d)", r"\1.\2.\3", line)
				
			# This needs to go after sl-fermi until we can make
			# a better regexp
			elif line.count('CentOS release')>0:
				distro = 'centos'
			elif re.search('Fermi', line):
				distro = 'fermi'
			elif re.search('Rocks', line):
				distro = 'rocks'
			
#			if distro != None:
#				version_match = re.search(r"\d+\.\d+", line)
#				if version_match:
#					version_string = line[version_match.start():version_match.end()]
#					versions = ('linux-' + distro + '-' + version_string,
#								'linux-'+distro)
#				else:
#					versions = ('', 'linux-'+distro)
#				break
#...replaced with Alain's new code as follows...
#
			if distro != None:
				version_match = re.search(r"\d+\.\d+", line)
				if version_match:
					version_string = line[version_match.start():version_match.end()]
					# -- BU linux puts their version string in a funny place.  S.Y.
					if distro=='BU' and len(string.split(line,' '))>5: version_string = string.split(line,' ')[5]
					versions = ('linux-' + distro + '-' + version_string,
					   'linux-'+distro)
				else:
					version_match = re.search(r"\d+", line)
					if version_match:
						version_string = line[version_match.start():version_match.end()]
						versions = ('linux-' + distro + '-' + version_string,
							'linux-'+distro)
					else:
						versions = ('', 'linux-'+distro)
				break

	except IOError:
		versions = ("", "")

	return versions

# This subroutine was originally written by Saul Youssef
# It was modified by Scot Kronenfeld on 2/2009 to re-implement AIX5 detection
def findAIXVersion():
	try:
		version = string.rstrip(os.popen('uname -v').readlines()[0])
		release = string.rstrip(os.popen('uname -r').readlines()[0])
		versions = ('AIX' + version + '.' + release)
	except IOError:
		versions = None
	return versions

# This subroutine was originally written by Saul Youssef
# It was modified by Scot Kronenfeld on 2/2009 to re-implement Mac detection
def findDarwinVersion():
	try:
		release = string.rstrip(os.popen('sw_vers -productVersion').readlines()[0])
		version_match = re.search(r"\d+\.\d+", release)
		if version_match:
			version = release[version_match.start():version_match.end()]
			versions = ('MacOS-' + version)
		else:
			versions = None
	except IOError:
		versions = None
	return versions

# This class is like a simple dictionary.
# Unlike the normal dictionary, it can take a list of indices.
# It searches them in order until it finds one that matches.
# This is used to look for the best matching platform in the list
# of systems
# We don't implement all methods that a dictionary has, just because
# we don't need them right now. 
class Platforms:
	def __init__(self, dictionary):
		self.dictionary = dictionary
  	def __getitem__(self, index):
  		value = None;
  		if isinstance(index, types.ListType):
  			for i in index:
  				if self.dictionary.has_key(i):
  					value = self.dictionary[i]
  					break;
  		else:
  			value = self.dictionary[index]
  		return value;
	def has_key(self, index):
		key_exists = 0;
  		if isinstance(index, types.ListType):
  			for i in index:
  				if self.dictionary.has_key(i):
  					key_exists = 1;
  					break;
  		else:
  			key_exists = self.dictionary.has_key(index)
  		return key_exists

# This is just testing code, and it is not needed for normal
# operation
def testPlatform():
	print "You are running: ", findPlatform()
	platforms = Platforms({ 'linux-i386' : ['gpt-0.2.tar.gz', 'gpt-0.2'], \
							'linux2'     : ['gpt-0.3.tar.gz', 'gpt-0.3'], \
						   })
	print "linux2 is: ", platforms['linux2']
	print "linux-i386 is: ", platforms['linux-i386']
	print "['linux-i386', 'linux2']: ", platforms[['linux-i386', 'linux2']]
	print "['linux2', 'linux-i386']: ", platforms[['linux2', 'linux-i386']]
	print "[]: ", platforms[[]]
	print "Has linux2: ", platforms.has_key('linux2')
	print "Has linux-i386: ", platforms.has_key('linux-i386')
	print "Has ['linux-i386', 'linux2']: ", platforms.has_key(['linux-i386', 'linux2'])
	print "Has ['linux2', 'linux-i386']: ", platforms.has_key(['linux2', 'linux-i386'])
	return

#testPlatform()
