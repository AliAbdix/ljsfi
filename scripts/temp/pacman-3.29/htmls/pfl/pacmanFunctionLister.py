#python 2.4

from sys import argv, stdout, exit
from datetime import datetime
import os
import re

from DataTableClasses import *
from TextProcessors import *
from FncnClasses import *
from html_template import *

#
#--- classes and helpers
#
def processCtgryFile(dfilename, cfilename, gfilename, ffilename):
	#reads entire definition file and appends to the python code files
	#uses filenames as is
	def parseKeyName(text):
		#text = '  \t   	[keyName]  \n'
		patt = re.compile(r'\s*\[(.[^\s]*)\]\s*')	#any whitespace, a '[', one or more characters that aren't whitespace (could include multiple '[' or ']'), a ']', any whitespace
		matcher = patt.search(text)
		if matcher == None:
			assert 0, 'bad definition file format'
		return matcher.group(1)
	def parseFullNameOrOrder(text):
		#text = '  \t   	[this is the fullName or order]  \n'
		patt = re.compile(r'\s*\[(.+)\]\s*')		#any whitespace, a '[', one or more characters (could include multiple '[' or ']'), a ']', any whitespace
		matcher = patt.search(text)
		if matcher == None:
			assert 0, 'bad definition file format'
		return matcher.group(1)

	dfile = open(dfilename, 'r')
	cfile = open(cfilename, 'a')
	gfile = open(gfilename, 'a')
	ffile = open(ffilename, 'a')

	i= 0			#line counter
	d = dfile.readlines()

	#get all the category data
	#keyName
	while isBlank(d[i]): i += 1
	ctgry_keyName = parseKeyName(d[i])
	i += 1
	#fullName
	while isBlank(d[i]): i += 1
	ctgry_fullName = parseFullNameOrOrder(d[i])
	i += 1
	#Order
	while isBlank(d[i]): i += 1
	ctgry_order = parseFullNameOrOrder(d[i])
	i += 1
	#write out the category data
	cfile.write("filel.append(FncnCtgry('" + escapeForLiteral(ctgry_keyName) + "','" + escapeForLiteral(ctgry_fullName) + "'," + ctgry_order + "))\n")

	#get all the groups, and all their functions		
	grpi = 0		#group counter; for naming the groups (as of right now, all internal), and for ordering
	while i < len(d):
		while isBlank(d[i]):
			i += 1
			if not i < len(d): break
		if not i < len(d): break
		#initialize stuff for the group
		grp_keyName = ctgry_keyName + 'grp' + str(grpi)
		fncni = 0	#function counter (per group); for ordering
		#get all the functions for the group
		while not isBlank(d[i]):
			#get the fncnName and argmnts
			fncndict = buildDictFromFncnSpec(d[i])
			i += 1
			#get dscrptn
			fncndscrptnstr = ''
			while not isBlank(d[i]) and startsWithWhiteSpace(d[i]):
				fncndscrptnstr += d[i]
				i += 1
			if fncndscrptnstr == '':
				dscrptncode = None
			else:
				dscrptncode = "'''" + escapeForLiteral(fncndscrptnstr) + "'''"
			#build the code for list of argument constructors
			if fncndict['argmnts'] == None:
				argcode = 'None'
			else:
				argcode = '['
				firstarg = True
				for arg in fncndict['argmnts']:
					if not firstarg:
						argcode += ','
					firstarg = False
					argcode += "Argmnt('" + escapeForLiteral(arg.argName) + "'," + str(arg.needed) + ")"
				argcode += ']'
			#if len(fncndict['argmnts']) == 0
			ffile.write("filel.append(Fncn('" + escapeForLiteral(fncndict["fncnName"]) + "'," + argcode + "," + str(dscrptncode) + ",'" + escapeForLiteral(grp_keyName) + "'," + str(fncni) + "))\n")
			fncni += 1
		#get the group description
		while isBlank(d[i]): i += 1
		grpdscrptnstr = ''
		while i<len(d) and not isBlank(d[i]):
			grpdscrptnstr += d[i]
			i += 1
		gfile.write("filel.append(FncnGrp('" + escapeForLiteral(grp_keyName) + "','''" + escapeForLiteral(grpdscrptnstr) + "''','" + escapeForLiteral(ctgry_keyName) + "'," + str(grpi) + "))\n")
		grpi += 1
	for iofile in (dfile, cfile, gfile, ffile): iofile.close()

def writeindex():
	#---- header printing
	if style == 'text':
		pass
	elif style == 'html':
		o.write(htmlcomments + htmltitlestart + html_index_title + htmltitleend + htmlbodystart + htmlheaderstart + html_index_header + htmlheaderend + html_index_mainpagestart)
	#----

	writefncns(fncnorder='fncnName')

	#--- footer printing
	if style == 'text':
		pass
	elif style == 'html':
		o.write(htmlmainpageend + htmlfooterstart + htmlfooterend + htmlbodyend)

