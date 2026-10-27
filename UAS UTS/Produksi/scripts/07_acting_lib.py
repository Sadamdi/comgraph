# 07 - Pustaka akting: act(ch, f, ...) menyetel & mengunci pose lengkap; tangan target dunia/lokal; auto-condong agar tangan sampai
import bpy, math
from mathutils import Vector, Matrix, Euler

AN = bpy.app.driver_namespace["ANIM"]
Char = AN["Char"]; walk = AN["walk"]
rad = math.radians

def init_state(ch):
    ch.state = dict(
        hips=(0.0, 0.0, -0.025), hips_rot=(0, 0, 0), lean=0.0, twist=0.0, bend=0.0,
        neck=(0, 0, 0), head=(0, 0, 0), clavL=(0, 0, 0), clavR=(0, 0, 0),
        handL=None, handR=None, footL=None, footR=None, gripL="relaxed", gripR="relaxed",
        place=None)
    ch.reach_max = 0.50

def _apply_hand(ch, side, spec):
    n = f"hand_ik.{side}"
    if spec is None:
        ch.ctrl_local(n, ch.rest_pos(n)); return
    mode, pos, rot = spec
    if mode == "world": ch.ctrl_world_local_rot(n, pos, rot)
    elif mode == "frame": ch.ctrl_frame(n, pos, rot)
    else: ch.ctrl_local(n, pos, rot)

def _ctrl_world_local_rot(self, name, wpos, rot_local_deg):
    Mi = self.M().inverted()
    p = Mi @ Vector(wpos)
    R = self.rest_R[name]
    if rot_local_deg is not None:
        R = Euler([rad(a) for a in rot_local_deg], 'XYZ').to_matrix() @ R
    self.pb[name].matrix = Matrix.Translation(p) @ R.to_4x4()
Char.ctrl_world_local_rot = _ctrl_world_local_rot


# ---------- pose genggam (derajat tekuk ruas 1/2/3; + = menekuk ke arah telapak) ----------
GRIPS = {
    "open":    dict(index=(-4, 0, 0), middle=(-4, 0, 0), ring=(-4, 0, 0), pinky=(-4, 0, 0), thumb=(-6, 0, 0)),
    "flat":    dict(index=(0, 0, 0), middle=(0, 0, 0), ring=(0, 0, 0), pinky=(0, 0, 0), thumb=(4, 0, 0)),
    "relaxed": dict(index=(12, 16, 9), middle=(18, 22, 12), ring=(24, 24, 14), pinky=(30, 28, 16), thumb=(8, 8, 6)),
    "point":   dict(index=(4, 0, 0), middle=(78, 86, 56), ring=(80, 88, 58), pinky=(82, 88, 58), thumb=(22, 26, 20)),
    "pinch":   dict(index=(34, 36, 24), middle=(44, 44, 28), ring=(48, 46, 28), pinky=(52, 46, 28), thumb=(26, 30, 20)),
    "board":   dict(index=(40, 46, 30), middle=(46, 50, 32), ring=(50, 52, 32), pinky=(54, 52, 32), thumb=(30, 22, 16)),   # menjepit tepi papan: jempol depan, empat jari belakang
    "phone":   dict(index=(52, 54, 34), middle=(56, 56, 36), ring=(60, 58, 36), pinky=(62, 58, 36), thumb=(18, 24, 18)),
    "tongs":   dict(index=(52, 46, 28), middle=(56, 50, 30), ring=(62, 52, 32), pinky=(64, 52, 32), thumb=(40, 32, 22)),
    "bag":     dict(index=(46, 52, 32), middle=(52, 56, 34), ring=(58, 58, 36), pinky=(62, 58, 36), thumb=(34, 26, 18)),
    "cup":     dict(index=(14, 18, 10), middle=(16, 20, 12), ring=(18, 22, 14), pinky=(20, 24, 14), thumb=(10, 10, 8)),   # telapak menghadap atas menopang benda
    "wallet":  dict(index=(36, 40, 24), middle=(42, 44, 26), ring=(48, 46, 28), pinky=(52, 46, 28), thumb=(24, 20, 14)),
}


# regangan jari (derajat, positif = ke arah kelingking; sumbu Z lokal tulang jari). Tangan kiri berlawanan tanda. Faktor per pose: terbuka lebih renggang, menggenggam rapat.
SPREAD = dict(index=-4.0, middle=-1.0, ring=2.5, pinky=7.0, thumb=9.0)
SPREAD_F = dict(open=1.7, flat=1.3, relaxed=1.0, cup=1.0, point=0.4)
def spread_z(side, fn, f_open):
    return rad(SPREAD[fn] * f_open * (1.0 if side == "R" else -1.0))

