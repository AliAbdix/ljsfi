#!/usr/bin/env python
#################################################################
# LJSF Bookkeeping interface to mysql
# Author: Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>
# Version: 2.0
# 29-03-2013

import MySQLdb
import string, os, getopt, sys
import re, socket
from ljsfutils import *
try:
    import hashlib
except:
    import md5 as hashlib
try:
    import memcache
except:
    memcache = None

__version__ = "$Revision: 2.0 $"[11:-1]

HELP="""LJSF Bookkeeping mysql interface %s.
Usage: ljsfbkk.py <--select|--insert> <--jobid id> [OPTION]...
                                                                                
Options:
  --help                        display this help and exit.
  --cache                       use cache engine
  --cache-timeout=<seconds>     cache timeout, in seconds
  --conf=<conf file>            database configuration file
  --dbhost=<db host>            database host name
  --dbname=<db name>            database name
  --dbuser=<username>           database username
  --dbpass=<password>           database password
  --debug                       enable debug output
  --admin-id=<ID>               user ID of the admin user
                                or the user who triggered the job
  --arch=<arch name>            installation architecture
  --cs=<contact string>         contact string for the CE
  --dest=<name>                 destination CE
  --exit=<exit code>            return code
  --facility=<facility name>    facility name (e.g. WMS, Panda)
  --grid=<grid name>            grid name
  --insert                      insert into the database
  --jdlname=<name>              JDL name
  --jdltype=<type>              type of job/jdl
  --jdlfile=<jdl file name>     full path to the jdl file
  --jobid=<id>                  jobID
  --joblock=<0|1>               show jobs locked (1) or free (0)
  --jobname=<name>              job name
  --jobcomments=<text>          comments for this job
  --jobinfo=<file name>         get the job info from <file name>
  --last=<n>                    show only the last <n> records
  --not                         negate select
  --osname=<OS name>            Operating System Name
  --osrelease=<OS release>      Operating System release
  --osversion=<OS version>      Operating System version
  --quiet                       run in quiet mode (suppress normal output)
  --reachtime=<time>            submission time
  --rel=<release_name>          release name
  --rettime=<time>              retrieval time
  --request=<id>                request id
  --select=<field-names|all>    query the database for records
  --set-output=<output files>   Set the output files (comma separated list
                                of [<file-type>:]<file-name> values)
  --atlas-sitename=<name>       ATLAS Site Name
  --sitename=<name>             Site Name
  --statreason=<details>        status reason
  --status=<status>             status
  --subtime=<time>              submission time
  --unset-output=<output files> Unset the output files (comma separated list
                                of <file-name> values)
  --user=<username>             operator username
  --validation=<status>         validation status

Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>.
"""

utils=ljsfUtils()

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


