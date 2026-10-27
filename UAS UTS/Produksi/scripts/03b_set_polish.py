# 03b - Poles set warung: material PBR, bevel, tenda kain bergaris + valance, rangka kayu, lampu gantung (bandul), kompor & wajan, properti
import bpy, bmesh, math, random
from mathutils import Vector

L = bpy.app.driver_namespace["MATLIB"]
F = bpy.app.driver_namespace["MATFN"]
random.seed(21)
OB = bpy.data.objects
_dc = bpy.data.collections.get('11_SET_DETAIL')
if _dc:
    for _o in list(_dc.objects): bpy.data.objects.remove(_o)

def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c
C_ROOT = coll("10_PRODUKSI"); C_DET = coll("11_SET_DETAIL", C_ROOT)

def new_box(name, x0, x1, y0, y1, z0, z1, mat, bevel=0.01, seg=2, c=None):
    c = c or C_DET
    hx, hy, hz = (x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=2.0)
    for v in bm.verts: v.co.x *= hx; v.co.y *= hy; v.co.z *= hz
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); c.objects.link(o)
    me.materials.append(mat)
    if bevel > 0:
        b = o.modifiers.new("Bevel", 'BEVEL'); b.width = bevel; b.segments = seg; b.limit_method = 'ANGLE'
    for p in me.polygons: p.use_smooth = False
    return o

def cyl(name, r, h, loc, mat, rot=(0, 0, 0), seg=24, c=None, bevel=0.0, cap=True):
    c = c or C_DET
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=cap, segments=seg, radius1=r, radius2=r, depth=h)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = loc; o.rotation_euler = rot; c.objects.link(o); me.materials.append(mat)
    if bevel > 0:
        b = o.modifiers.new("Bevel", 'BEVEL'); b.width = bevel; b.segments = 2
    return o

def sphere(name, r, loc, mat, scale=(1, 1, 1), c=None, seg=24, rings=14):
    c = c or C_DET
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r)
    for v in bm.verts: v.co.x *= scale[0]; v.co.y *= scale[1]; v.co.z *= scale[2]
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = loc; c.objects.link(o); me.materials.append(mat); return o

def hide(*names):
    for n in names:
        o = OB.get(n)
        if o: o.hide_render = True; o.hide_viewport = True

def bevel_existing(o, w=0.012, seg=2):
    if not any(m.type == 'BEVEL' for m in o.modifiers):
        b = o.modifiers.new("Bevel", 'BEVEL'); b.width = w; b.segments = seg; b.limit_method = 'ANGLE'

# ---------- material pada objek set milik teman ----------
asg = F["assign"]
asg(OB["Counter base"], L["wood_paint"]); bevel_existing(OB["Counter base"], 0.015)
asg(OB["Counter top"], L["wood_counter"]); bevel_existing(OB["Counter top"], 0.012)
for n in ("Rear support", "Rear support.001"):
    asg(OB[n], L["wood_post"]); bevel_existing(OB[n], 0.008)
for n in ("Sign cord", "Sign cord.001"):
    asg(OB[n], L["wood_post"])
asg(OB["Hanging sign"], L["sign_teal"]); bevel_existing(OB["Hanging sign"], 0.012)
asg(OB["Wall base"], F["paint"]("M_WallBase", (0.05, 0.38, 0.40), rough=0.45, spec=0.5, noise_bump=0.05, dirt=0.35))
asg(OB["Display tray"], L["metal"]); bevel_existing(OB["Display tray"], 0.006)
asg(OB["Tongs"], L["metal"])
asg(OB["Small menu"], L["paper"]); asg(OB["PLAN_ClothBanner_not_simulated"], L["mustard"])
white_text = F["paint"]("M_TextCream", (0.96, 0.93, 0.85), rough=0.6, noise_bump=0.0, dirt=0.0)
dark_text = F["paint"]("M_TextDark", (0.10, 0.08, 0.07), rough=0.6, noise_bump=0.0, dirt=0.0)
for n, m in (("Warung name", white_text), ("Banner words", dark_text), ("Menu text", dark_text)):
    o = OB.get(n)
    if o:
        o.data.materials.clear(); o.data.materials.append(m)
        o.data.extrude = 0.004
        if hasattr(o.data, "bevel_depth"): o.data.bevel_depth = 0.0015
rnd = random.Random(4)
for o in OB:
    pass
for o in [x for x in OB if x.name.startswith("Gorengan")]:
    asg(o, L["food"])
    if not any(m.type == 'SUBSURF' for m in o.modifiers):
        s = o.modifiers.new("Sub", 'SUBSURF'); s.levels = 1; s.render_levels = 2
    for p in o.data.polygons: p.use_smooth = True
    o.scale = (rnd.uniform(0.92, 1.12), rnd.uniform(0.9, 1.1), rnd.uniform(0.9, 1.15))
# tanah lebih gelap & kotor agar tidak terlalu putih
OB["Ground"].data.materials.clear()
OB["Ground"].data.materials.append(F["pbr"]("M_Paving2", "large_floor_tiles_02", scale=0.45, tint=(0.62, 0.58, 0.52), tint_mix=0.9, normal=0.9, rough_mul=1.0))

