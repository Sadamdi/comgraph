# 01 - Render, color management, dunia (HDRI Poly Haven wide_street_02, CC0)
# Dijalankan lewat Blender MCP: exec(open(path, encoding="utf8").read())
import bpy, math

HDRI = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\assets\wide_street_02_2k_nosun.hdr"
SUN_AZ_IN_HDRI = math.degrees(math.atan2(-0.39, 0.92))   # hasil kalibrasi (-23 derajat)
SUN_AZ_TARGET = -125.0                                    # matahari datang dari kiri-depan kamera
SUN_STRENGTH_WORLD = 1.6
SUN_ELEV = 38.0
SUN_ENERGY = 4.2

sc = bpy.context.scene
r = sc.render
r.engine = 'BLENDER_EEVEE'
r.resolution_x, r.resolution_y, r.resolution_percentage = 1080, 1920, 100
r.fps = 30

# --- EEVEE Next ---
ev = sc.eevee
def tryset(obj, name, val):
    try:
        setattr(obj, name, val)
    except Exception as e:
        print("skip", name, "->", str(e)[:90])
tryset(ev, "taa_render_samples", 64)
tryset(ev, "use_raytracing", True)
tryset(ev, "ray_tracing_method", 'SCREEN')
tryset(ev, "use_shadows", True)
tryset(ev, "shadow_ray_count", 2)
tryset(ev, "shadow_step_count", 8)
tryset(ev, "use_fast_gi", True)
ro = ev.ray_tracing_options
tryset(ro, "resolution_scale", '2')
tryset(ro, "use_denoise", True)
tryset(r, "use_motion_blur", True)
tryset(ev, "motion_blur_shutter", 0.4)
tryset(r, "motion_blur_shutter", 0.4)

# --- color management ---
vs = sc.view_settings
try:
    vs.view_transform = 'AgX'
except TypeError as e:
    print("AgX tidak ada:", str(e)[:120])
    try: vs.view_transform = 'Filmic'
    except TypeError: vs.view_transform = 'Standard'
print("view_transform:", vs.view_transform)
print("looks:", [i.identifier for i in vs.bl_rna.properties["look"].enum_items])
vs.exposure = 0.0
vs.gamma = 1.0

# --- dunia: HDRI + ekstraksi matahari ---
w = bpy.data.worlds.get("Langit_Warung") or bpy.data.worlds.new("Langit_Warung")
sc.world = w
w.use_nodes = True
nt = w.node_tree
nt.nodes.clear()
tc = nt.nodes.new("ShaderNodeTexCoord")
mp = nt.nodes.new("ShaderNodeMapping")
env = nt.nodes.new("ShaderNodeTexEnvironment")
bg = nt.nodes.new("ShaderNodeBackground")
out = nt.nodes.new("ShaderNodeOutputWorld")
env.image = bpy.data.images.load(HDRI, check_existing=True)
mp.inputs["Rotation"].default_value[2] = math.radians(SUN_AZ_TARGET - SUN_AZ_IN_HDRI)
bg.inputs["Strength"].default_value = SUN_STRENGTH_WORLD
nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
nt.links.new(env.outputs["Color"], bg.inputs["Color"])
# Kamera melihat langit tropis (Nishita); HDRI dipakai untuk cahaya & pantulan saja
sky = nt.nodes.new("ShaderNodeTexSky")
sky.sky_type = 'MULTIPLE_SCATTERING'
for n, v in (("sun_elevation", math.radians(24)), ("sun_rotation", math.radians(40)), ("altitude", 5.0),
             ("air_density", 1.2), ("dust_density", 2.2), ("ozone_density", 1.0), ("sun_disc", False)):
    try: setattr(sky, n, v)
    except Exception as e: print("sky skip", n, str(e)[:60])
bg_sky = nt.nodes.new("ShaderNodeBackground"); bg_sky.inputs["Strength"].default_value = 0.9
nt.links.new(sky.outputs["Color"], bg_sky.inputs["Color"])
lp = nt.nodes.new("ShaderNodeLightPath")
mixs = nt.nodes.new("ShaderNodeMixShader")
nt.links.new(lp.outputs["Is Camera Ray"], mixs.inputs["Fac"])
nt.links.new(bg.outputs["Background"], mixs.inputs[1])
nt.links.new(bg_sky.outputs["Background"], mixs.inputs[2])
nt.links.new(mixs.outputs["Shader"], out.inputs["Surface"])
tryset(w, "sun_threshold", 1.0e6)   # tanpa ekstraksi matahari dari HDRI (matahari = lampu Sun sendiri)
print("world sun attrs:", [p for p in dir(w) if "sun" in p])

# --- matahari (lampu Sun) ---
cL = bpy.data.collections.get("12_LIGHTS")
if cL is None:
    cL = bpy.data.collections.new("12_LIGHTS")
    root = bpy.data.collections.get("10_PRODUKSI") or sc.collection
    root.children.link(cL)
sun = bpy.data.objects.get("SUN_Key")
if sun is None:
    ld = bpy.data.lights.new("SUN_Key", 'SUN'); sun = bpy.data.objects.new("SUN_Key", ld); cL.objects.link(sun)
from mathutils import Vector
az, el = math.radians(SUN_AZ_TARGET), math.radians(SUN_ELEV)
d = Vector((math.cos(el)*math.cos(az), math.cos(el)*math.sin(az), math.sin(el)))
sun.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
sun.data.energy = SUN_ENERGY; sun.data.angle = math.radians(1.0); sun.data.color = (1.0, 0.93, 0.80)
tryset(sun.data, "use_shadow", True)
for n in ("Cube",):
    pass
for n, v in (("look", 'AgX - Medium High Contrast'),):
    try: vs.look = v
    except Exception as e: print("look skip:", str(e)[:100])
print("OK render+world")
