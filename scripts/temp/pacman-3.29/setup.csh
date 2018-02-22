#setup.csh is initially a symlink to this script
#this script builds the real setup.csh (specific to the user's pacman location), replacing that link, and sources it
if (-f scripts/build_python_if_necessary) then
	./scripts/build_python_if_necessary
	/usr/bin/env rm -f setup.csh
	echo '#'                                                      >  setup.csh
	echo '#  % pacman -info to start'                             >> setup.csh
	echo '#'                                                      >> setup.csh
	echo ''                                                       >> setup.csh
	echo 'if (-d "'"`pwd`"'/python/python/bin") then'             >> setup.csh
	echo '    setenv PATH "'"`pwd`"'/python/python/bin:${PATH}"'  >> setup.csh
	echo 'endif'                                                  >> setup.csh	
	echo ''                                                       >> setup.csh
	echo 'setenv PATH "'"`pwd`"'/bin:${PATH}"'                    >> setup.csh
	echo 'setenv PACMAN_LOCATION "'"`pwd`"'"'                     >> setup.csh
	#echo 'if ($?PYTHONPATH) then'                                 >> setup.csh
	#echo '    setenv PYTHONPATH "'"`pwd`"'/src:${PYTHONPATH}"'    >> setup.csh
	#echo 'else'                                                   >> setup.csh
	#echo '    setenv PYTHONPATH "'"`pwd`"'/src"'                  >> setup.csh
	#echo 'endif'                                                  >> setup.csh
	source ./setup.csh
else
	echo '** cd into the untarred Pacman directory for the first setup.'
endif

