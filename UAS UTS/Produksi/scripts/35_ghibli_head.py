# 35 - Kepala bergaya Ghibli, dibangun ulang DI TEMPAT (objek lama dipakai ulang -> rig, gaze, kedip, mulut, animasi tetap jalan)
# Tengkorak = SDF (gabungan halus tengkorak/rahang/pipi/alis/hidung/bibir, dikurangi lekuk mata) diproyeksikan radial ke quad-sphere (tanpa kutub).
# Bukaan mata = lubang almond pada topologi; tepinya membungkus bola mata (tebal kelopak). Kelopak kedip mengikuti tepi atas almond.
# Pakai: ghibli_head("LASTRI", "lastri"); ghibli_head("MHS", "cust")   (koordinat lokal kepala: -Y depan, Z atas, sebelum skala 1.22)
import bpy, bmesh, math
import numpy as np
from mathutils import Vector

OB = bpy.data.objects

# ---------------- SDF (numpy, P: (n,3)) ----------------
def _ell(P, c, r):
    q = (P - np.asarray(c)) / np.asarray(r)
    k0 = np.linalg.norm(q, axis=1); k1 = np.linalg.norm(q / np.asarray(r), axis=1)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)

def _sph(P, c, r):
    return np.linalg.norm(P - np.asarray(c), axis=1) - r

def _cap(P, a, b, ra, rb):
    a = np.asarray(a); b = np.asarray(b); ba = b - a
    h = np.clip(((P - a) @ ba) / (ba @ ba), 0, 1)
    return np.linalg.norm(P - a - h[:, None] * ba, axis=1) - (ra + (rb - ra) * h)

def _smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b + (a - b) * h - k * h * (1 - h)

def _ssub(a, s, k):          # a dikurangi s (halus)
    return -_smin(-a, s, k)

SPEC = {
    # Bu Lastri: wanita paruh baya - wajah oval lembut, rahang membulat, dagu kecil tidak lancip, pipi berisi
    "lastri": dict(
        cranium=((0, 0.000, 0.014), (0.070, 0.079, 0.085)),
        face=((0, -0.016, -0.028), (0.054, 0.058, 0.062)),
        jaw=((0, -0.010, -0.050), (0.047, 0.048, 0.042)),
        chin=((0, -0.049, -0.079), (0.023, 0.023, 0.019)),
        cheek=((0.034, -0.052, -0.026), 0.020),
        brow=((0, -0.057, 0.023), (0.056, 0.026, 0.015)),
        nose=((0, -0.071, 0.008), (0, -0.0850, -0.030), 0.0058, 0.0080), nose_tip=((0, -0.0868, -0.0340), 0.0088), alae=((0.0098, -0.0775, -0.0385), 0.0066),
        lip_u=((0, -0.0725, -0.0555), (0.017, 0.009, 0.0058)), lip_l=((0, -0.0705, -0.0655), (0.0150, 0.009, 0.0062)),
        eye=(0.0300, -0.0570, 0.004), er=0.0150, socket=1.20,
        almond=dict(a_in=-0.62, a_out=0.72, e_in=-0.03, e_out=0.05, eu=0.52, el=0.44),
        iris=0.62, brow_pts=((0.011, 0.020), (0.026, 0.0285), (0.044, 0.0245), (0.054, 0.016)), brow_r=0.0015,
        ear=((0.0685, 0.008, -0.010), (0.0060, 0.0135, 0.0215)),
        mouth=dict(z=-0.0605, w=0.0115),
    ),
    # Mahasiswa: pria muda - rahang lebih tegas, dagu lebar, alis tebal lurus, hidung sedikit lebih panjang
    "cust": dict(
        cranium=((0, 0.000, 0.016), (0.074, 0.081, 0.088)),
        face=((0, -0.016, -0.030), (0.057, 0.059, 0.064)),
        jaw=((0, -0.008, -0.054), (0.052, 0.050, 0.044)),
        chin=((0, -0.050, -0.085), (0.027, 0.023, 0.020)),
        cheek=((0.035, -0.051, -0.026), 0.019),
        brow=((0, -0.058, 0.024), (0.060, 0.027, 0.016)),
        nose=((0, -0.072, 0.010), (0, -0.0880, -0.032), 0.0062, 0.0084), nose_tip=((0, -0.0895, -0.0360), 0.0092), alae=((0.0105, -0.0795, -0.0405), 0.0068),
        lip_u=((0, -0.0730, -0.0585), (0.018, 0.009, 0.0055)), lip_l=((0, -0.0715, -0.0690), (0.0160, 0.009, 0.0060)),
        eye=(0.0315, -0.0580, 0.004), er=0.0142, socket=1.20,
        almond=dict(a_in=-0.62, a_out=0.70, e_in=-0.02, e_out=0.02, eu=0.46, el=0.38),
        iris=0.60, brow_pts=((0.011, 0.0195), (0.028, 0.0250), (0.046, 0.0225), (0.056, 0.0150)), brow_r=0.0024,
        ear=((0.0715, 0.008, -0.010), (0.0062, 0.0140, 0.0225)),
        mouth=dict(z=-0.0635, w=0.0125),
    ),
}

