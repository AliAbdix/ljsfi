#!/usr/bin/env python
#################################################################
# LJSF Installation Info interface to mysql
# Author: Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>
# Version: 2.1
# 2-3-2015

import MySQLdb
import string, os, getopt, sys
import re, socket
from time import *
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

HELP="""LJSF Installation Info mysql interface %s.
Usage: ljsfinfo.py [--create] [OPTION]...

Options:
  --help                         display this help and exit.
  --cache                        cache results
  --cache-timeout=<seconds>      cache timeout, in seconds
  --dbhost=<db host>             database host name
  --dbname=<db name>             database name
  --dbuser=<username>            database username
  --dbpass=<password>            database password
  --show-db-version              show the database version
  --arch=<arch name>             architecture name
  --autoinstall                  select only targets to install automatically
                                 in all the sites, equivalent to
                                 --autoinstall-target=all
  --autoinstall-target=<tgt>     select only <tgt> autoinstall types,
                                 if omitted will default to ALL, please
                                 refer to --list-autoinstall-targets for
                                 a full list of targets
  --list-autoinstall-targets     return the list of possible autoinstall targets
  --base                         select only base releases
  --patch                        select only patch releases
  --comments=<comments>          some comments
  --cename=<CE FQDN>             CE name
  --create                       create a new record (needs --cs and --rel)
  --create-conf=<fname>          save the release configuration in <fname>
  --gen-parser                   generate a parser for a given release
  --cs=<contact string>          contact string for the given CE
  --ctime=<creation time>        creation time (YYYY-MM-DD HH:MM:SS)
  --has-cvmfs                    select sites using cvmfs
  --no-cvmfs                     select sites not using cvmfs
  --cvmfs-available              select only releases available in cvmfs
  --cvmfs-unavailable            select only releases not available in cvmfs
  --debug                        enable debug output
  --definerel=<p1=v1>,<p2=v2>,.. define a new release with parameters p1=v1,
                                 p2=v2, ..., pN=vN
  --free                         select only free (unpinned) releases
  --jdlname=<jdl filename>       jdl filename
  --jdltype=<jdl type>           jdl type
  --jdlfile=<jdl file name>      full path to the jdl file
  --jobid=<job id>               job id
  --list-ce                      list the CEs
  --list-resource                list the resources
  --noout                        do not output anything
  --osname=<OS name>             name of the OS
  --osrelease=<OS rel>           release of the OS
  --osversion=<OS version>       version of the OS
  --facility=<facility name>     facility name
  --grid-name=<grid name>        grid name
  --production                   use production releases (with --queryrel)
  --obsolete                     use obsolete releases (with --queryrel)
  --orphaned                     select orphaned installations, i.e. installation
                                 without any job executed
  --min-proxy-lt                 min proxy lifetime before opening a new one
  --after <date>                 show records after <date>
  --before <date>                show records before <date>
  --pinned                       select only pinned releases
  --quiet                        quiet mode (no verbosity)
  --remove-lock                  remove a lock for a jdl (implies --jdlname)
  --select=<all|field list>      show the records
  --queryrel=<rel number>        show the definition of release <rel number>
  --querysite=<site cs>          show the site definition for <site cs>
  --set-lock                     set a lock for a jdl (implies --jdlname)
  --show-alias                   list the site alias
  --set-fs=<fstype>              set the fs type for a resource/site
  --set-alias=<alias>            set the alias for a site
  --list-tags                    list the site tags
  --set-tags=<tag list>          set the tags (comma separated list) for a site
  --show-task=<task_name>        show the task description for <task_name>
  --show-task-tokens             show the tokens associated to the task names
  --show-parser-tokens           show all the tokens used in the parser
  --show-relarch=<arch_name>     show the architecture description for <arch_name>
  --show-reltypedef=<type_name>  show the release type definition of <type_name>
  --show-lock                    show the lock status for a jdl
                                 (implies --jdlname)
  --show-fake-locks              show fake locks
  --fix-wrong-requests           fix wrong requests
  --atlas-sitename=<name>        ATLAS site name
  --sitename=<name>              name of the site
  --sitetype=<site type>         set the site type
  --status=<installation status> status of the installation
  --reltag=<tag>                 select only releases with tag <tag>
  --show-attrs                   show the attributes of the resource/site
  --show-fs                      show the fs type of the resource/site
  --show-reltype                 show the type of the release
  --set-reltype=<release type>   set the type of the release
  --show-relstatus               show the status of the release
  --set-relstatus=<rel status>   set the status of the release
  --show-relname                 show the name of a release from a tag
  --show-reltag                  show the tag of a release
  --set-reltag=<rel tag>         set the tag of a release
  --show-reqstatus               show the status of a request
  --set-reqstatus=<req status>   set the status of a request
  --set-autoinstall=<tgt>        enable the autoinstall facility for the release
                                 for the <tgt> targets, see
                                 --list-autoinstall-targets for a list of targets
  --unset-autoinstall            disable the autoinstall facility for the release
  --show-autoinstall             show the autoinstall status for the release
  --set-siteinfo                 set the site info
  --set-sitestatus               set the site (ce name) to 'enabled' or 'disabled'
  --site-disabled                select only the sites in disabled state
  --site-enabled                 select only the sites in enabled state
  --show-sitestatus              show the site status
  --show-rel-subscriptions       show the release subscriptions in a site
  --rel=<release name>           release name
  --reqid=<request ID>           request ID
  --tag=<tag name>               tag value
  --user=<user name>             user name
  --bdii=<BDII FQDN>             use the <BDII FQDN> BDII
  --create-wmsvoconf=<file>      create the wms vo conf file <file>.
  --create-wmscmdconf=<file>     create the wms cmd conf file <file>.
  --wmsvoconf-template=<tmpl>    use <tmpl> for the wms vo conf file.
                                 (current: %s)
  --wmscmdconf-template=<tmpl>   use <tmpl> for the wms cmd conf file.
                                 (current: %s)
  --vo=<vo name>                 set the vo name
  --ns=<ns address>              Network server address
  --lb=<lb address>              Logging & bookkeeping server address
  --ld=<ld address>              Logging destination server address
  --wmproxy=<wmproxy URI>        WMProxy URI
  --myproxy=<myproxy address>    MyProxy server address
  --show-active-wmproxy          Show the active wmproxy entries
  --tier-level=<level>           Set the tier level of the resource to <level>

Alessandro De Salvo <Alessandro.DeSalvo@roma1.infn.it>.
"""

