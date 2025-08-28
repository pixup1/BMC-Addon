import bpy
from .device import BmcDevice

def register():
	bpy.types.Scene.bmc_interface = bpy.props.EnumProperty( #TODO: use something other than scene
		name="Interface",
		description="Network interface to bind UDP server to",
		items=[
			("ETH0", "eth0", "Ethernet network interface"),
			("WLAN0", "wlan0", "Wireless network interface"),
			("LOOPBACK", "loopback", "Loopback interface")
		],
		default="WLAN0"
	)
	
	bpy.types.Scene.bmc_port = bpy.props.IntProperty( 
		name="Port",
		description="Local port to bind UDP server to",
		default=34198
	)
	
	bpy.types.Scene.bmc_connected_devices = bpy.props.CollectionProperty( #TODO: fix this
		type=BmcDevice,
	)
	
	bpy.types.Scene.bmc_connected_device_index = bpy.props.IntProperty(
	)

def unregister():
	del bpy.types.Scene.bmc_interface
	del bpy.types.Scene.bmc_port
	del bpy.types.Scene.bmc_connected_devices
	del bpy.types.Scene.bmc_connected_device_index