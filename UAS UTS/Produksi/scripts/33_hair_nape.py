# 33 - Perpanjang tepi bawah rambut bagian BELAKANG sampai garis tengkuk (sebelumnya berhenti membentuk V dan kulit kepala terlihat).
# extend_nape(nm, z_nape, y_sign): nm = "LASTRI"/"MHS"/...; y_sign = +1 bila belakang kepala ke arah +Y dunia.
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def extend_nape(nm, z_nape, y_sign=1.0, off=0.007, zmin_sel=None):
    H = bpy.data.objects[nm + "_HAIR"]; Hd = bpy.data.objects[nm + "_HEAD"]
    bpy.context.scene.frame_set(1)
    Mh = Hd.matrix_world.inverted() @ H.matrix_world
    bmh = bmesh.new(); bmh.from_mesh(Hd.data); bvh = BVHTree.FromBMesh(bmh)
    cy = (Hd.matrix_world @ Vector((0, 0, 0))).y
    cyw = sum((Hd.matrix_world @ v.co).y for v in Hd.data.vertices) / len(Hd.data.vertices)
    bm = bmesh.new(); bm.from_mesh(H.data); bm.edges.ensure_lookup_table()
    W = H.matrix_world
    def rear(v):
        w = W @ v.co; return (w.y - cyw) * y_sign > 0.004 and w.z > z_nape + 0.004
    edges = [e for e in bm.edges if e.is_boundary and rear(e.verts[0]) and rear(e.verts[1])]
    ret = bmesh.ops.extrude_edge_only(bm, edges=edges)
    nv = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)]
    Wi = W.inverted(); n = 0
    for v in nv:
        w = W @ v.co; w.z = z_nape
        hl = Mh @ (Wi @ w)                                   # ke koordinat lokal kepala
        loc, nrm, idx, dist = bvh.find_nearest(hl)
        if loc is None: continue
        hl2 = loc + nrm.normalized() * off
        v.co = Wi @ (Hd.matrix_world @ hl2); n += 1
    bm.to_mesh(H.data); bm.free(); bmh.free(); H.data.update()
    return {"edges": len(edges), "newverts": len(nv), "projected": n}
