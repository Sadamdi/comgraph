# 22a - Tekstur papan QRIS (kode QR dummy, isi teks contoh BUKAN rekening) & tampilan layar ponsel (app pembayaran generik). Jalankan: python 22a_screens_tex.py
import os, segno
from PIL import Image, ImageDraw, ImageFont

OUT = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\assets\screens"
os.makedirs(OUT, exist_ok=True)
F = r"C:\Windows\Fonts" + "\\"
def font(sz, bold=False): return ImageFont.truetype(F + ("arialbd.ttf" if bold else "arial.ttf"), sz)
def center(d, y, text, f, fill, W): w = d.textlength(text, font=f); d.text(((W - w) / 2, y), text, font=f, fill=fill)

def qr_img(text, size):
    q = segno.make(text, error="m", micro=False)
    mods = q.matrix_iter(border=0)
    rows = [list(r) for r in mods]; n = len(rows)
    cell = size // n; img = Image.new("RGB", (cell * n, cell * n), "white"); d = ImageDraw.Draw(img)
    for y, r in enumerate(rows):
        for x, v in enumerate(r):
            if v: d.rectangle((x * cell, y * cell, (x + 1) * cell - 1, (y + 1) * cell - 1), fill=(20, 20, 20))
    return img

def board():
    W, H = 1024, 1300
    im = Image.new("RGB", (W, H), (250, 248, 243)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, W - 9, H - 9), radius=36, outline=(210, 205, 195), width=6)
    d.rectangle((14, 14, W - 15, 210), fill=(204, 28, 36))
    center(d, 38, "QRIS", font(150, True), "white", W)
    center(d, 215, "QR Code Standar Pembayaran Nasional", font(36, True), (60, 60, 60), W)
    q = qr_img("CONTOH-WARUNG-BU-LASTRI-BUKAN-REKENING-ILUSTRASI", 560)
    pad = 30; box = (W - q.width - pad * 2) // 2
    d.rounded_rectangle((box, 290, box + q.width + pad * 2, 290 + q.height + pad * 2), radius=24, fill="white", outline=(30, 30, 30), width=5)
    im.paste(q, (box + pad, 290 + pad))
    y = 290 + q.height + pad * 2 + 30
    center(d, y, "WARUNG BU LASTRI", font(70, True), (30, 30, 30), W)
    center(d, y + 90, "Gorengan Hangat Setiap Hari", font(38), (90, 90, 90), W)
    center(d, y + 150, "NMID : ID0000000000 (contoh)", font(34), (90, 90, 90), W)
    d.rectangle((14, H - 150, W - 15, H - 15), fill=(235, 232, 225))
    center(d, H - 135, "SATU QRIS UNTUK SEMUA", font(46, True), (204, 28, 36), W)
    center(d, H - 75, "Scan - Bayar - Selesai", font(36), (70, 70, 70), W)
    im.save(OUT + r"\qris_board.png")

def phone(name, kind):
    W, H = 600, 1012
    bg = {"learn": (246, 247, 251), "confirm": (246, 247, 251), "received": (240, 250, 243), "scan": (20, 22, 28)}[kind]
    im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)
    d.text((28, 22), "09.41", font=font(30, True), fill=(255, 255, 255) if kind == "scan" else (30, 30, 30))
    d.rounded_rectangle((W - 110, 26, W - 28, 52), radius=8, outline=(255, 255, 255) if kind == "scan" else (30, 30, 30), width=3)
    if kind == "learn":
        d.rectangle((0, 80, W, 230), fill=(204, 28, 36)); center(d, 110, "Aplikasi Pembayaran", font(44, True), "white", W); center(d, 168, "Terima QRIS untuk usaha", font(30), (255, 220, 220), W)
        for i, (t, s) in enumerate((("1  Buka menu QRIS", "Pilih 'Terima Pembayaran'"), ("2  Tampilkan kode QR", "Pasang di meja warung"), ("3  Cek status", "Pembayaran masuk otomatis"))):
            y = 290 + i * 190
            d.rounded_rectangle((36, y, W - 36, y + 160), radius=26, fill="white", outline=(222, 224, 232), width=3)
            d.ellipse((60, y + 36, 148, y + 124), fill=(255, 235, 235)); d.text((84, y + 52), t[0], font=font(54, True), fill=(204, 28, 36))
            d.text((170, y + 40), t[3:], font=font(36, True), fill=(30, 30, 30)); d.text((170, y + 92), s, font=font(28), fill=(100, 100, 100))
    elif kind == "scan":
        for i in range(4):
            x0, y0 = (110, 230) if i == 0 else (W - 110, 230) if i == 1 else (110, 700) if i == 2 else (W - 110, 700)
            sx = 1 if i % 2 == 0 else -1; sy = 1 if i < 2 else -1
            d.line((x0, y0, x0 + 90 * sx, y0), fill=(255, 255, 255), width=10); d.line((x0, y0, x0, y0 + 90 * sy), fill=(255, 255, 255), width=10)
        center(d, 120, "Arahkan ke kode QRIS", font(40, True), "white", W)
        center(d, 780, "Pindai kode QR penjual", font(32), (200, 200, 210), W)
    elif kind == "confirm":
        d.rectangle((0, 80, W, 170), fill="white"); d.text((36, 102), "<  Konfirmasi", font=font(40, True), fill=(30, 30, 30))
        d.rounded_rectangle((36, 210, W - 36, 520), radius=30, fill="white", outline=(222, 224, 232), width=3)
        d.text((70, 240), "Bayar ke", font=font(30), fill=(110, 110, 110)); d.text((70, 284), "WARUNG BU LASTRI", font=font(44, True), fill=(30, 30, 30))
        d.text((70, 360), "Nominal", font=font(30), fill=(110, 110, 110)); d.text((70, 402), "Rp 15.000", font=font(70, True), fill=(204, 28, 36))
        d.rounded_rectangle((36, 860, W - 36, 960), radius=50, fill=(204, 28, 36)); center(d, 884, "Bayar", font(48, True), "white", W)
    elif kind == "received":
        d.ellipse((W / 2 - 110, 200, W / 2 + 110, 420), fill=(60, 170, 90))
        d.line((W / 2 - 55, 315, W / 2 - 10, 365), fill="white", width=22); d.line((W / 2 - 12, 365, W / 2 + 62, 262), fill="white", width=22)
        center(d, 470, "Pembayaran Diterima", font(48, True), (30, 30, 30), W)
        center(d, 560, "Rp 15.000", font(84, True), (30, 130, 60), W)
        center(d, 680, "dari Pelanggan via QRIS", font(32), (100, 100, 100), W)
        d.rounded_rectangle((36, 860, W - 36, 960), radius=50, fill=(60, 170, 90)); center(d, 884, "Selesai", font(48, True), "white", W)
    im.save(OUT + "\\" + name + ".png")

board()
for n, k in (("phone_learn", "learn"), ("phone_scan", "scan"), ("phone_confirm", "confirm"), ("phone_received", "received")): phone(n, k)
sheet = Image.new("RGB", (1024 // 2 + 4 * 300, 650), "white")
sheet.paste(Image.open(OUT + r"\qris_board.png").resize((512, 650)), (0, 0))
for i, n in enumerate(("phone_learn", "phone_scan", "phone_confirm", "phone_received")): sheet.paste(Image.open(OUT + "\\" + n + ".png").resize((300, 506)), (512 + i * 300, 0))
sheet.save(os.path.join(OUT, "..", "..", "preview", "screens_sheet.png")); print("ok")
