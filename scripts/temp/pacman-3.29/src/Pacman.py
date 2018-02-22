#
#   Copyright 2004, Saul Youssef
#
#   Pacman fetches, installs, configures and sets up software
#
#   See http://physics.bu.edu/pacman/ for more information.
#
from Abort import *
try:
	import sys,os,pythonCheck
	pythonCheck.pythonCheck()

	import commandCheck
	commandCheck.commandCheck()

	mutable = 0
	for x in ['-repair','-fetch','-install','-uninstall','-remove','-remove-all','-update','-get','-setup']: 
		if x in sys.argv: mutable = 1

	import lock
	if mutable: lock.lock()

	from Base import *
	sys.stdout = Writer(sys.stdout)

	from Environment import *
	import Home,Package,UniversalCache,Platform,Execution,Registry,Trust,MirrorCache,tracebackSaver
	from switchFinalize import *  # to prevent late module loading!

	r = Reason()
	home = Home.home
	
	if (switch('lc') or switch('domain') or switch('extract-sources') or switch('extract-downloads')) and \
	    not (switch('update-check') or switch('snap') or switch('snapshot') or switch('mirror') or switch('get') \
	         or switch('install') or switch('fetch') or switch('update') or switch('remove')):
		topspecs = []
	else:
		topspecs = home.topSpecs()
		
	mirrorstring,snapstring = 'installation','installation'
	if    len(switchItems('mirror'  ))>0: mirrorstring = fileify(switchItems('mirror'  )[0])
	if    len(switchItems('snap'    ))>0: snapstring   = fileify(switchItems('snap'    )[0])
	elif  len(switchItems('snapshot'))>0: snapstring   = fileify(switchItems('snapshot')[0])
	
	mirrorUpdate = len(params)>0 and forall(params,lambda param: tail(param,'.mirror'  ) or tail(param,'.mirror/'  ) or \
	                                                             tail(param,'.snapshot') or tail(param,'.snapshot/') )

	def specPars(sw): 
		specs = []
		lastcaches = []
		for param in switchItems(sw):
			spec = Package.Spec(param)
			if not sw in ['uninstall','remove','remove-all'] and spec.caches==[]: spec.caches = lastcaches[:]
			specs.append(spec)
			if len(spec.caches)>0: lastcaches = spec.caches[:]
		return specs
	def specParT(sw):
		specs = specPars(sw)
		if len(specs)==0 and switch(sw): specs = topspecs
		return specs
		
	def pathfix(name):
		if len(name)>=2 and name[:2]=='..': return fullpath(name)
		else:                               return name
		
	depth = displayModeDepth()
except KeyboardInterrupt:
	import lock
	lock.unlock()
	import sys
	print '^C user interrupt.  No actions have been taken.'
	if '-debug' in sys.argv: raise
	sys.exit(1)
except AbortException,message:
	import lock
	lock.unlock()
	import sys
	print message.value
	if '-debug' in sys.argv: raise
	sys.exit(1)
except MemoryError:
	import lock
	lock.unlock()
	import sys
	print 'Not enough memory.'
	if '-debug' in sys.argv: raise
	sys.exit(1)
#except NameError:
#	import lock
#	lock.unlock()
#	import sys
#	print 'Obsolete Python installation ['+sys.version+'].  Update before using Pacman.'
#	if '-debug' in sys.argv: raise
#	sys.exit(1)
except ImportError:
	import lock
	lock.unlock()
	import sys
	print 'Missing python module.'
	if '-debug' in sys.argv: raise
	sys.exit(1)

try:
	alreadySetup = os.path.exists('setup.csh') or os.path.exists('setup.sh')
	if allow('save-setup'): 
		if not os.path.exists(os.path.join(pac_anchor,pacmanDir,'setupmess')):
			print '** Note that setup scripts are no longer removed by Pacman during installaton or update.'
			print '** As of Pacman 3.19, -allow save-setup only suppresses cleanup of backup .sav files even if'
			print '** an installation has succeeded.  - S.Y.'
			try:
				f = open(os.path.join(pac_anchor,pacmanDir,'setupmess'),'w')
				f.write('done')
				f.close()
			except:
				pass
#-- save current setup files if any
	if r.ok() and (switch('setup') or switch('get') or switch('resume') or alreadySetup and (switch('update') or switch('remove'))): saveFiles('setup.csh','setup.sh','setup.py','setup.pl','setup.ksh')
