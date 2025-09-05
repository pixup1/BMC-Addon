# bpy-specific syntax
# pyright: reportAttributeAccessIssue=false

import bpy
from bpy.types import Context
from .utils import get_ip_port

redraw_requested = False

def redraw_ui():
	global redraw_requested
	redraw_requested = True
	print("Requested UI redraw")

# Context is only available from the main thread, so we can't refresh the UI directly from background threads
def redraw_timer():
	global redraw_requested
	if redraw_requested:
		assert bpy.context.screen is not None
		for area in bpy.context.screen.areas:
			if area.type == "VIEW_3D":
				for region in area.regions:
					if region.type == "UI":
						area.tag_redraw()
		redraw_requested = False
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
		box.template_list(
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