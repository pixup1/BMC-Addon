# bpy-only syntax
# pyright: reportAttributeAccessIssue=false
# pyright: reportInvalidTypeForm=false

import bpy
from .ui import redraw_ui

class BmcDevice(bpy.types.PropertyGroup):
	name: bpy.props.StringProperty(
		name="Device Name",
		description="Name of the device"
	)
	
	ip: bpy.props.StringProperty(
		name="Device IP Address",
		description="IP address of the device"
	)
	
	port: bpy.props.IntProperty(
		name="Device Port",
		description="Remote port the device is communicating from"
	)
	
	object: bpy.props.PointerProperty(
		type=bpy.types.Object,
		name="Controlled Object",
		description="Object controlled by this device"
	)
	
	def apply_transform(self, transform: dict):
		if self.object is None:
			return
		
		loc = transform.get("loc", None)
		rot = transform.get("rot", None)
		scale = transform.get("scale", None)
		
		if loc is not None:
			self.object.location = loc
		if rot is not None:
			self.object.rotation_euler = rot
		if scale is not None:
			self.object.scale = scale

def add_bmc_device(name, ip, port):
	assert bpy.context.window_manager is not None
	device = bpy.context.window_manager.bmc_devices.add()
	device.name = name
	device.ip = ip
	device.port = port
	
	redraw_ui()

def remove_bmc_device(ip):
	assert bpy.context.window_manager is not None
	wm = bpy.context.window_manager
	for i, device in enumerate(wm.bmc_devices):
		if device.ip == ip:
			wm.bmc_devices.remove(i)
			
			redraw_ui()
			return

def apply_bmc_device_transform(ip, transform):
	assert bpy.context.window_manager is not None
	wm = bpy.context.window_manager
	for device in wm.bmc_devices:
		if device.ip == ip:
			device.apply_transform(transform)
			return