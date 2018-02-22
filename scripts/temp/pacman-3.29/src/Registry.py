#
#	Copyright, Saul Youssef, August 2004
#
from Environment import *
import pickle

def registry0():
	reg = {}
	reg['ATLAS']      = Register(      'ATLAS',  'http://atlas-computing.web.cern.ch/atlas-computing/links/monolith/whole/ATLAS.caches',                 'The Atlas Experiment, CERN',  'http://atlas.web.cern.ch/Atlas/GROUPS/SOFTWARE/OO/sit/Distribution/', 'SIT', 'atlas-sw-sit@cern.ch')
	reg['Atlas']      = Register(      'Atlas',  'http://atlas.web.cern.ch/Atlas/GROUPS/SOFTWARE/OO/pacman/whole/ATLAS.caches',                 'The Atlas Experiment, CERN',  'http://atlas.web.cern.ch/Atlas/GROUPS/SOFTWARE/OO/sit/Distribution/', 'SIT', 'atlas-sw-sit@cern.ch')
#	reg['am-UM']      = Register(      'am-UM',  'http://gate01.grid.umich.edu/am-UM/ATLAS.mirror','ATLAS Great Lakes Tier 2 Center','University of Michigan','Shawn McKee','smckee@umich.edu')
	reg['am-UM']      = Register(      'am-UM',  'http://gate01.aglt2.org/am-UM/ATLAS.mirror/','ATLAS Great Lakes Tier 2 Center','University of Michigan','Shawn McKee','smckee@umich.edu')
	reg['am-IU']      = Register(      'am-IU',  'http://pacman.uits.indiana.edu/atlas/Atlas.mirror/','ATLAS Midwest Tier 2 Center','Indiana University','Kristy Kallbac-Rose','kallbac@indiana.edu')
	reg['am-RAL']     = Register(     'am-RAL',  'http://atlassw.gridpp.rl.ac.uk/ATLAS.mirror/','ATLAS UK Tier 1 Centre','Rutherford Appleton Laboratory','lcg-support','lcg-support@gridpp.rl.ac.uk')
	reg['am-CERN']    = Register(    'am-CERN',  'http://atlas-install00.cern.ch/am-CERN/ATLAS.mirror/','ATLAS mirror at CERN','CERN','SIT','atlas-sw-sit@cern.ch')
	reg['am-IHEP']    = Register(    'am-IHEP',  'http://202.122.33.67/expsoft/atlas/ATLAS.mirror/','ATLAS mirror at IHEP','China','Erming Pei','Erming.Pei@ihep.ac.cn')
	reg['am-TRIUMF']  = Register(    'am-TRIUMF','http://pacman.atlas-canada.ca/ATLAS.mirror','ATLAS mirror at TRIUMF','Canada','Asoka De Silva','desilva@triumf.ca')
