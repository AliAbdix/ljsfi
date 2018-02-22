"""

Interface to MakePacball

"""

from Base import *
import makePacball

def pacball(pacballs,defaults):
	r = Reason()
	if not len(pacballs)==1: r = Reason("-pacball specification must be a single package.")
	if r.ok():
		if len(defaults)>1: r = Reason("Must specify at most one default package.")
	
	if r.ok():
		package = pacballs[0]
		default = ''
		if len(defaults)>0: default = defaults[0]
		
		if not ':' in package:
			r = Reason("-pacball argument ["+package+"] must be of the form <cache>:<package>")
		
		if r.ok():
			pos = package.rfind(':')
			cache,snapshot_package = package[:pos],package[pos+1:]
#			cache,snapshot_package = package.rsplit(':')
			if default=='': default=snapshot_package
			try:
				makePacball.makePacball(cache,snapshot_package,default)
			except makePacball.PacballException:
				r = Reason(baseErrorMessage())
	return r