# ---------- sembunyikan yang diganti ----------
hide("Back wall", "Canopy")
for n in [x.name for x in OB if x.name.startswith("Canopy stripe")]: hide(n)

# ---------- panel & trim meja ----------
wp = L["wood_paint"]; dark = F["paint"]("M_WoodDark", (0.34, 0.18, 0.11), rough=0.55, noise_bump=0.02, dirt=0.10, noise_scale=6.0)
for i, x in enumerate((-0.97, 0.0, 0.97)):
    new_box(f"Panel_{i}", x - 0.40, x + 0.40, -0.215, -0.19, 0.18, 0.98, dark, 0.012)
    new_box(f"PanelFrame_{i}", x - 0.43, x + 0.43, -0.215, -0.205, 0.15, 1.01, wp, 0.008)
new_box("Plinth", -1.47, 1.47, -0.23, 0.5, 0.0, 0.14, dark, 0.012)
new_box("CornerTrimL", -1.47, -1.40, -0.22, -0.17, 0.0, 1.10, wp, 0.006)
new_box("CornerTrimR", 1.40, 1.47, -0.22, -0.17, 0.0, 1.10, wp, 0.006)

# ---------- rangka kayu & tenda kain bergaris ----------
beam = L["wood_post"]
for x in (-1.5, 0.0, 1.5):
    new_box(f"Beam_{x}", x - 0.035, x + 0.035, -0.74, 1.04, 2.52, 2.58, beam, 0.006)
new_box("Beam_Front", -1.73, 1.73, -0.77, -0.70, 2.50, 2.57, beam, 0.006)
new_box("Beam_Back", -1.73, 1.73, 1.00, 1.07, 2.50, 2.57, beam, 0.006)
for x in (-1.5, 1.5):  # tiang depan
    new_box(f"PostFront_{x}", x - 0.04, x + 0.04, -0.77, -0.69, 0.0, 2.55, L["wood_post"], 0.008)
