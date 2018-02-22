
from Base import *
import traceback,os,time,sys

def tracebackSave():
	path = os.path.join(pac_anchor,pacmanDir,'logs','tracebacks')
	etype, value, tb = sys.exc_info()
	list = traceback.format_exception(etype,value,tb)
		
	f = open(path,'a')
	for l in list: f.write(l)
	f.write('======= Above error occurred at =======> '+time.ctime(time.time())+'\n')
	f.close()


	
