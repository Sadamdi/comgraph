# 06 - Inti animasi: kelas Char (pose IK/FK, kunci), siklus jalan prosedural (langkah terencana), kedip, pandangan, mulut
import bpy, math, random
from mathutils import Vector, Matrix, Euler

OB = bpy.data.objects
SC = bpy.context.scene
rad = math.radians
FINGERS = [f"{f}{i}.{s}" for s in ("L", "R") for f in ("index", "middle", "ring", "pinky", "thumb") for i in (1, 2, 3)]
KEYED = ["hips", "spine", "chest", "neck", "head", "clavicle.L", "clavicle.R", "hand_ik.L", "hand_ik.R", "foot_ik.L", "foot_ik.R"] + FINGERS

def ease(u):                       # smoothstep
    u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)

class Char:
    def __init__(self, nm):
        self.nm = nm; self.rig = OB["RIG_" + nm]; self.pb = self.rig.pose.bones
        for b in self.pb: b.rotation_mode = 'XYZ'
        self.rest_M = {b.name: b.matrix_local.copy() for b in self.rig.data.bones}
        self.rest_R = {n: m.to_3x3() for n, m in self.rest_M.items()}
        self.rest_h = {n: m.translation.copy() for n, m in self.rest_M.items()}
        self.eyes = {s: OB[f"{nm}_eye_{s}"] for s in ("L", "R")}
        self.lids = {s: OB[f"{nm}_lid_{s}"] for s in ("L", "R")}
        self.mouth = OB[f"{nm}_mouth"]
        self.brows = {s: OB[f"{nm}_brow_{s}"] for s in ("L", "R")}
        self.rig_loc = Vector(self.rig.location); self.rig_yaw = self.rig.rotation_euler[2]
        self.gaze = None

    # ---------- transform objek rig (jalur) ----------
    def place(self, loc, yaw_deg):
        self.rig.location = Vector(loc); self.rig.rotation_euler = (0, 0, rad(yaw_deg))
        self.rig_loc = Vector(loc); self.rig_yaw = rad(yaw_deg)

    def M(self):
        return Matrix.Translation(self.rig_loc) @ Euler((0, 0, self.rig_yaw), 'XYZ').to_matrix().to_4x4()

    # ---------- kontrol IK (koordinat lokal rig = ruang armature) ----------
    def ctrl_local(self, name, pos, rot_deg=None):
        R = self.rest_R[name]
        if rot_deg is not None:
            R = Euler([rad(a) for a in rot_deg], 'XYZ').to_matrix() @ R
        self.pb[name].matrix = Matrix.Translation(Vector(pos)) @ R.to_4x4()

    def ctrl_world(self, name, wpos, rot_world_deg=None):
        Mi = self.M().inverted()
        p = Mi @ Vector(wpos)
        R = self.rest_R[name]
        if rot_world_deg is not None:
            Rw = Euler([rad(a) for a in rot_world_deg], 'XYZ').to_matrix()
            R = (Mi.to_3x3() @ Rw) @ R
        self.pb[name].matrix = Matrix.Translation(p) @ R.to_4x4()

    def rest_pos(self, name):
        return self.rest_h[name].copy()

    # ---------- FK ----------
    def fk(self, name, pitch=0.0, twist=0.0, bend=0.0):
        """pitch + = maju, twist + = menoleh/putar ke kiri karakter, bend + = miring ke -X."""
        self.pb[name].rotation_euler = Euler((rad(pitch), rad(twist), rad(bend)), 'XYZ')

    def hips_move(self, dx=0.0, dy=0.0, dz=0.0):
        self.pb["hips"].location = Vector((dx, dz, -dy))      # sumbu lokal: X, Y=atas, Z=-Y dunia

    # ---------- kunci ----------
    def key(self, f, rig_obj=True):
        for n in KEYED:
            self.pb[n].keyframe_insert("location", frame=f)
            self.pb[n].keyframe_insert("rotation_euler", frame=f)
        if rig_obj:
            self.rig.keyframe_insert("location", frame=f)
            self.rig.keyframe_insert("rotation_euler", frame=f)

    def reset_pose(self):
        for n in KEYED:
            self.pb[n].location = (0, 0, 0); self.pb[n].rotation_euler = (0, 0, 0)
        for s in ("L", "R"):
            self.ctrl_local(f"hand_ik.{s}", self.rest_pos(f"hand_ik.{s}"))
            self.ctrl_local(f"foot_ik.{s}", self.rest_pos(f"foot_ik.{s}"))

    # ---------- wajah ----------
    def blink(self, f, dur=5):
        for s in ("L", "R"):
            lid = self.lids[s]
            for ff, v in ((f - 1, 0), (f + 1, 82), (f + 2, 82), (f + dur, 0)):
                lid.rotation_euler[0] = rad(v); lid.keyframe_insert("rotation_euler", index=0, frame=ff)

    def auto_blink(self, f0, f1, seed=1):
        r = random.Random(seed + hash(self.nm) % 100); f = f0 + r.randint(20, 70)
        while f < f1 - 6:
            self.blink(f); f += r.randint(60, 140)

    def mouth_key(self, f, smile=0.0, a=0.0, o=0.0):
        sk = self.mouth.data.shape_keys.key_blocks
        for k, v in (("smile", smile), ("open_a", a), ("open_o", o)):
            sk[k].value = v; sk[k].keyframe_insert("value", frame=f)

    def talk(self, f0, f1, smile=0.2, seed=3, gap=4):
        """Gerak mulut (lip-flap) selama f0..f1; berakhir tersenyum ringan."""
        r = random.Random(seed + f0)
        f = f0
        self.mouth_key(f0 - 2, smile, 0, 0)
        while f < f1:
            kind = r.random()
            if kind < 0.6: self.mouth_key(f, smile * 0.6, r.uniform(0.4, 0.95), 0)
            elif kind < 0.85: self.mouth_key(f, smile * 0.4, 0.1, r.uniform(0.4, 0.8))
            else: self.mouth_key(f, smile, 0.05, 0)
            f += gap + r.randint(0, 2)
        self.mouth_key(f1 + 3, smile, 0, 0)

    def look_at(self, f, target):
        """Kunci posisi target pandangan (dunia)."""
        t = self.gaze
        t.location = Vector(target); t.keyframe_insert("location", frame=f)

    def brow(self, f, raise_=0.0, tilt=0.0):
        """raise_ (m) mengangkat alis; tilt (derajat) memiringkan (sedih +)."""
        for s, sg in (("L", 1), ("R", -1)):
            b = self.brows[s]
            b.location = (0, 0, raise_); b.rotation_euler = (0, 0, rad(tilt * sg)); b.keyframe_insert("location", frame=f); b.keyframe_insert("rotation_euler", frame=f)

