# 02b - Material karakter bergaya anime di dunia realistis:
# Diffuse BSDF -> Shader to RGB -> Color Ramp (pita bayangan lembut) -> kalikan warna dasar. Ikut arah matahari & bayangan jatuh dunia.
import bpy, math

def _new(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)   # pakai ulang agar objek yang sudah memakai tidak kehilangan material
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
    return m, nt, next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')

def toon(name, color, shadow=None, shade_pos=0.60, soft=0.14, core_pos=0.22, ring=0.0, ring_color=(0.55, 0.60, 0.75), ring_center=0.55, ring_w=0.09, spec=0.0, spec_color=(1, 1, 1), rim=0.0, rim_color=(1, 0.95, 0.9), gain=1.0, noise=0.0, ao=0.45, streak=0.0, fabric=0.0):
    """Toon 3 pita: terang / bayangan / inti bayangan. 'gain' menyesuaikan intensitas cahaya sebelum ramp."""
    m, nt, out = _new(name)
    cool = (0.55, 0.50, 0.85)                                  # warna bayangan ala lukisan: bukan sekadar gelap, melainkan geser ke violet-biru
    shadow = shadow or tuple(max(c * 0.70 * 0.72 + cool[i] * 0.28 * c, 0.0) for i, c in enumerate(color))
    core = tuple(max(c * 0.44 * 0.70 + cool[i] * 0.30 * c * 0.8, 0.0) for i, c in enumerate(color))
    df = nt.nodes.new("ShaderNodeBsdfDiffuse"); df.inputs["Color"].default_value = (1, 1, 1, 1)
    s2r = nt.nodes.new("ShaderNodeShaderToRGB"); nt.links.new(df.outputs["BSDF"], s2r.inputs["Shader"])
    bw = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(s2r.outputs["Color"], bw.inputs["Color"])
    gm = nt.nodes.new("ShaderNodeMath"); gm.operation = 'MULTIPLY'; gm.inputs[1].default_value = gain
    nt.links.new(bw.outputs["Val"], gm.inputs[0])
    cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.interpolation = 'EASE'
    e = cr.color_ramp.elements
    e[0].position = max(core_pos - soft * 0.5, 0.0); e[0].color = (*core, 1)
    e[1].position = min(shade_pos + soft, 1.0); e[1].color = (*color, 1)
    mid = e.new(max(shade_pos - soft * 0.2, 0.01)); mid.color = (*shadow, 1)
    nt.links.new(gm.outputs[0], cr.inputs["Fac"])
    last = cr.outputs["Color"]
    if noise > 0:  # variasi warna halus ala cat tangan
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 18; nz.inputs["Detail"].default_value = 4
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'OVERLAY'; mx.inputs[0].default_value = noise
        nt.links.new(last, mx.inputs[6]); nt.links.new(nz.outputs["Color"], mx.inputs[7]); last = mx.outputs[2]
    if spec > 0 or ring > 0:   # cincin cahaya (angel ring) ala anime: pita pada normal ruang-kamera, bukan pantulan langit
        ng = nt.nodes.new("ShaderNodeNewGeometry")
        vt = nt.nodes.new("ShaderNodeVectorTransform"); vt.vector_type = 'NORMAL'; vt.convert_from = 'WORLD'; vt.convert_to = 'CAMERA'
        nt.links.new(ng.outputs["Normal"], vt.inputs["Vector"])
        sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(vt.outputs["Vector"], sp.inputs[0])
        ab = nt.nodes.new("ShaderNodeMath"); ab.operation = 'SUBTRACT'; ab.inputs[1].default_value = ring_center or 0.55
        nt.links.new(sp.outputs["Y"], ab.inputs[0])
        ab2 = nt.nodes.new("ShaderNodeMath"); ab2.operation = 'ABSOLUTE'; nt.links.new(ab.outputs[0], ab2.inputs[0])
        lt = nt.nodes.new("ShaderNodeMath"); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = ring_w
        nt.links.new(ab2.outputs[0], lt.inputs[0])
        fc = nt.nodes.new("ShaderNodeMath"); fc.operation = 'GREATER_THAN'; fc.inputs[1].default_value = 0.1
        nt.links.new(sp.outputs["Z"], fc.inputs[0])
        both = nt.nodes.new("ShaderNodeMath"); both.operation = 'MULTIPLY'
        nt.links.new(lt.outputs[0], both.inputs[0]); nt.links.new(fc.outputs[0], both.inputs[1])
        gs = nt.nodes.new("ShaderNodeMath"); gs.operation = 'MULTIPLY'; gs.inputs[1].default_value = max(ring, spec)
        nt.links.new(both.outputs[0], gs.inputs[0])
        add = nt.nodes.new("ShaderNodeMix"); add.data_type = 'RGBA'; add.blend_type = 'ADD'
        nt.links.new(gs.outputs[0], add.inputs[0]); nt.links.new(last, add.inputs[6]); add.inputs[7].default_value = (*ring_color, 1)
        last = add.outputs[2]
    if rim > 0:    # rim light tipis (cahaya pinggir) ala anime
        lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
        rr = nt.nodes.new("ShaderNodeMath"); rr.operation = 'GREATER_THAN'; rr.inputs[1].default_value = 0.78
        nt.links.new(lw.outputs["Facing"], rr.inputs[0])
        rg = nt.nodes.new("ShaderNodeMath"); rg.operation = 'MULTIPLY'; rg.inputs[1].default_value = rim
        nt.links.new(rr.outputs[0], rg.inputs[0])
        add2 = nt.nodes.new("ShaderNodeMix"); add2.data_type = 'RGBA'; add2.blend_type = 'ADD'
        nt.links.new(rg.outputs[0], add2.inputs[0]); nt.links.new(last, add2.inputs[6]); add2.inputs[7].default_value = (*rim_color, 1)
        last = add2.outputs[2]
    if streak > 0:    # helai rambut: pita Wave sepanjang sumbu Z (arah helai), terdistorsi noise -> bias terang/gelap tipis
        wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = 'BANDS'; wv.bands_direction = 'X'; wv.inputs["Scale"].default_value = 70
        wv.inputs["Distortion"].default_value = 6.0; wv.inputs["Detail"].default_value = 2.0
        wm = nt.nodes.new("ShaderNodeMix"); wm.data_type = 'RGBA'; wm.blend_type = 'OVERLAY'; wm.inputs[0].default_value = streak
        nt.links.new(last, wm.inputs[6]); nt.links.new(wv.outputs["Color"], wm.inputs[7]); last = wm.outputs[2]
    if fabric > 0:    # serat kain halus (noise frekuensi tinggi) -> tampak bertekstur, bukan datar
        fz = nt.nodes.new("ShaderNodeTexNoise"); fz.inputs["Scale"].default_value = 220; fz.inputs["Detail"].default_value = 1.0
        fm_ = nt.nodes.new("ShaderNodeMix"); fm_.data_type = 'RGBA'; fm_.blend_type = 'OVERLAY'; fm_.inputs[0].default_value = fabric
        nt.links.new(last, fm_.inputs[6]); nt.links.new(fz.outputs["Color"], fm_.inputs[7]); last = fm_.outputs[2]
    if ao > 0:     # bayangan kontak lukis (bawah lengan, lipatan, ketiak): AO dicampur dengan warna bayangan
        try:
            aon = nt.nodes.new("ShaderNodeAmbientOcclusion"); aon.inputs["Distance"].default_value = 0.06; aon.samples = 4
            mxa = nt.nodes.new("ShaderNodeMix"); mxa.data_type = 'RGBA'; mxa.blend_type = 'MIX'
            nt.links.new(aon.outputs["AO"], mxa.inputs[0]); mxa.inputs[6].default_value = (*shadow, 1); nt.links.new(last, mxa.inputs[7])
            mxa.inputs[0].default_value = 1.0; nt.links.new(aon.outputs["AO"], mxa.inputs[0])
            # faktor: AO=1 (terbuka) -> warna asli; AO=0 (tertutup) -> warna bayangan; dibatasi 'ao' agar halus
            mxo = nt.nodes.new("ShaderNodeMix"); mxo.data_type = 'RGBA'; mxo.inputs[0].default_value = ao
            nt.links.new(last, mxo.inputs[6]); nt.links.new(mxa.outputs[2], mxo.inputs[7]); last = mxo.outputs[2]
        except Exception as e: print("AO skip", str(e)[:60])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 1.0
    nt.links.new(last, em.inputs["Color"]); nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return m