#	reg['am-CERN']    = Register(    'am-CERN',  'http://atlas-computing.web.cern.ch/atlas-computing/links/mirror/Atlas.mirror/','ATLAS mirror at CERN','CERN','SIT','atlas-sw-sit@cern.ch')
#	reg['am-CERN-afs']= Register('am-CERN-afs',  '/afs/cern.ch/atlas/software/am-CERN/Atlas.mirror/','ATLAS Tier 0 at CERN','CERN','SIT','atlas-sw-sit@cern.ch')
	reg['am-BU']      = Register(      'am-BU',  'http://atlas.bu.edu/caches/Atlas.mirror/','ATLAS Northeast Tier 2 Center',  'Boston University',   'S. Youssef','http://physics.bu.edu/~youssef/')
	reg['BU']         = Register(         'BU',  'http://atlas.bu.edu/caches/',                                                     'Atlas Tier 2, Boston University',  'http://physics.bu.edu/~usatlas/',         'Saul Youssef',       'http://physics.bu.edu/~youssef/')
	reg['am-BNL']     = Register(     'am-BNL',  'http://www.usatlas.bnl.gov/computing/cache/Atlas.mirror/','ATLAS mirror at BNL',  'BNL',   'Alex Undrus','undrus@bnl.gov')
	reg['HLT']        = Register(        'HLT',  'http://atlas.web.cern.ch/Atlas/project/hlt/admin/www/pacman/cache/','ATLAS HLT',  'CERN',   'Jiri Masik','Jiri.Masik@cern.ch')
	reg['KV']         = Register(         'KV',  'http://classis01.roma1.infn.it/pacman/cache/','ATLAS Kit Validation',  'INFN, Italy',   'Alessandro De Salvo','Alessandro.De.Salvo@cern.ch')
	reg['Dartmouth']  = Register(  'Dartmouth',  'http://grid.dartmouth.edu/pacman/',                                                                     'Dartmouth',  'Dartmouth College',                       'James E. Dobson',                       'James.E.Dobson@Dartmouth.EDU')
	reg['OU']         = Register(         'OU',  'http://www-hep.nhn.ou.edu/pacman-cache/',                                                  'University of Oklahoma',  'http://www-hep.nhn.ou.edu/',                                             'Horst Severini',        'hs@nhn.ou.edu')
	reg['CMT']        = Register(        'CMT',  'http://www.cmtsite.org/pacman/cache/',                                                                        'CMT',  'http://www.cmtsite.org/', 'Christian Arnault', 'arnault@lal.in2p3.fr')
	reg['Pacman']     = Register(     'Pacman',  'http://physics.bu.edu/pacman/sample_cache/',                               'Pacman Headquarters, Boston University',  'http://physics.bu.edu/~youssef/pacman/',  'Saul Youssef',                        'youssef@bu.edu')
	reg['Demo']       = Register(       'Demo',  'http://physics.bu.edu/pacman/demo/',                                                                 'Pacman Demos',  'http://physics.bu.edu/pacman/',           'Saul Youssef',                        'youssef@bu.edu')
	reg['BNL']        = Register(        'BNL',  'http://www.usatlas.bnl.gov/computing/cache/',   'Brookhaven National Laboratory',  'http://www.usatlas.bnl.gov/',  'Alex Undrus',       'undrus@bnl.gov')
	reg['VDT']        = Register(        'VDT',  'http://vdt.cs.wisc.edu/vdt_cache/',                             'Virtual Data Toolkit, University of Wisconson',  'http://vdt.cs.wisc.edu/',  'Alain Roy',                          'roy@cs.wisc.edu')
	reg['OSG']        = Register(        'OSG',  'http://software.grid.iu.edu/pacman/',                                  'Open Science Grid',  'http://www.opensciencegrid.org/',                 'Leigh Grundhoefer',  'leighg@indiana.edu')
	reg['ITB']        = Register(        'ITB',  'http://software.grid.iu.edu/itb/','Open Science Grid Integration Testbed',  'http://www.opensciencegrid.org/',                 'Leigh Grundhoefer',  'leighg@indiana.edu')
	reg['UTA']        = Register(        'UTA',  'http://www-hep.uta.edu/pacman/',                                          'Atlas, University of Texas at Arlington',  'http://heppc12.uta.edu/atlas/',           'Kaushik De',                         'kaushik@uta.edu')
	reg['UCHEP']      = Register(      'UCHEP',  'http://grid.uchicago.edu/caches/',                                               'HEP at the University of Chicago',  'http://grid.uchicago.edu/atlaschimera',   'Marco Mambelli',              'marco@hep.uchicago.edu')
	reg['GCL']        = Register(        'GCL',  'http://grid.uchicago.edu/caches/gcl/',                              'Grid Component Library, University of Chicago',  'http://grid.uchicago.edu/gcl/',           'Marco Mambelli',              'marco@hep.uchicago.edu')
#	reg['iVDGL']      = Register(      'iVDGL',  'http://hep.uchicago.edu/ivdgl/',                                       'International Virtual Data Grid Laboratory',  'http://www.ivdgl.org/',                   'Rob Gardner',                   'rwg@hep.uchicago.edu')
#        reg['GridCat']    = Register(    'GridCat',  'http://www.ivdgl.org/gridcat/GridCat/',                                                     'Grid Cataloging System', 'http://www.ivdgl.org/',                   'Bockjoo Kim',                   'bockjoo@phys.ufl.edu')
	reg['LDR']        = Register(        'LDR',  'http://www.lsc-group.phys.uwm.edu/LDR/cache/',                                            'Lightweight Data  Replicator', 'http://www.lsc-group.phys.uwm.edu/LDR',   'Scott Koranda',        'skoranda@gravity.phys.uwm.edu')
	reg['STAR']       = Register(       'STAR',  'http://www.star.bnl.gov/STAR/comp/ofl/pacman/caches/', 'The STAR Experiment at RHIC, BNL','http://www.star.bnl.gov/','Valeri Fine','fine@bnl.gov')
        reg['TeraGrid']   = Register(   'TeraGrid',  'http://software.teragrid.org/pacman/','NSF TeraGrid','http://www.teragrid.org/','JP Navarro','navarro@mcs.anl.gov')
	reg['LDG']        = Register(        'LDG',  'http://www.ldas-sw.ligo.caltech.edu/ldg_dist/ldg/','LIGO Scientific Collaboration Data Grid','http://www.lsc-group.phys.uwm.edu/lscdatagrid/','Gregory Mendell','gmendell@ligo-wa.caltech.edu')
	reg['JAB']        = Register(        'JAB',  'http://atlas000.bu.edu/cache/',"ATLAS and grid software",'http://atlas000.bu.edu/NETier2/wiki/index.php/Main_Page','John Brunelle','brunejo@physics.bu.edu')
	reg['VTB']        = Register(        'VTB',  'http://osg-vtb.uchicago.edu/vtb/','VTB testbed, UC','http://osg-vtb.uchicago.edu/','Suchandra Thapa','sthapa@ci.uchicago.edu')
        reg['BIRN']       = Register(       'BIRN',  'http://software.nbirn.org/pacman/','NIH Biomedical Informatics Research Network','http://www.nbirn.net/','JP Navarro','navarro@mcs.anl.gov')
        reg['TRIUMF']     = Register(   'TRIUMF',    'http://pacman.atlas-canada.ca/AtlasCanada.pacman/','TRIUMF ATLAS','http://pacman.atlas-canada.ca/','Asoka De Silva','desilva@triumf.ca')
      	return reg

