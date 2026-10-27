# 17 - Dua gaya akhir: STYLE = "ghibli" (hangat, lukisan) atau "pocari" (cerah, biru jernih, bloom kuat, bersih)
import bpy, math
SC = bpy.context.scene
STYLE = globals().get("STYLE", "ghibli")

P = {
 "ghibli": dict(kuw=4, bloom=0.50, bloom_thr=0.9, bloom_size=0.6, lift=(1.00, 0.98, 1.04), gain=(1.07, 1.02, 0.94), sat=1.12, contrast=0.04, bright=0.05, vig=0.80, grain=0.0, exposure=0.25, disp=0.0),
 "pocari": dict(kuw=0, bloom=0.95, bloom_thr=0.75, bloom_size=0.75, lift=(0.97, 1.00, 1.06), gain=(0.98, 1.03, 1.10), sat=1.30, contrast=0.10, bright=0.10, vig=0.90, grain=0.0, exposure=0.55, disp=0.004),
}

def build(style):
    p = P[style]
    nm = "Grade_Warung"
    old = bpy.data.node_groups.get(nm)
    if old: bpy.data.node_groups.remove(old)
    tree = bpy.data.node_groups.new(nm, "CompositorNodeTree")
    tree.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    N = tree.nodes; Lk = tree.links.new
    def setin(n, name, val):
        try: n.inputs[name].default_value = val
        except Exception as e: print("skip", n.bl_idname, name, str(e)[:60])
    rl = N.new("CompositorNodeRLayers"); rl.location = (-1100, 0)
    last = rl.outputs["Image"]
    if p["kuw"] > 0:      # efek lukisan cat (Kuwahara)
        ku = N.new("CompositorNodeKuwahara"); ku.location = (-900, 0)
        try: ku.variation = 'ANISOTROPIC'
        except Exception as e: print("kuw variation", e)
        setin(ku, "Size", p["kuw"])
        Lk(last, ku.inputs["Image"]); last = ku.outputs[0]
    gl = N.new("CompositorNodeGlare"); gl.location = (-650, 0)
    for typ in ("Bloom", "BLOOM", 'Fog Glow', 'FOG_GLOW'):
        try: gl.inputs["Type"].default_value = typ; break
        except Exception: pass
    setin(gl, "Threshold", p["bloom_thr"]); setin(gl, "Strength", p["bloom"]); setin(gl, "Size", p["bloom_size"]); setin(gl, "Smoothness", 0.6)
    Lk(last, gl.inputs["Image"]); last = gl.outputs["Image"]
    cb = N.new("CompositorNodeColorBalance"); cb.location = (-400, 0)
    cb.inputs[4].default_value = (*p["lift"], 1.0); cb.inputs[6].default_value = (1.0, 1.0, 1.0, 1.0); cb.inputs[8].default_value = (*p["gain"], 1.0)
    Lk(last, cb.inputs["Image"]); last = cb.outputs[0]
    ex = N.new("CompositorNodeExposure"); ex.location = (-200, 0); setin(ex, "Exposure", p["exposure"]); Lk(last, ex.inputs["Image"]); last = ex.outputs[0]
    hs = N.new("CompositorNodeHueSat"); hs.location = (0, 0); setin(hs, "Saturation", p["sat"])
    Lk(last, hs.inputs["Image"]); last = hs.outputs[0]
    bc = N.new("CompositorNodeBrightContrast"); bc.location = (200, 0); setin(bc, "Brightness", p["bright"]); setin(bc, "Contrast", p["contrast"])
    Lk(last, bc.inputs["Image"]); last = bc.outputs[0]
    if p["disp"] > 0:
        ln = N.new("CompositorNodeLensdist"); ln.location = (400, 0); setin(ln, "Distortion", 0.0); setin(ln, "Dispersion", p["disp"])
        Lk(last, ln.inputs["Image"]); last = ln.outputs[0]
    em = N.new("CompositorNodeEllipseMask"); em.location = (200, -300); setin(em, "Position", (0.5, 0.5)); setin(em, "Size", (1.0, 1.0))
    bl = N.new("CompositorNodeBlur"); bl.location = (400, -300); setin(bl, "Size", (180.0, 180.0))
    ma = N.new("ShaderNodeMath"); ma.location = (620, -300); ma.operation = 'MULTIPLY_ADD'; ma.inputs[1].default_value = 1.0 - p["vig"]; ma.inputs[2].default_value = p["vig"]
    Lk(em.outputs["Mask"], bl.inputs["Image"]); Lk(bl.outputs[0], ma.inputs[0])
    mx = N.new("ShaderNodeMix"); mx.location = (620, 0); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1.0
    Lk(last, mx.inputs[6]); Lk(ma.outputs[0], mx.inputs[7])
    out = N.new("NodeGroupOutput"); out.location = (1250, 0)
    final = mx.outputs[2]
    if style == "ghibli":
        # tekstur kanvas/kertas lukisan halus (multiply 10%)
        try:
            im = N.new("CompositorNodeImage"); im.location = (700, -500)
            im.image = bpy.data.images.get("p_plaster_cream.png") or bpy.data.images.load(r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\assets\paint\p_plaster_cream.png")
            sc_ = N.new("CompositorNodeScale"); sc_.location = (900, -500)
            try: sc_.space = 'RENDER_SIZE'
            except Exception: pass
            try: sc_.frame_method = 'CROP'
            except Exception: pass
            Lk(im.outputs[0], sc_.inputs[0])
            mc = N.new("ShaderNodeMix"); mc.location = (1100, 0); mc.data_type = 'RGBA'; mc.blend_type = 'MULTIPLY'; mc.inputs[0].default_value = 0.10
            Lk(final, mc.inputs[6]); Lk(sc_.outputs[0], mc.inputs[7]); final = mc.outputs[2]
        except Exception as e: print("kanvas skip:", str(e)[:80])
    Lk(final, out.inputs[0])
    SC.compositing_node_group = tree
    # cahaya: eksposur adegan & key sedikit sesuai gaya
    SC.view_settings.view_transform = 'Standard'
    try: SC.view_settings.look = 'None'
    except Exception: pass
    print("gaya", style, "ok")

build(STYLE)
