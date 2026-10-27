# 22c - Tampilan aplikasi dompet digital GENERIK (referensi tata letak: aplikasi e-wallet biru-putih, kartu saldo, ikon bulat, bottom sheet) TANPA merek/logo asli.
# Nama aplikasi fiktif: "DompetKu". Jalankan: python 22c_screens_v2.py  (Pillow saja)
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\assets\screens"
F = r"C:\Windows\Fonts" + "\\"
def font(sz, bold=False):
    for n in (("segoeuib.ttf" if bold else "segoeui.ttf"), ("arialbd.ttf" if bold else "arial.ttf")):
        try: return ImageFont.truetype(F + n, sz)
        except Exception: pass
W, H = 900, 1518
BLUE = (0, 150, 214); DBLUE = (0, 98, 160); NAVY = (20, 38, 66); GRAY = (108, 118, 134); LGRAY = (238, 241, 246); WHITE = (255, 255, 255)
GREEN = (30, 168, 96); RED = (218, 40, 52)

def new(bg=WHITE):
    im = Image.new("RGB", (W, H), bg); return im, ImageDraw.Draw(im)
def center(d, y, t, f, fill, x0=0, x1=W): w = d.textlength(t, font=f); d.text((x0 + (x1 - x0 - w) / 2, y), t, font=f, fill=fill)
def status(d, dark=False):
    c = WHITE if dark else NAVY
    d.text((44, 26), "09.41", font=font(34, True), fill=c)
    for i in range(4): d.rectangle((W - 230 + i * 18, 52 - i * 7, W - 218 + i * 18, 52), fill=c)
    d.rounded_rectangle((W - 130, 30, W - 50, 58), radius=7, outline=c, width=3); d.rectangle((W - 126, 34, W - 80, 54), fill=c)
def card(d, box, r=34, fill=WHITE, shadow=True):
    x0, y0, x1, y1 = box
    if shadow: d.rounded_rectangle((x0, y0 + 6, x1, y1 + 6), radius=r, fill=(214, 220, 230))
    d.rounded_rectangle(box, radius=r, fill=fill)
def icon_circle(d, cx, cy, r, fill, glyph):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)
    s = r * 0.45
    if glyph == "scan":
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            d.line((cx + sx * s, cy + sy * s, cx + sx * s * 0.4, cy + sy * s), fill=WHITE, width=7); d.line((cx + sx * s, cy + sy * s, cx + sx * s, cy + sy * s * 0.4), fill=WHITE, width=7)
        d.line((cx - s * 0.7, cy, cx + s * 0.7, cy), fill=WHITE, width=6)
    elif glyph == "plus":
        d.line((cx - s, cy, cx + s, cy), fill=WHITE, width=9); d.line((cx, cy - s, cx, cy + s), fill=WHITE, width=9)
    elif glyph == "send":
        d.polygon([(cx - s, cy + s * 0.9), (cx + s, cy), (cx - s, cy - s * 0.9), (cx - s * 0.4, cy)], fill=WHITE)
    elif glyph == "more":
        for i in (-1, 0, 1): d.ellipse((cx + i * s * 0.9 - 6, cy - 6, cx + i * s * 0.9 + 6, cy + 6), fill=WHITE)
    elif glyph == "check":
        d.line((cx - s, cy, cx - s * 0.2, cy + s * 0.8), fill=WHITE, width=14); d.line((cx - s * 0.2, cy + s * 0.8, cx + s, cy - s * 0.7), fill=WHITE, width=14)

