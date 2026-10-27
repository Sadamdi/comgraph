# 02 - Pustaka material "real world": PBR bertekstur (Poly Haven CC0) + prosedural
# Diffuse (matte) vs specular/glossy (mengilap) sengaja dibedakan jelas (bukti poin 7 dosen)
import bpy, math, random

TEX = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\assets\tex"

def _principled(m):
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")

def _img(nt, name, cs):
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(f"{TEX}\\{name}", check_existing=True)
    n.image.colorspace_settings.name = cs
    n.interpolation = 'Smart'
    return n

def new_mat(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    for n in list(m.node_tree.nodes):
        if n.type != 'OUTPUT_MATERIAL' and n.type != 'BSDF_PRINCIPLED': m.node_tree.nodes.remove(n)
    return m

def pbr(name, tex, scale=1.0, tint=(1, 1, 1), tint_mix=0.0, normal=1.0, rough_mul=1.0, blend=0.25, spec=0.5):
    """Material PBR dari set tekstur Poly Haven. Koordinat = posisi dunia (set statis)."""
    m = new_mat(name); nt = m.node_tree; b = _principled(m)
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale, scale, scale)
    nt.links.new(geo.outputs["Position"], mp.inputs["Vector"])
    d = _img(nt, f"{tex}_diff_1k.jpg", "sRGB"); r = _img(nt, f"{tex}_rough_1k.jpg", "Non-Color"); n = _img(nt, f"{tex}_nor_1k.jpg", "Non-Color")
    for t in (d, r, n):
        t.projection = 'BOX'; t.projection_blend = blend
        nt.links.new(mp.outputs["Vector"], t.inputs["Vector"])
    col = d.outputs["Color"]
    if tint_mix > 0:
        mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
        mix.inputs[0].default_value = tint_mix; mix.inputs[6].default_value = (*tint, 1)
        nt.links.new(col, mix.inputs[7]); col = mix.outputs[2]
    nt.links.new(col, b.inputs["Base Color"])
    if rough_mul != 1.0:
        mr = nt.nodes.new("ShaderNodeMath"); mr.operation = 'MULTIPLY'; mr.inputs[1].default_value = rough_mul
        nt.links.new(r.outputs["Color"], mr.inputs[0]); nt.links.new(mr.outputs[0], b.inputs["Roughness"])
    else:
        nt.links.new(r.outputs["Color"], b.inputs["Roughness"])
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = normal
    nt.links.new(n.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    try: b.inputs["Specular IOR Level"].default_value = spec
    except KeyError: pass
    return m

def paint(name, color, rough=0.55, spec=0.5, noise_bump=0.06, metallic=0.0, coat=0.0, dirt=0.18, noise_scale=40.0):
    """Cat/plastik/kain prosedural: warna + variasi kasar + bump halus + kotoran ringan."""
    m = new_mat(name); nt = m.node_tree; b = _principled(m)
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = noise_scale; nz.inputs["Detail"].default_value = 6
    nt.links.new(geo.outputs["Position"], nz.inputs["Vector"])
    # variasi warna halus (kotoran/pemudaran)
    cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].position = 0.35; cr.color_ramp.elements[1].position = 0.7
    cr.color_ramp.elements[0].color = (1, 1, 1, 1); cr.color_ramp.elements[1].color = (1 - dirt, 1 - dirt, 1 - dirt, 1)
    nt.links.new(nz.outputs["Fac"], cr.inputs["Fac"])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs[0].default_value = 1.0
    mix.inputs[6].default_value = (*color, 1); nt.links.new(cr.outputs["Color"], mix.inputs[7])
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    # roughness bervariasi
    rr = nt.nodes.new("ShaderNodeMapRange"); rr.inputs[3].default_value = max(rough - 0.12, 0.02); rr.inputs[4].default_value = min(rough + 0.12, 1)
    nt.links.new(nz.outputs["Fac"], rr.inputs[0]); nt.links.new(rr.outputs[0], b.inputs["Roughness"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = noise_bump; bp.inputs["Distance"].default_value = 0.01
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Metallic"].default_value = metallic
    try:
        b.inputs["Specular IOR Level"].default_value = spec
        b.inputs["Coat Weight"].default_value = coat; b.inputs["Coat Roughness"].default_value = 0.1
    except KeyError: pass
    return m

def fabric_stripes(name, c1, c2, stripes=14, rough=0.85):
    m = new_mat(name); nt = m.node_tree; b = _principled(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sp.inputs[0])
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = 'BANDS'; wv.bands_direction = 'X'; wv.inputs["Scale"].default_value = stripes
    wv.inputs["Distortion"].default_value = 0.0; wv.wave_profile = 'SAW'
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    st = nt.nodes.new("ShaderNodeMath"); st.operation = 'GREATER_THAN'; st.inputs[1].default_value = 0.5
    nt.links.new(wv.outputs["Fac"], st.inputs[0])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'
    mix.inputs[6].default_value = (*c1, 1); mix.inputs[7].default_value = (*c2, 1)
    nt.links.new(st.outputs[0], mix.inputs[0]); nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    wv2 = nt.nodes.new("ShaderNodeTexWave"); wv2.wave_type = 'BANDS'; wv2.inputs["Scale"].default_value = 260; wv2.inputs["Distortion"].default_value = 0
    wv3 = nt.nodes.new("ShaderNodeTexWave"); wv3.wave_type = 'BANDS'; wv3.bands_direction = 'Y'; wv3.inputs["Scale"].default_value = 260
    for w in (wv2, wv3): nt.links.new(tc.outputs["Object"], w.inputs["Vector"])
    add = nt.nodes.new("ShaderNodeMath"); add.operation = 'ADD'
    nt.links.new(wv2.outputs["Fac"], add.inputs[0]); nt.links.new(wv3.outputs["Fac"], add.inputs[1])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.25; bp.inputs["Distance"].default_value = 0.004
    nt.links.new(add.outputs[0], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = rough
    try: b.inputs["Sheen Weight"].default_value = 0.5
    except KeyError: pass
    return m

def skin(name, color, rough=0.55, sss=0.25):
    m = new_mat(name); b = _principled(m)
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough
    try:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2)
        b.inputs["Subsurface Scale"].default_value = 0.02
        b.inputs["Specular IOR Level"].default_value = 0.45
    except KeyError as e:
        print("skin attr", e)
    return m

def cloth(name, color, rough=0.9, bump=0.3):
    m = new_mat(name); nt = m.node_tree; b = _principled(m)
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough
    tc = nt.nodes.new("ShaderNodeTexCoord")
    w1 = nt.nodes.new("ShaderNodeTexWave"); w1.wave_type = 'BANDS'; w1.inputs["Scale"].default_value = 300; w1.inputs["Distortion"].default_value = 1.0
    w2 = nt.nodes.new("ShaderNodeTexWave"); w2.wave_type = 'BANDS'; w2.bands_direction = 'Y'; w2.inputs["Scale"].default_value = 300; w2.inputs["Distortion"].default_value = 1.0
    for w in (w1, w2): nt.links.new(tc.outputs["Object"], w.inputs["Vector"])
    ad = nt.nodes.new("ShaderNodeMath"); nt.links.new(w1.outputs["Fac"], ad.inputs[0]); nt.links.new(w2.outputs["Fac"], ad.inputs[1])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump; bp.inputs["Distance"].default_value = 0.003
    nt.links.new(ad.outputs[0], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    try: b.inputs["Sheen Weight"].default_value = 0.4
    except KeyError: pass
    return m

def assign(obj, mat, slot=0):
    if obj.type not in ('MESH', 'CURVE', 'FONT'): return
    if len(obj.data.materials) == 0: obj.data.materials.append(mat)
    else:
        for i in range(len(obj.data.materials)): obj.data.materials[i] = mat

def build_library():
    L = {}
    L["paving"] = pbr("M_Paving", "large_floor_tiles_02", scale=0.45, tint=(0.95, 0.92, 0.86), tint_mix=0.4, normal=0.8)
    L["asphalt"] = pbr("M_Asphalt", "asphalt_02", scale=0.25, normal=1.0)
    L["plaster"] = pbr("M_Plaster", "painted_plaster_wall", scale=0.35, tint=(1.0, 0.95, 0.82), tint_mix=0.55, normal=0.8)
    L["shutter"] = pbr("M_Shutter", "painted_metal_shutter", scale=0.5, tint=(0.85, 0.95, 0.95), tint_mix=0.35, normal=1.0, spec=0.6)
    L["wood_counter"] = pbr("M_WoodCounter", "wood_table_001", scale=0.6, normal=0.7, spec=0.5)
    L["wood_paint"] = pbr("M_WoodPainted", "planks_brown_10", scale=0.7, tint=(0.80, 0.38, 0.25), tint_mix=0.8, normal=0.6)
    L["wood_post"] = pbr("M_WoodPost", "planks_brown_10", scale=0.7, tint=(0.75, 0.6, 0.45), tint_mix=0.5, normal=0.7)
    L["awning"] = fabric_stripes("M_Awning", (0.93, 0.89, 0.78), (0.78, 0.33, 0.22), stripes=14)
    L["sign_teal"] = paint("M_SignTeal", (0.05, 0.36, 0.40), rough=0.35, spec=0.6, coat=0.4, noise_bump=0.03, dirt=0.1)
    L["metal"] = paint("M_AluTray", (0.82, 0.83, 0.85), rough=0.28, spec=0.8, metallic=1.0, noise_bump=0.02, dirt=0.15)
    L["food"] = paint("M_Gorengan", (0.62, 0.34, 0.09), rough=0.55, spec=0.5, noise_bump=0.6, dirt=0.35, noise_scale=120)
    L["mustard"] = paint("M_Mustard", (0.80, 0.58, 0.10), rough=0.6, noise_bump=0.05)
    L["paper"] = paint("M_Paper", (0.92, 0.88, 0.78), rough=0.9, noise_bump=0.1, dirt=0.08)
    L["kraft"] = paint("M_Kraft", (0.55, 0.38, 0.22), rough=0.85, noise_bump=0.15, dirt=0.12)
    L["plastic_red"] = paint("M_PlasticRed", (0.65, 0.08, 0.06), rough=0.25, spec=0.7, coat=0.3, noise_bump=0.02)
    L["plastic_blue"] = paint("M_PlasticBlue", (0.08, 0.20, 0.55), rough=0.3, spec=0.7, coat=0.2, noise_bump=0.02)
    L["steel_dark"] = paint("M_SteelDark", (0.18, 0.18, 0.19), rough=0.35, spec=0.7, metallic=1.0, noise_bump=0.02, dirt=0.3)
    L["glass"] = new_mat("M_Glass"); g = _principled(L["glass"])
    g.inputs["Base Color"].default_value = (0.9, 0.95, 0.95, 1); g.inputs["Roughness"].default_value = 0.03
    try: g.inputs["Transmission Weight"].default_value = 1.0; g.inputs["IOR"].default_value = 1.45
    except KeyError: pass
    L["rubber"] = paint("M_Rubber", (0.02, 0.02, 0.02), rough=0.75, noise_bump=0.1, dirt=0.05)
    L["skin_lastri"] = skin("M_Skin_Lastri", (0.52, 0.31, 0.19))
    L["skin_cust"] = skin("M_Skin_Cust", (0.60, 0.38, 0.24))
    L["hair_black"] = paint("M_Hair", (0.015, 0.011, 0.010), rough=0.35, spec=0.7, noise_bump=0.03, dirt=0.0)
    L["teal_cloth"] = cloth("M_Apron_Teal", (0.05, 0.38, 0.42))
    L["salmon_cloth"] = cloth("M_Shirt_Lastri", (0.80, 0.45, 0.36))
    L["yellow_cloth"] = cloth("M_Jacket_Yellow", (0.90, 0.68, 0.10))
    L["navy_cloth"] = cloth("M_Jeans_Navy", (0.05, 0.08, 0.20), rough=0.85)
    L["teal_bag"] = cloth("M_Backpack", (0.05, 0.42, 0.45), rough=0.7, bump=0.15)
    L["shoe_brown"] = paint("M_Shoe_Brown", (0.25, 0.12, 0.06), rough=0.45, spec=0.5)
    L["sandal"] = paint("M_Sandal", (0.1, 0.1, 0.11), rough=0.5)
    L["eye_white"] = paint("M_EyeWhite", (0.95, 0.95, 0.93), rough=0.15, spec=0.8, noise_bump=0.0, dirt=0.0)
    L["iris"] = paint("M_Iris", (0.06, 0.035, 0.02), rough=0.1, spec=0.9, noise_bump=0.0, dirt=0.0)
    L["screen"] = new_mat("M_PhoneScreen"); s = _principled(L["screen"])
    s.inputs["Base Color"].default_value = (0.02, 0.03, 0.05, 1); s.inputs["Roughness"].default_value = 0.05
    try:
        s.inputs["Emission Color"].default_value = (0.25, 0.45, 0.8, 1); s.inputs["Emission Strength"].default_value = 0.6
    except KeyError: pass
    return L

LIB = build_library()
bpy.app.driver_namespace["MATLIB"] = LIB
bpy.app.driver_namespace["MATFN"] = {"assign": assign, "paint": paint, "pbr": pbr, "cloth": cloth, "skin": skin}
print("materials:", len(LIB))
