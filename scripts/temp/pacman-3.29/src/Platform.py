#
#	Copyright Saul Youssef, November 2004
#
from Base             import *
from Environment      import *
from StringAttr       import *
import PlatformBase,FinitePreOrder,platform23

mtrans = {  'linux-redhat-6.0':'RedHat-6',
            'linux-redhat-6.2':'RedHat-6',
	    'linux-redhat-6.3':'RedHat-6',
	    'linux-redhat-7.0':'RedHat-7',
            'linux-redhat-7.1':'RedHat-7',
	    'linux-redhat-7.2':'RedHat-7',
	    'linux-redhat-7.3':'RedHat-7',
	    'linux-redhat-9'  :'RedHat-9',
	    'linux-redhat-8'  :'RedHat-8',
	    'linux-fedora-1'  :'Fedora-1',
	    'linux-fedora-2'  :'Fedora-2',
	    'linux-fedora-3'  :'Fedora-3',
	    'linux-fedora-4'  :'Fedora-4',
	    'linux-rhel-1'    :'RHEL-1',
	    'linux-rhel-2'    :'RHEL-2',
	    'linux-rhel-3'    :'RHEL-3',
	    'linux-rhel-4'    :'RHEL-4',
	    'linux-rhel-5'    :'RHEL-5',
	    'linux-suse-1'    :'SuSE-1',
	    'linux-suse-2'    :'SuSE-2',
	    'linux-suse-3'    :'SuSE-3',
	    'linux-suse-4'    :'SuSE-4',
	    'linux-suse-5'    :'SuSE-5',
	    'linux-suse-6'    :'SuSE-6',
	    'linux-suse-7'    :'SuSE-7',
	    'linux-suse-8'    :'SuSE-8',
	    'linux-suse-9'    :'SuSE-9',
	    'linux-suse-9.1'  :'SuSE-9',
	    'linux-suse-9.2'  :'SuSE-9',
	    'linux-suse-9.3'  :'SuSE-9',
	    'linux-debian-1'  :'Debian-1',
	    'linux-debian-2'  :'Debian-2',
	    'linux-debian-3'  :'Debian-3',
	    'linux-debian-4'  :'Debian-4',
	    'linux-debian-5'  :'Debian-5',
	    'linux-debian-6'  :'Debian-6',
	    'linux-debian-7'  :'Debian-7',
	    'linux-debian-3.0':'Debian-3',
	    'linux-debian-3.1':'Debian-3',
	    'linux-debian-3.2':'Debian-3',
	    'linux-debian-3.3':'Debian-3',
	    'linux-debian-3.4':'Debian-3',
	    'linux-sl-3.0'    :'SL-3',
	    'linux-sl-3.1'    :'SL-3',
	    'linux-sl-3.2'    :'SL-3',
	    'linux-sl-3.3'    :'SL-3',
	    'linux-sl-3.4'    :'SL-3',
	    'linux-sl-3.5'    :'SL-3',
	    'linux-sl-3.6'    :'SL-3',
	    'linux-sl-3.7'    :'SL-3',
	    'linux-sl-fermi-3.0' :'SL-3',
	    'linux-sl-fermi-3.1' :'SL-3',
	    'linux-sl-fermi-3.2' :'SL-3',
	    'linux-sl-fermi-3.3' :'SL-3',
	    'linux-sl-fermi-3.4' :'SL-3',
	    'linux-sl-fermi-3.5' :'SL-3',
	    'linux-sl-fermi-3.6' :'SL-3',
	    'linux-sl-fermi-3.7' :'SL-3',
	    'linux-sl-cern-3.0' :'SL-3',
	    'linux-sl-cern-3.1' :'SL-3',
	    'linux-sl-cern-3.2' :'SL-3',
	    'linux-sl-cern-3.3' :'SL-3',
	    'linux-sl-cern-3.4' :'SL-3',
	    'linux-sl-cern-3.5' :'SL-3',
	    'linux-sl-cern-3.6' :'SL-3',
	    'linux-sl-cern-3.7' :'SL-3',
	    'linux-sl-ific-3.0' :'SL-3',
	    'linux-sl-ific-3.1' :'SL-3',
	    'linux-sl-ific-3.2' :'SL-3',
	    'linux-sl-ific-3.3' :'SL-3',
	    'linux-sl-ific-3.4' :'SL-3',
	    'linux-sl-ific-3.5' :'SL-3',
	    'linux-sl-ific-3.6' :'SL-3',
	    'linux-sl-ific-3.7' :'SL-3',
	    'linux-rocks-3.0'    :'Rocks-3',
	    'linux-rocks-3.1'    :'Rocks-3',
	    'linux-rocks-3.2'    :'Rocks-3',
	    'linux-rocks-3.3'    :'Rocks-3',
	    'linux-rocks-3.4'    :'Rocks-3',
	    'linux-rocks-3.5'    :'Rocks-3',
	    'linux-rocks-3.5'    :'Rocks-3',
	    'linux-sl-4.0'    :'SL-4',
	    'linux-sl-4.1'    :'SL-4',
	    'linux-sl-4.2'    :'SL-4',
	    'linux-sl-4.3'    :'SL-4',
	    'linux-sl-4.4'    :'SL-4',
	    'linux-sl-4.5'    :'SL-4',
	    'linux-sl-4.6'    :'SL-4',
	    'linux-sl-4.7'    :'SL-4',
	    'linux-sl-fermi-4.0' :'SL-4',
	    'linux-sl-fermi-4.1' :'SL-4',
	    'linux-sl-fermi-4.2' :'SL-4',
	    'linux-sl-fermi-4.3' :'SL-4',
	    'linux-sl-fermi-4.4' :'SL-4',
	    'linux-sl-fermi-4.5' :'SL-4',
	    'linux-sl-fermi-4.6' :'SL-4',
	    'linux-sl-fermi-4.7' :'SL-4',
	    'slc3':'SL-3',
	    'slc4':'SL-4',
	    'linux-sl-cern-4.0' :'CERN-SL-4',
	    'linux-sl-cern-4.1' :'CERN-SL-4',
	    'linux-sl-cern-4.2' :'CERN-SL-4',
	    'linux-sl-cern-4.3' :'CERN-SL-4',
	    'linux-sl-cern-4.4' :'CERN-SL-4',
	    'linux-sl-cern-4.5' :'CERN-SL-4',
	    'linux-sl-cern-4.6' :'CERN-SL-4',
	    'linux-sl-cern-4.7' :'CERN-SL-4',
	    'linux-sl-ific-4.0' :'IFIC-SL-4',
	    'linux-sl-ific-4.1' :'IFIC-SL-4',
	    'linux-sl-ific-4.2' :'IFIC-SL-4',
	    'linux-sl-ific-4.3' :'IFIC-SL-4',
	    'linux-sl-ific-4.4' :'IFIC-SL-4',
	    'linux-sl-ific-4.5' :'IFIC-SL-4',
	    'linux-sl-ific-4.6' :'IFIC-SL-4',
	    'linux-sl-ific-4.7' :'IFIC-SL-4',
	    'linux-rocks-4.0'    :'Rocks-4',
	    'linux-rocks-4.1'    :'Rocks-4',
	    'linux-rocks-4.2'    :'Rocks-4',
	    'linux-rocks-4.3'    :'Rocks-4',
	    'linux-rocks-4.4'    :'Rocks-4',
	    'linux-rocks-4.5'    :'Rocks-4',
	    'linux-rocks-4.5'    :'Rocks-4',
	    'linux-sl-5.0'    :'SL-5',
	    'linux-sl-5.1'    :'SL-5',
	    'linux-sl-5.2'    :'SL-5',
	    'linux-sl-5.3'    :'SL-5',
	    'linux-sl-5.4'    :'SL-5',
	    'linux-sl-5.5'    :'SL-5',
	    'linux-sl-5.6'    :'SL-5',
	    'linux-sl-5.7'    :'SL-5',
	    'linux-sl-fermi-5.0' :'SL-5',
	    'linux-sl-fermi-5.1' :'SL-5',
	    'linux-sl-fermi-5.2' :'SL-5',
	    'linux-sl-fermi-5.3' :'SL-5',
	    'linux-sl-fermi-5.4' :'SL-5',
	    'linux-sl-fermi-5.5' :'SL-5',
	    'linux-sl-fermi-5.6' :'SL-5',
	    'linux-sl-fermi-5.7' :'SL-5',
	    'linux-sl-cern-5.0' :'SL-5',
	    'linux-sl-cern-5.1' :'SL-5',
	    'linux-sl-cern-5.2' :'SL-5',
	    'linux-sl-cern-5.3' :'SL-5',
	    'linux-sl-cern-5.4' :'SL-5',
	    'linux-sl-cern-5.5' :'SL-5',
	    'linux-sl-cern-5.6' :'SL-5',
	    'linux-sl-cern-5.7' :'SL-5',
	    'linux-sl-ific-5.0' :'SL-5',
	    'linux-sl-ific-5.1' :'SL-5',
	    'linux-sl-ific-5.2' :'SL-5',
	    'linux-sl-ific-5.3' :'SL-5',
	    'linux-sl-ific-5.4' :'SL-5',
	    'linux-sl-ific-5.5' :'SL-5',
	    'linux-sl-ific-5.6' :'SL-5',
	    'linux-sl-ific-5.7' :'SL-5',
	    'linux-centos-4.0' :'CentOS-4',
	    'linux-centos-4.1' :'CentOS-4',
	    'linux-centos-4.2' :'CentOS-4',
	    'linux-centos-4.3' :'CentOS-4',
	    'linux-centos-4.4' :'CentOS-4',
	    'linux-centos-4.5' :'CentOS-4',
	    'linux-centos-4.6' :'CentOS-4',
	    'linux-centos-4.7' :'CentOS-4',
	    'linux-rocks-5.0'    :'Rocks-5',
	    'linux-rocks-5.1'    :'Rocks-5',
	    'linux-rocks-5.2'    :'Rocks-5',
	    'linux-rocks-5.3'    :'Rocks-5',
	    'linux-rocks-5.4'    :'Rocks-5',
	    'linux-rocks-5.5'    :'Rocks-5',
	    'linux-rocks-5.5'    :'Rocks-5' }
	    