__QUERY_RELEASE__           = "SELECT %s FROM release_stat, release_data, site, user"
__FILTER_RELEASE__          = "WHERE release_stat.sitefk=site.ref AND release_stat.userfk=user.ref AND release_stat.name=release_data.name"
__ORDER_RELEASE__           = "ORDER BY release_stat.name, site.name"
__RELEASE_MINDATE__         = "release_stat.date >= %s"
__RELEASE_MAXDATE__         = "release_stat.date <= %s"
__QUERY_RELEASE_DATA__      = "SELECT %s FROM release_data JOIN release_type ON release_data.typefk=release_type.ref JOIN autoinstall_target ON release_data.autoinstall=autoinstall_target.ref"
__QUERY_RELEASE_DATA_EXT__  = "SELECT release_data.name AS name, show_conf, field_name, token, release_data_ext.value AS value, field_nullfk, field_default, format, fregexp FROM release_data JOIN field_descriptions LEFT OUTER JOIN release_data_ext ON field_descriptions.ref=release_data_ext.fieldfk AND release_data.ref=release_data_ext.relfk WHERE table_name = 'release_data_ext' AND name='%s'"
__FILTER_RELEASE_DATA__     = "WHERE release_data.name like '%s'"
__GROUP_RELEASE_DATA__      = "GROUP BY release_data_ext.relfk"
__ORDER_RELEASE_DATA__      = "ORDER BY release_data.ref"
__TABLE_RELEASE_DATA__      = ["release_data", "release_data_ext"]
__QUERY_SITE_DATA__         = "SELECT %s FROM site s LEFT OUTER JOIN site_ext se ON s.ref=se.sitefk"
__QUERY_SITE_DATA_EXT__     = "SELECT site.cs AS cs, show_conf, field_name, token, site_ext.value AS value, field_nullfk, field_default, format, fregexp FROM site JOIN field_descriptions LEFT OUTER JOIN site_ext ON field_descriptions.ref=site_ext.fieldfk AND site_ext.sitefk = site.ref WHERE table_name = 'site_ext' AND cs='%s'"
__FILTER_SITE_DATA__        = "WHERE s.cs like '%s'"
__GROUP_SITE_DATA__         = "GROUP BY se.sitefk"
__ORDER_SITE_DATA__         = "ORDER BY s.cename DESC"
__TABLE_SITE_DATA__         = ["site", "site_ext"]
__SET_TAGS_SITENAME__       = "UPDATE site SET tags=%s WHERE site.name=%s"
__SET_TAGS_CENAME__         = "UPDATE site SET tags=%s WHERE site.cename=%s"
__SET_ALIAS_SITENAME__      = "UPDATE site SET alias=%s WHERE site.name=%s"
__SET_ALIAS_CENAME__        = "UPDATE site SET alias=%s WHERE site.cename=%s"
__SET_FS_SITENAME__         = "UPDATE site SET fstype=%s WHERE site.name=%s"
__SET_FS_CENAME__           = "UPDATE site SET fstype=%s WHERE site.cename=%s"
__SHOW_REL_TYPE__           = "SELECT description FROM release_type, release_data WHERE release_data.name=%s AND release_data.typefk=release_type.ref"
__LIST_REL_TYPE__           = "SELECT description FROM release_type ORDER BY ref"
__GET_REL_TYPE__            = "SELECT ref FROM release_type WHERE description like %s"
__SET_REL_TYPE__            = "UPDATE release_data SET typefk=%d WHERE name=%s"
__GET_REL_STATUS__          = "SELECT obsolete FROM release_data WHERE release_data.name=%s"
__SET_REL_STATUS__          = "UPDATE release_data SET release_data.obsolete=%d WHERE release_data.name=%s"
__GET_REL_TAG__             = "SELECT tag FROM release_data WHERE release_data.name=%s"
__SET_REL_TAG__             = "UPDATE release_data SET release_data.tag=%s WHERE release_data.name=%s"
__GET_REL_NAME__            = "SELECT name FROM release_data WHERE tag=%s"
__GET_REQ_STATUS__          = "SELECT request_status.description FROM request, request_status WHERE request.statusfk=request_status.ref AND request.id=%s"
__GET_REQ_STATUS_REL__      = "SELECT CONCAT(release_stat.name,',',request_type.description,',',request.id,',',request_status.description) FROM request, request_status, request_type, release_stat WHERE request.relfk=release_stat.ref AND request.typefk=request_type.ref AND request.statusfk=request_status.ref AND release_stat.name LIKE %s"
__SET_REQ_STATUS__          = "UPDATE request SET request.statusfk=(SELECT ref FROM request_status WHERE description=%s) WHERE request.id=%s"
__SET_REQ_STATUS_REL__      = "UPDATE request SET request.statusfk=(SELECT ref FROM request_status WHERE description=%s) WHERE request.id IN (SELECT request.id FROM request, request_type, release_stat WHERE request.relfk=release_stat.ref AND request.typefk=request_type.ref AND release_stat.name LIKE %s AND request_type.description LIKE %s)"
__LIST_REQ_STATUS__         = "SELECT description FROM request_status WHERE description LIKE %s ORDER BY description"
__GET_AUTOINSTALL__         = "SELECT autoinstall FROM release_data WHERE release_data.name=%s"
__SET_AUTOINSTALL__         = "UPDATE release_data SET release_data.autoinstall=%s WHERE release_data.name=%s"
__LIST_AI_TARGETS__         = "SELECT name, description FROM autoinstall_target"
__GET_SITESTATUS__          = "SELECT status FROM site WHERE cename=%s"
__GET_SITESTATUS_CS__       = "SELECT status FROM site WHERE cs=%s"
__SET_SITESTATUS__          = "UPDATE site SET status=%d WHERE cename like %s"
__SET_SITESTATUS_CS__       = "UPDATE site SET status=%d WHERE cs like %s"
__SET_SITEINFO__            = "UPDATE site SET %s WHERE cs=%s"
__SITEINFO_SITENAME__       = "site.name=%s"
__SITEINFO_ATLAS_SITENAME__ = "site.atlas_name=%s"
__SITEINFO_OSNAME__         = "site.osname=%s"
__SITEINFO_OSRELEASE__      = "site.osrelease=%s"
__SITEINFO_OSVERSION__      = "site.osversion=%s"
__SITEINFO_GRIDFK__         = "site.gridfk=%s"
__GET_RELSUBS__             = "SELECT rd.name FROM release_data rd, release_subscription rs WHERE rd.name LIKE rs.pattern AND rs.sitename=%s"
__LIST_RES__                = "SELECT DISTINCT(%s) AS res FROM site"
__LIST_RES_ORDER__          = "ORDER BY res"
__LIST_TAGS_SITENAME__      = "SELECT DISTINCT(site.tags) FROM site WHERE site.name LIKE %s AND site.name IS NOT NULL"
__LIST_TAGS_CENAME__        = "SELECT DISTINCT(site.tags) FROM site WHERE site.cename=%s AND site.cename IS NOT NULL"
__LIST_TAGS_CS__            = "SELECT DISTINCT(site.tags) FROM site WHERE site.cs=%s AND site.cename IS NOT NULL"
__SHOW_ALIAS_SITENAME__     = "SELECT DISTINCT(site.alias), site.name FROM site WHERE site.name LIKE %s AND site.name IS NOT NULL"
__SHOW_ALIAS_CENAME__       = "SELECT DISTINCT(site.alias), site.cename FROM site WHERE site.cename=%s AND site.cename IS NOT NULL ORDER BY alias DESC"
__SHOW_ATTRS_SITENAME__     = "SELECT GROUP_CONCAT(DISTINCT site_attr.name), site.name FROM site, site_attr WHERE site.name LIKE %s AND site.name IS NOT NULL AND site.attr & site_attr.attr = site_attr.attr GROUP BY site.attr"
__SHOW_ATTRS_CENAME__       = "SELECT GROUP_CONCAT(DISTINCT site_attr.name), site.cename FROM site, site_attr WHERE site.cename=%s AND site.cename IS NOT NULL AND site.attr & site_attr.attr = site_attr.attr GROUP BY site.attr"
__SHOW_FS_SITENAME__        = "SELECT DISTINCT(site.fstype), site.name FROM site WHERE site.name LIKE %s AND site.name IS NOT NULL"
__SHOW_FS_CENAME__          = "SELECT DISTINCT(site.fstype), site.cename FROM site WHERE site.cename=%s AND site.cename IS NOT NULL ORDER BY fstype DESC"
__CHECK_RELEASE__           = "SELECT ref FROM release_data WHERE name=%s"
__DEFINE_RELEASE__          = "INSERT INTO release_data SET %s"
__GET_BDII_INFO__           = "SELECT ns, lb, ld, wmproxy, myproxy FROM bdii WHERE hostname='%s'"
__SHOW_TASK__               = "SELECT ref, name, description FROM task WHERE task.name=%s"
__SHOW_RELARCH__            = "SELECT ref, platform_type, os_type, gcc_ver, mode, description FROM release_arch WHERE release_arch.description=%s"
__SHOW_RELTYPEDEF__         = "SELECT ref, category, description FROM release_type WHERE release_type.description=%s"
__SHOW_DB_VERSION__         = "SELECT major, minor, patch FROM schema_version LIMIT 1"
__SHOW_TASK_TOKENS__        = "SELECT request_type.description,field_descriptions.token FROM field_descriptions, request_type WHERE table_name='release_data.task' AND field_name=(SELECT name FROM field_relations WHERE table1='release_data' AND field1=request_type.field AND table2='task')"
__SHOW_PARSER_TOKENS__      = "SELECT token FROM field_descriptions WHERE show_conf=1 AND token IS NOT NULL"
__SHOW_ACTIVE_WMPROXY__     = "SELECT DISTINCT(wmproxy) FROM bdii WHERE enabled=1"
__SHOW_FAKE_LOCKS__         = "SELECT DISTINCT(j.name) FROM request r, release_stat rs, jdl j, job jb WHERE jb.jdlfk=j.ref AND r.relfk=j.relfk AND r.relfk=rs.ref AND statusfk=(SELECT ref FROM request_status WHERE description='autorun') AND joblock=1 AND jb.id NOT IN (SELECT id FROM job WHERE validationfk=(SELECT ref FROM validation WHERE description='pending')) UNION SELECT DISTINCT(jdl.name) FROM jdl WHERE (SELECT COUNT(*) FROM job WHERE jdlfk=jdl.ref)=0 AND joblock=1 UNION SELECT DISTINCT(jdl.name) FROM jdl, job WHERE jdl.ref=job.jdlfk AND (SELECT COUNT(*) FROM request WHERE id=job.requestfk) = 0 AND joblock=1"
__SHOW_WRONG_REQS__         = "SELECT job.id, request.id, job.requestfk FROM request, job, jdl WHERE job.jdlfk=jdl.ref AND jdl.relfk=request.relfk AND request.statusfk=(SELECT ref FROM request_status WHERE description='autorun') AND (SELECT COUNT(*) FROM request WHERE id=job.requestfk) = 0 AND request.id != job.requestfk"
__SHOW_DUP_REQS__           = "SELECT DISTINCT(request.id), job.requestfk FROM request, job, jdl WHERE job.jdlfk=jdl.ref AND jdl.relfk=request.relfk AND request.statusfk=(SELECT ref FROM request_status WHERE description='autorun') AND (SELECT COUNT(*) FROM request WHERE id=job.requestfk) > 0 AND request.id != job.requestfk"
__FIX_WRONG_REQS__          = "UPDATE job SET requestfk='%s' WHERE id='%s'"
__FIX_DUP_REQS__            = "UPDATE request SET statusfk=(SELECT ref FROM request_status WHERE description='ignore') WHERE id='%s'"
__CONFMAP__                 = { 'RELEASE' : 1
                              , 'INSTALLERVER' : 11
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
                              , 'RELCATEGORY' : 31 }
__WMSCONFMAP__              = { 'NS' : 'ns'
                              , 'LB' : 'lb'
                              , 'LD' : 'ld'
                              , 'WMPROXY' : 'wmproxy'
                              , 'MYPROXY' : 'myproxy' }



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


