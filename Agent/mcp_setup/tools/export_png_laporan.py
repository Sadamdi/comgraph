"""Render hasil modul ke PNG untuk laporan (sudut pandang mengikuti gambar hasil akhir di PDF modul).

Dijalankan di Blender latar belakang, file .blend TIDAK diubah/disimpan:
    blender -b "<file.blend>" --factory-startup -P export_png_laporan.py -- "<out_dir>" "<prefix>" "<view1,view2>" [opsi...]
view : front | back | right | left | top | persp | persp_left | persp_front | head | camera
opsi : frames=1,10,20   -> render tiap frame (animasi)
       bones=1          -> tampilkan tulang armature (dibuat mesh sementara, karena Workbench tidak menggambar bone)
       start=N          -> nomor gambar pertama (default 1)
Nama file: "<prefix> (n).png"; kalau hanya 1 gambar: "<prefix>.png".
"""
import bpy, sys, math, bmesh
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
out_dir, prefix, views = argv[0], argv[1], argv[2].split(",")
opt = dict(a.split("=", 1) for a in argv[3:] if "=" in a)
frames = [int(f) for f in opt.get("frames", str(bpy.context.scene.frame_current)).split(",")]
show_bones = opt.get("bones") == "1"
num = int(opt.get("start", "1"))

sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light = "STUDIO"; sh.color_type = "MATERIAL"; sh.single_color = (0.8, 0.8, 0.8)
sh.show_cavity = True; sh.cavity_type = "WORLD"; sh.show_object_outline = True
sh.background_type = "WORLD"
sc.display.render_aa = "16"
if sc.world is None:
    sc.world = bpy.data.worlds.new("W")
sc.world.color = (0.045, 0.045, 0.045)        # abu gelap seperti viewport Blender
# warna Solid diambil dari Base Color node material (hanya di sesi render ini, file tidak disimpan)
for m in bpy.data.materials:
    if m.node_tree:
        bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf:
            m.diffuse_color = tuple(bsdf.inputs["Base Color"].default_value)
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 100
sc.render.image_settings.file_format = "PNG"
sc.render.film_transparent = False

bone_mat = bpy.data.materials.new("TulangLaporan"); bone_mat.diffuse_color = (0.35, 0.65, 1.0, 1.0)


def make_bones():
    """Octahedron per pose bone (bentuk bone default Blender), objek sementara."""
    old = bpy.data.objects.get("TulangLaporan")
    if old:
        bpy.data.objects.remove(old)
    me = bpy.data.meshes.new("TulangLaporan"); bm = bmesh.new()
    for arm in [o for o in sc.objects if o.type == "ARMATURE"]:
        for pb in arm.pose.bones:
            h = arm.matrix_world @ pb.head; t = arm.matrix_world @ pb.tail
            d = t - h; L = d.length
            if L < 1e-6:
                continue
            ax = d.normalized(); up = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
            u = ax.cross(up).normalized() * L * 0.1; w = ax.cross(u).normalized() * L * 0.1
            mid = h + d * 0.2
            vs = [bm.verts.new(p) for p in (h, mid + u, mid + w, mid - u, mid - w, t)]
            for a, b in ((1, 2), (2, 3), (3, 4), (4, 1)):
                bm.faces.new((vs[0], vs[b], vs[a])); bm.faces.new((vs[5], vs[a], vs[b]))
    bm.to_mesh(me); bm.free(); me.materials.append(bone_mat)
    ob = bpy.data.objects.new("TulangLaporan", me); sc.collection.objects.link(ob)
    ob.show_in_front = True


def scene_points():
    dg = bpy.context.evaluated_depsgraph_get(); pts = []
    for o in sc.objects:
        if o.type == "MESH" and not o.hide_render and o.visible_get():
            ev = o.evaluated_get(dg); me = ev.to_mesh()
            pts += [o.matrix_world @ v.co for v in me.vertices]
            ev.to_mesh_clear()
    return pts


scene_cam = sc.camera
cam = bpy.data.objects.new("CamLaporan", bpy.data.cameras.new("CamLaporan"))
sc.collection.objects.link(cam)
DIRS = {  # (azimut derajat dari -Y ke +X, elevasi derajat)
    "front": (0, 0), "back": (180, 0), "right": (90, 0), "left": (-90, 0), "top": (0, 89.9),
    "persp": (35, 18), "persp_left": (-35, 18), "persp_front": (0, 12), "head": (25, 5),
}
total = len(frames) * len(views)
for fr in frames:
    sc.frame_set(fr)
    if show_bones:
        make_bones()
    pts_all = scene_points()
    for view in views:
        if view == "camera" and scene_cam:
            sc.camera = scene_cam
        else:
            sc.camera = cam
            pts = pts_all
            if view == "head":   # close-up wajah: bagian teratas, dekat garis tengah (tanpa lengan T-pose)
                zmax = max(p.z for p in pts_all); zmin = min(p.z for p in pts_all); H = zmax - zmin
                cx = sum(p.x for p in pts_all) / len(pts_all)
                pts = [p for p in pts_all if p.z > zmax - 0.17 * H and abs(p.x - cx) < 0.09 * H]
            az, el = DIRS[view]
            d = Vector((math.sin(math.radians(az)) * math.cos(math.radians(el)),
                        -math.cos(math.radians(az)) * math.cos(math.radians(el)),
                        math.sin(math.radians(el))))
            cam.rotation_mode = "QUATERNION"; cam.rotation_quaternion = d.to_track_quat("Z", "Y")
            persp = view.startswith("persp") or view == "head"
            cam.data.type = "PERSP" if persp else "ORTHO"; cam.data.lens = 50; cam.data.sensor_fit = "AUTO"
            # framing manual: proyeksikan titik ke sumbu kamera (camera_fit_coords salah untuk model lebar)
            Rm = cam.rotation_quaternion.to_matrix()
            right, up = Rm.col[0], Rm.col[1]
            xs = [p.dot(right) for p in pts]; ys = [p.dot(up) for p in pts]; ds = [p.dot(d) for p in pts]
            w, h = max(xs) - min(xs), max(ys) - min(ys)
            xc, yc = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
            aspect = sc.render.resolution_x / sc.render.resolution_y
            if persp:
                half_h = math.atan(18 / 50); half_v = math.atan(18 / 50 / aspect)
                dist = max(w / 2 / math.tan(half_h), h / 2 / math.tan(half_v)) * (1.4 if view == "head" else 1.15)
                cam.location = right * xc + up * yc + d * ((max(ds) + min(ds)) / 2 + dist + (max(ds) - min(ds)) / 2)
            else:
                cam.data.ortho_scale = max(w, h * aspect) * 1.12
                cam.location = right * xc + up * yc + d * (max(ds) + 50)
            cam.data.clip_start, cam.data.clip_end = 0.1, 100000
        name = prefix if total == 1 else "%s (%d)" % (prefix, num)
        sc.render.filepath = out_dir + "/" + name + ".png"
        bpy.ops.render.render(write_still=True)
        print("SAVED", sc.render.filepath)
        num += 1
