#!/usr/bin/env python
import MySQLdb

hostn="pc-ads.roma1.infn.it"
usern="dbreader"
userpass="dbreader"
dbname="test"

db = MySQLdb.connect(host=hostn, user=usern, passwd=userpass,db=dbname)

cursor = db.cursor()

cursor.execute("SELECT * FROM test")

numrows = int(cursor.rowcount)

for x in range(0,numrows):
	row = cursor.fetchone()
	print row
