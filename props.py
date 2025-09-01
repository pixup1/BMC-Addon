# bpy-only syntax
# pyright: reportAttributeAccessIssue=false

import bpy
from .device import BmcDevice
from .utils import get_ifs
from .props_callbacks import *

def register() -> None:
	ifs = get_ifs()
	
	bpy.types.WindowManager.bmc_interface = bpy.props.EnumProperty(
		name="Interface",
		description="Network interface to bind UDP server to",
		items=[(id, name, "IP: "+str(ip)) for (id, name, ip) in ifs],
		default=ifs[0][0],
		update=on_address_change
	)
	
	bpy.types.WindowManager.bmc_port = bpy.props.IntProperty(
		name="Port",
		description="Local port to bind UDP server to",
		default=34198,
		update=on_address_change
	)
	
	bpy.types.WindowManager.bmc_connected_devices = bpy.props.CollectionProperty( #TODO: fix this
		type=BmcDevice,
	)
	
	bpy.types.WindowManager.bmc_connected_device_index = bpy.props.IntProperty(
	)
	
	update_qr_code()

def unregister():
	del bpy.types.WindowManager.bmc_interface
	del bpy.types.WindowManager.bmc_port
	del bpy.types.WindowManager.bmc_connected_devices
	del bpy.types.WindowManager.bmc_connected_device_index
	del bpy.types.WindowManager.qr_code