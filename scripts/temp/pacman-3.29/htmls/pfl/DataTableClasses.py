#python 2.4

#
#--- classes
#

class DataTable:
	#like a database table; rows are internally tuples, and table is internally list of rows
	#	stress internally, because __getitem__ depends on returnAs (see below)
	#maintains an internal order
	#for any method that gets an individual row, like indexing and iteration (which are both implemented), it will be returned as either a tuple or a dictionary, based on the returnAs parameter, and always decided internally with dictORtup (default is dictionary)
	#	if it's a tuple ...
	#		it's the internal tuple, in the order of colnames
	#	if it's a dictionary
	#		the tuple is copied to a dictionary, keyed by colnames
	#fields can be objects (so be careful, the tuples themselves aren't mutable, but they may contain references to other objects)
	#typical usage
	#	rs = DataTable('name', 'address', 'phone')
	#	rs.populate(<some iterator that returns tuples of len 3>)
	#	firstname = rs[0]['name']	#rs[0][0] if returnAs=='tup'
	#	...
	def __init__(self, colnames, returnAs='dict'):
		self.colnames = colnames		#tuple of strings of column names
		if returnAs not in ('dict', 'tup'):
			assert 0, 'unsupported DataTable returnAs method; needs to be \'dict\' or \'tup\''
		self.returnAs = returnAs		#whether to return rows as tuples or dictionaries
		self.rows = []				#the data table: a list of tuples
	def __getitem__(self, i):
		return self.dictORtup(self.rows[i])
	def __len__(self):
		return len(self.rows)
	def populate(self, iterator, strict=True):
		#iterator must return tuples (my be generalized in the future, especially to handle dictionaries, with keys matching colnames)
		#	simplist is just list of tuples
		#if strict, each tuple is checked to match size and and its contents' types
		#	otherwise assumed, and prone to unpredicatble behavior if not satisfied
		#	doesn't differentiate between different object types
		#none is OK
		for row in iterator:
			if strict:
				if not len(row)==len(self.colnames):
					assert 0, 'incompatible record size for populating DataTable'
				if len(self.rows) > 0:
					i = len(self.colnames) - 1
					while i > 0:
						if not self.rows[0][i] == None and not row[i] == None and not type(self.rows[0][i]) == type(row[i]):
							assert 0, 'incompatible type for populating DataTable'
						i -= 1
			self.rows.append(row)
	def sort(self, colname, comparison=cmp):
		#reorders itself based on comparison function
		#comparison must be two argument fucntion that compares data in colname and returns -1,0,1 (just like cmp)
		def sorter(tup1,tup2):
			return apply(comparison, (tup1[list(self.colnames).index(colname)],tup2[list(self.colnames).index(colname)]))
		self.rows.sort(sorter)
	def select(self, colname, data, comparison = lambda x,y:x==y):
		#returns a new DataTable based on the query
		#	as of now, all the same columns and colnames
		#comparison must be two argument function (first will be data in colname, second will be data as given to compare to) that returns whether or not to include in result set
		if colname not in self.colnames:
			assert 0, 'unknown column name being used in the select comparison function'
		rslist = [row for row in self.rows if apply(comparison, (row[list(self.colnames).index(colname)],data))]
		rs = DataTable(self.colnames)
		rs.populate(rslist)
		return rs
	def printout(self):
		#this is definitely nothing fancy, mainly for debugging
		#note that it prints out the internal tuples, regardless of dictORtup
		print self.colnames
		print '='*50
		for row in self.rows:
			#print self.dictORtup(row)
			print row
	#helper methods
	def dictORtup(self, tup):
		#takes the given tuple (one of self.rows) and converts (if needed) according to returnAs
		if self.returnAs == 'tup':
			return tup
		elif self.returnAs == 'dict':
			retdict = {}
			i=0
			while i < len(self.colnames):
				retdict[self.colnames[i]] = tup[i]
				i += 1
			return retdict


#
#--- fix
#
#BUG: if first insert into DataTable column is None, any types go in after that, even if strict is on

#
#--- todo
#
#change sort(self, colname) to sort(self, *colnames) and to primary, secondary, ... sort
#have select be able to just pick a certain number of columns, instead of having to return them all
#DataTable dict vs tup
#	have populate be able to take tuples or dictionaries, and take either way, regardless of returnAs
#have method to run primary key check
