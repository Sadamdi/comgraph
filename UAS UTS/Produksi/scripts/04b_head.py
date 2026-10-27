# 04b - Kepala bergaya anime: tengkorak (deformasi elipsoid), telinga, mata + kelopak (blink), kilau, alis, mulut (shape key)
import bpy, bmesh, math
import numpy as np
from mathutils import Vector, Matrix, Euler

TL = bpy.app.driver_namespace["TOON"]
TF = bpy.app.driver_namespace["TOONFN"]

def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)

def smooth_obj(o):
    for p in o.data.polygons: p.use_smooth = True

def link_to(o, coll):
    for c in list(o.users_collection): c.objects.unlink(o)
    coll.objects.link(o)

def make_skull(name, rx=0.072, ry=0.080, rz=0.098, chin=0.40, cheek=0.004, female=True):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=28, radius=1.0)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    nx, ny, nz = co[:, 0].copy(), co[:, 1].copy(), co[:, 2].copy()
    x = rx * nx; y = ry * ny; z = rz * nz
    # rahang meruncing (dagu anime)
    t = smoothstep(0.0, 1.0, np.clip((-z - 0.012) / (rz * 0.92), 0, 1))
    wx = 1 - chin * t ** 1.25
    wy = 1 - 0.20 * t
    x = x * wx; y = y * wy
    # dagu sedikit maju & lancip
    front = (ny < 0).astype(np.float32)
    y = y - front * 0.007 * smoothstep(0.55, 1.0, t)
    # pipi penuh
    cm = np.exp(-(((z + 0.028) / 0.034) ** 2)) * (1 - t * 0.3)
    x = x * (1 + cheek / rx * cm)
    # bidang wajah agak rata
    plane = -(ry * 0.93) + 0.012 * (x / rx) ** 2
    w = smoothstep(0.15, 0.65, -ny) * 0.55 * (1 - smoothstep(0.1, 0.6, np.clip(z / rz, 0, 1)))
    y = np.where(ny < 0, y * (1 - w) + plane * w * (wy), y)
    # hidung kecil
    bump = np.exp(-((x / 0.010) ** 2 + ((z + 0.020) / 0.016) ** 2))
    y = y - front * 0.0055 * bump
    # belakang kepala sedikit lebih besar (sanggul/rambut menempel)
    out = np.stack([x, y, z], axis=1).astype(np.float32)
    me.vertices.foreach_set("co", out.ravel()); me.update()
    o = bpy.data.objects.new(name, me)
    sd = o.modifiers.new("Subsurf", 'SUBSURF'); sd.levels = 1; sd.render_levels = 2
    smooth_obj(o)
    return o

def ellipsoid(name, r, scale, loc, rot=(0, 0, 0), seg=16, rings=10):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    for v in bm.verts:
        v.co.x *= r * scale[0]; v.co.y *= r * scale[1]; v.co.z *= r * scale[2]
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.location = loc; o.rotation_euler = rot
    smooth_obj(o); return o