backwardcompats = {
    'RedHat-6.1':'RedHat-6',
    'RedHat-6.2':'RedHat-6',
    'RedHat-6.3':'RedHat-6',
    'RedHat-7.0':'RedHat-7',
    'RedHat-7.1':'RedHat-7',
    'RedHat-7.2':'RedHat-7',
    'RedHat-7.3':'RedHat-7',
    'SuSE-9.1':'SuSE-9',
    'SuSE-9.2':'SuSE-9',
    'SuSE-9.3':'SuSE-9',
    'Debian-3.0':'Debian-3',
    'Debian-3.1':'Debian-3',
    'Debian-3.2':'Debian-3',
    'Debian-3.3':'Debian-3',
    'Debian-3.4':'Debian-3',
    'SL-3.0':'SL-3',
    'SL-3.1':'SL-3',
    'SL-3.2':'SL-3',
    'SL-3.3':'SL-3',
    'SL-3.4':'SL-3',
    'SL-3.5':'SL-3',
    'SL-3.6':'SL-3',
    'SL-3.7':'SL-3',
    'Fermi-SL-3.0':'SL-3',
    'Fermi-SL-3.1':'SL-3',
    'Fermi-SL-3.2':'SL-3',
    'Fermi-SL-3.3':'SL-3',
    'Fermi-SL-3.4':'SL-3',
    'Fermi-SL-3.5':'SL-3',
    'Fermi-SL-3.6':'SL-3',
    'Fermi-SL-3.7':'SL-3',
    'CERN-SL-3.0':'SL-3',
    'CERN-SL-3.1':'SL-3',
    'CERN-SL-3.2':'SL-3',
    'CERN-SL-3.3':'SL-3',
    'CERN-SL-3.4':'SL-3',
    'CERN-SL-3.5':'SL-3',
    'CERN-SL-3.6':'SL-3',
    'CERN-SL-3.7':'SL-3',
    'IFIC-SL-3.0':'SL-3',
    'IFIC-SL-3.1':'SL-3',
    'IFIC-SL-3.2':'SL-3',
    'IFIC-SL-3.3':'SL-3',
    'IFIC-SL-3.4':'SL-3',
    'IFIC-SL-3.5':'SL-3',
    'IFIC-SL-3.6':'SL-3',
    'IFIC-SL-3.7':'SL-3',
    'Rocks-3.0':'Rocks-3',
    'Rocks-3.1':'Rocks-3',
    'Rocks-3.2':'Rocks-3',
    'Rocks-3.3':'Rocks-3',
    'Rocks-3.4':'Rocks-3',
    'Rocks-3.5':'Rocks-3',
    'Rocks-3.6':'Rocks-3',
    'SL-4.0':'SL-4',
    'SL-4.1':'SL-4',
    'SL-4.2':'SL-4',
    'SL-4.3':'SL-4',
    'SL-4.4':'SL-4',
    'SL-4.5':'SL-4',
    'SL-4.6':'SL-4',
    'SL-4.7':'SL-4',
    'Fermi-SL-4':'SL-4',
    'Fermi-SL-4.0':'SL-4',
    'Fermi-SL-4.1':'SL-4',
    'Fermi-SL-4.2':'SL-4',
    'Fermi-SL-4.3':'SL-4',
    'Fermi-SL-4.4':'SL-4',
    'Fermi-SL-4.5':'SL-4',
    'Fermi-SL-4.6':'SL-4',
    'Fermi-SL-4.7':'SL-4',
    'CERN-SL-4':'SL-4',
    'CERN-SL-4.0':'SL-4',
    'CERN-SL-4.1':'SL-4',
    'CERN-SL-4.2':'SL-4',
    'CERN-SL-4.3':'SL-4',
    'CERN-SL-4.4':'SL-4',
    'CERN-SL-4.5':'SL-4',
    'CERN-SL-4.6':'SL-4',
    'CERN-SL-4.7':'SL-4',
    'IFIC-SL-4.0':'SL-4',
    'IFIC-SL-4.1':'SL-4',
    'IFIC-SL-4.2':'SL-4',
    'IFIC-SL-4.3':'SL-4',
    'IFIC-SL-4.4':'SL-4',
    'IFIC-SL-4.5':'SL-4',
    'IFIC-SL-4.6':'SL-4',
    'IFIC-SL-4.7':'SL-4',
    'Rocks-4.0':'Rocks-4',
    'Rocks-4.1':'Rocks-4',
    'Rocks-4.2':'Rocks-4',
    'Rocks-4.3':'Rocks-4',
    'Rocks-4.4':'Rocks-4',
    'Rocks-4.5':'Rocks-4',
    'Rocks-4.6':'Rocks-4',
    'CentOS-4.0':'CentOS-4',
    'CentOS-4.1':'CentOS-4',
    'CentOS-4.2':'CentOS-4',
    'CentOS-4.3':'CentOS-4',
    'CentOS-4.4':'CentOS-4',
    'CentOS-4.5':'CentOS-4',
    'CentOS-4.6':'CentOS-4',
    'CentOS-4.7':'CentOS-4'}

