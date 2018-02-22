#
#	Copyright, Saul Youssef, 2004
#
from Base import *
import os,string

def dictParser(text):
	if '{' in text:
		text2 = text[string.find(text,'{'):]
		return dp2(text2)
	else:
		abort('Syntax error in ['+text+'].')
		
def dp2(text):
	t = string.strip(text)
	if len(t)>2 and t[0]=='{' and t[-1]=='}':
		return dp3(t[1:-1])
	else:
		abort('Syntax error in ['+t+'].')

def dp3(text):
	l = string.split(string.strip(text),',')
	ds = []
	for ll in l:
		if not string.strip(ll)=='':
			ds.append(dp4(ll))
	return ds
		
def dp4(text):
	l = string.split(text,':')
	if len(l)==2:
		tx = string.strip(l[0])
		exec("xx = "+tx)
		ty = string.strip(l[-1])
		exec("yy = "+ty)
		
		return xx,yy
	else:
		abort('Syntax error in ['+text+'].')

