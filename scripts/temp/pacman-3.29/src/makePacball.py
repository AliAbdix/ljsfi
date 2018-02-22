#!/usr/bin/env python

"""
Introduction
------------

This script makes a self-contained, standalone executable that can be used to 
install any package from an ATLAS release without requiring Pacman or a 
network connection.  The executable includes a Pacman snapshot of a single 
ATLAS release including externals, CMT, Pacman, KV, requirements encoded into 
Pacman, etc.  This kind of file is intended as both an archive of a release at 
a particular moment in time and as a file that can be treated like just 
another kind of input file used by Panda, DQ2, etc.

Usage
-----

Usage: makePacball.py RELEASE_NUMBER, where RELEASE_NUMBER is a release in the 
ATLAS cache.  This creates an executable called 
RELEASE_NUMBER_KV.time-TIME.md5-MD5SUM.sh, where TIME is the UTC time at 
creation, formatted with %Y-%m-%d-%H-%M-%S, and MD5SUM is its md5 checksum.  
Run the executable to install RELEASE_NUMBER, or, to install any other package 
that's included with RELEASE_NUMBER+KV, run the executable with one argument 
specifying the name of that package.

Details
-------

This python script makes a tarball archive of a Pacman snapshot of the ATLAS 
release specified on the command line, including Kit Validation.  It then 
generates a shell script and appends it to the front of the archive, making 
the executable.  Running the executable runs this script.  The script is able 
to extract and unpack the tarball that is attached to itself and install a 
package from the resulting snapshot.  (The tarball is not gzipped, since, for 
an ATLAS release, gzipping only reduces the tarball's size by about 1%.  Plus 
this, eliminates the extra depedency on gunzip at the installation location.)

Note that the script at the front of the executable may be manually removed 
(up to and including the line `exit 0'), resulting in a standard tarball 
containing the ATLAS snapshot and a copy of Pacman.
"""

import sys, os, commands, md5, string, time, urllib2 as urllibX

class PacballException(Exception): pass

def runcmd(cmd, checkStatus=True):
	"""Run the given sh code and return the wait status.
	
	Output is ignored, except when building an exception message.  Note that 
	the returned status is like that returned by wait(), not just a simple 
	exit status.  If checkStatus is True, this method raises an exception if 
	the status is not zero.
	"""
	try: status, output = commands.getstatusoutput(cmd)
	except KeyboardInterrupt: raise
	except: raise PacballException("Unable to run helper command [%s]." % cmd)
	if checkStatus and status!=0:
		msg = "Error making pacball"
		if os.WIFEXITED(status):
			output = output.strip()
			if output!='':
				msg += ":"
				if '\n' in output: msg += '\n'
				else: msg += ' '
				msg += "%s" % output.strip()
		else:
			msg += ": helper command [%s] interrupted" % cmd
		msg += '.'
		raise PacballException(msg)
	return status

def quote(text):
	"""Quote the text for use in sh code."""
	return "'%s'" % text.replace("'", r"'\''")

def encode(c):
	"""Return a (very) sh code safe interpretation of the character c."""
	if c not in string.ascii_letters+string.digits+'_'+'.'+'-': return '_'
	else: return c

def makePacball(cache, snapshot_package, install_package=None):
	"""Create a pacball of cache:snapshot_package.
	
	The pacball will install snapshot_package, or, if given, install_package, 
	by default.
	"""

	#---parameters

	if install_package is None: install_package = snapshot_package

	PACMAN_URL = 'http://physics.bu.edu/pacman/sample_cache/tarballs/pacman-latest.tar.gz'
	TMPDIR     = 'o..tmp..o'             #temporary sandbox directory, used by this script and by the pacball; in both cases it will be deleted from the current working directory if it already exists
	SKIP       = 'o..SKIP..o'            #a unique placeholder string used only during the execution of this method
	PACBALLTMP = 'pacball.sh'            #temporary name while the pacball is being built
	PACMANTMP  = 'pacman-latest.tar.gz'  #temporary name to download pacman to

	#make sure SKIP is not in any of the parameters
	for param in [cache, snapshot_package, install_package, TMPDIR]:
		if param.find(SKIP)!=-1: raise PacballException("Parameter [%s] cannot contain the phrase [%s]." % (param, SKIP))


	try:
		#---create working area

		#do all the work in a temporary sandbox (clobber it, too)
		origcwd = os.getcwd()
		runcmd('rm -rf %s' % quote(TMPDIR))
		runcmd('mkdir %s' % quote(TMPDIR))
		os.chdir(TMPDIR)

		
		#---gather inputs
		
		#(note that the snapshot and pacman are later moved to another TMPDIR, so it untars that way)

		#fetch
		print "Fetching dependent packages..."
		runcmd('pacman -allow trust-all-caches unsupported-platforms tar-overwrite -fetch %s:%s' % (quote(cache), quote(snapshot_package)))

		#make the snapshot
		snapshot_name = ''.join([encode(c) for c in snapshot_package])
		print "Collecting downloads..."
		runcmd('pacman -snap -o %s' % quote(snapshot_name))

		#get pacman
		print "Getting latest Pacman..."
		try: open(PACMANTMP, 'w').write(urllibX.urlopen(PACMAN_URL).read())
		except KeyboardInterrupt: raise
		except: raise PacballException("Unable to download [%s]." % PACMAN_URL)
		runcmd('gunzip -c %s | tar x' % quote(PACMANTMP))
		runcmd('rm %s' % quote(PACMANTMP))
		pacman_untarred = None
		for fname in os.listdir('.'):
			if fname.startswith('pacman-'):
				try: float(fname[len('pacman-'):])
				except ValueError: continue
				pacman_untarred = fname
				break
		if pacman_untarred is None: raise PacballException("Unable to get Pacman.")  #this should only happen if there's an internal error with this logic
		

		#---write the header

		header = \