def tarp(name, w, d, nx, ny, mat, z0, sag=0.02):
    bm = bmesh.new()
    g = [[bm.verts.new(((i / nx - 0.5) * w, (j / ny - 0.5) * d,
                       z0 + 0.12 * (j / ny) * 0 - 0.06 * (j / ny - 0.5) + sag * math.sin((i / nx) * 3 * 2 * math.pi) * 0.5)) for i in range(nx + 1)] for j in range(ny + 1)]
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((g[j][i], g[j][i + 1], g[j + 1][i + 1], g[j + 1][i]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); me.materials.append(mat); C_DET.objects.link(o)
    s = o.modifiers.new("Solid", 'SOLIDIFY'); s.thickness = 0.006; s.offset = 1.0
    return o
t = tarp("Tarp", 3.52, 1.9, 60, 20, L["awning"], 2.63)
t.location = (0, 0.15, 0)
# valance bergerigi (scallop) di tepi depan
def valance(name, w, h, n, mat, y, z_top):
    bm = bmesh.new(); seg = 8
    cols = n * seg
    for ci in range(cols + 1):
        u = ci / cols; x = (u - 0.5) * w
        ph = (u * n) % 1.0
        drop = h * (0.55 + 0.45 * math.cos((ph - 0.5) * math.pi * 1.0) ** 1.0) if False else h * (0.6 + 0.4 * math.sin(ph * math.pi))
        bm.verts.new((x, y, z_top)); bm.verts.new((x, y - 0.02 * math.sin(ph * math.pi), z_top - drop))
    bm.verts.ensure_lookup_table()
    for ci in range(cols):
        a = 2 * ci
        bm.faces.new((bm.verts[a], bm.verts[a + 2], bm.verts[a + 3], bm.verts[a + 1]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); me.materials.append(mat); C_DET.objects.link(o)
    s = o.modifiers.new("Solid", 'SOLIDIFY'); s.thickness = 0.005; s.offset = 1.0
    return o
valance("Valance", 3.52, 0.22, 8, L["awning"], -0.775 + 0.02, 2.60)

# ---------- lampu gantung (bandul) ----------
pv = bpy.data.objects.new("LAMP_pivot", None); pv.empty_display_type = 'PLAIN_AXES'; pv.location = (1.05, 0.28, 2.52); C_DET.objects.link(pv)
bulb_mat = bpy.data.materials.get("M_Bulb") or bpy.data.materials.new("M_Bulb"); bulb_mat.use_nodes = True
nt = bulb_mat.node_tree; b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
b.inputs["Base Color"].default_value = (1, 0.9, 0.7, 1)
try: b.inputs["Emission Color"].default_value = (1, 0.82, 0.55, 1); b.inputs["Emission Strength"].default_value = 3.0
except KeyError: pass
cab = cyl("LampCable", 0.004, 0.30, (1.05, 0.28, 2.37), L["steel_dark"], seg=8); cab.parent = pv; cab.matrix_parent_inverse = pv.matrix_world.inverted()
sk = cyl("LampSocket", 0.016, 0.05, (1.05, 0.28, 2.20), L["steel_dark"], seg=12); sk.parent = pv; sk.matrix_parent_inverse = pv.matrix_world.inverted()
bu = sphere("LampBulb", 0.034, (1.05, 0.28, 2.15), bulb_mat, (1, 1, 1.25)); bu.parent = pv; bu.matrix_parent_inverse = pv.matrix_world.inverted()

# ---------- kompor, wajan, perlengkapan di belakang meja ----------
steel = L["steel_dark"]
new_box("StoveTable", 0.85, 1.45, 1.00, 1.55, 0.0, 0.78, F["paint"]("M_StoveTable", (0.55, 0.57, 0.58), rough=0.4, spec=0.7, metallic=0.6, noise_bump=0.03), 0.01)
new_box("StoveTop", 0.83, 1.47, 0.98, 1.57, 0.78, 0.81, steel, 0.008)
wok = cyl("Wok", 0.19, 0.08, (1.15, 1.28, 0.865), steel, seg=32)
oil = cyl("WokOil", 0.165, 0.004, (1.15, 1.28, 0.90), F["paint"]("M_Oil", (0.55, 0.36, 0.07), rough=0.08, spec=0.9, coat=0.8, noise_bump=0.0, dirt=0.0), seg=32)
new_box("WokHandle", 1.30, 1.58, 1.265, 1.295, 0.88, 0.905, steel, 0.005)
cyl("GasTank", 0.15, 0.55, (1.0, 1.30, 0.28), F["paint"]("M_Gas", (0.25, 0.55, 0.45), rough=0.4, spec=0.6, noise_bump=0.03), seg=24).location.x = 0.62
# rak belakang & keranjang plastik
new_box("Shelf", -1.45, -0.2, 1.80, 2.0, 1.55, 1.60, L["wood_post"], 0.008)
cyl("Thermos", 0.07, 0.30, (-1.0, 1.9, 1.75), L["plastic_red"], seg=20)
new_box("Crate", -1.45, -0.75, 1.15, 1.65, 0.0, 0.32, L["plastic_blue"], 0.01)
for i in range(3):
    cyl(f"Bottle{i}", 0.032, 0.24, (-1.3 + i * 0.2, 1.4, 0.44), L["glass"], seg=16)
# stoples kerupuk & gelas di atas meja
cyl("Jar", 0.09, 0.22, (1.15, -0.02, 1.30), L["glass"], seg=24)
cyl("JarLid", 0.095, 0.02, (1.15, -0.02, 1.42), L["plastic_red"], seg=24)
cyl("Cup1", 0.04, 0.09, (0.85, 0.15, 1.245), L["glass"], seg=16)
cyl("Cup2", 0.04, 0.09, (0.95, 0.20, 1.245), L["glass"], seg=16)

# ---------- tanaman & bangku di samping ----------
pot = cyl("Pot", 0.17, 0.30, (-2.5, -0.25, 0.15), F["paint"]("M_Pot", (0.65, 0.30, 0.18), rough=0.7, noise_bump=0.2), seg=20, bevel=0.01)
leafm = F["paint"]("M_Leaf", (0.12, 0.45, 0.14), rough=0.45, spec=0.6, noise_bump=0.15, dirt=0.2)
for i in range(14):
    a = i / 14 * 2 * math.pi
    lf = sphere(f"Leaf{i}", 0.11, (-2.5 + 0.12 * math.cos(a), -0.25 + 0.12 * math.sin(a), 0.55 + 0.1 * (i % 3)), leafm, (0.3, 0.9, 2.4))
    lf.rotation_euler = (math.radians(rnd.uniform(-35, 35)), math.radians(rnd.uniform(-35, 35)), a)
new_box("Bench", 2.0, 3.2, 1.1, 1.55, 0.40, 0.46, L["wood_post"], 0.01)
for x in (2.1, 3.1):
    new_box(f"BenchLeg_{x}", x - 0.03, x + 0.03, 1.15, 1.20, 0.0, 0.40, L["wood_post"], 0.006)
    new_box(f"BenchLeg2_{x}", x - 0.03, x + 0.03, 1.45, 1.50, 0.0, 0.40, L["wood_post"], 0.006)

# ---------- properti storyboard (material) ----------
for n, key in (("Bag body", "kraft"), ("Bag folded rim", "kraft"), ("QR stand base", "sign_teal"), ("QR display card", "paper"),
               ("QR stripe", "sign_teal"), ("Wallet lower", "kraft"), ("Wallet back", "kraft"), ("Empty lining", "paper"),
               ("CUSTOMER_PHONE_case", "steel_dark"), ("CUSTOMER_PHONE_screen", None), ("LASTRI_PHONE_case", "steel_dark"), ("LASTRI_PHONE_screen", None)):
    o = OB.get(n)
    if o and key: asg(o, L[key])
    elif o and key is None: asg(o, L["screen"])
for n in ("Bag label", "QR heading", "QR nonactive", "Wallet empty label", "Customer screen", "Learning mock screen", "Received mock screen"):
    o = OB.get(n)
    if o: o.data.materials.clear(); o.data.materials.append(dark_text if n not in ("Customer screen", "Learning mock screen", "Received mock screen") else white_text)
print("set polish ok")
