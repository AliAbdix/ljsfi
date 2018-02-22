#!/usr/bin/env python
import os,string,MySQLdb

hostn="atlas-install.roma1.infn.it"
usern="dbwriter"
userpass="dbwriter"
dbname="atlas_install"
skips=['rel_%', 'DQ2clients%', 'LCG%', 'ALL']
keeppatch=3

db_conf = ("%s/.my.cnf" % os.environ["CONFPATH"])
db = MySQLdb.connect(read_default_file=db_conf,db="atlas_install")

cursor = db.cursor()

query = "SELECT rd.name, rd.sw_name, ra.platform_type, ra.os_type, ra.gcc_ver, ra.mode, rd.date FROM release_data rd, release_arch ra WHERE rd.archfk=ra.ref AND rd.name NOT IN (SELECT DISTINCT(requires) FROM release_data WHERE date > NOW() - INTERVAL 1 YEAR AND requires IS NOT NULL AND obsolete=0) AND (rd.requires IS NULL OR rd.requires NOT IN (SELECT DISTINCT(requires) FROM release_data WHERE date > NOW() - INTERVAL 1 YEAR AND requires IS NOT NULL AND obsolete=0)) AND rd.obsolete=0 AND rd.date < NOW()-INTERVAL 1 YEAR"
for skip in skips:
	query += " AND rd.name NOT LIKE '%s'" % skip
query += " ORDER BY date"
cursor.execute(query)

numrows = int(cursor.rowcount)

print "Inactive releases during the last year (%d):" % numrows
for x in range(0,numrows):
	row = cursor.fetchone()
        name = row[0].split("_")[0].split("-")[0]
	print "%-35s, %-6s, %-6s, gcc %-6s, %-6s [%s]" % (("%s-%s" % (row[1], name)),row[2],row[3],row[4],row[5],row[6])

query = "SELECT rd.name, rd.sw_name, ra.platform_type, ra.os_type, ra.gcc_ver, ra.mode, rd.date, rd.requires FROM release_data rd, release_arch ra WHERE rd.archfk=ra.ref AND rd.obsolete=0 AND rd.requires IS NOT NULL AND rd.date >= NOW()-INTERVAL 1 YEAR"
for skip in skips:
	query += " AND rd.name NOT LIKE '%s'" % skip
query += " ORDER BY date"
cursor.execute(query)

numrows = int(cursor.rowcount)

reldefs = {}
reqs    = []
for x in range(0,numrows):
	row = cursor.fetchone()
        name = "%s-%s" % (row[1], row[0].split("_")[0].split("-")[0])
        relkey = "%s-%s" % (row[1],row[7])
        if (not reldefs.has_key(relkey)): reldefs[relkey] = []
	reldefs[relkey].append("%-35s, %-6s, %-6s, gcc %-6s, %-6s [%s]" % (name, row[2],row[3],row[4],row[5],row[6]))
        req = "'%s'" % row[7]
        if (req not in reqs): reqs.append(req)
rellist = []
for relkey in reldefs.keys():
        indx = 0
        if (len(reldefs[relkey]) > keeppatch):
		indx -= keeppatch
		for rdef in reldefs[relkey][:indx]:
			rellist.append(rdef)
rellist.sort()
print
print "Old patches of active releases during the last year (%s):" % len(rellist)
print
for rel in rellist:
	print rel

rellist = []
for relkey in reldefs.keys():
        indx = 0
        if (len(reldefs[relkey]) > keeppatch): indx -= keeppatch
	for rdef in reldefs[relkey][indx:]:
		rellist.append(rdef)
query = "SELECT rd.name, rd.sw_name, ra.platform_type, ra.os_type, ra.gcc_ver, ra.mode, rd.date FROM release_data rd, release_arch ra WHERE rd.archfk=ra.ref AND rd.name IN (%s)" % string.join(reqs,",")
cursor.execute(query)
numrows = int(cursor.rowcount)
for x in range(0,numrows):
	row = cursor.fetchone()
        name = "%s-%s" % (row[1], row[0].split("_")[0].split("-")[0])
	rellist.append("%-35s, %-6s, %-6s, gcc %-6s, %-6s [%s]" % (name, row[2],row[3],row[4],row[5],row[6]))

rellist.sort()
print
print "Active releases and patches during the last year (%d):" % len(rellist)
print
for rel in rellist:
	print rel
