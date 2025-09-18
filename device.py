# bpy-only syntax
# pyright: reportAttributeAccessIssue=false
# pyright: reportInvalidTypeForm=false

import bpy
from .ui import redraw_ui
from mathutils import Quaternion

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
	
	loc_mode: bpy.props.EnumProperty(
		name="Location Mode",
		description="How to apply device location to object",
		items=[
			("add", "Add", "Add device location to object location"),
			("replace", "Replace", "Set object location to device location"),
			("disabled", "Disabled", "Do not apply device location to object")
		],
		default="add"
	)
	
	rot_mode: bpy.props.EnumProperty(
		name="Rotation Mode",
		description="How to apply device rotation to object",
		items=[
			("add", "Add", "Add device rotation to object rotation"),
			("replace", "Replace", "Set object rotation to device rotation"),
			("disabled", "Disabled", "Do not apply device rotation to object")
		],
		default="add"
	)
	
	loc_scale: bpy.props.FloatProperty(
		name="Location Scale",
		description="Scale factor for device location (1.0 is 1:1 with real world)",
		min=0.0,
		soft_min=0.1,
		soft_max=100.0,
		default=1.0
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
	
	#TODO: convert to keyframes when "Auto Keying" is on (idk how)
	#TODO: handle adding to animated motion (replace all the calls to self["transform_backup"] with something else idk)
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
			if apply_to_backup:
				obj.location = loc
			else:
				if self.loc_mode == 'add':
					obj.location = [a + b for a, b in zip([a * self.loc_scale for a in loc], self["transform_backup"]["loc"])]
				elif self.loc_mode == 'replace':
					obj.location = [a * self.loc_scale for a in loc]
				elif self.loc_mode == 'disabled':
					obj.location = self["transform_backup"]["loc"]
		
		if rot is not None: #TODO: fix this shit idk wtf is going on (is it still an issue ? hahahaha (i'm going insane))
			if apply_to_backup:
				mode = obj.rotation_mode
				obj.rotation_mode = 'QUATERNION'
				obj.rotation_quaternion = rot
				obj.rotation_mode = mode
			else:
				if self.rot_mode == 'add':
					mode = obj.rotation_mode
					obj.rotation_mode = 'QUATERNION'
					backup_quat = Quaternion(self["transform_backup"]["rot"])
					device_quat = Quaternion(rot)
					obj.rotation_quaternion = device_quat @ backup_quat
					obj.rotation_mode = mode
				elif self.rot_mode == 'replace':
					mode = obj.rotation_mode
					obj.rotation_mode = 'QUATERNION'
					obj.rotation_quaternion = rot
					obj.rotation_mode = mode
				elif self.rot_mode == 'disabled':
					mode = obj.rotation_mode
					obj.rotation_mode = 'QUATERNION'
					obj.rotation_quaternion = Quaternion(self["transform_backup"]["rot"])
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