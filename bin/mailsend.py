#!/usr/bin/env python
import sys, smtplib, socket

def mailSend(fromaddr=None,toaddr=None,subj='',msg=None):
    if (not fromaddr):
        fromaddr = ("LJSFi AutoInstall <nobody@%s>" % socket.getfqdn())
    if (toaddr and msg):
        msg = "From: "+fromaddr+"\n"+"To: "+toaddr+"\n"+"Subject: "+subj+"\n\n"+msg
        toaddrs = toaddr.split(',')
        server = smtplib.SMTP('localhost')
        server.sendmail(fromaddr, toaddrs, msg)
        server.quit()