def make_sdf(S):
    E = np.array(S["eye"]); er = S["er"]
    def f(P):
        d = _ell(P, *S["cranium"])
        d = _smin(d, _ell(P, *S["face"]), 0.020)
        d = _smin(d, _ell(P, *S["jaw"]), 0.020)
        d = _smin(d, _ell(P, *S["chin"]), 0.016)
        c, r = S["cheek"]
        for sx in (1, -1): d = _smin(d, _sph(P, (sx * c[0], c[1], c[2]), r), 0.020)
        d = _smin(d, _ell(P, *S["brow"]), 0.014)
        d = _smin(d, _cap(P, *S["nose"]), 0.009)
        d = _smin(d, _sph(P, *S["nose_tip"]), 0.006)
        c, r = S["alae"]
        for sx in (1, -1): d = _smin(d, _sph(P, (sx * c[0], c[1], c[2]), r), 0.005)
        d = _smin(d, _ell(P, *S["lip_u"]), 0.006)
        d = _smin(d, _ell(P, *S["lip_l"]), 0.006)
        for sx in (1, -1):      # lekuk soket dibatasi ke sisi luar garis x=0.012 -> punggung hidung tidak teriris
            sk = np.maximum(_sph(P, (sx * E[0], E[1], E[2]), er * S["socket"]), 0.013 - sx * P[:, 0])
            d = _ssub(d, sk, 0.006)
        return d
    return f

def _bisect(f, P0, D, lo, hi, it=42):
    lo = np.full(len(P0), lo); hi = np.full(len(P0), hi)
    for _ in range(it):
        m = 0.5 * (lo + hi)
        inside = f(P0 + D * m[:, None]) < 0
        lo = np.where(inside, m, lo); hi = np.where(inside, hi, m)
    return 0.5 * (lo + hi)

C0 = np.array((0.0, 0.0, -0.008))       # pusat proyeksi radial

def surf_y(f, x, z):
    """y permukaan depan kepala pada (x,z) lokal (bisection dari depan)."""
    x = np.atleast_1d(np.asarray(x, float)); z = np.atleast_1d(np.asarray(z, float))
    lo = np.full(len(x), -0.15); hi = np.full(len(x), 0.0)      # lo di luar (depan), hi di dalam
    for _ in range(42):
        m = 0.5 * (lo + hi)
        ins = f(np.stack([x, m, z], 1)) < 0
        hi = np.where(ins, m, hi); lo = np.where(ins, lo, m)
    return 0.5 * (lo + hi)

# ---------------- almond (ruang sudut bola mata) ----------------
def almond_fns(A):
    def lerp(a, b, t): return a + (b - a) * t
    def up(t): return lerp(A["e_in"], A["e_out"], t) + A["eu"] * np.sin(np.pi * np.clip(t, 0, 1) ** 0.85) ** 0.55
    def lo(t): return lerp(A["e_in"], A["e_out"], t) - A["el"] * np.sin(np.pi * np.clip(t, 0, 1) ** 1.15) ** 0.62
    def a_of(t): return lerp(A["a_in"], A["a_out"], t)
    def t_of(a): return (a - A["a_in"]) / (A["a_out"] - A["a_in"])
    return up, lo, a_of, t_of

def eye_angles(V, E, sx):
    """V (n,3) titik lokal kepala -> (a, e) relatif bola mata; a + = ke luar (temporal)."""
    v = V - E
    a = np.arctan2(sx * v[:, 0], -v[:, 1])
    e = np.arctan2(v[:, 2], np.hypot(v[:, 0], v[:, 1]))
    return a, e

def dir_from(a, e, sx):
    return np.stack([sx * np.cos(e) * np.sin(a), -np.cos(e) * np.cos(a), np.sin(e)], -1)

# ---------------- mesh kepala ----------------
def quad_sphere(n):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=n - 1, use_grid_fill=True)
    for v in bm.verts:
        p = v.co
        x, y, z = p.x, p.y, p.z      # cube->sphere seragam (mapping Nowell)
        v.co = Vector((x * math.sqrt(1 - y * y / 2 - z * z / 2 + y * y * z * z / 3),
                       y * math.sqrt(1 - z * z / 2 - x * x / 2 + z * z * x * x / 3),
                       z * math.sqrt(1 - x * x / 2 - y * y / 2 + x * x * y * y / 3)))
    return bm

