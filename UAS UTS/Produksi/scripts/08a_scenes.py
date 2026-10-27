# 08a - Akting S01-S05 (Bu Lastri = L, Mahasiswa = M). Frame mengikuti marker storyboard. Staging jarak dekat agar tangan sampai.
import bpy, math, random
from mathutils import Vector

AN = bpy.app.driver_namespace["ANIM"]
walk = AN["walk"]
L = bpy.app.driver_namespace["L"]; M = bpy.app.driver_namespace["M"]

L_POS = (-0.30, 0.595, 0.22)      # berdiri di lantai panggung warung (tinggi 0,22 m) agar tinggi meja 1,30 m sesuai tinggi siku
M_STAND = Vector((0.30, -0.60, 0))
M_YAW = -150.0
def _face(y): return Vector((math.sin(math.radians(y)), -math.cos(math.radians(y)), 0))
FACE = _face(M_YAW); RIGHT = Vector((FACE.y, -FACE.x, 0))
def Mrel(f, r, z): return M_STAND + FACE * f + RIGHT * r + Vector((0, 0, z))

# titik kunci di atas meja (dunia)
TRAY_B = Vector((-0.50, 0.16, 1.41))        # baris belakang gorengan (mudah dijangkau)
TRAY_M = Vector((-0.75, 0.14, 1.41))
BAG0 = Vector((-0.10, 0.22, 1.345)); BAG_F = Vector((-0.42, 0.10, 1.345))
PH_L = Vector((-0.28, 0.28, 1.335))          # ponsel Bu Lastri di meja
QR = Vector((-0.05, 0.04, 1.46))             # pusat papan QRIS saat berdiri di meja
HAND = Vector((0.08, -0.04, 1.40))           # titik serah-terima kantong
STREET = Vector((3.6, -3.4, 1.45))
H_FLAT = (-80, 0, 0); H_TONG = (-50, 0, 0)

def W(v): return ("world", tuple(v), (-80, 0, 0))
def Wr(v, rot): return ("world", tuple(v), rot)

# ============================================================== S01  f1-240
def S01():
    L.place(L_POS, 0)
    L.auto_blink(1, 2700, seed=5); M.auto_blink(1, 2700, seed=9)
    ctr_R = Wr((-0.50, 0.28, 1.37), H_FLAT); ctr_L = Wr((-0.06, 0.30, 1.37), H_FLAT)
    act(L, 1, handR=Wr(TRAY_B + Vector((0, 0.0, 0.09)), H_TONG), handL=Wr(BAG0 + Vector((0, 0.10, -0.05)), (-60, 0, 0)), lean=8, head=(8, 0, 0),
        gaze=tuple(TRAY_B), mouth=(0.15, 0, 0), brow=(0, 0))
    act(L, 30, handR=Wr(TRAY_B + Vector((0.0, 0.0, 0.0)), H_TONG), lean=10, head=(12, 4, 0), gaze=tuple(TRAY_B))
    act(L, 46, handR=Wr(TRAY_B + Vector((0.0, 0.0, 0.05)), H_TONG), head=(10, 2, 0))
    act(L, 72, handR=Wr(TRAY_M + Vector((0, 0, 0.05)), H_TONG), head=(10, -6, 0), gaze=tuple(TRAY_M))
    act(L, 88, handR=Wr(TRAY_M, H_TONG), head=(12, -6, 0))
    act(L, 104, handR=Wr(TRAY_M + Vector((0.12, 0, 0.05)), H_TONG), head=(6, -2, 0), gaze=tuple(BAG0))
    # tangan kiri meraih kantong kosong lalu menggesernya ke depan
    act(L, 118, handR=Wr(Vector((-0.55, 0.20, 1.375)), H_FLAT), handL=Wr(BAG0 + Vector((0.0, -0.02, 0.10)), (-70, 0, 0)), head=(8, -4, 0), gaze=tuple(BAG0))
    act(L, 142, handL=Wr(BAG_F + Vector((0.0, 0.0, 0.10)), (-70, 0, 0)), head=(6, -6, 0), gaze=tuple(BAG_F))
    act(L, 158, handL=Wr(BAG_F + Vector((0.0, 0.0, 0.075)), (-70, 0, 0)), head=(6, -6, 0))
    # tegak, tangan bertumpu di meja, menengok ke jalan
    act(L, 184, handR=ctr_R, handL=ctr_L, lean=2, head=(-2, 0, 0), gaze=tuple(STREET), mouth=(0.35, 0, 0))
    act(L, 214, head=(-3, -18, 0), lean=0, hips=(0.0, 0.0, -0.02), gaze=tuple(STREET), brow=(0.003, 0))
    act(L, 240, head=(-3, -22, 0), lean=1)
    act(M, 1, place=((7.0, -1.10, 0), -90), gaze=(0.3, 0.3, 1.5))
    act(M, 240, place=((7.0, -1.10, 0), -90))

