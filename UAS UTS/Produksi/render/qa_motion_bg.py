# QA gerak di proses Blender latar belakang: percepatan tangan/kepala (hentakan), sudut tekuk pergelangan, dan rotasi kepala per frame (utk gerak sekunder rambut).
# Keluaran: render/qa_motion.json , render/head_rot.json
import bpy, math, json, time
SC = bpy.context.scene
rigs = {"L": bpy.data.objects["RIG_LASTRI"], "M": bpy.data.objects["RIG_MHS"]}
tr = {}; bend = {}; headq = {"L": [], "M": []}; t0 = time.time()
for f in range(1, 2701):
    SC.frame_set(f)
    for k, r in rigs.items():
        mw = r.matrix_world
        for b in ("hand.L", "hand.R", "head", "forearm.L", "forearm.R", "foot.L", "foot.R"):
            tr.setdefault((k, b), []).append(tuple(mw @ r.pose.bones[b].head))
        hb = r.pose.bones["head"]; q = (mw @ hb.matrix).to_quaternion()
        headq[k].append((q.w, q.x, q.y, q.z))
        for s in ("L", "R"):
            fa = (mw @ r.pose.bones["forearm." + s].tail - mw @ r.pose.bones["forearm." + s].head).normalized()
            ha = (mw @ r.pose.bones["hand." + s].tail - mw @ r.pose.bones["hand." + s].head).normalized()
            bend.setdefault((k, s), []).append(math.degrees(fa.angle(ha)))
out = {"t": round(time.time() - t0)}
def acc(p, i): return math.dist([p[i][j] - 2 * p[i - 1][j] + p[i - 2][j] for j in range(3)], (0, 0, 0))
sp = []
for key, pts in tr.items():
    for i in range(2, len(pts)):
        a = acc(pts, i)
        lim = 0.03 if not key[1].startswith("foot") else 0.05
        if a > lim: sp.append((i + 1, key[0] + ":" + key[1], round(a, 3)))
out["spikes"] = sp; out["n_spikes"] = len(sp)
out["bend"] = {f"{k[0]}{k[1]}": {"max": round(max(v)), "over45": sum(1 for x in v if x > 45), "over60": sum(1 for x in v if x > 60), "frames_over60": [i + 1 for i, x in enumerate(v) if x > 60][:30]} for k, v in bend.items()}
json.dump(out, open(r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\render\qa_motion.json", "w"), indent=1)
json.dump(headq, open(r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\render\head_rot.json", "w"))
print("QA_MOTION_DONE", out["t"])
