#!/usr/bin/env python
import httplib, mimetypes
import os, sys, time, socket, re
import getopt
import commands
from xml.dom import minidom
from OpenSSL import crypto

try:
    socket.setdefaulttimeout(60)
except:
    pass

__version__ = "$Revision: 2.1 $"[11:-1]
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
              , 'RELCATEGORY' : 32 }
__WMSCONFMAP__ = { 'NS' : 'ns'
                , 'LB' : 'lb'
                , 'LD' : 'ld'
                , 'WMPROXY' : 'wmproxy'
                , 'MYPROXY' : 'myproxy' }

HELP="""LJSF request interface %s.
Usage: ljsfreq.py --cs=<contact string> --rel=<release> [OPTION]...

Options:
  --grid-name <name>                   declare you are using the grid <name>
                                       (current: %s)
  --query                              query the database for requests.
  --queryrel                           query the database for release data.
  --querysite                          query the database for site data.
  --update                             update the database.
  --allow-multi                        allow multiple request for the same record.
  --create-conf=<conf file>            create the installation file <conf file>.
  --create-wmsvoconf=<file>            create the wms vo conf file <file>.
  --create-wmscmdconf=<file>           create the wms cmd conf file <file>.
  --conf-template=<template>           use <template> for the installation conf file.
                                       (current: %s)
  --wmsvoconf-template=<tmpl>          use <tmpl> for the wms vo conf file.
                                       (current: %s)
  --wmscmdconf-template=<tmpl>          use <tmpl> for the wms cmd conf file.
                                       (current: %s)
  --atlas-sitename=<atlas site name>   ATLAS site name, defaults to sitename
                                       if not specified.
  --sitename=<site name>               site name.
  --sitetype=<site type>               site type.
  --facility=<facility name>           facility name
  --max-records=<num>                  max number of records to print
  --offset=<num>                       number of requests to skip
  --osname=<OS name>                   OS name.
  --osver=<OS version>                 OS version.
  --osrel=<OS release>                 OS release.
  --cename=<CE name>                   CE FQDN.
  --siteid=<site ID>                   Site numerical ID
  --bdii=<BDII hostname>               BDII FQDN.
  --ns=<NS hostname>                   Network Server FQDN and port.
  --lb=<LB hostname>                   Logging and Bookkeeping FQDN and port.
  --ld=<LD hostname>                   Logging Destination FQDN and port.
  --wmproxy=<wmproxy hsname>           WMproxy FQDN.
  --myproxy=<myproxy hsname>           Myproxy FQDN.
  --reqtype=<request type>             Request type (validation,installation,removal,cleanup).
  --reqid=<request id>                 Request id.
  --comments=<text>                    Use <text> as comments.
  --nodeps                             Ignore dependencies
  --showtags                           Show the tags for installed releases in the CE
  --showcs                             Show the CS along with the tag info
  --status=<status name>               Use status <status name>
  --help                               display this help and exit.
  --key <private key file>             use the provided private key
                                       (current: %s)
  --cert <certificate file>            use the provided certificate
                                       (current: %s)
  --host=<hostname>                    hostname of the LJSF server
                                       (current: %s)
  --sel=<selector>                     use <selector> as target page
                                       (current: %s)
  --since=<timestamp>                  select records newer than <timestamp>
  --age=<timestamp>                    select records <= than <timestamp>
  --debug                              debug mode (verbose).
  --protocol=<n>                       use protocol version <n>.
  --timeout <seconds>                  timeout in seconds.
  --default-site-status={0|1}          default site status for new sites,
                                       0=disabled, 1=enabled (default).

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

  def reset(self):
    self._fields = []

class LJSFpost:

    # Options
    short_options = ""
    long_options  = ["query", "queryrel", "querysite", "update", "help"
                    ,"create-conf=", "conf-template=", "allow-multi"
                    ,"create-wmsvoconf=", "wmsvoconf-template="
                    ,"create-wmscmdconf=", "wmscmdconf-template="
                    ,"host=", "atlas-sitename=", "sitename=", "sitetype="
                    ,"obsolete", "osname=", "osver=", "osrel="
                    ,"production", "grid-name=", "facility="
                    ,"cename=", "cs=", "rel=", "sel=", "siteid="
                    ,"bdii=", "reqtype=", "reqid=", "comments=", "nodeps"
                    ,"ns=", "lb=", "ld=", "wmproxy=", "myproxy=", "since="
                    ,"showcs","showtags","status=","key=", "cert=", "debug"
                    ,"age=", "timeout=", "default-site-status="
                    ,"protocol=", "max-records=", "offset="]

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
    facility       = None
    maxrecords     = None
    offset         = None
    protocol       = 1
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
        DBURL = "/atlas_install/protected"
    sel      = ("%s/subreq.php" % DBURL)
    if (os.environ.has_key('LJSFAGENTKEY')):
        keyfile  = ("%s" % os.environ['LJSFAGENTKEY'])
    else:
        if (os.environ.has_key('X509_USER_PROXY')):
            keyfile  = os.environ['X509_USER_PROXY']
        else:
            print "No Agent key specified and no User Proxy found"
            sys.exit(-1)
    if (os.environ.has_key('LJSFAGENTCERT')):
        certfile = ("%s" % os.environ['LJSFAGENTCERT'])
    else:
        if (os.environ.has_key('X509_USER_PROXY')):
            certfile  = os.environ['X509_USER_PROXY']
        else:
            print "No Agent certificate specified and no User Proxy found"
            sys.exit(-1)

    def reset(self):
        self.pars.reset()

    def main(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:],
                         self.short_options,
                         self.long_options,
                       )
        except getopt.GetoptError:
            # Print help
            print "GetOpt Error"
            self.help()
            sys.exit(-1)

        for cmd, arg in opts:
            if cmd in ('--debug',):
                self.debug = True
            if cmd in ('--query',):
                self.mode = 'query'
                self.sel  = ("%s/showreq.php" % self.DBURL)
            if cmd in ('--queryrel',):
                self.mode = 'query'
                if (self.protocol == 1):
                    self.sel  = ("%s/showrel.php" % self.DBURL)
                else:
                    self.sel  = ("%s/showrel_v2.php" % self.DBURL)
            if cmd in ('--querysite',):
                self.mode = 'query'
                self.sel  = ("%s/showsite.php" % self.DBURL)
            elif cmd in ('--showtags',):
                self.mode = 'query'
                self.sel  = ("%s/showtags.php" % self.DBURL)
            if cmd in ('--protocol',):
                self.protocol = int(arg)
            elif cmd in ('--showcs',):
                self.pars.add('showcs', "yes")
            if cmd in ('--create-conf',):
                self.instconf = arg
            if cmd in ('--create-wmsvoconf',):
                self.wmsvoconf = arg
            if cmd in ('--create-wmscmdconf',):
                self.wmscmdconf = arg
            if cmd in ('--conf-template',):
                self.conftmpl = arg
            if cmd in ('--wmsvoconf-template',):
                self.wmsvoconftmpl = arg
            if cmd in ('--wmscmdconf-template',):
                self.wmscmdconftmpl = arg
            if cmd in ('--update',):
                self.mode = 'update'
                self.sel  = ("%s/req.php" % self.DBURL)
            elif cmd in ('--host',):
                self.host = arg
            elif cmd in ('--sel',):
                self.sel = arg
            elif cmd in ('--atlas-sitename',):
                self.pars.add('atlassitename', ("%s" % arg))
            elif cmd in ('--sitename',):
                self.pars.add('sitename', ("%s" % arg))
            elif cmd in ('--sitetype',):
                self.pars.add('sitetype', ("%s" % arg))
            elif cmd in ('--facility',):
                if (arg.upper() == "ALL"): self.facility = None
                else:                      self.facility = arg
            elif cmd in ('--max-records',):
                self.maxrecords = int(arg)
            elif cmd in ('--offset',):
                self.offset = int(arg)
            elif cmd in ('--osname',):
                self.pars.add('osname', ("%s" % arg))
            elif cmd in ('--osver',):
                self.pars.add('osver', ("%s" % arg))
            elif cmd in ('--osrel',):
                self.pars.add('osrel', ("%s" % arg))
            elif cmd in ('--cename',):
                self.pars.add('cename', ("%s" % arg))
            elif cmd in ('--cs',):
                self.pars.add('cs', ("%s" % arg))
            elif cmd in ('--siteid',):
                self.pars.add('siteid', ("%s" % arg))
            elif cmd in ('--bdii',):
                self.pars.add('bdii', ("%s" % arg))
            elif cmd in ('--comments',):
                self.pars.add('comments', ("%s" % arg))
            elif cmd in ('--reqtype',):
                self.pars.add('reqtype', ("%s" % arg))
            elif cmd in ('--reqid',):
                self.pars.add('reqid', ("%s" % arg))
            elif cmd in ('--status',):
                self.pars.add('status', ("%s" % arg))
            elif cmd in ('--grid-name',):
                if (arg.upper() == "ALL"): self.gridname = None
                else:                      self.gridname = arg
            elif cmd in ('--key',):
                self.keyfile = arg
            elif cmd in ('--cert',):
                self.certfile = arg
            elif cmd in ('--rel',):
                self.pars.add('rel', ("%s" % arg))
            elif cmd in ('--allow-multi',):
                self.multi = 'y'
            elif cmd in ('--nodeps',):
                self.nodeps = 'y'
            elif cmd in ('--obsolete',):
                self.pars.add('obsolete', "1")
            elif cmd in ('--production',):
                self.pars.add('obsolete', "0")
            elif cmd in ('--ns',):
                nslist = ""
                for ns in arg.split(" "):
                    if (len(ns)>0):
                        if (len(nslist)>0): nslist += ","
                        nslist += ('"%s"' % ns)
                if (len(nslist) >0): self.pars.add('ns', nslist)
            elif cmd in ('--lb',):
                lblist = ""
                for lb in arg.split(" "):
                    if (len(lb)>0):
                        if (len(lblist)>0): lblist += ","
                        lblist += ('{"%s"}' % lb)
                if (len(lblist) >0): self.pars.add('lb', lblist)
            elif cmd in ('--ld',):
                self.pars.add('ld', ('"%s"' % arg))
            elif cmd in ('--wmproxy',):
                wmproxylist = ""
                for wmproxy in arg.split(" "):
                    if (len(wmproxy)>0):
                        if (len(wmproxylist)>0): wmproxylist += ","
                        wmproxylist += ('"%s"' % wmproxy)
                if (len(wmproxylist) >0): self.pars.add('wmproxy', wmproxylist)
            elif cmd in ('--myproxy',):
                self.pars.add('myproxy', '"%s"' % arg)
            elif cmd in ('--since',):
                self.pars.add('since', arg)
            elif cmd in ('--age',):
                self.pars.add('age', arg)
            elif cmd in ('--default-site-status',):
                self.pars.add('dsstatus', arg)
            elif cmd in ('--timeout',):
                try:
                    socket.setdefaulttimeout(int(arg))
                except:
                    print "Cannot set timeout"
            elif cmd in ('--help',):
                self.help()
                sys.exit()
        if (not self.pars.index('sitename')):      self.pars.add('sitename', '-')
        if (not self.pars.index('atlassitename')): self.pars.add('atlassitename', self.pars.get('sitename'))
        if (not self.pars.index('osname')):        self.pars.add('osname', '-')
        if (not self.pars.index('osver')):         self.pars.add('osver', '-')
        if (not self.pars.index('osrel')):         self.pars.add('osrel', '-')
        if (not self.pars.index('cename') and self.pars.index('cs')):
            self.pars.add('cename', self.pars.get('cs').split(':')[0])
        if (not self.pars.index('comments')):      self.pars.add('comments', '-')
        if (not self.pars.index('bdii')):          self.pars.add('bdii', 'lcg-bdii.cern.ch')

        if (self.mode == 'insert' and
            (not self.pars.index('cs') or not self.pars.index('rel'))):
            print "Missing --cs or --rel argument for insert. Exiting..."
            self.help();
            sys.exit(-1);

        if (self.mode == 'update' and
            (not self.pars.index('reqid') or not self.pars.index('status'))):
            print "Missing --reqid or --status argument for update. Exiting..."
            self.help();
            sys.exit(-1);

        if (self.mode == 'insert'):
            self.sendData()
        elif (self.mode == 'query'):
            self.queryData()
        elif (self.mode == 'update'):
            self.updateData()
        else:
            print "Unknown mode %s" % mode
            sys.exit(-1)


    def sendData(self):
        # Prepare the data to send
        cfile=open(self.certfile)
        cdata=cfile.read()
        x509cert=crypto.load_certificate(crypto.FILETYPE_PEM,cdata)
        cfile.close()
        commonName=x509cert.get_subject().commonName
        emailAddress=x509cert.get_subject().emailAddress
        if (emailAddress == None): emailAddress='noreply@localhost'
        if (not self.pars.index('reqtype')): self.pars.add('reqtype', 'installation')

        data = (
                ('submit','yes')
               ,('atlassitename',self.pars.get('atlassitename'))
               ,('sitename',self.pars.get('sitename'))
               ,('osname',self.pars.get('osname'))
               ,('osver',self.pars.get('osver'))
               ,('osrel',self.pars.get('osrel'))
               ,('cs',self.pars.get('cs'))
               ,('cename',self.pars.get('cename'))
               ,('user',commonName)
               ,('email',emailAddress)
               ,('rel',self.pars.get('rel'))
               ,('bdii',self.pars.get('bdii'))
               ,('reqtype',self.pars.get('reqtype'))
               ,('comments',self.pars.get('comments'))
               ,('multi',self.multi)
               ,('quiet','1')
               )
        if (self.nodeps == "y"):
            data+=(('nodeps','yes'),)
        if self.pars.index('status'):
            data+=(('status',self.pars.get('status')),)
        if self.pars.index('since'):
            data+=(('since',self.pars.get('since')),)
        if self.pars.index('age'):
            data+=(('age',self.pars.get('age')),)
        if self.gridname:
            data+=(('gridname',self.gridname),)
        if self.facility:
            data+=(('facility',self.facility),)
        if self.pars.index('sitetype'):
            data+=(('sitetype',self.pars.get('sitetype')),)
        if self.pars.index('dsstatus'):
            data+=(('dsstatus',self.pars.get('dsstatus')),)
        if (self.debug):
            print "LJSFREQ> host:     %s" % self.host
            print "LJSFREQ> selector: %s" % self.sel
            print "LJSFREQ> data:"
            print data
        # Send the data
        try:
            reply = self.post_multipart(self.host, self.sel, data)
            if (len(reply) > 2): print reply
        except:
            print "Cannot send LJSF request";
            raise
            sys.exit(-1)


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
        if (self.pars.index('cename')):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%scename=%s" % (url, sep, self.pars.get('cename')))
            numArgs=numArgs+1
        if (self.pars.index('cs')):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%scs=%s" % (url, sep, self.pars.get('cs')))
            numArgs=numArgs+1
        if (self.pars.index('reqtype')):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%sreqtype=%s" % (url, sep, self.pars.get('reqtype')))
            numArgs=numArgs+1
        if (self.pars.index('since')):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%ssince=%s" % (url, sep, self.pars.get('since')))
            numArgs=numArgs+1
        if (self.pars.index('age')):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%sage=%s" % (url, sep, self.pars.get('age')))
            numArgs=numArgs+1
        if (self.pars.index('sitetype')):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%ssitetype=%s" % (url, sep, self.pars.get('sitetype')))
            numArgs=numArgs+1
        if (self.maxrecords):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%smaxrecords=%d" % (url, sep, self.maxrecords))
            numArgs=numArgs+1
        if (self.offset):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%soffset=%d" % (url, sep, self.offset))
            numArgs=numArgs+1
        if (self.facility):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%sfacility=%s" % (url, sep, self.facility))
            numArgs=numArgs+1
        if (self.gridname):
            if (numArgs==0): sep = "?"
            else:            sep = "&"
            url = ("%s%sgridname=%s" % (url, sep, self.gridname))
            numArgs=numArgs+1
        h.request('GET', url)
        response = h.getresponse().read()
        if (len(response)>2): print response[:-1]

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
                        print "LJSFREQ> Cannot open %s for output" % self.instconf
                confin.close()
            else:
                if (self.debug):
                    print "LJSFREQ> Cannot open %s for input" % self.conftmpl
        if (self.wmsvoconf != ''):
            self.writeConfig(self.wmsvoconftmpl,self.wmsvoconf,__WMSCONFMAP__)
        if (self.wmscmdconf != ''):
            self.writeConfig(self.wmscmdconftmpl,self.wmscmdconf,__WMSCONFMAP__)


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
                    print "LJSFREQ> Cannot open %s for output" % conf
            confin.close()
        else:
            if (self.debug):
                print "LJSFREQ> Cannot open %s for input" % tmpl


    def updateData(self):
        # Prepare the data to send
        data = (
                ('submit','yes')
               ,('id',self.pars.get('reqid'))
               ,('reqstat',self.pars.get('status'))
               ,('ws','yes')
               ,('admincomm',self.pars.get('comments'))
               )
        if (self.pars.index('reqtype')):
            data += (('reqtype', self.pars.get('reqtype')),)
        if (self.debug):
            print "LJSFREQ> host:     %s" % self.host
            print "LJSFREQ> selector: %s" % self.sel
            print "LJSFREQ> data:"
            print data
        # Send the data
        try:
            reply = self.post_multipart(self.host, self.sel, data)
            print reply
        except:
            print "Cannot send LJSF request";
            raise


    def post_multipart(self, host, selector, fields):
        """
        Post fields to an https host as multipart/form-data.
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files.
        Return the server's response page.
        """
        content_type, body = self.encode_multipart_formdata(fields)
        h = httplib.HTTPSConnection(host, 443, self.keyfile, self.certfile)
        h.putrequest('POST', selector)
        h.putheader('content-type', content_type)
        h.putheader('content-length', str(len(body)))
        h.endheaders()
        h.send(body)
        response = h.getresponse()
        return response.read()

    def encode_multipart_formdata(self, fields):
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
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body

    def get_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    def help(self):
        print HELP % (__version__.strip(),self.gridname,self.conftmpl,self.wmsvoconftmpl,self.wmscmdconftmpl,self.keyfile,self.certfile,self.host,self.sel)


# main class
if __name__ == '__main__':
    ljsfpost=LJSFpost()
    ljsfpost.main()
