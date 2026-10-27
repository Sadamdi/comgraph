# Render yang BISA DILANJUTKAN (aman dimatikan kapan saja). Dijalankan di dalam Blender background oleh mulai_render.ps1.
# - Frame yang sudah jadi dilewati; frame ditulis ke file .tmp lalu di-rename (tidak ada PNG setengah jadi).
# - Aman untuk loncat frame (animasi memakai keyframe/driver deterministik; cache kain di disk).
import bpy, os, sys, time

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0]; F0 = int(argv[1]); F1 = int(argv[2]); SAMPLES = int(argv[3]) if len(argv) > 3 else 48
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, 100
sc.eevee.taa_render_samples = SAMPLES
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'; sc.render.image_settings.color_depth = '8'
sc.render.use_overwrite = True; sc.render.use_file_extension = False

# bersihkan sisa tmp dari sesi yang terputus
for f in os.listdir(OUT):
    if f.endswith(".tmp"):
        try: os.remove(os.path.join(OUT, f))
        except OSError: pass

def final_path(fr): return os.path.join(OUT, f"f_{fr:04d}.png")
todo = [fr for fr in range(F0, F1 + 1) if not (os.path.exists(final_path(fr)) and os.path.getsize(final_path(fr)) > 20000)]
print(f"[render] {len(todo)} frame tersisa dari {F1 - F0 + 1} (rentang {F0}-{F1})", flush=True)
log = open(os.path.join(OUT, "_progress.txt"), "a", encoding="utf8")
t_all = time.time(); done = 0
for fr in todo:
    t = time.time()
    sc.frame_set(fr)
    tmp = final_path(fr) + ".tmp"
    sc.render.filepath = tmp
    bpy.ops.render.render(write_still=True)
    if os.path.exists(tmp):
        os.replace(tmp, final_path(fr)); done += 1
    dt = time.time() - t
    log.write(f"{fr}\t{dt:.1f}\n"); log.flush()
    avg = (time.time() - t_all) / done if done else dt
    print(f"[render] frame {fr} {dt:.1f}s | selesai {done}/{len(todo)} | sisa ~{(len(todo) - done) * avg / 3600:.1f} jam", flush=True)
print("[render] SELESAI rentang", F0, F1, flush=True)
