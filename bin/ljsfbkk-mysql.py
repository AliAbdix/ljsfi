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

__version__ = "$Revision: 2.0 $"[11:-1]

HELP="""LJSF Bookkeeping mysql interface %s.
Usage: ljsfbkk.py <--select|--insert> <--jobid id> [OPTION]...
                                                                                
Options:
  --help                        display this help and exit.
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



class ljsfBKK:
  short_options = ""
  long_options = ["admin-id=", "arch=", "conf=", "cs=", "dest=", "exit=", "help", "insert"
                 ,"dbhost=", "dbname=" ,"dbuser=", "dbpass=", "debug", "exit="
                 ,"facility=", "grid-name=","jdlname=", "jdltype=", "jdlfile=", "jobid=", "jobinfo="
                 ,"joblock=","jobname=", "jobcomments=", "last=", "not"
                 ,"min-proxy-lt=", "output=", "osname=","osrelease="
                 ,"osversion=", "quiet", "reachtime=","request=","rel=","rettime="
                 ,"select=", "set-output=", "sitename=","statreason=","status=", "subtime="
                 ,"unset-output=", "user=", "validation="]

  # Defaults
  conf   = None
  db     = None
  dbhost = None
  dbname = None
  dbuser = None
  dbpass = None
  debug  = False

  fields = Fields()
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

  # Minimum and maximum proxy lifetime (seconds)
  minproxylt = 14400
  maxproxylt = 86400
  if (os.environ.has_key('LJSF_MINPROXY_LT')):
    minproxylt = int(os.environ['LJSF_MINPROXY_LT'])
  if (os.environ.has_key('LJSF_MAXPROXY_LT')):
    maxproxylt = int(os.environ['LJSF_MAXPROXY_LT'])

  def main(self):
    try:
      opts, args = getopt.getopt(sys.argv[1:],
                   self.short_options,
                   self.long_options,
                   )
    except getopt.GetoptError:
      # Print help
      self.help()
      sys.exit(-1)

    # Local vars
    cmd=''
    arg=''
    selectMode=0
    insertMode=0
    username=None
    userdn=None
    userid=None
    role=None


    for cmd, arg in opts:
      if cmd in ('--help',):
        self.help()
        sys.exit()
      elif cmd in ('--conf',):
        self.conf = arg
      elif cmd in ('--dbhost',):
        self.dbhost = arg
      elif cmd in ('--dbname',):
        self.dbname = arg
      elif cmd in ('--dbuser',):
        self.dbuser = arg
      elif cmd in ('--dbpass',):
        self.dbpass = arg
      elif cmd in ('--debug',):
        self.debug = True
      elif cmd in ('--admin-id',):
        self.fields.add('job.adminfk', ("%s" % arg))
      elif cmd in ('--arch',):
        self.fields.add('site.arch', ("'%s'" % arg))
      elif cmd in ('--cs',):
        self.fields.add('site.cs', ("'%s'" % arg))
      elif cmd in ('--dest',):
        self.fields.add('site.cename', ("'%s'" % arg))
      elif cmd in ('--exit',):
        self.fields.add('job.exit_code', arg)
      elif cmd in ('--facility',):
        self.facility = arg
      elif cmd in ('--grid-name',):
        if (arg.upper() != 'ALL'):
          self.fields.add('grid.name', ("'%s'" % arg))
      elif cmd in ('--insert',):
        insertMode=1
      elif cmd in ('--jdlname',):
        self.fields.add('jdl.name', ("'%s'" % arg))
      elif cmd in ('--jdltype',):
        self.fields.add('jdl.type', ("'%s'" % arg))
      elif cmd in ('--jdlfile',):
        try:
          self.fields.add('jdl.content', ("'%s'" % open(arg,"r").read()))
        except:
          print "File %s not found. Skipping." % arg
      elif cmd in ('--jobcomments',):
        self.fields.add('job.comments', ("'%s'" % arg))
      elif cmd in ('--jobid',):
        self.fields.add('job.id', ("'%s'" % arg))
      elif cmd in ('--jobinfo',):
        try:
          jif=open(arg,"r")
          jobinfo=jif.read().replace("'","''")
          jif.close()
          self.fields.add('job.info', ("'%s'" % jobinfo))
        except:
          pass
      elif cmd in ('--joblock',):
        self.fields.add('jdl.joblock', ("%d" % int(arg)))
      elif cmd in ('--jobname',):
        self.fields.add('job.name', ("'%s'" % arg))
      elif cmd in ('--min-proxy-lt',):
        self.minproxylt=int(arg)
      elif cmd in ('--last',):
        self.last=int(arg)
      elif cmd in ('--not',):
        self.antiselect = 1
      elif cmd in ('--osname',):
        self.fields.add('site.osname', ("'%s'" % arg))
      elif cmd in ('--osrelease',):
        self.fields.add('site.osrelease', ("'%s'" % arg))
      elif cmd in ('--osversion',):
        self.fields.add('site.osversion', ("'%s'" % arg))
      elif cmd in ('--set-output',):
        self.outputFiles = arg.split(",")
        self.manageOutputFiles = "add"
        insertMode = 1
      elif cmd in ('--unset-output',):
        self.outputFiles = arg.split(",")
        self.manageOutputFiles = "remove"
        insertMode = 1
      elif cmd in ('--quiet',):
        self.outputMode="quiet"
      elif cmd in ('--reachtime',):
        self.fields.add('job.reach_time', ("'%s'" % arg))
      elif cmd in ('--request',):
        self.fields.add('job.requestfk', ("'%s'" % arg))
      elif cmd in ('--rettime',):
        self.fields.add('job.retrieval_time', ("'%s'" % arg))
      elif cmd in ('--select',):
        selectMode=1
        if (arg not in self.selectionFields.keys()):
          self.selectionKey='user'
          self.selectionFields['user']=arg
        else:
          self.selectionKey=arg
      elif cmd in ('--sitename',):
        self.fields.add('site.name', ("'%s'" % arg))
      elif cmd in ('--statreason',):
        self.fields.add('job.status_reason', ("'%s'" % arg))
      elif cmd in ('--status',):
        self.fields.add('job.status', ("'%s'" % arg))
      elif cmd in ('--subtime',):
        self.fields.add('job.submission_time', ("'%s'" % arg))
      elif cmd in ('--user',):
        self.fields.add('user.name', ("'%s'" % arg))
      elif cmd in ('--validation',):
        self.fields.add('validation.description', ("'%s'" % arg.lower()))
      elif cmd in ('--rel',):
        self.fields.add('release_stat.name', ("'%s'" % arg))

    if ((not self.fields.index('job.id') and insertMode==1) or
       (insertMode==0 and selectMode==0)) :
      self.help()
      sys.exit(-1)

    # Check for NULLs
    for field in self.fields.getall():
      if (self.fields.get(field[0]) == "'NULL'"): self.fields.add(field[0],"NULL")

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

    # Execute the task
    if (selectMode==1) :
      self.readDB()
    elif (insertMode==1) :
      self.writeDB()

    # Close the database

  def help(self):
    print HELP % (__version__.strip(),)


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
        sys.exit(-1)

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
        sys.exit(20)
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


  def readDB(self):
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
    res = self.queryDB(query)

    # If quiet mode then suppress normal output
    if (self.outputMode == "quiet"):
      for rec in res:
        indx = 0
        for field in rec:
          if (indx > 0): sys.stdout.write(", ")
          sys.stdout.write("%s" % field)
          indx += 1
        sys.stdout.write("\n")
      return

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

  def queryDB(self, query, commit=False):
    # Query the DB
    cursor = self.db.cursor()
    cursor.execute(query)
    numrows = int(cursor.rowcount)
    if (commit): self.db.commit()
    return cursor.fetchall()
    

# main class
if __name__ == '__main__':
    ljsf=ljsfBKK()
    ljsf.main()
