# 11 - Animasi properti: pegangan tangan (Copy Transforms ke empty yang di-parent ke tulang tangan, influence berkunci),
#      penempatan, kemunculan; osilasi papan nama & lampu (sinus teredam)
import bpy, math
from mathutils import Vector, Matrix, Euler

OB = bpy.data.objects; SC = bpy.context.scene
rad = math.radians
L = bpy.app.driver_namespace["L"]; M = bpy.app.driver_namespace["M"]
C4 = bpy.data.collections["04_PROPS"]
exec(open(SD + "08a_scenes.py", encoding="utf8").read().split("# ============================================================== S01")[0])   # konstanta

def tree(o): return [o] + list(o.children_recursive)

def reset_prop(o, scale):
    if o.animation_data: o.animation_data_clear()
    for c in list(o.constraints): o.constraints.remove(c)
    o.scale = (scale,) * 3
    for t in tree(o):
        if t.animation_data and t is not o: t.animation_data_clear()
        t.hide_render = False; t.hide_viewport = False

def key_basis(o, f, loc, rot_deg):
    o.location = Vector(loc); o.rotation_euler = Euler([rad(a) for a in rot_deg], 'XYZ')
    o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f)

def show(o, f, vis):
    for t in tree(o):
        t.hide_render = not vis; t.hide_viewport = not vis
        t.keyframe_insert("hide_render", frame=f); t.keyframe_insert("hide_viewport", frame=f)

def parent_bone(obj, rig, bname):
    bpy.context.view_layer.update()
    mw = obj.matrix_world.copy()
    obj.parent = rig; obj.parent_type = 'BONE'; obj.parent_bone = bname
    bpy.context.view_layer.update()
    pbn = rig.pose.bones[bname]
    for tail in (True, False):
        Mx = rig.matrix_world @ pbn.matrix
        if tail: Mx = Mx @ Matrix.Translation((0, pbn.bone.length, 0))
        obj.matrix_parent_inverse = Mx.inverted()
        bpy.context.view_layer.update()
        if (obj.matrix_world.translation - mw.translation).length < 1e-4: return

def make_att(name, ch, side, f_pose, world_loc, world_rot_deg, scale):
    """Empty pegangan: pada frame f_pose, prop (di dunia) berada di world_loc/rot; offset relatif ke tulang tangan dipertahankan."""
    SC.frame_set(f_pose); bpy.context.view_layer.update()
    e = OB.get(name)
    if e: OB.remove(e)
    e = bpy.data.objects.new(name, None); e.empty_display_type = 'ARROWS'; e.empty_display_size = 0.05
    C4.objects.link(e)
    e.rotation_mode = 'XYZ'
    e.matrix_world = Matrix.Translation(Vector(world_loc)) @ Euler([rad(a) for a in world_rot_deg], 'XYZ').to_matrix().to_4x4() @ Matrix.Diagonal((*(scale if hasattr(scale,'__len__') else (scale,scale,scale)), 1))
    parent_bone(e, ch.rig, f"hand.{side}")
    return e

def hold(prop, att, f_on, f_off, ramp=7):
    c = prop.constraints.new('COPY_TRANSFORMS'); c.name = "hold_" + att.name; c.target = att
    c.influence = 0.0
    keys = [(f_on - ramp, 0.0), (f_on, 1.0)] + ([(f_off, 1.0), (f_off + ramp, 0.0)] if f_off is not None else [])
    for f, v in keys:
        c.influence = v; c.keyframe_insert("influence", frame=f)
    return c

def constant_interp(o):
    ad = o.animation_data
    if not ad or not ad.action: return
    for layer in ad.action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fc in cb.fcurves:
                    if fc.data_path in ("location", "rotation_euler", "hide_render", "hide_viewport"):
                        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

SCL = dict(bag=0.9, wallet=0.85, phone=0.55, lphone=0.55, qr=0.8, tongs=1.0)

