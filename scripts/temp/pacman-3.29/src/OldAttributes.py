#
#	Copyright Saul Youssef, July 2003
#
from Base import *

class OldAttributes(List):
	def __init__(self):
		self.attributes = [
			'description',
			'url',
			'name',
			'localdoc',
			'source',
			'systems',
			'depends',
			'inpath',
			'bins',
			'paths',
			'enviros',
			'exists',
			'daemons',
			'install',
			'setup',
			'demo',
			'uninstall',
			'nativelyInstalled',
			'suffixHandling',
			'usePackageRoot',
			'download',
			'requires',
			'systemSetenv',
			'packageName',
			'localInstallation',
			'remoteInstallation' ]
			
	def __eq__      (self,x):       return self.attributes == x.attributes
	def __getitem__ (self,i):       return self.attributes[i]
	def __len__     (self):         return len(self.attributes)
	def isAtt       (self,string):  return self.attributes.count(string)>0
	def allAtt      (self,strings): return forall(strings,lambda s: self.isAtt(s))
