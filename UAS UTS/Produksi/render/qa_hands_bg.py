# QA tangan di Blender latar: titik jari/telapak yang menembus (a) pakaian/badan karakter LAIN, (b) pakaian karakter sendiri (bukan lengan baju sisi sama dekat pergelangan),
# (c) properti statis. Hanya titik mesh tangan di bawah pergelangan. Keluaran: render/qa_hands.json  (kedalaman > 1.5 cm dihitung)
import bpy, json, math, time, sys
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB = bpy.data.objects; SC = bpy.context.scene
STEP = int(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv else 4
THR = 0.015
def wmesh(o):
    sm = [m for m in o.modifiers if m.type == "SOLIDIFY"]; st = [m.show_viewport for m in sm]      # tanpa kulit outline (normal terbalik) agar uji "di dalam" benar
    for m in sm: m.show_viewport = False
    ev = o.evaluated_get(bpy.context.evaluated_depsgraph_get()); me = ev.to_mesh()
    n = len(me.vertices); co = np.empty(n * 3, dtype=np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    M = np.array(o.matrix_world); P = co @ M[:3, :3].T + M[:3, 3]
    polys = [tuple(p.vertices) for p in me.polygons]; ev.to_mesh_clear()
    for m, v in zip(sm, st): m.show_viewport = v
    return P, polys
def bvh_of(names):
    V = []; T = []; off = 0
    for n in names:
        o = OB.get(n)
        if o is None: continue
        P, polys = wmesh(o); V += [tuple(v) for v in P]
        for p in polys:
            for i in range(1, len(p) - 1): T.append((p[0] + off, p[i] + off, p[i + 1] + off))
        off += len(P)
    return BVHTree.FromPolygons(V, T) if T else None
OWN = {"LASTRI": ["LASTRI_blouse", "LASTRI_apron", "LASTRI_skirt"], "MHS": ["MHS_jacket", "MHS_jeans", "MHS_backpack"]}
OTHER = {"LASTRI": ["MHS_BODY", "MHS_HAND_L", "MHS_HAND_R", "MHS_jacket", "MHS_jeans", "MHS_backpack"], "MHS": ["LASTRI_BODY", "LASTRI_HAND_L", "LASTRI_HAND_R", "LASTRI_blouse", "LASTRI_apron", "LASTRI_skirt"]}
STATIC = ["Counter base", "Counter top", "Display tray", "Jar", "JarLid", "Thermos", "Shelf", "Lantai_Warung", "Cup1", "Cup2", "StoveTable", "StoveTop", "Crate", "Plinth"]
def inside(bvh, P, thr=THR):
    cnt = 0; dmax = 0.0
    for p in P:
        loc, nrm, fi, d = bvh.find_nearest(Vector(p), 0.06)
        if loc is not None and (Vector(p) - loc).dot(nrm) < 0 and d > thr: cnt += 1; dmax = max(dmax, d)
    return cnt, round(dmax, 3)
res = []; t0 = time.time()
static = bvh_of(STATIC)
for f in range(1, 2701, STEP):
    SC.frame_set(f)
    for ch in ("LASTRI", "MHS"):
        own = bvh_of(OWN[ch]); oth = bvh_of(OTHER[ch])
        for s in ("L", "R"):
            h = OB.get(f"{ch}_HAND_{s}")
            if h is None: continue
            P, _ = wmesh(h); wr = np.array(OB["RIG_" + ch].matrix_world @ OB["RIG_" + ch].pose.bones["hand." + s].head)
            dist_w = np.linalg.norm(P - wr, axis=1); tip = P[dist_w > 0.035]; tip_own = P[dist_w > 0.060]      # buang area pergelangan (lengan baju menutup pangkal tangan)
            for tag, bv in (("pakaian_sendiri", own), ("karakter_lain", oth), ("statis", static)):
                if bv is None: continue
                c, d = inside(bv, tip_own if tag == "pakaian_sendiri" else tip)
                if c: res.append((f, f"{ch}_{s}", tag, c, d))
json.dump({"t": round(time.time() - t0), "hits": res, "n": len(res)}, open(r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\render\qa_hands.json", "w"))
print("QA_HANDS_DONE", len(res), round(time.time() - t0))

