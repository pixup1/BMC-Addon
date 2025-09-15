# bpy-only syntax
# pyright: reportAttributeAccessIssue=false
# pyright: reportInvalidTypeForm=false

import bpy
from .ui import redraw_ui

def update_object(self, context):
	if self.object_backup:
		self.apply_transform(self["transform_backup"], True)
	self.object_backup = self.object
	self["transform_backup"] = self.get_transform()

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
		description="Object controlled by this device",
		update=update_object
	)
	
	object_backup: bpy.props.PointerProperty(
		type=bpy.types.Object
	)
	
	def get_transform(self):
		if self.object is None:
			return {}
		
		mode = self.object.rotation_mode
		self.object.rotation_mode = 'QUATERNION'
		
		transform = {
			"loc": list(self.object.location),
			"rot": list(self.object.rotation_quaternion),
			"scale": list(self.object.scale)
		}
		
		self.object.rotation_mode = mode
		
		return transform
	
	def apply_transform(self, transform: dict, apply_to_backup: bool = False):
		obj = None
		
		if apply_to_backup:
			obj = self.object_backup
		else:
			obj = self.object
		
		if obj is None:
			return
		
		loc = transform.get("loc", None)
		rot = transform.get("rot", None)
		scale = transform.get("scale", None)
		
		if loc is not None:
			obj.location = loc
		
		if rot is not None:
			mode = obj.rotation_mode
			obj.rotation_mode = 'QUATERNION'
			obj.rotation_quaternion = rot
			obj.rotation_mode = mode
		
		if scale is not None:
			obj.scale = scale

def add_bmc_device(name, ip, port):
	assert bpy.context.window_manager is not None
	device = bpy.context.window_manager.bmc_devices.add()
	device.name = name
	device.ip = ip
	device.port = port
	if bpy.context.view_layer is not None:
		if bpy.context.view_layer.objects.active is not None:
			device.object = bpy.context.view_layer.objects.active
	
	redraw_ui()
	
	return device

def remove_bmc_device(ip):
	assert bpy.context.window_manager is not None
	wm = bpy.context.window_manager
	for i, device in enumerate(wm.bmc_devices):
		if device.ip == ip:
			wm.bmc_devices.remove(i)
			
			redraw_ui()
			return