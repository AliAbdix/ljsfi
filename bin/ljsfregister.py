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
    socket.setdefaulttimeout(3)
except:
    pass

__version__ = "$Revision: 0.1 $"[11:-1]

HELP="""LJSF registration interface %s.
Usage: ljsfregister.py [OPTIONS]

Options:
  --help                      display this help and exit.
  --key <private key file>    use the provided private key
                              (current: %s)
  --cert <certificate file>   use the provided certificate
                              (current: %s)
  --host=<hostname>           hostname of the LJSF server
                              (current: %s)
  --sel=<selector>            use <selector> as target page
                              (current: %s)
  --local                     register local operator user
  --user=<username>           register as <username>
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


class LJSFregister:

    # Options
    short_options = ""
    long_options  = ["help", "host=", "sel=", "key=", "cert="
                    ,"debug","user=", "local"]

    # Defaults
    debug    = False
    pars     = Fields()
    if (os.environ.has_key('LJSFDBURL')):
        p = re.compile("(\S+)://([^/]*)(.*)")
        dbinfo = p.search(os.environ['LJSFDBURL']).groups()
        host  = dbinfo[1]
        DBURL = dbinfo[2]
    else:
        host = "atlas-install.roma1.infn.it"
    sel      = "%s/user.php" % DBURL
    keyfile  = "%s/.globus/userkey.pem" % os.environ["HOME"]
    certfile = "%s/.globus/usercert.pem" % os.environ["HOME"]
    user     = None

    
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
            elif cmd in ('--host',):
                self.host = arg
            elif cmd in ('--sel',):
                self.sel = arg
            elif cmd in ('--key',):
                self.keyfile = arg
            elif cmd in ('--cert',):
                self.certfile = arg
            elif cmd in ('--user',):
                self.user = arg
            elif cmd in ('--local',):
                 self.user=("%s@%s" % (os.environ["USER"],socket.getfqdn()))
            elif cmd in ('--help',):
                self.help()
                sys.exit()

        # Send out the data
        self.sendData()

    def sendData(self):
        # Prepare the data to send
        emailAddress = None
        (s,o) = commands.getstatusoutput("openssl x509 -in %s -noout -email" % self.certfile)
        if (s == 0): emailAddress = o.split("\n")[0]
        if (not emailAddress or emailAddress == ''): emailAddress=raw_input('email address: ')

        data  = (
                 ('quiet','yes'),
                 ('submit','yes'),
                 ('role','master'),
                 ('email',emailAddress),
                 ('view','1'),
                 ('insert','1'),
                 ('update','1'),
                 ('pin','1')
                )
        if (self.user): data += (('user',self.user),)

        if (self.debug):
            print "LJSFREGISTER> host:     %s" % self.host
            print "LJSFREGISTER> selector: %s" % self.sel
            print "LJSFREGISTER> data:"
            print data
        # Send the data
        try:
            reply = self.post_multipart(self.host, self.sel, data)
            if (len(reply) > 2): print reply
        except:
            print "Cannot send LJSFi registration";
            raise
            sys.exit(-1)


    def post_multipart(self, host, selector, fields, files=None):
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
        if (files):
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
    ljsflog=LJSFregister()
    ljsflog.main()
