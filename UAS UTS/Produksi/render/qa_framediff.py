# Analisis glitch dari render pratinjau kecil (qa_frames/q_####.png, tiap 6 frame): lonjakan perbedaan antar-frame (pop/flicker), terlalu gelap/terbakar.
import os, sys, glob, statistics
from PIL import Image, ImageChops, ImageStat

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(BASE, sys.argv[1] if len(sys.argv) > 1 else "qa_frames")
STRIDE = int(sys.argv[2]) if len(sys.argv) > 2 else 1
PAT = "f_*.png" if "frames_" in D else "q_*.png"
files = sorted(glob.glob(os.path.join(D, PAT)))[::STRIDE]
STEP = 6
# batas shot (marker) supaya potongan kamera tidak dihitung sebagai glitch
CUTS = [1, 241, 391, 541, 661, 841, 1081, 1321, 1501, 1741, 1951, 2101, 2311, 2461]
def is_cut(f0, f1): return any(f0 < c <= f1 for c in CUTS)

rows = []; prev = None; pf = None
for p in files:
    f = int(os.path.basename(p)[2:6]); im = Image.open(p).convert("RGB"); im = im.reduce(10) if im.width > 400 else im
    st = ImageStat.Stat(im); lum = sum(st.mean) / 3 / 255
    g = im.convert("L"); hist = g.histogram(); n = sum(hist)
    burn = sum(hist[250:]) / n; dark = sum(hist[:8]) / n
    diff = None
    if prev is not None and not is_cut(pf, f):
        diff = sum(ImageStat.Stat(ImageChops.difference(im, prev)).mean) / 3 / 255
    rows.append((f, lum, burn, dark, diff)); prev = im; pf = f

diffs = [r[4] for r in rows if r[4] is not None]
med = statistics.median(diffs); mad = statistics.median([abs(d - med) for d in diffs]) or 1e-4
thr = med + 8 * mad
spikes = [(r[0], round(r[4], 4)) for r in rows if r[4] is not None and r[4] > max(thr, med * 3)]
print(f"frame dianalisis: {len(rows)} | median diff {med:.4f} | ambang lonjakan {max(thr, med * 3):.4f}")
print("LONJAKAN antar-frame (kandidat pop/glitch):", spikes[:40])
print("terbakar >2% piksel:", [(r[0], round(r[2], 3)) for r in rows if r[2] > 0.02][:30])
print("terlalu gelap >25% piksel:", [(r[0], round(r[3], 2)) for r in rows if r[3] > 0.25][:30])
print("luminansi min/maks:", round(min(r[1] for r in rows), 2), round(max(r[1] for r in rows), 2))
with open(os.path.join(D, "_ringkasan.txt"), "w", encoding="utf8") as fh:
    for r in rows: fh.write("\t".join("" if v is None else f"{v:.4f}" if isinstance(v, float) else str(v) for v in r) + "\n")