def writectgry(whichctgry):
	#makes a whole category page
	#(to redirect output, redefine the writer o before calling)
 	cat = ctgrys.select('keyName', whichctgry)
 	if len(cat) == 0:
 		assert 0, 'no such function category'
	
	#---- header printing
	if style == 'text':
 		o.write(cat[0]['fullName'] + '\n')
 		o.write('='*70 + '\n')
	elif style == 'html':
		o.write(htmlcomments + htmltitlestart + cat[0]['fullName'] + htmltitleend + htmlbodystart + htmlheaderstart + cat[0]['fullName'] + htmlheaderend + htmlmainpagestart)
		if whichctgry in html_individual_top:
			o.write(html_individual_top[whichctgry])
	#----
	
	writegrps(fncnCtgry=cat[0]['keyName'], grporder='order', fncnorder='order')

	#--- footer printing
	if style == 'text':
		pass
	elif style == 'html':
		if whichctgry in html_individual_bottom:
			o.write(html_individual_bottom[whichctgry])
		o.write(htmlmainpageend + htmlfooterstart + htmlfooterend + htmlbodyend)

def writegrps(fncnCtgry, grporder, fncnorder, withHTMLanchors=True):
	#writes all the function groups (functions and group descriptions) belonging to fncnCtgry
	#grporder and fncnorder are the respective keys to the columns by which to sort the data
	#if withHTMLanchors, and style is 'html' ...
	catgrps = grps.select('fncnCtgry', fncnCtgry)
 	catgrps.sort(grporder)
 	for grp in catgrps:
 		grpfncns = fncns.select('fncnGrp', grp['keyName'])
 		grpfncns.sort(fncnorder)
 		firstfncn = True		#(to determine if need to write ', ')
		#--- group printing 1/2
		if style == 'text':
			pass
		elif style == 'html':
			o.write(htmlgrpstart)
		#---
 		for fncn in grpfncns:
 			if not firstfncn:
				#---- function printing 1/2
				if style == 'text':
 					o.write(', ')
				elif style == 'html':
					o.write(htmlfncnseparator)
				#----
 			else:
				firstfncn = False
			fncnspec = buildFncnSpecFromDict(fncn)
			#---- function printing 2/2
			if style == 'text':
				o.write(fncnspec)
 			elif style == 'html':
				o.write(htmlfncnstart)
				if withHTMLanchors:
					keyName = makeFncnPrimKey(fncn)
					o.write('<a name="' + keyName + '" id="' + keyName + '">')
					#o.write('<a id="' + keyName + '">')
				o.write(convertFncnSpecToHTML(fncnspec))
				if withHTMLanchors:
					o.write('</a>')
				o.write(htmlfncnend)
			#----
 		firstfncn = True
		#---- group printing 2/2
		if style == 'text':
 			o.write('\n\t' + convertHTMLtoText(grp['dscrptn']) + '\n\n')
		elif style == 'html':
			o.write(htmldscrptnstart + grp['dscrptn'] + htmldscrptnend)

def writefncns(fncnorder, withHTMLanchors=True):
	#writes all functions, ordered by the column keyed by fncnorder
	fncns.sort(fncnorder)
	for fncn in fncns:
		fncnspec = buildFncnSpecFromDict(fncn)
		ctgrykeyName = grps.select('keyName', fncn['fncnGrp'])[0]['fncnCtgry']
		#---- function printing
		if style == 'text':
 			o.write(fncnspec + '\n')
			if fncn['dscrptn']:
				o.write('\t' + fncn['dscrptn'] + '\n')
			o.write('\n')
		elif style == 'html':
			if withHTMLanchors:
				o.write('<a href="' + ctgrykeyName + '.html#' + makeFncnPrimKey(fncn) + '" ' + html_index_linkattributes + '>')
			o.write(convertFncnSpecToHTML(fncnspec))
			if withHTMLanchors:
				o.write('</a>')
			o.write('<br>\n')
			if fncn['dscrptn']:
				o.write(html_index_fncndscrptnstart + fncn['dscrptn'] + html_index_fncndscrptnend)
		#----

def makeFncnPrimKey(fncn):
	#there's no such thing as Fncn.keyName, so make something unique (usually for an anchor tag) by combining the function name with its number of arguments
	if fncn['argmnts']:
		numargs = len(fncn['argmnts'])
	else:
		numargs = 0
	return fncn['fncnName'] + str(numargs)

def convertFncnSpecToHTML(fncnspec):
	fncnspec = fncnspec
	fncnspec = fncnspec.replace(' ', htmlfncnspecspacereplacement)
	fncnspec = fncnspec.replace('(', htmlargsstart+'(')
	fncnspec = fncnspec.replace(')', ')'+htmlargsend)
	return fncnspec


