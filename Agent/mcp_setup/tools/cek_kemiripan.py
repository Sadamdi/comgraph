
"""Cek kemiripan hasil praktikum (.blend) terhadap ilustrasi PDF modul.

Pakai:  1) buka Blender (port 9876 harus LISTENING)
        2) python "Agent/tools/cek_kemiripan.py"
Hasil:  tabel IoU di terminal + gambar perbandingan di Agent/hasil_cek/
"""
import json, os, socket

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT  = os.path.join(ROOT, "Agent", "hasil_cek")
os.makedirs(OUT, exist_ok=True)
OUTU = OUT.replace("\\", "/") + "/"

MODUL = [
 ("Modul 3","Pertemuan 3/Modul 3 - Modelling Rocket.blend",
  "Pertemuan 3/Modul 3 - Modelling Rocket.pdf",12,0,
  dict(shading="SOLID", persp=True, orbit=(0.10,0.06), crop=(360,60,760,640))),
 ("Modul 4","Pertemuan 4/Modul 4 - Modelling Character Part 1.blend",
  "Pertemuan 4/Modul 4 - Modelling Character Part 1.pdf",11,0, dict(shading="SOLID", crop=(60,45,900,600))),
 ("Modul 5","Pertemuan 5/Modul 5 - Modelling Character Part 2.blend",
  "Pertemuan 5/Modul 5 - Modelling Character Part 2.pdf",17,1, dict(shading="SOLID", crop=(190,40,900,600))),
 ("Modul 6","Pertemuan 6/Modul 6 - Modelling Character Part 3.blend",
  "Pertemuan 6/Modul 6 - Modelling Character Part 3.pdf",15,1, dict(shading="MATERIAL", crop=(330,60,800,600))),
 ("Modul 7","Pertemuan 7/Modul 7 - Rigging.blend",
  "Pertemuan 7/Modul 7 - Rigging.pdf",8,0, dict(shading="SOLID", rest=True, overlay=True, crop=(150,50,1030,600))),
 ("Modul 8","Pertemuan 8/Modul 8 - Animating.blend",
  "Pertemuan 8/Modul 8 - Animating.pdf",2,1, dict(shading="MATERIAL", axis="RIGHT", frame=1, crop=(120,50,1050,600))),
]

def blender(code, timeout=240):
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(timeout)
    s.connect(("127.0.0.1",9876))
    s.sendall(json.dumps({"type":"execute_code","params":{"code":code}}).encode())
    buf=b""
    while True:
        try: ch=s.recv(65536)
        except socket.timeout: break
        if not ch: break
        buf+=ch
        try: json.loads(buf.decode()); break
        except Exception: continue
    s.close()
    return json.loads(buf.decode())

TPL = """
import bpy
BASE = %(root)r.replace(chr(92), "/") + "/"
bpy.ops.wm.open_mainfile(filepath=BASE + %(blend)r)
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = 900, 1100
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = 'PNG'
if %(frame)r: sc.frame_set(%(frame)r)
if %(rest)r and "Armature" in bpy.data.objects:
    bpy.data.objects["Armature"].data.pose_position = 'REST'
win = bpy.context.window_manager.windows[0]
area = next(x for x in win.screen.areas if x.type == 'VIEW_3D')
region = next(r for r in area.regions if r.type == 'WINDOW')
sp = area.spaces.active
sp.overlay.show_overlays = %(overlay)r
if %(overlay)r:
    for a in ("show_floor","show_axis_x","show_axis_y","show_cursor",
              "show_object_origins","show_text"):
        if hasattr(sp.overlay, a): setattr(sp.overlay, a, False)
sp.shading.type = %(shading)r
with bpy.context.temp_override(window=win, screen=win.screen, area=area,
                               region=region, space_data=sp):
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.data.objects:
        if o.type == 'MESH': o.select_set(True)
    bpy.ops.view3d.view_axis(type=%(axis)r)
    sp.region_3d.view_perspective = 'PERSP' if %(persp)r else 'ORTHO'
    orb = %(orbit)r
    if orb:
        bpy.ops.view3d.view_orbit(type='ORBITLEFT', angle=orb[0])
        bpy.ops.view3d.view_orbit(type='ORBITUP', angle=orb[1])
    bpy.ops.view3d.view_selected()
    bpy.ops.object.select_all(action='DESELECT')
    sc.render.filepath = %(out)r + %(tag)r + ".png"
    bpy.ops.render.opengl(write_still=True, view_context=True)
print("ok")
"""

