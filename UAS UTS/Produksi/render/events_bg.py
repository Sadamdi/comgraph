# Ekstrak peristiwa dari animasi untuk sinkronisasi SFX: tapak kaki (kontak lantai), lintasan mobil, ketukan tangan, posisi kamera per frame.
# Jalankan: blender -b file.blend -P events_bg.py   -> render/events.json
import bpy, json, math, time
from mathutils import Vector
SC = bpy.context.scene; OB = bpy.data.objects
rigs = {"LASTRI": 0.22, "MHS": 0.0, "NPC1": 0.0, "NPC2": 0.0, "NPC3": 0.0, "NPC4": 0.0, "NPC5": 0.0, "NPC6": 0.0}
cars = [n for n in ("CAR_A", "CAR_B", "CAR_C", "CAR_D") if n in OB]
foot = {}; hips = {}; carp = {k: [] for k in cars}; cam = []; hand = {"LASTRI": [], "MHS": []}
t0 = time.time()
for f in range(1, 2701):
    SC.frame_set(f)
    c = SC.camera; cam.append(tuple(c.matrix_world.translation) + tuple(c.matrix_world.to_3x3().col[0]))
    for k in rigs:
        r = OB["RIG_" + k]; mw = r.matrix_world
        for s in ("L", "R"):
            foot.setdefault((k, s), []).append((mw @ r.pose.bones["foot." + s].tail).z)
        hips.setdefault(k, []).append(tuple(mw @ r.pose.bones["hips"].head))
    for k in hand:
        r = OB["RIG_" + k]; mw = r.matrix_world
        hand[k].append(tuple(mw @ r.pose.bones["hand.R"].head) + tuple(mw @ r.pose.bones["hand.L"].head))
    for n in cars: carp[n].append(tuple(OB[n].matrix_world.translation))
ev = {"cam": cam, "steps": [], "cars": [], "hand": hand}
for (k, s), zs in foot.items():
    fl = rigs[k]; inc = False
    for i in range(3, len(zs)):
        c = zs[i] < fl + 0.035
        if c and not inc and all(z >= fl + 0.035 for z in zs[max(0, i - 3):i]):
            h = hips[k]; sp = math.dist(h[i][:2], h[i - 2][:2]) / 2
            if sp > 0.012 or k.startswith("NPC"): ev["steps"].append((i + 1, k, s, round(sp, 4), [round(x, 2) for x in h[i]]))
        inc = c
for n, pts in carp.items():
    best = None
    for i, p in enumerate(pts):
        cp = Vector(cam[i][:3]); d = (Vector(p) - cp).length
        if best is None or d < best[1]: best = (i + 1, d)
    sp = (Vector(pts[min(len(pts) - 1, best[0] + 5)]) - Vector(pts[best[0] - 1])).length / 6
    ev["cars"].append({"name": n, "closest_frame": best[0], "dist": round(best[1], 2), "speed": round(sp, 3), "x0": pts[0][0], "x1": pts[-1][0], "dx": pts[min(len(pts) - 1, best[0] + 5)][0] - pts[best[0] - 1][0]})
json.dump(ev, open(r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\render\events.json", "w"))
print("EVENTS_DONE", len(ev["steps"]), round(time.time() - t0))
