# 08b - Akting S06-S10
import bpy, math
from mathutils import Vector
exec(open(SD + "08a_scenes.py", encoding="utf8").read().split("# ============================================================== S01")[0])   # konstanta & helper

# ============================================================== S06  f841-1080
def S06():
    # M: "Nanti saya balik lagi, Bu."  lalu berbalik & berjalan keluar ke kanan layar
    M.talk(846, 872, smile=0.4, seed=11)
    act(M, 850, handL=None, head=(0, 8, 0), gaze=(L_POS[0], L_POS[1], L_POS[2] + 1.45))
    act(M, 878, head=(2, 6, 0))
    M.state["place"] = None
    act(M, 880, place=((M_STAND.x, M_STAND.y, 0), M_YAW), head=(0, 4, 0))
    YAW_OUT = math.degrees(math.atan2(1.2 - M_STAND.x, -(-1.05 - M_STAND.y))) - 360
    act(M, 905, place=((M_STAND.x, M_STAND.y, 0), YAW_OUT), head=(0, -10, 0), gaze=(4.5, -0.5, 1.5))
    M.state["place"] = None
    walk(M, 906, (M_STAND.x, M_STAND.y), (5.2, -1.10), T=13, n=11, via=[(1.2, -1.05)])
    # L: mengangguk, bahu turun, menatap tempat M tadi berdiri, lalu meraih ponsel
    act(L, 846, head=(0, -3, 0), gaze=tuple(Mrel(0, 0, 1.55)), mouth=(0.4, 0, 0))
    act(L, 876, head=(0, -4, 0), mouth=(0.2, 0, 0))
    act(L, 912, head=(3, -2, 0), gaze=tuple(Mrel(0, 0, 1.0)), clavL=(0, 0, 8), clavR=(0, 0, -8), brow=(0.003, 7), mouth=(0, 0, 0))
    act(L, 952, head=(10, 0, 0), gaze=(0.3, -0.5, 1.3), clavL=(0, 0, 8), clavR=(0, 0, -8), handL=W(Vector((-0.10, 0.27, 1.32))), lean=3)
    act(L, 986, head=(8, 6, 0), handL=Wr(PH_L + Vector((0.0, -0.02, 0.05)), (-80, 0, 0)), gaze=tuple(PH_L), lean=6, brow=(0.002, 4))
    act(L, 1010, handL=Wr(PH_L + Vector((0.0, -0.02, 0.05)), (-80, 0, 0)), gaze=tuple(PH_L))
    act(L, 1040, handL=Wr(Vector((-0.22, 0.30, 1.38)), (-110, 0, 0)), head=(18, 0, 0), gaze=(-0.22, 0.32, 1.38), lean=4, clavL=(0, 0, 3), clavR=(0, 0, -3))
    act(L, 1068, handL=Wr(Vector((-0.22, 0.30, 1.38)), (-110, 0, 0)), head=(20, 0, 0))

# ============================================================== S07  f1081-1320
def S07():
    P = Vector((-0.22, 0.30, 1.38))
    act(L, 1081, handL=Wr(P, (-110, 0, 0)), head=(20, 0, 0), gaze=tuple(P))
    taps = (1128, 1164, 1206, 1252, 1290)
    for i, f in enumerate(taps):
        tip = Vector((-0.34 + 0.02 * (i % 2), 0.27, 1.40 - 0.02 * (i % 3)))
        act(L, f - 12, handR=Wr(tip + Vector((0, 0.04, 0.08)), (-100, 0, 0)), head=(20 + (i % 2), -3 + (i % 3), 0), gaze=tuple(P + Vector((0, 0, 0.0))))
        act(L, f, handR=Wr(tip, (-100, 0, 0)))
    act(L, 1304, handR=Wr(Vector((-0.34, 0.31, 1.46)), (-100, 0, 0)), head=(12, -2, 0), mouth=(0.45, 0, 0), brow=(0.004, -2))
    act(L, 1318, handL=Wr(PH_L + Vector((0.0, 0.0, 0.07)), (-90, 0, 0)), handR=None, head=(8, 0, 0), gaze=tuple(PH_L), lean=6)

