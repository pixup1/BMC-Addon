'''
Blender Motion Control - Addon

Copyright (C) 2025 pixup1

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from . import props, ops, ui
from .server import Server
from .utils import get_ip_port

srv = None

def register():
	props.register1()
	global srv
	srv = Server(*get_ip_port())
	props.register2(srv)
	ops.register()
	ui.register()
	srv.start()

def unregister():
	global srv
	if srv is not None:
		srv.stop()
	ui.unregister()
	ops.unregister()
	props.unregister()