# ============================================================== S02  f241-390
def S02():
    global YAW_IN
    last = walk(M, 243, (3.6, -1.12), (M_STAND.x, M_STAND.y), T=15, n=7, via=[(1.2, -1.12)])
    YAW_IN = math.degrees(M.rig_yaw)
    M.look_at(241, (0.2, 0.3, 1.5)); M.look_at(375, (L_POS[0], L_POS[1], L_POS[2] + 1.45))
    act(L, 262, head=(-2, -22, 0), gaze=(2.4, -1.0, 1.45))
    act(L, 300, head=(-2, -14, 0), gaze=(1.2, -0.8, 1.45), mouth=(0.55, 0, 0), brow=(0.004, 0))
    act(L, 326, head=(5, -10, 0), gaze=(0.9, -0.7, 1.45))
    act(L, 340, head=(-1, -8, 0))
    act(L, 362, head=(0, -6, 0), gaze=(0.45, -0.5, 1.5), mouth=(0.6, 0, 0))
    M.state["place"] = None
    act(M, 376, place=((M_STAND.x, M_STAND.y, 0), YAW_IN))
    act(M, 398, place=((M_STAND.x, M_STAND.y, 0), M_YAW), gaze=(L_POS[0], L_POS[1], L_POS[2] + 1.45), head=(0, 12, 0))
    act(M, 424, place=((M_STAND.x, M_STAND.y, 0), M_YAW), head=(0, 6, 0))
    M.state["place"] = None

# ============================================================== S03  f391-540
def S03():
    M.talk(402, 428, smile=0.35, seed=1)                        # "Seperti biasa, Bu."
    act(M, 436, head=(0, 6, 0), gaze=(L_POS[0], L_POS[1], L_POS[2] + 1.5))
    act(M, 450, head=(5, 6, 0)); act(M, 458, head=(-2, 6, 0))   # mengangguk
    L.talk(446, 480, smile=0.5, seed=2)                         # "Masih hangat, nih."
    act(L, 405, head=(0, -4, 0), gaze=tuple(Mrel(0, 0, 1.55)), mouth=(0.55, 0, 0))
    act(L, 428, handL=Wr(BAG_F + Vector((0, 0, 0.10)), (-70, 0, 0)), handR=Wr(Vector((-0.50, 0.30, 1.37)), H_FLAT), head=(2, -3, 0))
    act(L, 452, handL=Wr(BAG_F + Vector((-0.06, 0.08, 0.14)), (-70, 0, 0)), head=(4, -3, 0), gaze=tuple(BAG_F))
    act(L, 484, handL=Wr(BAG_F + Vector((-0.04, 0.04, 0.10)), (-70, 0, 0)), head=(1, -3, 0), gaze=tuple(Mrel(0, 0, 1.55)), mouth=(0.55, 0, 0))
    act(L, 522, handL=Wr(BAG_F + Vector((-0.04, 0.04, 0.10)), (-70, 0, 0)), head=(0, -3, 0))