def run_props():
    # --- reset ---
    tg0 = OB["Tongs"]
    if tg0.animation_data: tg0.animation_data_clear()
    for c in list(tg0.constraints): tg0.constraints.remove(c)
    tg0.scale = (1, 1, 1); bpy.context.view_layer.update()
    d0 = tg0.dimensions
    TSC = (0.25 / d0.x, 0.03 / d0.y, 0.03 / d0.z)
    tg0.scale = TSC
    for n, s in (("PAPER_BAG", SCL["bag"]), ("EMPTY_WALLET", SCL["wallet"]), ("CUSTOMER_PHONE", SCL["phone"]),
                 ("LASTRI_PHONE", SCL["lphone"]), ("QRIS_DUMMY_NONAKTIF", SCL["qr"])):
        reset_prop(OB[n], s)
    for o in list(OB):
        if o.name.startswith("ATT_"): OB.remove(o)
    SC.frame_set(1)
    # ================= penjepit =================
    tg = OB["Tongs"]
    a1 = make_att("ATT_tongs_L_R", L, "R", 30, tuple(TRAY_B + Vector((0, -0.05, -0.03))), (-10, 0, 90), TSC)
    hold(tg, a1, 1, 104, ramp=1)
    key_basis(tg, 0, (-0.70, 0.08, 1.285), (0, 0, 10)); key_basis(tg, 104, (-0.70, 0.08, 1.285), (0, 0, 10))
    a2 = make_att("ATT_tongs_L_R2", L, "R", 2152, tuple(TRAY_B + Vector((0, -0.05, 0.07)) ), (-10, 0, 90), TSC)
    hold(tg, a2, 2134, 2232)
    key_basis(tg, 2232, (-0.66, 0.10, 1.285), (0, 0, 25))
    a3 = make_att("ATT_tongs_L_R3", L, "R", 2570, tuple(TRAY_B + Vector((0, -0.05, 0.07))), (-10, 0, 90), TSC)
    hold(tg, a3, 2566, None)
    # ================= kantong =================
    bg = OB["PAPER_BAG"]
    hand_bag = BAG_F + Vector((0, 0, 0.10))
    b1 = make_att("ATT_bag_L_L", L, "L", 142, tuple(hand_bag + Vector((0, 0, -0.13))), (0, 0, 0), SCL["bag"])
    key_basis(bg, 0, BAG0, (0, 0, 0)); key_basis(bg, 118, BAG0, (0, 0, 0))
    hold(bg, b1, 120, 158)
    key_basis(bg, 158, BAG_F, (0, 0, 0))
    hold(bg, make_att("ATT_bag_L_L2", L, "L", 452, tuple(BAG_F + Vector((-0.06, 0.08, 0.14)) + Vector((0, 0, -0.13))), (0, 0, 0), SCL["bag"]), 428, 722)
    key_basis(bg, 722, BAG_F, (0, 0, 0))
    hold(bg, make_att("ATT_bag_L_L3", L, "L", 2152, (-0.28, 0.14, 1.52 - 0.13), (0, 0, 0), SCL["bag"]), 2134, 2280)
    key_basis(bg, 2280, HAND + Vector((0, 0, -0.14)), (0, 0, 0))
    hold(bg, make_att("ATT_bag_M_R", M, "R", 2256, tuple(HAND + Vector((-0.02, 0.0, 0.06)) + Vector((0, 0, -0.13))), (0, 0, 0), SCL["bag"]), 2262, None)
    # gorengan di dalam kantong (muncul satu per satu)
    for i, f in enumerate((2170, 2194, 2216)):
        nm = f"BagItem{i}"
        o = OB.get(nm)
        if o: OB.remove(o)
        bm = bpy.data.meshes.new(nm)
        import bmesh
        b = bmesh.new(); bmesh.ops.create_uvsphere(b, u_segments=16, v_segments=10, radius=0.05); b.to_mesh(bm); b.free()
        for p in bm.polygons: p.use_smooth = True
        o = bpy.data.objects.new(nm, bm); bm.materials.append(bpy.data.materials["M_Gorengan"]); C4.objects.link(o)
        o.parent = bg; o.location = (-0.05 + 0.05 * i, 0.0, 0.17 + 0.01 * i); o.scale = (1.0, 0.9, 0.8)
        show(o, 0, False); show(o, f, True)
        constant_interp(o)
    # ================= dompet =================
    wl = OB["EMPTY_WALLET"]
    w1 = make_att("ATT_wallet_M_R", M, "R", 612, tuple(Mrel(0.19, 0.08, 1.31)), (0, 0, M_YAW + 180), SCL["wallet"])
    key_basis(wl, 0, Mrel(0.14, 0.18, 1.05), (0, 0, M_YAW + 180))
    show(wl, 0, False); show(wl, 578, True)
    hold(wl, w1, 585, 686)
    show(wl, 690, False)
    # ================= ponsel pelanggan =================
    cp = OB["CUSTOMER_PHONE"]
    ph = Mrel(0.34, -0.02, 1.30)
    p1 = make_att("ATT_cphone_M_L", M, "L", 724, tuple(ph), (-10, 0, M_YAW + 180), SCL["phone"])
    key_basis(cp, 0, ph, (-10, 0, M_YAW + 180))
    show(cp, 0, False); show(cp, 697, True)
    hold(cp, p1, 700, 846)
    show(cp, 850, False); show(cp, 1740, True)
    hold(cp, make_att("ATT_cphone_M_L2", M, "L", 1766, tuple(QR + Vector((0.0, -0.20, 0.06))), (-10, 0, M_YAW + 180), SCL["phone"]), 1745, 1942)
    show(cp, 1946, False)
    # ================= ponsel Bu Lastri =================
    lp = OB["LASTRI_PHONE"]
    key_basis(lp, 0, PH_L + Vector((0, 0, 0.0)), (-15, 0, 180))
    lh = make_att("ATT_lphone_L_L", L, "L", 1040, (-0.22, 0.30, 1.38), (-25, 0, 180), SCL["lphone"])
    hold(lp, lh, 1000, 1318)
    key_basis(lp, 1318, PH_L, (-15, 0, 180))
    hold(lp, make_att("ATT_lphone_L_L2", L, "L", 1990, (-0.20, 0.30, 1.40), (-25, 0, 180), SCL["lphone"]), 1966, 2114)
    key_basis(lp, 2114, PH_L, (-15, 0, 180))
    # teks layar: 'belajar' sampai S08, 'diterima' mulai S11
    show(OB["Learning mock screen"], 0, True); show(OB["Learning mock screen"], 1400, False)
    show(OB["Received mock screen"], 0, False); show(OB["Received mock screen"], 2036, True)
    # ================= papan QRIS =================
    qr = OB["QRIS_DUMMY_NONAKTIF"]
    show(qr, 0, False); show(qr, 1321, True)
    top = QR + Vector((0, 0, 0.24))
    qh = make_att("ATT_qr_L_L", L, "L", 1392, tuple(QR + Vector((0, 0, 0.02))), (0, 0, 0), SCL["qr"])
    key_basis(qr, 0, QR + Vector((0, 0, 0.6)), (0, 0, 0))
    hold(qr, qh, 1321, 1405, ramp=1)
    # lepas: setelah genggaman membuka papan turun dan berdiri
    key_basis(qr, 1405, QR, (0, 0, 0))
    for o in (tg, bg, wl, cp, lp, qr): constant_interp(o)
    finish_grips()
    SC.frame_set(1)
    print("props ok")

