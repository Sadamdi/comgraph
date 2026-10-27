# 23 - Tanaman realistis (Poly Haven, CC0; assets/polyhaven): pohon pachira & island tree, semak, pot. Menggantikan pohon primitif X_Tree*.
# Impor dulu (gltf) bila belum ada; templat disembunyikan, instans memakai data mesh yang sama (hemat memori).
import bpy, math, glob, random
from mathutils import Vector

OB = bpy.data.objects
BASE = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\assets\polyhaven" + "\\"
coll = bpy.data.collections.get("14_POLYHAVEN") or bpy.data.collections.new("14_POLYHAVEN")
if coll.name not in bpy.context.scene.collection.children.keys(): bpy.context.scene.collection.children.link(coll)

def ensure(name):
    if any(o.name.startswith(name) for o in OB): return
    pre = set(OB.keys()); bpy.ops.import_scene.gltf(filepath=glob.glob(BASE + name + "\\*.gltf")[0])
    for k in OB.keys():
        if k not in pre:
            o = OB[k]
            for c in list(o.users_collection): c.objects.unlink(o)
            coll.objects.link(o)

for n in ("pachira_aquatica_01", "island_tree_02", "potted_plant_01", "shrub_01"): ensure(n)
for o in [o for o in OB if o.name.startswith("X_Tree")]: bpy.data.objects.remove(o)
for o in [o for o in OB if o.name.startswith("PL_")]: bpy.data.objects.remove(o)

TEMPLATES = {"pachira": ["pachira_aquatica_01_bark_b", "pachira_aquatica_01_leaves_b"], "island": ["island_tree_02_LOD0"],
             "pot": ["potted_plant_01_leaves", "potted_plant_01_pebbles", "potted_plant_01_pot", "potted_plant_01_stem"], "shrub": ["shrub_01_a"]}
used = set(sum(TEMPLATES.values(), []))
for o in OB:
    if o.name.startswith(("pachira_aquatica_01", "island_tree_02", "potted_plant_01", "shrub_01")):
        o.hide_render = True; o.hide_viewport = True; o.location = (0, 0, -60) if o.name in used else o.location
for o in OB:
    if o.name.startswith("pachira_aquatica_01") and o.name not in used: o.location.z = -60

def inst(kind, tag, loc, scale, yaw, sway=0.012):
    root = bpy.data.objects.new("PL_" + tag, None); coll.objects.link(root)
    root.location = loc; root.rotation_euler = (0, 0, math.radians(yaw)); root.scale = (scale,) * 3
    for tn in TEMPLATES[kind]:
        t = OB[tn]; c = t.copy(); c.data = t.data; c.name = f"PL_{tag}_{tn}"
        coll.objects.link(c); c.parent = root; c.location = (-t.location.x if False else 0, 0, 0)
        # templat pachira_b berada di x=0, island di 0 -> pusatkan pada akar
        c.location = (0, 0, 0); c.hide_render = False; c.hide_viewport = False
        c.rotation_euler = (0, 0, 0); c.scale = (1, 1, 1)
    if sway:
        for f, a in ((1, 0.0), (80, sway), (170, -sway), (260, sway), (350, 0.0)):
            root.rotation_euler = (a * 0.6, a, math.radians(yaw)); root.keyframe_insert("rotation_euler", frame=f)
        for fc in root.animation_data.action.layers[0].strips[0].channelbags[0].fcurves:
            for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'
            fc.modifiers.new('CYCLES')
    return root

inst("island", "T0", (-4.2, 2.4, 0), 2.1, 20)
inst("island", "T1", (4.6, 2.8, 0), 2.3, 70)
inst("island", "T2", (-8.0, 1.6, 0), 2.5, 140)
inst("island", "T3", (8.6, 1.8, 0), 2.4, 250)
inst("island", "T4", (-9.5, -5.9, 0), 2.0, 10)
inst("island", "T5", (10.0, -5.9, 0), 2.2, 200)
inst("pot", "P0", (-1.62, -0.42, 0.0), 1.1, 40, sway=0.0)
inst("pot", "P1", (1.62, -0.42, 0.0), 0.95, 200, sway=0.0)
inst("shrub", "S0", (-2.4, 1.75, 0), 1.0, 0, sway=0.01)
inst("shrub", "S1", (2.8, 1.75, 0), 1.0, 180, sway=0.01)
print("tanaman:", len([o for o in OB if o.name.startswith("PL_") and o.type == 'EMPTY']))