# ============================================================== S04  f541-660
def S04():
    wal_hi = Mrel(0.20, 0.10, 1.30); wal_open = Mrel(0.24, 0.06, 1.36)
    act(M, 541, head=(0, 6, 0))
    act(M, 566, handR=Wr(Mrel(0.16, 0.20, 0.95), (-70, 0, 0)), head=(8, 2, 0), gaze=tuple(Mrel(0.2, 0.15, 1.0)))
    Hw = lambda c: Hold("wallet", c, M_YAW + 180)                # telapak kanan menopang dompet terbuka (menghadap pelanggan)
    act(M, 580, handR=Hw(Mrel(0.14, 0.18, 1.05)), head=(10, 2, 0), gaze=tuple(Mrel(0.2, 0.15, 1.0)))   # dompet di kantong/pinggul
    act(M, 592, handR=Hw(Mrel(0.16, 0.14, 1.22)), head=(18, 0, 0), gaze=tuple(wal_hi), lean=4)
    act(M, 612, handR=Hw(Mrel(0.19, 0.08, 1.31)), head=(24, 0, 0), gaze=tuple(wal_open), brow=(0.003, -4))
    M.talk(600, 634, smile=0.0, seed=4)                         # "Waduh, lupa ambil tunai."
    act(M, 640, head=(22, -4, 0), brow=(0.006, 6))
    act(M, 660, head=(20, -4, 0))
    act(L, 548, head=(2, -3, 0), gaze=tuple(wal_hi), brow=(0.002, 0), handL=Wr(BAG_F + Vector((-0.04, 0.04, 0.10)), (-70, 0, 0)))
    act(L, 640, head=(4, -4, 0), gaze=tuple(wal_open), brow=(0.004, 4))

# ============================================================== S05  f661-840
def S05():
    ph = Mrel(0.34, -0.02, 1.30)
    act(M, 676, handR=Wr(Mrel(0.20, 0.20, 1.05), (-70, 0, 0)), head=(8, 0, 0), brow=(0, 0))
    act(M, 700, handR=None, handL=Wr(Mrel(0.20, -0.17, 1.05), (-70, 0, 0)), head=(4, 4, 0), gaze=(L_POS[0], L_POS[1], L_POS[2] + 1.45))
    act(M, 724, handL=Wr(ph, (-110, 0, 0)), head=(0, 6, 0), gaze=(L_POS[0], L_POS[1], L_POS[2] + 1.45), brow=(0.005, 0))
    M.talk(716, 742, smile=0.2, seed=6)                         # "Bisa QRIS, Bu?"
    act(M, 748, head=(0, 6, 0))
    act(M, 800, head=(2, 8, 0), brow=(0.004, 4))
    act(M, 840, head=(4, 8, 0))
    # L: meletakkan kantong, menjawab "Belum, Nak." sambil menunduk
    act(L, 668, head=(0, -3, 0), gaze=tuple(ph))
    act(L, 700, handL=Wr(BAG_F + Vector((0.0, 0.0, 0.06)), (-70, 0, 0)), head=(2, -2, 0))
    act(L, 722, handL=Wr(Vector((-0.06, 0.30, 1.37)), H_FLAT), head=(4, -2, 0), gaze=tuple(ph))
    L.talk(752, 776, smile=0.0, seed=8)                         # "Belum, Nak."
    act(L, 752, head=(8, -6, 0), brow=(0.004, 8), gaze=(0.45, -0.4, 1.3), clavL=(0, 0, 4), clavR=(0, 0, -4))
    act(L, 790, head=(12, -3, 0), brow=(0.003, 8), clavL=(0, 0, 6), clavR=(0, 0, -6))
    act(L, 830, head=(10, -2, 0), brow=(0.003, 8))

def run_A():
    S01(); S02(); S03(); S04(); S05()
    print("scenes A ok")
