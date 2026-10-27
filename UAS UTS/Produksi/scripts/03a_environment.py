# 03a - Lingkungan: trotoar, curb, jalan raya, deretan ruko (belakang & seberang jalan), langit
# Dikerjakan di file bersama; objek lama tidak dihapus, hanya disembunyikan dari render bila diganti.
import bpy, bmesh, math, random
from mathutils import Vector

L = bpy.app.driver_namespace["MATLIB"]
F = bpy.app.driver_namespace["MATFN"]
random.seed(11)
sc = bpy.context.scene

# ---------- koleksi ----------
def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or sc.collection).children.link(c)
    return c
C_ROOT = coll("10_PRODUKSI")
C_ENV = coll("10_ENV", C_ROOT)
C_DET = coll("11_SET_DETAIL", C_ROOT)

def link(o, c):
    for cc in list(o.users_collection):
        cc.objects.unlink(o)
    c.objects.link(o)

def box(name, x0, x1, y0, y1, z0, z1, mat=None, c=None, bevel=0.0, seg=2):
    c = c or C_ENV
    hx, hy, hz = (x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    for v in bm.verts:
        v.co.x *= hx; v.co.y *= hy; v.co.z *= hz
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    c.objects.link(o)
    if mat: me.materials.append(mat)
    if bevel > 0:
        b = o.modifiers.new("Bevel", 'BEVEL'); b.width = bevel; b.segments = seg; b.limit_method = 'ANGLE'
    return o

# ---------- sembunyikan placeholder lama ----------
for n in ("Light", "Camera", "Cube"):
    o = bpy.data.objects.get(n)
    if o: o.hide_render = True; o.hide_viewport = True
for cn in ("07_FRAME_LABELS",):
    cc = bpy.data.collections.get(cn)
    if cc: cc.hide_render = True; cc.hide_viewport = True

# ---------- material fasad (shader prosedural: jendela + rolling door lantai dasar) ----------
def facade_mat(name, x0, tint, spacing=3.0, zlower=2.7, floor_h=3.2, shutter_tint=(0.85, 0.9, 0.9), glass=(0.04, 0.06, 0.09), win=True):
    old = bpy.data.materials.get(name)
    if old: bpy.data.materials.remove(old)
    m = F["pbr"](name + "_tmp", "painted_plaster_wall", scale=0.35, tint=tint, tint_mix=0.55, normal=0.7)  # sumber node plaster
    nt = m.node_tree; b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    geo = next(n for n in nt.nodes if n.type == "NEW_GEOMETRY")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Position"], sep.inputs[0])
    def mth(op, a=None, b_=None, av=None, bv=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        if a is not None: nt.links.new(a, n.inputs[0])
        elif av is not None: n.inputs[0].default_value = av
        if b_ is not None: nt.links.new(b_, n.inputs[1])
        elif bv is not None: n.inputs[1].default_value = bv
        return n.outputs[0]
    u = mth('FRACT', mth('DIVIDE', mth('SUBTRACT', sep.outputs["X"], bv=x0), bv=spacing))
    v = mth('FRACT', mth('DIVIDE', mth('SUBTRACT', sep.outputs["Z"], bv=zlower), bv=floor_h))
    def rng(val, lo, hi):
        return mth('MULTIPLY', mth('GREATER_THAN', val, bv=lo), mth('LESS_THAN', val, bv=hi))
    upper = mth('GREATER_THAN', sep.outputs["Z"], bv=zlower)
    inner = mth('MULTIPLY', mth('MULTIPLY', rng(u, 0.30, 0.70), rng(v, 0.35, 0.80)), upper)
    outer = mth('MULTIPLY', mth('MULTIPLY', rng(u, 0.27, 0.73), rng(v, 0.32, 0.83)), upper)
    frame = mth('SUBTRACT', outer, inner)
    if not win:
        inner = mth('MULTIPLY', inner, bv=0.0); frame = mth('MULTIPLY', frame, bv=0.0)
    # warna dasar: plaster -> kaca (jendela) -> bingkai
    base_in = [l.from_socket for l in b.inputs["Base Color"].links][0]
    mix1 = nt.nodes.new("ShaderNodeMix"); mix1.data_type = 'RGBA'; mix1.inputs[7].default_value = (*glass, 1)
    nt.links.new(inner, mix1.inputs[0]); nt.links.new(base_in, mix1.inputs[6])
    mix2 = nt.nodes.new("ShaderNodeMix"); mix2.data_type = 'RGBA'; mix2.inputs[7].default_value = (0.75, 0.76, 0.78, 1)
    nt.links.new(frame, mix2.inputs[0]); nt.links.new(mix1.outputs[2], mix2.inputs[6])
    # lantai dasar = rolling door logam
    ds = nt.nodes.new("ShaderNodeTexImage"); ds.image = bpy.data.images.load(F_TEX + "painted_metal_shutter_diff_1k.jpg", check_existing=True)
    ds.projection = 'BOX'; ds.projection_blend = 0.2
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.5, 0.5, 0.5)
    nt.links.new(geo.outputs["Position"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], ds.inputs["Vector"])
    tm = nt.nodes.new("ShaderNodeMix"); tm.data_type = 'RGBA'; tm.blend_type = 'MULTIPLY'; tm.inputs[0].default_value = 0.4
    tm.inputs[6].default_value = (*shutter_tint, 1); nt.links.new(ds.outputs["Color"], tm.inputs[7])
    low = mth('LESS_THAN', sep.outputs["Z"], bv=zlower)
    mix3 = nt.nodes.new("ShaderNodeMix"); mix3.data_type = 'RGBA'
    nt.links.new(low, mix3.inputs[0]); nt.links.new(mix2.outputs[2], mix3.inputs[6]); nt.links.new(tm.outputs[2], mix3.inputs[7])
    nt.links.new(mix3.outputs[2], b.inputs["Base Color"])
    # roughness: kaca licin, lain ikut tekstur
    rin = [l.from_socket for l in b.inputs["Roughness"].links][0]
    mr = nt.nodes.new("ShaderNodeMix"); mr.data_type = 'FLOAT'; mr.inputs[3].default_value = 0.04
    nt.links.new(inner, mr.inputs[0]); nt.links.new(rin, mr.inputs[2])
    nt.links.new(mr.outputs[0], b.inputs["Roughness"])
    mt = nt.nodes.new("ShaderNodeMix"); mt.data_type = 'FLOAT'; mt.inputs[3].default_value = 0.0
    nt.links.new(inner, mt.inputs[0]); mt.inputs[2].default_value = 0.0
    nt.links.new(mt.outputs[0], b.inputs["Metallic"])
    m.name = name
    return m

F_TEX = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\assets\tex\\"

# ---------- tanah, trotoar, curb, jalan ----------
g = bpy.data.objects["Ground"]
g.dimensions = (90, 6.6, 0.2); g.location = (0, -1.2, -0.11)
bpy.context.view_layer.update()
F["assign"](g, L["paving"])
link(g, C_ENV)
box("Curb", -45, 45, -4.80, -4.50, -0.17, 0.0, F["pbr"]("M_Curb", "large_floor_tiles_02", scale=0.5, tint=(0.82, 0.8, 0.76), tint_mix=0.6), bevel=0.02)
box("Jalan", -90, 90, -62, -4.80, -0.55, -0.17, L["asphalt"])
box("Trotoar_Seberang", -90, 90, -18.2, -12.4, -0.55, 0.0, L["paving"])
box("Curb_Seberang", -90, 90, -12.4, -12.1, -0.55, 0.0, F["pbr"]("M_Curb2", "large_floor_tiles_02", scale=0.5, tint=(0.82, 0.8, 0.76), tint_mix=0.6))
# marka jalan putus-putus
white = F["paint"]("M_Marka", (0.88, 0.88, 0.84), rough=0.7, noise_bump=0.1, dirt=0.35)
for i in range(-14, 15):
    box(f"Marka_{i}", i * 6 - 1.2, i * 6 + 1.2, -8.67, -8.55, -0.172, -0.168, white, c=C_ENV)

# ---------- fasad ruko ----------
FAC = {}
def ruko(name, x0, x1, y_front, depth, height, tint, spacing, shutter_tint=(0.85, 0.9, 0.9), win=True, ypad=0.0):
    m = facade_mat("F_" + name, x0, tint, spacing=spacing, shutter_tint=shutter_tint, win=win)
    o = box(name, x0, x1, y_front, y_front + depth, 0.0, height, m, bevel=0.0)
    return o

# baris belakang (menempel pada dinding warung: bidang y = 2.025)
ruko("Ruko_Tengah_Atas", -4.0, 4.0, 2.025, 8.0, 6.4, (1.0, 0.93, 0.78), 2.6)
ruko("Ruko_Kiri", -16.0, -4.0, 2.025, 9.0, 3.5, (0.95, 0.78, 0.55), 3.0, (0.8, 0.9, 0.85))
ruko("Ruko_Kanan", 4.0, 16.0, 2.025, 9.0, 6.8, (0.72, 0.88, 0.85), 3.0, (0.95, 0.85, 0.7))
ruko("Ruko_Kiri2", -34.0, -16.0, 2.025, 9.0, 7.6, (0.95, 0.88, 0.8), 3.2, (0.85, 0.85, 0.9))
ruko("Ruko_Kanan2", 16.0, 34.0, 2.025, 9.0, 5.2, (0.9, 0.78, 0.7), 3.4, (0.8, 0.88, 0.8))
ruko("Ruko_Jauh_Kiri", -70.0, -34.0, 2.025, 9.0, 8.4, (0.85, 0.9, 0.95), 3.2)
ruko("Ruko_Jauh_Kanan", 34.0, 70.0, 2.025, 9.0, 6.0, (0.95, 0.9, 0.85), 3.2)
# baris belakang kedua (tampak di atas atap rendah)
ruko("Belakang_1", -30.0, 10.0, 14.0, 10.0, 11.0, (0.9, 0.88, 0.82), 3.0, win=True)
ruko("Belakang_2", 10.0, 60.0, 14.0, 10.0, 9.0, (0.85, 0.82, 0.78), 3.0)
# seberang jalan (S07 & S11 memotret ke arah jalan)
ruko("Seberang_1", -60.0, -14.0, -26.0, 8.0, 6.5, (0.95, 0.85, 0.7), 3.2)
for o in [o for o in bpy.data.objects if o.name.startswith("Seberang_1")]:
    # menghadap +Y (arah warung): putar bidang fasad dengan cermin sumbu Y tidak perlu; bidang depan = sisi y terbesar
    pass
ruko("Seberang_2", -14.0, 30.0, -27.0, 9.0, 8.8, (0.78, 0.85, 0.9), 3.0, (0.9, 0.85, 0.8))
ruko("Seberang_3", 30.0, 90.0, -26.0, 8.0, 5.8, (0.95, 0.9, 0.82), 3.4)

# material pada sisi yang menghadap kamera di seberang: shader memakai posisi dunia (x,z) sehingga cocok untuk kedua sisi

# ---------- langit/dunia (diulang agar ikut perubahan skrip 01) ----------
print("env objects:", len(C_ENV.objects))