# ---------- interval pegangan benda: (tokoh, sisi, frame_ambil, frame_lepas, pose genggam). Dipakai act() & finish_grips() ----------
HOLDS = [
    ("LASTRI", "R", 1, 104, "tongs"), ("LASTRI", "R", 2134, 2232, "tongs"), ("LASTRI", "R", 2566, 2700, "tongs"),
    ("LASTRI", "L", 120, 158, "bag"), ("LASTRI", "L", 428, 722, "bag"), ("LASTRI", "L", 2134, 2280, "bag"),
    ("MHS", "R", 2250, 2700, "bag"), ("MHS", "R", 585, 686, "cup"),
    ("MHS", "L", 700, 846, "phone"), ("MHS", "L", 1745, 1942, "phone"),
    ("LASTRI", "L", 1000, 1318, "phone"), ("LASTRI", "L", 1966, 2114, "phone"),
    ("LASTRI", "L", 1321, 1405, "board"),
]
PRE, POST = 12, 10
def grip_for(nm, side, f):
    """Pose genggam otomatis pada frame f: membuka sebelum menyentuh, menggenggam selama memegang, membuka setelah melepas."""
    for n, sd, a, b, g in HOLDS:
        if n != nm or sd != side: continue
        if a <= f <= b: return g
        if a - PRE <= f < a or b < f <= b + POST: return "open"
    return None

def finish_grips():
    """Kunci jari tepat di batas tiap interval pegangan (membuka -> menggenggam -> menggenggam -> membuka) agar transisi tidak melambat."""
    chars = {"LASTRI": bpy.app.driver_namespace["L"], "MHS": bpy.app.driver_namespace["M"]}
    for n, side, a, b, g in HOLDS:
        ch = chars[n]
        for fr, pose in ((a - PRE, "open"), (a, g), (b, g), (b + POST, "open")):
            if fr < 1: continue
            gg = GRIPS[pose]
            for fn in ("index", "middle", "ring", "pinky", "thumb"):
                for i in range(3):
                    pbn = ch.pb[f"{fn}{i + 1}.{side}"]
                    pbn.rotation_euler = Euler((rad(gg[fn][i]), 0, spread_z(side, fn, SPREAD_F.get(pose, 0.25)) if i == 0 else 0.0), 'XYZ'); pbn.keyframe_insert("rotation_euler", frame=fr)

def apply_grip(ch):
    for side in ("L", "R"):
        g = ch.state.get("grip" + side, "relaxed")
        name, amt = (g if isinstance(g, tuple) else (g, 1.0))
        pose = GRIPS[name]
        rel = GRIPS["relaxed"]
        for fn in ("index", "middle", "ring", "pinky", "thumb"):
            for i in range(3):
                a = rel[fn][i] + (pose[fn][i] - rel[fn][i]) * amt
                ch.pb[f"{fn}{i + 1}.{side}"].rotation_euler = Euler((rad(a), 0, spread_z(side, fn, SPREAD_F.get("relaxed", 1.0) + (SPREAD_F.get(name, 0.25) - SPREAD_F.get("relaxed", 1.0)) * amt) if i == 0 else 0.0), 'XYZ')
Char.apply_grip = apply_grip


def _ctrl_frame(self, name, wpos, dirs):
    """Pasang kontrol tangan: pergelangan di wpos (dunia); arah jari = dirs[0], arah telapak (arah jari menekuk) = dirs[1] (dunia).
    Memakai sumbu lokal kontrol saat istirahat: jari = sumbu Y lokal; telapak = (-sx,0,0) ruang armature saat istirahat."""
    Mi = self.M().inverted(); R3 = Mi.to_3x3()
    fd = (R3 @ Vector(dirs[0])).normalized()
    pd = (R3 @ Vector(dirs[1])); pd = (pd - fd * pd.dot(fd)).normalized()
    sx = 1.0 if name.endswith(".L") else -1.0
    Rr = self.rest_R[name]                                 # kolom = sumbu lokal tulang saat istirahat (di ruang armature)
    fa = Vector((0.0, 1.0, 0.0))                           # arah jari dalam koordinat lokal tulang
    pa = (Rr.inverted() @ Vector((-sx, 0.0, 0.0)))         # arah telapak dalam koordinat lokal tulang
    pa = (pa - fa * pa.dot(fa)).normalized()
    Floc = Matrix(((fa.x, pa.x, fa.cross(pa).x), (fa.y, pa.y, fa.cross(pa).y), (fa.z, pa.z, fa.cross(pa).z)))
    xt = fd.cross(pd)
    Ftgt = Matrix(((fd.x, pd.x, xt.x), (fd.y, pd.y, xt.y), (fd.z, pd.z, xt.z)))
    O = Ftgt @ Floc.inverted()
    self.pb[name].matrix = Matrix.Translation(Mi @ Vector(wpos)) @ O.to_4x4()