def run_oscillation():
    """Sinus teredam: papan nama (pivot) & lampu bandul. Angin: ledakan di awal S01 dan S14; sinus kecil sepanjang waktu."""
    sg = OB["SIGN_oscillation_pivot"]; lp = OB["LAMP_pivot"]
    for o in (sg, lp):
        if o.animation_data: o.animation_data_clear()
    bursts = [(6, 5.0), (700, 2.0), (1330, 2.5), (1980, 2.0), (2470, 4.0)]     # (frame, amplitudo derajat)
    def angle(f, T_ , k, phase=0.0, amb=0.7):
        a = amb * math.sin(2 * math.pi * f / (T_ * 2.2) + phase)
        for f0, A in bursts:
            if f >= f0:
                t = f - f0
                a += A * math.exp(-k * t) * math.sin(2 * math.pi * t / T_ + phase)
        return a
    for f in range(1, 2701, 3):
        sg.rotation_euler = (0, rad(angle(f, 52, 0.022)), 0); sg.keyframe_insert("rotation_euler", index=1, frame=f)
        lp.rotation_euler = (rad(angle(f, 38, 0.018, 1.3, 1.0)), 0, 0); lp.keyframe_insert("rotation_euler", index=0, frame=f)
    print("osilasi ok")

run_props(); run_oscillation()
