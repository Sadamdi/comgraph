# 16 - Look Ghibli: material dunia jadi "cat" (toon berpita bayangan ungu hangat + sapuan kuas), langit & awan prosedural bergerak
import bpy, math

SKIP = ("M_Glass", "M_Bulb", "M_PhoneScreen", "screen.001", "M_Sparkle", "M_Outline", "M_Outline_Hair", "Dots Stroke", "Material")

def paint_material(m, sat=1.22, val=1.30, shadow=(0.74, 0.68, 0.92), mid=(0.97, 0.93, 0.97), light=(1.22, 1.15, 1.02), soft=0.10, brush=0.10):
    nt = m.node_tree
    if any(n.label == "GHIBLI" for n in nt.nodes): return False
    bs = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
    if bs is None or out is None: return False
    links = bs.inputs["Base Color"].links
    src = links[0].from_socket if links else None
    base = tuple(bs.inputs["Base Color"].default_value)
    def N(t, lab="GHIBLI"):
        n = nt.nodes.new(t); n.label = lab; return n
    # warna sumber -> saturasi & value (palet hangat)
    hs = N("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value = sat; hs.inputs["Value"].default_value = val
    if src is not None: nt.links.new(src, hs.inputs["Color"])
    else: hs.inputs["Color"].default_value = base
    # faktor cahaya dari Diffuse -> ShaderToRGB -> ramp 3 pita
    df = N("ShaderNodeBsdfDiffuse"); df.inputs["Color"].default_value = (1, 1, 1, 1)
    s2 = N("ShaderNodeShaderToRGB"); nt.links.new(df.outputs["BSDF"], s2.inputs["Shader"])
    bw = N("ShaderNodeRGBToBW"); nt.links.new(s2.outputs["Color"], bw.inputs["Color"])
    cr = N("ShaderNodeValToRGB"); cr.color_ramp.interpolation = 'EASE'
    e = cr.color_ramp.elements
    e[0].position = 0.18; e[0].color = (*shadow, 1)
    e[1].position = 0.62 + soft; e[1].color = (*light, 1)
    md = e.new(0.50); md.color = (*mid, 1)
    nt.links.new(bw.outputs["Val"], cr.inputs["Fac"])
    mx = N("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1.0
    nt.links.new(hs.outputs["Color"], mx.inputs[6]); nt.links.new(cr.outputs["Color"], mx.inputs[7])
    last = mx.outputs[2]
    # sapuan kuas: noise anisotropik halus, overlay
    tc = N("ShaderNodeTexCoord"); mp = N("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (3.0, 3.0, 22.0)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = N("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9.0; nz.inputs["Detail"].default_value = 6.0; nz.inputs["Roughness"].default_value = 0.65
    nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    ov = N("ShaderNodeMix"); ov.data_type = 'RGBA'; ov.blend_type = 'OVERLAY'; ov.inputs[0].default_value = brush
    nt.links.new(last, ov.inputs[6]); nt.links.new(nz.outputs["Color"], ov.inputs[7])
    em = N("ShaderNodeEmission"); em.inputs["Strength"].default_value = 1.0
    nt.links.new(ov.outputs[2], em.inputs["Color"]); nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return True

def paint_all():
    n = 0
    for m in bpy.data.materials:
        if not m.use_nodes or m.name in SKIP or m.name.startswith("T_") or not m.users: continue
        try:
            if paint_material(m): n += 1
        except Exception as ex:
            print("skip", m.name, str(ex)[:80])
    print("material dicat:", n)

def ghibli_sky():
    w = bpy.context.scene.world; nt = w.node_tree
    for n in [x for x in nt.nodes if x.label.startswith("GSKY")]: nt.nodes.remove(n)
    def N(t, lab="GSKY"):
        n = nt.nodes.new(t); n.label = lab; return n
    tc = N("ShaderNodeTexCoord")
    nm = N("ShaderNodeVectorMath"); nm.operation = 'NORMALIZE'; nt.links.new(tc.outputs["Generated"], nm.inputs[0])
    sp = N("ShaderNodeSeparateXYZ"); nt.links.new(nm.outputs[0], sp.inputs[0])
    # gradien langit: pagi (biru jernih + cakrawala krem) -> sore (jingga keemasan + biru lembayung)
    def ramp(lab, cols):
        r = N("ShaderNodeValToRGB", lab); r.color_ramp.interpolation = 'EASE'
        el = r.color_ramp.elements; el[0].position = 0.0; el[0].color = (*cols[0], 1); el[1].position = 1.0; el[1].color = (*cols[-1], 1)
        if len(cols) > 2:
            m = el.new(0.35); m.color = (*cols[1], 1)
        nt.links.new(clamp.outputs[0], r.inputs["Fac"]); return r
    clamp = N("ShaderNodeClamp"); nt.links.new(sp.outputs["Z"], clamp.inputs["Value"]); clamp.inputs["Min"].default_value = 0.0; clamp.inputs["Max"].default_value = 1.0
    day = ramp("GSKY_day", [(0.93, 0.96, 0.92), (0.55, 0.80, 0.98), (0.16, 0.45, 0.92)])
    eve = ramp("GSKY_eve", [(1.00, 0.80, 0.55), (0.98, 0.62, 0.60), (0.36, 0.42, 0.80)])
    mixd = N("ShaderNodeMix", "GSKY_mix"); mixd.data_type = 'RGBA'
    nt.links.new(day.outputs[0], mixd.inputs[6]); nt.links.new(eve.outputs[0], mixd.inputs[7])
    mixd.inputs[0].default_value = 0.0; mixd.inputs[0].keyframe_insert("default_value", frame=1320)
    mixd.inputs[0].default_value = 1.0; mixd.inputs[0].keyframe_insert("default_value", frame=1321)
    # awan kumulus bergaya Ghibli: proyeksi ke bidang + ambang keras + sisi bawah berbayang
    dv = N("ShaderNodeMath"); dv.operation = 'ADD'; dv.inputs[1].default_value = 0.32; nt.links.new(sp.outputs["Z"], dv.inputs[0])
    iv = N("ShaderNodeMath"); iv.operation = 'DIVIDE'; iv.inputs[0].default_value = 1.0; nt.links.new(dv.outputs[0], iv.inputs[1])
    pxy = N("ShaderNodeCombineXYZ")
    mx_ = N("ShaderNodeMath"); mx_.operation = 'MULTIPLY'; nt.links.new(sp.outputs["X"], mx_.inputs[0]); nt.links.new(iv.outputs[0], mx_.inputs[1])
    my_ = N("ShaderNodeMath"); my_.operation = 'MULTIPLY'; nt.links.new(sp.outputs["Y"], my_.inputs[0]); nt.links.new(iv.outputs[0], my_.inputs[1])
    nt.links.new(mx_.outputs[0], pxy.inputs["X"]); nt.links.new(my_.outputs[0], pxy.inputs["Y"])
    mp = N("ShaderNodeMapping", "GSKY_map"); nt.links.new(pxy.outputs[0], mp.inputs["Vector"])
    mp.inputs["Scale"].default_value = (0.9, 0.9, 0.9)
    drv = mp.inputs["Location"].driver_add("default_value", 0).driver
    drv.type = 'SCRIPTED'; drv.expression = "frame*0.0012"
    def cloud(lab, off):
        v = N("ShaderNodeVectorMath", lab + "_off"); v.operation = 'ADD'; v.inputs[1].default_value = (0, off, 0)
        nt.links.new(mp.outputs[0], v.inputs[0])
        nz = N("ShaderNodeTexNoise", lab); nz.noise_dimensions = '3D'; nz.inputs["Scale"].default_value = 1.8; nz.inputs["Detail"].default_value = 5.0; nz.inputs["Roughness"].default_value = 0.55
        nt.links.new(v.outputs[0], nz.inputs["Vector"])
        cr = N("ShaderNodeValToRGB", lab + "_cut"); cr.color_ramp.interpolation = 'EASE'
        e = cr.color_ramp.elements; e[0].position = 0.545; e[0].color = (0, 0, 0, 1); e[1].position = 0.575; e[1].color = (1, 1, 1, 1)
        nt.links.new(nz.outputs["Fac"], cr.inputs["Fac"]); return cr.outputs[0]
    A = cloud("GSKY_cloudA", 0.0); B = cloud("GSKY_cloudB", 0.10)
    # horizon memudar: awan hanya di atas ufuk
    hz = N("ShaderNodeMapRange", "GSKY_hz"); hz.inputs[1].default_value = 0.02; hz.inputs[2].default_value = 0.22
    nt.links.new(sp.outputs["Z"], hz.inputs[0])
    am = N("ShaderNodeMath"); am.operation = 'MULTIPLY'; nt.links.new(A, am.inputs[0]); nt.links.new(hz.outputs[0], am.inputs[1])
    # warna awan: terang vs sisi bawah berbayang (lavender/pink)
    cl = N("ShaderNodeMix", "GSKY_cloudcol"); cl.data_type = 'RGBA'
    cl.inputs[6].default_value = (0.78, 0.80, 0.96, 1)  # bayangan
    cl.inputs[7].default_value = (1.0, 0.99, 0.95, 1)   # terang
    nt.links.new(B, cl.inputs[0])
    sky = N("ShaderNodeMix", "GSKY_final"); sky.data_type = 'RGBA'
    nt.links.new(am.outputs[0], sky.inputs[0]); nt.links.new(mixd.outputs[2], sky.inputs[6]); nt.links.new(cl.outputs[2], sky.inputs[7])
    # pakai sebagai warna sinar kamera (ganti Sky Texture)
    bg = nt.nodes["Background.001"]
    for l in list(bg.inputs["Color"].links): nt.links.remove(l)
    nt.links.new(sky.outputs[2], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 1.0
    print("langit ghibli ok")

paint_all()
ghibli_sky()
