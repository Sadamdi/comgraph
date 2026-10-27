# 32 - Tulang puntir (twist) lengan bawah: roll tangan didistribusikan sepanjang lengan bawah, bukan memuntir di satu titik (efek "bungkus permen").
# add_twist(rig) menambah forearm_tw1/2.s (Copy Rotation sumbu Y dari hand.s) dan menulis ulang bobot kulit lengan bawah.
import bpy, bmesh, math
from mathutils import Vector
CTRL = (("forearm", 0.0), ("forearm_tw1", 0.45), ("forearm_tw2", 0.72), ("hand", 1.0))

def ramp(t, S):
    """bobot piecewise-linear antar titik kontrol sepanjang lengan bawah (t=0 siku, t=1 pergelangan)"""
    if t >= 1.0: return {"hand" + S: 1.0}
    if t <= 0.0: return {"forearm" + S: 1.0}
    for (n0, t0), (n1, t1) in zip(CTRL, CTRL[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0); u = u * u * (3 - 2 * u)
            return {n0 + S: 1 - u, n1 + S: u}

def add_twist(R):
    bpy.context.view_layer.objects.active = R
    for o in bpy.context.selected_objects: o.select_set(False)
    R.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); eb = R.data.edit_bones
    for s in ("L", "R"):
        S = "." + s; fa = eb["forearm" + S]
        for nm, a, b in (("forearm_tw1", 0.38, 0.62), ("forearm_tw2", 0.62, 0.86)):
            if nm + S in eb: continue
            e = eb.new(nm + S); e.head = fa.head.lerp(fa.tail, a); e.tail = fa.head.lerp(fa.tail, b); e.roll = fa.roll
            e.parent = fa; e.use_connect = False; e.use_deform = True
    bpy.ops.object.mode_set(mode='POSE')
    for s in ("L", "R"):
        S = "." + s
        for nm, inf in (("forearm_tw1", 0.34), ("forearm_tw2", 0.68)):
            pb = R.pose.bones[nm + S]
            for c in list(pb.constraints): pb.constraints.remove(c)
            c = pb.constraints.new('COPY_ROTATION'); c.target = R; c.subtarget = "hand" + S
            c.use_x = False; c.use_y = True; c.use_z = False; c.euler_order = 'YXZ'
            c.owner_space = 'LOCAL'; c.target_space = 'LOCAL'; c.influence = inf
    bpy.ops.object.mode_set(mode='OBJECT')

def reweight_forearm(R, B):
    A = R.data; toloc = (B.matrix_parent_inverse @ B.matrix_basis).inverted()
    n = 0
    for s in ("L", "R"):
        S = "." + s
        for nm in ("forearm_tw1", "forearm_tw2"):
            if nm + S not in B.vertex_groups: B.vertex_groups.new(name=nm + S)
        a = toloc @ A.bones["forearm" + S].head_local; b = toloc @ A.bones["hand" + S].head_local; ab = b - a
        gF, gH = B.vertex_groups["forearm" + S].index, B.vertex_groups["hand" + S].index
        for v in B.data.vertices:
            w = {g.group: g.weight for g in v.groups}; W = w.get(gF, 0.0) + w.get(gH, 0.0)
            if W < 0.05: continue
            t = (v.co - a).dot(ab) / ab.length_squared
            if not (-0.2 < t < 1.6): continue
            for g in (gF, gH): B.vertex_groups[g].remove([v.index]) if g in w else None
            for nm, ww in ramp(t, S).items(): B.vertex_groups[nm].add([v.index], ww * W, 'REPLACE'); n += 1
    return n

def twist_weights_for_hand(R, B, m, s):
    """verts mesh tangan di atas pergelangan memakai ramp yang sama dengan kulit lengan"""
    A = R.data; S = "." + s; toloc = (B.matrix_parent_inverse @ B.matrix_basis).inverted()
    a = toloc @ A.bones["forearm" + S].head_local; b = toloc @ A.bones["hand" + S].head_local; ab = b - a
    for nm in ("forearm_tw1", "forearm_tw2"):
        if nm + S not in m.vertex_groups: m.vertex_groups.new(name=nm + S)
    k = 0
    for v in m.data.vertices:
        t = (v.co - a).dot(ab) / ab.length_squared
        if t < 1.0:
            for g in list(v.groups): m.vertex_groups[g.group].remove([v.index]) if m.vertex_groups[g.group].name.startswith(("hand", "forearm")) else None
            for nm, ww in ramp(t, S).items(): m.vertex_groups[nm].add([v.index], ww, 'REPLACE'); k += 1
    return k
