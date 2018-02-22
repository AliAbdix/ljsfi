#python 2.4

import re

#
#--- classes
#

#module methods
def isBlank(text):
	#returns true if text is empty string or just whitespace
	#text = '  \t   \n \t', '', '\n'
	patt = re.compile(r'^\s*$')
	matcher = patt.search(text)
	return not matcher==None
def startsWithWhiteSpace(text):
	#text = ' \t \n\t  testing space\ttab\nnewline'
	patt = re.compile(r'^\s+.*$', re.DOTALL)	#start of string, some whitespace, anything (including more whitespace, and, because of DOTALL, newlines),,end of string
	matcher = patt.search(text)
	return not matcher==None
def removeWhiteSpace(text):
	#returns a string with all the whitespace in it removed
	#text = ' this \n is a \t test '	#-> 'thisisatest'
	patt = re.compile(r'\s+')
	return patt.sub('',text)
def condenseWhiteSpace(text):
	#returns a string with all the whitespace sections in it condensed to single spaces (so could still be leading and/or trailing single space)
	#also strips any leading and trailing whitespace
	#text = ' \t this \n is a \t test \n '	#-> 'this is a test'
	patt = re.compile(r'\s+')
	text = patt.sub(' ',text)
	if text.startswith(' '):
		text = text[1:]
	if text.endswith(' '):
		text = text[:-1]
	return text
def condenseWhiteSpaceExceptInPRE(text):
	#like condenseWhiteSpace, but doesn't do it for sections between html <pre></pre> tags
	#text = 'asfd<pre>this   is \n\tpreformatted\ttext</pre>this   is  not\n\tpreformatted\ttext'
	parts = text.split('<pre')	#(allow for attributes)
	parts[0] = condenseWhiteSpace(parts[0])
	i = 1
	while i<len(parts):
		work = parts[i].split('</pre>')
		parts[i] = work[0] + '</pre>' + condenseWhiteSpace(work[1])
		i += 1
	return '<pre'.join(parts)
def escapeForLiteral(text):
	#escapes backslash and quotes in text
	text = text.replace('\\','\\\\')
	text = text.replace('"','\\"')
	text = text.replace("'","\\'")
	return text
def convertHTMLtoText(text):
	#makes some simple substitutions, ignores other tags, condenses whitespace (except between pre tags)
	text = condenseWhiteSpaceExceptInPRE(text)
	text = text.replace('<i>', '')
	text = text.replace('</i>', '')
	text = text.replace('<b>', '')
	text = text.replace('</b>', '')
	text = text.replace('<br>', '\n')
	text = text.replace('<ul>', '')
	text = text.replace('</ul>', '')
	text = text.replace('<li>', '\n\t')
	text = text.replace('</li>', '')
	text = text.replace('<pre>', '\n')
	text = text.replace('</pre>', '\n')
	return text


#
#--- main
#
if __name__ == '__main__':
	pass

#
#--- fix
#

#
#--- todo
#
