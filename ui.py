# bpy-specific syntax
# pyright: reportAttributeAccessIssue=false

import bpy
from bpy.types import Context
from .utils import get_ip_port

class BmcPanel(bpy.types.Panel):
	bl_category = "Motion Control"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"

class BmcMainPanel(BmcPanel):
	bl_idname = "VIEW3D_PT_bmc_panel"
	bl_label = "Motion Control"
	
	def draw(self, context: Context):
		assert self.layout is not None
		layout= self.layout
		assert context.window_manager is not None
		wm = context.window_manager
		
		ip, port = get_ip_port()
		
		layout.label(text="Scan to connect:")
		
		layout.template_icon_view(wm, "qr_code")
		
		layout.label(text=f"{ip}:{port}")

class BmcSubPanel1(BmcPanel):
	bl_parent_id = "VIEW3D_PT_bmc_panel"
	bl_label = "Server Settings"
	
	def draw(self, context: Context):
		assert self.layout is not None
		layout = self.layout
		assert context.window_manager is not None
		wm = context.window_manager
		
		layout.prop(wm, "bmc_interface") #TODO: add a refresh button for the interfaces
		layout.prop(wm, "bmc_port")

class BmcSubPanel2(BmcPanel):
	bl_parent_id = "VIEW3D_PT_bmc_panel"
	bl_label = "Connected Devices"
	
	def draw(self, context: Context):
		assert self.layout is not None
		layout = self.layout
		assert context.window_manager is not None
		wm = context.window_manager
		
		box = layout.box()
		box.template_list( #TODO: fix this
			listtype_name="bmc_devices",
			list_id="bmc_devices",
			dataptr=wm,
			propname="bmc_connected_devices",
			active_dataptr=wm,
			active_propname="bmc_connected_device_index",
		)
	

def register():
	bpy.utils.register_class(BmcMainPanel)
	bpy.utils.register_class(BmcSubPanel1)
	bpy.utils.register_class(BmcSubPanel2)

def unregister():
	bpy.utils.unregister_class(BmcMainPanel)
	bpy.utils.unregister_class(BmcSubPanel1)
	bpy.utils.unregister_class(BmcSubPanel2)