def render(blend, tag, o):
    code = TPL % dict(root=ROOT, blend=blend, out=OUTU, tag=tag,
        shading=o.get("shading","MATERIAL"), axis=o.get("axis","FRONT"),
        frame=o.get("frame"), rest=o.get("rest",False),
        overlay=o.get("overlay",False), persp=o.get("persp",False),
        orbit=o.get("orbit"))
    r = blender(code)
    if r.get("status") != "success":
        print("   gagal render:", str(r)[:200]); return False
    return True

def main():
    try:
        import numpy as np, pymupdf
        from PIL import Image, ImageDraw
        from scipy import ndimage as ndi
    except ImportError as e:
        print("Butuh paket:", e); print("  pip install pillow numpy scipy pymupdf"); return

    def siluet(path, tol=45, crop=None):
        im = Image.open(path).convert("RGB")
        if crop: im = im.crop(crop)
        a = np.array(im).astype(int)
        q = (a//8)*8
        u,c = np.unique(q.reshape(-1,3), axis=0, return_counts=True)
        m = np.abs(a-u[c.argmax()]).sum(2) > tol
        m = ndi.binary_opening(m, np.ones((5,5)))
        m = ndi.binary_closing(m, np.ones((5,5)))
        l,n = ndi.label(m)
        if n == 0: return None, None
        s = ndi.sum(m,l,range(1,n+1))
        m = ndi.binary_fill_holes(l == np.argmax(s)+1)
        ys,xs = np.flatnonzero(m.any(1)), np.flatnonzero(m.any(0))
        return m[ys[0]:ys[-1]+1, xs[0]:xs[-1]+1], im.crop((xs[0],ys[0],xs[-1]+1,ys[-1]+1))

    def norm(m, S=240):
        h,w = m.shape; s = S/max(h,w)
        i = Image.fromarray((m*255).astype(np.uint8)).resize(
            (max(1,int(w*s)), max(1,int(h*s))), Image.NEAREST)
        c = Image.new("L",(S,S),0); c.paste(i, ((S-i.width)//2,(S-i.height)//2))
        return np.array(c) > 127

    print(); print("%-10s %-14s %11s" % ("Modul","referensi","IoU siluet"))
    print("-"*39)
    for nama, blend, pdf, hal, idx, o in MODUL:
        if not os.path.exists(os.path.join(ROOT, blend)):
            print("%-10s file .blend belum ada" % nama); continue
        tag = nama.replace(" ","_").lower()
        if not render(blend, tag, o): continue
        d = pymupdf.open(os.path.join(ROOT, pdf))
        imgs = d[hal-1].get_images(full=True)
        if idx >= len(imgs):
            print("%-10s hal.%d tidak punya gambar ke-%d" % (nama,hal,idx)); continue
        pix = pymupdf.Pixmap(d, imgs[idx][0])
        if pix.n > 4: pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        ref = os.path.join(OUT, tag+"_pdf.png"); pix.save(ref)
        A, ia = siluet(ref, crop=o.get('crop')); B, ib = siluet(os.path.join(OUT, tag+'.png'))
        if A is None or B is None:
            print("%-10s siluet gagal" % nama); continue
        a,b = norm(A), norm(B)
        iou = 100.0*(a&b).sum()/(a|b).sum()
        print("%-10s hal.%-10d %9.1f%%" % (nama, hal, iou))
        H = 640
        ia2 = ia.resize((int(ia.width*H/ia.height),H), Image.LANCZOS)
        ib2 = ib.resize((int(ib.width*H/ib.height),H), Image.LANCZOS)
        ov = np.zeros(a.shape+(3,), np.uint8); ov[...,0]=a*255; ov[...,1]=b*255
        io_ = Image.fromarray(ov).convert("RGB").resize((H,H), Image.NEAREST)
        cmp_ = Image.new("RGB", (ia2.width+ib2.width+io_.width+20, H+24), (15,15,15))
        dr = ImageDraw.Draw(cmp_)
        cmp_.paste(ia2,(0,24)); cmp_.paste(ib2,(ia2.width+10,24))
        cmp_.paste(io_,(ia2.width+ib2.width+20,24))
        dr.text((6,6), "%s - PDF hal.%d | punya saya | tumpang tindih (IoU %.0f%%)" % (nama,hal,iou),
                fill=(255,220,80))
        cmp_.save(os.path.join(OUT, tag+"_banding.png"))
    print(); print("Gambar perbandingan:", OUT)
    print("Merah = PDF, hijau = punya kamu, kuning = cocok.")

if __name__ == "__main__":
    main()
