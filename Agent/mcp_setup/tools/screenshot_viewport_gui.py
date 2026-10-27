"""Screenshot JENDELA Blender asli lengkap dengan tools/panel (bukan render) untuk laporan PDF.

Harus dijalankan dengan jendela Blender (GUI), bukan -b, karena memakai screenshot_area:
  blender --factory-startup -P screenshot_viewport_gui.py -- jobs.json
jobs.json = [{"key": "m5", "file": ".../x.blend" | null, "out": "folder", "shots": [{"name": "a", "view": "front", "frame": 1}]}]
view: front back right left top persp persp2 camera.  File .blend tidak disimpan (hanya dibuka di sesi ini).
"""
import bpy, sys, json, math, os
from mathutils import Euler

JOBS = json.load(open(sys.argv[sys.argv.index("--") + 1], encoding="utf-8"))
ROT = {"front": (math.pi / 2, 0, 0), "back": (math.pi / 2, 0, math.pi), "right": (math.pi / 2, 0, math.pi / 2),
       "left": (math.pi / 2, 0, -math.pi / 2), "top": (0, 0, 0), "persp": (1.15, 0, 0.6), "persp2": (1.15, 0, -0.7)}


def v3d():
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == "VIEW_3D":
                return win, area, next(r for r in area.regions if r.type == "WINDOW"), area.spaces.active
    return None


def ov(win, area, region):
    return bpy.context.temp_override(window=win, screen=win.screen, area=area, region=region)


def run():
    for job in JOBS:
        os.makedirs(job["out"], exist_ok=True)
        if job.get("file"):
            bpy.ops.wm.open_mainfile(filepath=job["file"])
        else:
            bpy.ops.wm.read_homefile(app_template="")
        yield 1.0
        t = v3d()
        win, area, region, sp = t
        # jendela Blender utuh (toolbar, Outliner, Properties, Timeline) seperti gambar di PDF modul
        yield 0.8
        sp.shading.type = "SOLID"; sp.shading.color_type = "MATERIAL"; sp.shading.light = "STUDIO"
        sp.overlay.show_overlays = True
        for m in bpy.data.materials:
            if m.node_tree:
                b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
                if b:
                    m.diffuse_color = tuple(b.inputs["Base Color"].default_value)
        sel = [o for o in bpy.context.view_layer.objects if o.type in {"MESH", "ARMATURE"} and o.visible_get()]
        for shot in job["shots"]:
            if shot.get("frame") is not None:
                bpy.context.scene.frame_set(shot["frame"])
            win, area, region, sp = v3d()
            r3 = sp.region_3d
            if shot["view"] == "camera":
                with ov(win, area, region):
                    bpy.ops.view3d.view_camera()
            else:
                r3.view_perspective = "PERSP" if shot["view"].startswith("persp") else "ORTHO"
                r3.view_rotation = Euler(ROT[shot["view"]]).to_quaternion()
                for o in bpy.context.view_layer.objects:
                    o.select_set(o in sel)
                with ov(win, area, region):
                    bpy.ops.view3d.view_selected()
                for o in bpy.context.view_layer.objects:
                    o.select_set(False)
                r3.view_distance *= 0.85
            yield 0.7
            win, area, region, sp = v3d()
            with bpy.context.temp_override(window=win, screen=win.screen):
                bpy.ops.screen.screenshot(filepath=os.path.join(job["out"], shot["name"] + ".png"))
            print("SHOT", job["key"], shot["name"], flush=True)
            yield 0.2
    print("SELESAI", flush=True)
    bpy.ops.wm.quit_blender()
    yield None


_gen = run()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        return None
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("GAGAL", e, flush=True)
        bpy.ops.wm.quit_blender()
        return None


bpy.app.timers.register(tick, first_interval=3.0, persistent=True)
