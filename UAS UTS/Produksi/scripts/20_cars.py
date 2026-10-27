# 20 - Mobil dari Kenney Car Kit (CC0) menggantikan mobil primitif; roda berputar; dicat toon via paint_material (16_ghibli_look)
import bpy, math
from mathutils import Vector

OB = bpy.data.objects
for o in list(OB):
    if o.name.startswith(("X_Car", "X_Walker")): bpy.data.objects.remove(o)
coll = bpy.data.collections["13_EXTRAS"]
BASE = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\assets\kenney\car-kit\Models\FBX format" + "\\"
YAW0 = globals().get("CAR_YAW0", 0.0)    # koreksi arah depan model (derajat)
SC = 1.7

def get_car(name, tag):
    root = OB.get(name)
    if root is None:
        before = set(OB.keys()); bpy.ops.import_scene.fbx(filepath=BASE + name + ".fbx"); root = OB[name]
    return root

def drive(tag, name, x0, x1, y, f0, f1):
    src = get_car(name, tag)
    # duplikat hierarki (tiap mobil unik) bila sudah dipakai
    if src.get("used"):
        kids = [src] + list(src.children_recursive); mp = {}
        for o in kids:
            c = o.copy(); c.data = o.data if o.data else None
            if o.type == 'MESH': c.data = o.data
            mp[o] = c; coll.objects.link(c)
        for o, c in mp.items():
            c.parent = mp.get(o.parent, None) if o.parent else None
            c.matrix_parent_inverse = o.matrix_parent_inverse.copy()
        root = mp[src]
    else:
        root = src; src["used"] = True
        for c in list(root.users_collection): c.objects.unlink(root)
        coll.objects.link(root)
        for k in root.children_recursive:
            for c in list(k.users_collection): c.objects.unlink(k)
            coll.objects.link(k)
    root.name = tag
    root.scale = (0.01 * SC,) * 3
    sgn = 1 if x1 > x0 else -1
    root.rotation_euler = (math.pi / 2, 0, math.radians((-90 if sgn > 0 else 90) + YAW0))
    root.location = (x0, y, 0); root.animation_data_clear() if root.animation_data else None
    root.keyframe_insert("location", frame=f0)
    root.location = (x1, y, 0); root.keyframe_insert("location", frame=f1)
    for fc in root.animation_data.action.layers[0].strips[0].channelbags[0].fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    # roda berputar
    dist = abs(x1 - x0); turns = dist / (2 * math.pi * 0.30)
    for w in root.children_recursive:
        if "wheel" in w.name.lower():
            w.rotation_mode = 'XYZ'; w.keyframe_insert("rotation_euler", frame=f0)
            r = list(w.rotation_euler); r[0] += sgn * turns * 2 * math.pi * (1 if YAW0 == 0 else 1); w.rotation_euler = r
            w.keyframe_insert("rotation_euler", frame=f1)
            for fc in w.animation_data.action.layers[0].strips[0].channelbags[0].fcurves:
                for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    return root

drive("CAR_A", "sedan", -16, 16, -9.2, 60, 330)
drive("CAR_B", "taxi", 16, -16, -10.4, 700, 960)
drive("CAR_C", "van", -16, 16, -9.2, 1500, 1780)
drive("CAR_D", "hatchback-sports", 16, -16, -10.4, 2200, 2480)
print("mobil:", [o.name for o in OB if o.name.startswith("CAR_")])
