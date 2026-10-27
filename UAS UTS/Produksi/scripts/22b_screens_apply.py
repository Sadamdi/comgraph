# 22b - Pasang tekstur papan QRIS & layar ponsel ke objek (papan: bidang baru di muka depan kartu; layar: material gambar)
import bpy, bmesh
OB = bpy.data.objects
P = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\assets\screens" + "\\"

def img(n): return bpy.data.images.get(n + ".png") or bpy.data.images.load(P + n + ".png")

def img_mat(name, tex, strength=1.0, lit=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = img(tex); tx.interpolation = 'Cubic'
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = strength
    nt.links.new(tx.outputs["Color"], em.inputs["Color"])
    if lit > 0:     # papan kertas: sedikit terpengaruh cahaya agar menyatu dengan adegan
        df = nt.nodes.new("ShaderNodeBsdfDiffuse"); nt.links.new(tx.outputs["Color"], df.inputs["Color"])
        mx = nt.nodes.new("ShaderNodeMixShader"); mx.inputs[0].default_value = lit
        nt.links.new(em.outputs[0], mx.inputs[1]); nt.links.new(df.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs["Surface"])
    else: nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m, tx

def face_plane(name, parent, w, h, loc, mat):
    old = OB.get(name)
    if old: bpy.data.objects.remove(old)
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    v = [bm.verts.new((-w / 2, 0, -h / 2)), bm.verts.new((w / 2, 0, -h / 2)), bm.verts.new((w / 2, 0, h / 2)), bm.verts.new((-w / 2, 0, h / 2))]
    f = bm.faces.new(v); uv = bm.loops.layers.uv.new("UVMap")
    for l, (u, vv) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): l[uv].uv = (u, vv)   # menghadap -Y (depan), dilihat dari -Y: u terbalik
    f.normal_flip(); bm.to_mesh(me); bm.free()
    me.materials.append(mat); o = bpy.data.objects.new(name, me); o.parent = parent; o.location = loc
    for c in parent.users_collection: c.objects.link(o)
    return o

# ---- papan QRIS ----
qr = OB["QRIS_DUMMY_NONAKTIF"]
for n in ("QR heading", "QR nonactive", "QR stripe"): OB[n].hide_render = True; OB[n].hide_viewport = True
for n in ("QR heading", "QR nonactive", "QR stripe"):
    o = OB[n]
    if o.animation_data: o.animation_data_clear()
    o.hide_render = True
m_board, _ = img_mat("M_QRIS_Board", "qris_board", 0.35, 0.65)
fp = face_plane("QR face", qr, 0.286, 0.286 * 1300 / 1024, (0, -0.0195, 0.0), m_board)
card = OB["QR display card"]
card.scale = (card.scale.x, card.scale.y, card.scale.z)
# kartu ikut mengikuti proporsi poster: tinggi kartu 0.376 vs poster 0.363 -> sudah pas
fp.hide_render = False
bpy.context.scene.frame_set(1430); bpy.context.view_layer.update()
from mathutils import Vector
ymin = min((card.matrix_world @ Vector(b)).y for b in card.bound_box)
wp = fp.matrix_world.translation.copy(); wp.y = ymin - 0.003; fp.location = qr.matrix_world.inverted() @ wp
# visibilitas ikut papan (show() pada induk mengatur anak? salin kunci dari kartu)
if card.animation_data and card.animation_data.action:
    fp.animation_data_create(); fp.animation_data.action = card.animation_data.action.copy()
else:
    fp.hide_render = card.hide_render
# ---- layar ponsel ----
for n in ("Customer screen", "Learning mock screen", "Received mock screen"):
    o = OB[n]; o.hide_render = True
    if o.animation_data: o.animation_data_clear()
    o.hide_render = True
m_cust, _ = img_mat("M_Screen_Cust", "phone_confirm", 1.0)
OB["CUSTOMER_PHONE_screen"].material_slots[0].material = m_cust
# ponsel Bu Lastri: belajar -> diterima (ganti di f2036)
m_l = bpy.data.materials.get("M_Screen_Lastri") or bpy.data.materials.new("M_Screen_Lastri")
m_l.use_nodes = True; nt = m_l.node_tree
for n in list(nt.nodes): nt.nodes.remove(n)
out = nt.nodes.new("ShaderNodeOutputMaterial")
t1 = nt.nodes.new("ShaderNodeTexImage"); t1.image = img("phone_learn"); t2 = nt.nodes.new("ShaderNodeTexImage"); t2.image = img("phone_received")
mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
nt.links.new(t1.outputs[0], mx.inputs[6]); nt.links.new(t2.outputs[0], mx.inputs[7])
em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 1.0
nt.links.new(mx.outputs[2], em.inputs["Color"]); nt.links.new(em.outputs[0], out.inputs["Surface"])
mx.inputs[0].default_value = 0.0; mx.inputs[0].keyframe_insert("default_value", frame=2035)
mx.inputs[0].default_value = 1.0; mx.inputs[0].keyframe_insert("default_value", frame=2036)
for fc in nt.animation_data.action.layers[0].strips[0].channelbags[0].fcurves:
    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
OB["LASTRI_PHONE_screen"].material_slots[0].material = m_l
# layar mahasiswa: 'scan' di tahap pindai (S10) lalu 'confirm'
print("layar & papan terpasang")
