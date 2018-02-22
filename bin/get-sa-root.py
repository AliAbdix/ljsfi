#!/usr/bin/env python

import sys
import ldap

if __name__ == '__main__':
    dpmSE = sys.argv[1]
    l=ldap.open("atlas-bdii.cern.ch",2170)
    baseDN = "mds-vo-name=local,o=grid"
    searchScope = ldap.SCOPE_SUBTREE
    gluSEID='GlueSEUniqueID='+dpmSE
    print gluSEID
    result = l.search_s(baseDN, searchScope, "(&(objectClass=GlueSATop)(GlueChunkKey="+gluSEID+")(GlueSALocalID=atlas))",["GlueSARoot"])
    SARoot = result[0][1]['GlueSARoot'][0]
    vospec,GlSARoot = SARoot.split(':/')
    print "%s" % GlSARoot