def home():
    im, d = new(LGRAY)
    d.rectangle((0, 0, W, 540), fill=BLUE)
    d.ellipse((520, -200, 1100, 380), fill=(20, 168, 228))
    status(d, True)
    d.text((54, 110), "DompetKu", font=font(58, True), fill=WHITE); d.text((54, 184), "Selamat pagi, Bu Lastri", font=font(36), fill=(214, 240, 252))
    card(d, (44, 290, W - 44, 560))
    d.text((88, 322), "Saldo DompetKu", font=font(32), fill=GRAY); d.text((88, 372), "Rp 2.385.000", font=font(78, True), fill=NAVY)
    d.rounded_rectangle((88, 478, 420, 540), radius=31, fill=(226, 244, 252)); d.text((118, 486), "Lihat riwayat", font=font(30, True), fill=DBLUE)
    for i, (g, t, c) in enumerate((("scan", "Bayar", BLUE), ("plus", "Isi saldo", (255, 154, 28)), ("send", "Kirim", (118, 90, 220)), ("more", "Lainnya", (36, 176, 140)))):
        cx = 150 + i * 200; icon_circle(d, cx, 700, 62, c, g); center(d, 786, t, font(30, True), NAVY, cx - 100, cx + 100)
    d.text((54, 900), "Terima pembayaran QRIS", font=font(44, True), fill=NAVY)
    card(d, (44, 980, W - 44, 1220))
    d.rounded_rectangle((84, 1020, 214, 1150), radius=26, fill=(226, 244, 252)); d.rectangle((110, 1046, 136, 1072), fill=BLUE); d.rectangle((160, 1046, 186, 1072), fill=BLUE); d.rectangle((110, 1096, 136, 1122), fill=BLUE)
    d.text((250, 1030), "Kode QR toko", font=font(42, True), fill=NAVY); d.text((250, 1092), "Pasang di meja, pembayaran", font=font(30), fill=GRAY); d.text((250, 1132), "masuk otomatis.", font=font(30), fill=GRAY)
    d.rounded_rectangle((0, H - 130, W, H), radius=0, fill=WHITE); d.line((0, H - 130, W, H - 130), fill=LGRAY, width=3)
    for i, t in enumerate(("Beranda", "Promo", "Riwayat", "Profil")):
        center(d, H - 84, t, font(28, i == 0), BLUE if i == 0 else GRAY, i * 225, (i + 1) * 225)
    return im