def outline_mat(name="M_Outline", color=(0.20, 0.10, 0.09)):
    m, nt, out = _new(name)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*color, 1); em.inputs["Strength"].default_value = 1.0
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    m.use_backface_culling = True
    try: m.use_backface_culling_shadow = True
    except Exception: pass
    return m

def add_outline(obj, thickness=0.0035, mat=None, name="Outline"):
    """Inverted hull: slot material objek harus sudah ada; garis memakai slot setelahnya."""
    mat = mat or bpy.data.materials["M_Outline"]
    obj.data.materials.append(mat)
    sd = obj.modifiers.new(name, 'SOLIDIFY')
    sd.thickness = thickness; sd.offset = 1.0; sd.use_flip_normals = True
    sd.material_offset = len(obj.data.materials) - 1 - 0  # asumsi tepat 1 slot utama sebelum outline
    sd.use_rim = False
    return sd

def eye_mat(name, iris_top=(0.17, 0.08, 0.04), iris_bot=(0.55, 0.30, 0.10)):
    m, nt, out = _new(name)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nv = nt.nodes.new("ShaderNodeVectorMath"); nv.operation = 'NORMALIZE'; nt.links.new(tc.outputs["Object"], nv.inputs[0])
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(nv.outputs[0], sp.inputs[0])
    neg = nt.nodes.new("ShaderNodeMath"); neg.operation = 'MULTIPLY'; neg.inputs[1].default_value = -1.0   # maju = -Y
    nt.links.new(sp.outputs["Y"], neg.inputs[0])
    def thr(lo):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = 'GREATER_THAN'; n.inputs[1].default_value = lo; nt.links.new(neg.outputs[0], n.inputs[0]); return n.outputs[0]
    iris = thr(math.cos(0.64)); limb = thr(math.cos(0.60)); pupil = thr(math.cos(0.27))
    # gradien vertikal iris + pinggiran gelap
    gz = nt.nodes.new("ShaderNodeMapRange"); gz.inputs[1].default_value = -0.55; gz.inputs[2].default_value = 0.55
    nt.links.new(sp.outputs["Z"], gz.inputs[0])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.inputs[6].default_value = (*iris_bot, 1); mix.inputs[7].default_value = (*iris_top, 1)
    nt.links.new(gz.outputs[0], mix.inputs[0])
    # sclera -> iris -> pinggir gelap -> pupil
    c0 = nt.nodes.new("ShaderNodeMix"); c0.data_type = 'RGBA'; c0.inputs[6].default_value = (0.93, 0.92, 0.90, 1)
    nt.links.new(iris, c0.inputs[0]); nt.links.new(mix.outputs[2], c0.inputs[7])
    c1 = nt.nodes.new("ShaderNodeMix"); c1.data_type = 'RGBA'; c1.inputs[7].default_value = (0.02, 0.012, 0.01, 1)
    ring = nt.nodes.new("ShaderNodeMath"); ring.operation = 'SUBTRACT'; nt.links.new(iris, ring.inputs[0]); nt.links.new(limb, ring.inputs[1])
    nt.links.new(ring.outputs[0], c1.inputs[0]); nt.links.new(c0.outputs[2], c1.inputs[6])
    c2 = nt.nodes.new("ShaderNodeMix"); c2.data_type = 'RGBA'; c2.inputs[7].default_value = (0.005, 0.003, 0.003, 1)
    nt.links.new(pupil, c2.inputs[0]); nt.links.new(c1.outputs[2], c2.inputs[6])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 0.9
    nt.links.new(c2.outputs[2], em.inputs["Color"]); nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return m