r"""#!/bin/sh
targs='-n'
echo '' | tail $targs +0 >/dev/null 2>&1
if [ $? -ne 0 ]; then targs=''; fi  #SunOS
set -e
install_package="$1"
if [ -z "$install_package" ]; then install_package=%(install_package)s; fi
rm -fr %(TMPDIR)s
printf "Untarring..."
tail $targs +%(SKIP)s "$0" | tar xf -
printf "done.\n"
cd %(TMPDIR)s/%(pacman_untarred)s; . ./setup.sh; cd ../..
pacman -allow trust-all-caches unsupported-platforms tar-overwrite -get %(TMPDIR)s/%(snapshot_name)s.snapshot:"$install_package"
rm -fr %(TMPDIR)s
exit 0
""" % {
			'install_package': quote(install_package),
			'TMPDIR'         : quote(TMPDIR)         ,
			'SKIP'           : SKIP                  ,
			'pacman_untarred': quote(pacman_untarred),
			'snapshot_name'  : quote(snapshot_name)  ,
		}
		header = header.replace(SKIP, str(header.count('\n')+1))
		open(PACBALLTMP, 'w').write(header)


		#---create and append the tarball
		
		print "Assembling Pacball..."
		runcmd('mkdir %s' % quote(TMPDIR))
		runcmd('mv %s %s %s/' % (quote(snapshot_name+'.snapshot'), quote(pacman_untarred), quote(TMPDIR)))
		runcmd('tar c %s/%s %s/%s >> %s' % (quote(TMPDIR), quote(snapshot_name+'.snapshot'), quote(TMPDIR), quote(pacman_untarred), quote(PACBALLTMP)))

		
		#---name the pacball

		#compute md5sum (with a meter)
		print "Computing md5 checksum..."
		md5sum = md5.md5()
		f = open(PACBALLTMP, 'rb')
		megs = 0
		while True:
			x = f.read(10000000)
			if x=='': break
			md5sum.update(x)
			megs = megs + 10
			if megs%100==0: sys.stdout.write('\r%d MB...' % megs); sys.stdout.flush()
		sys.stdout.write('\r'); sys.stdout.flush()  #(next line printed below is longer than any of the above, so no need to erase that final line)
		f.close()
		md5sum = md5sum.hexdigest()

		#name it
		pacballfname = '%s.time-%s.md5-%s.sh' % (snapshot_name, time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime()), md5sum)
		runcmd('mv %s %s' % (quote(PACBALLTMP), quote(pacballfname)))
		runcmd('chmod 755 %s' % quote(pacballfname))


		#---cleanup

		runcmd('mv %s %s/' % (quote(pacballfname), quote(origcwd)))
		os.chdir(origcwd)
		runcmd('rm -rf %s' % quote(TMPDIR))
		print "Pacball [%s] successfully created." % pacballfname
		print "Use %% %s to install %s." % (pacballfname, install_package)
	finally:
		os.chdir(origcwd)
		runcmd('rm -rf %s' % quote(TMPDIR))


if __name__=='__main__':
	#makePacball('http://atlas000.bu.edu/democache', 'Foo1')
	#sys.exit(0)
	
	#require pacman
	if runcmd('which pacman &> /dev/null', checkStatus=False)!=0: raise PacballException("Making a pacball requires Pacman.")
	
	#require python version
	verReq = [2,2]
	verSys = [sys.version_info[0],sys.version_info[1],sys.version_info[2]]
	if verSys<verReq: raise PacballException("You are using Python %s.  This script requires Python >= %s." % ('.'.join(map(str,verSys)), '.'.join(map(str,verReq))))

	if len(sys.argv)!=2:
		sys.stderr.write("*** ERROR ***\n")
		sys.stderr.write("usage: %s RELEASE_NUMBER\n" % sys.argv[0].split('/')[-1])
		sys.exit(1)
	RELEASE = sys.argv[1]
	if RELEASE.endswith('+KV'):
		sys.stderr.write("*** ERROR ***\n")
		sys.stderr.write("The RELEASE_NUMBER should not include `+KV'.  It's handled automatically.\n")
		sys.exit(1)

	makePacball('ATLAS', RELEASE+'+KV', RELEASE)
