#!/usr/bin/python2.2
#################################################################
# LJSF Bookkeeping interface
# Author: Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>
# Version: 0.2
# 15-09-2004

import bsddb
import string, os, getopt, sys
import re

__version__ = "$Revision: 1 $"[11:-1]

HELP="""LJSF Bookkeeping interface %s.
Usage: ljsfbkk-db.py <--select|--insert> <--jobid id> [OPTION]...
                                                                                
Options:
  --help                      display this help and exit.
  --dest=<name>               destination CE
  --exit=<exit code>          return code
  --insert                    insert into the database
  --jdlname=<name>            JDL name
  --jobid=<id>                jobID
  --jobname=<name>            job name
  --not                       negate select
  --output=<output files>     output files (comma separated list)
  --reachtime=<time>          submission time
  --rettime=<time>            retrieval time
  --select=<field-names|all>  query the database for records
  --statreason=<details>      status reason
  --status=<status>           status
  --subtime=<time>            submission time
  --user=<username>           operator username
  --validation=<status>       validation status

Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>.
"""


class Tables:
  _tables = []

  def open(self, table, filename):
    if not self.index(table): self._tables.append(table)
    tbl=bsddb.btopen(filename,'c')
    setattr(self, table, tbl)

  def index(self, table):
    return table in self._tables

class Fields:
  _fields = []

  def add(self, field, value):
    if not self.index(field): self._fields.append(field)
    setattr(self, field, value)

  def index(self, field):
    return field in self._fields



