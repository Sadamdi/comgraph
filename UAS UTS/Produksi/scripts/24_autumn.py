# 24 - Musim gugur + angin: (a) daun pohon bergetar (Displace dengan noise yang bergeser = embusan), warna daun jadi kuning-oranye bercampur hijau,
# (b) daun berguguran (particle system + gaya angin) di atas warung & trotoar. Jalankan SEBELUM 23_plants (modifier ikut tersalin), lalu 23, lalu bagian (b) = fall_leaves().
import bpy, math, random
from mathutils import Vector

OB = bpy.data.objects
SC = bpy.context.scene

def tint_leaf_materials(hue=0.32, sat=1.25, val=1.12, mix_green=0.35):
    n = 0
    for m in bpy.data.materials:
        if not m.use_nodes or "leaves" not in m.name.lower(): continue
        nt = m.node_tree
        if any(x.label == "AUTUMN" for x in nt.nodes): continue
        bs = next((x for x in nt.nodes if x.type == 'BSDF_PRINCIPLED'), None)
        if bs is None or not bs.inputs["Base Color"].links: continue
        src = bs.inputs["Base Color"].links[0].from_socket
        hs = nt.nodes.new("ShaderNodeHueSaturation"); hs.label = "AUTUMN"
        hs.inputs["Hue"].default_value = hue; hs.inputs["Saturation"].default_value = sat; hs.inputs["Value"].default_value = val
        nt.links.new(src, hs.inputs["Color"])
        # campuran per-daun: noise pada koordinat objek menentukan sebagian daun tetap hijau
        ng = nt.nodes.new("ShaderNodeNewGeometry"); ng.label = "AUTUMN"
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.label = "AUTUMN"; nz.inputs["Scale"].default_value = 3.5; nz.inputs["Detail"].default_value = 2.0
        nt.links.new(ng.outputs["Position"], nz.inputs["Vector"])
        cr = nt.nodes.new("ShaderNodeValToRGB"); cr.label = "AUTUMN"; cr.color_ramp.elements[0].position = 0.42; cr.color_ramp.elements[1].position = 0.58
        nt.links.new(nz.outputs["Fac"], cr.inputs["Fac"])
        mx = nt.nodes.new("ShaderNodeMix"); mx.label = "AUTUMN"; mx.data_type = 'RGBA'
        nt.links.new(cr.outputs["Color"], mx.inputs[0]); nt.links.new(src, mx.inputs[6]); nt.links.new(hs.outputs["Color"], mx.inputs[7])
        nt.links.new(mx.outputs[2], bs.inputs["Base Color"]); n += 1
    print("material daun musim gugur:", n)

def flutter(obj, canopy_from=1.2, ramp=1.4, strength=0.035, scale=0.55, speed=0.012):
    """Getaran daun: dua Displace (sumbu Z dan X) memakai tekstur Clouds yang koordinatnya mengikuti Empty yang bergeser (embusan angin lewat)."""
    if any(m.name.startswith("WIND_") for m in obj.modifiers): return
    drv = OB.get("WIND_TEX_EMPTY")
    if drv is None:
        drv = bpy.data.objects.new("WIND_TEX_EMPTY", None); SC.collection.objects.link(drv)
        for f, p in ((1, (0, 0, 0)), (1200, (14, 9, 0)), (2700, (31, 20, 0))):
            drv.location = p; drv.keyframe_insert("location", frame=f)
        for fc in drv.animation_data.action.layers[0].strips[0].channelbags[0].fcurves:
            for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    tex = bpy.data.textures.get("WIND_noise") or bpy.data.textures.new("WIND_noise", 'CLOUDS')
    tex.noise_scale = scale; tex.noise_depth = 2
    vg = obj.vertex_groups.get("canopy") or obj.vertex_groups.new(name="canopy")
    me = obj.data
    zs = [v.co.z for v in me.vertices]
    ws = [max(0.0, min(1.0, (z - canopy_from) / ramp)) for z in zs]
    for i, w in enumerate(ws):
        if w > 0.001: vg.add([i], w, 'REPLACE')
    for nm, d, s in (("WIND_Z", 'Z', strength), ("WIND_X", 'X', strength * 0.7)):
        m = obj.modifiers.new(nm, 'DISPLACE'); m.texture = tex; m.texture_coords = 'OBJECT'; m.texture_coords_object = drv
        m.direction = d; m.strength = s; m.mid_level = 0.5; m.vertex_group = "canopy"