#	if mutable:
#		if allow('save-setup'): saveFiles  ('setup.csh','setup.sh','setup.py','setup.pl','setup.ksh')
#		else:                   removeFiles('setup.csh','setup.sh','setup.py','setup.pl','setup.ksh')
	if switch( 'registry'): Registry.registry.display()
	
	if switch('single'): adepth = 0
	else:                adepth = 999999
	
	r = gnuTarCheck()
	
	if r.ok() and len(switchItems('pacball'))>0:
		import pacball
		r = pacball.pacball(switchItems('pacball'),switchItems('default'))
	
	if r.ok(): r = allReason(specPars(         'fetch'),lambda spec: Package.LazyPackage(spec).fetch            ())
	if r.ok(): r = allReason(specParT(       'install'),lambda spec: Package.LazyPackage(spec).satisfiable      ())
	if r.ok(): r = allReason(specParT(       'install'),lambda spec: Package.LazyPackage(spec).satisfy          ())
	if r.ok(): r = allReason(specParT(        'resume'),lambda spec: Package.LazyPackage(spec).satisfy          ())
	if r.ok(): r = allReason(specParT(           'get'),lambda spec: Package.LazyPackage(spec).satisfiable      ())
	if r.ok(): r = allReason(specParT(           'get'),lambda spec: Package.LazyPackage(spec).satisfy          ())
	if r.ok(): r = allReason(specParT(     'installed'),lambda spec: Package.LazyPackage(spec).satisfied        ())
	if r.ok(): r = allReason(specParT(     'uninstall'),lambda spec: Package.LazyPackage(spec).uninstall  (adepth))
	if r.ok(): r = allReason(specParT(        'remove'),lambda spec: Package.LazyPackage(spec).remove     (adepth))
	if r.ok(): r = allReason(specParT(        'verify'),lambda spec: Package.LazyPackage(spec).setup            ())
	if r.ok(): r = allReason(specParT(        'verify'),lambda spec: Package.LazyPackage(spec).verify           ())
	if r.ok(): r = allReason(specParT(        'repair'),lambda spec: Package.LazyPackage(spec).repair           ())
	if not mirrorUpdate:
		if r.ok(): r = allReason(specParT(  'update-check'),lambda spec: Package.LazyPackage(spec).updateCheck      ())
		if r.ok(): r = allReason(specParT(        'update'),lambda spec: Package.LazyPackage(spec).updateCheck      ())
		if r.ok(): r = allReason(specParT(        'update'),lambda spec: Package.LazyPackage(spec).update           ())
		if r.ok(): r = allReason(specParT( 'update-remove'),lambda spec: Package.LazyPackage(spec).updateRemove     ())
	else:
		if r.ok(): r = allReason(switchItems('update-check'), lambda cache: UniversalCache.UniversalCache(cache)._cache.updateCheck  ())
		if r.ok(): r = allReason(switchItems('update'      ), lambda cache: UniversalCache.UniversalCache(cache)._cache.update       ())
		if r.ok(): r = allReason(switchItems('update-remove'),lambda cache: UniversalCache.UniversalCache(cache)._cache.updateRemove ())

	if r.ok() and (switch('setup') or switch('get') or switch('resume') or alreadySetup and (switch('update') or switch('remove'))):
		e = AND()
		for spec in home.topSpecs(): e.append(Package.LazyPackage(spec))
		r = e.setup()
		if r.ok() and (len(e)>0 or switch('setup')):
			os.chdir(home.UCL)
			saveFiles  ('setup.csh','setup.sh','setup.py','setup.pl','setup.ksh')
			removeFiles('setup.csh','setup.sh','setup.py','setup.pl','setup.ksh')
