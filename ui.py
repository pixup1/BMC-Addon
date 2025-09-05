# bpy-specific syntax
# pyright: reportAttributeAccessIssue=false

import bpy
from bpy.types import Context
from .utils import get_ip_port
from typing import Literal

RedrawType = Literal["NONE", "FULL", "SETTINGS", "DEVICES"]
redraw_requested: RedrawType = "NONE"

def redraw_ui(type: RedrawType = "FULL"):
	global redraw_requested
	if type != "NONE" and redraw_requested != "NONE" and redraw_requested != type:
		redraw_requested = "FULL"
	else:
		redraw_requested = type
	print("Requested UI redraw")

# Context is only available from the main thread, so we can't refresh the UI directly from background threads
def redraw_timer():
	global redraw_requested
	if redraw_requested != "NONE":
		assert bpy.context.screen is not None
		panel_id = "VIEW3D_PT_bmc_panel"
		
		match redraw_requested:
			case "SETTINGS":
				panel_id = "VIEW3D_PT_bmc_panel_settings"
			case "DEVICES":
				panel_id = "VIEW3D_PT_bmc_panel_devices"
		
		for area in bpy.context.screen.areas:
			if area.type == "VIEW_3D": #TODO: fix this, find a way to only update the BMC panel
				area.tag_redraw()
				print("Redrew UI yes sir")
		
		redraw_requested = "NONE"
		print("Redrew UI")
	return 0.1

class BmcDeviceListUI(bpy.types.UIList):
	bl_idname = "BMC_DEVICES_UL_list"
	
	def draw_item(self, context, layout, data, item, icon, active_data, active_property, index, flt_flag):
		if self.layout_type == 'DEFAULT':
			if isinstance(item, bpy.types.PropertyGroup):
				row = layout.row()
				
				row.label(text=item.name)
				
				sub_layout = row.row()
				sub_layout.alignment = 'RIGHT'
				sub_layout.enabled = False  # This greys out the label
				sub_layout.label(text=item.ip)

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
		
		# This is seemingly the only way to display an arbitrary image in the UI
		layout.template_icon_view(wm, "qr_code", scale=8)
		
		box = layout.box()
		row = box.row()
		row.alignment = 'CENTER'
		row.label(text=f"{ip}:{port}")

class BmcSubPanel1(BmcPanel):
	bl_parent_id = "VIEW3D_PT_bmc_panel"
	bl_idname = "VIEW3D_PT_bmc_panel_settings"
	bl_label = "Server Settings"
	bl_options = {'DEFAULT_CLOSED'}
	
	def draw(self, context: Context):
		assert self.layout is not None
		layout = self.layout
		assert context.window_manager is not None
		wm = context.window_manager
		
		layout.label(text="Changing these values will disconnect all devices", icon='WARNING_LARGE')
		
		row = layout.row()
		row.prop(wm, "bmc_interface")
		row.operator("wm.bmc_refresh_ifs", text="", icon='FILE_REFRESH', emboss=False)
		
		layout.prop(wm, "bmc_port")

class BmcSubPanel2(BmcPanel):
	bl_parent_id = "VIEW3D_PT_bmc_panel"
	bl_idname = "VIEW3D_PT_bmc_panel_devices"
	bl_label = "Connected Devices"
	
	def draw(self, context: Context):
		assert self.layout is not None
		layout = self.layout
		assert context.window_manager is not None
		wm = context.window_manager
		
		box = layout.box()
		box.template_list( #TODO: fix this
			listtype_name="BMC_DEVICES_UL_list",
			list_id="bmc_devices",
			dataptr=wm,
			propname="bmc_devices",
			active_dataptr=wm,
			active_propname="bmc_device_index",
		)
		
		if 0 <= wm.bmc_device_index < len(wm.bmc_devices):
			device = wm.bmc_devices[wm.bmc_device_index]
			box.prop(device, "object")

def register():
	bpy.utils.register_class(BmcDeviceListUI)
	bpy.utils.register_class(BmcMainPanel)
	bpy.utils.register_class(BmcSubPanel1)
	bpy.utils.register_class(BmcSubPanel2)
	bpy.app.timers.register(redraw_timer, persistent=True)

def unregister():
	bpy.app.timers.unregister(redraw_timer)
	bpy.utils.unregister_class(BmcSubPanel2)
	bpy.utils.unregister_class(BmcSubPanel1)
	bpy.utils.unregister_class(BmcMainPanel)
	bpy.utils.unregister_class(BmcDeviceListUI)