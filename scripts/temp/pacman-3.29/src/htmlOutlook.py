#
#	Copyright, August 2003, Saul Youssef
#
#from Selector import *
from WebPage  import *
from StringAttr import *
from Execution import *
import TrustedCaches,Collections

def htmlOL(title,message0,E,w):
	w.text('<tr>'); w.cr()
	
	w.text('<td>'); w.cr()
	w.text(title)
	w.text('</td>'); w.cr()
	
	w.text('<td>'); w.cr()
	htmlOutLoop(E,message0,w)
	w.text('</td>'); w.cr()
	w.text('</tr>'); w.cr()

def htmlOL2(title,message0,E,w):
	w.text('<tr>'); w.cr()
	
	w.text('<td>'); w.cr()
	w.text(title)
	w.text('</td>'); w.cr()
	
	w.text('<td>'); w.cr()
	htmlOutLoop2(E,message0,w)
	w.text('</td>'); w.cr()
	w.text('</tr>'); w.cr()

def htmlOutLoop(E,message0,w):
	if len(E)==0:
		w.bullet(1,1); w.text(message0)
	else:
		for i in range(len(E)):
			e = E[i]
			e.bullet(w)
			w.text(e.str())
			if not i==len(E): w.text('<br>')
			w.cr()

def htmlOutLoop2(E,message0,w):
	if len(E)==0:
		w.bullet(1,1); w.text(message0)
	else:
		for i in range(len(E)):
			e = E[i]
			e.bullet(w)
			e.htmlLine(w)
			if not i==len(E): w.text('<br>')
			w.cr()

def sectionHeader(w,title,gif,url):
	w.text('<tr>')
	w.text('<td>')
	w.text('<h3><b>-- '+title+' --</b></h3>')
	w.text('</td>')
	w.text('<td>')
	if gif!='' and 0:
		w.text(' ')
		w.text('<a href="'+url+'"><img border="0" src="'+gif+'" height=100 width=200></a>')
		w.text('</td>')
	w.text('</tr>')
	
def sectionTitle(w,title,e):
	if e.satisfied().ok():
		sectionHeader(w,title,'smile.gif','smile.html')
	else:
		if not e.satisfiable().ok(): sectionHeader(w,title,'stop-sign.gif','stop-sign.html')
		else:
			if   e.eversatGet (): sectionHeader(w,title,'boom.gif','boom.html')
			elif e.everfailGet(): sectionHeader(w,title,'stop-sign.gif','stop-sign.html')
			else:                    sectionHeader(w,title,'','')

def htmlOutlook(E,rr,w,pwp,num_packages,num_nodes,wap):
	w.text('<table>'); w.cr()
	
	sat     = E.satisfied().ok()
	r       = E.satisfiable()
		
	w.text('<tr>')
	w.text('<td>')
	w.text('<h3><b>-- Environment Status --</b></h3>')
	w.text('</td>')
	w.text('</tr>')

	
#-- Top level packages
	w.text('<tr>'); w.cr()
	w.text('<td>'); w.cr()
	w.text('Top Level Packages')
	w.text('</td>'); w.cr()
	w.text('<td>'); w.cr()
	if len(E)==0:
		w.bullet(1,1); w.text('No packages installed.')
	else:
		count = 0
		for e in E: 
			count = count + 1
			e.bullet(w); e.htmlShortLine(w)
			if count!=len(E): w.text('<br>'); w.cr()
		
	w.text('</td>'); w.cr() 

	
#-- Installation status
	w.text('<tr>'); w.cr()
	
	w.text('<td>'); w.cr()
	w.text('Installation')
	w.text('</td>'); w.cr()
	
#	verbo.log('web','Outlook: Installation status...')
	
	w.text('<td>'); w.cr()
	if sat: 
		E.bullet(w)
		w.text('Environment containing '+`num_packages`+' packages with a '+`num_nodes`+' node dependency tree is successfully installed.')
	else:
#		r = E.satisfiable()
		if r.ok():
			E.bullet(w)
			if   E. eversatGet(): w.text('Installation environment containing '+`num_packages`+' packages is no longer satisfied.')
			elif E.everfailGet(): w.text('Installation attempt has failed.')
			else:                 
				w.text('Environment containing '+`num_packages`+' packages with a '+`num_nodes`+' node dependency tree is ready to install.')
		else:
			rl = r.nodups()
			for i in range(len(rl)):
				x = rl[i]
				w.bulletcross(); x.htmlOut(w); 
				if not i==len(rl): w.text('<br>')
				w.cr()
			w.bulletcross();
			w.strongText('<i>The installation will fail unless the above problems are fixed.</i>')
	w.text('</td>'); w.cr()
	w.text('</tr>'); w.cr()
	
#	verbo.log('web','Outlook: Trusted caches...')
	
#-- Trusted Caches
	w.text('<tr>'); w.cr()
	w.text('<td>'); w.cr()
	w.text('Trusted Caches')
	w.text('</td>'); w.cr()
	w.text('<td>'); w.cr()
	
	caches = TrustedCaches.getTrustedCaches()
	xcaches = []
	for c in caches:
		if not c.access(): xcaches.append(c)
	if len(xcaches)==0:
		w.bullet(1,1); w.text('All caches are accessible.')
	else:
		count = 0
		for c in xcaches: 
			count = count + 1
			w.bullet(0,1); c.htmlOut(w); w.text(' is inaccessible.')
			if count!=len(xcaches): w.text('<br>'); w.cr()
	w.text('</td>'); w.cr()
	
