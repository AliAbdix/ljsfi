#
#	Copyright, August 2003, Saul Youssef
#
from Base import *

compilerswitches = [    '-help',
			'--help',
			'-dump',
			'-d',
			'-c',
			'-quiet','-q',
			'-no-anchor',
			'-display',
			'-repair',
			'-locate',
			'-h',
			'-ignore-cookies',
			'-compile',
			'-ignore-platform',
			'-pretendPlatform',
			'-version',
			'-installable',
			'-satisfy','-satisfiable','-satisfied','-restore',
			'-info',
			'-verbose','-v',
			'-ask',
			'-prefetch','-resolve',
			'-get','-fetch','-install','-reinstall','-verify',
			'-remove','-removeall',
			'-snapshot','-setup','-outfiles',
			'-checkupdates','-update','-updateall','-autoupdate',
			'-trust','-trust-registry','-trust-all-caches','-removeinstallation',
			'-ignorecookies' ]
			
def compilerCommandLine():
	for sw in switches: 
		if not sw in compilerswitches and 0: 
			abort('Unknown command line switch ['+sw+'].')
			