# ============================================================== S08  f1321-1500
def S08():
    # L membawa papan QRIS dengan menjepit TEPI SAMPING papan setinggi dada (jari mengarah ke tengah papan di sisi belakang, jempol melingkar ke muka
    # papan), condong ke depan melewati meja, meletakkan papan, membuka genggaman, lalu menarik tangan. Papan sudah di tangan sejak awal S08.
    FD = (1.0, 0.0, 0.0); PD = (0.0, -1.0, 0.0)
    HW = 0.118                                                          # setengah lebar kartu (0,237 m / 2)
    def P(dx, dy, dz): return Vector((QR.x - HW + dx, QR.y + dy, QR.z - 0.08 + dz))      # titik tepi kiri papan (prop di QR+0.02 saat diletakkan)
    def Gb(dx, dy, dz, lift=0.02): return G(P(dx, dy, dz), FD, PD, back=0.09, lift=lift)
    act(L, 1321, handL=Gb(0.20, 0.47, 0.05, 0.03), gripL="board", handR=None, head=(8, 0, 0), gaze=tuple(P(0, 0.3, 0)), lean=8)
    act(L, 1336, handR=Wr(Vector((-0.55, 0.30, 1.40)), H_FLAT), gripR="relaxed")
    act(L, 1346, handL=Gb(0.12, 0.30, 0.08, 0.03), gripL="board", head=(2, 0, 0), gaze=tuple(QR), lean=14, clavL=(0, 0, 0), clavR=(0, 0, 0), brow=(0.003, 0), mouth=(0.4, 0, 0))
    act(L, 1368, handL=Gb(0.04, 0.14, 0.05, 0.03), gripL="board", head=(6, -4, 0), gaze=tuple(QR), lean=26)
    act(L, 1392, handL=Gb(0.0, 0.0, 0.0, 0.02), gripL="board", head=(8, -6, 0), gaze=tuple(QR), lean=30)          # papan menyentuh meja
    act(L, 1405, handL=Gb(0.0, 0.0, 0.0, 0.02), gripL="board")
    act(L, 1411, handL=Gb(-0.01, 0.0, 0.01, 0.03), gripL="open")                                                  # buka genggaman setelah papan berdiri
    act(L, 1426, handL=Gb(-0.14, 0.18, 0.08, 0.05), gripL="open", head=(4, -4, 0), lean=12, mouth=(0.55, 0, 0))   # tarik tangan ke belakang
    act(L, 1450, handL=Wr(Vector((-0.06, 0.30, 1.37)), H_FLAT), gripL="relaxed", handR=Wr(Vector((-0.50, 0.28, 1.37)), H_FLAT), head=(0, -4, 0), lean=0, gaze=tuple(QR), mouth=(0.6, 0, 0))
    act(L, 1498, head=(-2, -8, 0), gaze=(3.0, -2.5, 1.45))

