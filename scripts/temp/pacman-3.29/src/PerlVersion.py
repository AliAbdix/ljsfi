from StringAttr import *
import commands, re

# Code modified by Scot Kronenfeld 2/2009
# Fixed to store the perl version, and not call 'perl -v' everytime this function is called
perlVers = None
def perlversion():
        global perlVers
        if perlVers != None: return perlVers
	if fileInPath('perl'):
		status,output = commands.getstatusoutput('perl -v')
		if status==0:
			l = string.split(output,' ')
			v = '- unknown perl version -'
			for x in l:
				if len(x)>3:
					if x[0]=='v' and '.' in x: v = x[1:]; break
                        perlVers = v
			return perlVers
                perlVers = '- no perl in $path -'
		return perlVers
	else:
                perlVers = '- no perl in $path -'
		return perlVers

# comparePerlVersion function added by Scot Kronenfeld 2/2009
# It is necessary to correctly compare perl 5.10 and higher
#
# Compare two perl versions
# Inputs:
#   Two versions, of the form returned by perlversion() above (e.g. '5.8.8')
#
# Returns 1 if  v1 > v2
# Returns 0 if  v1 = v2
# Returns -1 if v1 < v2
def comparePerlVersion(v1, v2):

        # If we find a version with a character other than a digit or dot,
        # then use the old method of comparing the version.
        p = re.compile("[^\d.]")
        if p.search(v1) or p.search(v2):
                if v1 < v2:
                        return -1
                elif v1 > v2:
                        return 1
                return 0
        else:
                v1c = v1.split(".")
                v2c = v2.split(".")

                for i in range(0, min(len(v1c), len(v2c)) ):
                        if   int(v1c[i]) > int(v2c[i]): return 1
                        elif int(v1c[i]) < int(v2c[i]): return -1

                # Define 5.8.x is greater than 5.8
                if   len(v1c) > len(v2c): return 1
                elif len(v2c) > len(v1c): return -1
        
                return 0
        

class PerlVersion(StringAttr):
	type   = 'perl version'
	title  = 'Perl Versions'
	action = 'perl version'
			
	def str(self): return 'must be equal to ['+self.value+'], actually ['+perlversion()+'].'
	def satisfied  (self): 
		pv = perlversion()
		if pv=='- no perl in $path -':
			r = Reason("[perl] is not in the installer's path.")
#			return Reason("[perl] is not in the installer's path.")
		else:
                        tmp = comparePerlVersion(pv, self.value) # Added by Scot Kronenfeld 2/2009
			r = Reason('perl version is ['+pv+']. It must be ['+self.value+'].',not tmp == 0)
#			return Reason('perl version is ['+perlversion()+']. It must be ['+self.value+'].',not perlversion() == self.value)	
		self.satset(r.ok())
		return r
	def satisfiable(self): return self.satisfied()	

	def acquire(self): return self.satisfied()
	def retract(self): return Reason()
	
class PerlVersionLE(PerlVersion):
	type   = 'perl version <='
	title  = 'perl version <=s'
	action = 'perl version <='
	
	def str(self): return '['+self.value+'], actually ['+perlversion()+'].'
	def satisfied(self): 
		pv = perlversion()
		if pv=='- no perl in $path -':
			r = Reason("[perl] is not in the installer's path.")
#			return Reason("[perl] is not in the installer's path.")
		else:
                        tmp = comparePerlVersion(pv, self.value) # Added by Scot Kronenfeld 2/2009
			r = Reason('perl version ['+pv+'] must be <= ['+self.value+'].',not (tmp == 0 or tmp == -1) )
#			return Reason('perl version ['+perlversion()+'] must be <= ['+self.value+'].',not perlversion() <= self.value) 
		self.satset(r.ok())
		return r
	
class PerlVersionLT(PerlVersion):
	type   = 'perl version <'
	title  = 'perl version <s'
	action = 'perl version <'
	
	def str(self): return '['+self.value+'], actually ['+perlversion()+'].'
	def satisfied(self):
		pv = perlversion()
		if pv=='- no perl in $path -':
			r = Reason("[perl] is not in the installer's path.")
#			return Reason("[perl] is not in the installer's path.")
		else:
                        tmp = comparePerlVersion(pv, self.value) # Added by Scot Kronenfeld 2/2009
 			r = Reason('perl version ['+pv+'] must be < ['+self.value+'].',not tmp == -1)
# 			return Reason('perl version ['+perlversion()+'] must be < ['+self.value+'].',not perlversion() < self.value) 
		self.satset(r.ok())
		return r
	
class PerlVersionGE(PerlVersion):
	type   = 'perl version >='
	title  = 'perl version >=s'
	action = 'perl version >='
	
	def str(self): return '['+self.value+'], actually ['+perlversion()+'].'
	def satisfied(self): 
		pv = perlversion()
		if pv=='- no perl in $path -':
			r = Reason("[perl] is not in the installer's path.")
#			return Reason("[perl] is not in the installer's path.")
		else:
                        tmp = comparePerlVersion(pv, self.value) # Added by Scot Kronenfeld 2/2009
			r = Reason('perl version ['+pv+'] must be >= ['+self.value+'].',not (tmp == 0 or tmp == 1) )
#			return Reason('perl version ['+perlversion()+'] must be >= ['+self.value+'].',not perlversion() >= self.value) 
		self.satset(r.ok())
		return r
	
class PerlVersionGT(PerlVersion):
	type   = 'perl version >'
	title  = 'perl version >s'
	action = 'perl version >'
	
	def str(self): return '['+self.value+'], actually ['+perlversion()+'].'
	def satisfied(self): 
		pv = perlversion()
		if pv=='- no perl in $path -':
			r = Reason("[perl] is not in the installer's path.")
#			return Reason("[perl] is not in the installer's path.")
		else:
                        tmp = comparePerlVersion(pv, self.value) # Added by Scot Kronenfeld 2/2009
			r = Reason('perl version ['+pv+'] must be > ['+self.value+'].',not tmp == 1) 
#			return Reason('perl version ['+perlversion()+'] must be > ['+self.value+'].',not perlversion() > self.value) 
		self.satset(r.ok())
		return r