def prep_templates():
    tint_leaf_materials()
    for n, cf, rp in (("island_tree_02_LOD0", 1.0, 1.4), ("pachira_aquatica_01_leaves_b", -1.0, 0.1), ("potted_plant_01_leaves", 0.1, 0.4), ("shrub_01_a", -1.0, 0.1)):
        o = OB.get(n)
        if o: flutter(o, cf, rp, strength=0.03 if "island" in n else 0.022)
    print("flutter terpasang")

# ================= daun berguguran =================
def make_leaf_template():
    o = OB.get("FALL_LEAF_TEMPLATE")
    if o: return o
    me = bpy.data.meshes.new("FALL_LEAF"); import bmesh
    bm = bmesh.new(); n = 8
    for i in range(n + 1):
        t = i / n; w = math.sin(math.pi * t) ** 0.8 * 0.035; y = (t - 0.5) * 0.09
        bm.verts.new((-w, y, 0.004 * (1 - 2 * abs(t - 0.5)))); bm.verts.new((w, y, 0.004 * (1 - 2 * abs(t - 0.5))))
    bm.verts.ensure_lookup_table()
    for i in range(n): bm.faces.new((bm.verts[2 * i], bm.verts[2 * i + 1], bm.verts[2 * i + 3], bm.verts[2 * i + 2]))
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new("FALL_LEAF_TEMPLATE", me); SC.collection.objects.link(o); o.location = (0, 0, -80)
    m = bpy.data.materials.get("M_FallLeaf") or bpy.data.materials.new("M_FallLeaf"); m.use_nodes = True; nt = m.node_tree
    for x in list(nt.nodes): nt.nodes.remove(x)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); oi = nt.nodes.new("ShaderNodeObjectInfo"); pi = nt.nodes.new("ShaderNodeParticleInfo")
    cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.interpolation = 'CONSTANT'
    el = cr.color_ramp.elements; el[0].position = 0.0; el[0].color = (0.82, 0.30, 0.08, 1); el[1].position = 0.34; el[1].color = (0.95, 0.62, 0.12, 1)
    e3 = el.new(0.68); e3.color = (0.70, 0.18, 0.06, 1)
    nt.links.new(pi.outputs["Random"], cr.inputs["Fac"])
    df = nt.nodes.new("ShaderNodeBsdfDiffuse"); nt.links.new(cr.outputs["Color"], df.inputs["Color"])
    tr = nt.nodes.new("ShaderNodeBsdfTranslucent"); nt.links.new(cr.outputs["Color"], tr.inputs["Color"])
    mx = nt.nodes.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.4
    nt.links.new(df.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs["Surface"])
    m.use_backface_culling = False
    me.materials.append(m); return o

def fall_leaves():
    for o in [o for o in OB if o.name.startswith(("FALL_EMIT", "WIND_FIELD"))]: bpy.data.objects.remove(o)
    leaf = make_leaf_template()
    wf = bpy.data.objects.new("WIND_FIELD", None); SC.collection.objects.link(wf)
    wf.empty_display_type = 'SINGLE_ARROW'; wf.location = (4, -6, 3); wf.rotation_euler = (math.radians(100), 0, math.radians(35))
    bpy.context.view_layer.objects.active = wf
    for o_ in bpy.context.selected_objects: o_.select_set(False)
    wf.select_set(True)
    if wf.field is None: bpy.ops.object.forcefield_toggle()
    wf.field.type = 'WIND'; wf.field.strength = 1.6; wf.field.noise = 1.2; wf.field.flow = 0.4; wf.field.seed = 7
    # kekuatan angin berubah pelan (embusan)
    for f, s in ((1, 1.2), (300, 2.4), (700, 1.0), (1300, 2.6), (1800, 1.3), (2300, 2.8), (2700, 1.4)):
        wf.field.strength = s; wf.field.keyframe_insert("strength", frame=f)
    spec = [("A", (0.0, -0.5, 4.2), (7.0, 5.0), 160), ("B", (-4.0, 1.5, 4.8), (4.0, 3.0), 70), ("C", (4.5, 1.0, 4.8), (4.0, 3.0), 70)]
    for tag, loc, size, count in spec:
        bpy.ops.mesh.primitive_plane_add(size=1, location=loc); em = bpy.context.active_object; em.name = "FALL_EMIT_" + tag
        em.scale = (size[0], size[1], 1); em.hide_render = True    # pemancar tidak dirender
        ps = em.modifiers.new("Leaves", 'PARTICLE_SYSTEM'); st = ps.particle_system.settings
        st.count = count; st.frame_start = -400; st.frame_end = 2650; st.lifetime = 520; st.lifetime_random = 0.45
        st.emit_from = 'FACE'; st.normal_factor = 0.0; st.object_align_factor = (0, 0, 0)
        st.physics_type = 'NEWTON'; st.mass = 0.012; st.use_dynamic_rotation = True; st.use_rotations = True; st.rotation_mode = 'NONE'; st.angular_velocity_factor = 3.0
        try: st.angular_velocity_mode = 'RAND'
        except Exception: pass
        st.rotation_factor_random = 1.0; st.phase_factor_random = 2.0
        st.render_type = 'OBJECT'; st.instance_object = leaf; st.particle_size = 1.0; st.size_random = 0.5
        st.effector_weights.gravity = 0.06; st.effector_weights.wind = 1.0
        st.drag_factor = 0.55; st.brownian_factor = 0.35; st.damping = 0.1
        st.show_unborn = False; st.use_dead = False
    SC.frame_set(1)
    print("daun berguguran siap")