machines = []

#
#-- make all the translated names equivalent to their translation
#
for key,val in mtrans.items():
	machines.append((key,val,))
	machines.append((val,key,))

for key,val in backwardcompats.items():
	machines.append((key,val,))
	machines.append((val,key,))

#
#-- Unix
#
machines.append(('Unix',          '*',))
machines.append(('Sun',        'Unix',))
machines.append(('FreeBSD',    'Unix',))
machines.append(('Aix',        'Unix',))
machines.append(('OSF1',       'Unix',))
machines.append(('Cygwin',     'Unix',))
machines.append(('darwin',     'Unix',))
machines.append(('Irix',       'Unix',))
machines.append(('unix',       'Unix',))
machines.append(('Unix',       'unix',))

#
#-- Linux
#
machines.append(('Linux',     'linux',))
machines.append(('linux',     'Linux',))
machines.append(('Linux',      'Unix',))
machines.append(('RedHat',    'Linux',))
#machines.append(('linux2',    'Linux',))
machines.append(('SuSE',      'Linux',))
machines.append(('Fedora',    'Linux',))
machines.append(('RHEL',      'Linux',))
machines.append(('Debian',    'Linux',))
machines.append(('linux',     'Linux',))
machines.append(('Linux',     'linux',))
machines.append(('Tao',       'Linux',))
machines.append(('SL',        'Linux',))
machines.append(('Rocks',     'Linux',))
machines.append(('BU-Linux',  'Linux',))
machines.append(('CentOS',    'Linux',))
machines.append(('Gentoo',    'Linux',))
machines.append(('Ubuntu',    'Linux',))
machines.append(('YellowDog', 'Linux',))

#
#-- Scientific Linux Family
#
machines.append(('Fermi-SL',           'SL',))
machines.append(('SLC',                'SL',))
machines.append(('CERN-SL',           'SLC',))
machines.append(('SLC',           'CERN-SL',))
machines.append(('IFIC-SL',           'SLI',))
machines.append(('SLI',           'IFIC-SL',))
machines.append(('SLI',                'SL',))

#
#-- Gentoo
#
machines.append(('Gentoo-1','Gentoo',))
machines.append(('Gentoo-2','Gentoo',))
machines.append(('Gentoo-3','Gentoo',))