#
#-- main
#
if __name__ == '__main__':
	o = stdout
	
#parse user input (and define some parameters)
	#if no arguments are given, make all the pages
	#output will be saved in files named according to category keyNames
	if len(argv) == 1:
		whichctgry = '_all_'
		style = 'html'
	else:
		#pick which page (based on category) to make ('_index_' means all functions on one page)
		if len(argv) < 3:
			print 'ERROR:'
			print 'If passing arguments, two arguments are needed:'
			print '\tcategory (_index_ for the listing of all functions)'
			print '\tstyle (text, html)'
			exit()
		whichctgry = argv[1]
		#pick the style
		style = argv[2]
		if style not in ('text', 'html'):
			print 'ERROR:'
			print '\tunknown style [' + style + ']'
			exit()
	defdirname = os.path.join(os.getcwd(),'def')
	tmpdirname = os.path.join(os.getcwd(),'tmp')
	outputdirname = os.path.join(os.getcwd(),'output')
	cfilename = os.path.join(tmpdirname,'ctgrys.py')
	gfilename = os.path.join(tmpdirname,'grps.py')
	ffilename = os.path.join(tmpdirname,'fncns.py')
	indexfilename = os.path.join(outputdirname,'fncn_index.html')
	leavefiles = False		#leave behind the temporary files that are created?
	leavetmpdir = leavefiles	#even if not leavefiles, tmpdir will be left behind if it was already there
	
#parse definition files
	#initialize instance files
	if not os.path.isdir(tmpdirname):
		os.mkdir(tmpdirname)
	else:
		leavetmpdir = True
	cfile = open(cfilename, 'w')
	gfile = open(gfilename, 'w')
	ffile = open(ffilename, 'w')
	for outfile in (cfile, gfile, ffile):
		outfile.write('#' + str(datetime.today()) + '\n')
		outfile.write('#This file is generated by pacmanFunctionLister.py\n')
		outfile.write('#If you want changes to stick around, make them in the corresponding definition files, not here\n')
		outfile.write('filel = []\n')
		outfile.close()
	#convert each definition file to python code for constructing the objects
	for deffilename in os.listdir(defdirname):
		deffilename = os.path.join(defdirname,deffilename)
		processCtgryFile(deffilename, cfilename, gfilename, ffilename)
	
#populate records
	#populate the DataTables from the python files
	ctgrys = DataTable(('keyName', 'fullName', 'order'))
	ctgrys.populate(FncnCtgryGrabber('import_instances', filename=cfilename))
	
	grps = DataTable(('keyName', 'dscrptn', 'fncnCtgry', 'order'))
	grps.populate(FncnGrpGrabber('import_instances', filename=gfilename))
	
	fncns = DataTable(('fncnName', 'argmnts', 'dscrptn', 'fncnGrp', 'order'))
	fncns.populate(FncnGrabber('import_instances', filename=ffilename))
	
	#delete temporary files, if told to do so
	if not leavefiles:
		for filename in (cfilename, gfilename, ffilename):
			os.remove(filename)
		if not leavetmpdir:
			os.rmdir(tmpdirname)
	
#print out page(s)
	#do everything?
	if whichctgry == '_all_':
		if not os.path.isdir(outputdirname):
			os.mkdir(outputdirname)
		prevo = o
		
		#write each ctgry page
		for ctgry in ctgrys:
			outputfilename = os.path.join(outputdirname,ctgry['keyName'])
			o = open(outputfilename + '.html', 'w')
			writectgry(ctgry['keyName'])
			o.close()
		
		#write the index page
		o = open(indexfilename, 'w')
		writeindex()
		o.close()
		
		o = prevo
	#all functions on one page?
	elif whichctgry == '_index_':
		writeindex()
	#functions of one category, sorted by groups (corresponding to a current page)
	else:
		writectgry(whichctgry)


#
#--- fix
#
#BUG: orders don't work if non-int (need to be enclosed in quotes in python code)
#put more of the Grabber code in superclass now that differences are obselete
#	eg, for 'import_instances' method, the only difference is the tuple itself
#don't have external code make a list; have it just make instances, and read in with module.__dict__
#don't have all the different if style, make a format structure, with text fillers and processing functions, and assign it once
#	use dictionary for forward compatibility, pass for no processing

#
#--- todo
#
#repeatable arguments is not yet implemented, and only shows up in constructor; maybe should just get rid of
#	search for ARGREPEATABLE
#	actually, take it all out, since repeatable argument can be specified as an additional argument named "..."
#when print all functions, if same name, sort by number of parameters
#other, just for practice
#	use packages (__init__.py, etc)
#use __setattr__ stuff in FncnClasses to make sure wrong things aren't being set to None
