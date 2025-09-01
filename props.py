# bpy-only syntax
# pyright: reportAttributeAccessIssue=false

import bpy
import bpy.utils.previews
from .utils import generate_qr_code
from .device import BmcDevice
from .utils import get_ifs

pcoll = None

def update_qr_code():
	print("Updating QR code...")
	global pcoll
	assert pcoll is not None
	
	pcoll.clear()
	
	img = pcoll.load("bmc_qr_code", generate_qr_code(), 'IMAGE')
	
	items = []
	
	items.append(("qr_code", "qr_code", "", img.icon_id, 0))
	
	bpy.types.WindowManager.qr_code = bpy.props.EnumProperty(
		items=items
	)

def on_address_change(self, context: bpy.types.Context):
	assert context.screen is not None
	
	update_qr_code()
	
	for area in context.screen.areas:
		if area.type == 'VIEW3D_PT_bmc_panel':
			area.tag_redraw()

def register() -> None:
	global pcoll
	pcoll = bpy.utils.previews.new()
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
	
	global pcoll
	bpy.utils.previews.remove(pcoll)