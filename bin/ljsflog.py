#!/usr/bin/env python
import httplib, mimetypes
import os, sys, time, socket
import getopt
import commands
import socket
import re
from xml.dom import minidom
from OpenSSL import crypto

try:
    socket.setdefaulttimeout(30.0)
except:
    pass

__version__ = "$Revision: 5 $"[11:-1]

HELP="""LJSF logfile interface %s.
Usage: ljsflog.py --jobid=<job ID> --logfile=<logfile name>

Options:
  --jobid=<job ID>            use <job ID> to attach the logfile.
  --logfile=<logfile name>    full path to the logfile to upload.
  --fragment=<num>            logfile fragment number <num>.
  --help                      display this help and exit.
  --key <private key file>    use the provided private key
                              (current: %s)
  --cert <certificate file>   use the provided certificate
                              (current: %s)
  --host=<hostname>           hostname of the LJSF server
                              (current: %s)
  --logreq                    list the jobs with log requests
  --sel=<selector>            use <selector> as target page
                              (current: %s)
  --debug                     debug mode (verbose).

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


class LJSFlog:

    # Options
    short_options = ""
    long_options  = ["jobid=", "logfile=", "help"
                    ,"host=", "sel=", "key=", "cert="
                    ,"fragment=", "logreq", "debug"]

    # Defaults
    debug    = False
    mode     = 'upload'
    pars     = Fields()
    if (os.environ.has_key('LJSFDBURL')):
        p = re.compile("(\S+)://([^/]*)(.*)")
        dbinfo = p.search(os.environ['LJSFDBURL']).groups()
        host  = dbinfo[1]
        DBURL = dbinfo[2]
    else:
        host = "atlas-install.roma1.infn.it"
        DBURL = "/atlas_install/protected"
    sel      = "%s/log.php" % DBURL

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
            elif cmd in ('--jobid',):
                self.pars.add('jobid', arg)
            elif cmd in ('--logfile',):
                self.pars.add('logfile', arg)
            elif cmd in ('--fragment',):
                self.pars.add('fragment', arg)
            elif cmd in ('--host',):
                self.host = arg
            elif cmd in ('--sel',):
                self.sel = arg
            elif cmd in ('--key',):
                self.keyfile = arg
            elif cmd in ('--cert',):
                self.certfile = arg
            elif cmd in ('--logreq',):
                self.mode = 'logreq'
            elif cmd in ('--help',):
                self.help()
                sys.exit()

        if (self.mode == "upload" and (not self.pars.index('jobid') or not self.pars.index('logfile'))):
            print "Missing --jobid or --logfile arguments. Exiting..."
            self.help();
            sys.exit(-1);

        # Send out the data
        res = self.sendData(mode=self.mode)
        if (res):
            for val in res: print val


    def set(self,name,val):
        self.pars.add(name, val)


    def unset(self,name):
        self.pars.remove(name)


    def sendData(self,mode='upload'):
        # Prepare the data to send
        cfile=open(self.certfile)
        cdata=cfile.read()
        x509cert=crypto.load_certificate(crypto.FILETYPE_PEM,cdata)
        cfile.close()
        commonName=x509cert.get_subject().commonName
        emailAddress=x509cert.get_subject().emailAddress
        if (emailAddress == None): emailAddress='noreply@localhost'

        data  = (('mode',mode),)
        if (self.pars.index('jobid')):    data += (('jobid',self.pars.get('jobid')),)
        if (self.pars.index('fragment')): data += (('fragment',self.pars.get('fragment')),)
        files = ()
        if (mode == 'upload'):
            try:
                logfile = open(self.pars.get('logfile'))
                logdata = logfile.read()
                logfile.close()
                files = (('file',os.path.basename(self.pars.get('logfile')),logdata),)
            except:
                pass

        if (self.debug):
            print "LJSFLOG> host:     %s" % self.host
            print "LJSFLOG> selector: %s" % self.sel
            print "LJSFLOG> data:"
            print data
            if (files):
                print "LJSFLOG> files:"
                print files
        # Send the data
        try:
            reply = self.post_multipart(self.host, self.sel, data, files)
            if (len(reply) > 2): return reply.split("\n")
        except:
            print "LJSFLOG> cannot send LJSF %s logfile request" % self.mode
            raise
        return []


    def post_multipart(self, host, selector, fields, files):
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

    def encode_multipart_formdata(self, fields, files):
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
            L.append(("%s" % value))
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
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

    def help(self):
        print HELP % (__version__.strip(),self.keyfile,self.certfile,self.host,self.sel)


# main class
if __name__ == '__main__':
    ljsflog=LJSFlog()
    ljsflog.main()
