# 99 - Bangun ulang seluruh animasi dari skrip (kecuali bake kain). Urutan wajib.
import bpy, time
SD = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\scripts" + "\\"
t = time.time()
exec(open(SD + "03c_fixes.py", encoding="utf8").read())
exec(open(SD + "12_rebuild_chars.py", encoding="utf8").read())
exec(open(SD + "09_boot.py", encoding="utf8").read())
for f in ("08a_scenes.py", "08b_scenes.py", "08c_scenes.py"):
    exec(open(SD + f, encoding="utf8").read())
run_A(); run_B(); run_C()
exec(open(SD + "11_props.py", encoding="utf8").read())
exec(open(SD + "10_cameras.py", encoding="utf8").read())
exec(open(SD + "13_light_comp.py", encoding="utf8").read())
print("SEMUA SELESAI", round(time.time() - t, 1), "detik")
