# 04d - Rakit karakter utuh di titik asal: badan (Skin->mesh), kepala, rambut, pakaian, alas kaki, ransel.
# Output: dict dengan daftar 'deform' (mesh yang diberi bobot tulang) dan 'rigid' {objek: nama_tulang}.
import bpy, bmesh, math
import numpy as np
from mathutils import Vector

TL = bpy.app.driver_namespace["TOON"]
TF = bpy.app.driver_namespace["TOONFN"]
exec(open(r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\scripts\04a_body.py", encoding="utf8").read().split("if __name__")[0])  # body_spec, build_body, coll
exec(open(r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\scripts\04b_head.py", encoding="utf8").read())
exec(open(r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\scripts\04c_hair.py", encoding="utf8").read())

def apply_mods(o):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = o.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev)
    old = o.data
    o.modifiers.clear()
    o.data = me
    bpy.data.meshes.remove(old)
    for p in me.polygons: p.use_smooth = True
    return o

def joints_of(o, keys):
    return {k: Vector(o["_J"][k]) for k in keys}

def shell_from(body_me, name, zcuts, cond, off, mat, thick=0.004, outline=0.0013, coll=None):
    bm = bmesh.new(); bm.from_mesh(body_me)
    for z in zcuts:
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, z), plane_no=(0, 0, 1), dist=1e-5)
    kill = [f for f in bm.faces if not cond(f.calc_center_median())]
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bm.normal_update()
    for v in bm.verts: v.co += v.normal * off
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    me.materials.append(mat)
    sd = o.modifiers.new("Thick", 'SOLIDIFY'); sd.thickness = -thick; sd.offset = 1.0
    if outline > 0: TF["add_outline"](o, outline)
    if coll: coll.objects.link(o)
    return o

def surf_grid(name, fn, nu, nv, mat, coll, thick=0.004, outline=0.0013):
    """Permukaan parametrik fn(u,v)->(x,y,z), u,v in [0,1]."""
    bm = bmesh.new()
    g = [[bm.verts.new(fn(i / nu, j / nv)) for i in range(nu + 1)] for j in range(nv + 1)]
    for j in range(nv):
        for i in range(nu):
            bm.faces.new((g[j][i], g[j][i + 1], g[j + 1][i + 1], g[j + 1][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); me.materials.append(mat)
    sd = o.modifiers.new("Thick", 'SOLIDIFY'); sd.thickness = thick; sd.offset = 1.0
    if outline > 0: TF["add_outline"](o, outline)
    coll.objects.link(o); return o

def rounded_box(name, size, loc, mat, coll, bevel=0.02, outline=0.0014):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co.x *= size[0]; v.co.y *= size[1]; v.co.z *= size[2]
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = loc; me.materials.append(mat)
    b = o.modifiers.new("Bevel", 'BEVEL'); b.width = bevel; b.segments = 4; b.limit_method = 'NONE'
    s = o.modifiers.new("Sub", 'SUBSURF'); s.levels = 1; s.render_levels = 2
    if outline > 0: TF["add_outline"](o, outline)
    coll.objects.link(o); return o

def ellipsoid_obj(name, r, scale, loc, mat, coll, outline=0.0014, seg=20, rings=12):
    o = ellipsoid(name, r, scale, loc, seg=seg, rings=rings)
    o.data.materials.append(mat)
    if outline > 0: TF["add_outline"](o, outline)
    coll.objects.link(o); return o

def ribbon(name, pts, width, mat, coll, thick=0.004, outline=0.0012):
    """Pita (tali) mengikuti polyline 3D."""
    bm = bmesh.new()
    P_ = [Vector(p) for p in pts]
    rows = []
    for i, p in enumerate(P_):
        t = (P_[min(i + 1, len(P_) - 1)] - P_[max(i - 1, 0)]).normalized()
        s_ = t.cross(Vector((0, 0, 1)))
        if s_.length < 1e-4: s_ = t.cross(Vector((1, 0, 0)))
        s_.normalize()
        rows.append((bm.verts.new(p - s_ * width / 2), bm.verts.new(p + s_ * width / 2)))
    for i in range(len(rows) - 1):
        bm.faces.new((rows[i][0], rows[i][1], rows[i + 1][1], rows[i + 1][0]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for q in me.polygons: q.use_smooth = True
    o = bpy.data.objects.new(name, me); me.materials.append(mat)
    sd = o.modifiers.new("Thick", 'SOLIDIFY'); sd.thickness = thick; sd.offset = 1.0
    if outline > 0: TF["add_outline"](o, outline)
    coll.objects.link(o); return o

def assemble(kind, coll):
    nm = "LASTRI" if kind == "lastri" else "MHS"
    f = kind == "lastri"
    S = body_spec(kind); Z = S["z"]; k = S["H"] / 1.55
    out = {"deform": [], "rigid": {}, "S": S}
    # ---- badan ----
    body, S2, keys = build_body(kind, nm)
    coll.objects.link(body)
    # perbaiki arah tekuk siku/lutut sebelum Skin dihitung
    bpy.context.view_layer.objects.active = body
    body["_J"] = {}
    me = body.data
    for i, key in enumerate(keys):
        body["_J"][key] = tuple(me.vertices[i].co)
    apply_mods(body)
    body.data.materials.append(TL["skin_lastri"] if f else TL["skin_cust"])
    TF["add_outline"](body, 0.0015)
    out["deform"].append(body); out["body"] = body
    bme = body.data
    # ---- kepala ----
    hp = build_head(nm, kind, coll)
    head = hp["head"]; head.location = (0, 0.002, (1.455 if f else 1.61))
    out["head_parts"] = hp
    hair = build_hair(nm, kind, head, coll)
    out["hair"] = hair
    head.scale = (1.22, 1.22, 1.22)
    bpy.context.view_layer.update()
    # parent ke tulang kepala nanti; simpan daftar rigid
    out["rigid"][head] = "head"
    for key, p in hp.items():
        if key != "head" and p.parent is head:
            pass  # anak kepala ikut kepala
    # ---- pakaian ----
    zsh = Z["sh"]; zneck = Z["neck0"] + 0.012
    sho = S["sh"]
    elbow_z = zsh - 0.015 - 0.27 * k
    wrist_z = elbow_z - 0.245 * k
    if f:
        blouse = shell_from(bme, nm + "_blouse", [0.93, elbow_z + 0.10, zneck],
                            lambda c: (abs(c.x) < 0.145 and 0.93 <= c.z <= zneck) or (abs(c.x) >= 0.145 and elbow_z + 0.10 <= c.z <= zsh + 0.02),
                            0.0085, TL["blouse"], coll=coll)
        out["deform"].append(blouse)
        # celemek teal (bib + rok depan)
        def skirt_r(z):
            return 0.155 + (0.215 - 0.155) * (max(0.0, 1.0 - z) / 0.60) ** 0.9 if z < 1.0 else 0.155
        def apron_fn(u, v):
            zt, zb = 1.215, 0.62
            z = zt + (zb - zt) * v
            if z >= 1.0:
                a_ = 0.118 + 0.012; b_ = 0.098 + 0.014
            else:
                a_ = skirt_r(z) * 1.02 + 0.014; b_ = skirt_r(z) * 0.92 + 0.020
            half = math.radians(30 + 56 * v)
            th = (u - 0.5) * 2 * half
            return (a_ * math.sin(th), -b_ * math.cos(th), z)
        apron = surf_grid(nm + "_apron", apron_fn, 18, 16, TL["apron"], coll, thick=0.005)
        out["deform"].append(apron)
        # tali celemek di leher
        for sx in (1, -1):
            strap = ribbon(f"{nm}_apron_strap{sx}", [(sx * 0.060, -0.118, 1.205), (sx * 0.075, -0.098, 1.26), (sx * 0.068, -0.045, 1.318), (sx * 0.040, 0.02, 1.335), (0.0, 0.062, 1.318)], 0.026, TL["apron"], coll)
            out["deform"].append(strap)
        # rok panjang (kain batik gelap) A-line
        def skirt_fn(u, v):
            th = 2 * math.pi * u
            z = 1.0 + (0.40 - 1.0) * v
            r = 0.155 + (0.215 - 0.155) * v ** 0.9
            wob = 1 + 0.02 * math.sin(th * 7) * v
            return (r * 1.02 * wob * math.sin(th), -r * 0.92 * wob * math.cos(th), z)
        skirt = surf_grid(nm + "_skirt", skirt_fn, 32, 10, TL["skirt"], coll, thick=0.005)
        out["deform"].append(skirt)
        # sandal jepit
        for side, sx in (("L", 1), ("R", -1)):
            sole = rounded_box(f"{nm}_sandal_{side}", (0.095, 0.245, 0.018), (sx * S["hip"], -0.045, 0.011), TL["sandal"], coll, 0.008, 0.0015)
            out["rigid"][sole] = f"foot.{side}"
    else:
        # jaket kuning, lengan panjang
        zjk = zsh - 0.005                 # batas atas jaket: dasar leher (di atasnya permukaan badan melengkung -> sayap runcing)
        jacket = shell_from(bme, nm + "_jacket", [0.90 * k, wrist_z + 0.03, zjk],
                            lambda c: (abs(c.x) < 0.17 and 0.90 * k <= c.z <= zjk) or (abs(c.x) >= 0.17 and wrist_z + 0.03 <= c.z <= zsh + 0.02),
                            0.017, TL["jacket"], thick=0.005, coll=coll)
        out["deform"].append(jacket)
        # kerah/hoodie di belakang leher
        hood = ellipsoid_obj(nm + "_hood", 0.062, (1.05, 0.55, 0.62), (0, 0.045, zneck + 0.005), TL["jacket"], coll)
        out["rigid"][hood] = "chest"
        jeans = shell_from(bme, nm + "_jeans", [0.07 * k, 0.99 * k],
                           lambda c: abs(c.x) < 0.172 and 0.07 * k <= c.z <= 0.99 * k and not (abs(c.x) > 0.105 and c.z > 0.80 * k and False),
                           0.012, TL["jeans"], thick=0.005, coll=coll)
        out["deform"].append(jeans)
        # sepatu sneakers
        for side, sx in (("L", 1), ("R", -1)):
            shoe = ellipsoid_obj(f"{nm}_shoe_{side}", 0.055, (1.0, 2.05, 0.82), (sx * S["hip"], -0.045, 0.051 * k), TL["shoe"], coll, 0.002)
            sole = ellipsoid_obj(f"{nm}_sole_{side}", 0.056, (1.10, 2.30, 0.30), (sx * S["hip"], -0.045, 0.019), TL["sole"], coll, 0.0016)
            out["rigid"][shoe] = f"foot.{side}"; out["rigid"][sole] = f"foot.{side}"
        # ransel teal
        pack = rounded_box(nm + "_backpack", (0.30, 0.15, 0.40), (0, 0.145, 1.15 * k), TL["backpack"], coll, 0.035, 0.002)
        out["rigid"][pack] = "chest"
        for sx in (1, -1):
            st = ribbon(f"{nm}_pack_strap{sx}", [(sx * 0.095, 0.105, 1.30 * k), (sx * 0.118, 0.02, 1.345 * k), (sx * 0.120, -0.07, 1.265 * k), (sx * 0.150, -0.075, 1.12 * k), (sx * 0.17, 0.0, 1.01 * k), (sx * 0.11, 0.10, 0.97 * k)], 0.045, TL["backpack"], coll, thick=0.005)
            out["deform"].append(st)
    return out

print("assemble lib ok")
