import socket

class Server:
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind((self.ip, self.port))
		
	def listen(self):
		self.socket.recvfrom(1024)