# ================= daun berguguran v2: driver (tanpa simulasi partikel, deterministik) =================
def fall_leaves_v2(n=170, seed=11):
    rnd = random.Random(seed)
    for o in [o for o in OB if o.name.startswith(("FALL_EMIT", "FALL_L_", "WIND_FIELD"))]: bpy.data.objects.remove(o)
    leaf = make_leaf_template()
    m = bpy.data.materials["M_FallLeaf"]; nt = m.node_tree
    for x in nt.nodes:
        if x.type == 'PARTICLE_INFO':
            oi = nt.nodes.new("ShaderNodeObjectInfo")
            for l in list(x.outputs["Random"].links): nt.links.new(oi.outputs["Random"], l.to_socket)
    coll = bpy.data.collections.get("13_EXTRAS") or SC.collection
    for i in range(n):
        o = bpy.data.objects.new(f"FALL_L_{i}", leaf.data); coll.objects.link(o)
        x0 = rnd.uniform(-6.0, 6.0); y0 = rnd.uniform(-5.5, 3.0); zt = rnd.uniform(4.0, 5.2)
        T = rnd.uniform(360, 470); off = rnd.uniform(0, T); ph = rnd.uniform(0, 6.28); v = zt / (T - 50)
        A = rnd.uniform(0.25, 0.6); w = rnd.uniform(0.035, 0.07); dr = rnd.uniform(0.003, 0.007); sz = rnd.uniform(0.7, 1.3)
        ph_expr = f"fmod(frame+{off:.1f},{T:.1f})"
        exprs = [f"{x0:.3f}+{A:.3f}*sin({w:.4f}*frame+{ph:.3f})+{dr:.4f}*{ph_expr}",
                 f"{y0:.3f}+{A*0.6:.3f}*cos({w*0.8:.4f}*frame+{ph:.3f})+0.002*{ph_expr}",
                 f"max({zt:.3f}-{v:.5f}*{ph_expr},0.025)"]
        for k, ex in enumerate(exprs):
            d = o.driver_add("location", k).driver; d.type = 'SCRIPTED'; d.expression = ex
        rots = [f"1.5+1.2*sin({w*1.7:.4f}*frame+{ph:.3f})", f"1.1*cos({w*1.3:.4f}*frame+{ph*0.7:.3f})", f"{rnd.uniform(0.01, 0.03):.4f}*frame+{ph:.3f}"]
        # saat mendarat (z menempel) daun rebah: rotasi x/y dikurangi
        for k, ex in enumerate(rots):
            d = o.driver_add("rotation_euler", k).driver; d.type = 'SCRIPTED'; d.expression = ex
        for k in range(3):
            d = o.driver_add("scale", k).driver; d.type = 'SCRIPTED'
            d.expression = f"{sz:.2f}*min({ph_expr}/25,1)*min(({T:.1f}-{ph_expr})/25,1)"
    print("daun berguguran v2:", n)