#
#-- Debian
#
machines.append(('Debian-1','Debian',))
machines.append(('Debian-2','Debian',))
machines.append(('Debian-3','Debian',))
machines.append(('Debian-4','Debian',))
machines.append(('Debian-5','Debian',))
machines.append(('Debian-6','Debian',))
machines.append(('Debian-7','Debian',))
machines.append(('Debian-8','Debian',))
machines.append(('Debian-9','Debian',))
machines.append(('Debian-10','Debian',))

#
#-- Ubuntu is based on Debian
#
machines.append(('Ubuntu-1' ,'Ubuntu',))
machines.append(('Ubuntu-2' ,'Ubuntu',))
machines.append(('Ubuntu-3' ,'Ubuntu',))
machines.append(('Ubuntu-4' ,'Ubuntu',))
machines.append(('Ubuntu-5' ,'Ubuntu',))
machines.append(('Ubuntu-6' ,'Ubuntu',))
machines.append(('Ubuntu-7' ,'Ubuntu',))
machines.append(('Ubuntu-8' ,'Ubuntu',))
machines.append(('Ubuntu-9' ,'Ubuntu',))
machines.append(('Ubuntu-10','Ubuntu',))

machines.append(('Ubuntu-1' ,'Debian-1',))
machines.append(('Ubuntu-2' ,'Debian-2',))
machines.append(('Ubuntu-3' ,'Debian-3',))
machines.append(('Ubuntu-4' ,'Debian-4',))
machines.append(('Ubuntu-5' ,'Debian-5',))
machines.append(('Ubuntu-6' ,'Debian-6',))
machines.append(('Ubuntu-7' ,'Debian-7',))
machines.append(('Ubuntu-8' ,'Debian-8',))
machines.append(('Ubuntu-9' ,'Debian-9',))
machines.append(('Ubuntu-10','Debian-10',))

machines.append(('Debian-1' ,'Ubuntu-1',))
machines.append(('Debian-2' ,'Ubuntu-2',))
machines.append(('Debian-3' ,'Ubuntu-3',))
machines.append(('Debian-4' ,'Ubuntu-4',))
machines.append(('Debian-5' ,'Ubuntu-5',))
machines.append(('Debian-6' ,'Ubuntu-6',))
machines.append(('Debian-7' ,'Ubuntu-7',))
machines.append(('Debian-8' ,'Ubuntu-8',))
machines.append(('Debian-9' ,'Ubuntu-9',))
machines.append(('Debian-10','Ubuntu-10',))

#
#-- Red Hat Enterprise Linux
#
machines.append(('RHEL-1','RHEL',))
machines.append(('RHEL-2','RHEL',))
machines.append(('RHEL-3','RHEL',))
machines.append(('RHEL-4','RHEL',))
machines.append(('RHEL-5','RHEL',))
machines.append(('RHEL-6','RHEL',))
machines.append(('RHEL-7','RHEL',))

#
#-- SuSE linux
#
machines.append(('SuSE-1' ,'SuSE',))
machines.append(('SuSE-2' ,'SuSE',))
machines.append(('SuSE-3' ,'SuSE',))
machines.append(('SuSE-4' ,'SuSE',))
machines.append(('SuSE-5' ,'SuSE',))
machines.append(('SuSE-6' ,'SuSE',))
machines.append(('SuSE-7' ,'SuSE',))
machines.append(('SuSE-8' ,'SuSE',))
machines.append(('SuSE-9' ,'SuSE',))
machines.append(('SuSE-10','SuSE',))
machines.append(('SuSE-11','SuSE',))
machines.append(('SuSE-12','SuSE',))
machines.append(('SuSE-13','SuSE',))

#
#-- CentOS is based on RHEL
#
machines.append(('CentOS-1' ,'CentOS',))
machines.append(('CentOS-2' ,'CentOS',))
machines.append(('CentOS-3' ,'CentOS',))
machines.append(('CentOS-4' ,'CentOS',))
machines.append(('CentOS-5' ,'CentOS',))
machines.append(('CentOS-6' ,'CentOS',))
machines.append(('CentOS-7' ,'CentOS',))

machines.append(('CentOS-1' ,'RHEL-1',))
machines.append(('CentOS-2' ,'RHEL-2',))
machines.append(('CentOS-3' ,'RHEL-3',))
machines.append(('CentOS-4' ,'RHEL-4',))
machines.append(('CentOS-5' ,'RHEL-5',))
machines.append(('CentOS-6' ,'RHEL-6',))
machines.append(('CentOS-7' ,'RHEL-7',))

