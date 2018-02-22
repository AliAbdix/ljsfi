#
#	Copyright Saul Youssef, 2003
#
from Base       import *
from Platform   import *
from Registry   import *
import webbrowser,sys

class Switches(FixedNames):
	def __init__(self):
		self._names = [
				'-help','-h','--help',
				'-version',
				'-info',
				'-verbose','-v',
				'-quiet','-q',
				'-ask',
				'-ignore-cookies',
				'-ignore-platform',

				'-get',
				'-preview',
				'-fetch',
				'-install',
				'-installall',
				'-uninstall',
				'-uninstallall',
				'-remove',
				'-removeall',

				'-snapshot',

				'-check-updates',
				'-update',
				'-updateall',
				'-trust-registry',
				'-trust-all-caches',
				
				'-clear-registry',
				
				'-addpackage',
				'-satisfy','-satisfiable','-satisfied','-restore',

				'-remove-installation' ]
#		self._names = [ 
#			'-help',
#			'-clear-registry',
#			'-installall',
#			'-uninstall',
#			'-uninstallall',
#			'--help',
#			'-dump',
#			'-d',
#			'-no-html',
#			'-c',
#			'-quiet','-q',
#			'-repair',
#			'-addpackage',
#			'-locate',
#			'-h',
#			'-ignore-cookies',
#			'-compile',
#			'-ignore-platform',
#			'-version',
#			'-installable',
#			'-satisfy','-satisfiable','-satisfied','-restore',
#			'-info',
#			'-verbose','-v',
#			'-ask',
#			'-prefetch','-resolve',
#			'-get','-fetch','-install','-reinstall','-verify',
#			'-remove','-removeall',
#			'-snapshot','-setup','-outfiles',
#			'-checkupdates','-update','-updateall','-autoupdate',
#			'-trust','-trust-registry','-trust-all-caches','-removeinstallation',
#			'-ignorecookies' ]

def commandLine():
	reason = Reason()
	SW = Switches()	
	for sw in switches:
		sw2 = string.split(sw,':')[0]
		if not sw2 in SW:
			pacmanCommands()
			reason = Reason("Unknown command line switch ["+sw2+"].")
			break
			abort("Unknown command line switch ["+sw2+"].")

	if switch('help') or switch('h') or switch('-help') or (len(switches)==0 and len(params)>0):
		pacmanCommands()
		sys.exit(0)
	if switch('clear-registry'):
		registry.clear_registry()
	if switch('info'):
		launchwebdisplay()
		sys.exit(0)
	if switch('version') or switch('verbose') or switch('v'):
		print 'Pacman version:  '+version
		print 'Python version: ',sys.version
		if switch('verbose') or switch('v'):
			p = Platform(); pl = Platform().platforms(); pl.reverse()
			print 'Platform: ',Platform(),'also satisfies',[x for x in pl if x!=p.str()]
		else:
			print 'Platform: ',`Platform()`
		if switch('version'): sys.exit(0)
	return reason
	
def launchwebdisplay(start='htmls/index.html'):
		if not os.path.exists(start): abort("Missing ["+start+"].  Can't display web page.")
		try:
			webbrowser.open(os.path.join(os.getcwd(),start),new=0)
		except:
			print 'Warning: Failed to launch web browser...'
	
	
def pacmanCommands():
	print 'Use:    pacman {Options} <package1> <package2> ... '
	print 'Options: '
	print '    -help, -h              To get this message.'
	print '    -version               Show version number.'
	print '    -info                  Show installation web pages.'
	print '    -verbose, -v           Show verbose messages.'
	print '    -quiet, -q             Show few messages.'
	print '    -ask                   Ask before executing shell commands.'
	print '    -ask:mode              Ask for mode = {root-shell,all-shell}'
	print ' '
	print '    -get                   Fetch and install the indicated packages.'
	print '    -preview               Check if installation will work on your system.'
	print '    -install               Install the indicated packages.'
	print '    -fetch                 Fetch the indicated packages.'
	print '                               '
	print '    -verify                Verify the integrity of the indicated packages.'
	print '    -repair                Repair the indicated packages.'
	print ' '
	print '    -remove                Remove the indicated packages.'
	print '    -removeall             Remove all packages in the installation.'
	print ' '
	print '    -snapshot              Generate a snapshot of the indicated packages.'
	print '    -setup                 Generate setup scripts for the indicated packages.'
	print ' '
	print '    -check-updates         Check if updates are available.'
	print '    -update                Update the indicated packages.'
	print '    -updateall             Update all packages which have an update.'
#	print '    -autoupdate            Set up automatic updating of the installation.'
	print ' '
	print '    -trust-registry        Automatically trust all registered caches.'
	print '    -trust-all-caches      Automatically trust all caches.'
	print ' '
	print '    -remove-installation   Remove the entire installation.'
	print ' '
