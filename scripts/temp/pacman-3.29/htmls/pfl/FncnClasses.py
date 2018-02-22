#python 2.4

class FncnCtgry:
	#defines a web page
	def __init__(self, keyName, fullName, order):
		self.keyName = keyName		#not None	#one word text, nickname
		self.fullName = fullName	#not None	#name of link, webpage, etc, to be printed
		self.order = order		#not None	#int for presentation order
	def __setattr__(self, attr, val):
		if attr in ('keyName', 'fullName', 'order'):
			if val == None:
				raise AttributeError, 'cannot set [' + attr + '] to None'
		self.__dict__[attr] = val

class FncnGrp:
	#defines a group in the webpage
	def __init__(self, keyName, dscrptn, fncnCtgry, order):
		self.keyName = keyName		#not None	#one word text, nickname
		self.dscrptn = dscrptn		#not None	#text
		self.fncnCtgry = fncnCtgry	#not None	#FncnCtgry.keyname to which it belongs
		self.order = order		#not None	#int for presentation order
	def __setattr__(self, attr, val):
		if attr in ('keyName', 'dscrptn', 'fncnCtgry', 'order'):
			if val == None:
				raise AttributeError, 'cannot set [' + attr + '] to None'
		self.__dict__[attr] = val

class Fncn: 
	#defines a function		
	#one for each form (diff params) of fuction
	#no primary key
	#	use fncnName and len(argmnts) as a primary key
	def __init__(self, fncnName, argmnts, dscrptn, fncnGrp, order):
		self.fncnName = fncnName	#not None	#name (without arguments)
		self.argmnts = argmnts				#list of Argmnt objects
		self.dscrptn = dscrptn				#individual description of function (not used on current pages)
		self.fncnGrp = fncnGrp		#not None	#FncnGrp.keyname to which it belongs
		self.order = order		#not None	#int for presentation order within group
	def __setattr__(self, attr, val):
		if attr in ('fncnName', 'fncnGrp', 'order'):
			if val == None:
				raise AttributeError, 'cannot set [' + attr + '] to None'
		self.__dict__[attr] = val

class Argmnt:
	def __init__(self, argName, needed):
		self.argName = argName		#not None	#text want printed in function specification
		self.needed = needed		#not None	#bool (if false, [] in spec); for this version (may be other function defined without the argument)
	def __setattr__(self, attr, val):
		if attr in ('argName', 'needed'):
			if val == None:
				raise AttributeError, 'cannot set [' + attr + '] to None'
		self.__dict__[attr] = val

class RowGrabber:
	#superclass of iterator that should return tuples of objects
	def __init__(self, mthd):
		self.mthd = mthd
	def __iter__(self):
		return self
	def next(self):
		#import_instances
		if self.mthd in ('import_instances'):
			self.counter += 1
			if self.counter >= len(self.l):
				self.counter = -1
				raise StopIteration
			return self.l[self.counter]
		else:
			assert 0, 'attempting use obselete method for RowGrabber implementation'

class FncnCtgryGrabber(RowGrabber):
	def __init__(self, mthd, **args):
		#possible args:
		#	filename: needed for 'import_instances' method
		if mthd not in ('import_instances'):
			assert 0, 'unsupported FncnCtgryGrabber method'
		if mthd == 'import_instances':
			if 'filename' not in args:
				assert 0, 'filename needs to be specified when using import_instances method'
			self.filename = args['filename']
		RowGrabber.__init__(self, mthd)
		##internal_list
		#if self.mthd == 'internal_list':
		#	self.l = []
		#	self.l.append(('basic',		'Basics',						1))
		#	self.l.append(('package',	'Packages etc.',					2))
		#	self.l.append(('version',	'Versions, releases tags, natively installed software',	3))
		#	self.l.append(('shell',		'Shells',						4))
		#	self.l.append(('system',	'System properties',					5))
		#	self.l.append(('grid',		'Grid atoms',						6))
		#	self.l.append(('file',		'File access manipulation',				7))
		#	self.counter = -1
		#import_instances
		if self.mthd == 'import_instances':
			exec 'junkcode = 0'		#I can't access filel from the execfile unless I exec something first; why?
			execfile(self.filename)
			self.l = [(ctgry.keyName, ctgry.fullName, ctgry.order) for ctgry in filel]
			self.counter = -1