machines.append(('RHEL-1' ,'CentOS-1',))
machines.append(('RHEL-2' ,'CentOS-2',))
machines.append(('RHEL-3' ,'CentOS-3',))
machines.append(('RHEL-4' ,'CentOS-4',))
machines.append(('RHEL-5' ,'CentOS-5',))
machines.append(('RHEL-6' ,'CentOS-6',))
machines.append(('RHEL-7' ,'CentOS-7',))
#
#-- Sun
#
machines.append((     'sun',      'Sun',))
machines.append((     'Sun',      'sun',))
machines.append((  'sunos5',   'sunos4',))
machines.append((  'sunos4',   'sunos3',))
machines.append((  'sunos3',   'sunos2',))
machines.append((  'sunos2',    'sunos',))
machines.append((   'sunos',      'sun',))
#
#-- Freebsd
#
machines.append((  'FreeBSD',    'freebsd',))
machines.append((  'freebsd',    'FreeBSD',))
machines.append((  'freebsd6',   'freebsd',))
machines.append((  'freebsd5',   'freebsd',))
machines.append((  'freebsd4',   'freebsd',))
machines.append((  'freebsd3',   'freebsd',))
machines.append((  'freebsd2',   'freebsd',))
machines.append((  'freebsd1',   'freebsd',))
#
#-- Irix
#
machines.append((    'irix',   'Irix',))
machines.append((    'Irix',   'irix',))
machines.append((   'irix7',  'irix6',))
machines.append((   'irix6',  'irix5',))
machines.append((   'irix5',  'irix4',))
machines.append((   'irix4',   'irix',))
#
#-- Fedora
#
machines.append(('Fedora-1' ,'Fedora',))
machines.append(('Fedora-2' ,'Fedora',))
machines.append(('Fedora-3' ,'Fedora',))
machines.append(('Fedora-4' ,'Fedora',))
machines.append(('Fedora-5' ,'Fedora',))
machines.append(('Fedora-6' ,'Fedora',))
machines.append(('Fedora-7' ,'Fedora',))
machines.append(('Fedora-8' ,'Fedora',))
machines.append(('Fedora-9' ,'Fedora',))
machines.append(('Fedora-10','Fedora',))
machines.append(('Fedora-11','Fedora',))
machines.append(('Fedora-12','Fedora',))
#
#-- Yellow dog is a fedora clone
#
machines.append(('YellowDog-1' ,'YellowDog',))
machines.append(('YellowDog-2' ,'YellowDog',))
machines.append(('YellowDog-3' ,'YellowDog',))
machines.append(('YellowDog-4' ,'YellowDog',))
machines.append(('YellowDog-5' ,'YellowDog',))
machines.append(('YellowDog-6' ,'YellowDog',))
machines.append(('YellowDog-7' ,'YellowDog',))
machines.append(('YellowDog-8' ,'YellowDog',))
machines.append(('YellowDog-9' ,'YellowDog',))
machines.append(('YellowDog-10','YellowDog',))
machines.append(('YellowDog-11','YellowDog',))
machines.append(('YellowDog-12','YellowDog',))

machines.append(('YellowDog-1' ,'Fedora-1',))
machines.append(('YellowDog-2' ,'Fedora-2',))
machines.append(('YellowDog-3' ,'Fedora-3',))
machines.append(('YellowDog-4' ,'Fedora-4',))
machines.append(('YellowDog-5' ,'Fedora-5',))
machines.append(('YellowDog-6' ,'Fedora-6',))
machines.append(('YellowDog-7' ,'Fedora-7',))

machines.append(('Fedora-1' ,'YellowDog-1' ,))
machines.append(('Fedora-2' ,'YellowDog-2' ,))
machines.append(('Fedora-3' ,'YellowDog-3' ,))
machines.append(('Fedora-4' ,'YellowDog-4' ,))
machines.append(('Fedora-5' ,'YellowDog-5' ,))
machines.append(('Fedora-6' ,'YellowDog-6' ,))
machines.append(('Fedora-7' ,'YellowDog-7' ,))
machines.append(('Fedora-8' ,'YellowDog-8' ,))
machines.append(('Fedora-9' ,'YellowDog-9' ,))
machines.append(('Fedora-10','YellowDog-10',))
machines.append(('Fedora-11','YellowDog-11',))
machines.append(('Fedora-12','YellowDog-12',))
#
#-- aix
#
#
# AIX 5.X added by Scot Kronenfeld 2/2009
# The VDT wants to tell the difference between AIX 5.2 and AIX 5.3
machines.append((      'AIX5',     'AIX' ,))
machines.append((      'AIX5.0',   'AIX5',))
machines.append((      'AIX5.1',   'AIX5',))
machines.append((      'AIX5.2',   'AIX5',))
machines.append((      'AIX5.3',   'AIX5',))
machines.append((      'AIX5.4',   'AIX5',))
machines.append((      'AIX5.5',   'AIX5',))
machines.append((      'AIX5.6',   'AIX5',))
machines.append((      'AIX5.7',   'AIX5',))
machines.append((      'AIX5.8',   'AIX5',))
machines.append((      'AIX5.9',   'AIX5',))
machines.append((      'AIX4',     'AIX' ,))
machines.append((      'AIX3',     'AIX' ,))
machines.append((      'AIX2',     'AIX' ,))
machines.append((       'AIX',     'Aix' ,))
machines.append((       'Aix',     'AIX' ,))
#
#-- OSF1
#
machines.append((   'OSF1-V7', 'OSF1-V6',))
machines.append((   'OSF1-V6', 'OSF1-V5',))
machines.append((   'OSF1-V5', 'OSF1-V4',))
machines.append((   'OSF1-V4', 'OSF1-V3',))
machines.append((   'OSF1-V3', 'OSF1-V2',))
machines.append((   'OSF1-V2', 'OSF1-V1',))
machines.append((   'OSF1-V1', 'OSF1'   ,))
#
#-- cygwin
#
machines.append((  'cygwin',   'Cygwin',))
machines.append((  'Cygwin',   'cygwin',))
machines.append((  'cygwin',   'CygWin',))
machines.append((  'CygWin',   'cygwin',))
#
#-- MacOS
#
# MacOS-10.X added by Scot Kronenfeld 2/2009
# The VDT wants to tell the difference between MacOS-10.4, 10.5, and 10.6
machines.append((  'MacOS',      'darwin',))
machines.append((  'darwin',     'MacOS' ,))
machines.append((  'MacOS-10.4', 'MacOS' ,))
machines.append((  'MacOS-10.5', 'MacOS' ,))
machines.append((  'MacOS-10.6', 'MacOS' ,))
machines.append((  'MacOS-10.7', 'MacOS' ,))
machines.append((  'MacOS-10.8', 'MacOS' ,))
machines.append((  'MacOS-10.9', 'MacOS' ,))
#
#-- misc
#
machines.append(('linux-i386',  'Linux',))
machines.append(('linux-i686',  'Linux',))
machines.append(('Mandrake',    'Linux',))
#machines.append(('linux2',      'Linux',))
#
#-- Red Hat
#
machines.append(('RedHat-6','RedHat',))
machines.append(('RedHat-7','RedHat',))
machines.append(('RedHat-8','RedHat',))
machines.append(('RedHat-9','RedHat',))

