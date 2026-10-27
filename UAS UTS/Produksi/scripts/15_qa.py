# 15 - QA otomatis sebelum render: tembus objek, tembus antar-karakter, kontak lantai, jangkauan IK, lompatan tulang, peregangan mesh
import bpy, math, json
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

OB = bpy.data.objects; SC = bpy.context.scene
DG = lambda: bpy.context.evaluated_depsgraph_get()

def world_mesh(o):
    ev = o.evaluated_get(DG()); me = ev.to_mesh()
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    M = np.array(o.matrix_world); P = co @ M[:3, :3].T + M[:3, 3]
    polys = [tuple(p.vertices) for p in me.polygons]
    ev.to_mesh_clear()
    return P, polys

STATIC_NAMES = ["Counter base", "Counter top", "Rear support", "Rear support.001", "PostFront_-1.5", "PostFront_1.5", "Wall base",
                "Ruko_Tengah_Atas", "Ground", "Lantai_Warung", "StoveTable", "StoveTop", "Shelf", "Crate", "GasTank", "Display tray", "Plinth", "Bench", "Pot"]
_static = {}
def build_static():
    _static.clear()
    for n in STATIC_NAMES:
        o = OB.get(n)
        if o is None: continue
        P, polys = world_mesh(o)
        if len(P) == 0: continue
        tris = []
        for p in polys:
            for i in range(1, len(p) - 1): tris.append((p[0], p[i], p[i + 1]))
        bvh = BVHTree.FromPolygons([tuple(v) for v in P], tris)
        _static[n] = (bvh, P.min(axis=0) - 0.02, P.max(axis=0) + 0.02)

def pen_vs_static(P, thr=0.012):
    """Mengembalikan {nama_static: (jumlah_titik, kedalaman_maks)} untuk titik P yang menembus solid statis lebih dari thr."""
    hits = {}
    for n, (bvh, lo, hi) in _static.items():
        idx = np.nonzero(np.all((P > lo) & (P < hi), axis=1))[0]
        cnt = 0; dmax = 0.0
        for i in idx:
            p = Vector(P[i])
            loc, nrm, fi, d = bvh.find_nearest(p)
            if loc is None: continue
            if (p - loc).dot(nrm) < 0 and d > thr:
                cnt += 1; dmax = max(dmax, d)
        if cnt: hits[n] = (cnt, round(dmax, 3))
    return hits

DEFORM = {
    "LASTRI": ["LASTRI_BODY", "LASTRI_HAND_L", "LASTRI_HAND_R", "LASTRI_blouse", "LASTRI_apron", "LASTRI_skirt", "LASTRI_HAIR"],
    "MHS": ["MHS_BODY", "MHS_HAND_L", "MHS_HAND_R", "MHS_jacket", "MHS_jeans", "MHS_backpack", "MHS_HAIR"],
}
FEET = {"LASTRI": ["LASTRI_sandal_L", "LASTRI_sandal_R"], "MHS": ["MHS_sole_L", "MHS_sole_R", "MHS_shoe_L", "MHS_shoe_R"]}

def check_frames(frames, thr=0.012):
    build_static()
    rep = {"penetrasi": [], "antar_karakter": [], "kaki": []}
    for f in frames:
        SC.frame_set(f); bpy.context.view_layer.update()
        allP = {}
        for ch, names in DEFORM.items():
            pts = []
            for n in names:
                o = OB.get(n)
                if o is None: continue
                P, polys = world_mesh(o)
                pts.append(P)
                if n.endswith(("_HAIR", "_backpack")) and False: continue
                h = pen_vs_static(P, thr)
                if h: rep["penetrasi"].append((f, n, h))
            allP[ch] = np.vstack(pts)
        # antar karakter: tumpang tindih segitiga mesh badan+pakaian L vs M (BVH overlap)
        try:
            def char_bvh(names):
                V = []; T = []; off = 0
                for n in names:
                    o = OB.get(n)
                    if o is None: continue
                    P, polys = world_mesh(o)
                    V += [tuple(v) for v in P]
                    for pl in polys:
                        for i in range(1, len(pl) - 1): T.append((pl[0] + off, pl[i] + off, pl[i + 1] + off))
                    off += len(P)
                return BVHTree.FromPolygons(V, T)
            bl = char_bvh(["LASTRI_BODY", "LASTRI_HAND_L", "LASTRI_HAND_R", "LASTRI_blouse", "LASTRI_apron", "LASTRI_skirt"])
            bm_ = char_bvh(["MHS_BODY", "MHS_HAND_L", "MHS_HAND_R", "MHS_jacket", "MHS_jeans", "MHS_backpack"])
            ov = bl.overlap(bm_)
            if ov: rep["antar_karakter"].append((f, len(ov)))
        except Exception as e:
            rep["antar_karakter"].append((f, "err", str(e)[:60]))
        for ch, names in FEET.items():
            zs = []
            for n in names:
                o = OB.get(n)
                if o is None: continue
                P, _ = world_mesh(o); zs.append(float(P[:, 2].min()))
            if zs:
                rep["kaki"].append((f, ch, round(min(zs), 4)))
    return rep

