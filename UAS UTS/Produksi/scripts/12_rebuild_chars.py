# 12 - Bangun ulang kedua tokoh (badan, wajah, rambut, pakaian, rig) tanpa menyentuh objek milik teman
import bpy, math
SD = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\scripts" + "\\"
PROT = {"LASTRI_PHONE", "LASTRI_PHONE_case", "LASTRI_PHONE_screen"}
for o in list(bpy.data.objects):
    if (o.name.startswith(("LASTRI_", "MHS_", "RIG_LASTRI", "RIG_MHS", "LOOK_", "ATT_", "BagItem")) and o.name not in PROT) or o.name.endswith("_tp"):
        bpy.data.objects.remove(o)
for a in [a for a in bpy.data.armatures if a.name in ("ARM_LASTRI", "ARM_MHS")]:
    bpy.data.armatures.remove(a)
exec(open(SD + "02b_toon.py", encoding="utf8").read())
exec(open(SD + "04d_assemble.py", encoding="utf8").read())
exec(open(SD + "05_rig.py", encoding="utf8").read())
C = bpy.data.collections["20_TOKOH"]
POLE = {"arm.L": 70, "arm.R": 110, "leg.L": -90, "leg.R": -90}
for kind, nm in (("lastri", "LASTRI"), ("pelanggan", "MHS")):
    A = assemble(kind, C)
    rig, res = build_rig(kind, A, C, nm)
    for side in ("L", "R"):
        for limb, bn in (("arm", "forearm"), ("leg", "shin")):
            ik = [c for c in rig.pose.bones[f"{bn}.{side}"].constraints if c.type == 'IK'][0]
            ik.pole_angle = math.radians(POLE[f"{limb}.{side}"])
    rig.location = (-0.30, 0.56, 0) if nm == "LASTRI" else (0.30, -0.60, 0)
print("tokoh dibangun ulang")
