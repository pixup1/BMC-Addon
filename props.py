# bpy-only syntax
# pyright: reportAttributeAccessIssue=false
# pyright: reportInvalidTypeForm=false

import bpy
import bpy.utils.previews
from .utils import generate_qr_code, get_ifs, pick_default_if, get_ip_port
from .server import Server

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

pcoll = None

def update_qr_code():
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

def on_address_change(self, context: bpy.types.Context, srv: Server):
	assert context.screen is not None
	
	srv.change_address(*get_ip_port())
	
	update_qr_code()
	
	for area in context.screen.areas:
		if area.type == 'VIEW3D_PT_bmc_panel':
			area.tag_redraw()

def register1(): # Initialize temporary props needed for server creation
	ifs = get_ifs()
	
	bpy.types.WindowManager.bmc_interface = bpy.props.EnumProperty(
		name="Interface",
		description="Network interface to bind UDP server to",
		items=[(id, name, "IP: "+str(ip)) for (id, name, ip) in ifs],
		default=pick_default_if(ifs)
	)
	
	bpy.types.WindowManager.bmc_port = bpy.props.IntProperty(
		name="Port",
		description="Local port to bind UDP server to",
		default=34198
	)

def register2(srv: Server): # Initialize actual props
	del bpy.types.WindowManager.bmc_interface
	del bpy.types.WindowManager.bmc_port
	
	bpy.utils.register_class(BmcDevice)

	global pcoll
	pcoll = bpy.utils.previews.new()
	ifs = get_ifs()
	
	def update_callback(self, context):
		on_address_change(self, context, srv)
	
	bpy.types.WindowManager.bmc_interface = bpy.props.EnumProperty(
		name="Interface",
		description="Network interface to bind UDP server to",
		items=[(id, name, "IP: "+str(ip)) for (id, name, ip) in ifs],
		default=pick_default_if(ifs),
		update=update_callback
	)
	
	bpy.types.WindowManager.bmc_port = bpy.props.IntProperty(
		name="Port",
		description="Local port to bind UDP server to",
		default=34198,
		update=update_callback
	)
	
	bpy.types.WindowManager.bmc_devices = bpy.props.CollectionProperty(
		type=BmcDevice,
	)
	
	bpy.types.WindowManager.bmc_device_index = bpy.props.IntProperty(
		name="Selected BMC Device Index"
	)
	
	# TEMP example device
	assert bpy.context.window_manager is not None
	example_device1 = bpy.context.window_manager.bmc_devices.add()
	example_device1.name = "Example Device 1"
	example_device1.ip = "192.168.1.104"
	example_device1.port = 54678
	example_device2 = bpy.context.window_manager.bmc_devices.add()
	example_device2.name = "Super Long Name Example Device 2"
	example_device2.ip = "192.168.1.156"
	example_device2.port = 64574

	update_qr_code()

def unregister():
	assert bpy.context.window_manager is not None
	bpy.context.window_manager.bmc_devices.clear()
	
	del bpy.types.WindowManager.bmc_interface
	del bpy.types.WindowManager.bmc_port
	del bpy.types.WindowManager.bmc_devices
	del bpy.types.WindowManager.bmc_device_index
	del bpy.types.WindowManager.qr_code
	
	bpy.utils.unregister_class(BmcDevice)
	
	global pcoll
	bpy.utils.previews.remove(pcoll)