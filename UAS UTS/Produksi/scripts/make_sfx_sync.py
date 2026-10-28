"""make_sfx_sync.py - mix SFX yang DISINKRONKAN dengan animasi (render/events.json dari events_bg.py).
Tapak kaki per kontak lantai (tiap karakter, volume ~ 1/jarak ke kamera, pan dari posisi layar), mobil di titik terdekat ke kamera,
ketukan/gerakan benda pada frame sebenarnya. Waktu = frame/30 (video di-encode 30 fps; 2700 frame = 90 dtk).
Jalankan (Python yang punya numpy+scipy):  python make_sfx_sync.py     -> audio/sfx/sfx_mix.wav (menimpa mix lama)"""
import json, math
from pathlib import Path
import numpy as np
import make_sfx as M

SR = M.SR; FPS = 30.0
EV = json.load(open(Path(__file__).resolve().parent.parent / "render" / "events.json"))
M.build_all()
SFX = M.SFX
N = 90 * SR

def t(frame): return (frame - 1) / FPS
def cam_at(f): return EV["cam"][min(len(EV["cam"]) - 1, max(0, int(f) - 1))]

def pan_dist(f, pos):
    cx, cy, cz, rx, ry, rz = cam_at(f)
    dx, dy, dz = pos[0] - cx, pos[1] - cy, pos[2] - cz
    d = math.sqrt(dx * dx + dy * dy + dz * dz) + 1e-6
    side = (dx * rx + dy * ry + dz * rz) / d                      # -1 kiri .. +1 kanan relatif kamera
    return d, max(-0.8, min(0.8, side))

def place(buf, name, frame, gain_db, pan=0.0, dist=None, rate=1.0):
    x = SFX[name]
    if x.ndim == 1: x = M.S(x)
    g = M.gain_for(name, x, -20.0, gain_db)
    if dist is not None: g *= min(1.5, 1.8 / max(dist, 1.2)) ** 1.0
    y = x * g
    y = M.pan_st(y.mean(axis=1), pan) if abs(pan) > 1e-3 else y
    M.add_at(buf, y, t(frame) * SR)

def build():
    mix = np.zeros((N, 2))
    # bed kontinu (sama dengan mix lama)
    def tile(name, rel_db):
        a = SFX[name]; reps = int(np.ceil(N / len(a))); return np.tile(a, (reps, 1))[:N] * 10 ** (rel_db / 20)
    bed = tile("amb_street", 0) + tile("crowd_murmur", -8) + tile("frying_sizzle", -14)
    bed *= 10 ** ((-30 - M.lufs_integrated(bed)) / 20); mix += bed
    # tapak kaki sesuai kontak lantai (dibatasi 3 varian bergilir)
    var = ("footstep_a", "footstep_b", "footstep_c"); rng = np.random.default_rng(7); n_steps = 0
    for f, k, s, sp, pos in EV["steps"]:
        if k == "LASTRI": continue                                            # Bu Lastri berdiri; pergeseran bobot tidak berbunyi
        d, pan = pan_dist(f, pos)
        db = -4.0 if k == "MHS" else -9.0
        if d > 14: continue
        place(mix, var[rng.integers(0, 3)], f, db + rng.uniform(-1.2, 1.2), pan, d); n_steps += 1
    # mobil: puncak suara di frame terdekat ke kamera (file 6 dtk, puncak di ~3 dtk)
    for c in EV["cars"]:
        if c["dist"] > 20: continue
        name = "car_pass_L2R" if c["dx"] > 0 else "car_pass_R2L"
        place(mix, name, c["closest_frame"] - 3 * FPS, -23.0 + (0 if c["dist"] < 9 else -3))
    # peristiwa benda (frame dari skrip akting)
    for f in (1128, 1164, 1206, 1252, 1290): place(mix, "phone_tap", f, -1.0, -0.2)            # S07 ketukan layar
    place(mix, "qris_board_place", 1392, 0.0)                                                     # papan menyentuh meja
    place(mix, "qr_scan_beep", 1810, 0.0); place(mix, "pay_confirm_tap", 1895, 0.0)
    place(mix, "phone_tap", 1770, -2.0, 0.3); place(mix, "phone_tap", 1862, -2.0, 0.3)
    place(mix, "notif_chime", 1995, 0.0)                                                          # ponsel Bu Lastri setelah dicek
    place(mix, "wallet_open", 575, 0.0); place(mix, "paper_rustle", 445, 0.0)
    place(mix, "bag_handoff", 2250, 0.0); place(mix, "paper_rustle", 2215, -1.5)
    for f in (80, 125, 165): place(mix, "tongs_clink", f, -1.0, 0.1)                              # S01 penjepit + baki
    for f in (2176, 2200, 2228): place(mix, "tongs_clink", f, -1.5, 0.1)                          # S12 tiga gorengan masuk kantong
    place(mix, "sign_creak", 95, -3.0, 0.0); place(mix, "sign_creak", 2480, -4.0, 0.2)
    for fr in (150, 1020, 1480, 2060, 2540): place(mix, "bird_chirps", fr, -5.0)
    for fr in (70, 690, 1340, 2400): place(mix, "wind_gust", fr, -5.0)
    fi, fo = int(0.05 * SR), int(0.5 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)[:, None]; mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
    pk = float(np.abs(mix).max())
    if pk > 0.89: mix *= 0.89 / pk                                                               # puncak <= -1 dBFS
    return mix, n_steps

if __name__ == "__main__":
    mix, n = build()
    out = Path(__file__).resolve().parent.parent / "audio" / "sfx"
    M.write_wav(out / "sfx_mix.wav", mix)
    print("langkah:", n, "| puncak dBFS:", round(20 * math.log10(np.abs(mix).max()), 1), "| LUFS:", round(M.lufs_integrated(mix), 1), "| detik:", len(mix) / SR)
