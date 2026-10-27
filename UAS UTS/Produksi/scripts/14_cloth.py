# 14 - Simulasi fisika (wajib poin 8): spanduk kain tertiup angin (Cloth + Wind force field), teks mengikuti lewat Surface Deform
import bpy, bmesh, math, random
from mathutils import Vector

OB = bpy.data.objects; SC = bpy.context.scene
rad = math.radians
random.seed(8)
F = bpy.app.driver_namespace["MATFN"]; L = bpy.app.driver_namespace["MATLIB"]
C_DET = bpy.data.collections["11_SET_DETAIL"]

b = OB.get("Spanduk_Kain") or OB["PLAN_ClothBanner_not_simulated"]
b.name = "Spanduk_Kain"
tx = OB.get("Banner words") or OB["Spanduk_Teks"]
print("teks spanduk:", tx.data.body if tx.type == "FONT" else "(mesh)")

W, H = 0.56, 0.30
TOP = (-1.20, -0.80, 2.42)           # tepi atas (dijepit di balok depan)
# ---------- mesh kain: grid 28 x 16 ----------
nx, ny = 28, 16
bm = bmesh.new()
g = [[bm.verts.new(((i / nx - 0.5) * W, 0.0, -(j / ny) * H)) for i in range(nx + 1)] for j in range(ny + 1)]
for j in range(ny):
    for i in range(nx):
        bm.faces.new((g[j][i], g[j][i + 1], g[j + 1][i + 1], g[j + 1][i]))
me = bpy.data.meshes.new("Spanduk_Kain_mesh"); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth = True
old = b.data
b.data = me
b.rotation_euler = (0, 0, 0); b.scale = (1, 1, 1); b.location = TOP
me.materials.clear(); me.materials.append(L["mustard"])
mat = L["mustard"]
for m in list(b.modifiers): b.modifiers.remove(m)
if b.animation_data: b.animation_data_clear()
# grup titik jepit (2 baris atas)
vg = b.vertex_groups.get("pin") or b.vertex_groups.new(name="pin")
for v in me.vertices:
    if v.co.z > -H / ny * 1.5: vg.add([v.index], 1.0, 'REPLACE')
# ---------- Cloth ----------
cl = b.modifiers.new("Cloth", 'CLOTH')
s = cl.settings
s.quality = 7; s.mass = 0.06
s.tension_stiffness = 5; s.compression_stiffness = 5; s.shear_stiffness = 3; s.bending_stiffness = 0.08
s.tension_damping = 1.0; s.compression_damping = 1.0; s.shear_damping = 1.0; s.bending_damping = 0.2; s.air_damping = 0.15
s.vertex_group_mass = "pin"
cl.collision_settings.use_collision = False
cl.collision_settings.use_self_collision = False
pc = cl.point_cache; pc.frame_start = 1; pc.frame_end = 2700
sd = b.modifiers.new("Tebal", 'SOLIDIFY'); sd.thickness = 0.004; sd.offset = 0.0
# ---------- Angin ----------
w = OB.get("WIND_Spanduk")
if w is None or w.field is None:
    if w is not None: OB.remove(w)
    bpy.ops.object.effector_add(type='WIND', location=(-1.20, -2.2, 2.30), rotation=(rad(-90), 0, 0))
    w = bpy.context.view_layer.objects.active; w.name = "WIND_Spanduk"
    for c in list(w.users_collection): c.objects.unlink(w)
    C_DET.objects.link(w)
w.field.type = 'WIND'
w.location = (-1.20, -2.2, 2.30); w.rotation_euler = (rad(-90), 0, 0)
w.field.noise = 0.8; w.field.flow = 0.0; w.field.use_max_distance = False
w.field.shape = 'PLANE'
if w.animation_data: w.animation_data_clear()
f = 1
while f <= 2700:
    base = 330 + 170 * math.sin(f / 70.0) + random.uniform(-50, 50)
    gust = 350 if f in (1, 31, 2461, 2491) else 0
    w.field.strength = max(90.0, base + gust)
    w.field.keyframe_insert("strength", frame=f)
    f += 30
# ---------- teks mengikuti kain (Surface Deform) ----------
if tx.type == 'FONT':
    for m in list(tx.modifiers): tx.modifiers.remove(m)
    tx.parent = None
    tx.data.size = 0.075; tx.data.align_x = 'CENTER'; tx.data.align_y = 'CENTER'
    tx.data.extrude = 0.002
    tx.location = (TOP[0], TOP[1] - 0.006, TOP[2] - H / 2); tx.rotation_euler = (rad(90), 0, 0)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = tx; tx.select_set(True)
    bpy.ops.object.convert(target='MESH')
    tx = bpy.context.view_layer.objects.active; tx.name = "Spanduk_Teks"
    tx.data.materials.clear(); tx.data.materials.append(F["paint"]("M_SpandukTeks", (0.10, 0.07, 0.05), rough=0.7, noise_bump=0.0, dirt=0.0))
    sdf = tx.modifiers.new("Ikut kain", 'SURFACE_DEFORM'); sdf.target = b
else:
    sdf = tx.modifiers["Ikut kain"]
    if sdf.is_bound:
        with bpy.context.temp_override(object=tx, active_object=tx):
            bpy.ops.object.surfacedeform_bind(modifier="Ikut kain")     # lepas ikatan lama
    tx.location = (TOP[0], TOP[1] - 0.006, TOP[2] - H / 2)
    sdf.target = b
SC.frame_set(1)
bpy.context.view_layer.update()
with bpy.context.temp_override(object=tx, active_object=tx):
    bpy.ops.object.surfacedeform_bind(modifier="Ikut kain")
print("spanduk siap; bind:", sdf.is_bound)