class FncnGrpGrabber(RowGrabber):
	def __init__(self, mthd, **args):
		#possible args:
		#	filename: needed for 'import_instances' method
		if mthd not in ('import_instances'):
			assert 0, 'unsupported FncnGrpGrabber method'
		if mthd == 'import_instances':
			if 'filename' not in args:
				assert 0, 'filename needs to be specified when using import_instances method'
			self.filename = args['filename']
		RowGrabber.__init__(self, mthd)
		##internal_list
		#if self.mthd == 'internal_list':
		#	self.l = []
		#	self.l.append(('dltgz',		'---dltgz desc here---',	'basic',	1))
		#	self.l.append(('md5',		'---md5 desc here---',		'basic',	2))
		#	self.l.append(('env',		'---env desc here---',		'basic',	3))
		#	self.l.append(('platform',	'---platform desc here---',	'system',	1))
		#	self.l.append(('tcp',		'---tcp desc here---',		'system',	2))
		#	self.l.append(('rpm',		'---rpm desc here---',		'system',	3))
		#	self.l.append(('usrgrp', 	'---usrgrp desc here---',	'grid',		5))
		#	self.l.append(('perms',		'---perms desc here---',	'file',		1))
		#	self.l.append(('ownedBy',	'---ownedBy desc here---',	'file',		3))
		#	self.l.append(('chown',		'---chown desc here---',	'file',		4))
		#	self.counter = -1
		#import_instances
		if self.mthd == 'import_instances':
			exec 'junkcode = 0'		#I can't access filel from the execfile unless I exec something first; why?
			execfile(self.filename)
			self.l = [(grp.keyName, grp.dscrptn, grp.fncnCtgry, grp.order) for grp in filel]
			self.counter = -1

class FncnGrabber(RowGrabber):
	def __init__(self, mthd, **args):
		#possible args:
		#	filename: needed for 'import_instances' method
		if mthd not in ('import_instances'):
			assert 0, 'unsupported FncnGrabber method'
		if mthd == 'import_instances':
			if 'filename' not in args:
				assert 0, 'filename needs to be specified when using import_instances method'
			self.filename = args['filename']
		RowGrabber.__init__(self, mthd)
		##import_objlist
		#if self.mthd == 'import_objlist':
		#	from fncn_list_short import fncnlist
		#	self.l = [(fncn.fncnName, fncn.argmnts, fncn.dscrptn, fncn.fncnGrp, fncn.order) for fncn in fncnlist]
		#	self.counter = -1
		#import_instances
		if self.mthd == 'import_instances':
			exec 'junkcode = 0'		#I can't access filel from the execfile unless I exec something first; why?
			execfile(self.filename)
			self.l = [(fncn.fncnName, fncn.argmnts, fncn.dscrptn, fncn.fncnGrp, fncn.order) for fncn in filel]
			self.counter = -1

def buildFncnSpecFromDict(fncn):
	#returns string that's a function specification, eg userAdd(username [, group [, shell [, homedir]]]]), where fncn is a dictionary keyed according to the fncns DataTable as defined below
	fncnspec = fncn['fncnName'] + '('
	firstarg = True		#to determine if need to write ', '
	numoptargs = 0
	if not fncn['argmnts'] == None:
		for farg in fncn['argmnts']:
			if not farg.needed:
				fncnspec += ' ['
				numoptargs += 1
			if not firstarg:
				fncnspec += ', '
			else:
				firstarg = False
			fncnspec += farg.argName
		while numoptargs > 0:
			fncnspec += ']'
			numoptargs -= 1
	fncnspec += ')'
	return fncnspec

def buildDictFromFncnSpec(fncnspec, dscrptn=None, fncnGrp=None, order=None):
	#parses function specification string into dictionary keyed according to the fncns DataTable as defined below
	#fncnName and argmnts is taken from fncnspec, and others are just put in place as given
	#fncnspec should be string like userAdd(username [, group [, shell [, homedir]]]])
	#whitespace doesn't matter and will be removed before processing
	#if there are no arguments, dictionary 'argmnts' will be set to None
	#test with buildFncnSpecFromDict(buildDictFromFncnSpec('userAdd(username [, group [, shell [, homedir]]]])'))
	from TextProcessors import removeWhiteSpace
	fncnspec = removeWhiteSpace(fncnspec)

	parts = fncnspec.split('(',1)	#split into 'functionname' and 'argstuff)'

	fncnName = parts[0]
	argstuff = parts[1][:-1]	#strip off extra ')' at end of argument stuff

	if argstuff == '':
		argmnts = None
	else:
		argmnts = []
		nextargisopt = False
		for argstr in argstuff.split(','):
			argisopt = nextargisopt
			if argstr.startswith('['):	#only applies to first one (but makes things more likely to be forwards compatible, and like this should work regardless of relative position of ',' and '['
				argisopt = True
			if argstr.endswith('['):
				nextargisopt = True
				argstr = argstr[:-1]
			else:
				nextargisopt = False
			while argstr.endswith(']'):
				argstr = argstr[:-1]
			argmnts.append(Argmnt(argstr,not argisopt))
	return {'fncnName':fncnName, 'argmnts':argmnts, 'dscrptn':dscrptn,'fncnGrp':fncnGrp, 'order':order}


#
#--- fix
#
#use __setattr__ to make sure not None stay that way

#
#--- todo