def build_skull_mesh(name, S, f, n=40):
    bm = quad_sphere(n)
    D = np.array([v.co[:] for v in bm.verts]); D /= np.linalg.norm(D, axis=1)[:, None]
    P0 = np.tile(C0, (len(D), 1))
    r = _bisect(f, P0, D, 0.004, 0.2)
    for v, p in zip(bm.verts, P0 + D * r[:, None]): v.co = Vector(p)
    E0 = np.array(S["eye"]); er = S["er"]
    up, lo, a_of, t_of = almond_fns(S["almond"])
    rim_r, lip_r = 1.10 * er, 1.045 * er
    for sx in (1, -1):
        E = E0 * np.array((sx, 1, 1))
        bm.verts.ensure_lookup_table()
        V = np.array([v.co[:] for v in bm.verts])
        a, e = eye_angles(V, E, sx); t = t_of(a)
        near = np.linalg.norm(V - E, axis=1) < 3.0 * er
        inside = near & (t > 0) & (t < 1) & (e < up(t)) & (e > lo(t)) & (V[:, 1] < E[1])
        kill = [fc for fc in bm.faces if all(inside[v.index] for v in fc.verts)]
        # tumbuhkan 1 cincin bila sudut-sudut almond terlalu tipis untuk grid
        bmesh.ops.delete(bm, geom=kill, context='FACES')
        loose = [v for v in bm.verts if not v.link_faces]
        bmesh.ops.delete(bm, geom=loose, context='VERTS')
        bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
        bnd_e = [ed for ed in bm.edges if ed.is_boundary and np.linalg.norm(np.array(ed.verts[0].co[:]) - E) < np.linalg.norm(np.array(ed.verts[0].co[:]) - E * np.array((-1, 1, 1)))]
        bnd_v = list({v for ed in bnd_e for v in ed.verts})
        # tempel verteks tepi ke kurva almond (titik terdekat di ruang sudut), radius rim
        ts = np.linspace(0, 1, 400)
        curve = np.concatenate([np.stack([a_of(ts), up(ts)], 1), np.stack([a_of(ts[::-1]), lo(ts[::-1])], 1)])
        for v in bnd_v:
            av, ev = eye_angles(np.array([v.co[:]]), E, sx)
            k = np.argmin((curve[:, 0] - av[0]) ** 2 + (curve[:, 1] - ev[0]) ** 2)
            v.co = Vector(E + dir_from(curve[k, 0], curve[k, 1], sx) * rim_r)
        # ratakan jarak sepanjang loop tepi (hindari verteks bertumpuk), tetap di kurva
        loop = _order_loop(bnd_e)
        if loop:
            m = len(loop); ss = np.linspace(0, 1, m, endpoint=False)
            # indeks awal = verteks terdekat sudut dalam
            A0 = np.array([eye_angles(np.array([v.co[:]]), E, sx) for v in loop])[:, :, 0]
            i0 = int(np.argmin(A0[:, 0])); loop = loop[i0:] + loop[:i0]
            A0 = np.roll(A0, -i0, axis=0)
            if A0[min(2, m - 1), 1] < A0[0, 1]: loop = [loop[0]] + loop[1:][::-1]   # arah: dalam -> atas -> luar -> bawah
            L = len(curve); cs = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(curve, axis=0), axis=1))]); cs /= cs[-1]
            for v, s in zip(loop, ss):
                k = np.searchsorted(cs, s); k = min(k, L - 1)
                v.co = Vector(E + dir_from(curve[k, 0], curve[k, 1], sx) * rim_r)
        # tebal kelopak: ekstrusi tepi masuk ke arah bola mata
        ret = bmesh.ops.extrude_edge_only(bm, edges=bnd_e)
        lipv = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)]
        for v in lipv:
            d = np.array(v.co[:]) - E; v.co = Vector(E + d / np.linalg.norm(d) * lip_r)
        # relaksasi kulit sekitar mata (Laplacian) + proyeksi ulang ke SDF -> tanpa keriput/segitiga tipis
        fixed = set(bnd_v) | set(lipv)
        ring = [v for v in bm.verts if v not in fixed and np.linalg.norm(np.array(v.co[:]) - E) < 2.9 * er]
        for _ in range(24):
            new = {}
            for v in ring:
                nb = [e2.other_vert(v).co for e2 in v.link_edges]
                new[v] = sum(nb, Vector()) / len(nb)
            for v, p in new.items(): v.co = v.co * 0.5 + p * 0.5
            Pr = np.array([v.co[:] for v in ring]); Dr = Pr - C0; Dr /= np.linalg.norm(Dr, axis=1)[:, None]
            rr = _bisect(f, np.tile(C0, (len(ring), 1)), Dr, 0.004, 0.2)
            for v, p in zip(ring, C0 + Dr * rr[:, None]): v.co = Vector(p)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    return me