class Registry(HtmlOut,IOAble):
	def __init__(self): 
		if os.path.isdir(fullpath('$PAC_ANCHOR/'+pacmanDir+'/registry')):
			self._regfile = fullpath('$PAC_ANCHOR/'+pacmanDir+'/registry/registry')
		else:
			self._regfile = fullpath(pacmanDir+'/registry/registry')
		if os.path.exists(self._regfile) and not os.path.isdir(self._regfile): 
			verbo.log('registry','Using registry from ['+self._regfile+']...')
			try:
				f = open(self._regfile,'r')
				self._registry = pickle.load(f)
				f.close()
			except (IOError,OSError):
				abort('Error attempting to read registry from ['+self._regfile+'].')
		else:
			self._registry = registry0()

	def __repr__(self): return `self._registry`
	def __eq__(self,x): return self._registry==x._registry
	
	def clear_registry(self): 
		self._registry = {}
		return self.save()
	
	def saved(self): return os.path.exists(self._regfile)
	
	def equiv(self,name1,name2):
		eq = 0
		n1,n2 = self.trans(name1),self.trans(name2)
		if name1=='*' or name1=='' or name2=='*' or name2=='':
			eq = 1
		elif contains(n1, ':') or contains(n2, ':') or   \
		     contains(n1, '@') or contains(n2, '@') or   \
		     contains(n1,'//') or contains(n2,'//'):
			eq = equivSlash(n1,n2)
		else:
			eq = fullpath(n1)==fullpath(n2)
		return eq
	
	def has0 (self,name): return self._registry.has_key(name)
	def has  (self,name):
		name2 = string.split(name,'/')[0]
		return self.has0(name2)
	def trans0(self,name): 
		if self.has(name): return self._registry[name].url
		else:              return name
		
	def trans(self,name): 
		transName = self.transPath(name)
#		verbo.log('registry',name+' => '+transName)
			
		return transName
		
	def short(self,name0):
		new = name0
		for name,reg in self._registry.items():
			if equivURL(name0,reg.url): new = name; break
		return new
		
	def transPath(self,path3):
		path = os.path.expandvars(os.path.expanduser(path3))
		if    ':' in path: 
			path2 = path
			return path2
		elif len(path)>0 and path[0]=='/':
			path2 = path
			return path2
		elif  '/' in path:
			lp = string.split(path,'/')
			count = 0
			path2 = ''
			for x in lp:
				if count==0: path2 = path2 + self.trans0(x)
				else:        path2 = os.path.join(path2,x)
				count = count + 1
			return path2
		else:
			path2 = self.trans0(path)
			return path2

	def regNames(self): return self._registry.keys()
	def getReg (self,name): return self._registry[name]
		
	def add(self,regEntry):
		reason = self.addable(regEntry)
		if not reason.ok():
			if allow('trust-all-caches'): 
				print 'Replacing registry entry ['+regEntry.name+']...'
				reason = Reason()
			elif yesno('About to replace registry entry ['+regEntry.name+']. OK?'): 
				reason = Reason()
		if reason.ok():
			reason = ask.re('registry','OK to add ['+regEntry.name+'] to the local registry?')
			if reason.ok():
				verbo.log('registry',regEntry.name+' added to the local registry...')
				self._registry[regEntry.name] = regEntry
				reason = self.save()
		return reason
	def hasReg(self,regEntry):
		reason = Reason()
		if self._registry.has_key(regEntry.name):
			reg = self._registry[regEntry.name]
			reason = Reason('Registry does not contain ['+`self`+'].',not reg==regEntry)
		else:
			reason = Reason('Registry does not contain ['+`self`+'].')
		return reason
	def addable(self,regEntry):
		reason = Reason()
		if self._registry.has_key(regEntry.name):
			reg = self._registry[regEntry.name]
			if not reg==regEntry:
				reason = Reason("Registry contains a different entry for ["+regEntry.name+"].  Can't add ["+`regEntry`+"] to registry.")
		return reason
		
	def remove(self,regEntry):
		reason = Reason()
		if self._registry.has_key(regEntry.name):
			reg = self._registry[regEntry.name]
			if reg==regEntry:
				del self._registry[regEntry.name]
				verbo.log('registry',regEntry.name+' removed from the local registry...')
				reason = self.save()
