# bpy-only syntax
# pyright: reportInvalidTypeForm=false

import bpy

class BmcDevice(bpy.types.PropertyGroup):
	name: bpy.props.StringProperty(name="Device Hostname")
	ip: bpy.props.StringProperty(name="Device IP Address")
	port: bpy.props.IntProperty(name="Device Port")
	object: bpy.props.PointerProperty(type=bpy.types.Object)

def register():
	bpy.utils.register_class(BmcDevice)

def unregister():
	bpy.utils.unregister_class(BmcDevice)