def lid_cap(name, r, loc, a0, a1):
    """Cangkang bola (kelopak): sudut kutub a0..a1 (rad) dari kutub atas."""
    bm = bmesh.new()
    segs, rings = 20, 8
    verts = []
    for i in range(rings + 1):
        phi = a0 + (a1 - a0) * i / rings
        row = []
        for j in range(segs + 1):
            th = 2 * math.pi * j / segs
            row.append(bm.verts.new((r * math.sin(phi) * math.cos(th), r * math.sin(phi) * math.sin(th), r * math.cos(phi))))
        verts.append(row)
    for i in range(rings):
        for j in range(segs):
            bm.faces.new((verts[i][j], verts[i][j + 1], verts[i + 1][j + 1], verts[i + 1][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.location = loc
    smooth_obj(o)
    sd = o.modifiers.new("Thick", 'SOLIDIFY'); sd.thickness = 0.0014; sd.offset = 1.0
    return o

def curve_stroke(name, pts, radius, mat, taper=True):
    cd = bpy.data.curves.new(name, 'CURVE'); cd.dimensions = '3D'
    sp = cd.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for p, bp in zip(pts, sp.bezier_points):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    cd.bevel_depth = radius; cd.bevel_resolution = 3; cd.use_fill_caps = True
    o = bpy.data.objects.new(name, cd); cd.materials.append(mat)
    if taper:
        tp = bpy.data.curves.new(name + "_taper", 'CURVE'); tp.dimensions = '3D'
        s2 = tp.splines.new('POLY'); s2.points.add(2)
        for i, (xx, yy) in enumerate(((0, 0.35), (0.5, 1.0), (1, 0.25))): s2.points[i].co = (xx, yy, 0, 1)
        to = bpy.data.objects.new(name + "_taper", tp); cd.taper_object = to; to.hide_render = True; to.hide_viewport = True
        bpy.context.scene.collection.objects.link(to)
        o["_taper"] = to.name
    return o

def build_head(name, kind, coll):
    """Mengembalikan dict objek kepala. Semua di-parent ke objek 'name_HEAD' (origin = pusat tengkorak)."""
    f = kind == "lastri"
    skin = TL["skin_lastri"] if f else TL["skin_cust"]
    skull = make_skull(name + "_HEAD", rx=0.071 if f else 0.076, ry=0.080, rz=0.098 if f else 0.102, chin=0.27 if f else 0.22, cheek=0.007)
    skull.data.materials.append(skin); TF["add_outline"](skull, 0.0015)
    link_to(skull, coll)
    parts = {"head": skull}
    ex, ey, ez, er = 0.036, -0.060, 0.001, 0.0225
    for side, sx in (("L", 1), ("R", -1)):
        # bola mata
        eye = ellipsoid(f"{name}_eye_{side}", er, (1, 1, 1), (sx * ex, ey, ez), seg=24, rings=16)
        eye.data.materials.append(TL["eye_l"] if f else TL["eye_c"]); eye.parent = skull
        link_to(eye, coll); parts[f"eye_{side}"] = eye
        # kelopak atas (blink): cangkang dari kutub atas sampai ~ 66 derajat
        lid = lid_cap(f"{name}_lid_{side}", er * 1.06, (sx * ex, ey, ez), 0.0, math.radians(56))
        lid.data.materials.append(skin); lid.parent = skull; link_to(lid, coll); parts[f"lid_{side}"] = lid
        # kelopak bawah (tetap): cangkang tipis dari bawah
        lo = lid_cap(f"{name}_lidlow_{side}", er * 1.06, (sx * ex, ey, ez), math.radians(142), math.radians(180))
        lo.data.materials.append(skin); lo.parent = skull; link_to(lo, coll); parts[f"lidlow_{side}"] = lo
        # bulu mata tebal di tepi kelopak atas (ikut berkedip karena child kelopak)
        pts = []
        for k in range(9):
            a = math.radians(-58 + 116 * k / 8)
            pts.append((er * 1.075 * math.sin(math.radians(68)) * math.sin(a) * 0 + er * 1.075 * math.sin(a), 0, 0))
        # busur di bidang XZ pada tepi kelopak (phi=68 derajat)
        arc = []
        for k in range(9):
            th = math.radians(200 + 140 * k / 8) if sx > 0 else math.radians(200 + 140 * k / 8)
            # tepi kelopak: lingkaran pada phi tetap; parametrisasi sepanjang bagian depan (-Y)
            ph = math.radians(56)
            ang = math.radians(-70 + 140 * k / 8)
            arc.append((er * 1.075 * math.sin(ph) * math.sin(ang), -er * 1.075 * math.sin(ph) * math.cos(ang), er * 1.075 * math.cos(ph)))
        lash = curve_stroke(f"{name}_lash_{side}", arc, 0.0016, TL["lash"])
        lash.parent = lid; link_to(lash, coll); parts[f"lash_{side}"] = lash
        # kilau mata (sparkle) tetap di depan iris: tidak ikut gerak bola
        for tag, (dx, dz, sr) in (("a", (-0.30, 0.34, 0.0050)), ("b", (0.26, -0.28, 0.0022))):
            d = Vector((dx * (1 if sx > 0 else 1), -0.9, dz)).normalized()
            sp = ellipsoid(f"{name}_sparkle{tag}_{side}", sr, (1, 0.3, 1), Vector((sx * ex, ey, ez)) + d * er * 1.012, seg=10, rings=6)
            sp.data.materials.append(TL["sparkle"]); sp.parent = skull; link_to(sp, coll); parts[f"spark{tag}_{side}"] = sp
        # alis
        brow_pts = [(sx * (ex + 0.020), ey - 0.003, ez + 0.036), (sx * (ex + 0.002), ey - 0.008, ez + 0.040), (sx * (ex - 0.016), ey - 0.006, ez + 0.036)]
        brow = curve_stroke(f"{name}_brow_{side}", brow_pts, 0.0030, TL["hair_black"] if f else TL["hair_black"])
        brow.parent = skull; link_to(brow, coll); parts[f"brow_{side}"] = brow
        # pipi merona
        bl = ellipsoid(f"{name}_blush_{side}", 0.0085, (1.3, 0.10, 1.0), (sx * 0.040, -0.0725, -0.026), rot=(0, 0, 0), seg=12, rings=6)
        bl.data.materials.append(TL["blush"]); bl.parent = skull; link_to(bl, coll); parts[f"blush_{side}"] = bl
        # telinga
        ear = ellipsoid(f"{name}_ear_{side}", 0.017, (0.45, 0.8, 1.2), (sx * 0.0715, 0.004, -0.010), rot=(0, 0, math.radians(8 * sx)), seg=12, rings=8)
        ear.data.materials.append(skin); ear.parent = skull; link_to(ear, coll); parts[f"ear_{side}"] = ear
    # garis hidung (lengkung kecil) di atas bibir
    nose = curve_stroke(name + "_nose", [(-0.006, -0.0700, -0.0300), (0.0, -0.0715, -0.0335), (0.006, -0.0700, -0.0300)], 0.0009, TL["nose"], taper=False)
    nose.parent = skull; link_to(nose, coll); parts["nose"] = nose
    # mulut: strip dengan shape key
    mo = make_mouth(name + "_mouth", TL["mouth_in"], TL["lip"])
    mo.location = (0, -0.0745, -0.057)
    mo.parent = skull; link_to(mo, coll); parts["mouth"] = mo
    for k, p in parts.items():
        if k != "head": p.matrix_parent_inverse = skull.matrix_world.inverted()
    return parts

def make_mouth(name, inner, lip):
    """Mulut: cincin elips kecil. Shape key: smile, open_a, open_o."""
    bm = bmesh.new()
    n = 16
    ring_o, ring_i = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        ring_o.append(bm.verts.new((math.cos(a) * 0.017, 0, math.sin(a) * 0.0040)))
        ring_i.append(bm.verts.new((math.cos(a) * 0.0135, -0.0006, math.sin(a) * 0.0022)))
    c = bm.verts.new((0, -0.0006, 0))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ring_o[i], ring_o[j], ring_i[j], ring_i[i]))
        bm.faces.new((ring_i[i], ring_i[j], c))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(lip); me.materials.append(inner)
    for p in me.polygons: p.material_index = 0 if len(p.vertices) == 4 else 1
    o = bpy.data.objects.new(name, me)
    basis = o.shape_key_add(name="Basis")
    def key(nm, fn):
        k = o.shape_key_add(name=nm)
        for i, v in enumerate(me.vertices):
            k.data[i].co = fn(Vector(basis.data[i].co))
        k.value = 0.0
    # smile: sudut terangkat, lebar, bawah melengkung
    key("smile", lambda p: Vector((p.x * 1.18, p.y, p.z + 0.0042 * (abs(p.x) / 0.017) ** 2 - 0.0010)))
    key("open_a", lambda p: Vector((p.x * 0.92, p.y, p.z - (0.0075 * max(0.0, 1 - (abs(p.x) / 0.017) ** 2)) if p.z <= 0.0004 else p.z + 0.0010 * max(0.0, 1 - (abs(p.x) / 0.017) ** 2))))
    key("open_o", lambda p: Vector((p.x * 0.50, p.y, p.z * 2.6)))
    return o

print("head lib ok")
