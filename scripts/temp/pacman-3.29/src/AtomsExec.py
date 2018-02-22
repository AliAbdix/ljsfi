#
#	Copyright Saul Youssef, July, 2003
#
from Environment    import *
from Atoms          import *
import sys

def newAttributeExec(string):
	if newAttributeText(string):
		x = 'ens = '+string
		try:
			exec x
		except (SyntaxError,NameError,TypeError):
			abort('Syntax error in ['+string+'].')
	else:
		ens = AND()
		
	return ens

