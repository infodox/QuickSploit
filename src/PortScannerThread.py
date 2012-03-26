from socket import *
from threading import Thread

class PortScannerThread(Thread):

	def __init__(self,ip):
		Thread.__init__(self)
		self.ip = ip
		self.complete = False
		self.ports = [135,445]
		self.openPorts = []
		self.returnOnce = False
	def run(self):

		for port in self.ports:
			s = socket(AF_INET,SOCK_STREAM)
			s.settimeout(5)
			result = s.connect_ex((self.ip,port))

			if result == 0:
				self.openPorts.append(port)

		self.complete = True

	def isComplete(self):
		return self.complete

	def getOpenPorts(self):
		if self.returnOnce == False:
			self.returnOnce = True
			return self.openPorts
		return []

	def getIpAddress(self):
		return self.ip