# 03c - Perbaikan geometri set berdasarkan QA (idempoten): meja diperdangkal agar penjual bisa menjangkau tanpa menembus
import bpy
OB = bpy.data.objects
def fit_y(o, y0, y1):
    o.scale.y = o.scale.y * ((y1 - y0) / o.dimensions.y)
    bpy.context.view_layer.update()
    o.location.y = (y0 + y1) / 2
fit_y(OB["Counter top"], -0.26, 0.30)
fit_y(OB["Counter base"], -0.20, 0.30)
fit_y(OB["Plinth"], -0.23, 0.30) if "Plinth" in OB else None
# bibir papan meja dipertipis (5 cm) agar lengan tidak 'tersangkut'; badan meja dinaikkan agar permukaan tetap z=1.19
OB["Counter top"].scale.z = OB["Counter top"].scale.z * (0.05 / OB["Counter top"].dimensions.z)
bpy.context.view_layer.update()
OB["Counter top"].location.z = 1.19 - 0.025
OB["Counter base"].scale.z = OB["Counter base"].scale.z * (1.14 / OB["Counter base"].dimensions.z)
bpy.context.view_layer.update()
OB["Counter base"].location.z = 0.57
print("meja: top", [round(v, 3) for v in OB["Counter top"].dimensions], "base", [round(v, 3) for v in OB["Counter base"].dimensions])

# nampan + gorengan digeser 10 cm ke arah penjual agar baris belakang dalam jangkauan (idempoten lewat properti kustom)
for o in [x for x in OB if x.name == "Display tray" or x.name.startswith("Gorengan") or x.name == "Tongs"]:
    if not o.get("_geser_nampan"):
        o.location.y += 0.10; o["_geser_nampan"] = 1
print("nampan digeser")
