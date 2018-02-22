#
#	Copyright Saul Youssef, January 2005
#

# The packageRevision atom was added by Scot Kronenfeld in 2/2009
from StringAttr import *

class PackageRevision(StringAttr):
	type   =  'packageRevision'
	title  =  'Package Revision'
	action =  'packageRevision'

        def __init__(self, os='', arch='', rev='', comment=''):
                # os, arch, and rev *must* be defined, or throw a syntax error
                if os != "" and arch != '' and rev != "":
                        if (os == '*' and arch != '*') or (os != '*' and arch == '*'):
                                abort("Syntax error: packageRevision atom - OS and arch must both be '*' or neither can be '*'")
                        else:
                                self.os   = os
                                self.arch = arch
                                self.rev  = rev
                else:
                        abort('Syntax error: packageRevision atom must have OS, arch, and revision defined.')
                                                                                                
	
	def str(self): return 'Platform: ' + self.os + '/' + self.arch + ' Revision: ' + self.rev

        def equal(self,n):
                return self.os == n.os and self.arch == n.arch and self.rev == n.rev
	
        def getRevision(self):
                return self.rev

	def satisfies(self,v):
		if self.type==v.type:
			return self.rev == v.rev
		else:
			return 0