#			else:
#				reason = Reason("Registry does not contain ["+`regEntry`+"]. Can't remove.")					
		return reason
		
	def save(self,file=''): 
		reason = Reason()
		try:
			if file=='': path = self._regfile
			else:        path = fullpath(file)
			f = open(path,'w')
			pickle.dump(self._registry,f)
			f.close() 
			self._regfile = path		
		except (IOError,OSError):
			reason = Reason("Error attempting to save registry to ["+self._regfile+"].  Registry not updated.")
		return reason
		
	def remove_registry(self):
		removeFile(self._regfile)
		return Reason()
		
	def htmlOut(self,w):
		w.text('<table>'); w.cr()
		w.text('<tr>')
		w.text('<th>Cache Name</th>')
		w.text('<th>Title</th>')
		w.text('<th>Contact Information</th>')
		w.text('</tr>'); w.cr()
	
		keys = self._registry.keys()
		keys.sort()
		for key in keys:
			reg = self._registry[key]
			
			w.text('<tr>'); w.cr()
			w.text('<td>'); reg.   nameHtml(w); w.text('</td>'); w.cr()
			w.text('<td>'); reg.   infoHtml(w); w.text('</td>'); w.cr()
			w.text('<td>'); reg.contactHtml(w); w.text('</td>'); w.cr()
		w.text('</table>'); w.cr()
		
	def display(self,indent=0):
		keys = self._registry.keys()
		keys.sort()
		print '- Name -      - Location -                                                            - Contact -          '
		print 140*'-'
		for key in keys:
			reg = self._registry[key]
#			print '  ',reg.name,max(0,12-len(reg.name))*' ',reg.contactName,max(0,20-len(reg.contactName))*' ',reg.contactEmail,max(0,35-len(reg.contactEmail))*' ',reg.url
			print reg.name,max(0,12-len(reg.name))*' ',reg.url,max(0,70-len(reg.url))*' ',reg.contactName,max(0,20-len(reg.contactName))*' ',reg.contactEmail
		print 140*'-'

class LocalRegistry(Environment):
	type  = 'local registry'
	title = 'Local Registries'
	action = 'save local registry'
	
	def __init__(self): pass
	def str(self): return 'saved to '+pacmanDir+'/registry'
	def equal(self,x): return 1
	
	def satisfiable (self): return Reason()
	def satisfied   (self): return Reason('Local registry has not been saved.',not registry.saved())
	def acquire     (self): return registry.save()
	def retract     (self): return registry.remove_registry()

class Register(Environment):
	type   = 'register'
	title  = 'Registry Entries'
	action = 'register'
	
	def __init__(self,symbolicName,cacheUrl,infoString='',infoUrl='',contactName='',contactEmail=''):
		self.name         = symbolicName
		self.url          = cacheUrl
		self.infoString   = infoString
		self.infoUrl      = infoUrl
		self.contactName  = contactName
		self.contactEmail = contactEmail
	def str(self): return `self.name,self.url,self.infoString,self.infoUrl,self.contactName,self.contactEmail`
	def equal(self,x): return 	self.name        ==x.name                 and \
					self.url         ==x.url                  and \
					self.infoString  ==x.infoString           and \
					self.infoUrl     ==x.infoUrl              and \
					self.contactName ==x.contactName          and \
					self.contactEmail==x.contactEmail
	
	def nameHtml(self,w): w.link(self.name,self.url)
	def infoHtml(self,w):
		if string.strip(self.infoUrl)=='': 
			w.text('<b>'); w.strongText(self.infoString); w.text('</b>')
		else:                              
			w.text('<b>'); w.strongLink(self.infoString,self.infoUrl); w.text('</b>')
	def contactHtml(self,w):
		if string.strip(self.contactEmail)=='': w.text(self.contactName)
		elif '@' in self.contactEmail: w.text('<i><a href="mailto:'+self.contactEmail+'">'+self.contactName+'</a></i>')
		else: w.text('<i>'); w.link(self.contactName,self.contactEmail); w.text('</i>')
		
	def htmlOut(self,w): 
		w.text('registry entry: '); self.nameHtml(w); w.text(' '); self.infoHtml(w); w.text(' '); self.contactHtml(w)

#-- satisfies
#	def satisfiable(self): return registry.addable(self)
	def satisfiable(self): return Reason()
#	def satisfied  (self): return registry.hasReg (self)
	def acquire    (self): return registry.add    (self)    
#	def retract    (self): return registry.remove (self)	
	def retract    (self): return Reason()		

registry = Registry()
