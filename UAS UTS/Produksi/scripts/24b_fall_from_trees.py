# 24b - Daun gugur realistis: daun LEPAS dari tajuk pohon (muncul di ranting), jatuh berayun tertiup angin, mendarat rebah, lalu memudar.
# Tekstur: assets/paint/leaf_a|b|c.png (24a_leaf_tex.py). Gerak lewat driver ekspresi sederhana (deterministik, tanpa simulasi).
import bpy, math, random, bmesh
from mathutils import Vector
OB = bpy.data.objects; SC = bpy.context.scene
P = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\assets\paint" + "\\"
TREES = [(-4.2, 2.4, 7.0), (4.6, 2.8, 7.5), (-8.0, 1.6, 8.0), (8.6, 1.8, 7.8)]    # (x, y, tinggi tajuk) = posisi pohon di 23_plants.py

def leaf_mats():
    mats = []
    for nm in ("leaf_a", "leaf_b", "leaf_c"):
        m = bpy.data.materials.get("M_" + nm) or bpy.data.materials.new("M_" + nm); m.use_nodes = True; nt = m.node_tree
        for x in list(nt.nodes): nt.nodes.remove(x)
        out = nt.nodes.new("ShaderNodeOutputMaterial"); tx = nt.nodes.new("ShaderNodeTexImage")
        im = bpy.data.images.get(nm + ".png")
        if im: im.filepath = P + nm + ".png"; im.reload()
        tx.image = im or bpy.data.images.load(P + nm + ".png")
        df = nt.nodes.new("ShaderNodeBsdfDiffuse"); tr = nt.nodes.new("ShaderNodeBsdfTranslucent"); mx = nt.nodes.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.35
        tp = nt.nodes.new("ShaderNodeBsdfTransparent"); ma = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(tx.outputs["Color"], df.inputs["Color"]); nt.links.new(tx.outputs["Color"], tr.inputs["Color"])
        nt.links.new(df.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
        nt.links.new(tx.outputs["Alpha"], ma.inputs[0]); nt.links.new(tp.outputs[0], ma.inputs[1]); nt.links.new(mx.outputs[0], ma.inputs[2]); nt.links.new(ma.outputs[0], out.inputs["Surface"])
        try: m.surface_render_method = 'DITHERED'
        except Exception: pass
        mats.append(m)
    return mats

def litter(n_per_tree=30, seed=21):
    """Daun yang sudah gugur tergeletak di tanah sekitar pohon & trotoar (statis, rebah, berbagai warna)."""
    rnd = random.Random(seed)
    for o in [o for o in OB if o.name.startswith("LITTER_")]: bpy.data.objects.remove(o)
    mats = leaf_mats(); base = bpy.data.meshes.get("FALL_LEAF")
    coll = bpy.data.collections.get("13_EXTRAS") or SC.collection
    for ti, (tx_, ty_, th) in enumerate(TREES):
        for i in range(n_per_tree):
            o = bpy.data.objects.new(f"LITTER_{ti}_{i}", base.copy()); o.data.materials.clear(); o.data.materials.append(mats[rnd.randrange(3)]); coll.objects.link(o)
            ang = rnd.uniform(0, 6.28); r = abs(rnd.gauss(0, 2.6))
            o.location = (tx_ + math.cos(ang) * r, ty_ - 0.6 + math.sin(ang) * r * 0.9, 0.012 + rnd.random() * 0.004)
            o.rotation_euler = (math.radians(rnd.uniform(-8, 8)), math.radians(rnd.uniform(-8, 8)), rnd.uniform(0, 6.28))
            s = rnd.uniform(0.8, 1.3); o.scale = (s, s, s)
    print("daun di tanah:", n_per_tree * len(TREES))

def canopy_points(n_total_per_tree, rnd):
    """Titik asal daun: verteks daun sungguhan pada tajuk tiap pohon (koordinat dunia, ikut skala/rotasi pohon)."""
    import numpy as np
    tpl = OB["island_tree_02_LOD0"]; me = tpl.data; nv = len(me.vertices)
    co = np.empty(nv * 3, dtype=np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    cand = np.where(co[:, 2] > 1.4)[0]               # bagian tajuk (di atas batang)
    res = []
    for root in [o for o in OB if o.name.startswith("PL_T") and o.type == 'EMPTY']:
        idx = cand[np.random.RandomState(rnd.randrange(10**6)).choice(len(cand), n_total_per_tree, replace=False)]
        M = root.matrix_world
        pts = [M @ Vector(co[i]) for i in idx]
        res.append((root.name, pts, root.scale.x))
    return res

def fall_leaves_v3(per_tree=48, seed=5):
    rnd = random.Random(seed)
    for o in [o for o in OB if o.name.startswith(("FALL_EMIT", "FALL_L_", "WIND_FIELD", "FALL_LEAF_TEMPLATE"))]: bpy.data.objects.remove(o)
    mats = leaf_mats()
    me = bpy.data.meshes.get("FALL_LEAF")
    if me is None:
        me = bpy.data.meshes.new("FALL_LEAF"); bm = bmesh.new()
        v = [bm.verts.new((-0.045, -0.0675, 0)), bm.verts.new((0.045, -0.0675, 0)), bm.verts.new((0.045, 0.0675, 0.006)), bm.verts.new((-0.045, 0.0675, 0.006))]
        f = bm.faces.new(v); uv = bm.loops.layers.uv.new("UVMap")
        for l, uvv in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): l[uv].uv = uvv
        bm.to_mesh(me); bm.free()
    coll = bpy.data.collections.get("13_EXTRAS") or SC.collection
    for ti, (rname, pts, sc_) in enumerate(canopy_points(per_tree, rnd)):
        for i, p in enumerate(pts):
            o = bpy.data.objects.new(f"FALL_L_{ti}_{i}", me.copy()); o.data.materials.clear(); o.data.materials.append(mats[rnd.randrange(3)]); coll.objects.link(o)
            x0, y0, zt = p.x, p.y, max(p.z, 0.6)
            T = rnd.uniform(560, 900); off = rnd.uniform(0, T); ph = rnd.uniform(0, 6.28)
            fall = min(T * 0.7, zt / 0.0085)          # kecepatan jatuh ~0.25 m/dtk, lebih lama dari ketinggian besar
            vz = (zt - 0.02) / fall; A = rnd.uniform(0.2, 0.55) * min(1.0, zt / 2.0); w = rnd.uniform(0.035, 0.07)
            pe = f"fmod(frame+{off:.1f},{T:.1f})"
            tf = f"min({pe},{fall:.1f})"
            sx = f"{x0:.3f}+{A:.3f}*sin({w:.4f}*{tf}+{ph:.3f})*min({tf}/40,1)+0.0045*{tf}"
            sy = f"{y0:.3f}+{A*0.6:.3f}*cos({w*0.8:.4f}*{tf}+{ph:.3f})*min({tf}/40,1)-0.0015*{tf}"
            fz = f"max({zt:.3f}-{vz:.5f}*{tf},0.02)"
            for k, ex in enumerate((sx, sy, fz)):
                d = o.driver_add("location", k).driver; d.type = 'SCRIPTED'; d.expression = ex
            land = f"min(max(({fall:.1f}-{pe})/18,0),1)"
            rots = [f"1.57*(1-{land})+{land}*1.3*sin({w*1.7:.4f}*{tf}+{ph:.3f})", f"{land}*1.0*cos({w*1.3:.4f}*{tf}+{ph*0.7:.3f})", f"{rnd.uniform(0.012, 0.03):.4f}*{tf}+{ph:.3f}"]
            for k, ex in enumerate(rots):
                d = o.driver_add("rotation_euler", k).driver; d.type = 'SCRIPTED'; d.expression = ex
            sz = rnd.uniform(0.45, 0.80)
            for k in range(3):
                d = o.driver_add("scale", k).driver; d.type = 'SCRIPTED'
                d.expression = f"{sz:.2f}*min({pe}/6,1)*min(({T:.1f}-{pe})/40,1)"
    print("daun gugur dari tajuk:", per_tree * len([o for o in OB if o.name.startswith('PL_T') and o.type == 'EMPTY']))

fall_leaves_v3(); litter()