def setup_gaze(ch, keep=False):
    """Satu target pandangan per karakter; kedua bola mata Damped Track ke sana."""
    e = bpy.data.objects.get(f"LOOK_{ch.nm}")
    if e is None:
        e = bpy.data.objects.new(f"LOOK_{ch.nm}", None); e.empty_display_type = 'SPHERE'; e.empty_display_size = 0.04
        bpy.data.collections["20_TOKOH"].objects.link(e)
    if not keep:
        if e.animation_data: e.animation_data_clear()
        e.location = (0, -6, 1.5)
    for s in ("L", "R"):
        for c in list(ch.eyes[s].constraints): ch.eyes[s].constraints.remove(c)
        c = ch.eyes[s].constraints.new('DAMPED_TRACK'); c.target = e; c.track_axis = 'TRACK_NEGATIVE_Y'
    ch.gaze = e
    return e

# =====================================================================
#  Siklus jalan prosedural: langkah kaki terencana (tanpa foot sliding)
# =====================================================================
def walk(ch, f0, start, end, T=15, n=7, lift=0.085, arm_swing=0.16, sway=0.022, bob=0.028, hold=12, step_w=0.095, yaw_deg=None, via=None):
    """Jalan sepanjang jalur start -> via... -> end (XY dunia). f0 = frame langkah pertama; mengembalikan frame terakhir (kaki rapat).
    Langkah k dilakukan kaki (k%2): pindah dari penempatan sebelumnya ke tujuan selama T frame; pelvis di titik tengah kedua kaki.
    Arah hadap mengikuti garis singgung jalur (dihaluskan) kecuali yaw_deg diberikan."""
    pts = [Vector((start[0], start[1], 0))] + [Vector((v[0], v[1], 0)) for v in (via or [])] + [Vector((end[0], end[1], 0))]
    seg = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    cum = [0.0]
    for l in seg: cum.append(cum[-1] + l)
    D = cum[-1]

    def pos_at(s):
        s = max(0.0, min(D, s))
        for i in range(len(seg)):
            if s <= cum[i + 1] + 1e-9:
                u = (s - cum[i]) / max(seg[i], 1e-9)
                return pts[i] + (pts[i + 1] - pts[i]) * u
        return pts[-1].copy()

    def heading_at(s):
        a_ = pos_at(s - 0.25); b_ = pos_at(s + 0.25)
        d_ = b_ - a_
        if d_.length < 1e-6: d_ = pts[1] - pts[0]
        return math.degrees(math.atan2(d_.x, -d_.y))

    sl = D / n
    pos_after = [(k + 1) * sl for k in range(n)] + [n * sl]
    total = n + 1
    last = f0 + total * T + hold
    ref_yaw = [None]

    def smooth(u): return u * u * (3 - 2 * u)

    def foot_state(side_idx, t):
        pos = 0.0
        for k in range(total):
            if k % 2 != side_idx: continue
            t0 = f0 + k * T; tgt = pos_after[k]
            if t < t0: return pos, 0.0, 0.0
            if t <= t0 + T:
                u = (t - t0) / T
                s_ = pos + (tgt - pos) * smooth(u)
                z_ = lift * math.sin(math.pi * u) ** 1.2
                pit = (24 * (1 - smooth(min(u * 2.0, 1.0))) if u < 0.5 else 0.0) - (14 * smooth(max((u - 0.55) / 0.45, 0.0)) * (1 - u) * 1.6)
                return s_, z_, pit
            pos = tgt
        return pos, 0.0, 0.0

    for fr in range(f0 - 1, last + 1):
        t = float(fr)
        sL, zL, pL = foot_state(0, t); sR, zR, pR = foot_state(1, t)
        s_root = 0.5 * (sL + sR)
        loc = pos_at(s_root)
        yw = heading_at(s_root) if yaw_deg is None else yaw_deg
        # buka lipatan sudut agar kontinu terhadap frame sebelumnya
        if ref_yaw[0] is not None:
            while yw - ref_yaw[0] > 180: yw -= 360
            while yw - ref_yaw[0] < -180: yw += 360
        ref_yaw[0] = yw
        ch.place((loc.x, loc.y, 0), yw)
        in_walk = f0 <= t <= f0 + total * T
        if in_walk:
            k = min(int((t - f0) // T), total - 1); u = (t - (f0 + k * T)) / T
            swing_side = k % 2
        else:
            k, u, swing_side = 0, 0.0, 0
        amp = 1.0 if in_walk else 0.0
        bz = -0.05 + bob * math.sin(math.pi * u) * amp
        sw = sway * math.sin(math.pi * u) * amp * (-1 if swing_side == 0 else 1)
        ch.hips_move(sw, 0, bz)
        tw = 7 * math.sin(math.pi * u) * amp * (1 if swing_side == 0 else -1)
        ch.fk("hips", 0, tw, 0)
        ch.fk("spine", 3 * amp, -tw * 0.8, 0)
        ch.fk("chest", 1.5 * amp, -tw * 0.9, 0)
        ch.fk("head", -2 * amp, tw * 0.5, 0)
        for side, s_f, z_f, pit in (("L", sL, zL, pL), ("R", sR, zR, pR)):
            xo = (1 if side == "L" else -1) * step_w
            rp = ch.rest_pos(f"foot_ik.{side}")
            z_adj = z_f + 0.12 * math.sin(math.radians(max(pit, 0.0))) + 0.05 * math.sin(math.radians(max(-pit, 0.0)))   # engsel di ujung jari / tumit agar tidak menembus tanah
            ch.ctrl_local(f"foot_ik.{side}", (xo, -(s_f - s_root), rp.z + z_adj), (pit, 0, 0))
        for side in ("L", "R"):
            opp = (sR - s_root) if side == "L" else (sL - s_root)
            rp = ch.rest_pos(f"hand_ik.{side}")
            sw_a = opp * (arm_swing / max(sl * 0.5, 1e-3)) * (1.0 if in_walk else 0.0)
            ch.ctrl_local(f"hand_ik.{side}", (rp.x, rp.y - sw_a * 0.9, rp.z + 0.05 * abs(sw_a) * 1.5), (0, 0, 0))
        ch.key(fr)
        for side, a_ in (("L", 70.0), ("R", 110.0)):
            ik = [c for c in ch.pb[f"forearm.{side}"].constraints if c.type == 'IK'][0]
            ik.pole_angle = math.radians(a_); ik.keyframe_insert("pole_angle", frame=fr)
    ch.last_hand = {}
    return last

# util antar-modul
bpy.app.driver_namespace["ANIM"] = {"Char": Char, "walk": walk, "setup_gaze": setup_gaze, "ease": ease}
print("anim core ok")
