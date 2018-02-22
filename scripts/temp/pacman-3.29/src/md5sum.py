##! /usr/bin/env python
#
#"""Python utility to print MD5 checksums of argument files.
#
#Works with Python 1.5.2 and later.
#"""
# -- md5checksum grabbed from www.python.org.   S.Y.
#

from Base import *
import sys, md5

BLOCKSIZE = 1024*1024

def hexify(s):
    return ("%02x"*len(s)) % tuple(map(ord, s))

def md5sum(path):
	r = Reason()
	sumstring = ''
	try:
		f = open(path,'rb')
		sum = md5.new()
		while 1:
			block = f.read(BLOCKSIZE)
			if not block:
				break
			sum.update(block)
		sumstring = hexify(sum.digest())
		f.close()
	except:
		r = Reason("Error computing md5checksum of ["+path+"].")

	return r,sumstring
