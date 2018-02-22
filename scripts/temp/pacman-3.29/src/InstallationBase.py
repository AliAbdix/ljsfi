#
#	Copyright, Saul Youssef, August 2004
#
from Environment         import *
from TextFile            import *
from Cp                  import *
from Message             import *
from PacmanVersion       import *
from Username            import *
from Anchor              import *
from EnvironmentVariable import *
from Registry            import *
from Platform            import *
from CommandLineSwitch   import *
from FileExists          import *
from Choice              import *
from CD                  import *
from DB                  import *
import Base
import Directory
#
#   returns the standard environment for a Pacman installation area
#
def installationBase(options=''):
	I = AND()
	
#-- optionally check if non-empty directory
	if not contains(options,'quiet'):
	        I.extend(OR(CommandLineSwitch('q'),DirectoryEmpty(os.getcwd()),FileExists(pacmanDir),FileExists('trusted.caches'),Choice('y','Current directory is not empty.  Are you sure you want to start a Pacman installation here?','y','n')))

	I.extend(          Setenv('PAC_ANCHOR','.'))
	if not allow('moveable-installations'):
		I.extend(                  Anchor())  # Fixes installation location
	if not allow('any-username'):
		I.extend(   Username(getusername()))  # Fixes installer
	
	I.extend(         PacmanVersionGE( version))  # Pacman version
#	I.extend(         PacmanVersionLT('3.2000'))  # Upper bound on version
	I.extend(         PacmanVersionLT('3.9000'))  # Upper bound on version
	I.extend(                  DateOfCreation())  # Date of creation
	if not switch('any-platform'):
		I.extend(                Platform())  # Platform used

#-- directories
	I.extend( Directory.Directory(      pacmanDir))
	I.extend(        CD(      pacmanDir))
#-- starter preference and README file
	I.extend(TextFile('README',['#','#  This directory contains the Pacman internal ', \
	                                '#  representation of your software environment.', \
					'#  ',\
					'#  DO NOT MODIFY ANY FILES IN THIS DIRECTORY',\
					'#']))

#	I.extend(        DB('ii'+version[:3]))  # Installation database
#	I.extend( Directory('ii'+version[:3]))
	if use_old_database: I.extend( Directory.Directory('ii'+version[:3]))
	else: I.extend(  Dict('ii'+version[:3]))
	I.extend(      Dict('is'+version[:3]))
	I.extend(      Dict('ie'+version[:3]))
	I.extend(      Dict('sh'+version[:3]))
	I.extend(      Dict('tr'+version[:3]))
	I.extend( Directory.Directory(         'logs'))
	I.extend( Directory.Directory(      'cookies'))
	I.extend( Directory.Directory(  'preferences'))
	
#	I.extend(AND(CD('preferences'),TextFile('v',['down pac tar up meter']),CD()))
	I.extend(AND(CD('preferences'),TextFile(     'v',['download-brief cache-brief tar-brief pac-brief up retry']),  CD()))
	I.extend(AND(CD('preferences'),TextFile( 'retry',['10 pause-30-seconds']),             CD()))
	I.extend(AND(CD('preferences'),TextFile('setups',['csh sh']),                         CD()))
	I.extend(AND(CD('preferences'),TextFile(   'ask',['tar-overwrite']),                  CD()))
	
	I.extend( Directory.Directory(       'htmls'))
	I.extend( Directory.Directory(   'snapshots'))
	I.extend( Directory.Directory(   'downloads'))
	I.extend( Directory.Directory(    'registry'))
	I.extend( Directory.Directory(         'tmp'))
	I.extend( Directory.Directory(       'saves'))
	ok,tarname = Base.gnuTarFinder()
	I.extend( TextFile('tar',[tarname]))
	I.extend(LocalRegistry())
	
#-- html index file for multi-site installations
	index = []
	index.append('<head><title>Pacman Environment at '+os.getcwd()+'</title></head>')
	index.append('<frameset cols="80%,20%">')
	index.append('<frame src="preview.html" name="mainwindow">')
	index.append('<frame src="menubar.html"     name="sidemenu">')
	index.append('</frameset>')
	index.append('</html>')
	I.extend(TextFile('htmls/index.html',index))
	
#-- graphics
#	I.append (AND(  Copy('$PACMAN_LOCATION/htmls/green.gif','htmls'),         \
#		     	Copy('$PACMAN_LOCATION/htmls/bullet1.gif','htmls'),       \
#			Copy('$PACMAN_LOCATION/htmls/bulletcross.gif','htmls'),   \
#			Copy('$PACMAN_LOCATION/htmls/orangeup.gif','htmls'),      \
#			Copy('$PACMAN_LOCATION/htmls/orangeupmild.gif','htmls'),  \
#			Copy('$PACMAN_LOCATION/htmls/sky.gif','htmls'),           \
#			Copy('$PACMAN_LOCATION/htmls/redstar.gif','htmls')))
	I.append(AND(Copy('$PACMAN_LOCATION/htmls/sky.gif','htmls')))
	I.extend(        CD(              ))

#-- Starter caches file
	caches = []
	caches.append('#')
	caches.append('#  - List of trusted Pacman Caches -')
	caches.append('#')
	caches.append('# Pacman will modify this file, but you can also edit it by hand at any time.')
	caches.append('#')
	I.extend(TextFile('trusted.caches',caches))
			
	return I

