# 27 - Kamera lebih sinematik: gerak genggam halus (noise F-curve pada kamera & target), napas lensa (focal length bergetar sangat kecil), rack-focus lembut di shot dialog.
import bpy, random
OB = bpy.data.objects

def add_noise(fc, scale, strength, seed):
    for m in list(fc.modifiers):
        if m.type == 'NOISE': fc.modifiers.remove(m)
    m = fc.modifiers.new('NOISE'); m.scale = scale; m.strength = strength; m.phase = seed; m.depth = 1

def fcurves(ob_or_data):
    ad = ob_or_data.animation_data
    if ad and ad.action:
        for layer in ad.action.layers:
            for st in layer.strips:
                for cb in st.channelbags:
                    for fc in cb.fcurves: yield fc

rnd = random.Random(3)
n = 0
for cam in [o for o in OB if o.type == 'CAMERA' and o.name.startswith("S") and o.name.endswith("_CAM")]:
    tgt = OB.get("TGT_" + cam.name)
    wide = cam.data.lens < 30
    amp_loc = 0.010 if wide else 0.004     # lensa panjang -> gerak lebih kecil agar tidak goyang berlebihan
    for fc in fcurves(cam):
        if fc.data_path == "location": add_noise(fc, rnd.uniform(70, 110), amp_loc, rnd.uniform(0, 100)); n += 1
    if tgt:
        for fc in fcurves(tgt):
            if fc.data_path == "location": add_noise(fc, rnd.uniform(60, 90), 0.008, rnd.uniform(0, 100)); n += 1
    for fc in fcurves(cam.data):
        if fc.data_path == "lens": add_noise(fc, 90, 0.12, rnd.uniform(0, 100)); n += 1
print("noise kamera:", n)
