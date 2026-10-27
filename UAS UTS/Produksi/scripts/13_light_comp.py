# 13 - Pencahayaan 3-point (key/fill/rim) + matahari & langit berubah di S08, lalu graf compositor (glow, grading, vignette, lens)
import bpy, math
from mathutils import Vector

OB = bpy.data.objects; SC = bpy.context.scene
rad = math.radians

def sun_rot(az, el):
    a, e = rad(az), rad(el)
    d = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))
    return d.to_track_quat('Z', 'Y').to_euler()

def tgt(name, pos):
    o = OB.get(name)
    if o is None:
        o = bpy.data.objects.new(name, None); o.empty_display_type = 'PLAIN_AXES'
        (bpy.data.collections.get("12_LIGHTS") or SC.collection).objects.link(o)
    o.location = Vector(pos); return o

def aim(light, target):
    for c in list(light.constraints): light.constraints.remove(c)
    c = light.constraints.new('TRACK_TO'); c.target = target; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'

def setup_lights():
    old = OB.get("Light")
    if old: old.hide_render = True; old.hide_viewport = True
    cl = bpy.data.collections.get("12_LIGHTS")
    # --- 3-point lighting ---
    key = OB.get("PLAN_Key") or OB["3PT_Key"]; fill = OB.get("PLAN_Fill") or OB["3PT_Fill"]; rim = OB.get("PLAN_Rim") or OB["3PT_Rim"]
    for o, nm in ((key, "3PT_Key"), (fill, "3PT_Fill"), (rim, "3PT_Rim")):
        if o.name != nm: o.name = nm
        o.hide_render = False; o.hide_viewport = False
    key.location = (-2.3, -2.8, 2.9); key.data.size = 2.2; key.data.energy = 180; key.data.color = (1.0, 0.93, 0.82)
    fill.location = (2.8, -2.4, 2.1); fill.data.size = 3.2; fill.data.energy = 60; fill.data.color = (0.82, 0.90, 1.0)
    rim.location = (0.4, 1.70, 2.35); rim.data.size = 1.3; rim.data.energy = 110; rim.data.color = (1.0, 0.95, 0.88)
    t = tgt("LT_target", (0.0, 0.1, 1.40)); t2 = tgt("LT_target_rim", (0.0, -0.3, 1.40))
    aim(key, t); aim(fill, t); aim(rim, t2)
    for o in (key, fill, rim):
        o.data.shadow_soft_size = 0.3
    # --- matahari: pagi (S01-S07) -> sore keemasan (S08-S14) ---
    sun = OB["SUN_Key"]
    if sun.animation_data: sun.animation_data_clear()
    if sun.data.animation_data: sun.data.animation_data_clear()
    def key_sun(f, az, el, col, en):
        sun.rotation_euler = sun_rot(az, el); sun.data.color = col; sun.data.energy = en
        sun.keyframe_insert("rotation_euler", frame=f); sun.data.keyframe_insert("color", frame=f); sun.data.keyframe_insert("energy", frame=f)
    key_sun(1, -125, 40, (1.0, 0.95, 0.85), 3.2)
    key_sun(1320, -125, 40, (1.0, 0.95, 0.85), 3.2)
    key_sun(1321, -62, 20, (1.0, 0.70, 0.42), 3.8)
    for fcs in (sun.animation_data.action, sun.data.animation_data.action):
        for layer in fcs.layers:
            for st in layer.strips:
                for cb in st.channelbags:
                    for fc in cb.fcurves:
                        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
    # langit: elevasi matahari pada tekstur langit ikut berubah
    w = SC.world
    sky = next((n for n in w.node_tree.nodes if n.type == 'TEX_SKY'), None)
    if sky is not None:
        try:
            if w.node_tree.animation_data: w.node_tree.animation_data_clear()
            sky.sun_elevation = rad(40); sky.keyframe_insert("sun_elevation", frame=1); sky.keyframe_insert("sun_elevation", frame=1320)
            sky.sun_elevation = rad(18); sky.keyframe_insert("sun_elevation", frame=1321)
        except Exception as e:
            print("sky key skip:", str(e)[:80])
    print("lampu ok")

