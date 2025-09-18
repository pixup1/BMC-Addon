# bpy-only syntax
# pyright: reportAttributeAccessIssue=false

import socket
import threading
import json
from .device import add_bmc_device, remove_bmc_device
from .utils import bmc_print, run_main_thread

#TODO: handle firewall or at least warn user to open the port

TIMEOUT = 2 # seconds
BUF_LENGTH = 1024

class Device:
	def __init__(self, name, address, bmc_device, server):
		self.name = name
		self.address = address
		
		self.bmc_device = bmc_device
		self.server = server
		
		# Disconnect if no data received in TIMEOUT seconds
		self.connection_timer = threading.Timer(TIMEOUT, self.timeout)
		self.reset_timer()
		
	def reset_timer(self):
		self.connection_timer.cancel()
		self.connection_timer = threading.Timer(TIMEOUT, self.timeout)
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
		#This is AF_INET, so address is (ip, port)
		bmc_device = add_bmc_device(name, address[0], address[1])
	
		self.connected_devices.append(Device(name, address, bmc_device, self))
		
		bmc_print(f"Connected to device {name} at {address[0]}:{address[1]}")
	
	def disconnect_device(self, address):
		device = next((device for device in self.connected_devices if device.address == address), None)
		
		if device:
			device.bmc_device.object = None
			self.connected_devices.remove(device)
		
		remove_bmc_device(address[0])
		
		bmc_print(f"Disconnected device at {address[0]}:{address[1]}")
	
	def listen(self):
		while not self.stop_event.is_set():
			try:
				bytes, address = self.sock.recvfrom(BUF_LENGTH)
			except socket.timeout:
				continue
			except OSError: # Socket closed
				if self.stop_event.is_set():
					break
				raise
			
			string = bytes.decode('utf-8')
			
			type = string.split(' ')[0]
			msg = ' '.join(string.split(' ')[1:])
			
			device: Device | None = next((device for device in self.connected_devices if device.address == address), None)
			if not device:
				if type == "CONNECT":
					self.connect_device(msg, address)
					self.sock.sendto(b"CONNECT Connected " + socket.gethostname().encode("utf-8"), address)
				elif type == "PING":
					self.sock.sendto(b"ERR Not connected", address)
			else:
				device.reset_timer()
				match type:
					case "CONNECT":
						self.sock.sendto(b"CONNECT Already connected", address)
					case "DISCONNECT":
						self.disconnect_device(address)
						self.sock.sendto(b"DISCONNECT Disconnected", address)
					case "DATA":
						run_main_thread(device.bmc_device.apply_transform, json.loads(msg))
					case "PING":
						self.sock.sendto(b"PONG " + msg.encode("utf-8"), address)
					case _:
						pass