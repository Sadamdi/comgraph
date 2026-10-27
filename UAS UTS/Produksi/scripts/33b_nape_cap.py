# 33b - Penutup tengkuk rambut: salin wajah kepala bagian belakang (antara zmin+zlo_off dan zmin+zhi_off), dinaikkan 5,8 mm sbg objek <NAMA>_HAIR_NAPE
# (rambut lama berhenti membentuk V sehingga kulit tengkuk terlihat). Arah belakang diturunkan dari posisi mata -> berlaku utk semua rig.
# Dipakai: nape_cap2("LASTRI", 0.036, 0.18) ; nape_cap2("MHS", 0.036, 0.175)   (jalankan pada frame 1)
import bpy, bmesh
from mathutils import Vector

def nape_cap2(nm, zlo_off=0.036, zhi_off=0.18, off=0.0058):
    sc = bpy.context.scene; sc.frame_set(1)
    H = bpy.data.objects[nm + "_HAIR"]; Hd = bpy.data.objects[nm + "_HEAD"]
    for o in [o for o in bpy.data.objects if o.name == nm + "_HAIR_NAPE"]: bpy.data.objects.remove(o)
    Wd = Hd.matrix_world
    ctr = sum(((Wd @ v.co) for v in Hd.data.vertices), Vector()) / len(Hd.data.vertices)
    eyes = (bpy.data.objects[nm + "_eye_L"].matrix_world.translation + bpy.data.objects[nm + "_eye_R"].matrix_world.translation) / 2
    fwd = Vector((eyes.x - ctr.x, eyes.y - ctr.y, 0)).normalized(); back = -fwd
    zmin = min((Wd @ v.co).z for v in Hd.data.vertices)
    bm = bmesh.new(); bm.from_mesh(Hd.data); bm.faces.ensure_lookup_table()
    kill = []
    for f in bm.faces:
        c = Wd @ f.calc_center_median()
        if not ((c - ctr).dot(back) > 0.0 and zmin + zlo_off < c.z < zmin + zhi_off): kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS'); bm.normal_update()
    for v in bm.verts: v.co = v.co + v.normal * off
    me = bpy.data.meshes.new(nm + "_HAIR_NAPE"); bm.to_mesh(me); n = len(bm.faces); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(nm + "_HAIR_NAPE", me); H.users_collection[0].objects.link(o)
    o.parent = Hd; o.matrix_parent_inverse = H.matrix_parent_inverse.copy()
    for s in H.material_slots: me.materials.append(s.material)
    hm = H.modifiers[0]; sd = next((m for m in Hd.modifiers if m.type == 'SUBSURF'), None)
    if sd:
        m = o.modifiers.new("Subsurf", 'SUBSURF'); m.levels = sd.levels; m.render_levels = sd.render_levels
    so = o.modifiers.new("Outline", 'SOLIDIFY'); so.thickness = hm.thickness; so.offset = hm.offset
    so.use_flip_normals = hm.use_flip_normals; so.material_offset = hm.material_offset; so.use_rim = hm.use_rim
    return {"faces": n, "back": [round(x, 2) for x in back]}
