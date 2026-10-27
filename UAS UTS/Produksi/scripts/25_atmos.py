# 25 - Atmosfer & pencahayaan per gaya. Ghibli = dunia dilukis (Emission toon), bayangan warna ungu lembut, kabut hangat.
# Pocari = dunia "real" (material PBR asli + GI ray-traced + bayangan tegas/lembut fisik) dengan tokoh anime, langit biru jernih, bloom kuat. Meniru "tampilan neural rendering" lewat GI, volumetrik, bloom, DOF, grading (bukan DLSS sungguhan).
import bpy, math
SC = bpy.context.scene
OB = bpy.data.objects

def set_realistic(flag):
    n = 0
    for m in bpy.data.materials:
        if not m.use_nodes: continue
        nt = m.node_tree
        if not any(x.label == "GHIBLI" for x in nt.nodes): continue
        bs = next((x for x in nt.nodes if x.type == 'BSDF_PRINCIPLED'), None); out = next((x for x in nt.nodes if x.type == 'OUTPUT_MATERIAL'), None)
        em = next((x for x in nt.nodes if x.type == 'EMISSION' and x.label == "GHIBLI"), None)
        if bs is None or out is None or em is None: continue
        nt.links.new((bs.outputs[0] if flag else em.outputs[0]), out.inputs["Surface"]); n += 1
    print("material", "REAL" if flag else "LUKIS", n)

def atmos(style):
    ev = SC.eevee
    def ts(o, k, v):
        try: setattr(o, k, v)
        except Exception as e: print("skip", k, str(e)[:50])
    sun = OB["SUN_Key"].data
    if style == "pocari":
        ts(sun, "angle", math.radians(0.5)); ts(sun, "energy", 4.2)
        ts(ev, "shadow_ray_count", 3); ts(ev, "shadow_step_count", 12); ts(ev, "use_volumetric_shadows", True)
        dens, aniso, col = 0.004, 0.55, (0.92, 0.96, 1.0)
    else:
        ts(sun, "angle", math.radians(1.6)); ts(sun, "energy", 3.4)
        ts(ev, "shadow_ray_count", 2); ts(ev, "shadow_step_count", 8)
        dens, aniso, col = 0.006, 0.6, (1.0, 0.88, 0.68)
    ts(sun, "shadow_cascade_max_distance", 40.0); ts(sun, "shadow_cascade_count", 4); ts(sun, "shadow_cascade_exponent", 0.7)
    ts(sun, "shadow_maximum_resolution", 0.004); ts(sun, "shadow_filter_radius", 0.6)
    ts(ev, "use_raytracing", True); ts(ev, "ray_tracing_method", 'SCREEN')
    try: ev.ray_tracing_options.resolution_scale = '1'; ev.ray_tracing_options.trace_max_roughness = 0.6
    except Exception as e: print("rt opts", str(e)[:50])
    for k, v in (("volumetric_tile_size", '4'), ("volumetric_samples", 48), ("volumetric_start", 0.1), ("volumetric_end", 60.0), ("use_volumetric_shadows", True)): ts(ev, k, v)
    # volume atmosfer (kabut tipis + berkas cahaya)
    a = OB.get("ATMOS")
    if a is None:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -1.5, 4)); a = bpy.context.active_object; a.name = "ATMOS"; a.scale = (30, 24, 8.5)
        a.display_type = 'WIRE'; a.visible_shadow = False
        m = bpy.data.materials.get("M_Atmos") or bpy.data.materials.new("M_Atmos"); m.use_nodes = True
        a.data.materials.append(m)
    m = a.data.materials[0]; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); vs = nt.nodes.new("ShaderNodeVolumeScatter")
    vs.inputs["Density"].default_value = dens; vs.inputs["Anisotropy"].default_value = aniso; vs.inputs["Color"].default_value = (*col, 1)
    nt.links.new(vs.outputs[0], out.inputs["Volume"])
    # kerapatan sedikit berubah (kabut bergerak)
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.6; nz.inputs["Detail"].default_value = 2
    mp = nt.nodes.new("ShaderNodeMath"); mp.operation = 'MULTIPLY_ADD'; mp.inputs[1].default_value = 1.2; mp.inputs[2].default_value = 0.5
    tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mk = nt.nodes.new("ShaderNodeMath"); mk.operation = 'MULTIPLY'; mk.inputs[1].default_value = dens * 2.0
    nt.links.new(nz.outputs["Fac"], mp.inputs[0]); nt.links.new(mp.outputs[0], mk.inputs[0]); nt.links.new(mk.outputs[0], vs.inputs["Density"])
    set_realistic(style == "pocari")
    SC.view_settings.view_transform = 'AgX' if style == "pocari" else 'Standard'
    try: SC.view_settings.look = 'AgX - Medium High Contrast' if style == "pocari" else 'None'
    except Exception as e: print("look", str(e)[:60])
    print("atmos", style)

STYLE = globals().get("STYLE_ENV", "ghibli")
atmos(STYLE)
