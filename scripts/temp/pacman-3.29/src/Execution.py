#
#	Copyright, Saul Youssef, 2005
#
from Base  import *
from CU    import *
from Alias import *
import sys,commands

def sustr(command):
	reason,user = currentUser()
	if not reason.ok(): abort(reason.reason)
	if user==getusername(): return command
	else:
		if switch('sudo'):
			return 'sudo -c "'+command+'" '+user
		else:   
			if    not '"' in command and not "'" in command: return 'su -c "'+command+'" '+user
			elif  not '"' in command and     "'" in command: return "su -c '"+command+"' "+user
			elif      '"' in command and not "'" in command: return "su -c '"+command+"' "+user
			else: return 'su -c """'+command+'""" '+user

def execute(command,mode='noclear'):
	reason,output = executeBase(command,mode)
	return reason

def executeBase(command,mode='noclear'):
	reason = Reason(); output = 'ok'
	try:
		reason,currentuser = currentUser()
		if reason.ok():
			if mode=='compatibility': com = sustr(alias(os.path.expandvars(command)))
			else:                     com = sustr(alias(                   command) )
			if verbo('shell-out'): print 'About to execute ['+com+'] as user ['+currentuser+'] at ['+os.getcwd()+'].'
			if ask('shell-all','About to execute ['+com+'] as user ['+currentuser+'] at ['+os.getcwd()+']. OK?'):
				if currentuser!='root' or ask('root-shell','About to execute ['+os.path.expandvars(command)+'] as user ['+currentuser+'] at ['+os.getcwd()+']. OK?'):
					verbo.log('shell-all','About to execute ['+com+'] as user ['+currentuser+'] at ['+os.getcwd()+'].')
					if (mode=='compatibility' or debug('os.system')) and not debug('os.popen'):
						if hasattr(sys.stdout,'clear') and mode.count('noclear')==0: sys.stdout.clear()
						status = os.system(com)
						if status!=0: output = 'Shell command ['+com+'] returns with an error code.'
						else:         output = ''
						if debug('shell'):
							print 'os.system('+com+')'
							if os.environ.has_key('PATH'): print 'PATH='+os.environ['PATH']
							else:                          print 'PATH undefined'
							print 'status=',status
							print 'output=['+output+']'
						verbo.log('shell-all','Finished executing ['+com+'] as user ['+currentuser+'] at ['+os.getcwd()+'].')
					else:
						if hasattr(sys.stdout,'clear') and mode.count('noclear')==0: sys.stdout.clear()
						status,output = commands.getstatusoutput(com)
						if debug('shell'):
							print 'commands.getstatusoutput('+com+')'
							if os.environ.has_key('PATH'): print 'PATH='+os.environ['PATH']
							else:                          print 'PATH undefined'
							print 'status=',status
							print 'output=['+output+']'
					verbo.log('shell-all','Finished executing ['+com+'] as user ['+currentuser+'] at ['+cwdd()+'].')
					if status!=0: reason.reason(output)

					if output!='':
						if verbo('shell-out'): print output
						if not os.path.exists(os.path.join(pac_anchor,pacmanDir,'logs','shellout.log')):
							verbo.log('io','Creating shellout.log...')
							try:
                                                                # Bug fix by Scot Kronenfeld 2/2009
                                                                # Switched from f.open(...
								f = open(os.path.join(pac_anchor,pacmanDir,'logs','shellout.log'),'w')
								f.write('- Shell output log\n')
								f.close()
							except:
								pass
						try:
							f = open(os.path.join(pac_anchor,pacmanDir,'logs','shellout.log'),'a')
							if verbo('io'): print 'Writing to shellout.log...'
							f.write('shell command> '+command+'\n')
							f.write(output+'\n')
							f.close()
						except (IOError,OSError):
							pass
#							reason = Reason("Can't write shell output to log file.")
				else:
					reason = Reason('Installer has denied permission to execute ['+command+'] as root.')
			else:
				reason = Reason('Installer has denied permission to execute ['+command+'].')			
#-- Check in case the users shell command has removed the cwd
			try:
				cwdir = os.getcwd()
			except (IOError,OSError):
				reason.append(Reason('Shell command ['+command+'] has removed the current directory.'))
	except (IOError,OSError):
		reason.reason('Shell command ['+command+'] returns with an error.')
	if debug('ignoreShellError'): reason = Reason()
	return reason,output	