Char.ctrl_frame = _ctrl_frame

def G(point, fdir, pdir, back=0.075, lift=0.0):
    """Spesifikasi genggam: titik yang digenggam (dunia), arah jari, arah telapak. Pergelangan diletakkan mundur sepanjang jari."""
    f = Vector(fdir).normalized(); p = Vector(pdir).normalized()
    wrist = Vector(point) - f * back - p * lift
    return ("frame", tuple(wrist), (tuple(f), tuple(p)))


# ---------- genggaman benda: dari POSISI BENDA yang diinginkan -> pose tangan (titik genggam, arah jari, arah telapak) ----------
#   nama: (titik genggam lokal, arah jari lokal, arah telapak lokal, back, lift, skala benda)
PROP_GRIPS = {
    "bag_back":  ((-0.09, 0.072, 0.012), (0, 0, -1), (0, -1, 0), 0.095, 0.02, 0.9),    # jepit tepi lipatan kantong dari belakang (jari di sisi luar)
    "bag_front": ((0.09, -0.072, 0.012), (0, 0, -1), (0, 1, 0), 0.095, 0.02, 0.9),     # jepit tepi dari depan
    "wallet":    ((0.0, -0.03, -0.015), (0, 1, 0), (0, 0, 1), 0.045, 0.012, 0.85),     # telapak menopang lembar bawah dompet (telapak menghadap atas)
}
def Hold(kind, center, yaw_deg=0.0):
    gp, fp, pp, back, lift, sc_ = PROP_GRIPS[kind]
    Rz = Euler((0, 0, rad(yaw_deg)), 'XYZ').to_matrix()
    g = Rz @ (Vector(gp) * sc_); fd = Rz @ Vector(fp); pd = Rz @ Vector(pp)
    return G(Vector(center) + g, fd, pd, back=back, lift=lift)

def apply_state(ch):
    s = ch.state
    if s["place"] is not None:
        ch.place(*s["place"])
    ch.hips_move(*s["hips"])
    ch.fk("hips", s["hips_rot"][0], s["hips_rot"][1], s["hips_rot"][2])
    lean = s["lean"]
    ch.fk("spine", lean * 0.425 + s["hips_rot"][0] * 0, s["twist"] * 0.5, s["bend"] * 0.5)
    ch.fk("chest", lean * 0.425, s["twist"] * 0.5, s["bend"] * 0.5)
    ch.fk("neck", s["neck"][0] + lean * 0.0, s["neck"][1], s["neck"][2])
    ch.fk("head", s["head"][0] - lean * 0.20, s["head"][1], s["head"][2])
    ch.fk("clavicle.L", *s["clavL"]); ch.fk("clavicle.R", *s["clavR"])
    ch.pb["hips"].rotation_euler = Euler((rad(lean * 0.15 + s["hips_rot"][0]), rad(s["hips_rot"][1]), rad(s["hips_rot"][2])), 'XYZ')
    _apply_hand(ch, "L", s["handL"]); _apply_hand(ch, "R", s["handR"])
    ch.apply_grip()
    for side in ("L", "R"):
        n = f"foot_ik.{side}"; spec = s["foot" + side]
        if spec is None: ch.ctrl_local(n, ch.rest_pos(n))
        else: ch.ctrl_local(n, spec[0], spec[1])

POLE_HANG = {"L": 70.0, "R": 110.0}
POLE_REACH = {"L": 120.0, "R": 60.0}

SLAB_LO = Vector((-1.62, -0.40, 1.04)); SLAB_HI = Vector((1.62, 0.36, 1.30))
BASE_LO = Vector((-1.50, -0.30, 0.0)); BASE_HI = Vector((1.50, 0.36, 1.30))

def _seg_box(p0, p1, lo=SLAB_LO, hi=SLAB_HI):
    d = p1 - p0; tmin, tmax = 0.0, 1.0
    for i in range(3):
        if abs(d[i]) < 1e-9:
            if p0[i] < lo[i] or p0[i] > hi[i]: return None
        else:
            t1 = (lo[i] - p0[i]) / d[i]; t2 = (hi[i] - p0[i]) / d[i]
            if t1 > t2: t1, t2 = t2, t1
            tmin = max(tmin, t1); tmax = min(tmax, t2)
            if tmin > tmax: return None
    return tmin, tmax