def glow_mat(name="M_Sparkle", strength=7.0):
    m, nt, out = _new(name)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (1, 1, 1, 1); em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return m

TL = {}
TL["outline"] = outline_mat()
TL["outline_hair"] = outline_mat("M_Outline_Hair", (0.07, 0.06, 0.14))
# kulit: bayangan hangat kemerahan (ala anime), highlight halus
TL["skin_lastri"] = toon("T_Skin_Lastri", (0.86, 0.60, 0.42), shadow=(0.74, 0.42, 0.32), shade_pos=0.50, soft=0.34, core_pos=0.12, spec=0.0, rim=0.25, noise=0.04)
TL["skin_cust"] = toon("T_Skin_Cust", (0.92, 0.68, 0.50), shadow=(0.80, 0.48, 0.36), shade_pos=0.50, soft=0.34, core_pos=0.12, rim=0.25, noise=0.04)
TL["hair_black"] = toon("T_Hair", (0.055, 0.045, 0.05), shadow=(0.02, 0.018, 0.025), shade_pos=0.60, soft=0.10, ring=0.75, ring_color=(0.40, 0.45, 0.62), rim=0.4, streak=0.35)
TL["blouse"] = toon("T_Blouse", (0.92, 0.50, 0.40), shade_pos=0.60, soft=0.14, rim=0.2, noise=0.06, fabric=0.10)
TL["apron"] = toon("T_Apron", (0.10, 0.52, 0.55), shade_pos=0.60, soft=0.14, rim=0.2, noise=0.06, fabric=0.10)
TL["skirt"] = toon("T_Skirt", (0.45, 0.20, 0.12), shade_pos=0.60, soft=0.14, noise=0.08, fabric=0.10)
TL["jacket"] = toon("T_Jacket", (0.96, 0.75, 0.16), shade_pos=0.60, soft=0.14, rim=0.25, noise=0.05, fabric=0.10)
TL["tshirt"] = toon("T_Tshirt", (0.93, 0.92, 0.88), shade_pos=0.60, soft=0.14, noise=0.04, fabric=0.10)
TL["jeans"] = toon("T_Jeans", (0.10, 0.17, 0.36), shade_pos=0.60, soft=0.12, noise=0.1, fabric=0.10)
TL["backpack"] = toon("T_Backpack", (0.08, 0.55, 0.56), shade_pos=0.60, soft=0.12, spec=0.4, noise=0.05, fabric=0.10)
TL["shoe"] = toon("T_Shoe", (0.55, 0.30, 0.16), shade_pos=0.60, soft=0.12, spec=0.35)
TL["sole"] = toon("T_Sole", (0.9, 0.9, 0.88), shade_pos=0.60, soft=0.12)
TL["sandal"] = toon("T_Sandal", (0.12, 0.12, 0.14), shade_pos=0.60, soft=0.12, spec=0.3)
TL["eye_l"] = eye_mat("T_Eye_Lastri", (0.16, 0.07, 0.03), (0.50, 0.26, 0.09))
TL["eye_c"] = eye_mat("T_Eye_Cust", (0.10, 0.06, 0.04), (0.42, 0.24, 0.10))
TL["sparkle"] = glow_mat()
TL["lash"] = toon("T_Lash", (0.02, 0.012, 0.012), shade_pos=0.60)
TL["mouth_in"] = toon("T_MouthIn", (0.45, 0.10, 0.10), shade_pos=0.60)
TL["lip"] = toon("T_Lip", (0.72, 0.30, 0.28), shade_pos=0.60)
TL["white"] = toon("T_White", (0.95, 0.94, 0.90), shade_pos=0.60, soft=0.12)
TL["blush"] = toon("T_Blush", (0.95, 0.45, 0.42), shade_pos=0.60)
TL["nose"] = toon("T_Nose", (0.55, 0.30, 0.20), shade_pos=0.60)
bpy.app.driver_namespace["TOON"] = TL
bpy.app.driver_namespace["TOONFN"] = {"toon": toon, "add_outline": add_outline, "outline_mat": outline_mat}
print("toon lib:", len(TL))
