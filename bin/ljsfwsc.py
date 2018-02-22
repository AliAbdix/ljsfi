#!/usr/bin/env python
import httplib, mimetypes
import os, sys, time, socket
import getopt
import commands
import socket
import re
import platform
import tempfile
from xml.dom import minidom
try:    from OpenSSL import crypto
except: pass
try:    socket.setdefaulttimeout(300)
except: pass

__version__ = "$Revision: 1.2 $"[11:-1]
__CONFMAP__ = { 'INSTALLERVER' : 11
              , 'INSTALLTOOLSVER' : 12
              , 'ARCH' : 2
              , 'RELARCH' : 3
              , 'SWNAME' : 13
              , 'SWREVISION' : 14
              , 'PACMANVERSION' : 15
              , 'PACMANPLATFORM' : 16
              , 'VERSIONAREA' : 17
              , 'ATLASFIX64' : 18
              , 'ATLASCOMPILER' : 19
              , 'KVPOST' : 20
              , 'RELTAG' : 21
              , 'OBSOLETE' : 22
              , 'REQUIRES' : 23
              , 'KITCACHE' : 24
              , 'PACKAGE' : 25
              , 'REQUIREDPRJ' : 26
              , 'PHYSICALPATH' : 27
              , 'LOGICALPATH' : 28
              , 'DISKSPACE' : 29
              , 'DBRELEASE' : 30
              , 'AUTOINSTALL' : 31 }
__WMSCONFMAP__ = { 'NS' : 'ns'
                , 'LB' : 'lb'
                , 'LD' : 'ld'
                , 'WMPROXY' : 'wmproxy'
                , 'MYPROXY' : 'myproxy' }
__CURLPOST__   = 'curl -k --connect-timeout 10'
__CURLFIELD__  = ' -F "%s=%s"'
__CURLFILE__   = ' -F "%s=@%s;filename=%s"'
__CURLEND__    = ' --stderr %s https://%s%s'

HELP="""LJSF request interface %s.
Usage: ljsfwsc.py [OPTION]...

Options:
  --cs <resource>              Use the resource name <resource>
  --rel <rel name>             Operate on release <rel name>
  --query                      query the database for requests.
  --queryrel                   query the database for release data.
  --update                     update the database.
  --allow-multi                allow multiple request for the same record.
  --set-job                    create or update a job definition.
  --set-rel                    update a release status in a site
                               (needs --cs and --status).
  --send-log                   send the logs to the DB
  --jobid=<job ID>             use the job id <job ID>.
  --jdlname=<JDL name>         use <JDL name> for the JDL of the job.
  --jdlfile=<fname>            set the filename of the JDL to <fname>.
  --jdltype=<type>             set the JDL type to <type>.
  --jobname=<name>             set the job name to <name>.
  --jobexit=<exit code>        set the job exit code to <exit code>.
  --jobinfo=<file name>        get the job info from <file name>.
  --joblog=<file name>         get the job log file from <file name>.
  --grid-name <name>           declare you are using the grid <name>
                               (current: %s)
  --create-conf=<conf file>    create the installation file <conf file>.
  --create-wmsvoconf=<file>    create the wms vo conf file <file>.
  --create-wmscmdconf=<file>   create the wms cmd conf file <file>.
  --conf-template=<template>   use <template> for the installation conf file.
                               (current: %s)
  --wmsvoconf-template=<tmpl>  use <tmpl> for the wms vo conf file.
                               (current: %s)
  --wmscmdconf-template=<tmpl> use <tmpl> for the wms cmd conf file.
                               (current: %s)
  --sitename=<site name>       site name.
  --arch=<arch>                set the architecture of the job to <arch>.
  --noout                      Suppress verbos output from the services.
  --osname=<OS name>           OS name.
  --osver=<OS version>         OS version.
  --osrel=<OS release>         OS release.
  --cename=<CE name>           CE FQDN.
  --bdii=<BDII hostname>       BDII FQDN.
  --ns=<NS hostname>           Network Server FQDN and port.
  --lb=<LB hostname>           Logging and Bookkeeping FQDN and port.
  --ld=<LD hostname>           Logging Destination FQDN and port.
  --wmproxy=<wmproxy hsname>   WMproxy FQDN.
  --myproxy=<myproxy hsname>   Myproxy FQDN.
  --reqtype=<request type>     Request type (validation,installation,removal,cleanup).
  --reqid=<request id>         Request id.
  --comments=<text>            Use <text> as comments.
  --nodeps                     Ignore dependencies.
  --tag=<tag name>             Use <tag name> as job tag.
  --show-dist                  Show the os distribution details as obtained
                               by lsb_release or the platform module
  --showtags                   Show the tags for installed releases in the CE.
  --showcs                     Show the CS along with the tag info.
  --obsolete                   Select only obsolete releases.
  --production                 Select only production releases.
  --autoinstall                Select only the releases set to autoinstall mode.
  --base                       Select only base releases, i.e. releases not
                               depending from any other ones.
  --patch                      Select only patch releases, i.e. releases
                               depending from other ones.
  --status=<status name>       Use status <status name>.
  --statreason=<text>          Set the status reason to <text>.
  --validation=<status>        Set the validation status to <status>.
  --help                       display this help and exit.
  --key <private key file>     use the provided private key
                               (current: %s).
  --cert <certificate file>    use the provided certificate
                               (current: %s).
  --host=<hostname>            hostname of the LJSF server
                               (current: %s).
  --sel=<selector>             use <selector> as target page
                               (current: %s).
  --debug                      debug mode (verbose).

Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>.
"""


