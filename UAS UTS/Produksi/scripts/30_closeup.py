# 30 - render close-up diagnostik: CLOSE(frame, rig_name, bone, out, dist, off)
import bpy, math
from mathutils import Vector
def close(frame, rig, bone, out, dist=0.9, off=(0.0, -1.0, 0.15), res=(720, 720), samples=12):
    sc = bpy.context.scene; sc.frame_set(frame)
    R = bpy.data.objects[rig]; pb = R.pose.bones[bone]
    tgt = R.matrix_world @ pb.head
    cam = bpy.data.objects.get("_CLOSE") or bpy.data.objects.new("_CLOSE", bpy.data.cameras.new("_CLOSE"))
    if cam.name not in sc.collection.objects: sc.collection.objects.link(cam)
    cam.data.lens = 60
    d = Vector(off).normalized() * dist
    cam.location = tgt + d
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    old = (sc.camera, sc.render.resolution_x, sc.render.resolution_y, sc.render.filepath, sc.eevee.taa_render_samples)
    mk = [(m, m.camera) for m in sc.timeline_markers]
    for m, _ in mk: m.camera = None                  # penanda kamera menimpa sc.camera saat render
    sc.camera = cam; sc.render.resolution_x, sc.render.resolution_y = res; sc.eevee.taa_render_samples = samples
    sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    for m, c in mk: m.camera = c
    sc.camera,sc.render.resolution_x, sc.render.resolution_y, sc.render.filepath, sc.eevee.taa_render_samples = old
