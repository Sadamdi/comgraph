# 04a - Badan karakter (Skin modifier dari kerangka garis) -> mesh halus, dihadapkan ke -Y, berdiri di z=0
import bpy, bmesh, math
from mathutils import Vector

def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c

def body_spec(kind):
    """Titik sendi (x,y,z) sisi kiri karakter (x>0) + radius (rx,ry). Satuan meter."""
    if kind == "lastri":   # ibu penjual, 1.55 m, sedikit berisi
        S = dict(H=1.55, sh=0.165, hip=0.085, torso_w=0.135, waist_w=0.125, hip_w=0.15, leg_r=0.066, arm_r=0.034, neck_r=0.030)
    else:                  # mahasiswa, 1.72 m, bahu lebar
        S = dict(H=1.72, sh=0.19, hip=0.09, torso_w=0.150, waist_w=0.125, hip_w=0.14, leg_r=0.068, arm_r=0.038, neck_r=0.036)
    k = S["H"] / 1.55
    z = lambda v: v * k
    S["z"] = dict(ankle=z(0.075), knee=z(0.43), hip=z(0.83), pelvis=z(0.88), waist=z(1.02), chest=z(1.17), sh=z(1.28), neck0=z(1.30), neck1=z(1.355), toe=z(0.03))
    return S

