# 35 - Pass wajah bergaya Ghibli: mata lebih kecil & tenang (iris besar gelap, sklera krem sedikit), garis kelopak atas tegas, batas gerak mata.
# Pakai: ghibli_eyes(["LASTRI","MHS"], scale=0.80)   (idempoten: bisa dijalankan ulang)
import bpy, math
D = math.radians

IRIS = {"T_Eye_Lastri": (0.17, 0.09, 0.045, 1.0), "T_Eye_Cust": (0.15, 0.085, 0.045, 1.0)}
SCLERA = (0.95, 0.90, 0.83, 1.0)
PUPIL = (0.012, 0.008, 0.007, 1.0)

def eye_mat(mn, iris_cos=0.58, ring=0.035, pupil_cos=0.86):
    nt = bpy.data.materials[mn].node_tree; N = nt.nodes
    N["Math.001"].inputs[1].default_value = iris_cos            # batas iris (cos sudut dari sumbu pandang)
    N["Math.002"].inputs[1].default_value = iris_cos + ring     # cincin gelap tepi iris
    N["Math.003"].inputs[1].default_value = pupil_cos           # pupil
    a = IRIS[mn]
    N["Mix"].inputs[6].default_value = a                        # warna iris (A, bagian atas)
    N["Mix"].inputs[7].default_value = (a[0] * 1.9, a[1] * 1.9, a[2] * 1.6, 1.0)   # B: bagian bawah sedikit lebih terang (kilau Ghibli)
    N["Mix.001"].inputs[6].default_value = SCLERA               # sklera
    N["Mix.003"].inputs[7].default_value = PUPIL

def ghibli_eyes(chars, scale=0.80, lid_line=0.0034):
    n = 0
    for mn in IRIS: eye_mat(mn)
    for ch in chars:
        for s in ("L", "R"):
            for part in ("eye", "lid", "lidlow"):
                o = bpy.data.objects.get(f"{ch}_{part}_{s}")
                if o: o.scale = (scale, scale, scale); n += 1
            e = bpy.data.objects[f"{ch}_eye_{s}"]
            for c in [c for c in e.constraints if c.type == 'LIMIT_ROTATION']: e.constraints.remove(c)
            c = e.constraints.new('LIMIT_ROTATION'); c.name = "EYE_LIMIT"; c.owner_space = 'LOCAL'
            c.use_limit_x = True; c.min_x = D(-18); c.max_x = D(18); c.use_limit_z = True; c.min_z = D(-30); c.max_z = D(30)
            c.use_limit_y = True; c.min_y = 0; c.max_y = 0
            lid = bpy.data.objects.get(f"{ch}_lid_{s}")
            if lid:
                for m in lid.modifiers:
                    if m.type == 'SOLIDIFY': m.thickness = lid_line
    return n
