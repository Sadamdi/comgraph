# Bangun ulang SELURUH animasi dalam satu proses Blender latar (tanpa batas waktu MCP), lalu poles & simpan.
# blender -b COMGRAPH_V3_GHIBLI.blend -P rebuild_all_bg.py   (menimpa file .blend; salinan cadangan dibuat sebelum berjalan oleh pemanggil)
# Urutan: A (S01-S07) -> B (S08-S14) -> props+layar -> polish -> smooth_poles -> head_rot.json -> hair spring -> simpan
import bpy, time, json
SD = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\scripts" + "\\"
RD = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\render" + "\\"
t0 = time.time()
def run(name): exec(open(SD + name, encoding="utf8").read(), NS)
NS = globals()
NS["CLEAR_ANIM"] = True
for n in ("09_boot.py", "08a_scenes.py", "08b_scenes.py", "08c_scenes.py"): run(n)
for nm in ("S01", "S02", "S03", "S04", "S05", "S06", "S07"): NS[nm]()
NS["save_state"](); print("A selesai", round(time.time() - t0), flush=True)
NS["CLEAR_ANIM"] = False
for n in ("09_boot.py", "08a_scenes.py", "08b_scenes.py", "08c_scenes.py"): run(n)
for nm in ("S08", "S09", "S10", "S11", "S12", "S13", "S14"): NS[nm]()
NS["save_state"](); print("B selesai", round(time.time() - t0), flush=True)
for n in ("06_anim_core.py", "07_acting_lib.py", "11_props.py", "22b_screens_apply.py", "22d_screens_seq.py"): run(n)
print("props selesai", round(time.time() - t0), flush=True)
run("36_polish_anim.py")
for rn in ("RIG_LASTRI", "RIG_MHS"): NS["polish"](rn)
for rn in ("RIG_LASTRI", "RIG_MHS"): NS["smooth_poles"](rn)
print("polish selesai", round(time.time() - t0), flush=True)
sc = bpy.context.scene; hq = {"L": [], "M": []}
for f in range(1, 2701):
    sc.frame_set(f)
    for k, rn in (("L", "RIG_LASTRI"), ("M", "RIG_MHS")):
        r = bpy.data.objects[rn]; q = (r.matrix_world @ r.pose.bones["head"].matrix).to_quaternion(); hq[k].append((q.w, q.x, q.y, q.z))
json.dump(hq, open(RD + "head_rot.json", "w"))
run("37_hair_spring.py")
print(NS["apply_hair_spring"]("LASTRI", "L"), NS["apply_hair_spring"]("MHS", "M"), flush=True)
bpy.ops.wm.save_mainfile()
print("REBUILD_DONE", round(time.time() - t0), flush=True)
