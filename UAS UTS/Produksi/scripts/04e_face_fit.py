# 04e - Tempelkan fitur wajah (mulut, pipi, hidung) tepat di permukaan kulit tengkorak (BVH, pose istirahat)
# Alasan: dagu meruncing -> fitur yang diletakkan dengan angka tetap melayang ~1 cm di depan kulit (terlihat dari samping).
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def _surface(nm):
    sk = bpy.data.objects[nm + "_HEAD"]
    sd = [m for m in sk.modifiers if m.type == 'SOLIDIFY']
    for m in sd: m.show_viewport = False
    dg = bpy.context.evaluated_depsgraph_get(); dg.update()
    ev = sk.evaluated_get(dg); me = ev.to_mesh()
    bvh = BVHTree.FromPolygons([v.co.copy() for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
    ev.to_mesh_clear()
    for m in sd: m.show_viewport = True
    def ys(x, z):
        h = bvh.ray_cast(Vector((x, -0.3, z)), Vector((0, 1, 0)))
        return None if h[0] is None else h[0].y
    return sk, ys

def fit_faces():
    sc = bpy.context.scene; sc.frame_set(1); bpy.context.view_layer.update()
    for nm in ("LASTRI", "MHS"):
        sk, ys = _surface(nm)
        W = sk.matrix_world; Wi = W.inverted()
        def snap(o, off):
            l = Wi @ o.matrix_world.translation
            y = ys(l.x, l.z)
            if y is None: return
            l.y = y + off
            m = o.matrix_world.copy(); m.translation = W @ l; o.matrix_world = m
        snap(bpy.data.objects[nm + "_mouth"], -0.0010)
        for s in "LR": snap(bpy.data.objects[f"{nm}_blush_{s}"], -0.0004)
        # garis hidung: titik kurva dipasang ke permukaan
        nz = bpy.data.objects.get(nm + "_nose")
        if nz:
            for bp in nz.data.splines[0].bezier_points:
                y = ys(bp.co.x, bp.co.z)
                if y is not None:
                    bp.co.y = y - 0.0006; bp.handle_left.y = bp.handle_right.y = bp.co.y
    bpy.context.view_layer.update()
    print("wajah dipasang ke permukaan")

fit_faces()