# ============================================================== S09  f1501-1740
def S09():
    # M kembali: jalan masuk dari kanan, berhenti, menghadap L
    M.state["place"] = None
    act(M, 1501, place=((7.0, -1.10, 0), -90), head=(0, 0, 0))
    act(M, 1502, place=((3.6, -1.10, 0), -90))
    last = walk(M, 1504, (3.6, -1.12), (M_STAND.x, M_STAND.y), T=15, n=7, via=[(1.2, -1.12)])
    YAW_IN2 = math.degrees(M.rig_yaw)
    M.state["place"] = None
    act(M, last + 1, place=((M_STAND.x, M_STAND.y, 0), YAW_IN2), head=(0, 0, 0))
    act(M, last + 24, place=((M_STAND.x, M_STAND.y, 0), M_YAW), head=(0, 8, 0), gaze=tuple(QR))
    M.state["place"] = None
    # L: menengok, tersenyum percaya diri, membuka telapak tangan ke arah QRIS
    act(L, 1520, head=(-2, -18, 0), gaze=(2.2, -1.2, 1.45), mouth=(0.5, 0, 0))
    act(L, 1580, head=(-2, -8, 0), gaze=tuple(Mrel(0, 0, 1.55)), brow=(0.005, 0))
    M.talk(1660, 1688, smile=0.3, seed=12)                      # "Sekarang sudah bisa, Bu?"
    act(M, 1664, head=(3, 8, 0), gaze=tuple(QR), brow=(0.005, 0))
    act(M, 1690, head=(0, 8, 0), gaze=(L_POS[0], L_POS[1], L_POS[2] + 1.45))
    L.talk(1696, 1730, smile=0.6, seed=13)                      # "Bisa. Seperti biasa?"
    act(L, 1692, handL=Wr(Vector((-0.02, 0.18, 1.34)), (-90, 0, 0)), head=(0, -4, 0), gaze=tuple(Mrel(0, 0, 1.55)), lean=4)
    act(L, 1712, handL=Wr(Vector((0.04, 0.10, 1.36)), (-90, 90, 0)), head=(-1, -3, 0), gaze=tuple(QR), lean=8, mouth=(0.6, 0, 0))
    act(L, 1738, handL=Wr(Vector((0.04, 0.10, 1.36)), (-90, 90, 0)), head=(0, -4, 0), gaze=tuple(Mrel(0, 0, 1.55)))

# ============================================================== S10  f1741-1950
def S10():
    scan = QR + Vector((0.0, -0.20, 0.06)); read = QR + Vector((0.05, -0.42, -0.06))
    act(M, 1741, handL=Wr(Mrel(0.20, -0.17, 1.05), (-70, 0, 0)), head=(0, 8, 0))
    act(M, 1766, handL=Wr(scan, (-110, 0, 0)), head=(4, 6, 0), gaze=tuple(QR), lean=4)
    act(M, 1800, handL=Wr(scan + Vector((0, 0.04, 0)), (-110, 0, 0)), head=(6, 6, 0))
    act(M, 1832, handL=Wr(read, (-110, 0, 0)), head=(16, 4, 0), gaze=tuple(read))
    act(M, 1866, handL=Wr(read, (-110, 0, 0)), handR=Wr(read + Vector((-0.02, -0.06, 0.1)), (-100, 0, 0)), head=(18, 4, 0))
    act(M, 1890, handR=Wr(read + Vector((-0.02, -0.01, 0.01)), (-100, 0, 0)))
    act(M, 1908, handR=Wr(read + Vector((-0.02, -0.08, 0.10)), (-100, 0, 0)), head=(14, 6, 0), mouth=(0.3, 0, 0))
    act(M, 1940, handL=Wr(Mrel(0.20, -0.17, 1.05), (-70, 0, 0)), handR=None, head=(2, 8, 0), gaze=(L_POS[0], L_POS[1], L_POS[2] + 1.45), mouth=(0.4, 0, 0))
    act(L, 1744, handL=Wr(Vector((0.04, 0.10, 1.36)), (-90, 90, 0)), head=(0, -4, 0), gaze=tuple(scan))
    act(L, 1790, handL=Wr(Vector((-0.06, 0.30, 1.37)), H_FLAT), handR=Wr(Vector((-0.50, 0.28, 1.37)), H_FLAT), head=(2, -4, 0), lean=0, gaze=tuple(scan))
    act(L, 1860, head=(4, -2, 0), gaze=tuple(read), brow=(0.003, 0))
    act(L, 1944, head=(2, -4, 0), gaze=(PH_L.x, PH_L.y, PH_L.z))

def run_B():
    S06(); S07(); S08(); S09(); S10()
    print("scenes B ok")