#	verbo.log('web','Oulook: Updates...')
	
#-- Updates
	w.text('<tr>'); w.cr()
	Es = wap.updates
	
	w.text('<td>'); w.cr()
	w.text('Updates')
	w.text('</td>'); w.cr()

	w.text('<td>'); w.cr()
	if len(Es)==0:
		w.bullet(1,1); w.text('All packages are up to date.')
	else:
		count = 0
		for e in Es: 
			count = count + 1
			e.bullet(w); e.htmlShortLine(w)
			if count!=len(Es): w.text('<br>'); w.cr()
	w.text('</td>'); w.cr()
	w.text('</tr>'); w.cr()
		
#	verbo.log('web','Outlook: Usernames...')

#-- Usernames required
#	u = UsernameSelector()
#	Es = u.reduce(E)
	Es = wap.usernames
	htmlOL('Installation Usernames','No usernames required.',Es,w)

#-- Questions
#	qu = QuestionSelector()
#	Es = qu.reduce(E)
	Es = wap.questions
	htmlOL('Installation Questions','No questions will be asked.',Es,w)
	
#-- Outgoing emails
	Es = wap.emails
	htmlOL('Outgoing emails','No outgoing emails.',Es,w)

#-- Last command
	w.text('<tr>'); w.cr()
	w.text('<td>'); w.cr()
	w.text('Last Command')
	w.text('</td>'); w.cr()

	w.text('<td>'); w.cr()
	if rr.ok():
		w.bullet(1,1); w.strongText(pcl()); w.text(' <i>( ok )</i>');
	else:
		w.bulletcross(); w.strongText(pcl())
		w.text(' <i>( ');
		rr.htmlOut(w,0)
		w.text(' )</i>')
	w.text('</td>'); w.cr()
	w.text('</tr>'); w.cr()

	w.text('<tr>')
	w.text('<td>'); w.text('<br>'); w.text('</td>')
	w.text('<td>'); w.text('<br>'); w.text('</td>')
	w.text('</tr>')
		
#	verbo.log('web','Outlook: Projects...')

#-- Projects
	Es = wap.impliesAccess
	sectionHeader(w,'Access and Accounts','','')

	htmlOL2('Access Packages','No access packages.',Es,w)

#	verbo.log('web','Outlook: SSH Access...')

#-- SSC Access
	Es = wap.sshAccess
	htmlOL('SSH Access','No SSH access granted.',Es,w)

#	verbo.log('web','Outlook: Globus access...')
	
#-- Globus Access
	Es = wap.globusAccess
	htmlOL('Globus Access','No Globus access granted.',Es,w)

#	verbo.log('web','Outlook: User groups...')

#-- User Groups created by Pacman
	Es = wap.groupadd
	htmlOL('Groups','No user groups created.',Es,w)

#	verbo.log('web','Outlook: New accounts...')
#-- Users created by Pacman
	Es = wap.useradd
	htmlOL('Accounts','No user accounts created.',Es,w)
		
#	verbo.log('web','Outlook: Work spaces...')
#-- Pacman created work areas
	Es = wap.workspaces
	htmlOL('Work Spaces','No work spaces created.',Es,w)

	w.text('<tr>')
	w.text('<td>'); w.text('<pre>                         </pre>'); w.text('</td>')
	w.text('</tr>')

	w.text('<tr>')
	w.text('<td>')
	w.text('<h3><b>-- Shell Operations --</b></h3>')
	w.text('</td>')
	w.text('</tr>')

#-- Shell commands executed as root
	w.text('<tr>'); w.cr()
	Es = wap.priviledgedShells

	w.text('<td>'); w.cr()
	w.text('Root Shell Commands')
	w.text('</td>'); w.cr()

	w.text('<td>'); w.cr()
	if len(Es)==0:
		w.bullet(1,1); w.text('No shell commands as root are required.')
		w.cr()
	elif len(Es)>10:
		sh2 = WebPage('Shell commmands as root.')
		Es.htmlOut(sh2)
		sh2.out('E/htmls/rootshellcommands.html')
		w.bullet(1,1); w.link('shell commands','rootshellcommands.html')
	else:
		htmlOutLoop(Es,'No shell commands as root are required.',w)
	w.text('</td>'); w.cr()
	w.text('</tr>'); w.cr()
	
#-- Shell commands
	w.text('<tr>'); w.cr()
	Es = wap.shells
	
	w.text('<td>'); w.cr()
	w.text('Non-Root Shell Commands')
	w.text('</td>'); w.cr()
		
	w.text('<td>'); w.cr()
	if len(Es)==0:
		w.bullet(1,1); w.text('No non-root shell commands are required.')
		w.cr()
	elif len(Es)>10:
		sh2 = WebPage('shell commands')
		Es.htmlOut(sh2)
		sh2.out('E/htmls/nonrootshellcommands.html')
		w.bullet(1,1); w.link('shell commands','nonrootshellcommands.html')
	else:
		htmlOutLoop(Es,'No non-root shell commands are required.',w)
	w.text('</td>'); w.cr()
	w.text('</tr>'); w.cr()

	w.text('</table>'); w.cr()
	w.text('<p>'); w.cr()