#			if allow('save-setup'): saveFiles  ('setup.csh','setup.sh','setup.py','setup.pl','setup.ksh')
#			else:                   removeFiles('setup.csh','setup.sh','setup.py','setup.pl','setup.ksh')
			csh,sh,py,pl,ksh = NullFile(),NullFile(),NullFile(),NullFile(),NullFile()
			if setupOptions('csh'): csh = open('setup.csh','w')
			if setupOptions( 'sh'):  sh = open('setup.sh', 'w')
			if setupOptions( 'py'):  py = open('setup.py', 'w')
			if setupOptions( 'pl'):  pl = open('setup.pl', 'w')
			if setupOptions('ksh'): ksh = open('setup.ksh','w')
			shellHeader(csh,sh,py,pl,ksh)
			e.shellOut (csh,sh,py,pl,ksh)
			shellFooter(csh,sh,py,pl,ksh)
			csh.close(); sh.close(); py.close(); pl.close(); ksh.close()

	if r.ok() and (switch('removeall') or switch('remove-all')):
		for spec in home.topSpecs():
			r = Package.LazyPackage(spec).restore()
			r = Package.LazyPackage(spec).remove ()
			if not r.ok(): break
		r2 = home.refreshParents()
		if r.ok():
			removeFiles('setup.csh',    'setup.sh',    'setup.py',    'setup.pl',    'setup.ksh',  'trusted.caches')
			removeFiles('setup.csh.sav','setup.sh.sav','setup.py.sav','setup.pl.sav','setup.ksh.sav')
			os.chdir(home.UCL); home.save()
			Execution.execute('rm -r -f "'+pacmanDir+'"','x')
			r = r2

	if (switch('fetch') or switch('install') or switch('get') or switch('uninstall') and switch('l')): topspecs = home.topSpecs ( )
	if r.ok(): r = allReason(specParT('l'                    ),                lambda  spec: Package.LazyPackage(spec).displayM                  (depth))	
	if r.ok(): forall       (switchItems('lc'                ),                lambda cache:    UniversalCache.UniversalCache(cache).display          ())
	if r.ok() and switch('lc'      ) and len(switchItems('lc'    ))==0:                            UniversalCache.UniversalCache(  '.').display          ()
	if r.ok(): r = allReason(switchItems('oldsnap'), lambda cache: UniversalCache.UniversalCache(pathfix(cache)).snapshot(snapstring))
	if r.ok() and switch('oldsnap' ) and len(switchItems('oldsnap'  ))==0: r = UniversalCache.UniversalCache(  '.').snapshot(snapstring)
	if r.ok() and switch('mirror'  ) and len(switchItems('mirror')) >0: r = MirrorCache.mirrorCreate(switchItems('mirror'),mirrorstring)
	if r.ok() and switch('mirror'  ) and len(switchItems('mirror'))==0: r = MirrorCache.mirrorCreate(['.'],                mirrorstring)
	if r.ok() and switch('snapshot') and len(switchItems('snapshot')) >0: r = MirrorCache.mirrorCreate(switchItems('snapshot'),snapstring)
	if r.ok() and switch('snapshot') and len(switchItems('snapshot'))==0: r = MirrorCache.mirrorCreate(['.'],                  snapstring)
	if r.ok() and switch('snap'    ) and len(switchItems('snap'    )) >0: r = MirrorCache.mirrorCreate(switchItems('snap'    ),snapstring)
	if r.ok() and switch('snap'    ) and len(switchItems('snap'    ))==0: r = MirrorCache.mirrorCreate(['.'],                  snapstring)
	if r.ok(): r = allReason(switchItems('domain'            ),                lambda cache:    UniversalCache.UniversalCache(cache).domain           ())
	if r.ok() and switch('domain' ) and len(switchItems('domain'))==0:                      r = UniversalCache.UniversalCache(  '.').domain           ()
	if r.ok(): r = allReason(switchItems('extract-sources'   ),                lambda cache:    UniversalCache.UniversalCache(cache).extractSources   ())
	if r.ok() and switch('extract-sources') and len(switchItems('extract-sources'))==0:     r = UniversalCache.UniversalCache(  '.').extractSources   ()
	if r.ok(): r = allReason(switchItems('extract-downloads' ),                lambda cache:    UniversalCache.UniversalCache(cache).extractDownloads ())
	if r.ok() and switch('extract-downloads') and len(switchItems('extract-downloads'))==0: r = UniversalCache.UniversalCache(  '.').extractDownloads ()
	os.chdir(home.UCL); home.save()
#
#-- remove saved setup files unless -allow save-setup has been used.
#
	if r.ok() and not allow('save-setup'): removeFiles('setup.csh.sav','setup.sh.sav','setup.py.sav','setup.pl.sav','setup.ksh.sav')

except AbortException,message:
	lock.unlock()
	if switch('debug'): raise
	r = Reason(message.value)
except MemoryError:
	lock.unlock()
	tracebackSaver.tracebackSave()
	if switch('debug'): raise
	r = Reason('Not enough memory for attempted operation.')
except TypeError:
	lock.unlock()
	tracebackSaver.tracebackSave()
	if switch('debug'): raise
	r = Reason('Error in Pacman. Complain to Pacman Headquarters http://physics.bu.edu/pacman/.')
except UnboundLocalError:
	lock.unlock()
	tracebackSaver.tracebackSave()
	if switch('debug'): raise
	r = Reason('Error in Pacman. Complain to Pacman Headquarters http://physics.bu.edu/pacman/.')
except AttributeError:
	lock.unlock()
	tracebackSaver.tracebackSave()
	if switch('debug'): raise
	r = Reason('Error in Pacman. Complain to Pacman Headquarters http://physics.bu.edu/pacman/.')
except RuntimeError:
	lock.unlock()
	tracebackSaver.tracebackSave()
	if switch('debug'): raise
	r = Reason('Looping packages.')
except ValueError:
	lock.unlock()
	tracebackSaver.tracebackSave()
	if switch('debug'): raise
	r = Reason('Suspected transient IO error reading Pacman database.')
except KeyboardInterrupt:
	lock.unlock()
	tracebackSaver.tracebackSave()
	if switch('debug'): raise
	print '^C user interrupt.  Saving work so far...'
	r = Reason('Interrupted by ^C.')
except IOError:
	lock.unlock()
	tracebackSaver.tracebackSave()
	if switch('debug'): raise
	r = Reason('IO Error.')
except ImportError:
	lock.unlock()
	tracebackSaver.tracebackSave()
	if switch('debug'): raise
	r = Reason('Missing python module.  Import error.')

lock.unlock()
switchFinalize()

import freedisk
verbo.log('io','['+`freedisk.localmegs(pac_anchor)`+'] Megs of disk space free at the end of the installation.')
if freedisk.localmegs(pac_anchor)<100: 
	if r.ok(): r = Reason("** Out of disk space at ["+pac_anchor+"].")
	else:      print      "** Out of disk space at ["+pac_anchor+"]."

if not r.ok() or switch('verify'): r.display()
commandCheck.saveCommand(r)

#if flicker._count>0: sys.stdout.write('\n')
if hasattr(sys.stdout, 'clear'): sys.stdout.clear()

if r.ok(): sys.exit(0)
else:      sys.exit(1)



