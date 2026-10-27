# 24a - Tekstur daun musim gugur realistis (bentuk elips bergerigi halus, urat daun, gradasi kuning->oranye->merah, bintik) RGBA 512x1024. Pillow saja.
import os, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

OUT = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\assets\paint"
W, H = 512, 768
def leaf(name, base, edge, seed):
    rnd = random.Random(seed)
    img = Image.new("RGB", (W, H), base); d = ImageDraw.Draw(img)
    # gradasi dari tengah ke tepi + noda
    for i in range(5200):
        x, y = rnd.randint(0, W), rnd.randint(0, H); r = rnd.randint(2, 9)
        t = rnd.random(); col = tuple(int(base[k] * (1 - t) + edge[k] * t + rnd.randint(-9, 9)) for k in range(3))
        d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(max(0, min(255, c)) for c in col))
    img = img.filter(ImageFilter.GaussianBlur(3)); d = ImageDraw.Draw(img)
    cx = W / 2
    # urat tengah & urat samping
    d.line((cx, 40, cx, H - 20), fill=tuple(int(c * 0.62) for c in base), width=9)
    for k in range(9):
        y = 120 + k * 70; L = 170 - abs(k - 4) * 14
        for sgn in (-1, 1):
            d.line((cx, y + 36, cx + sgn * L, y - 30), fill=tuple(int(c * 0.72) for c in base), width=4)
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    # bentuk alfa: daun runcing, tepi bergerigi halus
    mask = Image.new("L", (W, H), 0); md = ImageDraw.Draw(mask)
    pts = []
    for i in range(0, 361, 3):
        t = i / 360.0; y = 20 + t * (H - 40)
        wdt = math.sin(math.pi * t) ** 0.75 * 215
        wdt *= (1 + 0.035 * math.sin(i * 0.75))       # gerigi halus
        pts.append((cx + wdt, y))
    for i in range(360, -1, -3):
        t = i / 360.0; y = 20 + t * (H - 40)
        wdt = math.sin(math.pi * t) ** 0.75 * 215 * (1 + 0.035 * math.sin(i * 0.75 + 1.3))
        pts.append((cx - wdt, y))
    md.polygon(pts, fill=255)
    # tangkai
    md.rectangle((cx - 6, H - 40, cx + 6, H - 2), fill=255)
    edge_dark = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(9)))
    img = Image.composite(Image.new("RGB", (W, H), tuple(int(c * 0.55) for c in edge)), img, edge_dark.filter(ImageFilter.GaussianBlur(2)))
    out = img.convert("RGBA"); out.putalpha(mask.filter(ImageFilter.GaussianBlur(0.8)))
    out.save(os.path.join(OUT, name + ".png")); return out

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    A = leaf("leaf_a", (232, 168, 36), (190, 70, 20), 1); B = leaf("leaf_b", (206, 96, 30), (130, 36, 20), 2); C = leaf("leaf_c", (226, 196, 60), (196, 120, 30), 3)
    sheet = Image.new("RGB", (768, 384), (90, 110, 80))
    for i, im in enumerate((A, B, C)): sheet.paste(im.resize((256, 384)), (i * 256, 0), im.resize((256, 384)))
    sheet.save(os.path.join(OUT, "..", "..", "preview", "leaf_sheet.png")); print("ok")
