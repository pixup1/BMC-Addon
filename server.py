import socket
import threading

#TODO: add a callback for the server to add and remove BmcDevice objects, and set motion data for a BmcDevice

class Device:
	def __init__(self, name, address, server):
		self.name = name
		self.address = address
		
		self.server = server
		
		self.connection_timer = threading.Timer(0.2, self.timeout)
		self.reset_timer()
		
	def reset_timer(self):
		# Disconnect if no data received in 200ms
		self.connection_timer.cancel()
		self.connection_timer = threading.Timer(0.2, self.timeout)
		self.connection_timer.start()
		
	def timeout(self):
		self.server.disconnect_device(self.address)

class Server:
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port
		
		self.connected_devices: list[Device] = []
	
	def start(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind((self.ip, self.port))
		self.sock.settimeout(0.2)
		
		self.stop_event = threading.Event()
		self.listen_thread = threading.Thread(target=self.listen, daemon=True)
		self.listen_thread.start()

	def stop(self):
		self.stop_event.set()
		for device in self.connected_devices:
			self.disconnect_device(device.address)
		self.sock.close()
		if self.listen_thread.is_alive():
			self.listen_thread.join()
	
	def change_address(self, ip, port):
		self.stop()
		self.__init__(ip, port)
		self.start()
	
	def connect_device(self, name, address):
		self.connected_devices.append(Device(name, address, self))
	
	def disconnect_device(self, address):
		device_to_remove = next((device for device in self.connected_devices if device.address == address), None)
		if device_to_remove:
			self.connected_devices.remove(device_to_remove)
	
	def listen(self):
		while not self.stop_event.is_set():
			try:
				bytes, address = self.sock.recvfrom(1024)
			except socket.timeout:
				continue
			except OSError: # Socket closed
				if self.stop_event.is_set():
					break
				raise
			
			string = bytes.decode('utf-8')
			
			type = string.split(' ')[0]
			msg = string.split(' ')[1:]
			
			device = next((device for device in self.connected_devices if device.address == address), None)
			if not device:
				if type == "CONNECT":
					self.connect_device(msg, address)
					self.sock.sendto(b"ACK Connected", address)
				else:
					self.sock.sendto(b"ERR Not connected", address)
			else:
				device.reset_timer()
				match type:
					case "CONNECT":
						self.sock.sendto(b"ERR Already connected", address)
					case "DISCONNECT":
						self.disconnect_device(address)
						self.sock.sendto(b"ACK", address)
					case "DATA":
						#TODO: handle motion data
						self.sock.sendto(b"ACK", address)
					case "PING":
						self.sock.sendto(b"ACK", address)
					case _:
						self.sock.sendto(b"ERR Unknown message", address)