def setup_comp():
    nm = "Grade_Warung"
    old = bpy.data.node_groups.get(nm)
    if old: bpy.data.node_groups.remove(old)
    tree = bpy.data.node_groups.new(nm, "CompositorNodeTree")
    tree.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    N = tree.nodes; Lk = tree.links.new
    rl = N.new("CompositorNodeRLayers"); rl.location = (-900, 0)
    gl = N.new("CompositorNodeGlare"); gl.location = (-650, 0)
    def setin(n, name, val):
        try: n.inputs[name].default_value = val
        except Exception as e: print("skip", n.bl_idname, name, str(e)[:70])
    for typ in ("Bloom", "BLOOM", 'Fog Glow', 'FOG_GLOW'):
        try: gl.inputs["Type"].default_value = typ; break
        except Exception: pass
    setin(gl, "Threshold", 0.85); setin(gl, "Strength", 0.55); setin(gl, "Size", 0.55); setin(gl, "Smoothness", 0.5)
    cb = N.new("CompositorNodeColorBalance"); cb.location = (-400, 0)
    cb.inputs[4].default_value = (0.95, 1.00, 1.03, 1.0); cb.inputs[6].default_value = (1.0, 1.0, 1.0, 1.0); cb.inputs[8].default_value = (1.06, 1.01, 0.95, 1.0)
    hs = N.new("CompositorNodeHueSat"); hs.location = (-150, 0)
    setin(hs, "Saturation", 1.10); setin(hs, "Value", 1.0)
    bc = N.new("CompositorNodeBrightContrast"); bc.location = (100, 0)
    setin(bc, "Brightness", 0.0); setin(bc, "Contrast", 0.10)
    ln = N.new("CompositorNodeLensdist"); ln.location = (350, 0)
    setin(ln, "Distortion", 0.004); setin(ln, "Dispersion", 0.0035)
    # vignette: mask elips -> blur -> pengali
    em = N.new("CompositorNodeEllipseMask"); em.location = (100, -300)
    setin(em, "Position", (0.5, 0.5)); setin(em, "Size", (0.95, 0.95))
    bl = N.new("CompositorNodeBlur"); bl.location = (350, -300); setin(bl, "Size", (150.0, 150.0))
    mx = N.new("ShaderNodeMix"); mx.location = (620, 0); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1.0
    ma = N.new("ShaderNodeMath"); ma.location = (620, -300); ma.operation = 'MULTIPLY_ADD'
    ma.inputs[1].default_value = 0.28; ma.inputs[2].default_value = 0.72       # vig = 0.72 + 0.28*mask
    out = N.new("NodeGroupOutput"); out.location = (900, 0)
    Lk(rl.outputs["Image"], gl.inputs["Image"]); Lk(gl.outputs["Image"], cb.inputs["Image"])
    Lk(cb.outputs[0], hs.inputs["Image"]); Lk(hs.outputs[0], bc.inputs["Image"]); Lk(bc.outputs[0], ln.inputs["Image"])
    Lk(em.outputs["Mask"], bl.inputs["Image"]); Lk(bl.outputs[0], ma.inputs[0])
    # color2 <- nilai vignette sebagai abu-abu
    Lk(ln.outputs[0], mx.inputs[6]); Lk(ma.outputs[0], mx.inputs[7])
    Lk(mx.outputs[2], out.inputs[0])
    SC.compositing_node_group = tree
    print("compositor ok; glare outs", [o.name for o in gl.outputs], "| mix out", [o.name for o in mx.outputs])

setup_lights()
try:
    setup_comp()
except Exception as e:
    import traceback; traceback.print_exc(); print("comp gagal:", e)
