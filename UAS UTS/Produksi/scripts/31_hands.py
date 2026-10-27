# 31 - Tangan baru berbentuk anatomi (metaball kapsul -> mesh utuh) menggantikan tangan lama yang retak/menyatu.
# Dipanggil: rebuild_hands(rig_name)  -> mengganti tangan L & R pada BODY milik rig tsb. Jari bulat (kapsul), telapak pipih (elipsoid), jempol + thenar.
import bpy, bmesh, math
from mathutils import Vector, Quaternion, Matrix
K = 0.56                                     # radius permukaan = K * radius metaball (stiffness 2, threshold 0.6; terukur)
FING = ("index", "middle", "ring", "pinky")
FR = {"index": 0.0069, "middle": 0.0073, "ring": 0.0067, "pinky": 0.0057}     # radius permukaan jari (m) pada skala karakter 1.0
TAPER = (1.0, 0.94, 0.84)

def _body_of(R):
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.name.endswith("_BODY") and any(m.type == 'ARMATURE' and m.object == R for m in o.modifiers): return o

def _seg_dist(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9))); return (p - (a + ab * t)).length

def build_hand(R, B, s):
    A = R.data; S = "." + s
    toloc = (B.matrix_parent_inverse @ B.matrix_basis).inverted()
    def hd(n): return toloc @ A.bones[n].head_local
    def tl(n): return toloc @ A.bones[n].tail_local
    mb = bpy.data.metaballs.new("_hand"); mb.resolution = 0.0018; mb.render_resolution = 0.0018; mb.threshold = 0.6
    ob = bpy.data.objects.new("_hand", mb); bpy.context.scene.collection.objects.link(ob)
    def caps(a, b, Rs):
        e = mb.elements.new(type='CAPSULE'); e.radius = Rs / K; e.stiffness = 2.0
        d = b - a; e.size_x = d.length / 2; e.co = (a + b) / 2
        e.rotation = Vector((1, 0, 0)).rotation_difference(d.normalized())
    def ell(c, sx, sy, sz, rot=None):
        e = mb.elements.new(type='ELLIPSOID'); e.radius = 1.0; e.stiffness = 2.0; e.co = c
        e.size_x, e.size_y, e.size_z = sx / K, sy / K, sz / K
        if rot: e.rotation = rot
    wr = hd("hand" + S); up = (toloc @ A.bones["forearm" + S].head_local)
    k_in = {f: hd(f + "1" + S) for f in FING}
    ymid = sum(v.y for v in k_in.values()) / 4; ys = [v.y for v in k_in.values()]; spread = max(ys) - min(ys)
    kn = sum((v for v in k_in.values()), Vector()) / 4
    scale = R.scale.x if R.scale.x else 1.0
    # telapak: elipsoid pipih (X = tebal, Y = lebar, Z = panjang), pergelangan sedikit lebih sempit
    c_palm = (wr + kn) / 2 + Vector((0.0, 0.0, -0.002)); lp = (wr - kn).length / 2
    ell(c_palm, 0.0125, spread / 2 + 0.0095, lp + 0.004)
    ell(wr * 0.5 + kn * 0.5 + Vector((0, 0.0, 0.012)), 0.0115, spread / 2 + 0.006, lp * 0.7)
    cw = wr + Vector((0, 0, 0.012)); ell(cw, 0.0115, 0.0185, 0.022)                # pergelangan
    # jari: 3 kapsul per jari
    for f in FING:
        for i in (1, 2, 3):
            n = f + str(i) + S; caps(hd(n), tl(n), FR[f] * TAPER[i - 1])
    # jempol + thenar (gundukan pangkal jempol)
    t1, t2, t3 = hd("thumb1" + S), hd("thumb2" + S), hd("thumb3" + S)
    ell((t1 + t2) / 2 + Vector((0, 0, -0.002)), 0.0105, 0.0125, 0.021, Vector((0, 0, 1)).rotation_difference(Vector((0, 0, 1))))
    for i, (a, b, r) in enumerate(((t1, t2, 0.0088), (t2, t3, 0.0080), (t3, tl("thumb3" + S), 0.0070))): caps(a, b, r)
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.selected_objects: o.select_set(False)
    ob.select_set(True); bpy.ops.object.convert(target='MESH')
    m = bpy.context.view_layer.objects.active; m.name = B.name.replace("_BODY", "_HAND_" + s)
    me = m.data; me.name = m.name
    # parent / transformasi sama dengan BODY
    m.parent = B.parent; m.matrix_parent_inverse = B.matrix_parent_inverse.copy(); m.matrix_basis = B.matrix_basis.copy()
    # bobot: segmen tulang terdekat (campur halus)
    segs = {}
    for n in ("hand" + S, "forearm" + S) + tuple(f + str(i) + S for f in FING for i in (1, 2, 3)) + tuple("thumb" + str(i) + S for i in (1, 2, 3)):
        segs[n] = (hd(n), tl(n)); m.vertex_groups.new(name=n)
    for v in me.vertices:
        ds = {n: _seg_dist(v.co, a, b) for n, (a, b) in segs.items()}
        dmin = min(ds.values()); ws = {n: math.exp(-(d - dmin) / 0.0035) for n, d in ds.items() if d - dmin < 0.014}
        tot = sum(ws.values())
        for n, w in ws.items():
            if w / tot > 0.02: m.vertex_groups[n].add([v.index], w / tot, 'REPLACE')
    for p in me.polygons: p.use_smooth = True
    me.materials.clear()
    for sl in B.material_slots: me.materials.append(sl.material)
    am = m.modifiers.new("Armature", 'ARMATURE'); am.object = R
    so = m.modifiers.new("Outline", 'SOLIDIFY'); so.thickness = 0.0012; so.offset = 1; so.use_flip_normals = True; so.material_offset = 1
    m["wrist_local"] = list(wr)
    return m

def cut_old_hand(B, s):
    S = "." + s; names = ["hand" + S] + [f + str(i) + S for f in FING for i in (1, 2, 3)] + ["thumb" + str(i) + S for i in (1, 2, 3)]
    gi = {B.vertex_groups[n].index for n in names if n in B.vertex_groups}
    bm = bmesh.new(); bm.from_mesh(B.data); dl = B.data.vertices.layers if False else None
    dvl = bm.verts.layers.deform.verify(); kill = []
    for v in bm.verts:
        w = sum(v[dvl].get(i, 0.0) for i in gi)
        if w > 0.5: kill.append(v)
    n = len(kill); bmesh.ops.delete(bm, geom=kill, context='VERTS'); bm.to_mesh(B.data); bm.free(); return n

def rebuild_hands(rig_name, sides=("L", "R"), cut=True):
    R = bpy.data.objects[rig_name]; B = _body_of(R); out = []
    for s in sides:
        for o in [o for o in bpy.data.objects if o.name == B.name.replace("_BODY", "_HAND_" + s)]: bpy.data.objects.remove(o)
        h = build_hand(R, B, s); n = cut_old_hand(B, s) if cut else 0; out.append((h.name, len(h.data.vertices), n))
    return out
