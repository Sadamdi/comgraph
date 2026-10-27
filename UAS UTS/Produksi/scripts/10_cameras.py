# 10 - Kamera fisik per shot (bound ke marker S01-S14): posisi/target/lensa berkunci, DOF (fokus ke target), dolly halus
import bpy, math
from mathutils import Vector

OB = bpy.data.objects
SC = bpy.context.scene
C_CAM = bpy.data.collections.get("05_CAMERAS") or SC.collection

def cam(name, keys, fstop=4.0, focus_off=(0, 0, 0)):
    """keys = [(frame, pos, target, lens), ...]. Interpolasi Bezier (ease in/out) di antara kunci."""
    c = OB[name]
    for k in list(c.constraints): c.constraints.remove(k)
    if c.animation_data: c.animation_data_clear()
    if c.data.animation_data: c.data.animation_data_clear()
    tn = "TGT_" + name
    t = OB.get(tn)
    if t is None:
        t = bpy.data.objects.new(tn, None); t.empty_display_type = 'PLAIN_AXES'; t.empty_display_size = 0.08
        C_CAM.objects.link(t)
    if t.animation_data: t.animation_data_clear()
    con = c.constraints.new('TRACK_TO'); con.target = t; con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'
    for (f, p, tg, lens) in keys:
        c.location = Vector(p); c.keyframe_insert("location", frame=f)
        t.location = Vector(tg) + Vector(focus_off); t.keyframe_insert("location", frame=f)
        c.data.lens = lens; c.data.keyframe_insert("lens", frame=f)
    d = c.data
    d.sensor_fit = 'AUTO'; d.clip_start = 0.05; d.clip_end = 200
    d.dof.use_dof = True; d.dof.focus_object = t; d.dof.aperture_fstop = fstop
    try:
        d.dof.aperture_blades = 6
    except Exception: pass
    # FOV vertikal (derajat) untuk laporan
    c["fov_v_deg"] = round(math.degrees(2 * math.atan(18.0 / keys[0][3])), 1)
    c["lens_mm"] = keys[0][3]

def build():
    # --- S01 establishing: dolly-in pelan, menunjukkan warung & lingkungan, lalu Bu Lastri ---
    cam("S01_CAM", [(1, (5.2, -9.0, 2.7), (-0.4, 0.2, 1.7), 22), (120, (3.4, -6.0, 2.1), (-0.3, 0.3, 1.55), 26), (240, (1.35, -2.7, 1.8), (-0.35, 0.45, 1.36), 34)], fstop=8.0)
    # --- S02 wide: pelanggan masuk dari kanan ---
    cam("S02_CAM", [(241, (1.8, -6.2, 1.5), (0.1, 0.1, 1.25), 24), (390, (0.9, -4.3, 1.35), (0.25, 0.15, 1.2), 26)], fstop=8.0)
    # --- S03 two-shot depan 3/4 ---
    cam("S03_CAM", [(391, (-2.3, -2.9, 1.65), (-0.02, 0.05, 1.40), 30), (540, (-2.1, -2.6, 1.65), (-0.02, 0.05, 1.40), 32)], fstop=4.0)
    # --- S04 insert dompet (close-up tangan) ---
    # S04: close-up dompet & tangan; kamera dari depan-kiri pelanggan sehingga tangan, dompet, dan sebagian wajah terbaca (target = posisi dompet sebenarnya)
    exec(open(SD + "08a_scenes.py", encoding="utf8").read().split("# ============================================================== S01")[0], globals())
    wp = Mrel(0.17, 0.08, 1.30); c1 = wp + FACE * 0.85 - RIGHT * 0.55 + Vector((0, 0, 0.20)); c2 = wp + FACE * 0.78 - RIGHT * 0.50 + Vector((0, 0, 0.16))   # reverse-shot dari sisi warung: wajah, tangan, dompet
    cam("S04_CAM", [(541, tuple(c1), tuple(wp + Vector((0, 0, 0.04))), 50), (660, tuple(c2), tuple(wp + Vector((0, 0, 0.02))), 56)], fstop=2.8)
    # --- S05 two-shot lebih rapat ---
    cam("S05_CAM", [(661, (-2.2, -2.7, 1.62), (-0.02, 0.05, 1.40), 32), (840, (-1.95, -2.35, 1.62), (-0.02, 0.05, 1.40), 36)], fstop=4.0)
    # --- S06 medium-wide, ikut M keluar kanan lalu tinggal di Bu Lastri ---
    cam("S06_CAM", [(841, (2.3, -4.0, 1.7), (0.2, 0.0, 1.35), 30), (960, (2.2, -3.9, 1.7), (1.0, 0.0, 1.3), 30), (1080, (0.6, -2.6, 1.6), (-0.55, 0.55, 1.35), 40)], fstop=5.6)
    # --- S07 over-the-shoulder Bu Lastri ---
    cam("S07_CAM", [(1081, (0.25, 1.65, 1.78), (-0.4, 0.2, 1.32), 55), (1320, (0.15, 1.5, 1.74), (-0.38, 0.22, 1.32), 60)], fstop=2.8)
    # --- S08 close-up papan QRIS ---
    cam("S08_CAM", [(1321, (0.70, -0.95, 1.66), (-0.05, 0.04, 1.52), 52), (1500, (0.65, -0.90, 1.62), (-0.05, 0.04, 1.50), 56)], fstop=2.8)
    # --- S09 medium-wide kembali ---
    cam("S09_CAM", [(1501, (0.5, -4.4, 1.25), (0.35, 0.2, 1.12), 24), (1740, (-1.9, -2.9, 1.65), (-0.02, 0.05, 1.40), 32)], fstop=5.6)
    # --- S10 over-the-shoulder pelanggan (scan) ---
    cam("S10_CAM", [(1741, (1.01, -1.13, 1.85), (-0.05, 0.04, 1.46), 40), (1950, (0.96, -1.06, 1.82), (-0.05, 0.04, 1.46), 46)], fstop=2.8)
    # --- S11 insert over-the-shoulder Bu Lastri (cek status) ---
    cam("S11_CAM", [(1951, (0.15, 1.55, 1.85), (-0.22, 0.28, 1.35), 50), (2100, (0.10, 1.48, 1.82), (-0.22, 0.28, 1.36), 56)], fstop=2.8)
    # --- S12 two-shot (menyerahkan pesanan) ---
    cam("S12_CAM", [(2101, (-2.3, -2.8, 1.65), (-0.02, 0.05, 1.40), 32), (2310, (-2.1, -2.5, 1.63), (-0.02, 0.0, 1.40), 36)], fstop=4.0)
    # --- S13 close-up kantong & tangan ---
    cam("S13_CAM", [(2311, (1.75, -1.55, 1.60), (0.12, -0.10, 1.36), 46), (2460, (1.55, -1.40, 1.55), (0.14, -0.10, 1.34), 52)], fstop=2.8)
    # --- S14 medium-wide, dolly-out lembut ---
    cam("S14_CAM", [(2461, (2.0, -3.3, 1.8), (0.2, 0.2, 1.45), 34), (2560, (3.6, -6.4, 2.3), (0.1, 0.3, 1.6), 28), (2700, (6.0, -10.0, 3.0), (-0.2, 0.5, 2.0), 22)], fstop=5.6)
    print("kamera ok")

build()
