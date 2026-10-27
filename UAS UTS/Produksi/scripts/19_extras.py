# 19 - Kehidupan jalan bergaya lukisan: pohon bercat, pejalan kaki lalu-lalang, kendaraan lewat. Material pakai toon ramp (Ghibli/Pocari sama).
import bpy, math, random
from mathutils import Vector

OB = bpy.data.objects
coll = bpy.data.collections.get("13_EXTRAS") or bpy.data.collections.new("13_EXTRAS")
if coll.name not in bpy.context.scene.collection.children.keys(): bpy.context.scene.collection.children.link(coll)
for o in list(coll.objects):
    if o.name.startswith('X_Tree') or globals().get('MAKE_ALL', True): bpy.data.objects.remove(o)
TF = bpy.app.driver_namespace["TOONFN"]; toon = TF["toon"]

def mat(name, col, **k): return toon(name, col, **k)
M_TRUNK = mat("X_Trunk", (0.55, 0.38, 0.24), shadow=(0.38, 0.24, 0.16), soft=0.25, noise=0.15)
M_LEAF1 = mat("X_Leaf1", (0.52, 0.78, 0.28), shadow=(0.30, 0.52, 0.22), soft=0.3, rim=0.3, rim_color=(1.0, 0.95, 0.6), noise=0.2)
M_LEAF2 = mat("X_Leaf2", (0.66, 0.84, 0.32), shadow=(0.36, 0.58, 0.26), soft=0.3, rim=0.3, rim_color=(1.0, 0.95, 0.6), noise=0.2)
M_CAR = mat("X_Car", (0.86, 0.28, 0.24), shadow=(0.55, 0.22, 0.38), soft=0.25, spec=0.35, rim=0.3)
M_CAR2 = mat("X_Car2", (0.30, 0.62, 0.86), shadow=(0.20, 0.34, 0.62), soft=0.25, spec=0.35, rim=0.3)
M_GLASS = mat("X_CarGlass", (0.70, 0.88, 0.96), shadow=(0.40, 0.56, 0.78), soft=0.25, spec=0.5)
M_TIRE = mat("X_Tire", (0.12, 0.12, 0.14), shadow=(0.05, 0.05, 0.08))
SKIN = bpy.data.materials["T_Skin_Cust"]
CLOTH = [mat(f"X_Cloth{i}", c, shadow=tuple(x * 0.6 for x in c), soft=0.25, rim=0.2) for i, c in enumerate(
    [(0.95, 0.55, 0.45), (0.35, 0.65, 0.85), (0.95, 0.82, 0.35), (0.55, 0.78, 0.55), (0.80, 0.55, 0.85)])]
M_HAIR = bpy.data.materials["T_Hair"]

