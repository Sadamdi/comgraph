# 00 - alat bantu: render uji 1 frame & contact sheet (dipakai tiap tahap)
import bpy, os, time, math

SCR = r"C:\Users\A16\AppData\Local\Temp\claude\D--adam-kuliah-Semester-5-Computer-Graphic\9b31a844-a023-4df1-b2d6-04f4531e4325\scratchpad"
SHOT_FRAMES = {1:1, 2:241, 3:391, 4:541, 5:661, 6:841, 7:1081, 8:1321, 9:1501, 10:1741, 11:1951, 12:2101, 13:2311, 14:2461}
# frame representatif per shot (tengah aksi)
MID = {1:120, 2:385, 3:460, 4:600, 5:750, 6:1060, 7:1200, 8:1430, 9:1700, 10:1840, 11:2030, 12:2290, 13:2390, 14:2590}

def shot(frame, tag, pct=40, samples=24):
    sc = bpy.context.scene
    old = (sc.render.resolution_percentage, sc.eevee.taa_render_samples, sc.render.filepath, sc.frame_current)
    sc.render.resolution_percentage = pct
    sc.eevee.taa_render_samples = samples
    sc.frame_set(frame)
    path = os.path.join(SCR, f"{tag}_{frame:04d}.png")
    sc.render.filepath = path
    t = time.time()
    bpy.ops.render.render(write_still=True)
    dt = time.time() - t
    sc.render.resolution_percentage, sc.eevee.taa_render_samples, sc.render.filepath = old[0], old[1], old[2]
    sc.frame_set(old[3])
    return path, round(dt, 2)

def shots(frames, tag, pct=40, samples=24):
    out = []
    for f in frames:
        out.append(shot(f, tag, pct, samples))
    return out

def dbg_cam(name="DBG_CAM", pos=(0,-5,1), tgt=(0,0,1), ortho=None, lens=35):
    o = bpy.data.objects.get(name)
    if o is None:
        cd = bpy.data.cameras.new(name); o = bpy.data.objects.new(name, cd); bpy.context.scene.collection.objects.link(o)
    from mathutils import Vector
    o.location = Vector(pos)
    d = (Vector(tgt) - Vector(pos)); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if ortho: o.data.type = 'ORTHO'; o.data.ortho_scale = ortho
    else: o.data.type = 'PERSP'; o.data.lens = lens
    o.data.dof.use_dof = False
    return o

def shotcam(frame, cam, tag, pct=30, samples=12):
    sc = bpy.context.scene
    old = (sc.render.resolution_percentage, sc.eevee.taa_render_samples, sc.render.filepath, sc.frame_current, sc.camera)
    sc.render.resolution_percentage = pct; sc.eevee.taa_render_samples = samples
    mk=[(m,m.camera) for m in sc.timeline_markers]
    for m,_ in mk: m.camera=None
    sc.frame_set(frame); sc.camera = cam
    path = os.path.join(SCR, f"{tag}_{frame:04d}.png"); sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    sc.render.resolution_percentage, sc.eevee.taa_render_samples, sc.render.filepath = old[0], old[1], old[2]
    for m,c in mk: m.camera=c
    sc.frame_set(old[3]); sc.camera = old[4]
    return path

bpy.app.driver_namespace["T"] = {"dbg_cam": dbg_cam, "shotcam": shotcam,"shot": shot, "shots": shots, "MID": MID, "SCR": SCR}
print("tools ok")
