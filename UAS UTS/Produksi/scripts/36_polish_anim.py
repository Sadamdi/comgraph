# 36 - Poles animasi (prinsip animasi) pada Action rig: overshoot+settle, anticipation, overlap jari (follow-through), kepala menyusul mata.
# polish(rig_name) dijalankan SEKALI setelah animasi dibangun (09_boot + 08a/b/c + 11_props). Menambah key pada kurva yang sudah ada; bukan idempoten.
import bpy, math
from mathutils import Vector

def _chans(cb, path):
    return [next((f for f in cb.fcurves if f.data_path == path and f.array_index == i), None) for i in range(3)]

def _shift(fc, d):
    for kp in fc.keyframe_points:
        kp.co.x += d; kp.handle_left.x += d; kp.handle_right.x += d
    fc.update()

def _ins(fc, frame, val):
    kp = fc.keyframe_points.insert(frame, val, options={'FAST'})
    kp.interpolation = 'BEZIER'; kp.handle_left_type = 'AUTO_CLAMPED'; kp.handle_right_type = 'AUTO_CLAMPED'
    return kp

def polish(rig_name, over=0.15, over_max=0.018, antic=0.06, antic_max=0.02, finger_delay=(1, 2, 3), head_delay=2.0, neck_delay=1.0):
    R = bpy.data.objects[rig_name]; ad = R.animation_data; cb = ad.action.layers[0].strips[0].channelbag(ad.action_slot)
    st = {"overshoot": 0, "anticipation": 0, "finger_shift": 0}
    for s in ("L", "R"):
        ch = _chans(cb, f'pose.bones["hand_ik.{s}"].location')
        if not all(ch): continue
        frames = sorted({round(k.co.x) for fc in ch for k in fc.keyframe_points})
        P = lambda f: Vector([fc.evaluate(f) for fc in ch])
        new = []
        for i in range(1, len(frames) - 1):
            f0, f1, f2 = frames[i - 1], frames[i], frames[i + 1]
            p0, p1, p2 = P(f0), P(f1), P(f2)
            din = (p1 - p0).length; dout = (p2 - p1).length
            if din > 0.12 and (f2 - f1) >= 14 and dout < 0.04 and (f1 - f0) >= 8:            # tiba lalu menahan -> overshoot & settle
                ov = (p1 - p0).normalized() * min(over * din, over_max); ov.z = max(ov.z, 0.0)
                new.append((f1 + 3, p1 + ov)); new.append((min(f1 + 9, f2 - 3), p1)); st["overshoot"] += 1
            elif dout > 0.20 and (f2 - f1) >= 16 and (f1 - f0) >= 6:                         # sebelum gerakan besar -> sedikit tarik ke belakang
                d = (p2 - p1).normalized() * -min(antic * dout, antic_max); d.z = max(d.z, 0.0) if d.z < 0 else d.z
                new.append((f1 + 4, p1 + d)); st["anticipation"] += 1
        for fr, v in new:
            for k in range(3): _ins(ch[k], fr, v[k])
        for fc in ch: fc.update()
    # overlap jari: ruas distal menyusul (1,2,3 frame)
    for s in ("L", "R"):
        for fn in ("index", "middle", "ring", "pinky", "thumb"):
            for i in range(3):
                for ai in range(3):
                    fc = next((f for f in cb.fcurves if f.data_path == f'pose.bones["{fn}{i + 1}.{s}"].rotation_euler' and f.array_index == ai), None)
                    if fc: _shift(fc, finger_delay[i]); st["finger_shift"] += 1
    # kepala menyusul mata (mata sudah menuju target lewat Damped Track)
    for bn, d in (("head", head_delay), ("neck", neck_delay)):
        for ai in range(3):
            fc = next((f for f in cb.fcurves if f.data_path == f'pose.bones["{bn}"].rotation_euler' and f.array_index == ai), None)
            if fc: _shift(fc, d)
    return st


def smooth_poles(rig_name, passes=2, w=(0.25, 0.5, 0.25)):
    """Haluskan kurva sudut pole IK (ayunan siku): rata-rata berbobot tetangga pada nilai key; ujung tetap. Memengaruhi ayunan siku saja."""
    R = bpy.data.objects[rig_name]; ad = R.animation_data; cb = ad.action.layers[0].strips[0].channelbag(ad.action_slot)
    n = 0
    for fc in cb.fcurves:
        if not fc.data_path.endswith("pole_angle"): continue
        for _ in range(passes):
            vals = [kp.co[1] for kp in fc.keyframe_points]
            for i in range(1, len(vals) - 1):
                fc.keyframe_points[i].co[1] = w[0] * vals[i - 1] + w[1] * vals[i] + w[2] * vals[i + 1]
        fc.update(); n += 1
    return n
