# 09 - Bootstrap sesi animasi: muat pustaka, buat Char L & M, bersihkan animasi lama pada kedua tokoh
import bpy
SD = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\scripts" + "\\"
exec(open(SD + "06_anim_core.py", encoding="utf8").read())
exec(open(SD + "07_acting_lib.py", encoding="utf8").read())

def _clear(nm):
    for o in bpy.data.objects:
        if o.name.startswith((nm + "_lid", nm + "_brow", nm + "_eye")) and o.animation_data:
            o.animation_data_clear()
    r = bpy.data.objects["RIG_" + nm]
    if r.animation_data: r.animation_data_clear()
    for pb in r.pose.bones:
        pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
    m = bpy.data.objects[nm + "_mouth"]
    if m.data.shape_keys and m.data.shape_keys.animation_data:
        m.data.shape_keys.animation_data_clear()
    for k in m.data.shape_keys.key_blocks:
        if k.name != "Basis": k.value = 0.0
    for o in bpy.data.objects:
        if o.name.startswith(nm + "_lid_"): o.rotation_euler = (0, 0, 0)
        if o.name.startswith(nm + "_brow_"): o.location = (0, 0, 0); o.rotation_euler = (0, 0, 0)

if globals().get("CLEAR_ANIM", True):
    for nm in ("LASTRI", "MHS"):
        _clear(nm)
L = Char("LASTRI"); M = Char("MHS")
for c in (L, M):
    init_state(c)
_keep = not globals().get("CLEAR_ANIM", True)
setup_gaze(L, keep=_keep); setup_gaze(M, keep=_keep)
bpy.app.driver_namespace["L"] = L; bpy.app.driver_namespace["M"] = M
import copy
def save_state():
    """Simpan status akting antar panggilan MCP (namespace tidak persisten)."""
    bpy.app.driver_namespace["STATE"] = {nm: (copy.deepcopy(c.state), tuple(c.rig_loc), c.rig_yaw, copy.deepcopy(getattr(c, "last_hand", {})), dict(getattr(c, "pole_prev", {})))
                                         for nm, c in (("L", L), ("M", M))}
if not globals().get("CLEAR_ANIM", True) and "STATE" in bpy.app.driver_namespace:
    for nm, c in (("L", L), ("M", M)):
        st, loc, yaw, lh, pp = bpy.app.driver_namespace["STATE"][nm]
        c.state = copy.deepcopy(st); c.rig_loc = Vector(loc); c.rig_yaw = yaw; c.last_hand = copy.deepcopy(lh); c.pole_prev = dict(pp)
        c.rig.location = c.rig_loc; c.rig.rotation_euler = (0, 0, c.rig_yaw)      # pulihkan juga transform objek rig (kunci berikutnya memakai lokasi ini)
    print("status akting dipulihkan")
print("boot ok")
