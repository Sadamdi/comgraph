# 18b - Pasang tekstur lukisan (assets/paint) ke material lingkungan: gantikan noise kuas pada rantai GHIBLI dengan gambar + kekuatan lebih tinggi
import bpy
PAINT = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\assets\paint" + "\\"
MAP = {   # nama material -> (tekstur, skala, kekuatan overlay)
    "M_Asphalt": ("p_road", 0.25, 0.75), "Ground": ("p_cobble", 0.35, 0.8), "M_Paving": ("p_cobble", 0.35, 0.8), "M_Paving2": ("p_cobble", 0.35, 0.8),
    "M_Curb": ("p_cobble", 0.5, 0.7), "M_Curb2": ("p_cobble", 0.5, 0.7),
    "M_WoodCounter": ("p_planks", 0.5, 0.7), "M_WoodPost": ("p_planks", 0.6, 0.7), "M_WoodDark": ("p_planks_dark", 0.5, 0.7), "M_WoodPainted": ("p_planks", 0.5, 0.6),
    "wall": ("p_plaster_mint", 0.3, 0.8), "M_WallBase": ("p_plaster_sky", 0.3, 0.8), "M_Awning": ("p_roof", 0.5, 0.4),
    "M_Leaf": ("p_grass", 0.8, 0.8), "M_Pot": ("p_roof", 0.8, 0.6), "terracotta": ("p_roof", 0.8, 0.6), "terracotta.001": ("p_roof", 0.8, 0.6),
}
for k in ("F_Belakang_1", "F_Belakang_2", "F_Ruko_Jauh_Kanan", "F_Ruko_Jauh_Kiri", "F_Ruko_Kanan", "F_Ruko_Kanan2", "F_Ruko_Kiri", "F_Ruko_Kiri2",
          "F_Ruko_Tengah_Atas", "F_Seberang_1", "F_Seberang_2", "F_Seberang_3"):
    MAP[k] = ("p_plaster_cream", 0.3, 0.7)

def img(name):
    p = PAINT + name + ".png"
    im = bpy.data.images.get(name + ".png") or bpy.data.images.load(p)
    return im

n_ok = 0
for mn, (tex, sc, st) in MAP.items():
    m = bpy.data.materials.get(mn)
    if not m or not m.use_nodes: continue
    nt = m.node_tree
    ov = next((n for n in nt.nodes if n.label == "GHIBLI" and n.bl_idname == "ShaderNodeMix" and n.blend_type == 'OVERLAY'), None)
    if ov is None: continue
    for n in [x for x in nt.nodes if x.label == "GPAINT"]: nt.nodes.remove(n)
    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.label = "GPAINT"
    mp = nt.nodes.new("ShaderNodeMapping"); mp.label = "GPAINT"; mp.inputs["Scale"].default_value = (sc, sc, sc)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.label = "GPAINT"; tx.image = img(tex); tx.projection = 'BOX'; tx.projection_blend = 0.25
    tx.interpolation = 'Smart'
    nt.links.new(mp.outputs[0], tx.inputs["Vector"])
    for l in list(ov.inputs[7].links): nt.links.remove(l)
    nt.links.new(tx.outputs["Color"], ov.inputs[7]); ov.inputs[0].default_value = st
    n_ok += 1
print("material berlukis:", n_ok)
