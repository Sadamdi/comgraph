# 04c - Rambut gaya anime: cangkang kulit kepala + gumpalan (tuft) runcing + sanggul / rambut pendek acak
import bpy, bmesh, math, random
from mathutils import Vector

TL = bpy.app.driver_namespace["TOON"]
TF = bpy.app.driver_namespace["TOONFN"]

def P(rx, ry, rz, phi, el, off=0.0):
    x = rx * math.cos(el) * math.sin(phi)
    y = -ry * math.cos(el) * math.cos(phi)
    z = rz * math.sin(el)
    n = Vector((x / rx ** 2, y / ry ** 2, z / rz ** 2)).normalized()
    return Vector((x, y, z)) + n * off

def shell(name, rx, ry, rz, off, cut_fn, thick=0.004):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=80, v_segments=48, radius=1.0)
    for v in bm.verts:
        v.co.x *= rx + off; v.co.y *= ry + off; v.co.z *= rz + off
    # klem verteks di bawah garis rambut ke batas (tepi mulus), lalu gabungkan titik ganda dan buang muka degenerat
    for v in bm.verts:
        if not cut_fn(v.co):
            lo, hi = v.co.z, 1.0
            for _ in range(14):
                mid = (lo + hi) / 2
                # cari z terendah yang masih lolos untuk azimuth ini (cut_fn monoton terhadap z)
                if cut_fn(Vector((v.co.x, v.co.y, mid))): hi = mid
                else: lo = mid
            ztarget = hi
            sc_ = math.sqrt(max(1e-9, 1 - (ztarget / (rz + off)) ** 2)) / math.sqrt(max(1e-9, 1 - (v.co.z / (rz + off)) ** 2))
            v.co.x *= sc_; v.co.y *= sc_; v.co.z = ztarget
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0004)
    bad = [f for f in bm.faces if f.calc_area() < 1e-8]
    if bad: bmesh.ops.delete(bm, geom=bad, context='FACES')
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    for p in me.polygons: p.use_smooth = True
    sd = o.modifiers.new("Thick", 'SOLIDIFY'); sd.thickness = thick; sd.offset = -1.0
    return o

def tuft(name, pts, radius, mat, tip=0.04, mid=0.9):
    cd = bpy.data.curves.new(name, 'CURVE'); cd.dimensions = '3D'
    sp = cd.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for p, bp in zip(pts, sp.bezier_points):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    cd.bevel_depth = radius; cd.bevel_resolution = 3; cd.use_fill_caps = True
    tp = bpy.data.curves.new(name + "_tp", 'CURVE'); tp.dimensions = '3D'
    s2 = tp.splines.new('POLY'); s2.points.add(3)
    for i, (xx, yy) in enumerate(((0, 0.55), (0.35, mid), (0.75, 0.55), (1, tip))): s2.points[i].co = (xx, yy, 0, 1)
    to = bpy.data.objects.new(name + "_tp", tp); bpy.context.scene.collection.objects.link(to)
    to.hide_render = True; to.hide_viewport = True
    cd.taper_object = to
    cd.materials.append(mat)
    o = bpy.data.objects.new(name, cd)
    return o, to

def to_mesh(o):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.convert(target='MESH')
    return bpy.context.view_layer.objects.active

def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    r = bpy.context.view_layer.objects.active; r.name = name
    return r

