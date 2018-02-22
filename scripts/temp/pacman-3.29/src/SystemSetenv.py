#
#	Copyright, August 2003, Saul Youssef
#
from EnvironmentVariable import *

class SystemSetenv(Setenv):
	type   = 'system environment variable'
	title  = 'System Environment Variables'
	action = 'set a system environment variable'

