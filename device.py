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

def apply_rotation(obj, mode, rot):
	match mode:
		case 'QUATERNION':
			obj.rotation_quaternion = rot
		case 'AXIS_ANGLE':
			obj.rotation_axis_angle = rot.to_axis_angle()
		case _:
			obj.rotation_euler = rot.to_euler(mode)

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
			("disabled", "Off", "Do not apply device location to object")
		],
		default="add"
	)
	
	rot_mode: bpy.props.EnumProperty(
		name="Rotation Mode",
		description="How to apply device rotation to object",
		items=[
			("add", "Add", "Add device rotation to object rotation"),
			("replace", "Replace", "Set object rotation to device rotation"),
			("disabled", "Off", "Do not apply device rotation to object")
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
		
		do_keyframes = False
		if bpy.context.scene is not None:
			do_keyframes = bpy.context.scene.tool_settings.use_keyframe_insert_auto
		
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
			if do_keyframes and not self.loc_mode == 'disabled':
				obj.keyframe_insert(data_path="location")
		
		if rot is not None:
			rot = Quaternion(rot)
			mode = obj.rotation_mode
			if apply_to_backup:
				apply_rotation(obj, mode, rot)
			else:
				if self.rot_mode == 'add':
					apply_rotation(obj, mode, rot @ Quaternion(self["transform_backup"]["rot"]))
				elif self.rot_mode == 'replace':
					apply_rotation(obj, mode, rot)
				elif self.rot_mode == 'disabled':
					apply_rotation(obj, mode, Quaternion(self["transform_backup"]["rot"]))
			if do_keyframes and not self.loc_mode == 'disabled':
				path = "rotation_quaternion"
				match mode:
					case 'AXIS_ANGLE':
						path = "rotation_axis_angle"
					case _:
						path = "rotation_euler"
				obj.keyframe_insert(data_path=path)
		
		# if scale is not None:
		# 	obj.scale = scale

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