class ljsfInfo:
  # Defaults
  db         = None
  dbr        = None
  dbw        = None
  dbhost     = None
  dbname     = None
  dbuser     = None
  dbpass     = None
  fields     = Fields()
  antiselect = 0
  quiet      = False
  noout      = False
  relname    = ''
  atlas_sitename  = None
  sitename        = None
  mode            = 'update' # default mode
  selectionFields = 'site.name,site.cs,release_stat.name,release_stat.status,release_stat.comments,user.name'
  wmsvoconftmpl   = 'wmsvo.conf.template'
  wmscmdconftmpl  = 'wmscmd.conf.template'
  bdii       = None
  debug      = False
  showtokens = False
  genparser  = False
  tokenData  = []
  ns         = None
  lb         = None
  ld         = None
  wmproxy    = None
  myproxy    = None
  userid     = None
  role       = None
  mindate    = None
  maxdate    = None


  # Minimum and maximum proxy lifetime (seconds)
  minproxylt = 14400
  maxproxylt = 86400
  if (os.environ.has_key('LJSF_MINPROXY_LT')):
    minproxylt = int(os.environ['LJSF_MINPROXY_LT'])
  if (os.environ.has_key('LJSF_MAXPROXY_LT')):
    maxproxylt = int(os.environ['LJSF_MAXPROXY_LT'])

  # VO name
  vo = None
  if (os.environ.has_key('VO')): vo = os.environ['VO']

  # Configuration creator
  instconf=''
  wmsvoconf=''
  wmscmdconf=''
  conftmpl = 'install.conf.template'
  if (os.environ.has_key('TEMPLATEPATH')):
    conftmpl = ('%s/%s' % (os.environ['TEMPLATEPATH'],conftmpl))
    wmsvoconftmpl  = ('%s/%s' % (os.environ['TEMPLATEPATH'],wmsvoconftmpl))
    wmscmdconftmpl = ('%s/%s' % (os.environ['TEMPLATEPATH'],wmscmdconftmpl))

  # Cache
  ljsfDBURL = None
  memcacheServer = None
  memcacheClient = None
  cache = False
  cacheTimeout = 300

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

  def setArch(self,arg):
    self.fields.add('site.arch', ("'%s'" % arg))

  def setInfosys(self,arg):
    self.bdii = arg

  def setResource(self,arg):
    self.fields.add('site.cename', ("'%s'" % arg))

  def setCache(self,arg):
    self.cache = arg

  def setCacheTimeout(self,arg):
    self.cacheTimeout = int(arg)

  def setComments(self,arg):
    self.fields.add('release_stat.comments', ("'%s'" % arg))

  def setCS(self,arg):
    self.fields.add('site.cs', ("'%s'" % arg))

  def setCTime(self,arg):
    self.fields.add('release_stat.date', ("'%s'" % arg))

  def setInstconf(self,arg):
    self.instconf=arg

  def setGenparser(self,mode):
    self.genparser=mode

  def setWMSVOconf(self,arg):
    self.wmsvoconf=arg

  def setWMSCMDconf(self,arg):
    self.wmscmdconf=arg

  def setDebug(self,mode):
    self.debug=True

  def setReleaseParams(self,arg):
    for par in arg.split(','):
      ppar=par.split('=')
      self.fields.add(ppar[0],("'%s'" % ppar[1]))

  def setJdlName(self,arg):
    self.fields.add('jdl.name', ("'%s'" % arg))

  def setJdlType(self,arg):
    self.fields.add('jdl.type', ("'%s'" % arg))

  def setJdlFile(self,arg):
    try:
      self.fields.add('jdl.content', ("'%s'" % open(arg,"r").read()))
    except:
      print "File %s not found. Skipping." % arg

  def setJobID(self,arg):
    self.fields.add('job.id', ("'%s'" % arg))

  def setMinDate(self,arg):
    self.mindate = "'%s'" % arg

  def setMaxDate(self,arg):
    self.maxdate = "'%s'" % arg

  def setMinProxyLT(self,arg):
    self.minproxylt = int(arg)

  def setObsolete(self,arg):
    self.fields.add('release_data.obsolete', arg)

  def setOSName(self,arg):
    self.fields.add('site.osname', ("'%s'" % arg))

  def setOSRelease(self,arg):
    self.fields.add('site.osrelease', ("'%s'" % arg))

  def setOSVersion(self,arg):
    self.fields.add('site.osversion', ("'%s'" % arg))

  def setGridName(self,arg):
    if (arg.upper() != "ALL"):
        self.fields.add('site.gridfk', ("(SELECT ref FROM grid WHERE name='%s')" % arg))

  def setFacility(self,arg):
    self.fields.add('site.facilityfk', ("(SELECT ref FROM facility WHERE name='%s')" % arg))

  def setAutoinstallFlag(self,arg):
    self.fields.add('release_data.autoinstall', arg)

  def setAutoinstallTarget(self,arg):
    self.fields.add('autoinstall_target.name', ("'%s'" % arg))

  def setBaseRelease(self,arg):
    self.fields.add('release_data.requires', "NULL")

  def setPatchRelease(self,arg):
    self.fields.add('release_data.requires', "NOTNULL")

  def setQuiet(self,mode):
    self.quiet = mode

  def setNoout(self,mode):
    self.noout = mode

  def setRelease(self,arg):
    self.fields.add('release_stat.name', ("'%s'" % arg))

  def setRequest(self,arg):
    self.fields.add('request.id', ("'%s'" % arg))

  def setSitename(self,arg):
    self.fields.add('site.name', ("'%s'" % arg))

  def setAtlasSitename(self,arg):
    self.fields.add('site.atlas_name', ("'%s'" % arg))

  def setSitetype(self,arg):
    self.fields.add('site.activity_typefk', ("(SELECT ref FROM site_activity_type WHERE name='%s')" % arg))

  def setAliasValue(self,arg):
    self.fields.add('site.alias', ("'%s'" % arg))

  def setFSType(self,arg):
    self.fields.add('site.fstype', ("'%s'" % arg))

  def setSiteTags(self,arg):
    self.fields.add('site.tags', ("'%s'" % arg))

  def setReleaseTags(self,arg):
    self.fields.add('release_data.tag', ("'%s'" % arg))

  def setReleaseType(self,arg):
    self.fields.add('release_type.description', ("'%s'" % arg))

  def setReleaseStatus(self,arg):
    rc = 0
    if (arg == 'production'):
      self.fields.add('release_data.obsolete', 0)
    elif (arg == 'obsolete'):
      self.fields.add('release_data.obsolete', 1)
    else:
      print "Unknown release status '%s'" % arg
      print "Possible values are: 'obsolete', 'production'"
      rc = 1
    return rc

  def setRequestStatus(self,arg):
    self.fields.add('request_status.description', ("'%s'" % arg))

  def setSiteStatusFlag(self,arg):
    rc = 0
    if (arg == 'enabled'):
      self.fields.add('site.status', 1)
    elif (arg == 'disabled'):
      self.fields.add('site.status', 0)
    else:
      print "Unknown site status '%s'" % arg
      print "Possible values are: 'enabled', 'disabled'"
      rc = 1
    return rc

  def setSiteEnabled(self,arg):
    self.fields.add('site.status', arg)

  def setCVMFSAvailable(self,arg):
    self.fields.add('release_data.cvmfs_available', arg)

  def setReleaseName(self,arg):
    self.relname=arg

  def setQuerySitename(self,arg):
    self.sitename=arg

  def setTaskName(self,arg):
    self.fields.add('task.name', ("'%s'" % arg))

  def setReleaseArch(self,arg):
    self.fields.add('release_arch.description', ("'%s'" % arg))

  def setReleaseStatStatus(self,arg):
    self.fields.add('release_stat.status', ("'%s'" % arg))

  def setReleaseStatTag(self,arg):
    self.fields.add('release_stat.tag', ("'%s'" % arg))

  def setUser(self,arg):
    self.fields.add('user.name', ("'%s'" % arg))

  def setReleaseStatPin(self,arg):
    self.fields.add('release_stat.pin', arg)

  def setVOName(self,arg):
    self.vo = arg.lower()

  def setNS(self,arg):
    self.ns = arg.lower()

  def setLB(self,arg):
    self.lb = arg.lower()

  def setLD(self,arg):
    self.ld = arg.lower()

  def setWMProxy(self,arg):
    self.wmproxy = arg.lower()

  def setMyProxy(self,arg):
    self.myproxy = arg.lower()

  def setTierLevel(self,arg):
    self.fields.add('site.tier_level', ("'%s'" % arg))

  def getTokens(self, pattern=None, list=False):
    tokens = None
    if (list):
        tokens = {}
        if (pattern):
            for token in self.tokenData:
                m = re.search(pattern, token[0])
                if (m): tokens[m.group(1)] = token[1]
        else:
            for token in self.tokenData:
                tokens[token[0].replace("@","")] = token[1]
    else:
        tokens = []
        if (pattern):
            for token in self.tokenData:
                m = re.search(pattern, token[0])
                if (m): tokens.append(token)
        else:
            for token in self.tokenData:
                tokens.append(token)
    return tokens

  def getTasks(self):
    patt = "@([^@]*TASK)@"
    taskList = {}
    for token in self.tokenData:
        m = re.search(patt, token[0])
        if (m): taskList[m.group(1)] = token[1]
    return taskList

  def getRequirements(self):
    for token in self.tokenData:
        if (token[0] == "@REQUIRES@"): return token[1]
    return None

  def queryRel(self,relname=None):
      if (relname): self.relname = relname
      self.quiet = True
      showTokenOpt = self.showtokens
      self.showtokens = True
      # Main table
      self.selectionFields  = "release_data.*"
      # Aggregated tables
      tables = __TABLE_RELEASE_DATA__
      for tableName in tables:
        (numrows, rowdesc, res) = self.queryDB("SELECT name,field1,table2,field2 FROM field_relations WHERE table1='%s'" % tableName)
        for row in res:
          foreignConstraint = "%s.%s=%s.ref" % (tableName,row[1],row[2])
          fieldName = "%s.%s" % (row[2],row[3])
          aggregatedTable = "%s.%s" % (tableName,row[2])
          self.selectionFields += ",(SELECT %s FROM %s WHERE %s) AS '%s.%s'" % (fieldName,row[2],foreignConstraint,aggregatedTable,row[0])
          __TABLE_RELEASE_DATA__.append(aggregatedTable)
      # Complete the query
      qryfilter=(__FILTER_RELEASE_DATA__ % self.relname)
      if (self.fields.index('release_data.obsolete')):
        qryfilter = ("%s AND release_data.obsolete=%s AND release_data.typefk <> 1" % (qryfilter, self.fields.get('release_data.obsolete')))
      if (self.fields.index('release_data.autoinstall')):
        qryfilter = ("%s AND release_data.autoinstall=%s" % (qryfilter, self.fields.get('release_data.autoinstall')))
      if (self.fields.index('autoinstall_target.name')):
        qryfilter = ("%s AND autoinstall_target.name=%s" % (qryfilter, self.fields.get('autoinstall_target.name')))
      rc=self.readDB(body=__QUERY_RELEASE_DATA__,filter=qryfilter,orderby=__ORDER_RELEASE_DATA__,tables=__TABLE_RELEASE_DATA__,extquery=__QUERY_RELEASE_DATA_EXT__,extkey='name')
      self.showtokens = showTokenOpt
      return rc

  def querySite(self,sitename=None):
      if (sitename): self.sitename = sitename
      self.quiet = True
      showTokenOpt = self.showtokens
      self.showtokens = True
      self.selectionFields  = "s.*"
      self.selectionFields += ",GROUP_CONCAT((SELECT field_name FROM field_descriptions WHERE ref=se.fieldfk),',',se.value) AS site_ext"
      qryfilter=(__FILTER_SITE_DATA__ % self.sitename)
      rc=self.readDB(body=__QUERY_SITE_DATA__,filter=qryfilter,groupby=__GROUP_SITE_DATA__,orderby=__ORDER_SITE_DATA__,tables=__TABLE_SITE_DATA__,extquery=__QUERY_SITE_DATA_EXT__,extkey='cs')
      self.showtokens = showTokenOpt
      return rc


  def openDB(self,dbtype="r"):
    currdb = None
    # Open the database
    if (self.dbhost and self.dbname and self.dbuser and self.dbpass):
      if (dbtype == "r"):
        self.dbr = MySQLdb.connect(host=self.dbhost,user=self.dbuser,passwd=self.dbpass,db=self.dbname)
      else:
        self.dbw = MySQLdb.connect(host=self.dbhost,user=self.dbuser,passwd=self.dbpass,db=self.dbname)
    else:
      if (dbtype == "r" and os.path.exists("%s/.my-ro.cnf" % os.environ["CONFPATH"])):
        db_conf = ("%s/.my-ro.cnf" % os.environ["CONFPATH"])
        if (self.debug): print "Using the RO DB conf %s" % db_conf
      else:
        db_conf = ("%s/.my.cnf" % os.environ["CONFPATH"])
        if (self.debug): print "Using the RW DB conf %s" % db_conf
      if (os.environ.has_key('LJSFDBNAME')):
        db_name = os.environ["LJSFDBNAME"]
      else:
        db_name = "atlas_install"
      if (dbtype == "r"):
        self.dbr = MySQLdb.connect(read_default_file=db_conf,db=db_name)
        self.db = self.dbr
      else:
        self.dbw = MySQLdb.connect(read_default_file=db_conf,db=db_name)
        self.db = self.dbw

    # Check the user's credentials
    (self.userid,self.role) = self.checkUser()
    if (not self.userid or not self.role): sys.exit(100)


  def writeDB(self):
    # Defaults
    if (not self.fields.index('release_stat.date')):
      self.fields.add('release_stat.date',strftime("'%Y-%m-%d %H:%M:%S'", gmtime()))
    ctime = self.fields.get('release_stat.date')
    # Check for the site params
    cs = self.fields.get('site.cs')
    (numrows, rowdesc, res) = self.queryDB(("SELECT ref FROM site WHERE cs=%s" % cs))
    if (self.mode=='insert'):
      if (len(res) == 0):
        query = "INSERT INTO site SET"
        indx=0
        for field in self.fields.getall():
          if (field[0].split(".")[0] == "site"):
            if (indx > 0): query += ","
            query += (" %s=%s" % (field[0], field[1]))
            indx += 1
        self.queryDB(query, True)
        (numrows, rowdesc, res) = self.queryDB(("SELECT ref FROM site WHERE cs=%s" % cs))
      else:
        query = "UPDATE site SET"
        indx=0
        for field in self.fields.getall():
          if (field[0].split(".")[0] == "site"):
            if (indx > 0): query += ","
            query += (" %s=%s" % (field[0], field[1]))
            indx += 1
        query = ("%s WHERE ref=%d" % (query, res[0][0]))
        self.queryDB(query, True)
    sitefk=res[0][0]

    # Set the user id
    self.fields.add('jdl.userfk',self.userid)

    # Check if the requested record is already there
    query=("SELECT ref, status FROM release_stat WHERE sitefk=%d AND name=%s" % (sitefk, self.fields.get('release_stat.name')))
    (numrows, rowdesc, res) = self.queryDB(query)
    if (len(res) != 0):
      if (not self.fields.index('release_stat.status')):
        self.fields.add('release_stat.status',("'%s'" % res[0][1]))
      query = ('UPDATE release_stat SET userfk=%d, status=%s, date=%s' % (self.userid,self.fields.get('release_stat.status'),ctime))
      if (self.fields.index('release_stat.comments')):
        query += (", comments=%s" % self.fields.get('release_stat.comments'))
      query += (' WHERE ref=%d' % res[0][0])
    else:
      if (not self.fields.index('release_stat.status')):
        self.fields.add('release_stat.status',"'pending'")
      query = ('INSERT INTO release_stat SET date=%s, sitefk=%d, name=%s, tag=%s, status=%s, userfk=%d' % (ctime,sitefk,self.fields.get('release_stat.name'), self.fields.get('release_stat.tag'), self.fields.get('release_stat.status'), self.userid))

    # Insert or update the db
    if (self.debug): print query
    self.queryDB(query, True)
    query=("SELECT ref, status FROM release_stat WHERE sitefk=%d AND name=%s" % (sitefk, self.fields.get('release_stat.name')))
    if (self.debug): print query
    (numrows, rowdesc, res) = self.queryDB(query)
    self.fields.add('jdl.relfk',res[0][0])

    # Check for jdl
    if (self.fields.index('jdl.name')):
      jdlname = self.fields.get('jdl.name')
      if (self.fields.index('jdl.type')):
        jdltype = self.fields.get('jdl.type')
      else:
        jdltype = "'unknown'"
      (numrows, rowdesc, res) = self.queryDB(("SELECT ref FROM jdl WHERE name=%s" % jdlname))
      if (len(res) == 0):
        query = "INSERT INTO jdl SET joblock=0"
        for field in self.fields.getall():
          if (field[0].split(".")[0] == "jdl"):
            query += (", %s=%s" % (field[0], field[1]))
        if (self.debug): print query
        self.queryDB(query, True)
        (numrows, rowdesc, res) = self.queryDB(("SELECT ref FROM jdl WHERE name=%s" % jdlname))
      else:
        query = "UPDATE jdl SET"
        indx = 0
        for field in self.fields.getall():
          if (field[0].split(".")[0] == "jdl"):
            if (indx > 0): query += ","
            query += (" %s=%s" % (field[0], field[1]))
            indx += 1
        query += (" WHERE ref=%d" % res[0][0])
        if (self.debug): print query
        self.queryDB(query, True)
      self.fields.remove('jdl.name')
      self.fields.remove('jdl.type')
      self.fields.remove('jdl.content')

  def checkUser(self):
    # Check the user name
    if (self.fields.index('user.name')):
      username=self.fields.get('user.name')
      userdn=""
    else:
      username=("'%s@%s'" % (os.environ["USER"],socket.getfqdn()))
      userdn=utils.checkProxy(self.minproxylt,self.maxproxylt)
    (numrows, rowdesc, res) = self.queryDB("SELECT user.ref,role.description,valid_end>now(),enabled FROM user,role WHERE name=%s AND dn='%s' AND user.rolefk=role.ref" % (username,userdn))
    if (len(res)==0):
      print "User %s, %s unknown. Please register to LJSFi." % (username,userdn)
      return (None,None)
    else:
      if (res[0][1] != "admin" and res[0][1] != "master"):
        print "Your user %s does not have sufficient privileges to access the database." % username
        return (None,None)
      elif (res[0][2] == 0):
        print "Your user %s has expired." % username
        return (None,None)
      elif (res[0][3] == 0):
        print "Your user %s has been disabled." % username
        return (None,None)
    return (res[0][0],res[0][1])


  def showDBVersion(self):
    (numrows, rowdesc, res) = self.queryDB(__SHOW_DB_VERSION__)
    if (numrows==0):
      print "No schema version information available"
      sys.exit(1)
    else:
      print "Installation DB v%d.%d.%d" % (res[0][0],res[0][1],res[0][2])


  def showLock(self, jdlname=None):
    if (not jdlname): jdlname = self.fields.get('jdl.name')
    else: jdlname = "'%s'" % jdlname
    (numrows, rowdesc, res) = self.queryDB(("SELECT jdl.ref,jdl.joblock,user.name FROM jdl,user WHERE jdl.name=%s AND jdl.userfk=user.ref" % jdlname))
    if (len(res)==0):
      if (not self.noout): print "unlocked undefined"
      return None, None
    else:
      if (not self.noout):
        # Print the lock status
        if (res[0][1] == 0):
          print "unlocked"
        else:
          print "locked %s" % res[0][2]
      return res[0][1], res[0][2]


  def setLock(self,jdlname=None):
    rc = 0
    if (not jdlname): jdlname = self.fields.get('jdl.name')
    else: jdlname = "'%s'" % jdlname
    (numrows, rowdesc, res) = self.queryDB(("SELECT jdl.ref,jdl.joblock,user.name FROM jdl,user WHERE jdl.name=%s AND jdl.userfk=user.ref" % jdlname))
    if (len(res)==0):
      print "No jdl defined with this name"
      rc = 1
    elif (res[0][1]==1):
      print "JDL already locked by user %s" % res[0][2]
      rc = 2
    else:
      # Set the lock
      self.queryDB(("UPDATE jdl SET joblock=1,joblock_date=UTC_TIMESTAMP(),userfk=%d WHERE ref=%d" % (self.userid,res[0][0])), True)
    return rc


  def showFakeLocks(self):
    (numrows, rowdesc, res) = self.queryDB(__SHOW_FAKE_LOCKS__)
    if (not self.noout):
      # Print the jdl names
      for resdata in res:
        print resdata[0]
    return


  def fixWrongRequests(self):
    (numrows, rowdesc, res) = self.queryDB(__SHOW_WRONG_REQS__)
    for resdata in res:
      query = __FIX_WRONG_REQS__ % (resdata[1],resdata[0])
      self.queryDB(query, True)
    (numrows, rowdesc, res) = self.queryDB(__SHOW_DUP_REQS__)
    for resdata in res:
      query = __FIX_DUP_REQS__ % resdata[0]
      self.queryDB(query, True)
    return


  def removeLock(self, jdlname=None):
    if (not jdlname):
      if (self.fields.index('jdl.name')):
        jdlname = self.fields.get('jdl.name')
      else:
        (numrows, rowdesc, res) = self.queryDB(("SELECT jdl.name FROM job,jdl WHERE job.id=%s AND job.jdlfk=jdl.ref" % self.fields.get('job.id')))
        if (len(res)==0):
          print "Cannot retrieve the JDL name for this job"
          return 112
        else:
          jdlname = ("'%s'" % res[0][0])
    (numrows, rowdesc, res) = self.queryDB(("SELECT jdl.ref,jdl.joblock,user.name FROM jdl,user WHERE jdl.name=%s AND jdl.userfk=user.ref" % jdlname))
    if (len(res)==0):
      print "No jdl defined with this name"
      return 111
    elif (res[0][1]==0):
      print "JDL already unlocked"
      return 0
    elif (res[0][2].split('@')[0]!=os.environ["USER"]):
      print "You are not the owner of this lock"
      return 113
    else:
      # Remove the lock
      self.queryDB(("UPDATE jdl SET joblock=0,joblock_date=UTC_TIMESTAMP() WHERE ref=%d" % res[0][0]), True)
    return 0

  def listResource(self):
    # List the resources
    return self.readDB(body=__LIST_RES__,filter='',orderby=__LIST_RES_ORDER__)

  def setTags(self):
    # Set the site tags
    if (     self.fields.index('site.tags')
        and (self.fields.index('site.name') or self.fields.index('site.cename'))):
      if (self.fields.index('site.name')):
        query = (__SET_TAGS_SITENAME__ % (self.fields.get('site.tags'),self.fields.get('site.name')))
      else:
        query = (__SET_TAGS_CENAME__ % (self.fields.get('site.tags'),self.fields.get('site.cename')))
      try:
        (numrows, rowdesc, res) = self.queryDB(query, True)
      except:
        print "Cannot set the tags"
        sys.exit(43)

  def listTags(self):
    # List the site tags
    if (self.fields.index('site.name') or self.fields.index('site.cename') or self.fields.index('site.cs')):
      if (self.fields.index('site.name')):
        query = (__LIST_TAGS_SITENAME__ % self.fields.get('site.name'))
      elif (self.fields.index('site.cs')):
        query = (__LIST_TAGS_CS__ % self.fields.get('site.cs'))
      else:
        query = (__LIST_TAGS_CENAME__ % self.fields.get('site.cename'))
      try:
        if (self.debug): print query
        (numrows, rowdesc, res) = self.queryDB(query)
        if (len(res)>0):
          print res[0][0]
      except:
        print "Cannot list the tags"
        raise

  def setRelType(self):
    if (self.fields.index('release_type.description')):
      query = (__GET_REL_TYPE__ % self.fields.get('release_type.description'))
      try:
        (numrows, rowdesc, res) = self.queryDB(query)
        if (len(res)>0):
          relType=int(res[0][0])
          query = (__SET_REL_TYPE__ % (relType,self.fields.get('release_stat.name')))
          try:
            (numrows, rowdesc, res) = self.queryDB(query, True)
          except:
            print "Cannot set the release type"
            sys.exit(44)
        else:
          try:
            query = (__LIST_REL_TYPE__)
            (numrows, rowdesc, res) = self.queryDB(query)
            print "No release type found with the specified parameters"
            print "Possible values for release type are:"
            for reltype in res:
              print reltype[0]
          except:
            print "Cannot list the release types"
            sys.exit(45)
      except:
        print "Cannot retrieve the release type ID"
        sys.exit(46)

  def showRelType(self):
    if (self.fields.index('release_stat.name')):
      query = (__SHOW_REL_TYPE__ % self.fields.get('release_stat.name'))
      try:
        (numrows, rowdesc, res) = self.queryDB(query)
        if (len(res)>0):
          print res[0][0]
      except:
        print "Cannot show the release type"
        raise

  def setRelStatus(self):
    if (self.fields.index('release_data.obsolete')):
      query = (__SET_REL_STATUS__ % (self.fields.get('release_data.obsolete'),self.fields.get('release_stat.name')))
      try:
        (numrows, rowdesc, res) = self.queryDB(query, True)
      except:
        print "Cannot set the release status"
        sys.exit(50)

  def showRelStatus(self):
    statusDesc = [ 'production', 'obsolete' ]
    if (self.fields.index('release_stat.name')):
      query = (__GET_REL_STATUS__ % self.fields.get('release_stat.name'))
      try:
        (numrows, rowdesc, res) = self.queryDB(query)
        if (len(res)>0):
          print statusDesc[res[0][0]]
      except:
        raise

  def setRelTag(self):
    if (self.fields.index('release_data.tag')):
      query = (__SET_REL_TAG__ % (self.fields.get('release_data.tag'),self.fields.get('release_stat.name')))
      try:
        (numrows, rowdesc, res) = self.queryDB(query, True)
      except:
        print "Cannot set the release tag"
        sys.exit(60)

  def showRelTag(self):
    if (self.fields.index('release_stat.name')):
      query = (__GET_REL_TAG__ % self.fields.get('release_stat.name'))
      try:
        (numrows, rowdesc, res) = self.queryDB(query)
        if (len(res)>0):
          print res[0][0]
      except:
        raise

  def showRelName(self):
    if (self.fields.index('release_data.tag')):
      query = (__GET_REL_NAME__ % self.fields.get('release_data.tag'))
      try:
        (numrows, rowdesc, res) = self.queryDB(query)
        if (len(res)>0):
          print res[0][0]
      except:
        raise

  def setAutoinstall(self):
    if (self.fields.index('release_data.autoinstall')):
      query = (__SET_AUTOINSTALL__ % (self.fields.get('release_data.autoinstall'),self.fields.get('release_stat.name')))
      try:
        (numrows, rowdesc, res) = self.queryDB(query, True)
      except:
        print "Cannot set the autoinstall condition"
        sys.exit(70)

  def showAutoinstall(self):
    statusDesc = [ 'false', 'true' ]
    if (self.fields.index('release_stat.name')):
      query = (__GET_AUTOINSTALL__ % self.fields.get('release_stat.name'))
      try:
        (numrows, rowdesc, res) = self.queryDB(query)
        if (len(res)>0):
          print statusDesc[res[0][0]]
      except:
        raise

  def listAutoinstallTargets(self):
    query = (__LIST_AI_TARGETS__)
    try:
      (numrows, rowdesc, res) = self.queryDB(query, True)
      for row in res:
        print "%-20s: %s" % (row[0],row[1])
    except:
      raise

  def setSiteInfo(self):
    if (self.fields.index('site.cs')):
      values = []
      if (self.fields.index('site.name')): values.append(__SITEINFO_SITENAME__ % self.fields.get('site.name'))
      if (self.fields.index('site.atlas_name')): values.append(__SITEINFO_ATLAS_SITENAME__ % self.fields.get('site.atlas_name'))
      if (self.fields.index('site.osname')): values.append(__SITEINFO_OSNAME__ % self.fields.get('site.osname'))
      if (self.fields.index('site.osrelease')): values.append(__SITEINFO_OSRELEASE__ % self.fields.get('site.osrelease'))
      if (self.fields.index('site.osversion')): values.append(__SITEINFO_OSVERSION__ % self.fields.get('site.osversion'))
      if (self.fields.index('site.gridfk')): values.append(__SITEINFO_GRIDFK__ % self.fields.get('site.gridfk'))
      if (values):
        query = (__SET_SITEINFO__ % (string.join(values,','),self.fields.get('site.cs')))
        if (self.debug): print query
        try:
          (numrows, rowdesc, res) = self.queryDB(query, True)
        except:
          print "Cannot set the site info"
          sys.exit(80)

  def setSiteStatus(self):
    query = None
    if (self.fields.index('site.cename')):
      query = (__SET_SITESTATUS__ % (self.fields.get('site.status'),self.fields.get('site.cename')))
    elif (self.fields.index('site.cs')):
      query = (__SET_SITESTATUS_CS__ % (self.fields.get('site.status'),self.fields.get('site.cs')))
    if (query):
      try:
        (numrows, rowdesc, res) = self.queryDB(query, True)
      except:
        print "Cannot set the site status"
        sys.exit(80)

  def showSiteStatus(self):
    statusDesc = [ 'disabled', 'enabled' ]
    query = None
    if (self.fields.index('site.cename')):
      query = (__GET_SITESTATUS__ % self.fields.get('site.cename'))
    elif (self.fields.index('site.cs')):
      query = (__GET_SITESTATUS_CS__ % self.fields.get('site.cs'))
    if (query):
      try:
        (numrows, rowdesc, res) = self.queryDB(query)
        if (len(res)>0):
          print statusDesc[res[0][0]]
      except:
        raise

  def showRelSubscriptions(self):
    statusDesc = [ 'disabled', 'enabled' ]
    if (self.fields.index('site.name')):
      query = (__GET_RELSUBS__ % self.fields.get('site.name'))
      if (self.debug): print query
      try:
        (numrows, rowdesc, res) = self.queryDB(query)
        if (len(res)>0):
          for row in res: print row[0]
        else:
          print 'ALL'
      except:
        raise

  def setReqStatus(self):
    if (self.fields.index('request_status.description') and self.fields.index('request.id')):
      query = (__GET_REQ_STATUS__ % self.fields.get('request.id'))
      try:
        (numrows, rowdesc, res) = self.queryDB(query)
        if (len(res)>0):
          query = (__LIST_REQ_STATUS__ % self.fields.get('request_status.description'))
          (numrows, rowdesc, res) = self.queryDB(query)
          if (len(res)>0):
            query = (__SET_REQ_STATUS__ % (self.fields.get('request_status.description'),self.fields.get('request.id')))
            try:
              (numrows, rowdesc, res) = self.queryDB(query, True)
            except:
              print "Cannot set the request status"
              sys.exit(94)
          else:
            try:
              query = (__LIST_REQ_STATUS__ % "'%'")
              (numrows, rowdesc, res) = self.queryDB(query)
              print "No request status found with the specified parameters"
              print "Possible values for request status are:"
              for reqstat in res:
                print reqstat[0]
            except:
              print "Cannot list the request statuses"
              sys.exit(95)
        else:
          print "Cannot find request id '%s'" % self.fields.get('request.id')
          sys.exit(96)
      except:
        print "Cannot retrieve the request data"
        sys.exit(97)

  def showReqStatus(self):
    try:
      if (self.fields.index('request.id')):
        query = (__GET_REQ_STATUS__ % self.fields.get('request.id'))
        (numrows, rowdesc, res) = self.queryDB(query)
        if (len(res)>0):
          print res[0][0]
      else:
        query = (__GET_REQ_STATUS_REL__ % self.fields.get('release_stat.name'))
        (numrows, rowdesc, res) = self.queryDB(query)
        for resdata in res:
          print resdata[0]
    except:
      raise

  def getFieldData(self,tables=None):
    fielddata = {}
    for table in tables:
      query = "SELECT field_name,field_query,show_conf,format,fregexp,token,field_nullfk FROM field_descriptions WHERE table_name='%s'" % table
      (numrows, rowdesc, res) = self.queryDB(query)
      for row in res:
        if ("." in table): fieldname = "%s.%s" % (table,row[0])
        else:              fieldname = row[0]
        fielddata[fieldname] = { "query": row[1], "show_conf": row[2], "format": row[3], "fregexp": row[4], "token": row[5], "null": row[6] }
    if (self.debug): print fielddata
    return fielddata

  def showTaskTokens(self):
    (numrows, rowdesc, res) = self.queryDB(__SHOW_TASK_TOKENS__)
    for row in res: print "%s : %s" % (row[0],row[1])
    return

  def showParserTokens(self):
    (numrows, rowdesc, res) = self.queryDB(__SHOW_PARSER_TOKENS__)
    for row in res: print "@%s@" % (row[0])
    return

  def showActiveNs(self):
    (numrows, rowdesc, res) = self.queryDB(__SHOW_ACTIVE_WMPROXY__)
    for row in res: print "%s" % (row[0])
    return

  def readDB(self,body='',filter=__FILTER_RELEASE__,groupby='',orderby=__ORDER_RELEASE__,tables=[],extquery=None,extkey=None,cache=None):
    if (cache == None): cache = self.cache
    fielddata = None
    if (tables): fielddata = self.getFieldData(tables)
    if (fielddata):
      for field in fielddata.keys():
        if (fielddata[field]['query']): self.selectionFields += ", (%s) AS %s" % (fielddata[field]['query'],field)
    if (len(body) == 0):
      body = (__QUERY_RELEASE__ % self.selectionFields)
    else:
      body = (body % self.selectionFields)
    #if (len(filter) == 0):
    #  filter = __FILTER_RELEASE__
    #if (len(orderby) == 0):
    #  orderby = __ORDER_RELEASE__
    for field in self.fields.getall():
      if (len(filter) == 0):
        filter += ' WHERE '
      else:
        filter += ' AND '
      if (field[1] == "NULL"):
        filter += ('%s is NULL' % field[0])
      elif (field[1] == "NOTNULL"):
        filter += ('%s is not NULL' % field[0])
      else:
        valstr = "%s" % field[1]
        quote = False
        if (valstr[0]  == "'" or valstr[-1] == "'"): quote = True
        if (valstr[0]  == "'"): valstr = valstr[1:]
        if (valstr[-1] == "'"): valstr = valstr[:-1]
        valstrindx = 0
        for val in valstr.split(','):
          valstrindx += 1
          if (valstrindx > 1): filter += " AND "
          if (len(val) > 0 and val[0] == "!"):
            if (quote): filter += ("%s not like '%s'" % (field[0],val[1:]))
            else:       filter += ("%s not like %s" % (field[0],val[1:]))
          else:
            if (quote): filter += ("%s like '%s'" % (field[0],val))
            else:       filter += ("%s like %s" % (field[0],val))
    if (self.mindate or self.maxdate):
      if (len(filter) == 0): filter += ' WHERE '
      else:                  filter += ' AND '
      if (self.mindate):     filter += __RELEASE_MINDATE__ % self.mindate
      if (self.maxdate):     filter += __RELEASE_MAXDATE__ % self.maxdate
    query = ("%s %s %s %s" % (body, filter, groupby, orderby))
    if (self.debug): print query
    key = None
    resdata = None
    if (cache and self.memcacheClient):
      key = hashlib.md5(query).hexdigest()
      resdata = self.memcacheClient.get(key)
      if (resdata and self.debug): print "Using cached data"
    if (not resdata):
      resdata = self.queryDB(query)
      if (resdata and cache and self.memcacheClient and key):
        self.memcacheClient.set(key, resdata, self.cacheTimeout)
    (numrows, rowdesc, res) = resdata
    if (self.debug): print res

    # Calculate the field max lengths
    flen = []
    if (not self.quiet):
      for field in self.selectionFields.split(","):
        flen.append(len(field))
      for row in res:
        indx = 0
        for field in row:
          if (field):
            fldlen=len(field)
          else:
            fldlen=4
          try:
            if (fldlen > flen[indx]): flen[indx] = fldlen
          except:
            flen.append(fldlen)
          indx += 1
    # Print the report
    if (not self.quiet):
      sep = "-"
      for fnum in flen:
        for i in range(fnum+3):
          sep += "-"
      print sep
      indx = 0
      sys.stdout.write("|")
      for field in self.selectionFields.split(","):
        sys.stdout.write((" %%%ds |" % flen[indx]) % field)
        indx += 1
      sys.stdout.write("\n")
      print sep
    for row in res:
      indx = 0
      if (self.instconf != ''):
        if (len(row)>0):
          try:
            confin  = open(self.conftmpl, 'r')
          except:
            print "Cannot open %s for reading" % self.conftmpl
          if (confin):
            try:
              confout = open(self.instconf, 'w')
            except:
              confin.close()
              print "Cannot open %s for writing" % self.instconf
          if (confout):
            confdata=confin.read()
            tokens = {}
            key = 0
            for rowinfo in rowdesc:
              if (fielddata.has_key(rowinfo[0]) and fielddata[rowinfo[0]]['show_conf'] == 1):
                tokens[fielddata[rowinfo[0]]['token']] = row[key]
              key += 1
            for key in tokens.keys():
              keyword  = ("@%s@" % key)
              try:
                fld = ("%d" % tokens[key])
              except:
                fld = tokens[key]
              if (fld is None): fld=""
              confdata = confdata.replace(keyword, fld.replace('$','\$'))
            confdata = confdata.replace("@VO@", self.vo)
            confdata = confdata.replace("@WMSVOCONF@", self.wmsvoconf)
            confdata = confdata.replace("@WMSCMDCONF@", self.wmscmdconf)
            confout.write(confdata)
            confout.close()
      bdiiconf = {}
      query = None
      if (self.ns and self.lb and self.ld and self.wmproxy and self.myproxy):
        nss = self.ns
        lbs = self.lb
        ld  = self.ld
        wmproxies = self.wmproxy
        myproxy = self.myproxy
      elif (self.bdii):
        query = (__GET_BDII_INFO__ % self.bdii)
      elif (os.environ.has_key('LJSF_DEFBDII')):
        query = (__GET_BDII_INFO__ % os.environ['LJSF_DEFBDII'])
      nss = None
      lbs = None
      ld  = None
      wmproxies = None
      myproxy = None
      if (query):
        (bnumrows, browdesc, bres) = self.queryDB(query)
        nss = bres[0][0]
        lbs = bres[0][1]
        ld  = bres[0][2]
        wmproxies = bres[0][3]
        myproxy   = bres[0][4]
      if (nss):
        bdiiconf['ns'] = ""
        for ns in nss.split(" "):
          if (len(ns)>0):
            if (len(bdiiconf['ns'])>0): bdiiconf['ns'] += ","
            bdiiconf['ns'] += ('"%s"' % ns)
      if (lbs):
        bdiiconf['lb'] = ""
        for lb in lbs.split(" "):
          if (len(lb)>0):
            if (len(bdiiconf['lb'])>0): bdiiconf['lb'] += ","
            bdiiconf['lb'] += ('{"%s"}' % lb)
      if (ld): bdiiconf['ld'] = ('"%s"' % ld)
      if (wmproxies):
        bdiiconf['wmproxy'] = ""
        for wmproxy in wmproxies.split(" "):
          if (len(wmproxy)>0):
            if (len(bdiiconf['wmproxy'])>0): bdiiconf['wmproxy'] += ","
            bdiiconf['wmproxy'] += ('"%s"' % wmproxy)
      if (myproxy): bdiiconf['myproxy'] = ('"%s"' % myproxy)
      if (self.wmsvoconf != ''):
        self.writeConfig(self.wmsvoconftmpl,self.wmsvoconf,bdiiconf,__WMSCONFMAP__)
      if (self.wmscmdconf != ''):
        self.writeConfig(self.wmscmdconftmpl,self.wmscmdconf,bdiiconf,__WMSCONFMAP__)
      if (not self.quiet): sys.stdout.write("|")
      outdata = []
      if (not self.quiet): sep = '|'
      else:                sep = ','
      indx = 0
      field_values = []
      extkey_value = None
      for field in row:
        if (self.quiet): flen.append(0)
        if (not field):
          if (fielddata and fielddata.has_key(rowdesc[indx][0]) and fielddata[rowdesc[indx][0]]["null"] == 0):
            field='%UNDEFINED_'+rowdesc[indx][0].upper()
          else:
            field=''
        try:
          field_values.append((flen[indx],rowdesc[indx][0],field,fielddata[rowdesc[indx][0]]['fregexp'],fielddata[rowdesc[indx][0]]['format']))
          if (extquery and extkey and rowdesc[indx][0] == extkey): extkey_value = field
        except:
          field_values.append((flen[indx],rowdesc[indx][0],field,None,None))
        indx += 1

      # Extensions
      if (extkey_value):
        extq = extquery % extkey_value
        if (self.debug): print extq
        (numrows_ext, rowdesc_ext, res_ext) = self.queryDB(extq)
        if (self.debug): print res_ext
        for row_ext in res_ext:
          if (row_ext[1] == 1):
            if (row_ext[4]):
              field=row_ext[4]
            else:
              if (row_ext[5] == 1):
                if (row_ext[6]): field=row_ext[6]
                else:            field=''
              else:
                if (row_ext[6]): field=row_ext[6]
                else:            field='%UNDEFINED_'+row_ext[3].upper()
            field_values.append((0,row_ext[2],field,row_ext[8],row_ext[7]))

      # Token replacements
      for field in field_values:
        if (fielddata and fielddata.has_key(field[1])):
          token = "@%s@" % fielddata[field[1]]['token']
          for indx in range(0,len(field_values)):
            if (type(field_values[indx][2]) == type('') and token in field_values[indx][2]):
              try:
                field_values[indx]=(field_values[indx][0],field_values[indx][1],field_values[indx][2].replace(token,field[2]),field_values[indx][3],field_values[indx][4])
              except:
                pass
            if (type(field_values[indx][4]) == type('') and token in field_values[indx][4]):
              try:
                field_values[indx]=(field_values[indx][0],field_values[indx][1],field_values[indx][2],field_values[indx][3],field_values[indx][4].replace(token,field[2]))
              except:
                pass

      # Regexps
      for indx in range(0,len(field_values)):
        if (type(field_values[indx][2]) == type('') and field_values[indx][3]):
          pat = re.compile("/([^/|(\/)]*)/([^/|(\/)]*)/")
          (p,r) = field_values[indx][3].split("^")
          field_values[indx]=(field_values[indx][0],field_values[indx][1],re.sub(p,r,field_values[indx][2]),field_values[indx][3],field_values[indx][4])

      # Formats
      for indx in range(0,len(field_values)):
        if (field_values[indx][4]):
          if (field_values[indx][2]):
            if (field_values[indx][2].lower() == "no"):
              field_values[indx]=(field_values[indx][0],field_values[indx][1],'',field_values[indx][3],field_values[indx][4])
            else:
              try:
                formatstr = field_values[indx][4] % field_values[indx][2]
                field_values[indx]=(field_values[indx][0],field_values[indx][1],formatstr,field_values[indx][3],field_values[indx][4])
              except:
                field_values[indx]=(field_values[indx][0],field_values[indx][1],field_values[indx][4],field_values[indx][3],field_values[indx][4])

      indx = 0
      self.tokenData = []
      for field in field_values:
        if (self.debug): print field
        if (not self.quiet):
          __FORMAT__ = (' %%%ds ' % field[0])
        elif (self.showtokens):
          if (fielddata.has_key(field[1]) and fielddata[field[1]]['show_conf'] == 1):
            self.tokenData.append(("@%s@" % fielddata[field[1]]['token'],"%s" % field[2]))
            if (self.genparser):
              __FORMAT__ = ('s#@%s@#%%s#g' % fielddata[field[1]]['token'])
            else:
              __FORMAT__ = ('"%s=%%s"' % fielddata[field[1]]['token'])
          else:
            __FORMAT__ = None
        else:
          __FORMAT__ = ('"%s"')
        if (__FORMAT__): outdata.append(__FORMAT__ % field[2])
        indx += 1
      if (self.genparser):
        if (not self.noout):
          for str in outdata: print str
      else:
        if (self.quiet):
          if (not self.noout): print string.join(outdata,sep)
        else:
          if (not self.noout): print string.join(outdata,sep)+sep

    if (not self.quiet):
      sep = "-"
      for fnum in flen:
        for i in range(fnum+3):
          sep += "-"
      print sep
      print "%d records selected" % len(res)
    if (len(res) > 0):
      return 0
    else:
      return 10

  def writeConfig(self,tmpl,conf,bdiiconf,map):
    confin  = open(tmpl, 'r')
    if (confin):
      confout = open(conf, 'w')
      if (confout):
        confdata=confin.read()
        for key in map.keys():
          keyword  = ("@%s@" % key)
          if (bdiiconf.has_key(map[key])):
            confdata = confdata.replace(keyword, bdiiconf[map[key]].replace('$','\$'))
        if (self.vo): confdata = confdata.replace("@VO@", self.vo)
        confout.write(confdata)
        confout.close()
      else:
        print "Cannot open %s for output" % conf
      confin.close()
    else:
      print "Cannot open %s for input" % tmpl

  def defineRelease(self):
    # Defaults
    if (not self.fields.index('date')):
      self.fields.add('date',strftime("'%Y-%m-%d %H:%M:%S'", gmtime()))
    rtime = self.fields.get('date')
    # Check if the release already exists
    rname=self.fields.get('name')
    (numrows, rowdesc, res) = self.queryDB(__CHECK_RELEASE__ % rname)
    if (len(res) == 0):
      definition=""
      for field in self.fields.getall():
        if (definition): definition += ","
        definition += " %s=%s" % (field[0], field[1])
      query = __DEFINE_RELEASE__ % definition
      self.queryDB(query, True)
    else:
      print "The release %s is already defined" % rname
      return 150

  def setAlias(self):
    # Set the site alias
    if (     self.fields.index('site.alias')
        and (self.fields.index('site.name') or self.fields.index('site.cename'))):
      if (self.fields.index('site.name')):
        query = (__SET_ALIAS_SITENAME__ % (self.fields.get('site.alias'),self.fields.get('site.name')))
      else:
        query = (__SET_ALIAS_CENAME__ % (self.fields.get('site.alias'),self.fields.get('site.cename')))
      try:
        (numrows, rowdesc, res) = self.queryDB(query, True)
      except:
        print "Cannot set the alias"
        sys.exit(160)

  def showAlias(self):
    # Show the site alias
    if (self.fields.index('site.name') or self.fields.index('site.cename')):
      if (self.fields.index('site.name')):
        query = (__SHOW_ALIAS_SITENAME__ % self.fields.get('site.name'))
      else:
        query = (__SHOW_ALIAS_CENAME__ % self.fields.get('site.cename'))
      try:
        if (self.debug): print query
        (numrows, rowdesc, res) = self.queryDB(query)
        rows = len(res)
        if (rows>0):
          for r in res:
            if (rows > 1):
              print "%s: %s" % (r[1],r[0])
            else:
              print r[0]
      except:
        print "Cannot list the alias"
        raise


  def showAttrs(self):
    # Show the site attributes
    if (self.fields.index('site.name') or self.fields.index('site.cename')):
      if (self.fields.index('site.name')):
        query = (__SHOW_ATTRS_SITENAME__ % self.fields.get('site.name'))
      else:
        query = (__SHOW_ATTRS_CENAME__ % self.fields.get('site.cename'))
      try:
        if (self.debug): print query
        (numrows, rowdesc, res) = self.queryDB(query)
        rows = len(res)
        if (rows>0):
          for r in res:
            if (rows > 1):
              print "%s: %s" % (r[1],r[0])
            else:
              print r[0]
      except:
        print "Cannot show the site attributes"
        raise


  def setFS(self):
    # Set the site fs type
    if (     self.fields.index('site.fstype')
        and (self.fields.index('site.name') or self.fields.index('site.cename'))):
      if (self.fields.index('site.name')):
        query = (__SET_FS_SITENAME__ % (self.fields.get('site.fstype'),self.fields.get('site.name')))
      else:
        query = (__SET_FS_CENAME__ % (self.fields.get('site.fstype'),self.fields.get('site.cename')))
      try:
        (numrows, rowdesc, res) = self.queryDB(query, True)
      except:
        print "Cannot set the fs type"
        sys.exit(160)


  def showFS(self):
    # Show the site fs type
    if (self.fields.index('site.name') or self.fields.index('site.cename')):
      if (self.fields.index('site.name')):
        query = (__SHOW_FS_SITENAME__ % self.fields.get('site.name'))
      else:
        query = (__SHOW_FS_CENAME__ % self.fields.get('site.cename'))
      try:
        if (self.debug): print query
        (numrows, rowdesc, res) = self.queryDB(query)
        rows = len(res)
        if (rows>0):
          for r in res:
            if (rows > 1):
              print "%s: %s" % (r[1],r[0])
            else:
              print r[0]
      except:
        print "Cannot show the fs type"
        raise


  def showTask(self):
    # Show the task definition
    if (self.fields.index('task.name')):
      query = (__SHOW_TASK__ % self.fields.get('task.name'))
      try:
        (numrows, rowdesc, res) = self.queryDB(query)
        rows = len(res)
        if (rows>0):
          for r in res:
            print "%s,%s,%s" % (r[0],r[1],r[2])
      except:
        print "Cannot show the task definition"
        raise


  def showRelArch(self):
    # Show the release architecture definition
    if (self.fields.index('release_arch.description')):
      query = (__SHOW_RELARCH__ % self.fields.get('release_arch.description'))
      try:
        (numrows, rowdesc, res) = self.queryDB(query)
        rows = len(res)
        if (rows>0):
          for r in res:
            print "%s,%s,%s,%s,%s,%s" % (r[0],r[1],r[2],r[3],r[4],r[5])
      except:
        print "Cannot show the release arch definition"
        raise


  def showRelTypeDef(self):
    # Show the release type definition
    if (self.fields.index('release_type.description')):
      query = (__SHOW_RELTYPEDEF__ % self.fields.get('release_type.description'))
      try:
        (numrows, rowdesc, res) = self.queryDB(query)
        rows = len(res)
        if (rows>0):
          for r in res:
            print "%s,%s,%s" % (r[0],r[1],r[2])
      except:
        print "Cannot show the release type definition"
        raise


  def queryDB(self, query, commit=False):
    # Get the db type to be used
    if (query.startswith("SELECT") or query.startswith("select")):
      dbtype = "r"
    else:
      dbtype = "w"

    # Open the DB
    if (dbtype == "r"):
      if (not self.dbr): self.openDB(dbtype)
    else:
      if (not self.dbw): self.openDB(dbtype)

    try:
      # Query the DB
      cursor = self.db.cursor()
      cursor.execute(query)
    except MySQLdb.OperationalError, e:
      self.openDB(dbtype)
      # Query the DB
      cursor = self.db.cursor()
      cursor.execute(query)

    numrows = int(cursor.rowcount)
    desc = cursor.description
    if (commit): self.db.commit()
    return (numrows, desc, cursor.fetchall())
    