def build_body(kind, name):
    S = body_spec(kind); Z = S["z"]
    bm = bmesh.new()
    verts = {}; radii = {}
    def V(key, x, y, zz, rx, ry=None):
        verts[key] = bm.verts.new((x, y, zz)); radii[key] = (rx, ry if ry is not None else rx)
    def E(a, b): bm.edges.new((verts[a], verts[b]))
    # sumbu tubuh
    V("pelvis", 0, 0, Z["pelvis"], S["hip_w"], 0.095)
    V("waist", 0, 0, Z["waist"], S["waist_w"], 0.085)
    V("chest", 0, 0, Z["chest"], S["torso_w"], 0.095)
    V("sh_mid", 0, 0, Z["sh"], S["torso_w"] * 0.95, 0.08)
    V("neck0", 0, 0.005, Z["neck0"], S["neck_r"], S["neck_r"])
    V("neck1", 0, 0.01, Z["neck1"], S["neck_r"] * 0.95, S["neck_r"] * 0.95)
    for a, b in (("pelvis", "waist"), ("waist", "chest"), ("chest", "sh_mid"), ("sh_mid", "neck0"), ("neck0", "neck1")): E(a, b)
    arm_len_u = 0.27 * S["H"] / 1.55; arm_len_f = 0.245 * S["H"] / 1.55
    for side, sx in (("L", 1), ("R", -1)):
        # bahu -> siku -> pergelangan -> telapak (menggantung alami)
        V(f"sho_{side}", sx * S["sh"], 0.0, Z["sh"] - 0.015, S["arm_r"] * 1.15, S["arm_r"] * 1.15)
        V(f"elb_{side}", sx * (S["sh"] + 0.03), 0.0, Z["sh"] - 0.015 - arm_len_u, S["arm_r"] * 0.92, S["arm_r"] * 0.92)
        V(f"wri_{side}", sx * (S["sh"] + 0.045), -0.02, Z["sh"] - 0.015 - arm_len_u - arm_len_f, S["arm_r"] * 0.62, S["arm_r"] * 0.55)
        # ---- tangan anatomis: telapak + 4 jari (3 ruas) + jempol (3 ruas); ukuran menyesuaikan tinggi karakter ----
        kk = S["H"] / 1.55
        wz = Z["sh"] - 0.015 - arm_len_u - arm_len_f           # z pergelangan
        px = sx * (S["sh"] + 0.050)                              # x sumbu tangan (telapak menghadap ke dalam = -sx)
        V(f"palm_{side}", px, -0.025, wz - 0.040 * kk, 0.013, 0.034)
        ys = (-0.052, -0.034, -0.016, 0.002)                       # y buku jari: telunjuk (depan) -> kelingking (belakang)
        scl = (0.95, 1.00, 0.93, 0.78)
        names = ("index", "middle", "ring", "pinky")
        for i, (nmf, sc_) in enumerate(zip(names, scl)):
            ky = ys[i]; kz = wz - (0.082 + (0.004 if i == 3 else 0.0) + (-0.002 if i == 1 else 0)) * kk
            V(f"{nmf}0_{side}", px, ky, kz, 0.0090, 0.0090)                                  # buku jari (pangkal ruas 1)
            V(f"{nmf}1_{side}", px - sx * 0.003, ky, kz - 0.040 * sc_ * kk, 0.0082, 0.0082)  # ujung ruas 1
            V(f"{nmf}2_{side}", px - sx * 0.007, ky, kz - 0.062 * sc_ * kk, 0.0074, 0.0074)  # ujung ruas 2
            V(f"{nmf}3_{side}", px - sx * 0.010, ky, kz - 0.079 * sc_ * kk, 0.0062, 0.0062)  # ujung jari
        tb = (px - sx * 0.010, -0.050, wz - 0.026 * kk)
        V(f"thumb0_{side}", *tb, 0.0115, 0.0115)
        V(f"thumb1_{side}", tb[0] - sx * 0.004, tb[1] - 0.020 * kk, tb[2] - 0.026 * kk, 0.0105, 0.0105)
        V(f"thumb2_{side}", tb[0] - sx * 0.008, tb[1] - 0.034 * kk, tb[2] - 0.048 * kk, 0.0092, 0.0092)
        V(f"thumb3_{side}", tb[0] - sx * 0.010, tb[1] - 0.042 * kk, tb[2] - 0.066 * kk, 0.0078, 0.0078)
        E("sh_mid", f"sho_{side}"); E(f"sho_{side}", f"elb_{side}"); E(f"elb_{side}", f"wri_{side}"); E(f"wri_{side}", f"palm_{side}")
        for nmf in names:
            E(f"palm_{side}", f"{nmf}0_{side}"); E(f"{nmf}0_{side}", f"{nmf}1_{side}"); E(f"{nmf}1_{side}", f"{nmf}2_{side}"); E(f"{nmf}2_{side}", f"{nmf}3_{side}")
        E(f"palm_{side}", f"thumb0_{side}"); E(f"thumb0_{side}", f"thumb1_{side}"); E(f"thumb1_{side}", f"thumb2_{side}"); E(f"thumb2_{side}", f"thumb3_{side}")
        # kaki
        V(f"hip_{side}", sx * S["hip"], 0.0, Z["hip"], S["leg_r"] * 1.12, S["leg_r"] * 1.12)
        V(f"knee_{side}", sx * S["hip"], -0.004, Z["knee"], S["leg_r"] * 0.82, S["leg_r"] * 0.82)
        V(f"ank_{side}", sx * S["hip"], 0.0, Z["ankle"], S["leg_r"] * 0.52, S["leg_r"] * 0.52)
        V(f"toe_{side}", sx * S["hip"], -0.12, Z["toe"], 0.04, 0.028)
        E("pelvis", f"hip_{side}"); E(f"hip_{side}", f"knee_{side}"); E(f"knee_{side}", f"ank_{side}"); E(f"ank_{side}", f"toe_{side}")
    me = bpy.data.meshes.new(name + "_skin")
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name + "_BODY", me)
    # radius skin
    sk = o.modifiers.new("Skin", 'SKIN'); sk.use_smooth_shade = True
    if len(me.skin_vertices) == 0:
        me.skin_vertices.new()
    layer = me.skin_vertices[0].data
    keys = list(verts.keys())
    for i, key in enumerate(keys):
        layer[i].radius = radii[key]
    layer[keys.index("pelvis")].use_root = True
    for i, key in enumerate(keys):
        if key.startswith(("sho_", "elb_", "wri_", "hip_", "knee_", "ank_")):
            layer[i].use_loose = False
    sd = o.modifiers.new("Subsurf", 'SUBSURF'); sd.levels = 2; sd.render_levels = 2
    o["joint_keys"] = keys
    return o, S, keys

if __name__ == "__main__" or True:
    C = coll("20_TOKOH", bpy.data.collections.get("10_PRODUKSI"))
    for kind, nm, ox in (("lastri", "LASTRI", -1.2), ("pelanggan", "PELANGGAN", 1.2)):
        old = bpy.data.objects.get(nm + "_BODY")
        if old: bpy.data.objects.remove(old)
        o, S, keys = build_body(kind, nm)
        o.location = (ox, -3.0, 0)
        C.objects.link(o)
    print("body ok")
