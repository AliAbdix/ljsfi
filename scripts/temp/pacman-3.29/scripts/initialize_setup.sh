#setup.sh is initially a symlink to this script
#this script builds the real setup.sh (specific to the user's pacman location), replacing that link, and sources it
if [ -f scripts/build_python_if_necessary ]; then
	./scripts/build_python_if_necessary
	/usr/bin/env rm -f setup.sh
	echo '#'                                               >  setup.sh
	echo '#  % pacman -info to start'                      >> setup.sh
	echo '#'                                               >> setup.sh
	echo ''                                                >> setup.sh
	echo 'if [ -d "'"`pwd`"'/python/python/bin" ]; then'   >> setup.sh
	echo '    PATH="'"`pwd`"'/python/python/bin:${PATH}"'  >> setup.sh
	echo 'fi'                                              >> setup.sh
	echo 'export PATH'                                     >> setup.sh
	echo ''                                                >> setup.sh
	echo 'PATH="'"`pwd`"'/bin:${PATH}"'                    >> setup.sh
	echo 'export PATH'                                     >> setup.sh
	echo 'PACMAN_LOCATION="'"`pwd`"'"'                     >> setup.sh
	echo 'export PACMAN_LOCATION'                          >> setup.sh
	#echo 'if [ -n "${PYTHONPATH}" ]; then'                 >> setup.sh
	#echo '    PYTHONPATH="'"`pwd`"'/src:${PYTHONPATH}"'    >> setup.sh
	#echo 'else'                                            >> setup.sh
	#echo '    PYTHONPATH="'"`pwd`"'/src"'                  >> setup.sh
	#echo 'fi'                                              >> setup.sh
	#echo 'export PYTHONPATH'                               >> setup.sh
	. ./setup.sh
else
	echo '** cd into the untarred Pacman directory for the first setup.'
fi
