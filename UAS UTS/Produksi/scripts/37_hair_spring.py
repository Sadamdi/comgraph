# 37 - Gerak sekunder rambut: pegas-peredam (spring) terhadap percepatan sudut kepala (dari render/head_rot.json hasil qa_motion_bg.py).
# apply_hair_spring("LASTRI","L") menulis keyframe rotation_euler pada <NAMA>_HAIR (anak HEAD) tiap frame. Amplitudo kecil (<= ~3 derajat).
import bpy, json, math
from mathutils import Quaternion, Vector, Matrix

HEAD_ROT = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\render\head_rot.json"

def apply_hair_spring(nm, key, k=0.10, c=0.26, m=0.9, max_deg=3.2, path=HEAD_ROT):
    Q = [Quaternion(q) for q in json.load(open(path))[key]]
    sc = bpy.context.scene; sc.frame_set(1)
    rig = bpy.data.objects["RIG_" + nm]; head = bpy.data.objects[nm + "_HEAD"]; hair = bpy.data.objects[nm + "_HAIR"]
    Rb = (rig.matrix_world @ rig.pose.bones["head"].matrix).to_quaternion()
    C = Rb.inverted() @ head.matrix_world.to_quaternion()               # offset tetap tulang -> objek HEAD
    omega_prev = Vector((0, 0, 0)); th = Vector((0, 0, 0)); v = Vector((0, 0, 0)); lim = math.radians(max_deg)
    if hair.animation_data: hair.animation_data_clear()
    hair.rotation_mode = 'XYZ'; n = len(Q)
    out = []
    for i in range(1, n):
        d = Q[i] @ Q[i - 1].inverted(); ax, an = d.to_axis_angle()
        if an > math.pi: an -= 2 * math.pi
        omega = ax * an                                                    # kecepatan sudut dunia (rad/frame)
        a = omega - omega_prev; omega_prev = omega
        acc = -k * th - c * v - m * a
        v += acc; th += v
        if th.length > lim: th *= lim / th.length; v *= 0.5
        Ro = (Q[i] @ C)
        loc = Ro.inverted() @ th                                           # ke sumbu lokal objek HEAD (hair lokal = HEAD lokal)
        out.append((i + 1, Vector(loc)))
    for f, e in out:
        hair.rotation_euler = (e.x, e.y, e.z)
        hair.keyframe_insert("rotation_euler", frame=f)
    return {"keys": len(out), "max_deg": round(max(math.degrees(e.length) for _, e in out), 2)}