class ljsfBKK:
  # Defaults
  conf   = None
  db     = None
  dbhost = None
  dbname = None
  dbuser = None
  dbpass = None
  debug  = False

  fields = Fields()
  username = None
  userdn = None
  userid = None
  role = None
  antiselect = 0
  selectionFields = {}
  selectionFields['all'] = 'job.id,user.name,jdl.name,job.name,job.submission_time,job.reach_time,job.retrieval_time,job.status,job.status_reason,job.exit_code'
  selectionFields['min']   = 'job.id,jdl.name,description'
  selectionFields['run']   = 'jdl.name,site.cename,job.status,description'
  selectionFields['info']  = 'jdl.name,job.status,job.status_reason,description,user.name,job.retrieval_time'
  selectionFields['output']  = 'job.id,job.name,job.logfile,job_output.name'
  selectionFields['count'] = 'count(*)'
  selectionKey = 'all'
  outputMode="normal"
  outputFiles=[]
  manageOutputFiles=None
  facility=None
  last=None
  orderby=True
  ljsfDBURL = None
  memcacheServer = None
  memcacheClient = None
  cache = False
  cacheTimeout = 300
  

  # Minimum and maximum proxy lifetime (seconds)
  minproxylt = 14400
  maxproxylt = 86400
  if (os.environ.has_key('LJSF_MINPROXY_LT')):
    minproxylt = int(os.environ['LJSF_MINPROXY_LT'])
  if (os.environ.has_key('LJSF_MAXPROXY_LT')):
    maxproxylt = int(os.environ['LJSF_MAXPROXY_LT'])

  def __init__(self):
    patt="http[s]*://([^/:]*)"
    if (os.environ.has_key("LJSFDBURL")): self.ljsfDBURL = os.environ["LJSFDBURL"]
    else: self.ljsfDBURL = "atlas-install.roma1.infn.it"
    m=re.search(patt,self.ljsfDBURL)
    if (m):
      self.memcacheServer = "%s:11211" % m.group(1)
      if (memcache):
        try:
          self.memcacheClient = memcache.Client([self.memcacheServer], debug=0)
        except:
          self.memcacheClient = None

  def reset(self):
    self.fields.reset()

  def setAdminID(self,adminid):
    self.fields.add('job.adminfk', ("%s" % adminid))

  def setArch(self, arch):
    self.fields.add('site.arch', ("'%s'" % arch))

  def setCache(self, mode):
    self.cache = mode

  def setCacheTimeout(self, timeout):
    self.cacheTimeout = int(timeout)

  def setCS(self, cs):
    self.fields.add('site.cs', ("'%s'" % cs))

  def setDebug(self, mode):
    self.debug = mode

  def setDestination(self, dest):
    self.fields.add('site.cename', ("'%s'" % dest))

  def setExitCode(self, exitCode):
    self.fields.add('job.exit_code', exitCode)

  def setFacility(self,facility):
    self.facility = facility

  def setGridName(self,gridname):
    if (gridname.upper() != 'ALL'):
      self.fields.add('grid.name', ("'%s'" % gridname))

  def setJdlFile(self,jdlfile):
    try:
      self.fields.add('jdl.content', ("'%s'" % open(jdlfile,"r").read()))
    except:
      print "File %s not found. Skipping." % jdlfile

  def setJdlName(self, jdlname):
    self.fields.add('jdl.name', ("'%s'" % jdlname))

  def setJdlType(self,jdltype):
    self.fields.add('jdl.type', ("'%s'" % jdltype))

  def setJobComments(self,comments):
    self.fields.add('job.comments', ("'%s'" % comments))

  def setJobID(self,jobid):
    self.fields.add('job.id', ("'%s'" % jobid))

  def setJobInfo(self,jinfo):
    try:
      jif=open(jinfo,"r")
      jobinfo=jif.read().replace("'","''")
      jif.close()
      self.fields.add('job.info', ("'%s'" % jobinfo))
    except:
      pass

  def setJobLock(self,joblock):
    self.fields.add('jdl.joblock', ("%d" % int(joblock)))

  def setJobName(self,jobname):
    self.fields.add('job.name', ("'%s'" % jobname))

  def setOSName(self,osname):
    self.fields.add('site.osname', ("'%s'" % osname))

  def setOSRelease(self,osrel):
    self.fields.add('site.osrelease', ("'%s'" % osrel))

  def setOSVersion(self,osver):
    self.fields.add('site.osversion', ("'%s'" % osver))

  def setOutput(self,output):
    self.outputFiles = output.split(",")
    self.manageOutputFiles = "add"

  def setReachTime(self, reachtime):
    self.fields.add('job.reach_time', ("'%s'" % reachtime))

  def setRelease(self, rel):
    self.fields.add('release_stat.name', ("'%s'" % rel))

  def setRequest(self, req):
    self.fields.add('job.requestfk', ("'%s'" % req))

  def setRetrievalTime(self, rettime):
    self.fields.add('job.retrieval_time', ("'%s'" % rettime))

  def setSiteName(self, sitename):
    self.fields.add('site.name', ("'%s'" % sitename))

  def setAtlasSiteName(self, sitename):
    self.fields.add('site.atlas_name', ("'%s'" % sitename))

  def setStatus(self, status):
    self.fields.add('job.status', ("'%s'" % status))

  def setStatusReason(self, statusReason):
    self.fields.add('job.status_reason', ("'%s'" % statusReason))

  def setSubmissionTime(self, subtime):
    self.fields.add('job.submission_time', ("'%s'" % subtime))

  def setUser(self, user):
    self.fields.add('user.name', ("'%s'" % user))

  def setValidation(self, val):
    self.fields.add('validation.description', ("'%s'" % val.lower()))

  def unsetOutput(self,output):
    self.outputFiles = output.split(",")
    self.manageOutputFiles = "remove"

  def openDB(self):
    # Open the database
    if (self.dbhost and self.dbname and self.dbuser and self.dbpass):
      self.db = MySQLdb.connect(host=self.dbhost,user=self.dbuser,passwd=self.dbpass,db=self.dbname)
    else:
      if (self.conf):
        db_conf = ("%s" % self.conf)
      else:
        db_conf = ("%s/.my.cnf" % os.environ["CONFPATH"])
      if (os.environ.has_key('LJSFDBNAME')):
        db_name = os.environ["LJSFDBNAME"]
      else:
        db_name = "atlas_install"
      self.db = MySQLdb.connect(read_default_file=db_conf,db=db_name)

    # Check the user name
    if (self.fields.index('user.name')):
      self.username = self.fields.get('user.name')
    else:
      self.username=("'%s@%s'" % (os.environ["USER"],socket.getfqdn()))
    self.userdn=utils.checkProxy(self.minproxylt,self.maxproxylt)
    res=self.queryDB("SELECT user.ref,role.description,valid_end>now(),enabled FROM user,role WHERE name=%s AND dn='%s' AND user.rolefk=role.ref" % (self.username,self.userdn))
    if (len(res) == 0):
      print "User %s, %s unknown. Please register to LJSFi." % (self.username,self.userdn)
      return
    else:
      if (res[0][1] != "admin" and res[0][1] != "master"):
        print "Your user %s does not have sufficient privileges to access the database." % self.username
        return
      elif (res[0][2] == 0):
        print "Your user %s has expired." % self.username
        return
      elif (res[0][3] == 0):
        print "Your user %s has been disabled." % self.username
        return
      else:
        self.userid = res[0][0]
        self.role   = res[0][1]

  def writeDB(self):
    self.fields.remove('user.name')
    self.fields.add('job.userfk',self.userid)

    # Check if the requested record is already there
    query = ("SELECT ref FROM job WHERE id=%s" % (self.fields.get('job.id')))
    if (self.debug): print query
    res=self.queryDB(query)
    ref = None
    if (len(res) != 0):
      jobquery = 'UPDATE job SET'
      ref = res[0]
    else:
      jobquery = 'INSERT INTO job SET'
      # Check the jdl name for insert
      if (not self.fields.index('jdl.name')):
        sys.stderr.write("No JDL name specified for insert. Cannot continue\n")
        return 10

    # Check the user name
    if (self.fields.index('user.name')):
      username = self.fields.get('user.name')
      userdn=""
    else:
      username=("'%s@%s'" % (os.environ["USER"],socket.getfqdn()))
      userdn=utils.checkProxy(self.minproxylt,self.maxproxylt)
    res=self.queryDB(("SELECT ref FROM user WHERE name=%s" % username))
    if (len(res) == 0):
      self.queryDB(("INSERT INTO user SET name=%s, dn='%s'" % (username,userdn)), True)
      res=self.queryDB(("SELECT ref FROM user WHERE name=%s" % username))
    self.fields.remove('user.name')
    self.fields.add('job.userfk',res[0][0])

    # Check the validation status
    if (self.fields.index('validation.description')):
      validation = self.fields.get('validation.description')
      res=self.queryDB(("SELECT ref FROM validation WHERE description=%s" % validation))
      if (len(res) == 0):
        res = self.queryDB("SELECT description FROM validation")
        print "Unknown validation status"
        print "Validation status must be one of the following:"
        for val in res:
          print "%s" % val[0]
        return 20
      self.fields.remove('validation.description')
      self.fields.add('job.validationfk',res[0][0])

    # Check the jdl name
    if (self.fields.index('jdl.name')):
      jdlname = self.fields.get('jdl.name')
      res=self.queryDB(("SELECT ref FROM jdl WHERE name=%s" % jdlname))
      if (len(res) == 0):
        query = "INSERT INTO jdl SET"
        indx = 0
        for field in self.fields.getall():
          if (field[0].split(".")[0] == "jdl"):
            if (indx > 0): query += ","
            query += (" %s=%s" % (field[0], field[1]))
            indx += 1
        self.queryDB(query, True)
        res=self.queryDB(("SELECT ref FROM jdl WHERE name=%s" % jdlname))
      else:
        query = "UPDATE jdl SET"
        indx = 0
        for field in self.fields.getall():
          if (field[0].split(".")[0] == "jdl"):
            if (indx > 0): query += ","
            query += (" %s=%s" % (field[0], field[1]))
            indx += 1
        query += (" WHERE ref=%d" % res[0][0])
        self.queryDB(query, True)
      jdlref = res[0][0]
      self.fields.remove('jdl.name')
      self.fields.remove('jdl.type')
      self.fields.remove('jdl.content')
      self.fields.add('job.jdlfk',jdlref)
      res=self.queryDB(("SELECT type, relfk FROM jdl WHERE ref=%d" % jdlref))
      jdltype = res[0][0]
      resref  = res[0][1]
      self.queryDB(("UPDATE release_stat SET userfk=%d, status='%s' WHERE ref=%d" % (self.fields.get('job.userfk'),jdltype,resref)), True)

    # Check the facilities
    if (self.facility):
      res=self.queryDB("SELECT ref FROM facility WHERE name='%s'" % self.facility)
      if (not res):
        self.queryDB("INSERT INTO facility SET name='%s'" % self.facility)
        res=self.queryDB("SELECT ref FROM facility WHERE name='%s'" % self.facility)
      try: self.fields.add('job.facilityfk',"%d" % res[0][0])
      except: self.fields.add('job.facilityfk',1)

    # Check the destination
    if (not self.fields.index('site.cs')):
      res=self.queryDB(("SELECT site.cs FROM job,site WHERE job.sitefk=site.ref and job.id=%s" % self.fields.get('job.id')))
      try: self.fields.add('site.cs',("'%s'" % res[0][0]))
      except: self.fields.add('site.cs',"'unassigned'")
    cs = self.fields.get('site.cs')
    res=self.queryDB(("SELECT ref FROM site WHERE cs=%s" % cs))
    if (len(res) == 0):
      query = "INSERT INTO site SET"
      indx = 0
      for field in self.fields.getall():
        if (field[0].split(".")[0] == "site"):
          if (indx > 0): query += ","
          query += (" %s=%s" % (field[0], field[1]))
          indx += 1
      if (self.debug): print query
      self.queryDB(query, True)
      res=self.queryDB(("SELECT ref FROM site WHERE cs=%s" % cs))
    else:
      query = "UPDATE site SET"
      indx = 0
      for field in self.fields.getall():
        if (field[0].split(".")[0] == "site"):
          if (indx > 0): query += ","
          query += (" %s=%s" % (field[0], field[1]))
          indx += 1
      query += (" WHERE ref=%s" % res[0][0])
      if (self.debug): print query
      self.queryDB(query, True)
      
    self.fields.remove('site.arch')
    self.fields.remove('site.cename')
    self.fields.remove('site.cs')
    self.fields.remove('site.osname')
    self.fields.remove('site.osrelease')
    self.fields.remove('site.osversion')
    self.fields.remove('site.name')
    self.fields.add('job.sitefk',res[0][0])

    # Set the values
    fld = 0
    for field in self.fields.getall():
      if (fld > 0): jobquery += ','
      jobquery += (' %s=%s' % (field[0],field[1]))
      fld += 1
    if (ref is not None): jobquery += (" WHERE job.ref=%d" % ref)

    # Insert or update the job record in the db
    if (self.debug): print jobquery
    self.queryDB(jobquery, True)

    # Handle the output files
    if (self.outputFiles):
      res = self.queryDB("SELECT ref FROM job WHERE id=%s" % self.fields.get('job.id'))
      if (res):
        jobfk = res[0][0]
        res = self.queryDB("SELECT name FROM job_output WHERE jobfk=%d" % jobfk)
        outputList = []
        for row in res: outputList.append(row[0])
        res = self.queryDB("SELECT ref, name FROM job_output_type")
        if (res):
          jobOutputType = {}
          for jot in res: jobOutputType[jot[1]] = jot[0]
        if (self.manageOutputFiles == "add"):
          for outputFile in self.outputFiles:
            fileData = outputFile.split(":")
            if (len(fileData) > 1):
              outputFileType = fileData[0]
              outputFileName = fileData[1]
            else:
              outputFileType = "file"
              outputFileName = fileData[0]
            if (not outputFile in outputList):
              if (not jobOutputType.has_key(outputFileType)):
                self.queryDB("INSERT INTO job_output_type SET name='%s'" % outputFileType, True)
                res = self.queryDB("SELECT ref, name FROM job_output_type WHERE name='%s'" % outputFileType)
                jobOutputType[res[0][1]] = res[0][0]
              self.queryDB("INSERT INTO job_output (jobfk, typefk, name) VALUES (%d,%d,'%s')" % (jobfk, jobOutputType[outputFileType],outputFileName), True)
        else:
          for outputFile in self.outputFiles:
            if (outputFile in outputList):
              self.queryDB("DELETE FROM job_output WHERE jobfk=%d AND name='%s'" % (jobfk, outputFile), True)
    return 0


  def readDB(self, cache=None):
    if (cache == None): cache = self.cache
    ___QUERY_BODY___ = "SELECT %s"
    if (self.selectionKey == "count"):
      ___QUERY_FROM___ = " FROM job JOIN site ON job.sitefk=site.ref JOIN validation ON job.validationfk=validation.ref"
    else:
      ___QUERY_FROM___ = " FROM job LEFT JOIN jdl ON job.jdlfk=jdl.ref JOIN user ON job.userfk=user.ref JOIN site ON job.sitefk=site.ref JOIN validation ON job.validationfk=validation.ref"
    ___QUERY_COND___ = ""
    __SELECT_NO_ORDER__ = [ "count" ]
    if (self.debug): print self.fields.getall()
    if (self.fields.index("release_stat.name")): ___QUERY_FROM___ += " JOIN release_stat ON jdl.relfk=release_stat.ref"
    if (self.fields.index("grid.name")):
      ___QUERY_FROM___ += " JOIN grid ON site.gridfk=grid.ref"
    if (self.selectionKey == "output"): ___QUERY_FROM___ += " JOIN job_output ON job_output.jobfk=job.ref"
    query=(___QUERY_BODY___ % (self.selectionFields[self.selectionKey]))
    for field in self.fields.getall():
      if (___QUERY_COND___): ___QUERY_COND___ += " AND "
      if (self.antiselect == 0):
        if ("%" in field[1]):
          ___QUERY_COND___ += '%s like %s' % (field[0],field[1])
        else:
          ___QUERY_COND___ += '%s = %s' % (field[0],field[1])
      else:
        if ("%" in field[1]):
          ___QUERY_COND___ += '%s not like %s' % (field[0],field[1])
        else:
          ___QUERY_COND___ += '%s <> %s' % (field[0],field[1])
    query += ___QUERY_FROM___
    if (___QUERY_COND___): query += " WHERE " + ___QUERY_COND___
    if (self.selectionKey not in __SELECT_NO_ORDER__): query += " ORDER BY job.submission_time"
    if (self.last): query += " DESC LIMIT %d" % self.last
    if (self.debug): print query
    key = None
    res = None
    if (cache and self.memcacheClient):
      key = hashlib.md5(query).hexdigest()
      res = self.memcacheClient.get(key)
    if (not res):
      res = self.queryDB(query)
      if (res and cache and self.memcacheClient and key):
        self.memcacheClient.set(key, res, self.cacheTimeout)

    # If quiet mode then suppress normal output
    if (self.outputMode == "quiet"):
      for rec in res:
        indx = 0
        for field in rec:
          if (indx > 0): sys.stdout.write(", ")
          sys.stdout.write("%s" % field)
          indx += 1
        sys.stdout.write("\n")
      return 0

    # Calculate the field max lengths
    flen = []
    for field in self.selectionFields[self.selectionKey].split(","):
      flen.append(len(str(field)))
    for row in res:
      indx = 0
      for field in row:
        if (field):
          fldlen=len(str(field))
        else:
          fldlen=4
        try:
          if (fldlen > flen[indx]): flen[indx] = fldlen
        except:
          flen.append(fldlen)
        indx += 1
    # Print the report
    sep = "-"
    for fnum in flen:
      for i in range(fnum+3):
        sep += "-"
    print sep
    indx = 0
    sys.stdout.write("|")
    for field in self.selectionFields[self.selectionKey].split(","):
      sys.stdout.write((" %%%ds |" % flen[indx]) % field)
      indx += 1
    sys.stdout.write("\n")
    print sep
    for row in res:
      indx = 0
      sys.stdout.write("|")
      for field in row:
        __FORMAT__ = (" %%%ds |" % flen[indx])
        sys.stdout.write(__FORMAT__ % field)
        indx += 1
      sys.stdout.write("\n")
    print sep
    print "%d records selected" % len(res)
    return 0

  def queryDB(self, query, commit=False):
    if (not self.db): self.openDB()
    try:
      # Query the DB
      cursor = self.db.cursor()
      cursor.execute(query)
    except MySQLdb.OperationalError, e:
      self.openDB()
      # Query the DB
      cursor = self.db.cursor()
      cursor.execute(query)

    numrows = int(cursor.rowcount)
    if (commit): self.db.commit()
    return cursor.fetchall()
    