def _elbow_score(ch, side, e_w, sh_w):
    """Skor posisi siku: tinggi + keluar (baik); di dalam papan meja / di dalam badan (buruk)."""
    Mi = ch.M().inverted()
    e = Mi @ e_w; sh = Mi @ sh_w
    sgn = 1.0 if side == "L" else -1.0
    outward = max(-0.1, min(0.18, (e.x - sh.x) * sgn))
    sc_ = -abs(e_w.z - (sh_w.z - 0.03)) * 1.6 + 0.9 * outward
    sc_ -= 9.0 * max(0.0, e_w.z - sh_w.z - 0.02)             # siku di atas bahu = "sayap ayam": hampir tak pernah alami
    if _seg_box(e_w, e_w + Vector((0, 0, 1e-6)), SLAB_LO - Vector((0.03, 0.03, 0.03)), SLAB_HI) is not None: sc_ -= 10.0
    if abs(e.x) < 0.13 and -0.14 < e.y < 0.14 and e.z > 0.8: sc_ -= 5.0
    return sc_

def _set_pole(ch, f):
    s = ch.state
    if not hasattr(ch, "pole_prev"): ch.pole_prev = dict(POLE_HANG)
    for side in ("L", "R"):
        spec = s["hand" + side]
        ik = [c for c in ch.pb[f"forearm.{side}"].constraints if c.type == 'IK'][0]
        if spec is None:
            ang = POLE_HANG[side]
        else:
            mode, pos, rot = spec
            wz = Vector(pos).z if mode in ("world", "frame") else (ch.M() @ Vector(pos)).z
            w = max(0.0, min(1.0, (wz - 0.95) / 0.20))
            if w <= 0.0:
                ang = POLE_HANG[side]
            else:
                best = (-1e9, POLE_REACH[side]); sh_w = ch.rig.matrix_world @ ch.pb[f"upper_arm.{side}"].head
                prev = ch.pole_prev[side]
                for a_ in range(-180, 181, 20):
                    ik.pole_angle = rad(a_); bpy.context.view_layer.update()
                    e_w = ch.rig.matrix_world @ ch.pb[f"forearm.{side}"].head
                    mw_ = ch.rig.matrix_world; fa_ = (mw_ @ ch.pb[f"forearm.{side}"].tail - e_w).normalized()
                    ha_ = (mw_ @ ch.pb[f"hand.{side}"].tail - mw_ @ ch.pb[f"hand.{side}"].head).normalized()
                    bend = math.degrees(fa_.angle(ha_))                      # sudut tekuk pergelangan: manusia nyata <~45 derajat
                    sc_ = _elbow_score(ch, side, e_w, sh_w) - 0.0012 * min(abs(a_ - prev), 360 - abs(a_ - prev)) - 0.06 * max(0.0, bend - 25.0)
                    if sc_ > best[0]: best = (sc_, a_)
                ang = POLE_HANG[side] * (1 - w) + best[1] * w
        ch.pole_prev[side] = ang
        ik.pole_angle = rad(ang)
        ik.keyframe_insert("pole_angle", frame=f)
        _limit_wrist(ch, side, f)

WRIST_MAX = 42.0
def _limit_wrist(ch, side, f, tmax=WRIST_MAX):
    """Batasi tekuk pergelangan (sudut jari-vs-lengan bawah) <= tmax derajat: putar orientasi hand_ik mendekati arah lengan bawah."""
    from mathutils import Quaternion
    bpy.context.view_layer.update()
    mw = ch.rig.matrix_world; pb_h = ch.pb[f"hand_ik.{side}"]
    fa = (mw @ ch.pb[f"forearm.{side}"].tail - mw @ ch.pb[f"forearm.{side}"].head).normalized()
    W = mw @ pb_h.matrix; d0 = (W.to_3x3() @ Vector((0, 1, 0))).normalized()
    if d0.angle(fa) <= rad(tmax) + 1e-4: return
    ax = fa.cross(d0)
    if ax.length < 1e-6: return
    d1 = Quaternion(ax.normalized(), rad(tmax)) @ fa
    W3 = d0.rotation_difference(d1).to_matrix() @ W.to_3x3()
    Wn = W3.to_4x4(); Wn.translation = W.translation
    pb_h.matrix = mw.inverted() @ Wn
    bpy.context.view_layer.update()
    pb_h.keyframe_insert("rotation_euler", frame=f); pb_h.keyframe_insert("location", frame=f)

