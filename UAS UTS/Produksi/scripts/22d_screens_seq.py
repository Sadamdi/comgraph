# 22d - Layar ponsel berurutan (muat ulang PNG v2): mahasiswa: scan -> konfirmasi -> berhasil; Bu Lastri: belajar -> beranda -> diterima.
import bpy
OB = bpy.data.objects
P = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\assets\screens" + "\\"
def img(n):
    im = bpy.data.images.get(n + ".png")
    if im: im.filepath = P + n + ".png"; im.reload(); return im
    return bpy.data.images.load(P + n + ".png")

def seq_mat(name, seq):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    if nt.animation_data: nt.animation_data_clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); cur = None
    for i, (nm, f) in enumerate(seq):
        tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = img(nm); tx.interpolation = 'Cubic'
        if cur is None: cur = tx.outputs["Color"]; continue
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
        nt.links.new(cur, mx.inputs[6]); nt.links.new(tx.outputs["Color"], mx.inputs[7])
        mx.inputs[0].default_value = 0.0; mx.inputs[0].keyframe_insert("default_value", frame=f - 1)
        mx.inputs[0].default_value = 1.0; mx.inputs[0].keyframe_insert("default_value", frame=f)
        cur = mx.outputs[2]
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 1.0
    nt.links.new(cur, em.inputs["Color"]); nt.links.new(em.outputs[0], out.inputs["Surface"])
    if nt.animation_data and nt.animation_data.action:
        for fc in nt.animation_data.action.layers[0].strips[0].channelbags[0].fcurves:
            for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
    return m

OB["CUSTOMER_PHONE_screen"].material_slots[0].material = seq_mat("M_Screen_Cust", [("phone_home", 0), ("phone_scan", 1760), ("phone_confirm", 1840), ("phone_success", 1905)])
OB["LASTRI_PHONE_screen"].material_slots[0].material = seq_mat("M_Screen_Lastri", [("phone_learn", 0), ("phone_home", 1240), ("phone_received", 2036)])
print("layar berurutan terpasang")
