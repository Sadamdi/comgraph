# 26 - Dekorasi warung dari Poly Haven (CC0): lentera gantung, radio kaset di meja, tong, kursi kayu, pot keramik. Material ikut gaya (dilukis di Ghibli, PBR asli di Pocari lewat set_realistic()).
import bpy, math, glob
from mathutils import Vector
OB = bpy.data.objects
BASE = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\assets\polyhaven" + "\\"
coll = bpy.data.collections.get("15_DRESS") or bpy.data.collections.new("15_DRESS")
if coll.name not in bpy.context.scene.collection.children.keys(): bpy.context.scene.collection.children.link(coll)
for o in [o for o in OB if o.name.startswith("DR_")]: bpy.data.objects.remove(o)

def load(name):
    pre = set(OB.keys()); bpy.ops.import_scene.gltf(filepath=glob.glob(BASE + name + "\\*.gltf")[0])
    new = [OB[k] for k in OB.keys() if k not in pre]
    root = bpy.data.objects.new("DR_" + name, None); coll.objects.link(root)
    for o in new:
        for c in list(o.users_collection): c.objects.unlink(o)
        coll.objects.link(o)
        if o.parent is None: o.parent = root
    bpy.context.view_layer.update()
    meshes = [o for o in new if o.type == 'MESH']
    pts = [o.matrix_world @ Vector(b) for o in meshes for b in o.bound_box]
    return root, meshes, (min(p.z for p in pts), max(p.z for p in pts)), (max(p.x for p in pts) - min(p.x for p in pts), max(p.y for p in pts) - min(p.y for p in pts))

def place(name, loc, height, yaw=0.0):
    root, meshes, (z0, z1), _ = load(name)
    s = height / max(z1 - z0, 1e-4); root.scale = (s,) * 3; root.rotation_euler = (0, 0, math.radians(yaw))
    root.location = (loc[0], loc[1], loc[2] - z0 * s)
    return root, meshes

mats = set()
r_l, m_l = place("Lantern_01", (1.30, -0.18, 2.12), 0.34)          # tergantung di sudut kanopi
for f, a in ((1, 0.0), (70, 3.5), (150, -3.0), (230, 2.5), (310, 0.0)):
    r_l.rotation_euler = (math.radians(a * 0.4), math.radians(a), 0); r_l.keyframe_insert("rotation_euler", frame=f)
for fc in r_l.animation_data.action.layers[0].strips[0].channelbags[0].fcurves:
    fc.modifiers.new('CYCLES')
r_r, m_r = place("cassette_player", (0.78, 0.36, 1.19), 0.16, yaw=-15)
r_b, m_b = place("Barrel_01", (-1.95, 0.35, 0.0), 0.78, yaw=30)
r_c, m_c = place("WoodenChair_01", (-2.75, 0.55, 0.0), 0.88, yaw=-35)
r_p, m_p = place("ceramic_pot", (2.1, 0.30, 0.0), 0.42)
for ms in (m_l, m_r, m_b, m_c, m_p):
    for o in ms:
        for s in o.material_slots:
            if s.material: mats.add(s.material)
# warnai ikut gaya Ghibli (rantai GHIBLI) agar menyatu; Pocari memakai Principled asli lewat set_realistic()
try:
    for m in mats:
        if m.use_nodes and not any(n.label == "GHIBLI" for n in m.node_tree.nodes): paint_material(m, brush=0.08)
except NameError:
    print("paint_material belum dimuat (jalankan 16_ghibli_look dulu)")
# lampu lentera menyala hangat (di dalam lentera)
ll = bpy.data.lights.new("DR_Lantern_light", 'POINT'); ll.energy = 18; ll.color = (1.0, 0.72, 0.38); ll.shadow_soft_size = 0.05
lo = bpy.data.objects.new("DR_Lantern_light", ll); coll.objects.link(lo); lo.parent = r_l; lo.location = (0, 0, 0.12 / max(r_l.scale.x, 1e-3))
print("dekorasi:", [o.name for o in OB if o.name.startswith("DR_") and o.type == 'EMPTY'])
