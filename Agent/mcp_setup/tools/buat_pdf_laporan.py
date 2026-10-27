"""Susun PDF per modul: identitas + materi + screenshot Blender (dari screenshot_viewport_gui.py).
  python buat_pdf_laporan.py "<folder shots>"
"""
import sys, os, glob, pymupdf

SHOTS = sys.argv[1]
ROOT = "D:/adam kuliah/Semester 5/Computer Graphic Praktikum"
NAMA, NIM, KELAS = "Sulthan Adam Rahmadi", "240605110109", "K"
LABEL = {"front": "Tampak depan", "back": "Tampak belakang", "right": "Tampak kanan", "left": "Tampak kiri",
         "top": "Tampak atas", "persp": "Perspektif (serong kanan)", "persp2": "Perspektif (serong kiri)",
         "camera": "Dari kamera"}
# (nomor, materi, folder pertemuan, [(kunci shot, subjudul)])
MODUL = [
    (1, "Interface Blender", [("m1", "")]),
    (2, "Modelling Basket (Ring & Bola Basket)", [("m2", "")]),
    (3, "Modelling Rocket (Roket)", [("m3", "")]),
    (4, "Modelling Character Part 1 (Kepala dan Badan)", [("m4", "")]),
    (5, "Modelling Character Part 2 (Tangan dan Kaki)", [("m5", "")]),
    (6, "Modelling Character Part 3 (Baju, Celana, Sepatu, Rambut, Mata, Mulut)", [("m6", "")]),
    (7, "Rigging (Armature / Tulang)", [("m7", "")]),
    (8, "Animating (Pose Berjalan, Keyframe Frame 1-20)", [("m8", "")]),
    (9, "Animating Object (Keyframe dan Shape Keys)", [("m9", "")]),
    (10, "Basic Camera (Depth of Field)", [("m10", "")]),
    (11, "Fundamental Rendering (Lampu, Audio, Render)", [("m11a", "Praktikum: Tipe Lampu"), ("m11b", "Tugas: Animasi Karakter")]),
]


def caption(name):
    base = name.rsplit(".", 1)[0]
    parts = base.split("_")
    view = parts[-1]
    txt = LABEL.get(view, view)
    for p in parts:
        if p.startswith("f") and p[1:].isdigit():
            txt = "Frame %s - %s" % (p[1:], txt)
    return txt


def build(nomor, materi, groups):
    doc = pymupdf.open()
    W, H, M = 595, 842, 40
    page = None; y = 0

    def new_page(first=False):
        nonlocal page, y
        page = doc.new_page(width=W, height=H)
        y = M
        if first:
            page.insert_text((M, y + 16), "LAPORAN PRAKTIKUM GRAFIKA KOMPUTER", fontname="hebo", fontsize=15)
            page.insert_text((M, y + 36), "Modul %d" % nomor, fontname="hebo", fontsize=12)
            y += 56
            for k, v in (("Nama", NAMA), ("NIM", NIM), ("Kelas", KELAS), ("Materi", materi)):
                rect = pymupdf.Rect(M + 60, y, W - M, y + 30)
                page.insert_text((M, y + 11), k, fontname="helv", fontsize=11)
                page.insert_text((M + 50, y + 11), ":", fontname="helv", fontsize=11)
                page.insert_textbox(rect, v, fontname="helv", fontsize=11)
                y += 17 if len(v) < 70 else 30
            page.draw_line((M, y + 4), (W - M, y + 4), width=0.8)
            y += 18
            page.insert_text((M, y + 8), "Screenshot hasil di Blender", fontname="hebo", fontsize=11)
            y += 20

    new_page(True)
    iw = W - 2 * M
    for key, sub in groups:
        files = sorted(glob.glob(os.path.join(SHOTS, key, "*.png")),
                       key=lambda f: [int(c) if c.isdigit() else c for c in
                                      __import__("re").split(r"(\d+)", os.path.basename(f))])
        if sub:
            if y + 40 > H - M:
                new_page()
            page.insert_text((M, y + 12), sub, fontname="hebo", fontsize=11); y += 22
        for f in files:
            pix = pymupdf.Pixmap(f)
            ih = iw * pix.height / pix.width
            if y + ih + 20 > H - M:
                new_page()
            page.insert_image(pymupdf.Rect(M, y, M + iw, y + ih), filename=f)
            page.draw_rect(pymupdf.Rect(M, y, M + iw, y + ih), color=(0.6, 0.6, 0.6), width=0.5)
            page.insert_text((M, y + ih + 11), caption(os.path.basename(f)), fontname="heit", fontsize=9)
            y += ih + 22
    out_dir = "%s/Pertemuan %d" % (ROOT, nomor)
    out = "%s/%s_%s_Modul %d.pdf" % (out_dir, NIM, NAMA, nomor)
    doc.save(out); print(out, len(doc), "hal")


for n, materi, g in MODUL:
    build(n, materi, g)