#
#-- fermi-linux
#
machines.append(( 'linux-fermi-7.4','linux-fermi-7',))
machines.append(( 'linux-fermi-7.3','linux-fermi-7',))
machines.append(( 'linux-fermi-7.2','linux-fermi-7',))
machines.append(( 'linux-fermi-9.0','linux-fermi-9',))
machines.append(( 'linux-fermi-7.1','linux-fermi',  ))
machines.append(( 'linux-fermi',    'Linux',        ))

#
#-- Tao Linx
#
machines.append(('linux-tao-1',   'Tao', ))

#
#-- BU Linux is a Fedora clone
#
machines.append(('BU-Linux-1' ,'BU-Linux',))
machines.append(('BU-Linux-2' ,'BU-Linux',))
machines.append(('BU-Linux-3' ,'BU-Linux',))
machines.append(('BU-Linux-4' ,'BU-Linux',))
machines.append(('BU-Linux-5' ,'BU-Linux',))
machines.append(('BU-Linux-6' ,'BU-Linux',))
machines.append(('BU-Linux-7' ,'BU-Linux',))

machines.append(('BU-Linux-1' ,'Fedora-1',))
machines.append(('BU-Linux-2' ,'Fedora-2',))
machines.append(('BU-Linux-3' ,'Fedora-3',))
machines.append(('BU-Linux-4' ,'Fedora-4',))
machines.append(('BU-Linux-5' ,'Fedora-5',))
machines.append(('BU-Linux-6' ,'Fedora-6',))
machines.append(('BU-Linux-7' ,'Fedora-7',))

machines.append(('Fedora-1' ,'BU-Linux-1',))
machines.append(('Fedora-2' ,'BU-Linux-2',))
machines.append(('Fedora-3' ,'BU-Linux-3',))
machines.append(('Fedora-4' ,'BU-Linux-4',))
machines.append(('Fedora-5' ,'BU-Linux-5',))
machines.append(('Fedora-6' ,'BU-Linux-6',))
machines.append(('Fedora-7' ,'BU-Linux-7',))

#
#-- Rocks is an RHEL clone
#
machines.append(('Rocks-1' ,'Rocks',))
machines.append(('Rocks-2' ,'Rocks',))
machines.append(('Rocks-3' ,'Rocks',))
machines.append(('Rocks-4' ,'Rocks',))
machines.append(('Rocks-5' ,'Rocks',))
machines.append(('Rocks-6' ,'Rocks',))
machines.append(('Rocks-7' ,'Rocks',))

machines.append(('Rocks-1' ,'RHEL-1',))
machines.append(('Rocks-2' ,'RHEL-2',))
machines.append(('Rocks-3' ,'RHEL-3',))
machines.append(('Rocks-4' ,'RHEL-4',))
machines.append(('Rocks-5' ,'RHEL-5',))
machines.append(('Rocks-6' ,'RHEL-6',))
machines.append(('Rocks-7' ,'RHEL-7',))

machines.append(('RHEL-1' ,'Rocks-1',))
machines.append(('RHEL-2' ,'Rocks-2',))
machines.append(('RHEL-3' ,'Rocks-3',))
machines.append(('RHEL-4' ,'Rocks-4',))
machines.append(('RHEL-5' ,'Rocks-5',))
machines.append(('RHEL-6' ,'Rocks-6',))
machines.append(('RHEL-7' ,'Rocks-7',))

#
#-- IFIC is an SLC clone
#
machines.append(('IFIC-SLC-3','SLC-3',))
machines.append(('IFIC-SLC-4','SLC-4',))
machines.append(('IFIC-SLC-5','SLC-5',))
machines.append(('IFIC-SLC-6','SLC-6',))

machines.append(('SLC-3','IFIC-SLC-3',))
machines.append(('SLC-4','IFIC-SLC-4',))
machines.append(('SLC-5','IFIC-SLC-5',))
machines.append(('SLC-6','IFIC-SLC-6',))

#
#-- Vanilla Scientific Linux 
#
machines.append(('SL-1' ,'SL',))
machines.append(('SL-2' ,'SL',))
machines.append(('SL-3' ,'SL',))
machines.append(('SL-4' ,'SL',))
machines.append(('SL-5' ,'SL',))
machines.append(('SL-6' ,'SL',))
machines.append(('SL-7' ,'SL',))
machines.append(('SL-8' ,'SL',))
machines.append(('SL-9' ,'SL',))
machines.append(('SL-10','SL',))

machines.append(('SL-1' ,'RHEL-1',))
machines.append(('SL-2' ,'RHEL-2',))
machines.append(('SL-3' ,'RHEL-3',))
machines.append(('SL-4' ,'RHEL-4',))
machines.append(('SL-5' ,'RHEL-5',))
machines.append(('SL-6' ,'RHEL-6',))
machines.append(('SL-7' ,'RHEL-7',))

machines.append(('RHEL-1' ,'SL-1',))
machines.append(('RHEL-2' ,'SL-2',))
machines.append(('RHEL-3' ,'SL-3',))
machines.append(('RHEL-4' ,'SL-4',))
machines.append(('RHEL-5' ,'SL-5',))
machines.append(('RHEL-6' ,'SL-6',))
machines.append(('RHEL-7' ,'SL-7',))

#
#-- CERN Scientific Linux 
#
machines.append(('SLC-1' ,'SLC',))
machines.append(('SLC-2' ,'SLC',))
machines.append(('SLC-3' ,'SLC',))
machines.append(('SLC-4' ,'SLC',))
machines.append(('SLC-5' ,'SLC',))
machines.append(('SLC-6' ,'SLC',))
machines.append(('SLC-7' ,'SLC',))
machines.append(('SLC-8' ,'SLC',))
machines.append(('SLC-9' ,'SLC',))
machines.append(('SLC-10','SLC',))

