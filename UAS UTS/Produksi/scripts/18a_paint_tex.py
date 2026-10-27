# 18a - Tekstur "lukisan tangan" prosedural (sapuan kuas, noda cat air, batu bercat) -> Produksi/assets/paint/*.png
# Hanya Pillow (tanpa numpy). Jalankan: python -I 18a_paint_tex.py
import os, random, math
from PIL import Image, ImageDraw, ImageFilter, ImageChops

OUT = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\assets\paint"
os.makedirs(OUT, exist_ok=True)
SZ = 1024

def _wash(rnd, cells, sigma, amp):
    """Gambar RGB gaussian-blur noise rata-rata 128 -> dipakai sebagai offset warna halus."""
    base = Image.effect_noise((cells, cells), 64)
    im = base.resize((SZ, SZ), Image.BICUBIC).filter(ImageFilter.GaussianBlur(sigma))
    im = Image.eval(im, lambda v: int(max(0, min(255, 128 + (v - 128) * amp))))
    return Image.merge("RGB", (im, im, im))

def _strokes(img, rnd, n, base, var, length, width, angle, jitter, alpha=70):
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(n):
        x, y = rnd.random() * SZ, rnd.random() * SZ
        a = math.radians(angle + rnd.gauss(0, jitter))
        L = length * (0.5 + rnd.random())
        col = tuple(max(0, min(255, int(c + rnd.gauss(0, var * 0.4)))) for c in base)
        w = max(1, int(width * (0.6 + rnd.random() * 0.8)))
        for ox in (-SZ, 0, SZ):
            for oy in (-SZ, 0, SZ):
                d.line((x + ox, y + oy, x + ox + math.cos(a) * L, y + oy + math.sin(a) * L), fill=(*col, alpha), width=w)

def painted(name, base, var=10, n=2600, length=90, width=14, angle=0, jitter=12, wash=14, seed=1, save=True):
    rnd = random.Random(seed)
    img = Image.new("RGB", (SZ, SZ), tuple(base))
    for cells, sigma, amp in ((8, 38, wash / 40), (24, 10, wash / 70)):
        w = _wash(rnd, cells, sigma, amp)
        img = ImageChops.add(img, w, 1.0, -128)
    _strokes(img, rnd, n, base, var, length, width, angle, jitter)
    _strokes(img, rnd, n // 3, [min(c + 22, 255) for c in base], var, length * 0.6, width * 0.7, angle, jitter, 55)
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    if save: img.save(os.path.join(OUT, name + ".png"))
    return img

def cobble(name, base=(160, 152, 138), seed=3, cell=128):
    rnd = random.Random(seed)
    img = Image.new("RGB", (SZ, SZ), tuple(int(c * 0.55) for c in base))
    d = ImageDraw.Draw(img)
    y = 0
    while y < SZ:
        h = int(cell * (0.45 + rnd.random() * 0.2)); x = -int(rnd.random() * cell)
        while x < SZ:
            w = int(cell * (0.8 + rnd.random() * 0.7))
            tone = rnd.gauss(0, 14)
            col = tuple(max(0, min(255, int(base[i] + tone + rnd.gauss(0, 7)))) for i in range(3))
            d.rounded_rectangle((x + 4, y + 4, x + w - 4, y + h - 4), radius=14, fill=col)
            x += w
        y += h
    img = img.filter(ImageFilter.GaussianBlur(1.6))
    _strokes(img, rnd, 1800, base, 12, 70, 12, 8, 25, 60)
    img.save(os.path.join(OUT, name + ".png"))

def planks(name, base, seed=5):
    rnd = random.Random(seed)
    img = painted(name, base, var=14, n=3200, length=230, width=10, angle=0, jitter=3, wash=10, seed=seed, save=False)
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(8):
        y = int(i * SZ / 8 + rnd.randint(-4, 4)); d.line((0, y, SZ, y), fill=(60, 30, 15, 150), width=5)
    img.save(os.path.join(OUT, name + ".png"))

def make_all():
    painted("p_plaster_cream", (238, 214, 168), 8, 2400, 110, 16, -8, 10, 16, 11)
    painted("p_plaster_mint", (196, 220, 200), 8, 2400, 110, 16, -8, 10, 14, 12)
    painted("p_plaster_peach", (240, 196, 160), 8, 2400, 110, 16, -8, 10, 14, 13)
    painted("p_plaster_sky", (176, 208, 226), 8, 2400, 110, 16, -8, 10, 14, 14)
    painted("p_road", (120, 118, 122), 8, 2800, 140, 14, 0, 6, 12, 15)
    painted("p_grass", (120, 170, 80), 14, 3400, 60, 9, 80, 25, 18, 16)
    painted("p_roof", (186, 96, 64), 12, 2600, 160, 10, 0, 3, 10, 17)
    cobble("p_cobble", (160, 152, 138), 18)
    planks("p_planks", (156, 90, 56), 19)
    planks("p_planks_dark", (96, 56, 38), 20)
    print("tekstur lukisan:", sorted(os.listdir(OUT)))

if __name__ == "__main__":
    make_all()
    names = ["p_plaster_cream", "p_road", "p_cobble", "p_planks", "p_grass", "p_roof"]
    sheet = Image.new("RGB", (768, 512))
    for i, nme in enumerate(names):
        sheet.paste(Image.open(os.path.join(OUT, nme + ".png")).resize((256, 256)), ((i % 3) * 256, (i // 3) * 256))
    os.makedirs(os.path.join(os.path.dirname(OUT), "..", "preview"), exist_ok=True)
    sheet.save(os.path.join(os.path.dirname(OUT), "..", "preview", "paint_sheet.png"))