class Fields:
  _fields = []

  def add(self, field, value):
    if not self.index(field): self._fields.append(field)
    setattr(self, field, value)

  def remove(self, field):
    if self.index(field): self._fields.remove(field)

  def index(self, field):
    return field in self._fields

  def get(self, field):
    return getattr(self,field)

  def getall(self):
    list = []
    for field in self._fields:
       list.append((field, getattr(self,field)))
    return list


class LJSFwsc:

    # Defaults
    DBURL          = "/atlas_install/protected"
    debug          = False
    mode           = 'insert'
    instconf       = ''
    wmsvoconf      = ''
    wmscmdconf     = ''
    conftmpl       = 'install.conf.template'
    wmsvoconftmpl  = 'wmsvo.conf.template'
    wmscmdconftmpl = 'wmscmd.conf.template'
    multi          = 'n'
    nodeps         = 'n'
    gridname       = None
    commonName     = None
    emailAddress   = None
    keyfile        = None
    certfile       = None

    if (os.environ.has_key('TEMPLATEPATH')):
        conftmpl = ('%s/%s' % (os.environ['TEMPLATEPATH'],conftmpl))
        wmsvoconftmpl = ('%s/%s' % (os.environ['TEMPLATEPATH'],wmsvoconftmpl))
        wmscmdconftmpl = ('%s/%s' % (os.environ['TEMPLATEPATH'],wmscmdconftmpl))
    pars     = Fields()
    if (os.environ.has_key('LJSFDBURL')):
        p = re.compile("(\S+)://([^/]*)(.*)")
        dbinfo = p.search(os.environ['LJSFDBURL']).groups()
        host  = dbinfo[1]
        DBURL = dbinfo[2]
    else:
        host = "atlas-install.roma1.infn.it"
    sel      = ("%s/subreq.php" % DBURL)
    if (os.environ.has_key('LJSFAGENTKEY')):
        keyfile  = ("%s" % os.environ['LJSFAGENTKEY'])
    else:
        if (os.environ.has_key('X509_USER_PROXY')):
            keyfile  = os.environ['X509_USER_PROXY']
        else:
            print "[LJSFwsc] No Agent key specified and no User Proxy found"
    if (os.environ.has_key('LJSFAGENTCERT')):
        certfile = ("%s" % os.environ['LJSFAGENTCERT'])
    else:
        if (os.environ.has_key('X509_USER_PROXY')):
            certfile  = os.environ['X509_USER_PROXY']
        else:
            print "[LJSFwsc] No Agent certificate specified and no User Proxy found"

    def setDebug(self,debug):    
        self.debug = debug

    def setGridName(self,name):    
        if (name.upper() == "ALL"): self.gridname = None
        else:                       self.gridname = name

    def setInstConf(self,conf):
        self.instconf = conf

    def setWMSVOConf(self,conf):
        self.wmsvoconf = conf

    def setWMSCMDConf(self,conf):
        self.wmscmdconf = conf

    def setConfTemplate(self,conf):
        self.conftmpl = conf

    def setWMSVOConfTemplate(self,conf):
        self.wmsvoconftmpl = conf

    def setWMSCMDConfTemplate(self,conf):
        self.wmscmdconftmpl = conf

    def setHost(self,host):
        self.host = host

    def setSelector(self,sel):
        self.sel = sel

    def setKey(self,keyfile):
        self.keyfile = keyfile

    def setCert(self,certfile):
        self.certfile = certfile

    def setAllowMulti(self):
        self.multi = 'y'

    def setNoDeps(self):
        self.nodeps = 'y'

    def setParam(self,par,val):    
        self.pars.add(par,val)

    def setMode(self,mode):
        if (mode == 'query'):
            self.mode = 'query'
            self.sel  = ("%s/showreq.php" % self.DBURL)
        elif (mode == 'queryrel'):
            self.mode = 'query'
            self.sel  = ("%s/showrel.php" % self.DBURL)
        elif (mode == 'showtags'):
            self.mode = 'query'
            self.sel  = ("%s/showtags.php" % self.DBURL)
        elif (mode == 'setjob'):
            self.mode = 'setjob'
            self.sel  = ("%s/setjob.php" % self.DBURL)
        elif (mode == 'setrel'):
            self.mode = 'setrel'
            self.sel  = ("%s/setrel.php" % self.DBURL)
        elif (mode == 'update'):
            self.mode = 'update'
            self.sel  = ("%s/req.php" % self.DBURL)
        elif (mode == 'showdist'):
            self.mode = 'showdist'

    def loadInstallDef (self, file='installdef.xml'):
        fh = open(file,'r')
        installdef = minidom.parse(fh)
        installDef = {
                       'gridname'    : None
                     , 'release'     : None
                     , 'project'     : None
                     , 'arch'        : None
                     , 'reqtype'     : None
                     , 'resource'    : None
                     , 'cename'      : None
                     , 'sitename'    : None
                     , 'physpath'    : None
                     , 'reltype'     : None
                     , 'pacman'      : None
                     , 'pacball'     : None
                     , 'pacballrepo' : None
                     , 'diskfree'    : None
                     , 'jobinfo'     : None
                     , 'tag'         : None
                     , 'dbrelease'   : None
                     , 'requires'    : None
                     }
        for node in installdef.getElementsByTagName('installdef'):
            for field in installDef.keys():
                try:    installDef[field] = node.getElementsByTagName(field)[0].childNodes[0].data
                except: pass
        return installDef

    def execute(self):
        if (not self.keyfile or not self.certfile):
            print "[LJSFwsc] Missing user credentials"
            return (-30,None)

        # Get the user info from the certificate
        try:
            cfile=open(self.certfile)
            cdata=cfile.read()
            x509cert=crypto.load_certificate(crypto.FILETYPE_PEM,cdata)
            cfile.close()
            self.commonName=x509cert.get_subject().commonName
            self.emailAddress=x509cert.get_subject().emailAddress
        except NameError:
            if (self.debug): print "[LJSFwsc] No pyOpenSSL module found. Will try to use plain openssl commands"
            cmd="openssl x509 -in %s -noout -subject" % self.certfile
            (s,o) = commands.getstatusoutput(cmd)
            if (s == 0):
                p = re.compile("^CN=(.*)")
                for part in o.split("\n")[0].split("/"):
                    match = p.search(part)
                    if (match):
                        self.commonName = match.group(1)
                        break
            cmd="openssl x509 -in %s -noout -email" % self.certfile
            (s,o) = commands.getstatusoutput(cmd)
            if (s == 0): self.emailAddress=o.split("\n")[0]
        if (self.commonName   == None): self.commonName='user'
        if (self.emailAddress == None): self.emailAddress='noreply@localhost'
        if (self.debug): print self.commonName
        if (self.debug): print self.emailAddress
        if (not self.pars.index('sitename')): self.pars.add('sitename', '-')
        if (not self.pars.index('osname')):   self.pars.add('osname', '-')
        if (not self.pars.index('osver')):    self.pars.add('osver', '-')
        if (not self.pars.index('osrel')):    self.pars.add('osrel', '-')
        if (not self.pars.index('cename') and self.pars.index('cs')):
            self.pars.add('cename', self.pars.get('cs').split(':')[0])
        if (not self.pars.index('comments')): self.pars.add('comments', '-')
        if (not self.pars.index('bdii')):     self.pars.add('bdii', 'lcg-bdii.cern.ch')
        if (not self.pars.index('reqtype')):  self.pars.add('reqtype', 'installation')

        if (self.mode == 'insert' and
            (not self.pars.index('cs') or not self.pars.index('rel'))):
            print "[LJSFwsc] Missing cs or rel argument for insert."
            return (10,None)

        if (self.mode == 'update' and
            (not self.pars.index('reqid') or not self.pars.index('status'))):
            print "[LJSFwsc] Missing reqid or status argument for update."
            return (10,None)

        if (self.mode == 'setjob'):
            if (self.pars.index('jobid')):
                if (not self.pars.index('status')):
                    print "[LJSFwsc] Missing status argument for set-job (with jobid)."
                    return (10,None)
            else:
                if (   not self.pars.index('cs') or not self.pars.index('jobname')
                    or not self.pars.index('rel') or not self.pars.index('status')
                   ):
                    print "[LJSFwsc] Missing parameters for set-job (no jobid specified)."
                    print "Needed parameters are:"
                    print "   cs, jobname, rel, status"
                    return (10,None)

        if (self.mode == 'setrel'):
            if (   not self.pars.index('status') or not self.pars.index('cs')
                or not self.pars.index('rel')):
                print "[LJSFwsc] Missing cs, rel or status arguments for setrel."
                return (10,None)

        if (self.mode == 'insert'):
            return self.sendData()
        elif (self.mode == 'setjob'):
            return self.setJob()
        elif (self.mode == 'setrel'):
            return self.setRel()
        elif (self.mode == 'query'):
            return self.queryData()
        elif (self.mode == 'update'):
            return self.updateData()
        elif (self.mode == 'showdist'):
            return self.showDist()
        else:
            print "Unknown mode %s" % mode
            return (1, None)


    def sendData(self):
        # Prepare the data to send
        data = (
                ('submit','yes')
               ,('sitename',self.pars.get('sitename'))
               ,('osname',self.pars.get('osname'))
               ,('osver',self.pars.get('osver'))
               ,('osrel',self.pars.get('osrel'))
               ,('cs',self.pars.get('cs'))
               ,('cename',self.pars.get('cename'))
               ,('user',self.commonName.encode())
               ,('email',self.emailAddress.encode())
               ,('rel',self.pars.get('rel'))
               ,('bdii',self.pars.get('bdii'))
               ,('reqtype',self.pars.get('reqtype'))
               ,('comments',self.pars.get('comments'))
               ,('multi',self.multi)
               )
        if (not self.debug):           data += (('quiet','1'),)
        if (self.pars.index('arch')):  data += (('arch',self.pars.get('arch')),)
        if (self.nodeps == "y"):       data += (('nodeps','yes'),)
        if (self.pars.index('noout')): data += (('noout','1'),)
        if self.pars.index('status'):
            data+=(('status',self.pars.get('status')),)
        if (self.debug):
            print "[LJSFwsc] host:     %s" % self.host
            print "[LJSFwsc] selector: %s" % self.sel
            print "[LJSFwsc] data:"
            print data
        # Send the data
        curltemp = tempfile.mkstemp()
        os.close(curltemp[0])
        curlcmd = __CURLPOST__
        for field in data:
            curlcmd += __CURLFIELD__ % (field[0],field[1])
        curlcmd += __CURLEND__ % (curltemp[1], self.host, self.sel)
        (s,reply) = commands.getstatusoutput(curlcmd)
        if (s == 0):
            os.remove(curltemp[1])
            if (len(reply) > 2): return (0,reply)
            else: return (2,None)
        else:
            print "[LJSFwsc] Last command failed: %s" % curlcmd
            print "[LJSFwsc] %s" % reply
            print "[LJSFwsc] Failed to send data with curl"
            curlerr = open(curltemp[1])
            print "[LJSFwsc] CURL error: %s" % curlerr.read()
            curlerr.close()
            os.remove(curltemp[1])
            print "[LJSFwsc] Trying with the embedded engine"
            # Curl failed. Try with the embedded engine
            try:
                reply = cself.post_multipart(self.host, self.sel, data)
                if (len(reply) > 2): return (0,reply)
                else: return (3,None)
            except:
                print "[LJSFwsc] Cannot send LJSF request";
                return (1,None)


    def queryData(self):
        """
        Query DB for requests
        """
        h = httplib.HTTPSConnection(self.host, 443, self.keyfile, self.certfile, 0)
        url = self.sel
        numArgs=0
        if (self.pars.index('status')):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%sstatus=%s" % (url, sep, self.pars.get('status')))
            numArgs=numArgs+1
        if (self.pars.index('showcs')):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%sshowcs" % (url, sep))
            numArgs=numArgs+1
        if (self.pars.index('rel')):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%srel=%s" % (url, sep, self.pars.get('rel')))
            numArgs=numArgs+1
        if (self.pars.index('obsolete')):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%sobsolete=%s" % (url, sep, self.pars.get('obsolete')))
            numArgs=numArgs+1
        if (self.pars.index('autoinstall')):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%sautoinstall=%s" % (url, sep, self.pars.get('autoinstall')))
            numArgs=numArgs+1
        if (self.pars.index('base')):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%sbase=%s" % (url, sep, self.pars.get('base')))
            numArgs=numArgs+1
        if (self.pars.index('patch')):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%spatch=%s" % (url, sep, self.pars.get('patch')))
            numArgs=numArgs+1
        if (self.pars.index('cename')):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%scename=%s" % (url, sep, self.pars.get('cename')))
            numArgs=numArgs+1
        if (self.gridname):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%sgridname=%s" % (url, sep, self.gridname))
            numArgs=numArgs+1
        h.request('GET', url)
        response = h.getresponse().read()
        if (len(response)>2): retList = (0,response[:-1])
        else:                 retList = (1,None)

        #fields = response.split('\n')[0].split(',')
        # Get the conf map or use the default one
        fields = []
        field_indx = 0
        for field in response.split('\n')[0].split(','):
            field_data = field.split('=')
            if (len(field_data) > 1):
                fields.append(field_data[1])
                __CONFMAP__[field_data[0]] = field_indx
                field_indx += 1
            else:
                fields.append(field)

        if (self.instconf != ''):
            confin  = open(self.conftmpl, 'r')
            if (confin):
                confout = open(self.instconf, 'w')
                if (confout):
                    confdata=confin.read()
                    for key in __CONFMAP__.keys():
                        keyword  = ("@%s@" % key)
                        confdata = confdata.replace(keyword, fields[__CONFMAP__[key]].replace('$','\$'))
                    confdata = confdata.replace("@WMSVOCONF@", self.wmsvoconf)
                    confdata = confdata.replace("@WMSCMDCONF@", self.wmscmdconf)
                    confout.write(confdata)
                    confout.close()
                else:
                    if (self.debug):
                        print "[LJSFwsc] Cannot open %s for output" % self.instconf
                confin.close()
            else:
                if (self.debug):
                    print "[LJSFwsc] Cannot open %s for input" % self.conftmpl
        if (self.wmsvoconf != ''):
            self.writeConfig(self.wmsvoconftmpl,self.wmsvoconf,__WMSCONFMAP__)
        if (self.wmscmdconf != ''):
            self.writeConfig(self.wmscmdconftmpl,self.wmscmdconf,__WMSCONFMAP__)
        return retList


    def setJob(self):
        # Prepare the data to send
        data = (
                ('submit','yes')
               ,('user',self.commonName.encode())
               ,('email',self.emailAddress.encode())
               )
        if (self.gridname):                 data += (('gridname',self.gridname),)
        if (not self.debug):                data += (('quiet','1'),)
        if (self.pars.index('noout')):      data += (('noout','1'),)
        if (self.pars.index('jobid')):      data += (('jobid',self.pars.get('jobid')),)
        if (self.pars.index('sitename')):   data += (('sitename',self.pars.get('sitename')),)
        if (self.pars.index('arch')):       data += (('arch',self.pars.get('arch')),)
        if (self.pars.index('osname')):     data += (('osname',self.pars.get('osname')),)
        if (self.pars.index('osver')):      data += (('osver',self.pars.get('osver')),)
        if (self.pars.index('osrel')):      data += (('osrel',self.pars.get('osrel')),)
        if (self.pars.index('cs')):         data += (('cs',self.pars.get('cs')),)
        if (self.pars.index('cename')):     data += (('cename',self.pars.get('cename')),)
        if (self.pars.index('rel')):        data += (('rel',self.pars.get('rel')),)
        if (self.pars.index('jdlname')):    data += (('jdlname',self.pars.get('jdlname')),)
        if (self.pars.index('jdltype')):    data += (('jdltype',self.pars.get('jdltype')),)
        if (self.pars.index('jdlfile')):
            try:
                jdlf=open(self.pars.get('jdlfile'))
                jdldata=jdlf.read()
                jdlf.close()
                data += (('jdldata',jdldata),)
            except:
                pass
        if (self.pars.index('reqid')):      data += (('reqid',self.pars.get('reqid')),)
        if (self.pars.index('tag')):        data += (('tag',self.pars.get('tag')),)
        if (self.pars.index('jobname')):    data += (('jobname',self.pars.get('jobname')),)
        if (self.pars.index('status')):     data += (('status',self.pars.get('status')),)
        if (self.pars.index('statreason')): data += (('statreason',self.pars.get('statreason')),)
        if (self.pars.index('validation')): data += (('validation',self.pars.get('validation')),)
        if (self.pars.index('jobexit')):
            if (type(self.pars.get('jobexit')) != type('')):
                jobexit = '%s' % self.pars.get('jobexit')
            else:
                jobexit = self.pars.get('jobexit')
            data += (('jobexit',jobexit),)
        if (self.pars.index('jobinfo')):
            try:
                jobf=open(self.pars.get('jobinfo'))
                jobinfo=" "+jobf.read().replace('"','\\"')
                jobf.close()
                data += (('jobinfo',jobinfo),)
            except:
                pass
        files  = ()
        fnames = ()
        if (self.pars.index('joblog')):
            try:
                logfile = open(self.pars.get('joblog'))
                logdata = logfile.read()
                logfile.close()
                files = (('logfile',os.path.basename(self.pars.get('joblog')),logdata),)
                fnames = (('logfile',self.pars.get('joblog'),os.path.basename(self.pars.get('joblog'))),)
            except:
                pass

        if (self.debug):
            print "[LJSFwsc] host:     %s" % self.host
            print "[LJSFwsc] selector: %s" % self.sel
            print "[LJSFwsc] data:"
            print data
            print "DEBUG> files:"
            #print files
        # Send the data
        curltemp = tempfile.mkstemp()
        os.close(curltemp[0])
        curlcmd = __CURLPOST__
        for field in data:
            curlcmd += __CURLFIELD__ % (field[0],field[1])
        for fname in fnames:
            curlcmd += __CURLFILE__ % (fname[0],fname[1],fname[2])
        curlcmd += __CURLEND__ % (curltemp[1], self.host, self.sel)
        (s,reply) = commands.getstatusoutput(curlcmd)
        if (s == 0):
            os.remove(curltemp[1])
            if (len(reply) > 2): return (0,reply)
            else: return (2,None)
        else:
            # Curl failed. Try with the embedded engine
            print "[LJSFwsc] Last command failed: %s" % curlcmd
            print "[LJSFwsc] %s" % reply
            print "[LJSFwsc] Failed to send data with curl"
            curlerr = open(curltemp[1])
            print "[LJSFwsc] CURL error: %s" % curlerr.read()
            curlerr.close()
            os.remove(curltemp[1])
            print "[LJSFwsc] Trying with the embedded engine"
            try:
                reply = self.post_multipart(self.host, self.sel, data, files)
                if (len(reply) > 2): return (0,reply)
                else: return (3,None)
            except:
                print "[LJSFwsc] Cannot send LJSF request";
                return (1,None)


    def setRel(self):
        # Prepare the data to send
        data = (
                ('submit','yes')
               ,('user',self.commonName.encode())
               ,('email',self.emailAddress.encode())
               ,('rel',self.pars.get('rel'))
               ,('cs',self.pars.get('cs'))
               ,('status',self.pars.get('status'))
               )
        if (not self.debug):                data += (('quiet','1'),)
        if (self.pars.index('noout')):      data += (('noout','1'),)
        if (self.pars.index('comments')):   data += (('comments',self.pars.get('comments')),)

        if (self.debug):
            print "[LJSFwsc] host:     %s" % self.host
            print "[LJSFwsc] selector: %s" % self.sel
            print "[LJSFwsc] data:"
            print data
        # Send the data
        curltemp = tempfile.mkstemp()
        os.close(curltemp[0])
        curlcmd = __CURLPOST__
        for field in data:
            curlcmd += __CURLFIELD__ % (field[0],field[1])
        curlcmd += __CURLEND__ % (curltemp[1], self.host, self.sel)
        (s,reply) = commands.getstatusoutput(curlcmd)
        if (s == 0):
            os.remove(curltemp[1])
            if (len(reply) > 2): return (0,reply)
            else: return (2,None)
        else:
            # Curl failed. Try with the embedded engine
            print "[LJSFwsc] Last command failed: %s" % curlcmd
            print "[LJSFwsc] %s" % reply
            print "[LJSFwsc] Failed to send data with curl"
            curlerr = open(curltemp[1])
            print "[LJSFwsc] CURL error: %s" % curlerr.read()
            curlerr.close()
            os.remove(curltemp[1])
            print "[LJSFwsc] Trying with the embedded engine"
            try:
                reply = self.post_multipart(self.host, self.sel, data)
                if (len(reply) > 2): return (0,reply)
                else: return (3,None)
            except:
                print "[LJSFwsc] Cannot send LJSF request";
                return (1,None)


    def writeConfig(self,tmpl,conf,map):
        confin  = open(tmpl, 'r')
        if (confin):
            confout = open(conf, 'w')
            if (confout):
                confdata=confin.read()
                for key in map.keys():
                    keyword  = ("@%s@" % key)
                    if (self.pars.index(map[key])):
                        confdata = confdata.replace(keyword, self.pars.get(map[key]).replace('$','\$'))
                confout.write(confdata)
                confout.close()
            else:
                if (self.debug):
                    print "[LJSFwsc] Cannot open %s for output" % conf
            confin.close()
        else:
            if (self.debug):
                print "[LJSFwsc] Cannot open %s for input" % tmpl


    def updateData(self):
        # Prepare the data to send
        data = (
                ('submit','yes')
               ,('id',self.pars.get('reqid'))
               ,('reqstat',self.pars.get('status'))
               ,('ws','yes')
               ,('admincomm',self.pars.get('comments'))
               )
        if (self.debug):
            print "[LJSFwsc] host:     %s" % self.host
            print "[LJSFwsc] selector: %s" % self.sel
            print "[LJSFwsc] data:"
            print data
        # Send the data
        curltemp = tempfile.mkstemp()
        os.close(curltemp[0])
        curlcmd = __CURLPOST__
        for field in data:
            curlcmd += __CURLFIELD__ % (field[0],field[1])
        curlcmd += __CURLEND__ % (curltemp[1], self.host, self.sel)
        (s,reply) = commands.getstatusoutput(curlcmd)
        if (s == 0):
            os.remove(curltemp[1])
            return (0,reply)
        else:
            # Curl failed. Try with the embedded engine
            print "[LJSFwsc] Last command failed: %s" % curlcmd
            print "[LJSFwsc] %s" % reply
            print "[LJSFwsc] Failed to send data with curl"
            curlerr = open(curltemp[1])
            print "[LJSFwsc] CURL error: %s" % curlerr.read()
            curlerr.close()
            os.remove(curltemp[1])
            print "[LJSFwsc] Trying with the embedded engine"
            try:
                reply = self.post_multipart(self.host, self.sel, data)
                return (0,reply)
            except:
                print "[LJSFwsc] Cannot send LJSF request";
                return (1,None)

    def showDist(self):
        # Status code
        st = 0
        # Try first with lsb_release
        __LSB_DIST__ = "lsb_release -is"
        __LSB_REL__  = "lsb_release -rs"
        __LSB_CODE__ = "lsb_release -cs"
        (sd,distribution) = commands.getstatusoutput(__LSB_DIST__)
        (sr,release)      = commands.getstatusoutput(__LSB_REL__)
        (sc,codename)     = commands.getstatusoutput(__LSB_CODE__)
        if (sd != 0 or sr != 0 or sc != 0):
            # if lsb_release fails, try with the platform module
            (pd, pr, pc) = platform.dist()
            if (pd == ""):
                # If the platform module does not understand this platform
                # try to check if we are on a Mac
                (osv, (pd, pr, pc), osa) = platform.mac_ver()
                if (osv != ""):
                    pd = "MacOS"
                    pr = osv
                    pc = "Darwin"
                else:
                    st = 1
            if (sd != 0): distribution = pd
            if (sr != 0): release = pr
            if (sc != 0): codename = pc
        return (st,(distribution,release,codename))
            

    def post_multipart(self, host, selector, fields, files=()):
        """
        Post fields to an https host as multipart/form-data.
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files.
        Return the server's response page.
        """
        content_type, body = self.encode_multipart_formdata(fields, files)
        h = httplib.HTTPSConnection(host, 443, self.keyfile, self.certfile)
        h.putrequest('POST', selector)
        h.putheader('content-type', content_type)
        h.putheader('content-length', str(len(body)))
        h.endheaders()
        h.send(body)
        response = h.getresponse()
        return response.read()

    def encode_multipart_formdata(self, fields, files=()):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files.
        Return (content_type, body) ready for httplib.HTTP instance
        """
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' 
% (key, filename))
            L.append('Content-Type: %s' % self.get_content_type(filename))
            L.append('')
            L.append(("%s" % value))
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body

    def get_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

# Help
def help():
    print HELP % (__version__.strip(),ljsfwsc.gridname,ljsfwsc.conftmpl,ljsfwsc.wmsvoconftmpl,ljsfwsc.wmscmdconftmpl,ljsfwsc.keyfile,ljsfwsc.certfile,ljsfwsc.host,ljsfwsc.sel)


# Main class
if __name__ == '__main__':
    ljsfwsc=LJSFwsc()
    # Options
    short_options = ""
    long_options  = ["query", "queryrel", "update", "help"
                    ,"set-job", "grid-name=", "jobid=", "jdlname="
                    ,"jdlfile=", "jdltype=", "tag=", "jobname="
                    ,"jobexit=", "jobinfo=", "joblog=", "noout", "set-rel"
                    ,"create-conf=", "conf-template=", "allow-multi"
                    ,"create-wmsvoconf=", "wmsvoconf-template="
                    ,"create-wmscmdconf=", "wmscmdconf-template="
                    ,"host=", "sitename=", "obsolete", "arch="
                    ,"osname=", "osver=", "osrel=", "production"
                    ,"cename=", "cs=", "rel=", "sel="
                    ,"bdii=", "reqtype=", "reqid=", "comments=", "nodeps"
                    ,"ns=", "lb=", "ld=", "wmproxy=", "myproxy=", "validation="
                    ,"showcs", "showtags", "status=", "statreason="
                    ,"show-dist", "key=", "cert=", "debug", "autoinstall"
                    ,"base", "patch"]
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                     short_options,
                     long_options,
                   )
    except getopt.GetoptError:
        # Print help
        print "GetOpt Error"
        help()
        sys.exit(20)

    for cmd, arg in opts:
        if cmd in ('--debug',):                 ljsfwsc.setDebug(True)
        elif cmd in ('--query',):               ljsfwsc.setMode('query')
        elif cmd in ('--queryrel',):            ljsfwsc.setMode('queryrel')
        elif cmd in ('--showtags',):            ljsfwsc.setMode('showtags')
        elif cmd in ('--show-dist',):           ljsfwsc.setMode('showdist')
        elif cmd in ('--set-job',):             ljsfwsc.setMode('setjob')
        elif cmd in ('--set-rel',):             ljsfwsc.setMode('setrel')
        elif cmd in ('--update',):              ljsfwsc.setMode('update')
        elif cmd in ('--showcs',):              ljsfwsc.setParam('showcs', 'yes')
        elif cmd in ('--grid-name',):           ljsfwsc.setGridName(arg)
        elif cmd in ('--create-conf',):         ljsfwsc.setInstConf(arg)
        elif cmd in ('--create-wmsvoconf',):    ljsfwsc.setWMSVOConf(arg)
        elif cmd in ('--create-wmscmdconf',):   ljsfwsc.setWMSCMDConf(arg)
        elif cmd in ('--conf-template',):       ljsfwsc.setConfTemplate(arg)
        elif cmd in ('--wmsvoconf-template',):  ljsfwsc.setWMSVOConfTemplate(arg)
        elif cmd in ('--wmscmdconf-template',): ljsfwsc.setWMSCMDConfTemplate(arg)
        elif cmd in ('--host',):                ljsfwsc.setHost(arg)
        elif cmd in ('--sel',):                 ljsfwsc.setSelector(arg)
        elif cmd in ('--key',):                 ljsfwsc.setKey(arg)
        elif cmd in ('--cert',):                ljsfwsc.setCert(arg)
        elif cmd in ('--allow-multi',):         ljsfwsc.setAllowMulti()
        elif cmd in ('--nodeps',):              ljsfwsc.setNoDeps()
        elif cmd in ('--jobid',):               ljsfwsc.setParam('jobid', arg)
        elif cmd in ('--jdlname',):             ljsfwsc.setParam('jdlname', arg)
        elif cmd in ('--jdlfile',):             ljsfwsc.setParam('jdlfile', arg)
        elif cmd in ('--jdltype',):             ljsfwsc.setParam('jdltype', arg)
        elif cmd in ('--tag',):                 ljsfwsc.setParam('tag', arg)
        elif cmd in ('--jobname',):             ljsfwsc.setParam('jobname', arg)
        elif cmd in ('--jobexit',):             ljsfwsc.setParam('jobexit', arg)
        elif cmd in ('--jobinfo',):             ljsfwsc.setParam('jobinfo', arg)
        elif cmd in ('--joblog',):              ljsfwsc.setParam('joblog', arg)
        elif cmd in ('--sitename',):            ljsfwsc.setParam('sitename', arg)
        elif cmd in ('--arch',):                ljsfwsc.setParam('arch', arg)
        elif cmd in ('--osname',):              ljsfwsc.setParam('osname', arg)
        elif cmd in ('--osver',):               ljsfwsc.setParam('osver', arg)
        elif cmd in ('--osrel',):               ljsfwsc.setParam('osrel', arg)
        elif cmd in ('--cename',):              ljsfwsc.setParam('cename', arg)
        elif cmd in ('--cs',):                  ljsfwsc.setParam('cs', arg)
        elif cmd in ('--bdii',):                ljsfwsc.setParam('bdii', arg)
        elif cmd in ('--comments',):            ljsfwsc.setParam('comments', arg)
        elif cmd in ('--reqtype',):             ljsfwsc.setParam('reqtype', arg)
        elif cmd in ('--reqid',):               ljsfwsc.setParam('reqid', arg)
        elif cmd in ('--status',):              ljsfwsc.setParam('status', arg)
        elif cmd in ('--statreason',):          ljsfwsc.setParam('statreason', arg)
        elif cmd in ('--validation',):          ljsfwsc.setParam('validation', arg)
        elif cmd in ('--noout',):               ljsfwsc.setParam('noout', 'yes')
        elif cmd in ('--rel',):                 ljsfwsc.setParam('rel', arg)
        elif cmd in ('--obsolete',):            ljsfwsc.setParam('obsolete', '1')
        elif cmd in ('--production',):          ljsfwsc.setParam('obsolete', '0')
        elif cmd in ('--autoinstall',):         ljsfwsc.setParam('autoinstall', '1')
        elif cmd in ('--base',):                ljsfwsc.setParam('base', '1')
        elif cmd in ('--patch',):               ljsfwsc.setParam('patch', '1')
        elif cmd in ('--ld',):                  ljsfwsc.setParam('ld', arg)
        elif cmd in ('--myproxy',):             ljsfwsc.setParam('myproxy', '"%s"' % arg)
        elif cmd in ('--wmproxy',):
            wmproxylist = ""
            for wmproxy in arg.split(" "):
                if (len(wmproxy)>0):
                    if (len(wmproxylist)>0): wmproxylist += ","
                    wmproxylist += ('"%s"' % wmproxy)
            if (len(wmproxylist) >0): ljsfwsc.setParam('wmproxy', wmproxylist)
        elif cmd in ('--ns',):
            nslist = ""
            for ns in arg.split(" "):
                if (len(ns)>0):
                    if (len(nslist)>0): nslist += ","
                    nslist += ('"%s"' % ns)
            if (len(nslist) >0): ljsfwsc.setParam('ns', nslist)
        elif cmd in ('--lb',):
            lblist = ""
            for lb in arg.split(" "):
                if (len(lb)>0):
                    if (len(lblist)>0): lblist += ","
                    lblist += ('{"%s"}' % lb)
            if (len(lblist) >0): ljsfwsc.setParam('lb', lblist)
        elif cmd in ('--help',):
            help()
            sys.exit()

    (s,o) = ljsfwsc.execute()
    if (s == 0):
        print o
    sys.exit(s)