machines.append(('SLC-1' ,'RHEL-1',))
machines.append(('SLC-2' ,'RHEL-2',))
machines.append(('SLC-3' ,'RHEL-3',))
machines.append(('SLC-4' ,'RHEL-4',))
machines.append(('SLC-5' ,'RHEL-5',))
machines.append(('SLC-6' ,'RHEL-6',))
machines.append(('SLC-7' ,'RHEL-7',))

machines.append(('RHEL-1' ,'SLC-1',))
machines.append(('RHEL-2' ,'SLC-2',))
machines.append(('RHEL-3' ,'SLC-3',))
machines.append(('RHEL-4' ,'SLC-4',))
machines.append(('RHEL-5' ,'SLC-5',))
machines.append(('RHEL-6' ,'SLC-6',))
machines.append(('RHEL-7' ,'SLC-7',))

#
#-- Fermi Scientific Linux
#
machines.append(('Fermi-SL-1' ,'Fermi-SL',))
machines.append(('Fermi-SL-2' ,'Fermi-SL',))
machines.append(('Fermi-SL-3' ,'Fermi-SL',))
machines.append(('Fermi-SL-4' ,'Fermi-SL',))
machines.append(('Fermi-SL-5' ,'Fermi-SL',))
machines.append(('Fermi-SL-6' ,'Fermi-SL',))
machines.append(('Fermi-SL-7' ,'Fermi-SL',))
machines.append(('Fermi-SL-8' ,'Fermi-SL',))
machines.append(('Fermi-SL-9' ,'Fermi-SL',))
machines.append(('Fermi-SL-10','Fermi-SL',))

machines.append(('Fermi-SL-1' ,'RHEL-1',))
machines.append(('Fermi-SL-2' ,'RHEL-2',))
machines.append(('Fermi-SL-3' ,'RHEL-3',))
machines.append(('Fermi-SL-4' ,'RHEL-4',))
machines.append(('Fermi-SL-5' ,'RHEL-5',))
machines.append(('Fermi-SL-6' ,'RHEL-6',))
machines.append(('Fermi-SL-7' ,'RHEL-7',))

machines.append(('RHEL-1' ,'Fermi-SL-1',))
machines.append(('RHEL-2' ,'Fermi-SL-2',))
machines.append(('RHEL-3' ,'Fermi-SL-3',))
machines.append(('RHEL-4' ,'Fermi-SL-4',))
machines.append(('RHEL-5' ,'Fermi-SL-5',))
machines.append(('RHEL-6' ,'Fermi-SL-6',))
machines.append(('RHEL-7' ,'Fermi-SL-7',))
		
supportedPlatforms = ['Ubuntu','RedHat','CentOS','Fedora','Cygwin','RHEL','AIX','SuSE', 'Debian','Tao','SL','OSF1','MacOS','Rocks','Sun','FreeBSD','Irix','Gentoo']
supportedPlatforms.sort()

Machines = FinitePreOrder.FinitePreOrder(machines)

def platformstring():
	plat = thisPlatform()
	s = plat
	pl = Platform().platforms(); pl.reverse()
	for x in pl: 
		if x!=plat: s = s + ', ' + x
	return s

_thisplatform = {}

def thisPlatform():
	if not _thisplatform.has_key('platform'):
		ppl = os.path.join(pac_anchor,pacmanDir,'ppl')
		if os.path.exists(ppl):
			try:
				f = open(ppl,'r')
				lines = f.readlines()
				f.close()
			except:
				abort("Can't read ["+ppl+"].")
			
			if len(lines)>0 and len(lines[0])>0:
				plat = string.strip(lines[0][:-1])
			else:
				abort("File ["+ppl+"] has been corrupted.")
		else:
			pre,plat = switchpar('pretend-platform')
			if not pre:
				if len(switchItems('pretend-platform'))>0:
					plat = switchItems('pretend-platform')[0]
				else:
					ok,u = uname()
					if ok and len(u)>0 and u[0]=='OSF1':
						if len(u)>=3:
							plat='OSF1-'+u[2][:2]
						else:
							plat = 'OSF1'
					else:
			 			plat = findPlatform()[0]
			if mtrans.has_key(plat): plat = mtrans[plat]

		got_one = 0
		for x,y in machines: 
			if plat==x or plat==y: got_one = 1; break
		if not got_one: 
			plat = findLinux()
		_thisplatform['platform'] = plat
	else:
		plat = _thisplatform['platform']
	return plat

def platformDisplay():
	p = Platform()
	print '='
	sys.stdout.write('= Supported Architectures: '); niceListOut(supportedPlatforms); sys.stdout.write('\n')
	print '='
	print ' '
	for sup in supportedPlatforms:
		l = []
		for plat in Machines.items():
			if Machines.le(plat,sup): l.append(plat)
		sys.stdout.write(sup+':')
		sort(l,lambda x,y: string.lower(x)<=string.lower(y))
		sys.stdout.write(' { ')
		niceListOut(l)
		sys.stdout.write(' }')
		sys.stdout.write('\n')
		print ' '
	sys.stdout.write('- Your platform ')
	platSat(p.str())
	
def platSat(plat):
	p = Platform(plat)
	sys.stdout.write('['+plat+'] satisfies: ')
	l = []
	for plat in Machines.items():
		if Machines.le(p.str(),plat): l.append(plat)
	sort(l,lambda x,y: x<=y)
	if len(l)==0: l.append('*')
	sys.stdout.write('{ ')
	niceListOut(l)
	sys.stdout.write(' }\n')