def _order_loop(edges):
    """Urutkan tepi menjadi loop; bila ada beberapa loop (lubang kecil tersisa di sudut), ambil yang terpanjang."""
    if not edges: return []
    adj = {}
    for ed in edges:
        a, b = ed.verts
        adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    if any(len(v) != 2 for v in adj.values()):
        print("PERINGATAN: tepi mata bercabang", sorted(len(v) for v in adj.values())[-4:])
        return []
    loops, seen = [], set()
    for start in adj:
        if start in seen: continue
        out = [start]; seen.add(start); prev = None; cur = start
        while True:
            nx = [w for w in adj[cur] if w is not prev][0]
            if nx is start: break
            out.append(nx); seen.add(nx); prev, cur = cur, nx
        loops.append(out)
    if len(loops) > 1: print("info: loop tepi mata", [len(l) for l in loops], "-> pakai terpanjang")
    return max(loops, key=len)

# ---------------- bagian wajah ----------------
def sphere_mesh(name, r, seg=32, rings=24):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    return me

def lid_mesh(name, S, sx, r, segs=36, rings=10):
    """Kelopak atas: tudung bola dengan tepi bawah mengikuti tepi atas almond (rest: tersembunyi di bawah kulit, tepi = garis mata)."""
    up, lo, a_of, t_of = almond_fns(S["almond"])
    bm = bmesh.new(); grid = []
    pole = bm.verts.new((0, 0, r))
    for j in range(segs):
        th = 2 * math.pi * j / segs
        # cari phi pertama yang masuk bukaan almond pada meridian ini (tepi kelopak)
        phis = np.radians(np.linspace(1, 150, 300))
        D = np.stack([np.sin(phis) * math.cos(th), np.sin(phis) * math.sin(th), np.cos(phis)], 1)
        a, e = eye_angles(D, np.zeros(3), sx); t = t_of(a)
        ins = (t > 0) & (t < 1) & (e < up(t)) & (e > lo(t)) & (D[:, 1] < 0)
        pe = phis[np.argmax(ins)] if ins.any() else math.radians(105)
        grid.append([bm.verts.new((r * math.sin(pe * i / rings) * math.cos(th), r * math.sin(pe * i / rings) * math.sin(th), r * math.cos(pe * i / rings))) for i in range(1, rings + 1)])
    for j in range(segs):
        k = (j + 1) % segs
        bm.faces.new((pole, grid[k][0], grid[j][0]))
        for i in range(rings - 1):
            bm.faces.new((grid[j][i], grid[k][i], grid[k][i + 1], grid[j][i + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    return me

def blink_coverage(S, sx, ang=82):
    """Porsi bukaan almond yang tertutup kelopak saat diputar 'ang' derajat (harus ~1.0)."""
    up, lo, a_of, t_of = almond_fns(S["almond"])
    ts = np.linspace(0.02, 0.98, 60); pts = []
    for t in ts:
        for e in np.linspace(lo(t), up(t), 12)[1:-1]: pts.append(dir_from(a_of(t), e, sx))
    P = np.array(pts); c, s = math.cos(math.radians(-ang)), math.sin(math.radians(-ang))
    y = P[:, 1] * c - P[:, 2] * s; z = P[:, 1] * s + P[:, 2] * c      # putar balik ke ruang kelopak istirahat
    Pr = np.stack([P[:, 0], y, z], 1)
    a, e = eye_angles(Pr, np.zeros(3), sx); t = t_of(a)
    # tertutup bila di atas tepi kelopak istirahat (= di atas almond atas pada meridian yg sama) -> uji: bukan di dalam bukaan & di atas
    ph = np.arccos(np.clip(Pr[:, 2], -1, 1)); th = np.arctan2(Pr[:, 1], Pr[:, 0])
    cov = []
    for p_, t_ in zip(ph, th):
        phis = np.radians(np.linspace(1, 150, 300))
        D = np.stack([np.sin(phis) * math.cos(t_), np.sin(phis) * math.sin(t_), np.cos(phis)], 1)
        aa, ee = eye_angles(D, np.zeros(3), sx); tt = t_of(aa)
        ins = (tt > 0) & (tt < 1) & (ee < up(tt)) & (ee > lo(tt)) & (D[:, 1] < 0)
        pe = phis[np.argmax(ins)] if ins.any() else math.radians(105)
        cov.append(p_ <= pe)
    return float(np.mean(cov))

def set_curve(o, pts):
    sp = o.data.splines[0]
    if len(sp.bezier_points) < len(pts): sp.bezier_points.add(len(pts) - len(sp.bezier_points))
    for p, bp in zip(pts, sp.bezier_points):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'

def set_taper(o, prof):
    tn = o.get("_taper"); to = OB.get(tn) if tn else None
    if not to: return
    s2 = to.data.splines[0]
    if len(s2.points) < len(prof): s2.points.add(len(prof) - len(s2.points))
    for i, (xx, yy) in enumerate(prof): s2.points[i].co = (xx, yy, 0, 1)

def ear_mesh(name, size, sx):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=14, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co
        # cekungan (concha) pada sisi luar, heliks menebal di tepi belakang-atas
        cav = max(0.0, 1 - (y * y + z * z) / 0.55) if x * sx > 0 else 0.0
        v.co = Vector((sx * abs(x) * (1 - 0.75 * cav) if x * sx > 0 else x * 0.6, y * (1 + 0.15 * max(0, y)), z * (1 + 0.08 * max(0, z))))
        v.co.x *= size[0]; v.co.y *= size[1]; v.co.z *= size[2]
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    return me

def mouth_mesh(name, S, f, mats):
    """Mulut 2D (tempel di kulit): garis bibir (cincin luar) + rongga (isi). Shape key smile/open_a/open_o."""
    M = S["mouth"]; zc, w = M["z"], M["w"]; n = 28
    def contour(t, w_, top, bot, lift, sag=0.0):
        a = 2 * math.pi * t
        x = w_ * math.cos(a)
        s = math.sin(a)
        corner = (abs(x) / w_) ** 2
        z = (top * s if s > 0 else bot * s) + lift * corner - sag * (1 - corner) * (0 if s > 0 else 1)
        return x, z
    shapes = {
        "Basis": dict(w_=w, top=0.00035, bot=0.00045, lift=0.0006),
        "smile": dict(w_=w * 1.12, top=0.0003, bot=0.0007, lift=0.0030),
        "open_a": dict(w_=w * 0.90, top=0.0018, bot=0.0085, lift=0.0008),
        "open_o": dict(w_=w * 0.52, top=0.0040, bot=0.0060, lift=0.0),
    }
    line = 0.00110                                      # tebal garis bibir
    def verts_for(sh):
        ci = [contour(i / n, **sh) for i in range(n)]
        co = []
        for i, (x, z) in enumerate(ci):            # normal 2D ke luar
            x0, z0 = ci[i - 1]; x1, z1 = ci[(i + 1) % n]
            tx, tz = x1 - x0, z1 - z0; L = math.hypot(tx, tz) or 1.0
            nx, nz = tz / L, -tx / L
            if nx * x + nz * z < 0: nx, nz = -nx, -nz
            co.append((x + nx * line, z + nz * line))
        cen = (0.0, sum(z for _, z in ci) / n)
        pts = ci + co + [cen]
        X = np.array([p[0] for p in pts]); Z = np.array([p[1] for p in pts]) + zc
        Y = surf_y(f, X, Z) - 0.0016
        return [Vector(v) for v in zip(X, Y, Z)]
    bm = bmesh.new()
    base = verts_for(shapes["Basis"]); vs = [bm.verts.new(p) for p in base]
    ri, ro, c = vs[:n], vs[n:2 * n], vs[-1]
    for i in range(n):
        j = (i + 1) % n
        f1 = bm.faces.new((ro[i], ro[j], ri[j], ri[i])); f1.material_index = 0
        f2 = bm.faces.new((ri[i], ri[j], c)); f2.material_index = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    for p in me.polygons: p.use_smooth = True
    return me, {k: verts_for(sh) for k, sh in shapes.items() if k != "Basis"}

def eye_mat_ghibli(name, iris_top, iris_bot, iris_ang=0.50):
    """Mata ala Ghibli: iris besar gelap (gradien ke bawah lebih terang), pupil samar, bayangan kelopak di atas sklera."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for nd in list(nt.nodes):
        if nd.type != 'OUTPUT_MATERIAL': nt.nodes.remove(nd)
    out = next(nd for nd in nt.nodes if nd.type == 'OUTPUT_MATERIAL')
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nv = nt.nodes.new("ShaderNodeVectorMath"); nv.operation = 'NORMALIZE'; nt.links.new(tc.outputs["Object"], nv.inputs[0])
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(nv.outputs[0], sp.inputs[0])
    neg = nt.nodes.new("ShaderNodeMath"); neg.operation = 'MULTIPLY'; neg.inputs[1].default_value = -1.0
    nt.links.new(sp.outputs["Y"], neg.inputs[0])
    def thr(ang, soft=0.012):
        n = nt.nodes.new("ShaderNodeMapRange"); n.inputs[1].default_value = math.cos(ang) - soft; n.inputs[2].default_value = math.cos(ang) + soft
        nt.links.new(neg.outputs[0], n.inputs[0]); return n.outputs[0]
    iris = thr(iris_ang); limb = thr(iris_ang - 0.06); pupil = thr(iris_ang * 0.45, 0.02)
    gz = nt.nodes.new("ShaderNodeMapRange"); gz.inputs[1].default_value = -0.45; gz.inputs[2].default_value = 0.30
    nt.links.new(sp.outputs["Z"], gz.inputs[0])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.inputs[6].default_value = (*iris_bot, 1); mix.inputs[7].default_value = (*iris_top, 1)
    nt.links.new(gz.outputs[0], mix.inputs[0])
    # sklera: putih hangat, bagian atas tertutup bayangan kelopak (biru-ungu lembut)
    sh = nt.nodes.new("ShaderNodeMapRange"); sh.inputs[1].default_value = 0.30; sh.inputs[2].default_value = 0.42
    nt.links.new(sp.outputs["Z"], sh.inputs[0])
    scl = nt.nodes.new("ShaderNodeMix"); scl.data_type = 'RGBA'; scl.inputs[6].default_value = (0.96, 0.95, 0.92, 1); scl.inputs[7].default_value = (0.82, 0.80, 0.86, 1)
    nt.links.new(sh.outputs[0], scl.inputs[0])
    c0 = nt.nodes.new("ShaderNodeMix"); c0.data_type = 'RGBA'
    nt.links.new(iris, c0.inputs[0]); nt.links.new(scl.outputs[2], c0.inputs[6]); nt.links.new(mix.outputs[2], c0.inputs[7])
    ring = nt.nodes.new("ShaderNodeMath"); ring.operation = 'SUBTRACT'; nt.links.new(iris, ring.inputs[0]); nt.links.new(limb, ring.inputs[1])
    rs = nt.nodes.new("ShaderNodeMath"); rs.operation = 'MULTIPLY'; rs.inputs[1].default_value = 0.85; nt.links.new(ring.outputs[0], rs.inputs[0])
    c1 = nt.nodes.new("ShaderNodeMix"); c1.data_type = 'RGBA'; c1.inputs[7].default_value = (0.03, 0.02, 0.02, 1)
    nt.links.new(rs.outputs[0], c1.inputs[0]); nt.links.new(c0.outputs[2], c1.inputs[6])
    ps = nt.nodes.new("ShaderNodeMath"); ps.operation = 'MULTIPLY'; ps.inputs[1].default_value = 0.75; nt.links.new(pupil, ps.inputs[0])
    c2 = nt.nodes.new("ShaderNodeMix"); c2.data_type = 'RGBA'; c2.inputs[7].default_value = (0.012, 0.008, 0.008, 1)
    nt.links.new(ps.outputs[0], c2.inputs[0]); nt.links.new(c1.outputs[2], c2.inputs[6])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 0.9
    nt.links.new(c2.outputs[2], em.inputs["Color"]); nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return m

def make_sdf_proxy(S):
    """Kepala sederhana (tanpa hidung/bibir/lekuk mata), gabungan lebih lembut -> normal bersih untuk shading toon."""
    def f(P):
        d = _ell(P, *S["cranium"])
        d = _smin(d, _ell(P, *S["face"]), 0.035)
        d = _smin(d, _ell(P, *S["jaw"]), 0.035)
        d = _smin(d, _ell(P, *S["chin"]), 0.030)
        c, r = S["cheek"]
        for sx in (1, -1): d = _smin(d, _sph(P, (sx * c[0], c[1], c[2]), r), 0.030)
        return d
    return f

def normal_proxy(H, S, n=40):
    """Data Transfer normal kustom dari proxy halus (teknik umum wajah toon): bayangan wajah bersih.
    Bobot penuh di pipi/dahi, berkurang di hidung, tepi mata, bibir agar bentuk tetap terbaca."""
    nm = H.name[:-5]
    fp = make_sdf_proxy(S)
    bm = quad_sphere(n)
    D = np.array([v.co[:] for v in bm.verts]); D /= np.linalg.norm(D, axis=1)[:, None]
    r = _bisect(fp, np.tile(C0, (len(D), 1)), D, 0.004, 0.2)
    for v, p in zip(bm.verts, C0 + D * r[:, None]): v.co = Vector(p)
    me = bpy.data.meshes.new(nm + "_HEAD_NPROXY"); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    px = OB.get(nm + "_HEAD_NPROXY")
    if px is None:
        px = bpy.data.objects.new(nm + "_HEAD_NPROXY", me)
        for c in H.users_collection: c.objects.link(px)
    else:
        old = px.data; px.data = me
        if old.users == 0: bpy.data.meshes.remove(old)
    px.parent = H; px.matrix_parent_inverse.identity(); px.location = (0, 0, 0); px.rotation_euler = (0, 0, 0); px.scale = (1, 1, 1)
    px.hide_render = True; px.hide_viewport = True
    V = np.array([v.co[:] for v in H.data.vertices])
    E0 = np.array(S["eye"]); er = S["er"]
    w = np.ones(len(V))
    w -= 0.65 * np.exp(-((V[:, 0] / 0.012) ** 2 + ((V[:, 2] + 0.018) / 0.026) ** 2)) * (V[:, 1] < -0.06)
    for sx in (1, -1):
        d = np.linalg.norm(V - E0 * np.array((sx, 1, 1)), axis=1)
        w -= 0.75 * np.clip(1 - (d - 1.05 * er) / (0.9 * er), 0, 1)
    w -= 0.45 * np.exp(-((V[:, 0] / 0.020) ** 2 + ((V[:, 2] - S["mouth"]["z"]) / 0.010) ** 2)) * (V[:, 1] < -0.06)
    w = np.clip(w, 0.0, 1.0)
    vg = H.vertex_groups.get("NTRANSFER") or H.vertex_groups.new(name="NTRANSFER")
    for i, wi in enumerate(w): vg.add([i], float(wi), 'REPLACE')
    dt = H.modifiers.get("NormalProxy") or H.modifiers.new("NormalProxy", 'DATA_TRANSFER')
    dt.object = px; dt.use_loop_data = True; dt.data_types_loops = {'CUSTOM_NORMAL'}; dt.loop_mapping = 'POLYINTERP_NEAREST'
    dt.mix_mode = 'REPLACE'; dt.mix_factor = 0.92; dt.vertex_group = "NTRANSFER"
    names = [m.name for m in H.modifiers]
    want = [nn for nn in ("Subsurf", "NormalProxy") if nn in names] + [nn for nn in names if nn not in ("Subsurf", "NormalProxy")]
    for i, nn in enumerate(want):
        with bpy.context.temp_override(object=H, active_object=H):
            bpy.ops.object.modifier_move_to_index(modifier=nn, index=i)
    return px

def _swap_mesh(o, me, keep_mats=True):
    old = o.data
    if keep_mats:
        for m in old.materials: me.materials.append(m)
    o.data = me
    if old.users == 0: bpy.data.meshes.remove(old)

def ghibli_head(nm, kind, n=40):
    S = SPEC[kind]; f = make_sdf(S)
    H = OB[nm + "_HEAD"]
    _swap_mesh(H, build_skull_mesh(nm + "_HEAD", S, f, n))
    sub = H.modifiers.get("Subsurf")
    if sub: sub.levels = 1; sub.render_levels = 2
    normal_proxy(H, S, n)
    E0 = np.array(S["eye"]); er = S["er"]
    eye_m = eye_mat_ghibli("T_Eye_Lastri" if kind == "lastri" else "T_Eye_Cust",
                           (0.05, 0.03, 0.025) if kind == "lastri" else (0.035, 0.025, 0.025),
                           (0.33, 0.18, 0.08) if kind == "lastri" else (0.25, 0.15, 0.08), S["iris"])
    cov = {}
    for side, sx in (("L", 1), ("R", -1)):
        E = Vector((sx * E0[0], E0[1], E0[2]))
        eye = OB[f"{nm}_eye_{side}"]; _swap_mesh(eye, sphere_mesh(eye.name, er), keep_mats=False); eye.data.materials.append(eye_m)
        eye.location = E
        lid = OB[f"{nm}_lid_{side}"]; _swap_mesh(lid, lid_mesh(lid.name, S, sx, er * 1.015)); lid.location = E
        th = lid.modifiers.get("Thick")
        if th: th.thickness = 0.00030; th.offset = 1.0
        cov[side] = round(blink_coverage(S, sx), 3)
        # garis mata atas (bulu mata) = tepi kelopak, menebal ke sudut luar; anak kelopak -> ikut berkedip
        up, lo, a_of, t_of = almond_fns(S["almond"])
        ts = np.linspace(0.03, 1.0, 9)
        lash = OB[f"{nm}_lash_{side}"]
        set_curve(lash, [Vector(dir_from(a_of(t), up(t) - 0.01, sx) * er * 1.085) for t in ts])
        lash.data.bevel_depth = 0.00150 if kind == "lastri" else 0.00135
        set_taper(lash, ((0, 0.30), (0.55, 0.85), (0.92, 1.0), (1.0, 0.55)))
        low = OB.get(f"{nm}_lidlow_{side}")
        if low: low.hide_render = True; low.hide_viewport = True
        # kilau: satu titik di kiri-atas iris (+ satu kecil)
        for tag, (dx, dz, sr) in (("a", (0.20 * sx, 0.30, 0.0019)), ("b", (-0.22 * sx, -0.26, 0.0008))):
            sp = OB.get(f"{nm}_sparkle{tag}_{side}")
            if not sp: continue
            d = Vector((dx, -0.92, dz)).normalized()
            _swap_mesh(sp, sphere_mesh(sp.name, sr, 10, 6))
            sp.scale = (1, 0.3, 1); sp.location = E + d * er * 1.008
            sp.rotation_euler = d.to_track_quat('Y', 'Z').to_euler()
            # kilau hilang saat kelopak menutup (sudut X kelopak > ~17 derajat), tidak melayang di atas kulit
            if sp.animation_data: sp.animation_data_clear()
            for ax, base in enumerate((1.0, 0.3, 1.0)):
                fc = sp.driver_add("scale", ax); dr = fc.driver; dr.type = 'SCRIPTED'
                for md in list(fc.modifiers): fc.modifiers.remove(md)
                v = dr.variables.new(); v.name = "a"; v.type = 'SINGLE_PROP'
                v.targets[0].id = lid; v.targets[0].data_path = "rotation_euler[0]"
                dr.expression = f"{base} if a < 0.30 else 0.0"
        # alis: titik di permukaan (+ sedikit di depan)
        bp = S["brow_pts"]; X = np.array([sx * p[0] for p in bp]); Z = np.array([E0[2] + p[1] for p in bp])
        Y = surf_y(f, X, Z) - 0.0012
        brow = OB[f"{nm}_brow_{side}"]; set_curve(brow, [Vector(v) for v in zip(X, Y, Z)])
        brow.data.bevel_depth = S["brow_r"]
        set_taper(brow, ((0, 0.75), (0.35, 1.0), (0.75, 0.75), (1.0, 0.25)))
        bl = OB.get(f"{nm}_blush_{side}")
        if bl: bl.hide_render = True; bl.hide_viewport = True
        ear = OB.get(f"{nm}_ear_{side}")
        if ear:
            c, sz = S["ear"]
            _swap_mesh(ear, ear_mesh(ear.name, sz, sx)); ear.location = (sx * c[0], c[1], c[2]); ear.rotation_euler = (math.radians(-6), 0, math.radians(-10 * sx))
    nose = OB.get(nm + "_nose")
    if nose: nose.hide_render = True; nose.hide_viewport = True          # hidung sekarang bentuk 3D di tengkorak
    # mulut: mesh baru, kunci bentuk dengan nama sama, aksi lama dipindahkan
    mo = OB[nm + "_mouth"]
    old_key = mo.data.shape_keys
    act = old_key.animation_data.action if old_key and old_key.animation_data else None
    slot = old_key.animation_data.action_slot if act else None
    mats = list(mo.data.materials)
    line_m = bpy.data.materials.get("T_MouthLine")
    if line_m is None:                     # salinan T_Lip, warna rampa digelapkan (garis mulut coklat-merah tua)
        line_m = bpy.data.materials["T_Lip"].copy(); line_m.name = "T_MouthLine"
        for nd in line_m.node_tree.nodes:
            if nd.type == 'VALTORGB':
                for el in nd.color_ramp.elements: el.color = (el.color[0] * 0.48, el.color[1] * 0.40, el.color[2] * 0.38, 1)
    mats[0] = line_m
    me, keys = mouth_mesh(mo.name, S, f, mats)
    oldme = mo.data; mo.data = me
    mo.location = (0, 0, 0); mo.rotation_euler = (0, 0, 0); mo.scale = (1, 1, 1)
    mo.shape_key_add(name="Basis")
    for k, pts in keys.items():
        kb = mo.shape_key_add(name=k)
        for i, p in enumerate(pts): kb.data[i].co = p
    if act:
        ad = me.shape_keys.animation_data_create(); ad.action = act
        try: ad.action_slot = slot
        except Exception as ex: print("slot", ex)
    if oldme.users == 0: bpy.data.meshes.remove(oldme)
    bpy.context.view_layer.update()
    print(nm, "kepala Ghibli: verts", len(H.data.vertices), "cakupan kedip", cov)
    return cov

print("35 ghibli head lib ok")