class ljsfBKK:
  short_options = ""
  long_options = ["dest=", "exit=", "help", "insert", "jdlname=", "jobid="
                 ,"jobname=", "not", "output=", "reachtime=", "rettime="
                 , "select=", "statreason=","status=", "subtime="
                 , "user=" , "validation="]

  dbdir   = os.curdir+'/bookkeeping'

  dbfiles = { 'DEST'       : dbdir+'/destination'
            , 'EXIT'       : dbdir+'/exit_code'
            , 'JDLNAME'    : dbdir+'/jdlname'
            , 'JOBID'      : dbdir+'/jobid'
            , 'JOBNAME'    : dbdir+'/jobname'
            , 'OUTPUT'     : dbdir+'/output'
            , 'REACHTIME'  : dbdir+'/reach_time'
            , 'REASON'     : dbdir+'/status_reason'
            , 'RETTIME'    : dbdir+'/retrieval_time'
            , 'STATUS'     : dbdir+'/status'
            , 'SUBTIME'    : dbdir+'/submission_time'
            , 'USERS'      : dbdir+'/users'
            , 'VALIDATION' : dbdir+'/validation_status' }

  fields = Fields()
  tables = Tables()
  selections=0
  selectionFields=''
  antiselect=0

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

    for cmd, arg in opts:
      if cmd in ('--help',):
        self.help()
        sys.exit()
      elif cmd in ('--dest',):
        self.fields.add('dest', arg)
        self.selections += 1
      elif cmd in ('--exit',):
        self.fields.add('exit', arg)
        self.selections += 1
      elif cmd in ('--insert',):
        insertMode=1
      elif cmd in ('--jdlname',):
        self.fields.add('jdlname', arg)
        self.selections += 1
      elif cmd in ('--jobid',):
        self.fields.add('jobid', arg)
        self.selections += 1
      elif cmd in ('--jobname',):
        self.fields.add('jobname', arg)
        self.selections += 1
      elif cmd in ('--not',):
        self.antiselect = 1
      elif cmd in ('--output',):
        self.fields.add('output', arg)
        self.selections += 1
      elif cmd in ('--reachtime',):
        self.fields.add('reachtime', arg)
        self.selections += 1
      elif cmd in ('--rettime',):
        self.fields.add('rettime', arg)
        self.selections += 1
      elif cmd in ('--select',):
        selectMode=1
        self.selectionFields=arg
      elif cmd in ('--statreason',):
        self.fields.add('statreason', arg)
        self.selections += 1
      elif cmd in ('--status',):
        self.fields.add('status', arg)
        self.selections += 1
      elif cmd in ('--subtime',):
        self.fields.add('subtime', arg)
        self.selections += 1
      elif cmd in ('--user',):
        self.fields.add('user', arg)
        self.selections += 1
      elif cmd in ('--validation',):
        self.fields.add('validation', arg)
        self.selections += 1

    if ((not self.fields.index('jobid') and insertMode==1) or
       (insertMode==0 and selectMode==0)) :
      self.help()
      sys.exit(-1)

    #if self.fields.index('dest')       : print 'destination: %s' % self.fields.dest
    #if self.fields.index('exit')       : print '000exit code: %s' % self.fields.exit
    #if self.fields.index('jdlname')    : print 'jdlname: %s' % self.fields.jdlname
    #if self.fields.index('jobid')      : print 'jobid: %s' % self.fields.jobid
    #if self.fields.index('jobname')    : print 'job name: %s' % self.fields.jobname
    #if self.fields.index('output')     : print 'output files: %s' % self.fields.output
    #if self.fields.index('reachtime')  : print 'reached at: %s' % self.fields.reachtime
    #if self.fields.index('rettime')    : print 'retrieval time: %s' % self.fields.rettime
    #if self.fields.index('statreason') : print 'status reason: %s' % self.fields.statreason
    #if self.fields.index('status')     : print 'status: %s' % self.fields.status
    #if self.fields.index('subtime')    : print 'submission time: %s' % self.fields.subtime
    #if self.fields.index('user')    : print 'user: %s' % self.fields.user
    #if self.fields.index('validation') : print 'validation status: %s' % self.fields.validation

    if (selectMode==1) :
      self.readDB()
    elif (insertMode==1) :
      self.writeDB()


  def help(self):
    print HELP % (__version__.strip(),)


  def writeDB(self):
    # Create/open the databases
    if not os.path.isdir(self.dbdir) :
      try:
        os.mkdir(self.dbdir)
      except:
        print "Unable to create dir %s" % self.dbdir
        sys.exit(-1)

    self.tables.open('jobid',self.dbfiles["JOBID"])
    ljsfID=''
    try:
      rec = self.tables.jobid.first()
      while rec:
        if (rec[1] == self.fields.jobid) :
          ljsfID = rec[0]
          break
        else:
          try:
            rec = self.tables.jobid.next()
          except:
            rec = None
    except: pass
    if (ljsfID == '') :
      ljsfID='LCG'+'%05d'%(len(self.tables.jobid)+1)
      #print "Adding record for LJSF job %s" % ljsfID
      self.tables.jobid[ljsfID]=self.fields.jobid
      self.tables.jobid.close()
    #else :
      #print "Updating record for LJSF job %s" % ljsfID

    if self.fields.index('dest') :
      self.tables.open('dest',self.dbfiles["DEST"])
      self.tables.dest[ljsfID]=self.fields.dest
      self.tables.dest.close()

    if self.fields.index('exit') :
      self.tables.open('exit',self.dbfiles["EXIT"])
      self.tables.exit[ljsfID]=self.fields.exit
      self.tables.exit.close()

    if self.fields.index('jdlname') :
      self.tables.open('jdlname',self.dbfiles["JDLNAME"])
      self.tables.jdlname[ljsfID]=self.fields.jdlname
      self.tables.jdlname.close()

    if self.fields.index('jobname') :
      self.tables.open('jobname',self.dbfiles["JOBNAME"])
      self.tables.jobname[ljsfID]=self.fields.jobname
      self.tables.jobname.close()

    if self.fields.index('output') :
      self.tables.open('output',self.dbfiles["OUTPUT"])
      self.tables.output[ljsfID]=self.fields.output
      self.tables.output.close()

    if self.fields.index('reachtime') :
      self.tables.open('reachtime',self.dbfiles["REACHTIME"])
      self.tables.reachtime[ljsfID]=self.fields.reachtime
      self.tables.reachtime.close()

    if self.fields.index('rettime') :
      self.tables.open('rettime',self.dbfiles["RETTIME"])
      self.tables.rettime[ljsfID]=self.fields.rettime
      self.tables.rettime.close()

    if self.fields.index('statreason') :
      self.tables.open('statreason',self.dbfiles["REASON"])
      self.tables.statreason[ljsfID]=self.fields.statreason
      self.tables.statreason.close()

    if self.fields.index('status') :
      self.tables.open('status',self.dbfiles["STATUS"])
      self.tables.status[ljsfID]=self.fields.status
      self.tables.status.close()

    if self.fields.index('subtime') :
      self.tables.open('subtime',self.dbfiles["SUBTIME"])
      self.tables.subtime[ljsfID]=self.fields.subtime
      self.tables.subtime.close()

    if self.fields.index('user') :
      self.tables.open('user',self.dbfiles["USERS"])
      self.tables.user[ljsfID]=self.fields.user
      self.tables.user.close()

    if self.fields.index('validation') :
      self.tables.open('validation',self.dbfiles["VALIDATION"])
      self.tables.validation[ljsfID]=self.fields.validation
      self.tables.validation.close()


  def readDB(self):
    # Open the tables
    try:
      os.stat(self.dbfiles["JOBID"])
      self.tables.open('jobid',self.dbfiles["JOBID"])
    except: pass
    try:
      os.stat(self.dbfiles["DEST"])
      self.tables.open('dest',self.dbfiles["DEST"])
    except: pass
    try:
      os.stat(self.dbfiles["EXIT"])
      self.tables.open('exit',self.dbfiles["EXIT"])
    except: pass
    try:
      os.stat(self.dbfiles["JDLNAME"])
      self.tables.open('jdlname',self.dbfiles["JDLNAME"])
    except: pass
    try:
      os.stat(self.dbfiles["JOBNAME"])
      self.tables.open('jobname',self.dbfiles["JOBNAME"])
    except: pass
    try:
      os.stat(self.dbfiles["OUTPUT"])
      self.tables.open('output',self.dbfiles["OUTPUT"])
    except: pass
    try:
      os.stat(self.dbfiles["REACHTIME"])
      self.tables.open('reachtime',self.dbfiles["REACHTIME"])
    except: pass
    try:
      os.stat(self.dbfiles["RETTIME"])
      self.tables.open('rettime',self.dbfiles["RETTIME"])
    except: pass
    try:
      os.stat(self.dbfiles["REASON"])
      self.tables.open('statreason',self.dbfiles["REASON"])
    except: pass
    try:
      os.stat(self.dbfiles["STATUS"])
      self.tables.open('status',self.dbfiles["STATUS"])
    except: pass
    try:
      os.stat(self.dbfiles["SUBTIME"])
      self.tables.open('subtime',self.dbfiles["SUBTIME"])
    except: pass
    try:
      os.stat(self.dbfiles["USERS"])
      self.tables.open('user',self.dbfiles["USERS"])
    except: pass
    try:
      os.stat(self.dbfiles["VALIDATION"])
      self.tables.open('validation',self.dbfiles["VALIDATION"])
    except: pass

    # Now execute the select
    selectedRecords = 0
    rec = None
    print
    try:
      keys   = self.tables.jobid.keys()
      rec    = self.tables.jobid.first()
    except: pass
    while rec:
      try:
        ljsfID=rec[0]
        jobID=rec[1]
      except: pass
      try:
        dest=self.tables.dest[ljsfID]
      except:
        dest=''
      try:
        exit=self.tables.exit[ljsfID]
      except:
        exit=''
      try:
        jdlname=self.tables.jdlname[ljsfID]
      except:
        jdlname=''
      try:
        jobname=self.tables.jobname[ljsfID]
      except:
        jobname=''
      try:
        output=self.tables.output[ljsfID]
      except:
        output=''
      try:
        reachtime=self.tables.reachtime[ljsfID]
      except:
        reachtime=''
      try:
        rettime=self.tables.rettime[ljsfID]
      except:
        rettime=''
      try:
        status=self.tables.status[ljsfID]
      except:
        status=''
      try:
        statreason=self.tables.statreason[ljsfID]
      except:
        statreason=''
      try:
        subtime=self.tables.subtime[ljsfID]
      except:
        subtime=''
      try:
        user=self.tables.user[ljsfID]
      except:
        user=''
      try:
        validation=self.tables.validation[ljsfID]
      except:
        validation=''
      try:
        rec = self.tables.jobid.next()
      except:
        rec=None

      selected=0
      if (self.fields.index('jobid') and
          #jobID == self.fields.jobid) :
          re.match(self.fields.jobid,jobID) ) :
        selected += 1
      if (self.fields.index('dest') and
          #dest == self.fields.dest) :
          re.match(self.fields.dest,dest) ) :
        selected += 1
      if (self.fields.index('exit') and
          #exit == self.fields.exit) :
          re.match(self.fields.exit,exit) ) :
        selected += 1
      if (self.fields.index('jdlname') and
          #jdlname == self.fields.jdlname) :
          re.match(self.fields.jdlname,jdlname) ) :
        selected += 1
      if (self.fields.index('jobname') and
          #jobname == self.fields.jobname) :
          re.match(self.fields.jobname,jobname) ) :
        selected += 1
      if (self.fields.index('output') and
          #output == self.fields.output) :
          re.match(self.fields.output,output) ) :
        selected += 1
      if (self.fields.index('reachtime') and
          #reachtime == self.fields.reachtime) :
          re.match(self.fields.reachtime,reachtime) ) :
        selected += 1
      if (self.fields.index('rettime') and
          #rettime == self.fields.rettime) :
          re.match(self.fields.rettime,rettime) ) :
        selected += 1
      if (self.fields.index('status') and
          #status == self.fields.status) :
          re.match(self.fields.status,status) ) :
        selected += 1
      if (self.fields.index('statreason') and
          #statreason == self.fields.statreason) :
          re.match(self.fields.statreason,statreason) ) :
        selected += 1
      if (self.fields.index('subtime') and
          #subtime == self.fields.subtime) :
          re.match(self.fields.subtime,subtime) ) :
        selected += 1
      if (self.fields.index('user') and
          #user == self.fields.user) :
          re.match(self.fields.user,user) ) :
        selected += 1
      if (self.fields.index('validation') and
          #validation == self.fields.validation) :
          re.match(self.fields.validation,validation) ) :
        selected += 1

      if ((selected == self.selections and not self.antiselect) or
          (selected != self.selections and self.antiselect)) :
        selectedRecords += 1
        print '========'
        if (jobID and
            (self.selectionFields == "all" or
             string.find(self.selectionFields,'jobid')>=0)) :
            print 'LCG job ID:        %s' % jobID
        if (dest and
            (self.selectionFields == "all" or
             string.find(self.selectionFields,'dest')>=0)) :
            print 'Destination:       %s' % dest
        if (exit and
            (self.selectionFields == "all" or
             string.find(self.selectionFields,'exit')>=0)) :
            print 'Exit code:         %s' % exit
        if (jdlname and
            (self.selectionFields == "all" or
             string.find(self.selectionFields,'jdlname')>=0)) :
            print 'JDL name:          %s' % jdlname
        if (jobname and
            (self.selectionFields == "all" or
             string.find(self.selectionFields,'jobname')>=0)) :
            print 'Job name:          %s' % jobname
        if (output and
            (self.selectionFields == "all" or
             string.find(self.selectionFields,'output')>=0)) :
            print 'Output files:      %s' % output
        if (reachtime and
            (self.selectionFields == "all" or
             string.find(self.selectionFields,'reachtime')>=0)) :
            print 'Reached at:        %s' % reachtime
        if (rettime and
            (self.selectionFields == "all" or
             string.find(self.selectionFields,'rettime')>=0)) :
            print 'Retrieval time:    %s' % rettime
        if (status and
            (self.selectionFields == "all" or
             string.find(self.selectionFields,'status')>=0)) :
            print 'Status:            %s' % status
        if (statreason and
            (self.selectionFields == "all" or
             string.find(self.selectionFields,'statreason')>=0)) :
            print 'Status reason:     %s' % statreason
        if (subtime and
            (self.selectionFields == "all" or
             string.find(self.selectionFields,'subtime')>=0)) :
            print 'Submission time:   %s' % subtime
        if (user and
            (self.selectionFields == "all" or
             string.find(self.selectionFields,'user')>=0)) :
            print 'User:              %s' % user
        if (validation and
            (self.selectionFields == "all" or
             string.find(self.selectionFields,'validation')>=0)) :
            print 'Validation status: %s' % validation

    print
    print "-------------------------------"
    print "|  %7d record(s) selected |" % selectedRecords
    print "-------------------------------"

    try:
      self.tables.jobid.close()
    except: pass
    try:
      self.tables.dest.close()
    except: pass
    try:
      self.tables.exit.close()
    except: pass
    try:
      self.tables.jdlname.close()
    except: pass
    try:
      self.tables.jobname.close()
    except: pass
    try:
      self.tables.output.close()
    except: pass
    try:
      self.tables.reachtime.close()
    except: pass
    try:
      self.tables.rettime.close()
    except: pass
    try:
      self.tables.status.close()
    except: pass
    try:
      self.tables.statreason.close()
    except: pass
    try:
      self.tables.subtime.close()
    except: pass
    try:
      self.tables.user.close()
    except: pass
    try:
      self.tables.validation.close()
    except: pass


# main class
if __name__ == '__main__':
    ljsf=ljsfBKK()
    ljsf.main()