# thisArch function added by Scot Kronenfeld 2/2009
# It is necessary for the new -pretend-arch and -arch command line options
# Also, the AIX architecture detection was fixed
def thisArch():
	if not _thisplatform.has_key('arch'):
		parch = os.path.join(pac_anchor,pacmanDir,'parch')
		if os.path.exists(parch):
			try:
				f = open(parch,'r')
				lines = f.readlines()
				f.close()
			except:
				abort("Can't read ["+parch+"].")
			
			if len(lines)>0 and len(lines[0])>0:
				arch = string.strip(lines[0][:-1])
			else:
				abort("File ["+parch+"] has been corrupted.")
		else:
			pre,arch = switchpar('pretend-arch')
			if not pre:
				if len(switchItems('pretend-arch'))>0:
					arch = switchItems('pretend-arch')[0]
				else:
                                        # Special case for the AIX architecture.  platform23.machine() returns garbage on most
                                        # AIX systems, so override it by checking if we're on powerpc
                                        if platform23.system() == "AIX":
                                                if "_syscmd_uname" in dir(platform23) and platform23._syscmd_uname('-p','') == 'powerpc':
                                                        arch = "ppc"
                                                else:
                                                        arch = platform23.machine()
                                        else:
                                                arch = platform23.machine()

		_thisplatform['arch'] = arch
	else:
		arch = _thisplatform['arch']
	return arch

# Added by Scot Kronenfeld 2/2009
# Used by the new -arch command line option, and called when -version is supplied
def archDisplay():
        print 'Your current architecture is ' + thisArch()


# Added by Scot Kronenfeld 2/2009
# Return a hash of the platforms equivalent to the current platform
# Necessary for @@PLATFORM@@ macro and packageRevision atoms
def equivalentOSes():
        currentOS = thisPlatform()
        osList = {}
        for os in Machines.items():
                if Machines.eq(currentOS, os):
                        osList[os] = 1
        return osList

class Platform(Environment):
	type   = 'platform'
	title  = 'Platforms'
	action = 'test platform'
	def __init__(self,platform=thisPlatform()): self._platform = platform
		
	def str(self): return self._platform
	def equal(self,x): return self._platform==x._platform
	
	def display(self,indent=0):
		print indent*' '+self.statusStr(),'Platform ['+self._platform+'].'
	def display2(self,indent=0):
		sys.stdout.write(indent*' ')
		sys.stdout.write('Your platform ['+self._platform+'] satisfies { ')
		l = []
		for plat in Machines.items():
			if Machines.le(self.str(),plat): l.append(plat)
		sort(l,lambda x,y: string.lower(x)<=string.lower(y))
		niceListOut(l)
		sys.stdout.write(' }\n')
	
	def platforms(self): return Machines.items()
	def platformClasses(self):
		c = Clusters(Machines.items())
		cl = c.cluster(lambda p,q: Machines.eq(p,q))
		return cl
		
	def supported(self): 
		return allow('unsupported-platforms') or exists(supportedPlatforms,lambda plat: Machines.le(self._platform,plat))
#-- Set
	def str(self): return self._platform
	def equal(self,p): return Machines.eq(self._platform,p._platform)

#-- Satisfiable
	def satisfiable(self): return Reason()
	def satisfied(self): return Reason("["+self.str()+"] has not been attempted yet.",not self.acquired)
	def acquire(self):
		if Machines.eq(self._platform,thisPlatform()): 
			r = Reason()
		else:
			r = self.platformReason()
		self.satset(r.ok())
		return r
	def retract(self): return Reason()
	
	def name(self): return self._platform
	def platformReason(self): return Reason('Your os is ['+thisPlatform()+'] but it must satisfy ['+self.name()+'].')

#-- SatisfyOrder
	def satisfies(self,p):
		if self.type[:8]==p.type[:8]:
			if    p.type=='platform'   : s = Machines.eq(self._platform,p._platform)
			elif  p.type=='platform <=': s = Machines.ge(self._platform,p.value)
			elif  p.type=='platform <' : s = Machines.gt(self._platform,p.value)
			elif  p.type=='platform >=': s = Machines.le(self._platform,p.value)
			elif  p.type=='platform >' : s = Machines.lt(self._platform,p.value)
			else:  abort('Error in Platform.')
		else:
			s = 0
		return s
				
class PlatformLE(StringAttr):
	type   = 'platform <='
	title  = 'Platform <=s'
	action = 'platform <='
	def satisfied(self): 
		r = Reason('Your os is ['+thisPlatform()+'] but it must be <= ['+self.value+'].',not Machines.ge(thisPlatform(),self.value) )
		self.satset(r.ok())
		return r
	
class PlatformLT(StringAttr):
	type   = 'platform <'
	title  = 'Platform <s'
	action = 'platform <'
	def satisfied(self): 
		r = Reason('Your os is ['+thisPlatform()+'] but it must be < ['+self.value+'].',not Machines.gt(thisPlatform(),self.value) )
		self.satset(r.ok())
		return r
	
class PlatformGE(StringAttr):
	type   = 'platform >='
	title  = 'Platform >=s'
	action = 'platform >='
	def satisfied(self): 
		r =  Reason('Your os is ['+thisPlatform()+'] but it must be >= ['+self.value+'].',not Machines.le(thisPlatform(),self.value))
		self.satset(r.ok())
		return r
	
class PlatformGT(StringAttr):
	type   = 'platform >'
	title  = 'Platform >s'
	action = 'platform >'
	def satisfied(self): 
		r = Reason('Your os is ['+thisPlatform()+'] but it must be > ['+self.value+'].',not Machines.lt(thisPlatform(),self.value))
		self.satset(r.ok())
		return r

def platformCheck():
	p = Platform()
	if not p.supported() and not (switch('help') or switch('h') or switch('-help') or switch('platforms') or switch('platform')):
		print '-'
		print '- Platform ['+p.str()+'] is not yet supported.'
		print '- Contact Pacman headquarters at http://physics.bu.edu/pacman/ to request a new platform.'
		print '- Use [% pacman -pretend-platform <platform>] to override.'
		print '-'
		sys.exit(1)