def check_bones(frames_all):
    """Lompatan posisi tulang antar frame (flip IK / teleport) & galat jangkauan IK."""
    out = {"lompat": [], "ik_galat": []}
    prev = {}
    for f in frames_all:
        SC.frame_set(f); bpy.context.view_layer.update()
        for nm in ("LASTRI", "MHS"):
            rig = OB["RIG_" + nm]
            pose = {}
            for b in ("hand.L", "hand.R", "foot.L", "foot.R", "head", "forearm.L", "forearm.R", "shin.L", "shin.R"):
                pose[b] = rig.matrix_world @ rig.pose.bones[b].head
            if nm in prev:
                for b, p in pose.items():
                    d = (p - prev[nm][b]).length
                    lim = 0.20 if not b.startswith(("forearm", "shin")) else 0.18
                    if d > lim: out["lompat"].append((f, nm, b, round(d, 3)))
            prev[nm] = pose
            for side in ("L", "R"):
                for ctrl, eff in (("hand_ik." + side, "hand." + side), ("foot_ik." + side, "foot." + side)):
                    pc = rig.matrix_world @ rig.pose.bones[ctrl].head
                    pe = rig.matrix_world @ rig.pose.bones[eff].head
                    e = (pc - pe).length
                    if e > 0.03: out["ik_galat"].append((f, nm, eff, round(e, 3)))
    return out

def foot_slide(nm, f0, f1):
    """Galat luncur: selama telapak 'menapak' (z kecil), pergeseran XY per frame (m)."""
    rig = OB["RIG_" + nm]
    last = None; worst = 0.0; wf = None
    for f in range(f0, f1 + 1):
        SC.frame_set(f); bpy.context.view_layer.update()
        for side in ("L", "R"):
            p = rig.matrix_world @ rig.pose.bones["foot." + side].tail
            if last and (side in last) and p.z < 0.03 and last[side].z < 0.03:
                d = Vector((p.x - last[side].x, p.y - last[side].y, 0)).length
                # kecepatan badan dikurangi: gunakan perbedaan terhadap gerak rig (root)
                rv = Vector((rig.location.x, rig.location.y, 0))
                if d > worst: worst = d; wf = f
            last = last or {}
            last[side] = p
    return worst, wf

def stretch_check(frames, names=("LASTRI_BODY", "MHS_BODY", "LASTRI_skirt", "LASTRI_blouse", "MHS_jacket", "MHS_jeans")):
    """Peregangan sisi mesh dibanding frame awal (deteksi 'candy wrapper'/ tembus)."""
    SC.frame_set(1); bpy.context.view_layer.update()
    base = {}
    for n in names:
        o = OB[n]; ev = o.evaluated_get(DG()); me = ev.to_mesh()
        edges = np.array([e.vertices[:] for e in me.edges])
        n_ = len(me.vertices); co = np.empty(n_ * 3, dtype=np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
        base[n] = (edges, np.linalg.norm(co[edges[:, 0]] - co[edges[:, 1]], axis=1)); ev.to_mesh_clear()
    res = []
    for f in frames:
        SC.frame_set(f); bpy.context.view_layer.update()
        for n in names:
            o = OB[n]; ev = o.evaluated_get(DG()); me = ev.to_mesh()
            n_ = len(me.vertices); co = np.empty(n_ * 3, dtype=np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
            edges, l0 = base[n]
            l1 = np.linalg.norm(co[edges[:, 0]] - co[edges[:, 1]], axis=1)
            ratio = (l1 + 1e-6) / (l0 + 1e-6)
            r = float(ratio.max()); ev.to_mesh_clear()
            if r > 1.8: res.append((f, n, round(r, 2)))
    return res

print("qa lib ok")
