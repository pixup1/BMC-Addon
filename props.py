# bpy-only syntax
# pyright: reportAttributeAccessIssue=false
# pyright: reportInvalidTypeForm=false

import bpy
import bpy.utils.previews
from .utils import generate_qr_code
from .utils import get_ifs

class BmcDevice(bpy.types.PropertyGroup):
	name: bpy.props.StringProperty(name="Device Hostname")
	ip: bpy.props.StringProperty(name="Device IP Address")
	port: bpy.props.IntProperty(name="Device Port")
	object: bpy.props.PointerProperty(type=bpy.types.Object)

pcoll = None

def update_qr_code():
	print("Updating QR code...")
	global pcoll
	assert pcoll is not None
	
	pcoll.clear()
	
	assert bpy.context.preferences is not None
	theme = bpy.context.preferences.themes[0]
	bg_color = (int(theme.user_interface.wcol_regular.inner[0]*256.0), int(theme.user_interface.wcol_regular.inner[1]*256.0), int(theme.user_interface.wcol_regular.inner[2]*256.0))
	fg_color = (int(theme.user_interface.wcol_regular.text[0]*256.0), int(theme.user_interface.wcol_regular.text[1]*256.0), int(theme.user_interface.wcol_regular.text[2]*256.0))
	img = pcoll.load("bmc_qr_code", generate_qr_code(bg_color, fg_color), 'IMAGE')
	
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
	bpy.utils.register_class(BmcDevice)

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
	
	bpy.utils.unregister_class(BmcDevice)
	
	global pcoll
	bpy.utils.previews.remove(pcoll)