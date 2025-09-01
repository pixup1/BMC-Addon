# bpy-only syntax
# pyright: reportAttributeAccessIssue=false

import bpy
import bpy.utils.previews
from .utils import generate_qr_code

# Not a callback, but had to be here to avoid circular imports
def update_qr_code(): #TODO: fix qr code only updating a couple of times
	previews = bpy.utils.previews.new()
	
	img = previews.load("bmc_qr_code", generate_qr_code(), 'IMAGE')
	
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