def _reach_ok(ch):
    """True bila semua target tangan (dunia/lokal) berada dalam jangkauan lengan dari bahunya."""
    s = ch.state
    bpy.context.view_layer.update()
    for side in ("L", "R"):
        spec = s["hand" + side]
        if spec is None: continue
        mode, pos, rot = spec
        w = Vector(pos) if mode in ("world", "frame") else ch.M() @ Vector(pos)
        sh = ch.rig.matrix_world @ ch.pb[f"upper_arm.{side}"].head
        if (w - sh).length > ch.reach_max: return False
    return True

def _hand_world(ch, side, spec):
    if spec is None: return ch.M() @ ch.rest_pos(f"hand_ik.{side}")
    mode, pos, rot = spec
    return Vector(pos) if mode in ("world", "frame") else ch.M() @ Vector(pos)

def act(ch, f, key=True, auto_lean=True, _wp=False, **kw):
    """Parameter: hips=(dx,dy,dz) hips_rot=(p,t,b) lean twist bend neck head clavL clavR
       handL/handR=('world'|'local', pos, rot_local_deg|None) atau None=lepas ke posisi istirahat
       footL/footR=(pos_local, rot) place=(loc, yaw_deg) gaze=(x,y,z) brow=(raise,tilt) mouth=(smile,a,o)"""
    s = ch.state
    if not hasattr(ch, "last_hand"): ch.last_hand = {}
    if not _wp:
        for side in ("L", "R"):
            kk = "hand" + side
            if kk not in kw: continue
            p1 = _hand_world(ch, side, kw[kk])
            prev = ch.last_hand.get(side)
            if prev is not None and prev[0] < f and kw[kk] is not None:
                p0 = prev[1]
                hit = _seg_box(p0, p1, BASE_LO, BASE_HI)
                if hit is not None and hit[1] > 0.02 and hit[0] < 0.98 and (f - prev[0]) <= 220:
                    # angkat tangan dulu di sisi asalnya (belakang/depan meja), baru bergerak melewati permukaan meja
                    wp = Vector((p0.x + (p1.x - p0.x) * 0.15, p0.y + (p1.y - p0.y) * 0.10, 1.40))
                    fm = int(round(prev[0] + (f - prev[0]) * 0.40))
                    if prev[0] < fm < f:
                        mode, pos, rot = kw[kk]
                        _apply_hand(ch, side, ("world", tuple(wp), rot) if mode != "frame" else ("frame", tuple(wp), rot))
                        nm_ = f"hand_ik.{side}"
                        ch.pb[nm_].keyframe_insert("location", frame=fm); ch.pb[nm_].keyframe_insert("rotation_euler", frame=fm)
                        ik = [c for c in ch.pb[f"forearm.{side}"].constraints if c.type == 'IK'][0]
                        ik.pole_angle = rad(POLE_REACH[side]); ik.keyframe_insert("pole_angle", frame=fm)
            ch.last_hand[side] = (f, p1)
    for side in ("L", "R"):
        gk = "grip" + side
        if gk in kw: continue
        g = grip_for(ch.nm, side, f)
        if g is not None: s[gk] = g; s["_h" + side] = True
        elif s.get("_h" + side): s[gk] = "relaxed"; s["_h" + side] = False
    for side in ("L", "R"):
        kk = "hand" + side
        if kk in kw and kw[kk] is not None and kw[kk][0] == "world" and grip_for(ch.nm, side, f) == "bag":
            c = Vector(kw[kk][1]) - Vector((0, 0, 0.13))           # pusat kantong = 13 cm di bawah target tangan lama
            kw[kk] = Hold("bag_back" if ch.nm == "LASTRI" else "bag_front", c)
    for k, v in kw.items():
        if k in ("gaze", "brow", "mouth"): continue
        if k == "hand": continue
        s[k] = v
    if "lean" in kw: s["lean_base"] = kw["lean"]
    base = s.get("lean_base", 0.0)
    s["lean"] = base
    apply_state(ch)
    if auto_lean and (s["handL"] or s["handR"]):
        L = base
        for _ in range(16):
            if _reach_ok(ch): break
            L += 3.0
            if L > 32: break
            s["lean"] = L; apply_state(ch)
    if "gaze" in kw and ch.gaze is not None: ch.look_at(f, kw["gaze"])
    if "brow" in kw: ch.brow(f, *kw["brow"])
    if "mouth" in kw: ch.mouth_key(f, *kw["mouth"])
    if key:
        ch.key(f); _set_pole(ch, f)

def hold_interp(ch, f_from, f_to):
    pass

def clear_anim(*objs):
    for o in objs:
        if o is None: continue
        if o.animation_data: o.animation_data_clear()
        if o.type == 'ARMATURE':
            for pb in o.pose.bones: pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
    for nm in ("hips",):
        pass

print("acting lib ok")
