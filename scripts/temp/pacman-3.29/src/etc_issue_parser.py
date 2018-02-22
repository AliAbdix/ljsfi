import os

known_platforms = [  #put the higher precedence ones later
		('unix'              , 'Unix'     ),
		('linux'             , 'Linux'    ),
		('sl'                , 'SL'       ),
		('red hat'           , 'RedHat'   ),
		('red hat enterprise', 'RHEL'     ),
		('suse'              , 'SuSE'     ),
		('fedora'            , 'Fedora'   ),
		('debian'            , 'Debian'   ),
		('tao'               , 'Tao'      ),
		('scientific linux'  , 'SL'       ),
		('rocks'             , 'Rocks'    ),
		('bu-linux'          , 'BU-Linux' ),
		('centos'            , 'CentOS'   ),
		('gentoo'            , 'Gentoo'   ),
		('mandrake'          , 'Mandrake' ),
		('freebsd'           , 'FreeBSD'  ),
		('ubuntu'            , 'Ubuntu'   ),
		('yellow dog'        , 'YellowDog'),
	]

def find_first_int(text):
	intstr = ''
	for i in range(len(text)):
		try:
			n = int(text[i])
		except ValueError:
			pass
		else:
			intstr += text[i]
			for j in range(i+1, len(text)):
				try:
					n = int(text[j])
					intstr += text[j]
				except ValueError:
					return intstr
	return ''

def parse(etc_issue_text):
	text = etc_issue_text.lower()
	platform = ''
	for known_platform, nickname in known_platforms:
		if text.find(known_platform)>-1: platform = nickname
	return platform, find_first_int(text)

if __name__=='__main__':
	for etc_issue in os.listdir('etc_issues'):
		text = open(os.path.join('etc_issues', etc_issue)).read()
		print '-----------------------------------------'
		print text
		print parse(text)