def scan():
    im = Image.new("RGB", (W, H), (14, 18, 26)); d = ImageDraw.Draw(im); status(d, True)
    d.text((54, 110), "<", font=font(60, True), fill=WHITE); center(d, 112, "Pindai kode QR", font(48, True), WHITE)
    box = (150, 420, 750, 1020)
    # kisi samar di bidang pindai
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.rectangle((0, 0, W, H), fill=(0, 0, 0, 130)); od.rounded_rectangle(box, radius=40, fill=(0, 0, 0, 0)); im.paste(Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB"))
    d = ImageDraw.Draw(im)
    for (x0, y0, sx, sy) in ((box[0], box[1], 1, 1), (box[2], box[1], -1, 1), (box[0], box[3], 1, -1), (box[2], box[3], -1, -1)):
        d.line((x0, y0 + sy * 6, x0 + sx * 120, y0 + sy * 6), fill=(60, 210, 255), width=14); d.line((x0 + sx * 6, y0, x0 + sx * 6, y0 + sy * 120), fill=(60, 210, 255), width=14)
    d.line((box[0] + 24, 720, box[2] - 24, 720), fill=(60, 210, 255), width=6)
    center(d, 1070, "Arahkan kamera ke kode QR", font(38), WHITE)
    d.rounded_rectangle((300, 1250, 600, 1330), radius=40, fill=(40, 46, 58), outline=WHITE, width=3); center(d, 1268, "Senter", font(36, True), WHITE, 300, 600)
    return im

def confirm():
    im, d = new(LGRAY); d.rectangle((0, 0, W, 220), fill=WHITE); status(d); d.text((54, 110), "<", font=font(60, True), fill=NAVY); center(d, 112, "Konfirmasi pembayaran", font(46, True), NAVY)
    card(d, (44, 270, W - 44, 760))
    d.ellipse((84, 310, 196, 422), fill=(255, 238, 220)); center(d, 330, "WB", font(54, True), (214, 110, 20), 84, 196)
    d.text((228, 322), "Warung Bu Lastri", font=font(46, True), fill=NAVY); d.text((228, 382), "QRIS • Gorengan", font=font(30), fill=GRAY)
    d.line((84, 470, W - 84, 470), fill=LGRAY, width=4)
    d.text((88, 500), "Nominal", font=font(32), fill=GRAY); d.text((88, 550), "Rp 15.000", font=font(96, True), fill=NAVY)
    d.text((88, 690), "Biaya", font=font(30), fill=GRAY); d.text((W - 230, 690), "Gratis", font=font(30, True), fill=GREEN)
    card(d, (44, 800, W - 44, 1040))
    d.text((88, 830), "Bayar dengan", font=font(30), fill=GRAY); d.ellipse((88, 890, 168, 970), fill=BLUE); center(d, 902, "D", font(46, True), WHITE, 88, 168)
    d.text((196, 890), "DompetKu", font=font(42, True), fill=NAVY); d.text((196, 950), "Saldo Rp 2.385.000", font=font(30), fill=GRAY)
    d.rounded_rectangle((60, H - 220, W - 60, H - 90), radius=65, fill=BLUE); center(d, H - 196, "Bayar Rp 15.000", font(54, True), WHITE)
    return im

def success():
    im, d = new(WHITE); status(d)
    d.ellipse((W / 2 - 150, 250, W / 2 + 150, 550), fill=(224, 246, 234)); d.ellipse((W / 2 - 100, 300, W / 2 + 100, 500), fill=GREEN); icon_circle(d, W / 2, 400, 100, GREEN, "check")
    center(d, 620, "Pembayaran berhasil", font(58, True), NAVY); center(d, 710, "Rp 15.000", font(100, True), NAVY); center(d, 840, "ke Warung Bu Lastri", font(38), GRAY)
    card(d, (60, 960, W - 60, 1280))
    for i, (a, b) in enumerate((("Waktu", "09.43 • Hari ini"), ("Metode", "DompetKu"), ("No. referensi", "QR0042-9317"))):
        y = 995 + i * 100; d.text((100, y), a, font=font(32), fill=GRAY); w = d.textlength(b, font=font(32, True)); d.text((W - 100 - w, y), b, font=font(32, True), fill=NAVY)
    d.rounded_rectangle((60, H - 200, W - 60, H - 90), radius=55, fill=BLUE); center(d, H - 184, "Selesai", font(52, True), WHITE)
    return im

def received():
    im, d = new(LGRAY); d.rectangle((0, 0, W, 330), fill=BLUE); status(d, True)
    d.text((54, 110), "Kode QR toko", font=font(54, True), fill=WHITE); d.text((54, 190), "Warung Bu Lastri", font=font(36), fill=(214, 240, 252))
    d.text((54, 250), "Hari ini", font=font(32), fill=(214, 240, 252)); d.text((260, 236), "Rp 15.000", font=font(56, True), fill=WHITE)
    # banner notifikasi
    card(d, (40, 360, W - 40, 600), r=40)
    d.ellipse((80, 420, 190, 530), fill=GREEN); icon_circle(d, 135, 475, 55, GREEN, "check")
    d.text((222, 410), "Pembayaran diterima", font=font(46, True), fill=NAVY); d.text((222, 476), "Rp 15.000 • QRIS", font=font(38, True), fill=GREEN); d.text((222, 530), "Baru saja", font=font(28), fill=GRAY)
    d.text((54, 650), "Transaksi hari ini", font=font(42, True), fill=NAVY)
    rows = (("Pelanggan • QRIS", "Rp 15.000", "09.43", True), ("Pelanggan • QRIS", "Rp 8.000", "08.17", False), ("Pelanggan • QRIS", "Rp 22.000", "07.52", False))
    for i, (a, b, c, new_) in enumerate(rows):
        y = 730 + i * 170; card(d, (44, y, W - 44, y + 140), r=28)
        d.ellipse((80, y + 30, 160, y + 110), fill=(224, 246, 234)); icon_circle(d, 120, y + 70, 40, GREEN, "check")
        d.text((190, y + 28), a, font=font(34, True), fill=NAVY); d.text((190, y + 78), c + " • Berhasil", font=font(28), fill=GRAY)
        w = d.textlength(b, font=font(38, True)); d.text((W - 84 - w, y + 48), b, font=font(38, True), fill=GREEN)
    return im

def learn():
    im, d = new(LGRAY); d.rectangle((0, 0, W, 300), fill=BLUE); status(d, True)
    d.text((54, 110), "Aktifkan QR toko", font=font(56, True), fill=WHITE); d.text((54, 190), "Langkah mudah menerima QRIS", font=font(36), fill=(214, 240, 252))
    for i, (t, s) in enumerate((("Daftarkan usaha", "Isi nama warung dan alamat"), ("Cetak kode QR", "Tempel di meja jualan"), ("Mulai terima bayar", "Cek status di aplikasi"))):
        y = 360 + i * 300; card(d, (44, y, W - 44, y + 250))
        d.ellipse((84, y + 70, 190, y + 176), fill=BLUE); center(d, y + 82, str(i + 1), font(62, True), WHITE, 84, 190)
        d.text((224, y + 62), t, font=font(46, True), fill=NAVY); d.text((224, y + 128), s, font=font(32), fill=GRAY)
    d.rounded_rectangle((60, H - 200, W - 60, H - 90), radius=55, fill=BLUE); center(d, H - 184, "Lanjutkan", font(52, True), WHITE)
    return im

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    pages = {"phone_home": home(), "phone_scan": scan(), "phone_confirm": confirm(), "phone_success": success(), "phone_received": received(), "phone_learn": learn()}
    for k, im in pages.items(): im.save(os.path.join(OUT, k + ".png"))
    sheet = Image.new("RGB", (len(pages) * 300, 506), "white")
    for i, im in enumerate(pages.values()): sheet.paste(im.resize((300, 506)), (i * 300, 0))
    sheet.save(os.path.join(OUT, "..", "..", "preview", "screens_v2_sheet.png")); print("ok", list(pages))
