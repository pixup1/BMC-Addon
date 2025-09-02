# bpy-specific syntax
# pyright: reportAttributeAccessIssue=false

import bpy
import ifaddr
import re
import qrcode
import tempfile
import os

# Find all network interfaces and their IP addresses
# Returns a list of (id, name, ip) tuples
def get_ifs() -> list[tuple[str, str, str]]:
	ifs = []
	adapters = ifaddr.get_adapters()

	for adapter in adapters: #TODO: Make loopback last option
		ifs.append((adapter.name, adapter.nice_name, adapter.ips[0].ip))
	
	return ifs

# print(get_ifs())

# Get the currently selected IP and port
def get_ip_port():
	assert bpy.context.window_manager is not None
	wm = bpy.context.window_manager
	interface = wm.bmc_interface
	port = wm.bmc_port

	enum_items = bpy.types.WindowManager.bl_rna.properties["bmc_interface"].enum_items

	for item in enum_items:
		if item.identifier == interface:
			description = item.description
			ip = re.sub(r'^IP: ', '', description)
			return (ip,port)
	
	raise ValueError("Selected interface not found")

# Generate a QR code png and save it in the OS temp directory
# Returns the path to the image file
def generate_qr_code(bg_color, fg_color):
	ip, port = get_ip_port()
	
	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_L,
		box_size=10,
		border=1,
	)
	qr.add_data(f"{ip}:{port}")
	qr.make(fit=True)
	
	pil_img = qr.make_image(fill_color=fg_color, back_color=bg_color) #TODO: make pretty with theme colors
	
	qr_file = os.path.join(tempfile.gettempdir(), "bmc_qr_code.png")
	with open(qr_file, 'wb') as f:
		pil_img.save(f)
	
	return qr_file