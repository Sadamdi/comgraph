# 34 - Tali celemek baru: pita mulus yang menempel di permukaan blus (tidak lagi patah/tembus), bobot disalin dari kulit tubuh terdekat.
import bpy, bmesh, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

def _catmull(pts, n):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n; t2 = t * t; t3 = t2 * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1]); return out

def rebuild_strap(nm, strap_name, ctr0=None, cross_back=True, width=0.022, off=0.0065, n=5, cloth=None, ray=False):
    S = bpy.data.objects[strap_name]; Bl = bpy.data.objects[cloth or (nm + "_blouse")]; Bd = bpy.data.objects[nm + "_BODY"]
    bpy.context.scene.frame_set(1)
    Ws = S.matrix_world; Wsi = Ws.inverted()
    me = S.data; vs = [Ws @ v.co for v in me.vertices]
    ctr = list(ctr0) if ctr0 else [(vs[2 * i] + vs[2 * i + 1]) / 2 for i in range(len(vs) // 2)]
    if cross_back:                                   # lanjut menyilang di punggung ke sisi seberang (tali X)
        base = ctr[-1]; cx = base.x; sg = 1.0 if ctr[0].x > cx else -1.0
        for dx, dy, dz in ((0.0, 0.050, -0.040), (-0.045 * sg, 0.062, -0.095), (-0.075 * sg, 0.068, -0.150)):
            ctr.append(Vector((cx + dx, base.y + dy, base.z + dz)))
    smooth = _catmull(ctr, n)
    bmb = bmesh.new(); bmb.from_mesh(Bl.data); bmb.transform(Bl.matrix_world); bvh = BVHTree.FromBMesh(bmb)
    # permukaan blus + tubuh sebagai penutup: titik terdekat + normal keluar
    pos = []; nor = []
    if ray:                                          # tembak sinar dari luar ke arah sumbu badan -> selalu kena permukaan terluar kain
        Bw = Bd.data.vertices; ax = sum(((Bd.matrix_world @ v.co) for v in Bw if 1.0 < (Bd.matrix_world @ v.co).z < 1.3), Vector()); 
        cnt = sum(1 for v in Bw if 1.0 < (Bd.matrix_world @ v.co).z < 1.3); ax = ax / max(cnt, 1)
        ztop = max(p.z for p in smooth)
        fh = Vector((ctr[2].x - ctr[0].x, ctr[2].y - ctr[0].y, 0)).normalized()      # arah depan badan (horizontal): dari titik belakang ke titik depan jalur
        for p in smooth:
            dd = (p.x - ax.x) * fh.x + (p.y - ax.y) * fh.y
            if p.z > ztop - 0.03: org, dr = p + Vector((0, 0, 0.30)), Vector((0, 0, -1))
            elif dd > 0.03: org, dr = p + fh * 0.30, -fh
            elif dd < -0.03: org, dr = p - fh * 0.30, fh
            else: org, dr = p + Vector((0, 0, 0.30)), Vector((0, 0, -1))
            hit = bvh.ray_cast(org, dr, 0.8)
            if hit[0] is None: hit = bvh.find_nearest(p)
            loc, nrm = hit[0], hit[1]
            if nrm.dot(-dr) < 0: nrm = -nrm
            pos.append(loc + nrm.normalized() * off); nor.append(nrm.normalized())
        for _ in range(3):                           # haluskan derau
            pos = [pos[0]] + [(pos[i - 1] + pos[i] * 2 + pos[i + 1]) / 4 for i in range(1, len(pos) - 1)] + [pos[-1]]
    else:
        for p in smooth:
            loc, nrm, idx, dist = bvh.find_nearest(p)
            if loc is None: loc, nrm = p, Vector((0, 0, 1))
            pos.append(loc + nrm.normalized() * off); nor.append(nrm.normalized())
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap"); L = []
    for i, p in enumerate(pos):
        t = (pos[min(i + 1, len(pos) - 1)] - pos[max(i - 1, 0)]).normalized()
        b = t.cross(nor[i]).normalized() * width / 2
        L.append((bm.verts.new(Wsi @ (p - b)), bm.verts.new(Wsi @ (p + b))))
    for i in range(len(L) - 1):
        f = bm.faces.new((L[i][0], L[i][1], L[i + 1][1], L[i + 1][0])); f.smooth = True
        for lp, (u, v) in zip(f.loops, ((0, i / (len(L) - 1)), (1, i / (len(L) - 1)), (1, (i + 1) / (len(L) - 1)), (0, (i + 1) / (len(L) - 1)))): lp[uv].uv = (u, v)
    bm.to_mesh(me); bm.free(); bmb.free(); me.update()
    # bobot dari verteks tubuh terdekat
    kd = KDTree(len(Bd.data.vertices))
    for v in Bd.data.vertices: kd.insert(Bd.matrix_world @ v.co, v.index)
    kd.balance()
    for g in list(S.vertex_groups): S.vertex_groups.remove(g)
    for g in Bd.vertex_groups:
        if g.name != "OUTLINE_T": S.vertex_groups.new(name=g.name)
    for v in me.vertices:
        co, idx, d = kd.find(Ws @ v.co)
        for g in Bd.data.vertices[idx].groups:
            nmg = Bd.vertex_groups[g.group].name
            if nmg in S.vertex_groups: S.vertex_groups[nmg].add([v.index], g.weight, 'REPLACE')
    return {"verts": len(me.vertices)}
