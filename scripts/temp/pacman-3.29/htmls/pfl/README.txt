pacmanFunctionLister.py README
==============================
basic organization
	theory
		functions belong to groups (as organized in paragraphs on webpages)
		groups belong to categories (as organized by separate webpages)
		functions with different parameters are considered different functions
			because some, like setenv(env, val) and setenv(), are in different groups, so it seems necessary
	practice
		for each category, there should be a file in the definitions directory (def/) that has all of the information about the category and the groups and functions of the category
			see "definition file format" below
		pacmanFunctionLister can read these files, reorganize the data, and format output
			see "usage" below
			all the definition files are always processed, even if just making the page for one category
		html formatting is accomplished through definitions in html_template.py
usage
	python pacmanFunctionLister.py <category> <output_style>
		category
			the category to print
			there must be a definition file defining that category (but the file doesn't have to be named the same as the category)
			special directives
				_index_
					if the category is entered as _index_, the special index page (see below) is output
				_all_
					if the category is entered as _all_, for each category in the def directory, a style-formatted output file is created in the output directory, named according to the category keyName (see below), and the index page is also created
		output_style
			text
				no special formatting, just newlines and tabs
			html
				html formatting
		except for when category is entered as _all_, output is sent to stdout, so redirect to save as a file
		default behavior
			if no arguments are given, "_all_ html" is assumed
	files to maintain
		definition files in def/ directory, for all the function data
			see definition file format below
		html_template.py, for all the html to use
			this is the html that's put around the data when outputing html formattated pages
			variable names are supposed to be self explanatory
		convertHTMLtoText in TextProcessors.py
			certain things in the definition files can contain html; these are the substitutions that are made when those things are converted to plain text
		hardcoded parameters in pacmanFunctionLister.py
			such as the names of the directories and output files etc
	warning
		when writing files, previous versions are overwritten without notice
files
	def/
		directory where the definition files are to be kept
	output/
		directory for output files
	tmp/
		used for temporary files made by pacmanFunctionLister
		created and deleted on the fly, unless the directory already exists, in which case it's left behind, but any filenames matching pacmanFunctionLister's internal files will be overwritten
	DataTableClasses.py
		generic implementation of a database result set type of object, with some basic select and sort methods
	FncnClasses.py
		definitions of the function, group, and category classes
		some related classes for input into DataTables
		some helper methods for related things
	README.txt
		this file
	TextProcessors.py
		methods for testing and processing text, including the convertHTMLtoText processing
	html_template.py
		definitions for formatting html output
	pacmanFunctionLister.py
		the main program
	(for any file see the comments for notes on bugs and future things to do, and for more specific documentation)
terminology
	index
		the page that lists all the functions in alphabetical order and, if html formatted, links to anchors in the category pages
	definition files
		the files with all the category, group, and function definitions, maintained in the def/ directory
		one for each category
		see format instructions below
	keyName
		primary key; a one word text, alphanumeric, nickname
		category keyName is the main identifier of the categories
			specified in the first line of the category definition file
			shouldn't really be changed, because:
				html_template.html_individual_... stuff is hardcoded according to current category keyNames
				note that when the category files are automatically made (see _all_ in usage above), they're named according to the keyName as given in the definition files, and the index page links to these pages
		group keyname is completely internal
		functions have no explicit keyName, and therefore no primary key
			but fncnName plus number of arguments serves as primary key
			see makeFncnPrimKey
	order
		used to sort for presentation purposes
		just numeric ordering
		doesn't have to be sequential, and no other requirements, like starting value or anything
		can be negative
		note that it's manually given, and could be confused if function is listed in multiple groups, or used in future ways, etc
	function specification (aka fncnspec)
		a string like userAdd(username [, group [, shell [, homedir]]]])
assumptions
	I assume that in the argument list, if one argument is optional, all the one's following it are, too
		eg userAdd(username [, group [, shell [, homedir]]]])
		(each Argmnt object still has its own independent properties, but above is assumed on printing out (and could be assumed elsewhere))
	repeatable arguments can be coded as a separate ... argument or as just argname... as the last argument
	the index page links assume that the category pages are named by their keyName (keyName.html), the first line of the page of definitions (in the data directory)
definition file format
	basic format
		category data in beginning, in brackets, as follows
			[keyName]
			[fullName]
			[order]		
		optional blank lines
		functions on indivdual lines
			function names and argument names need to be single word
		indented lines below functions (anything starting with whitespace) taken to be individual function descriptions (as of now, there are none)
		one or more blank lines (can only contain whitespace)
		group description
		one or more blank lines (doesn't have to be two like I tend to write)
	eg
		[myctgry]
		[This is My Category]
		[0]
		
		function0(arg0 [, arg1])
			function0 description sentence 0
			function0 description sentence 1
		function1()
			function1 description sentence 0
			function1 description sentence 1

		group description sentence 0
		group description sentence 1		
	function specification style:
		example, userAdd(username [, group [, shell [, homedir]]]])
		whitespaces don't matter
	function and group descriptions
		newlines are converted to spaces (so doesn't have to be one sentence on one line, like I tend to write)
		multiple whitespaces (spaces and tabs) are converted to a single space
		html
			html is allowed in function and group descriptions only
			when outputing html, the descriptions are output as is
			when outputing text, the html will be converted as follows (if not in the list below, or not used as below, it'll be ignored and will appear after conversion to plain text)
				(see TextProcessors.convertHTMLtoText for code)
				tag, requirements
					what it will be replaced with
				<i>,</i>
					removed
				<b>,</i>
					removed
				<br> not closed
					newline
				<ul></ul>, <li>,</li>
					removed, removed, newline and tab, removed
				<pre> closed, and not nested
					<pre> and </pre> themselves replaced with newline
					other tags (in this list) inside are processed, but whitespaces are preserved
				(in future, want to catch <font> with any attibutes, and strip out anything between <!-- -->)
	assume
		all initial data (stuff in brackets) is there
		at least one function per group (functions do not have to have descriptions)
		every group has a description
	tips
		can't have blank lines in function or group descriptions, but can have lines that are solely <!----> and will therefore not show up in html
			(once better parsing is set up for html -> text, they shouldn't show up in text either)
