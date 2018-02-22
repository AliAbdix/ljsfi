#!/bin/sh

search () {
  BDII=$1
  CE=$2
#  ldapsearch -s sub -x -h $BDII -p 2170 -b "mds-vo-name=local,o=grid" "(|(&(objectClass=GlueClusterTop)(GlueChunkKey=GlueClusterUniqueID=$CE))(&(objectClass=GlueSite)(GlueForeignKey=GlueClusterUniqueID=$CE)))" GlueSiteName GlueClusterUniqueID GlueHostOperatingSystemName GlueHostOperatingSystemRelease GlueHostOperatingSystemVersion
  ldapsearch -s sub -x -h $BDII -p 2170 -b "mds-vo-name=local,o=grid" "(|(&(objectClass=GlueClusterTop)(GlueChunkKey=GlueClusterUniqueID=$CE))(&(objectClass=GlueKey)(GlueClusterUniqueID=$CE)))" GlueSiteName GlueClusterUniqueID GlueHostOperatingSystemName GlueHostOperatingSystemRelease GlueHostOperatingSystemVersion GlueForeignKey | grep -v GlueCEUniqueID | sed 's#GlueForeignKey: GlueSiteUniqueID=#GlueSiteName: #' | sort | uniq
  #ldapsearch -s sub -x -h $BDII -p 2170 -b "mds-vo-name=local,o=grid" "(|(&(objectClass=GlueClusterTop)(GlueChunkKey=GlueClusterUniqueID=$CE))(&(objectClass=GlueKey)(GlueClusterUniqueID=$CE)))" GlueClusterUniqueID GlueHostOperatingSystemName GlueHostOperatingSystemRelease GlueHostOperatingSystemVersion GlueForeignKey | grep -v GlueCEUniqueID | sed 's#dn: GlueClusterUniqueID=\(.*\),mds-vo-name=\(.*\)\,mds-vo-name=\(.*\)#GlueSiteName: \2#' | sed 's#GlueForeignKey: GlueSiteUniqueID=#GlueSiteName: #' | sort | uniq
}

source $CONFPATH/install.conf

search $LCG2_BDII $1 | grep -i ^Glue

exit
