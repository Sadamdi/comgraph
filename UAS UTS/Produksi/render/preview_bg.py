# Pratinjau cepat gerak: resolusi 33%, 4 sampel, tiap frame ke-3 (10 fps) -> PNG di render/prev_<gaya>/. Dipakai: blender -b file.blend -P preview_bg.py -- <gaya>
import bpy, sys, os
gaya = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "pocari"
out = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\render\prev_" + gaya + "\\"
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
sc.render.resolution_percentage = 33; sc.eevee.taa_render_samples = 4
sc.render.image_settings.file_format = 'PNG'
sc.frame_step = 3
sc.render.filepath = out + "p_"
bpy.ops.render.render(animation=True)
print("PREVIEW_DONE")
