# 08c - Akting S11-S14
import bpy, math
from mathutils import Vector
exec(open(SD + "08a_scenes.py", encoding="utf8").read().split("# ============================================================== S01")[0])

# ============================================================== S11  f1951-2100
def S11():
    # L mengambil ponselnya, memiringkan untuk membaca, mengangguk: "Sudah masuk."
    act(L, 1951, handL=Wr(Vector((-0.06, 0.30, 1.37)), H_FLAT), head=(2, -4, 0))
    act(L, 1966, handL=Wr(PH_L + Vector((0.0, -0.02, 0.05)), (-80, 0, 0)), head=(8, -2, 0), gaze=tuple(PH_L), lean=5)
    act(L, 1990, handL=Wr(Vector((-0.20, 0.30, 1.40)), (-110, 0, 0)), head=(16, 0, 0), gaze=(-0.20, 0.32, 1.40), lean=4)
    act(L, 2020, handL=Wr(Vector((-0.20, 0.30, 1.42)), (-118, 0, 0)), head=(20, 0, 0))
    L.talk(2040, 2062, smile=0.5, seed=21)                      # "Sudah masuk."
    act(L, 2038, head=(14, -2, 0), gaze=tuple(Mrel(0, 0, 1.55)), mouth=(0.5, 0, 0), brow=(0.005, 0))
    act(L, 2054, head=(20, -2, 0)); act(L, 2066, head=(8, -2, 0))   # mengangguk
    act(L, 2096, handL=Wr(Vector((-0.20, 0.30, 1.42)), (-118, 0, 0)), head=(4, -3, 0))
    act(M, 1960, head=(2, 8, 0), gaze=(L_POS[0], L_POS[1], L_POS[2] + 1.45))
    act(M, 2040, head=(0, 8, 0), gaze=(L_POS[0], L_POS[1], L_POS[2] + 1.45), mouth=(0.3, 0, 0), brow=(0.004, 0))
    act(M, 2096, head=(0, 8, 0))

# ============================================================== S12  f2101-2310
def S12():
    bag_open = Vector((-0.28, 0.14, 1.52))
    # L menaruh ponsel, mengambil penjepit (tangan kanan) dan kantong (tangan kiri)
    act(L, 2101, handL=Wr(PH_L + Vector((0.0, 0.0, 0.07)), (-90, 0, 0)), head=(6, -3, 0), gaze=tuple(PH_L), lean=4)
    act(L, 2114, handL=Wr(PH_L + Vector((0.0, 0.0, 0.035)), (-90, 0, 0)), head=(6, -3, 0))
    act(L, 2134, handL=Wr(BAG_F + Vector((0.0, 0.0, 0.10)), (-70, 0, 0)), handR=Wr(Vector((-0.70, 0.06, 1.41)), (-60, 0, 0)), head=(8, -4, 0), gaze=tuple(BAG_F))
    act(L, 2152, handL=Wr(bag_open, (-70, 0, 0)), handR=Wr(TRAY_B + Vector((0, 0, 0.05)), H_TONG), head=(10, -4, 0), gaze=tuple(TRAY_B))
    for i, f0 in enumerate((2160, 2184, 2206)):                # tiga gorengan masuk ke kantong
        act(L, f0, handR=Wr(TRAY_B + Vector((-0.10 * i, 0.0, 0.0)), H_TONG), gaze=tuple(TRAY_B))
        act(L, f0 + 10, handR=Wr(TRAY_B + Vector((-0.10 * i, 0.0, 0.05)), H_TONG), gaze=tuple(bag_open))
        act(L, f0 + 18, handR=Wr(bag_open + Vector((0.0, 0.0, 0.06)), H_TONG), gaze=tuple(bag_open))
    act(L, 2232, handR=Wr(Vector((-0.55, 0.30, 1.37)), H_FLAT), handL=Wr(bag_open + Vector((0.12, -0.08, 0.0)), (-70, 0, 0)), head=(4, -3, 0), gaze=tuple(Mrel(0, 0, 1.55)))
    # menyerahkan kantong ke M
    act(L, 2252, handL=Wr(HAND + Vector((-0.02, 0.0, 0.06)), (-80, 0, 0)), lean=10, head=(0, -3, 0), gaze=tuple(Mrel(0.1, 0, 1.55)), mouth=(0.5, 0, 0))
    act(L, 2276, handL=Wr(HAND + Vector((-0.02, 0.0, 0.06)), (-80, 0, 0)), head=(0, -3, 0))
    act(L, 2298, handL=Wr(Vector((-0.06, 0.30, 1.37)), H_FLAT), handR=Wr(Vector((-0.50, 0.28, 1.37)), H_FLAT), head=(0, -4, 0), lean=0, mouth=(0.6, 0, 0))
    L.talk(2272, 2304, smile=0.6, seed=22)                      # "Hati-hati, masih hangat."
    # M meraih kantong, tersenyum: "Makasih, Bu."
    act(M, 2101, head=(0, 8, 0))
    act(M, 2226, handR=Wr(Mrel(0.22, 0.05, 1.22), (-70, 0, 0)), head=(2, 8, 0), gaze=tuple(HAND))
    act(M, 2256, handR=Wr(HAND + Vector((-0.02, 0.0, 0.06)), (-85, 0, 0)), head=(6, 6, 0), gaze=tuple(HAND), mouth=(0.5, 0, 0))
    M.talk(2240, 2266, smile=0.6, seed=23)
    act(M, 2278, handR=Wr(HAND + Vector((-0.02, 0.0, 0.06)), (-85, 0, 0)), head=(0, 6, 0), gaze=(L_POS[0], L_POS[1], L_POS[2] + 1.5), mouth=(0.7, 0, 0), brow=(0.006, -3))