# main class
if __name__ == '__main__':
    short_options = ""
    long_options = ["dbhost=", "dbname=", "dbuser=", "dbpass=", "show-db-version",
                    "arch=", "cache", "cache-timeout=", "comments=", "create", "cename=",
                    "cs=", "debug", "ctime=", "help", "create-conf=","jdlfile=", "jdlname=",
                    "jdltype=", "jobid=", "list-tags", "gen-parser",
                    "add-autoinstall-target=", "del-autoinstall-target=",
                    "list-autoinstall-targets", "autoinstall-target=",
                    "has-cvmfs", "no-cvmfs", "cvmfs-available", "cvmfs-unavailable",
                    "list-ce", "list-resource", "list-site",
                    "after=", "before=", "min-proxy-lt=", "obsolete",
                    "osname=", "osrelease=", "osversion=", "grid-name=", "facility=",
                    "production", "queryrel=", "querysite=", "quiet", "noout",
                    "remove-lock", "rel=", "base", "patch", "definerel=",
                    "select=", "set-reltype=", "show-reltype", "set-lock", "show-fake-locks",
                    "fix-wrong-requests", "reltag=", "set-relstatus=", "show-relstatus",
                    "set-alias=", "show-alias", "set-reltag=", "show-reltag", "show-relname",
                    "set-attrs=", "show-attrs", "set-fs=", "show-fs",
                    "reqid=", "set-reqstatus=", "show-reqstatus",
                    "set-autoinstall=", "unset-autoinstall", "show-autoinstall",
                    "set-siteinfo", "set-sitestatus=", "show-sitestatus",
                    "show-rel-subscriptions", "site-enabled", "site-disabled",
                    "set-tags=", "show-lock", "atlas-sitename=", "sitename=", "sitetype=", "status=",
                    "show-task=", "show-task-tokens", "show-parser-tokens", "show-relarch=",
                    "show-reltypedef=", "autoinstall", "tag=", "user=", "orphaned",
                    "bdii=", "create-wmsvoconf=", "create-wmscmdconf=",
                    "wmsvoconf-template=", "wmscmdconf-template=", "vo=",
                    "ns=", "lb=", "ld=", "wmproxy=", "myproxy=", "show-active-wmproxy",
                    "free", "pinned", "tier-level=" ]

    ljsf=ljsfInfo()
    try:
      opts, args = getopt.getopt(sys.argv[1:],
                   short_options,
                   long_options,
                   )
    except getopt.GetoptError:
      # Print the help
      print HELP % (__version__.strip(),ljsf.wmsvoconftmpl,ljsf.wmscmdconftmpl)
      sys.exit(-1)

    # Local vars
    cmd=''
    arg=''

    for cmd, arg in opts:
      if cmd in ('--help',):
        print HELP % (__version__.strip(),ljsf.wmsvoconftmpl,ljsf.wmscmdconftmpl)
        sys.exit()
      elif cmd in ('--dbhost',):
        ljsf.dbhost = arg
      elif cmd in ('--dbname',):
        ljsf.dbname = arg
      elif cmd in ('--dbuser',):
        ljsf.dbuser = arg
      elif cmd in ('--dbpass',):
        ljsf.dbpass = arg
      elif cmd in ('--show-db-version',):
        ljsf.mode = "show-db-version"
      elif cmd in ('--arch',):
        ljsf.setArch(arg)
      elif cmd in ('--bdii',):
        ljsf.setInfosys(arg)
      elif cmd in ('--cache',):
        ljsf.setCache(True)
      elif cmd in ('--cache-timeout',):
        ljsf.setCacheTimeout(arg)
      elif cmd in ('--cename',):
        ljsf.setResource(arg)
      elif cmd in ('--comments',):
        ljsf.setComments(arg)
      elif cmd in ('--cs',):
        ljsf.setCS(arg)
      elif cmd in ('--create',):
        ljsf.mode='insert'
      elif cmd in ('--ctime',):
        ljsf.setCTime(arg)
      elif cmd in ('--create-conf',):
        ljsf.setInstconf(arg)
      elif cmd in ('--gen-parser',):
        ljsf.setGenparser(True)
      elif cmd in ('--create-wmsvoconf',):
        ljsf.setWMSVOconf(arg)
      elif cmd in ('--create-wmscmdconf',):
        ljsf.setWMSCMDconf(arg)
      elif cmd in ('--debug',):
        ljsf.setDebug(True)
      elif cmd in ('--definerel',):
        ljsf.mode='definerel'
        ljsf.setReleaseParams(arg)
      elif cmd in ('--jdlname',):
        ljsf.setJdlName(arg)
      elif cmd in ('--jdltype',):
        ljsf.setJdlType(arg)
      elif cmd in ('--jdlfile',):
        ljsf.setJdlFile(arg)
      elif cmd in ('--jobid',):
        ljsf.setJobID(arg)
      elif cmd in ('--after',):
        ljsf.setMinDate(arg)
      elif cmd in ('--before',):
        ljsf.setMaxDate(arg)
      elif cmd in ('--list-ce',):
        ljsf.mode='list-resource'
        ljsf.selectionFields = "site.cename"
      elif cmd in ('--list-resource',):
        ljsf.mode='list-resource'
        ljsf.selectionFields = "site.cs"
      elif cmd in ('--list-site',):
        ljsf.mode='list-resource'
        ljsf.selectionFields = "site.name"
      elif cmd in ('--list-tags',):
        ljsf.mode = "list-tags"
      elif cmd in ('--min-proxy-lt',):
        ljsf.setMinProxyLT(arg)
      elif cmd in ('--obsolete',):
        ljsf.setObsolete("1")
      elif cmd in ('--orphaned',):
        ljsf.mode='query-orphaned'
      elif cmd in ('--osname',):
        ljsf.setOSName(arg)
      elif cmd in ('--osrelease',):
        ljsf.setOSRelease(arg)
      elif cmd in ('--osversion',):
        ljsf.setOSVersion(arg)
      elif cmd in ('--grid-name',):
        ljsf.setGridName(arg)
      elif cmd in ('--facility',):
        ljsf.setFacility(arg)
      elif cmd in ('--production',):
        ljsf.setObsolete("0")
      elif cmd in ('--autoinstall',):
        ljsf.setAutoinstallFlag("1")
      elif cmd in ('--list-autoinstall-targets',):
        ljsf.mode='list-ai-targets'
      elif cmd in ('--autoinstall-target',):
        ljsf.setAutoinstallTarget(arg)
      elif cmd in ('--base',):
        ljsf.setBaseRelease(arg)
      elif cmd in ('--patch',):
        ljsf.setPatchRelease(arg)
      elif cmd in ('--quiet',):
        ljsf.setQuiet(True)
      elif cmd in ('--noout',):
        ljsf.setNoout(True)
      elif cmd in ('--rel',):
        ljsf.setRelease(arg)
      elif cmd in ('--reqid',):
        ljsf.setRequest(arg)
      elif cmd in ('--remove-lock',):
        ljsf.mode='remove-lock'
      elif cmd in ('--atlas-sitename',):
        ljsf.setAtlasSitename(arg)
      elif cmd in ('--sitename',):
        ljsf.setSitename(arg)
      elif cmd in ('--sitetype',):
        ljsf.setSitetype(arg)
      elif cmd in ('--select',):
        ljsf.mode='select'
        if (arg != 'all'): ljsf.selectionFields=arg
      elif cmd in ('--set-alias',):
        ljsf.mode = "set-alias"
        ljsf.setAliasValue(arg)
      elif cmd in ('--set-fs',):
        ljsf.mode = "set-fs"
        ljsf.setFSType(arg)
      elif cmd in ('--set-tags',):
        ljsf.mode = "set-tags"
        ljsf.setSiteTags(arg)
      elif cmd in ('--reltag',):
        ljsf.setReleaseTags(arg)
      elif cmd in ('--set-reltype',):
        ljsf.mode = "set-reltype"
        ljsf.setReleaseType(arg)
      elif cmd in ('--set-relstatus',):
        ljsf.mode = "set-relstatus"
        if (ljsf.setReleaseStatus(arg) != 0): sys.exit(1)
      elif cmd in ('--show-alias',):
        ljsf.mode = "show-alias"
      elif cmd in ('--show-attrs',):
        ljsf.mode = "show-attrs"
      elif cmd in ('--show-fs',):
        ljsf.mode = "show-fs"
      elif cmd in ('--show-relstatus',):
        ljsf.mode = "show-relstatus"
      elif cmd in ('--set-reltag',):
        ljsf.mode = "set-reltag"
        ljsf.setReleaseTags(arg)
      elif cmd in ('--show-reltag',):
        ljsf.mode = "show-reltag"
      elif cmd in ('--show-relname',):
        ljsf.mode = "show-relname"
      elif cmd in ('--set-reqstatus',):
        ljsf.mode = "set-reqstatus"
        ljsf.setRequestStatus(arg)
      elif cmd in ('--show-reqstatus',):
        ljsf.mode = "show-reqstatus"
      elif cmd in ('--set-autoinstall',):
        ljsf.mode = "set-autoinstall"
        ljsf.setAutoinstallFlag("(SELECT ref FROM autoinstall_target WHERE name='%s')" % arg)
      elif cmd in ('--unset-autoinstall',):
        ljsf.mode = "set-autoinstall"
        ljsf.setAutoinstallFlag("0")
      elif cmd in ('--show-autoinstall',):
        ljsf.mode = "show-autoinstall"
      elif cmd in ('--set-siteinfo',):
        ljsf.mode = "set-siteinfo"
      elif cmd in ('--set-sitestatus',):
        ljsf.mode = "set-sitestatus"
        if (ljsf.setSiteStatusFlag(arg) != 0): sys.exit(-1)
      elif cmd in ('--show-sitestatus',):
        ljsf.mode = "show-sitestatus"
      elif cmd in ('--show-rel-subscriptions',):
        ljsf.mode = "show-rel-subscriptions"
      elif cmd in ('--site-enabled',):
        ljsf.setSiteEnabled(1)
      elif cmd in ('--site-disabled',):
        ljsf.setSiteEnabled(0)
      elif cmd in ('--has-cvmfs',):
        ljsf.setFSType("cvmfs")
      elif cmd in ('--no-cvmfs',):
        ljsf.setFSType("!cvmfs")
      elif cmd in ('--cvmfs-available',):
        ljsf.setCVMFSAvailable(1)
      elif cmd in ('--cvmfs-unavailable',):
        ljsf.setCVMFSAvailable(0)
      elif cmd in ('--show-relstatus',):
        ljsf.mode = "show-relstatus"
      elif cmd in ('--show-reltype',):
        ljsf.mode = "show-reltype"
      elif cmd in ('--queryrel',):
        ljsf.mode='queryrel'
        ljsf.setReleaseName(arg)
      elif cmd in ('--querysite',):
        ljsf.mode='querysite'
        ljsf.setQuerySitename(arg)
      elif cmd in ('--show-task',):
        ljsf.mode='show-task'
        ljsf.setTaskName(arg)
      elif cmd in ('--show-task-tokens',):
        ljsf.mode='show-task-tokens'
      elif cmd in ('--show-parser-tokens',):
        ljsf.mode='show-parser-tokens'
      elif cmd in ('--show-relarch',):
        ljsf.mode='show-relarch'
        ljsf.setReleaseArch(arg)
      elif cmd in ('--show-reltypedef',):
        ljsf.mode='show-reltypedef'
        ljsf.setReleaseType(arg)
      elif cmd in ('--set-lock',):
        ljsf.mode='set-lock'
      elif cmd in ('--show-lock',):
        ljsf.mode='show-lock'
      elif cmd in ('--show-fake-locks',):
        ljsf.mode='show-fake-locks'
      elif cmd in ('--fix-wrong-requests',):
        ljsf.mode='fix-wrong-requests'
      elif cmd in ('--status',):
        ljsf.setReleaseStatStatus(arg)
      elif cmd in ('--tag',):
        ljsf.setReleaseStatTag(arg)
      elif cmd in ('--user',):
        ljsf.setUser(arg)
      elif cmd in ('--free',):
        ljsf.setReleaseStatPin("0")
      elif cmd in ('--pinned',):
        ljsf.setReleaseStatPin("1")
      elif cmd in ('--vo',):
        ljsf.setVOName(arg)
      elif cmd in ('--ns',):
        ljsf.setNS(arg)
      elif cmd in ('--lb',):
        ljsf.setLB(arg)
      elif cmd in ('--ld',):
        ljsf.setLD(arg)
      elif cmd in ('--wmproxy',):
        ljsf.setWMProxy(arg)
      elif cmd in ('--myproxy',):
        ljsf.setMyProxy(arg)
      elif cmd in ('--show-active-wmproxy',):
        ljsf.mode = "show-active-wmproxy"
      elif cmd in ('--tier-level',):
        ljsf.setTierLevel(arg)

    if (not ljsf.fields.index('site.atlas_name') and ljsf.fields.index('site.name')):
      ljsf.setAtlasSitename(ljsf.fields.get('site.name'))
    if ((ljsf.mode=='insert' or ljsf.mode=='update') and not
        (ljsf.fields.index('site.cs') and ljsf.fields.index('release_stat.name'))):
      print "No --cs and --rel options specified in insert or update mode."
      sys.exit(-1)
    if (ljsf.mode=='set-lock' and not ljsf.fields.index('jdl.name')):
      print "No --jdlname specified in set-lock operation"
      sys.exit(10)
    if (ljsf.mode=='remove-lock' and not
        (ljsf.fields.index('jdl.name') or ljsf.fields.index('job.id'))):
      print "No --jdlname or --jobid specified in remove-lock operation"
      sys.exit(11)
    if (ljsf.mode=='show-lock' and not ljsf.fields.index('jdl.name')):
      print "No --jdlname specified in show-lock operation"
      sys.exit(12)
    if (ljsf.mode=='set-tags' and not ljsf.fields.index('site.name')
                              and not ljsf.fields.index('site.cename')):
      print "No --sitename or --cename specified in set-tags operation"
      sys.exit(13)
    if (ljsf.mode=='list-tags' and not ljsf.fields.index('site.name')
                               and not ljsf.fields.index('site.cename')
                               and not ljsf.fields.index('site.cs')):
      print "No --sitename, --cename or --cs specified in list-tags operation"
      sys.exit(13)
    if (       (ljsf.mode=='set-reltype' or ljsf.mode=='show-reltype')
        and not ljsf.fields.index('release_stat.name')):
      print "No --rel specified in set-reltype or show-reltype operation"
      sys.exit(14)
    if (       (ljsf.mode=='set-relstatus' or ljsf.mode=='show-relstatus')
        and not ljsf.fields.index('release_stat.name')):
      print "No --rel specified in set-relstatus or show-relstatus operation"
      sys.exit(15)
    if (       (ljsf.mode=='set-reltag' or ljsf.mode=='show-reltag')
        and not ljsf.fields.index('release_stat.name')):
      print "No --rel specified in set-reltag or show-reltag operation"
      sys.exit(16)
    if (       (ljsf.mode=='set-autoinstall' or ljsf.mode=='show-autoinstall')
        and not ljsf.fields.index('release_stat.name')):
      print "No --rel specified in [un]set-autoinstall or show-autoinstall operation"
      sys.exit(17)
    if (       (ljsf.mode=='set-reqstatus' or ljsf.mode=='show-reqstatus')
       and not (ljsf.fields.index('request.id') or ljsf.fields.index('release_stat.name'))):
      print "No --reqid or --rel specified in set-reqstatus or show-reqstatus operation"
      sys.exit(18)
    if (       (ljsf.mode=='set-sitestatus' or ljsf.mode=='show-sitestatus')
        and not ljsf.fields.index('site.cename') and not ljsf.fields.index('site.cs')):
      print "No --cename or --cs specified in set-sitestatus or show-sitestatus operation"
      sys.exit(19)
    if (ljsf.mode=='definerel' and not ljsf.fields.index('name')):
      print "No 'name' parameter specified in release definition"
      sys.exit(20)
    if ((ljsf.mode=='set-alias' or ljsf.mode=='set-attr' or ljsf.mode=='set-fs' or ljsf.mode=='show-tags')
         and not ljsf.fields.index('site.name') and not ljsf.fields.index('site.cename')):
      print "No --sitename or --cename specified in %s operation" % ljsf.mode
      sys.exit(21)
    if (ljsf.mode=='show-rel-subscriptions' and not ljsf.fields.index('site.name')):
      print "No --sitename specified in show-rel-subscriptions operation"
      sys.exit(22)
    if (ljsf.mode=='show-relname' and not ljsf.fields.index('release_data.tag')):
      print "No --reltag specified in show-relname operation"
      sys.exit(23)
    if ((ljsf.instconf!='' and ljsf.mode!='queryrel')):
      print "You asked for a release configuration without any --queryrel option."
      sys.exit(-1)

    # Check for NULLs
    for field in ljsf.fields.getall():
      if (ljsf.fields.get(field[0]) == "'NULL'"): ljsf.fields.add(field[0],"NULL")

    # Execute the task
    rc=0
    if (ljsf.mode=='insert' or ljsf.mode=='update') :
      ljsf.writeDB()
    elif (ljsf.mode=='show-db-version'):
      ljsf.showDBVersion()
    elif (ljsf.mode=='show-lock'):
      lockStatus, lockUser = ljsf.showLock()
      if (not lockStatus and not lockUser): sys.exit(1)
    elif (ljsf.mode=='set-lock'):
      rc = ljsf.setLock()
    elif (ljsf.mode=='show-fake-locks'):
      ljsf.showFakeLocks()
    elif (ljsf.mode=='fix-wrong-requests'):
      ljsf.fixWrongRequests()
    elif (ljsf.mode=='remove-lock'):
      rc = ljsf.removeLock()
    elif (ljsf.mode=='list-resource'):
      ljsf.listResource()
    elif (ljsf.mode=='set-tags'):
      ljsf.setTags()
    elif (ljsf.mode=='list-tags'):
      ljsf.listTags()
    elif (ljsf.mode=='set-reltype'):
      ljsf.setRelType()
    elif (ljsf.mode=='show-reltype'):
      ljsf.showRelType()
    elif (ljsf.mode=='set-relstatus'):
      ljsf.setRelStatus()
    elif (ljsf.mode=='show-relstatus'):
      ljsf.showRelStatus()
    elif (ljsf.mode=='set-reltag'):
      ljsf.setRelTag()
    elif (ljsf.mode=='show-reltag'):
      ljsf.showRelTag()
    elif (ljsf.mode=='show-relname'):
      ljsf.showRelName()
    elif (ljsf.mode=='set-reqstatus'):
      ljsf.setReqStatus()
    elif (ljsf.mode=='show-reqstatus'):
      ljsf.showReqStatus()
    elif (ljsf.mode=='set-autoinstall'):
      ljsf.setAutoinstall()
    elif (ljsf.mode=='show-autoinstall'):
      ljsf.showAutoinstall()
    elif (ljsf.mode=='list-ai-targets'):
      ljsf.listAutoinstallTargets()
    elif (ljsf.mode=='set-siteinfo'):
      ljsf.setSiteInfo()
    elif (ljsf.mode=='set-sitestatus'):
      ljsf.setSiteStatus()
    elif (ljsf.mode=='show-sitestatus'):
      ljsf.showSiteStatus()
    elif (ljsf.mode=='show-rel-subscriptions'):
      ljsf.showRelSubscriptions()
    elif (ljsf.mode=='definerel'):
      ljsf.defineRelease()
    elif (ljsf.mode=='set-alias'):
      ljsf.setAlias()
    elif (ljsf.mode=='show-alias'):
      ljsf.showAlias()
    elif (ljsf.mode=='show-attrs'):
      ljsf.showAttrs()
    elif (ljsf.mode=='set-fs'):
      ljsf.setFS()
    elif (ljsf.mode=='show-fs'):
      ljsf.showFS()
    elif (ljsf.mode=='show-task'):
      ljsf.showTask()
    elif (ljsf.mode=='show-task-tokens'):
      ljsf.showTaskTokens()
    elif (ljsf.mode=='show-parser-tokens'):
      ljsf.showParserTokens()
    elif (ljsf.mode=='show-relarch'):
      ljsf.showRelArch()
    elif (ljsf.mode=='show-reltypedef'):
      ljsf.showRelTypeDef()
    elif (ljsf.mode=='query-orphaned'):
      qryfilter = __FILTER_RELEASE__ + " AND release_stat.name <> 'ALL' AND (SELECT COUNT(*) FROM request WHERE request.relfk=release_stat.ref)=0"
      rc = ljsf.readDB(filter=qryfilter)
    elif (ljsf.mode=='queryrel'):
      rc = ljsf.queryRel()
    elif (ljsf.mode=='querysite'):
      rc = ljsf.querySite()
    elif (ljsf.mode=='show-active-wmproxy'):
      ljsf.showActiveNs()
    else:
      rc=ljsf.readDB()
    sys.exit(rc)

    ljsf.main()
