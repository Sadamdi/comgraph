"""Auto-start BlenderMCP server setiap Blender dibuka (GUI saja).

Dipasang sebagai startup script karena Blender 5.x tidak lagi memuat
add-on legacy dari scripts/addons. Pasangannya: blender_mcp.py di folder ini.
"""
import bpy

PORT = 9876
_tries = 0


def _start():
    global _tries
    _tries += 1
    try:
        if getattr(bpy.types, "blendermcp_server", None) is not None:
            bpy.ops.blendermcp.start_server()
            print(f"BlenderMCP: auto-start OK (port {PORT})")
            return None
    except Exception as exc:
        print("BlenderMCP: auto-start gagal:", exc)
        return None
    return 1.0 if _tries < 10 else None   # tunggu addon selesai register


def register():
    if not bpy.app.background:
        bpy.app.timers.register(_start, first_interval=1.5, persistent=True)


def unregister():
    if bpy.app.timers.is_registered(_start):
        bpy.app.timers.unregister(_start)