def link(o): coll.objects.link(o) if o.name not in coll.objects else None; return o
def sphere(name, loc, r, m, sc=(1, 1, 1), seg=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=max(seg // 2, 6), radius=r, location=loc)
    o = bpy.context.active_object; o.name = name; o.scale = sc
    for p in o.data.polygons: p.use_smooth = True
    o.data.materials.append(m)
    for c in list(o.users_collection): c.objects.unlink(o)
    coll.objects.link(o); return o
def cyl(name, loc, r, h, m, rot=(0, 0, 0), vert=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vert, radius=r, depth=h, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name
    for p in o.data.polygons: p.use_smooth = True
    o.data.materials.append(m)
    for c in list(o.users_collection): c.objects.unlink(o)
    coll.objects.link(o); return o
def box(name, loc, size, m, bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.active_object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    b = o.modifiers.new("B", 'BEVEL'); b.width = bevel; b.segments = 3
    for p in o.data.polygons: p.use_smooth = True
    o.data.materials.append(m)
    for c in list(o.users_collection): c.objects.unlink(o)
    coll.objects.link(o); return o
def parent_all(root, kids):
    for k in kids: k.parent = root; k.matrix_parent_inverse = root.matrix_world.inverted()

def tree(i, x, y, h=3.4):
    rnd = random.Random(i)
    root = bpy.data.objects.new(f"X_Tree{i}", None); coll.objects.link(root); root.location = (x, y, 0)
    kids = [cyl(f"X_Tree{i}_trunk", (x, y, h * 0.3), 0.11, h * 0.6, M_TRUNK, vert=10)]
    for k in range(14):
        a = rnd.random() * 6.28; r = rnd.random() * 1.1
        kids.append(sphere(f"X_Tree{i}_leaf{k}", (x + math.cos(a) * r, y + math.sin(a) * r * 0.6, h * 0.72 + rnd.random() * 1.4), 0.45 + rnd.random() * 0.45, M_LEAF1 if k % 2 else M_LEAF2, sc=(1, 1, 0.85)))
    parent_all(root, kids)
    # goyangan daun lembut (angin)
    root.rotation_euler = (0, 0, 0)
    for f, a in ((1, 0.0), (90, 0.018), (180, -0.018), (270, 0.018), (360, 0.0)):
        root.rotation_euler = (a * 0.7, a, 0); root.keyframe_insert("rotation_euler", frame=f)
    return root

def walker(i, x0, x1, y, f0, f1, col):
    root = bpy.data.objects.new(f"X_Walker{i}", None); coll.objects.link(root)
    sgn = 1 if x1 > x0 else -1
    body = cyl(f"X_Walker{i}_body", (0, 0, 1.05), 0.17, 0.62, col, vert=12)
    head = sphere(f"X_Walker{i}_head", (0, 0, 1.55), 0.12, SKIN)
    hair = sphere(f"X_Walker{i}_hair", (0, 0.015, 1.60), 0.125, M_HAIR, sc=(1, 1, 0.8))
    legs = []
    for s in (-1, 1):
        lg = cyl(f"X_Walker{i}_leg{s}", (0.07 * s, 0, 0.40), 0.065, 0.74, CLOTH[(i + 2) % 5], vert=8)
        lg.data.transform(__import__("mathutils").Matrix.Translation((0, 0, 0.37))); lg.location = (0.07 * s, 0, 0.74)
        legs.append(lg)
    parent_all(root, [body, head, hair] + legs)
    root.location = (x0, y, 0); root.rotation_euler = (0, 0, math.radians(90 if sgn > 0 else -90) + math.radians(0))
    root.rotation_euler = (0, 0, 0)
    root.location = (x0, y, 0); root.keyframe_insert("location", frame=f0); root.location = (x1, y, 0); root.keyframe_insert("location", frame=f1)
    for fc in root.animation_data.action.layers[0].strips[0].channelbags[0].fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    # ayunan kaki + naik-turun badan
    for lg, ph in zip(legs, (0, math.pi)):
        for f in range(f0, f1 + 1, 8):
            lg.rotation_euler = (math.sin((f - f0) * 0.34 + ph) * 0.45, 0, 0); lg.keyframe_insert("rotation_euler", frame=f)
    for f in range(f0, f1 + 1, 8):
        body.location.z = 1.05 + abs(math.sin((f - f0) * 0.34)) * 0.025; body.keyframe_insert("location", index=2, frame=f)
    return root

def car(i, x0, x1, y, f0, f1, body_m):
    root = bpy.data.objects.new(f"X_Car{i}", None); coll.objects.link(root)
    kids = [box(f"X_Car{i}_low", (0, 0, 0.55), (1.0, 2.1, 0.32), body_m, 0.12), box(f"X_Car{i}_top", (0, -0.1, 1.05), (0.78, 1.0, 0.30), M_GLASS, 0.14)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            kids.append(cyl(f"X_Car{i}_w", (0.95 * sx, 1.35 * sy, 0.32), 0.32, 0.22, M_TIRE, rot=(0, math.radians(90), 0), vert=14))
    parent_all(root, kids)
    root.rotation_euler = (0, 0, math.radians(90 if x1 > x0 else -90))
    root.location = (x0, y, 0); root.keyframe_insert("location", frame=f0); root.location = (x1, y, 0); root.keyframe_insert("location", frame=f1)
    for fc in root.animation_data.action.layers[0].strips[0].channelbags[0].fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    return root

# pohon di tepi (kiri-kanan warung, di belakang tembok bawah) dan di sisi jalan
if True:
  for i, (x, y) in enumerate(((-3.6, 1.8), (3.8, 2.2), (-6.5, 0.8), (6.8, 1.2), (-2.2, -6.2), (4.6, -6.0))): tree(i, x, y)
if globals().get('MAKE_ALL', True):
    pass
print('pohon:', len([o for o in coll.objects if o.name.startswith('X_Tree') and o.type=='EMPTY']))
