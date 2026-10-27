# 21 - Pejalan kaki NPC: gandakan tokoh MHS (badan+wajah+rig yang sudah teruji) jadi NPC1..N dengan warna baju berbeda, jalan memakai walk() (kaki menapak, tanpa slide)
import bpy, math
from mathutils import Vector

OB = bpy.data.objects
SRC = "MHS"
exec(open(SD + "06_anim_core.py", encoding="utf8").read()) if "Char" not in globals() else None

def hue_mat(src_mat, name, hue, sat=1.0, val=1.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = src_mat.copy(); m.name = name
    nt = m.node_tree
    em = next((n for n in nt.nodes if n.type == 'EMISSION'), None)
    if em is None: return m
    hs = nt.nodes.new("ShaderNodeHueSaturation"); hs.inputs["Hue"].default_value = hue; hs.inputs["Saturation"].default_value = sat; hs.inputs["Value"].default_value = val
    srcs = em.inputs["Color"].links
    if srcs: nt.links.new(srcs[0].from_socket, hs.inputs["Color"])
    nt.links.new(hs.outputs["Color"], em.inputs["Color"]); return m

def clone_char(dst, hues):
    objs = [o for o in OB if o.name.startswith(SRC + "_") or o.name == "RIG_" + SRC]
    mp = {}
    def nn(n): return ("RIG_" + dst) if n == "RIG_" + SRC else dst + n[len(SRC):]
    for o in objs:
        c = o.copy()
        if o.data is not None: c.data = o.data.copy()
        c.name = nn(o.name)
        if c.animation_data: c.animation_data_clear()           # jangan berbagi Action dengan tokoh utama
        if c.type == 'MESH' and c.data.shape_keys and c.data.shape_keys.animation_data: c.data.shape_keys.animation_data_clear()
        for col in o.users_collection: col.objects.link(c)
        mp[o] = c
    for o, c in mp.items():
        if o.parent in mp: c.parent = mp[o.parent]
        c.matrix_parent_inverse = o.matrix_parent_inverse.copy()
        for m in c.modifiers:
            if getattr(m, "object", None) in mp: m.object = mp[m.object]
        for k in c.constraints:
            t = getattr(k, "target", None)
            if t in mp: k.target = mp[t]
            elif t is not None and t.name.startswith("LOOK_"): c.constraints.remove(k)
        if c.type == 'MESH':
            for i, s in enumerate(c.material_slots):
                nm = s.material.name if s.material else ""
                for key, h in hues.items():
                    if nm == key: s.material = hue_mat(bpy.data.materials[nm], f"{nm}_{dst}", *h)
    # IK/Copy-rotation pada tulang: tulang pada armature salinan; arahkan target ke rig baru
    rig = mp[OB["RIG_" + SRC]]
    for pb in rig.pose.bones:
        for k in pb.constraints:
            if getattr(k, "target", None) is OB["RIG_" + SRC]: k.target = rig
    return rig

HUES = [
    {"T_Jacket": (0.35, 0.6, 1.0), "T_Jeans": (0.0, 0.55, 1.15), "T_Backpack": (0.1, 0.7, 1.0)},
    {"T_Jacket": (0.62, 0.6, 1.0), "T_Jeans": (0.9, 0.55, 1.3), "T_Backpack": (0.8, 0.6, 1.0)},
    {"T_Jacket": (0.85, 0.6, 1.1), "T_Jeans": (0.1, 0.7, 1.0), "T_Backpack": (0.45, 0.6, 1.0)},
    {"T_Jacket": (0.15, 0.6, 1.0), "T_Jeans": (0.3, 0.5, 1.2), "T_Backpack": (0.9, 0.6, 1.0)},
]
# (nama, mulai, akhir, y, frame awal)
PLAN = [("NPC1", (-9, -3.3), (9, -3.3), 1), ("NPC2", (9, -3.7), (-9, -3.7), 260), ("NPC3", (-9, -3.1), (9, -3.1), 900), ("NPC4", (9, -3.5), (-9, -3.5), 1400),
        ("NPC5", (-9, -3.3), (9, -3.3), 1900), ("NPC6", (9, -3.7), (-9, -3.7), 2150)]
for o in [o for o in OB if o.name.startswith("NPC") or o.name.startswith("RIG_NPC")]: bpy.data.objects.remove(o)
for i, (nm, a, b, f0) in enumerate(PLAN):
    rig = clone_char(nm, HUES[i % len(HUES)])
    ch = Char(nm)
    dist = (Vector(b) - Vector(a)).length
    n = int(dist / 0.58)
    walk(ch, f0, a, b, T=15, n=n, via=None)
print("NPC:", [o.name for o in OB if o.name.startswith("RIG_NPC")])
