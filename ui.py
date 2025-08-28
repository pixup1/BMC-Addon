import bpy
from bpy.types import Context

class BmcPanel(bpy.types.Panel):
	bl_category = "Motion Control"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"

class BmcMainPanel(BmcPanel):
	bl_idname = "VIEW3D_PT_bmc_panel"
	bl_label = "Motion Control"
	
	def draw(self, context: Context):
		layout = self.layout
		
		layout.label(text="Scan to connect:")
		layout.label(text="(QR code here)")
		layout.label(text="(IP:Port display, not editable)")

class BmcSubPanel1(BmcPanel):
	bl_parent_id = "VIEW3D_PT_bmc_panel"
	bl_label = "Server Settings"
	
	def draw(self, context: Context):
		layout = self.layout
		scene = context.scene
		
		layout.prop(scene, "bmc_interface")  # TODO: use something other than scene
		layout.prop(scene, "bmc_port")

class BmcSubPanel2(BmcPanel):
	bl_parent_id = "VIEW3D_PT_bmc_panel"
	bl_label = "Connected Devices"
	
	def draw(self, context: Context):
		layout = self.layout
		
		box = layout.box()
		box.template_list(
			listtype_name="bmc_devices",
			list_id="bmc_devices",
			dataptr=context.scene,
			propname="bmc_connected_devices",
			active_dataptr=context.scene,
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