# main class
if __name__ == '__main__':
    short_options = ""
    long_options = ["admin-id=", "arch=", "atlas-sitename=", "cache", "cache-timeout=", "conf=", "cs=", "dest="
                   ,"help", "insert", "dbhost=", "dbname=" ,"dbuser=", "dbpass=", "debug", "exit="
                   ,"facility=", "grid-name=","jdlname=", "jdltype=", "jdlfile=", "jobid=", "jobinfo="
                   ,"joblock=","jobname=", "jobcomments=", "last=", "not"
                   ,"min-proxy-lt=", "output=", "osname=","osrelease="
                   ,"osversion=", "quiet", "reachtime=","request=","rel=","rettime="
                   ,"select=", "set-output=", "sitename=","statreason=","status=", "subtime="
                   ,"unset-output=", "user=", "validation="]
    cmd=''
    arg=''
    selectMode=0
    insertMode=0
    ljsf=ljsfBKK()
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                     short_options,
                     long_options,
                     )
    except getopt.GetoptError:
        # Print help
        print HELP % (__version__.strip(),)
        sys.exit(1)

    for cmd, arg in opts:
        if cmd in ('--help',):
            print HELP % (__version__.strip(),)
            sys.exit(0)
        elif cmd in ('--conf',):
            ljsf.conf = arg
        elif cmd in ('--dbhost',):
            ljsf.dbhost = arg
        elif cmd in ('--dbname',):
            ljsf.dbname = arg
        elif cmd in ('--dbuser',):
            ljsf.dbuser = arg
        elif cmd in ('--dbpass',):
            ljsf.dbpass = arg
        elif cmd in ('--debug',):
            ljsf.setDebug(True)
        elif cmd in ('--admin-id',):
            ljsf.setAdminID(arg)
        elif cmd in ('--arch',):
            ljsf.setArch(arg)
        elif cmd in ('--cache',):
            ljsf.setCache(True)
        elif cmd in ('--cache-timeout',):
            ljsf.setCacheTimeout(arg)
        elif cmd in ('--cs',):
            ljsf.setCS(arg)
        elif cmd in ('--dest',):
            ljsf.setDestination(arg)
        elif cmd in ('--exit',):
            ljsf.setExitCode(arg)
        elif cmd in ('--facility',):
            ljsf.setFacility(arg)
        elif cmd in ('--grid-name',):
            ljsf.setGridName(arg)
        elif cmd in ('--insert',):
            insertMode=1
        elif cmd in ('--jdlname',):
            ljsf.setJdlName(arg)
        elif cmd in ('--jdltype',):
            ljsf.setJdlType(arg)
        elif cmd in ('--jdlfile',):
            ljsf.setJdlFile(arg)
        elif cmd in ('--jobcomments',):
            ljsf.setJobComments(arg)
        elif cmd in ('--jobid',):
            ljsf.setJobID(arg)
        elif cmd in ('--jobinfo',):
            ljsf.setJobInfo(arg)
        elif cmd in ('--joblock',):
            ljsf.setJobLock(arg)
        elif cmd in ('--jobname',):
            ljsf.setJobName(arg)
        elif cmd in ('--min-proxy-lt',):
            ljsf.minproxylt=int(arg)
        elif cmd in ('--last',):
            ljsf.last=int(arg)
        elif cmd in ('--not',):
            ljsf.antiselect = 1
        elif cmd in ('--osname',):
            ljsf.setOSName(arg)
        elif cmd in ('--osrelease',):
            ljsf.setOSRelease(arg)
        elif cmd in ('--osversion',):
            ljsf.setOSVersion(arg)
        elif cmd in ('--set-output',):
            ljsf.setOutput(arg)
            insertMode = 1
        elif cmd in ('--unset-output',):
            ljsf.unsetOutput(arg)
            insertMode = 1
        elif cmd in ('--quiet',):
            ljsf.outputMode="quiet"
        elif cmd in ('--reachtime',):
            ljsf.setReachTime(arg)
        elif cmd in ('--request',):
            ljsf.setRequest(arg)
        elif cmd in ('--rettime',):
            ljsf.setRetrievalTime(arg)
        elif cmd in ('--select',):
            selectMode=1
            if (arg not in ljsf.selectionFields.keys()):
                ljsf.selectionKey='user'
                ljsf.selectionFields['user']=arg
            else:
                ljsf.selectionKey=arg
        elif cmd in ('--atlas-sitename',):
            ljsf.setAtlasSiteName(arg)
        elif cmd in ('--sitename',):
            ljsf.setSiteName(arg)
        elif cmd in ('--statreason',):
            ljsf.setStatusReason(arg)
        elif cmd in ('--status',):
            ljsf.setStatus(arg)
        elif cmd in ('--subtime',):
            ljsf.setSubmissionTime(arg)
        elif cmd in ('--user',):
            ljsf.setUser(arg)
        elif cmd in ('--validation',):
            ljsf.setValidation(arg)
        elif cmd in ('--rel',):
            ljsf.setRelease(arg)

    if (not ljsf.fields.index('site.atlas_name') and ljsf.fields.index('site.name')):
       ljsf.setAtlasSiteName(ljsf.fields.get('site.name'))
    if ((not ljsf.fields.index('job.id') and insertMode==1) or
       (insertMode==0 and selectMode==0)) :
        print HELP % (__version__.strip(),)
        sys.exit(1)

    # Check for NULLs
    for field in ljsf.fields.getall():
        if (ljsf.fields.get(field[0]) == "'NULL'"): ljsf.fields.add(field[0],"NULL")

    # Execute the task
    rc = 0
    if (selectMode==1) :
        rc = ljsf.readDB()
    elif (insertMode==1) :
        rc = ljsf.writeDB()

    sys.exit(rc)