def build_hair(name, kind, head, coll):
    random.seed(5 if kind == "lastri" else 9)
    f = kind == "lastri"
    rx, ry, rz = (0.071, 0.080, 0.098) if f else (0.076, 0.080, 0.102)
    mat = TL["hair_black"]
    def cut(co):
        phi = math.atan2(co.x, -co.y)   # 0 = depan
        a = abs(phi)
        if f:
            if a < math.radians(50): h = 0.40
            elif a < math.radians(100): h = 0.40 - 0.40 * (a - math.radians(50)) / math.radians(50)
            else: h = 0.0 - 0.62 * (a - math.radians(100)) / math.radians(80)
        else:   # mahasiswa: poni pendek, rambut turun menutupi pelipis, telinga, dan tengkuk (tidak ada kulit telanjang di belakang kepala)
            if a < math.radians(50): h = 0.52
            elif a < math.radians(95): h = 0.52 - 0.74 * (a - math.radians(50)) / math.radians(45)
            else: h = -0.22 - 0.46 * (a - math.radians(95)) / math.radians(85)
        return co.z / (rz + 0.007) > h
    sh = shell(name + "_hair_cap", rx, ry, rz, 0.0075, cut, 0.0045)
    sh.data.materials.append(mat)
    parts = [sh]
    tufts = []
    n_bang = 13 if f else 13
    for i in range(n_bang):
        u = -1 + 2 * i / (n_bang - 1)
        S = P(rx, ry, rz, 0.04 * u, math.radians(74), 0.006)
        M = P(rx, ry, rz, 0.55 * u, math.radians(50 if f else 56), 0.017)
        E = P(rx, ry, rz, 0.95 * u, math.radians((31 if f else 40) - 5 * abs(u)), 0.014 + 0.004 * random.random())
        o, to = tuft(f"{name}_bang{i}", [S, M, E], 0.0135 if f else 0.0120, mat, tip=0.05)
        tufts.append(o)
    if f:
        # rambut samping membingkai wajah (kiri/kanan)
        for sx in (1, -1):
            for k in range(2):
                S = P(rx, ry, rz, sx * math.radians(70 + 10 * k), math.radians(46), 0.01)
                M = P(rx, ry, rz, sx * math.radians(88 + 8 * k), math.radians(8), 0.021)
                E = P(rx, ry, rz, sx * math.radians(98 + 6 * k), math.radians(-34 - 6 * k), 0.016)
                o, to = tuft(f"{name}_side{sx}_{k}", [S, M, E], 0.0125, mat, tip=0.06)
                tufts.append(o)
        # sanggul (konde) di belakang atas kepala
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=0.044)
        for v in bm.verts: v.co.z *= 0.86
        me = bpy.data.meshes.new(name + "_bun"); bm.to_mesh(me); bm.free()
        bun = bpy.data.objects.new(name + "_bun", me); bun.location = (0, 0.072, 0.052)
        for p in me.polygons: p.use_smooth = True
        bun.data.materials.append(mat); parts.append(bun)
    else:
        # mahasiswa: jambul pendek acak di atas kepala
        for i in range(14):
            phi = random.uniform(-2.8, 2.8); el = math.radians(random.uniform(52, 82))
            S = P(rx, ry, rz, phi, el, 0.006)
            direction = Vector((math.sin(phi) * 0.8, -math.cos(phi) * 0.8, 0.9)).normalized()
            M = S + direction * 0.017 + Vector((random.uniform(-.006, .006), random.uniform(-.006, .006), 0))
            E = S + direction * 0.036 + Vector((random.uniform(-.01, .01), random.uniform(-.01, .01), -0.004))
            o, to = tuft(f"{name}_spike{i}", [S, M, E], 0.0125, mat, tip=0.03)
            tufts.append(o)
    for o in tufts + parts[1:]:
        coll.objects.link(o)
    coll.objects.link(sh)
    meshes = [to_mesh(o) for o in tufts]
    # buang objek taper
    for o in [x for x in bpy.data.objects if x.name.endswith("_tp")]:
        bpy.data.objects.remove(o)
    allobjs = [sh] + [p for p in parts[1:]] + meshes
    # terapkan solidify cangkang agar bisa digabung
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = sh; sh.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Thick")
    hair = join(allobjs, name + "_HAIR")
    for p in hair.data.polygons: p.use_smooth = True
    hair.location = (0, 0, 0)
    # material: toon + garis tepi
    hair.data.materials.clear(); hair.data.materials.append(mat)
    TF["add_outline"](hair, 0.0015, TL["outline_hair"])
    hair.parent = head   # mesh rambut dibangun di ruang-lokal kepala -> inverse identitas
    for c in list(hair.users_collection): c.objects.unlink(hair)
    coll.objects.link(hair)
    return hair

print("hair lib ok")
