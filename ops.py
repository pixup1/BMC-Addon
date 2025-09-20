# bpy-only syntax
# pyright: reportAttributeAccessIssue=false

import bpy
from .utils import get_ifs, pick_default_if

class RefreshIfsOperator(bpy.types.Operator):
	bl_idname = "wm.bmc_refresh_ifs"
	bl_label = "Refresh Interfaces"
	bl_description = "Refresh the list of network interfaces"
	
	def execute(self, context):
		assert context.window_manager is not None
		wm = context.window_manager
		
		ifs = [("fake", "Fake Interface", "1.1.1.1")] #get_ifs()
		
		# bpy.types.WindowManager.bmc_interface = bpy.props.EnumProperty(
		# 	name="Interface",
		# 	description="Network interface to bind UDP server to",
		# 	items=[(id, name, "IP: "+str(ip)) for (id, name, ip) in ifs],
		# 	default=pick_default_if(ifs),
		# 	update=lambda self, context: on_address_change(self, context, srv)
		# )
		
		self.report({'WARNING'}, "Feature not yet implemented")
		
		return {'FINISHED'}

def register():
	bpy.utils.register_class(RefreshIfsOperator)

def unregister():
	bpy.utils.unregister_class(RefreshIfsOperator)