# ============================================================== S13  f2311-2460
def S13():
    # M menarik kantong ke arahnya; L melepas
    act(M, 2311, handR=Wr(HAND + Vector((-0.02, 0.0, 0.06)), (-85, 0, 0)), mouth=(0.7, 0, 0))
    act(M, 2340, handR=Wr(Mrel(0.20, 0.16, 1.22), (-80, 0, 0)), head=(4, 6, 0), gaze=tuple(Mrel(0.20, 0.16, 1.22)), mouth=(0.7, 0, 0))
    act(M, 2400, handR=Wr(Mrel(0.20, 0.20, 1.02), (-70, 0, 0)), head=(0, 8, 0), gaze=(L_POS[0], L_POS[1], L_POS[2] + 1.5))
    act(M, 2450, handR=Wr(Mrel(0.20, 0.20, 1.02), (-70, 0, 0)), head=(0, 8, 0))
    act(L, 2300, handL=Wr(Vector((-0.16, 0.30, 1.42)), (-80, 0, 0)), lean=6)      # Bu Lastri sudah melepas kantong; tangan mundur agar tidak bertabrakan dengan tangan pelanggan
    act(L, 2338, handL=Wr(Vector((-0.04, 0.12, 1.38)), (-80, 0, 0)), lean=6, head=(0, -3, 0), gaze=tuple(Mrel(0, 0, 1.5)))
    act(L, 2380, handL=Wr(Vector((-0.06, 0.30, 1.37)), H_FLAT), handR=Wr(Vector((-0.50, 0.28, 1.37)), H_FLAT), lean=0, head=(-1, -3, 0), mouth=(0.6, 0, 0))
    act(L, 2458, head=(-1, -3, 0))

# ============================================================== S14  f2461-2700
def S14():
    # M berpamitan, berbalik, berjalan keluar kanan sambil membawa kantong
    M.state["place"] = None
    act(M, 2466, place=((M_STAND.x, M_STAND.y, 0), M_YAW), head=(0, 8, 0), gaze=(L_POS[0], L_POS[1], L_POS[2] + 1.5), mouth=(0.6, 0, 0))
    act(M, 2484, place=((M_STAND.x, M_STAND.y, 0), M_YAW), head=(0, 4, 0))
    YAW_OUT = math.degrees(math.atan2(1.2 - M_STAND.x, -(-1.05 - M_STAND.y))) - 360
    act(M, 2508, place=((M_STAND.x, M_STAND.y, 0), YAW_OUT), head=(0, -10, 0), gaze=(5.0, -0.5, 1.5))
    M.state["place"] = None
    walk(M, 2509, (M_STAND.x, M_STAND.y), (5.2, -1.10), T=13, n=11, via=[(1.2, -1.05)])
    # L: kembali merapikan dagangan dengan percaya diri, melepas pandang ke kanan
    act(L, 2466, head=(-1, -3, 0), gaze=tuple(Mrel(0, 0, 1.5)), mouth=(0.6, 0, 0))
    act(L, 2500, head=(0, -14, 0), gaze=(3.0, -1.0, 1.45))
    act(L, 2540, head=(0, -6, 0), mouth=(0.4, 0, 0), gaze=(1.5, -0.5, 1.4))
    act(L, 2570, handR=Wr(TRAY_B + Vector((0, 0, 0.05)), H_TONG), head=(8, -3, 0), gaze=tuple(TRAY_B), lean=8, mouth=(0.5, 0, 0))
    act(L, 2600, handR=Wr(TRAY_M + Vector((0, 0, 0.05)), H_TONG), head=(8, -4, 0), gaze=tuple(TRAY_M))
    act(L, 2640, handR=Wr(TRAY_M + Vector((0.1, 0, 0.05)), H_TONG), head=(4, -2, 0), mouth=(0.6, 0, 0), brow=(0.004, 0))
    act(L, 2690, handR=Wr(Vector((-0.50, 0.28, 1.37)), H_FLAT), head=(0, -2, 0), lean=0, gaze=(0.8, -2.5, 1.5))

def run_C():
    S11(); S12(); S13(); S14()
    print("scenes C ok")
