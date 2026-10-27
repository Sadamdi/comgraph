"""make_sfx.py - sintesis SFX + mix timeline untuk 'Satu Stiker, Satu Warung'.

Semua suara dibangkitkan lewat kode (numpy/scipy), seed tetap -> hasil deterministik.
Jalankan:  python make_sfx.py
Keluaran: Produksi/audio/sfx/*.wav, sfx_mix.wav, sfx_mix_wave.png, README.md
"""
import json
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, lfilter

SR = 48000
OUT = Path(__file__).resolve().parent.parent / "audio" / "sfx"
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- util
def R(seed):
    return np.random.default_rng(seed)


def _sos(kind, f, order):
    return butter(order, f, btype=kind, fs=SR, output="sos")


def lp(x, f, order=2):
    return sosfilt(_sos("low", f, order), x)


def hp(x, f, order=2):
    return sosfilt(_sos("high", f, order), x)


def bp(x, lo, hi, order=2):
    return sosfilt(_sos("band", [lo, hi], order), x)


def white(rng, n):
    return rng.standard_normal(n)


def slow(rng, n, hz):
    y = lp(white(rng, n), hz, 2)
    return y / (y.std() + 1e-12)


def tt(n):
    return np.arange(n) / SR


def S(x):
    return np.stack([x, x], 1)


def pan_st(x, p):
    p = np.clip(p, -1, 1)
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1)


def finalize(x, peak_db=-3.0, fade_in=0.004, fade_out=0.03):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = S(x)
    n = len(x)
    fi = int(fade_in * SR)
    fo = min(int(fade_out * SR), n // 4)
    if fi:
        x[:fi] *= np.linspace(0, 1, fi)[:, None]
    if fo:
        x[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return x * (10 ** (peak_db / 20) / (np.abs(x).max() + 1e-12))


def norm_only(x, peak_db=-3.0):
    return x * (10 ** (peak_db / 20) / (np.abs(x).max() + 1e-12))


def make_loop(x, n, xf):
    """x panjang n+xf (axis 0) -> loop mulus panjang n via crossfade ekor ke kepala."""
    out = x[:n].copy()
    w = np.linspace(0, 1, xf)
    shp = (xf,) + (1,) * (x.ndim - 1)
    wi = np.sqrt(w).reshape(shp)
    wo = np.sqrt(1 - w).reshape(shp)
    out[:xf] = x[:xf] * wi + x[n:n + xf] * wo
    return out


def exp_env(n, tau):
    return np.exp(-tt(n) / tau)


def add_at(buf, x, i):
    i = int(i)
    e = min(len(buf), i + len(x))
    if e > i:
        buf[i:e] += x[:e - i]


# ---------------------------------------------------------------- loudness (BS.1770 K-weighting, 48k)
_K1 = ([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585])
_K2 = ([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621])


def _kpow(x):
    x = x if x.ndim == 2 else S(x)
    p = 0
    for c in range(x.shape[1]):
        y = lfilter(*_K1, x[:, c])
        y = lfilter(*_K2, y)
        p = p + y * y
    return p


def lufs_integrated(x):
    p = _kpow(x)
    c = np.concatenate([[0], np.cumsum(p)])
    blk, hop = 19200, 4800
    idx = np.arange(0, len(p) - blk + 1, hop)
    ms = (c[idx + blk] - c[idx]) / blk
    l = -0.691 + 10 * np.log10(ms + 1e-20)
    ms1 = ms[l > -70]
    if len(ms1) == 0:
        return -99.0
    rel = -0.691 + 10 * np.log10(ms1.mean()) - 10
    ms2 = ms1[(-0.691 + 10 * np.log10(ms1)) > rel]
    return -0.691 + 10 * np.log10(ms2.mean())


def lufs_active(x):
    """Loudness hanya pada blok 20 ms yang aktif (<35 dB di bawah blok terkeras) - untuk SFX pendek."""
    p = _kpow(x)
    b = 960
    n = len(p) // b
    bm = p[:n * b].reshape(n, b).mean(1)
    act = bm[bm > bm.max() * 10 ** -3.5]
    return -0.691 + 10 * np.log10(act.mean())


# ---------------------------------------------------------------- sintesis
def bird_chirp(dur, f0, f1, vib_hz=0, vib_depth=0, curve=1.0, amp=1.0):
    n = int(dur * SR)
    t = tt(n)
    f = f0 + (f1 - f0) * (t / dur) ** curve + vib_depth * np.sin(2 * np.pi * vib_hz * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.22 * np.sin(2 * ph)
    env = np.sin(np.pi * t / dur) ** 1.5
    return amp * s * env


def bird_phrase(rng, kind=None):
    kind = kind or rng.choice(["tweet", "trill", "two"])
    parts = []
    if kind == "tweet":
        base = rng.uniform(2600, 3400)
        for _ in range(rng.integers(3, 6)):
            d = rng.uniform(0.07, 0.12)
            parts.append(bird_chirp(d, base, base * rng.uniform(1.25, 1.55), 30, 80, 1.3))
            parts.append(np.zeros(int(rng.uniform(0.05, 0.09) * SR)))
    elif kind == "trill":
        base = rng.uniform(3200, 4200)
        for _ in range(rng.integers(12, 18)):
            parts.append(bird_chirp(0.035, base, base * 1.12, 0, 0, 1.0, 0.8))
            parts.append(np.zeros(int(0.02 * SR)))
    else:
        base = rng.uniform(3600, 4600)
        parts.append(bird_chirp(0.16, base, base * 0.7, 25, 60, 0.8))
        parts.append(np.zeros(int(0.07 * SR)))
        parts.append(bird_chirp(0.2, base * 0.8, base * 0.55, 20, 50, 0.8, 0.8))
    return np.concatenate(parts)


def _street_channel(rng, n_total):
    lead = SR
    n = n_total + lead
    wind = lp(white(rng, n), 450, 2)
    wind = wind / wind.std() * (0.75 + 0.25 * np.tanh(slow(rng, n, 0.25)))
    wind2 = bp(white(rng, n), 250, 1400)
    wind2 = wind2 / wind2.std() * (0.55 + 0.4 * np.tanh(slow(rng, n, 0.15)))
    traffic = lp(white(rng, n), 120, 4)
    traffic = traffic / traffic.std() * (0.8 + 0.2 * np.tanh(slow(rng, n, 0.2)))
    t = tt(n)
    hum = 0.25 * np.sin(2 * np.pi * 48 * t + 1) + 0.18 * np.sin(2 * np.pi * 71 * t + 2)
    hum *= 0.7 + 0.3 * np.tanh(slow(rng, n, 0.3))
    hiss = bp(white(rng, n), 2500, 6000)
    hiss = hiss / hiss.std() * 0.05
    y = 0.35 * wind + 0.25 * wind2 + 0.55 * traffic + hum + hiss
    return y[lead:]


def amb_street():
    rng = R(101)
    N, xf = 20 * SR, 2 * SR
    chans = [make_loop(_street_channel(rng, N + xf), N, xf) for _ in range(2)]
    y = np.stack(chans, 1)
    y = y / np.abs(y).max() * 0.8
    for tb in (3.5, 9.0, 14.5):  # kicau dalam jarak jauh, jauh dari sambungan loop
        ph = bird_phrase(rng) * 0.05
        add_at_st = pan_st(ph, rng.uniform(-0.8, 0.8))
        i = int(tb * SR)
        y[i:i + len(ph)] += add_at_st
    return norm_only(y)


def foot_step(rng, tone=95, click=(1800, 4800), grit=1.0, dur=0.28):
    n = int(dur * SR)
    t = tt(n)
    f = tone * (0.65 + 0.35 * np.exp(-t / 0.04))
    thud = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.05)
    c = bp(white(rng, n), *click) * np.exp(-t / 0.006) * 2.2
    toe = np.zeros(n)
    k = int(0.055 * SR)
    toe[k:] = c[:n - k] * 0.4
    g = bp(white(rng, n), 700, 3000) * np.exp(-t / 0.03) * 0.9 * grit
    return thud * 1.1 + c + toe + g


STEP_VARIANTS = {
    "a": dict(tone=95, click=(1800, 4800), grit=1.0),
    "b": dict(tone=80, click=(1500, 4000), grit=1.6),
    "c": dict(tone=110, click=(2200, 5600), grit=0.8),
}


def footstep(v):
    rng = R({"a": 201, "b": 202, "c": 203}[v])
    return finalize(foot_step(rng, **STEP_VARIANTS[v]), fade_out=0.05)


def footsteps_walk():
    rng = R(210)
    n = int(4.4 * SR)
    buf = np.zeros((n, 2))
    keys = list(STEP_VARIANTS)
    for k in range(8):
        v = STEP_VARIANTS[keys[rng.integers(0, 3)]]
        p = dict(v)
        p["tone"] *= rng.uniform(0.93, 1.07)
        s = foot_step(rng, **p) * rng.uniform(0.8, 1.0)
        t0 = 0.1 + 0.5 * k + rng.uniform(-0.015, 0.015)
        add_at(buf, pan_st(s, 0.15 if k % 2 else -0.15), t0 * SR)
    return finalize(buf, fade_out=0.08)


def tongs_clink():
    rng = R(220)
    n = int(0.9 * SR)
    buf = np.zeros(n)
    modes = [(2100, 1.0, 0.12), (3270, 0.7, 0.09), (4510, 0.55, 0.07), (6130, 0.35, 0.05), (7900, 0.2, 0.035)]
    for t0, a, jit in ((0.0, 1.0, 1), (0.16, 0.45, 1.07)):
        m = int(0.7 * SR)
        t = tt(m)
        s = sum(a_ * np.sin(2 * np.pi * f * jit * t + rng.uniform(0, 6)) * np.exp(-t / d) for f, a_, d in modes)
        s += bp(white(rng, m), 3000, 9000) * np.exp(-t / 0.004) * 1.5
        add_at(buf, s * a, t0 * SR)
    return finalize(buf, fade_out=0.1)


def _rustle(rng, dur, density=160, lo=1500, hi=9000):
    n = int(dur * SR)
    imp = np.zeros(n)
    k = rng.poisson(density * dur)
    pos = rng.integers(0, n, k)
    amp = rng.exponential(1.0, k) ** 1.2
    # kerapatan dimodulasi agar seperti gerakan tangan
    mod = (0.3 + np.abs(slow(rng, n, 3.0))) ** 1.2
    imp[pos] = amp * rng.choice([-1, 1], k)
    grain = bp(white(rng, 240), lo, hi) * np.exp(-tt(240) / 0.0012)
    y = np.convolve(imp * mod, grain, mode="same")
    y += bp(white(rng, n), lo, hi) * 0.04 * mod
    return y


def paper_rustle():
    rng = R(230)
    n = int(1.6 * SR)
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 0.8
    return finalize(_rustle(rng, 1.6) * env, fade_in=0.02, fade_out=0.1)


def bag_handoff():
    rng = R(231)
    n = int(1.4 * SR)
    buf = np.zeros(n)
    r1 = _rustle(rng, 0.45, 150)
    r1 *= np.sin(np.pi * np.linspace(0, 1, len(r1)))
    add_at(buf, r1, 0.0)
    t = tt(int(0.3 * SR))
    f = 130 * (0.7 + 0.3 * np.exp(-t / 0.04))
    thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.07) * 2.0
    thump += lp(white(rng, len(t)), 500) * np.exp(-t / 0.02) * 2
    add_at(buf, thump, 0.55 * SR)
    r2 = _rustle(rng, 0.5, 130)
    r2 *= np.sin(np.pi * np.linspace(0, 1, len(r2))) * 0.7
    add_at(buf, r2, 0.7 * SR)
    return finalize(buf, fade_in=0.01, fade_out=0.12)


def wallet_open():
    rng = R(232)
    n = int(0.9 * SR)
    buf = np.zeros(n)
    m = int(0.28 * SR)
    t = tt(m)
    nz = bp(white(rng, m), 800, 4200)
    comb = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 85 * t + 0.5 * np.sin(2 * np.pi * 7 * t)))
    env = np.sin(np.pi * t / t[-1]) ** 0.6
    add_at(buf, nz * comb * env, 0.05 * SR)  # sobekan velcro lembut
    m2 = int(0.15 * SR)
    t2 = tt(m2)
    leather = lp(white(rng, m2), 700) * np.exp(-t2 / 0.025) * 2.0
    leather += np.sin(2 * np.pi * 210 * t2) * np.exp(-t2 / 0.04) * 0.6
    add_at(buf, leather, 0.42 * SR)
    return finalize(buf, fade_in=0.01, fade_out=0.15)


def sign_creak():
    rng = R(233)
    n = int(2.2 * SR)
    t = tt(n)
    parts = np.zeros(n)
    for t0, d, f0 in ((0.1, 1.0, 85), (1.2, 0.8, 70)):
        m = int(d * SR)
        tm = tt(m)
        f = f0 + 25 * np.sin(2 * np.pi * 1.3 * tm) + 12 * slow(rng, m, 8)
        ph = np.cumsum(f) / SR
        saw = (ph % 1.0) - 0.5
        y = bp(saw, 450, 1500, 2) + 0.5 * bp(saw, 1800, 2800, 2)
        y += bp(white(rng, m), 500, 2500) * 0.25
        y *= np.sin(np.pi * tm / d) ** 1.3 * (0.6 + 0.4 * np.abs(slow(rng, m, 5)))
        add_at(parts, y, t0 * SR)
    return finalize(parts, fade_in=0.05, fade_out=0.2)


def qris_board_place():
    rng = R(234)
    n = int(0.7 * SR)
    buf = np.zeros(n)

    def knock(amp):
        m = int(0.5 * SR)
        t = tt(m)
        f = 180 * (0.62 + 0.38 * np.exp(-t / 0.02))
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.06)
        s += lp(white(rng, m), 1800) * np.exp(-t / 0.012) * 1.6
        for fm, am, d in ((420, 0.5, 0.04), (760, 0.35, 0.03), (1240, 0.2, 0.02)):
            s += am * np.sin(2 * np.pi * fm * t + rng.uniform(0, 6)) * np.exp(-t / d)
        return s * amp

    add_at(buf, knock(1.0), 0)
    add_at(buf, knock(0.28), 0.085 * SR)
    return finalize(buf, fade_out=0.1)


def phone_tap():
    rng = R(235)
    n = int(0.25 * SR)
    t = tt(n)
    s = bp(white(rng, n), 1500, 4000) * np.exp(-t / 0.005) * 2.0
    s += np.sin(2 * np.pi * 420 * t) * np.exp(-t / 0.012) * 0.8
    s += lp(white(rng, n), 600) * np.exp(-t / 0.01) * 0.6
    return finalize(s, fade_out=0.05)


def qr_scan_beep():
    n = int(0.14 * SR)
    t = tt(n)
    s = np.sin(2 * np.pi * 1900 * t) + 0.15 * np.sin(2 * np.pi * 5700 * t)
    env = np.minimum(1, t / 0.004) * np.minimum(1, (t[-1] - t) / 0.012)
    return finalize(s * env, fade_in=0.002, fade_out=0.01)


def notif_chime():
    rng = R(236)
    n = int(1.8 * SR)
    buf = np.zeros(n)
    for t0, f, a in ((0.0, 784.0, 1.0), (0.2, 1174.7, 0.85)):
        m = int(1.4 * SR)
        t = tt(m)
        s = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t / 0.2)
             + 0.12 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.12)) * np.exp(-t / 0.35)
        s *= np.minimum(1, t / 0.006)
        add_at(buf, s * a, t0 * SR)
    # gema ruang tipis
    wet = np.zeros(n)
    for d, g in ((0.043, 0.25), (0.071, 0.18), (0.113, 0.12), (0.167, 0.08)):
        add_at(wet, buf * g, d * SR)
    return finalize(buf + wet, fade_in=0.004, fade_out=0.25)


def pay_confirm_tap():
    rng = R(237)
    n = int(0.32 * SR)
    t = tt(n)
    s = bp(white(rng, n), 1200, 3500) * np.exp(-t / 0.006) * 2.0
    s += np.sin(2 * np.pi * 330 * t) * np.exp(-t / 0.02)
    s += lp(white(rng, n), 500) * np.exp(-t / 0.015) * 1.0
    add_at(s, bp(white(rng, 200), 1500, 4000) * np.exp(-tt(200) / 0.003) * 0.5, 0.05 * SR)  # pantulan jari
    return finalize(s, fade_out=0.06)


def car_pass(seed, flip):
    rng = R(seed)
    dur, v, d, c = 6.0, 10.0, 5.0, 343.0
    N = int(dur * SR)
    t = tt(N)
    x = v * (t - 3.0)
    r = np.sqrt(x ** 2 + d ** 2)
    tau = t - r / c
    pad = int(0.4 * SR)
    ts = (np.arange(N + 2 * pad) - pad) / SR
    n = len(ts)
    f0 = 52 + 6 * np.sin(2 * np.pi * 0.7 * ts) + 1.5 * ts
    ph = 2 * np.pi * np.cumsum(f0) / SR
    eng = sum((1 / k ** 1.2) * np.sin(k * ph + rng.uniform(0, 6)) for k in range(1, 11))
    eng *= 1 + 0.2 * np.sin(2 * ph * 0.5)
    eng /= eng.std()
    tire = bp(white(rng, n), 250, 2500)
    tire = tire / tire.std() * (0.7 + 0.15 * slow(rng, n, 4))
    rumble = lp(white(rng, n), 150, 2)
    rumble = rumble / rumble.std() * 0.5
    src = 0.7 * eng + tire + rumble
    far = lp(src, 900, 2)
    near = np.interp(tau, ts, src)
    farv = np.interp(tau, ts, far)
    w = np.clip((r - 5) / 20, 0, 1)
    obs = ((1 - w) * near + w * farv) * (d / r)
    p = np.sin(np.arctan2(x, d))
    a = (p + 1) * np.pi / 4
    st = np.stack([obs * np.cos(a), obs * np.sin(a)], 1)
    if flip:
        st = st[:, ::-1].copy()
    return finalize(st, fade_in=0.3, fade_out=0.4)


def bird_chirps():
    rng = R(240)
    n = int(6.0 * SR)
    buf = np.zeros((n, 2))
    for t0, kind in ((0.2, "tweet"), (1.4, "trill"), (2.6, "two"), (3.7, "tweet"), (4.8, "trill")):
        ph = bird_phrase(rng, kind)
        st = pan_st(ph, rng.uniform(-0.7, 0.7))
        add_at(buf, st, t0 * SR)
        add_at(buf, st * 0.18, (t0 + 0.07) * SR)  # gema tipis
    return finalize(buf, fade_in=0.01, fade_out=0.2)


def wind_gust():
    rng = R(250)
    n = int(3.0 * SR)
    t = np.linspace(0, 1, n)
    env = np.sin(np.pi * t) ** 1.8 * (0.8 + 0.2 * np.tanh(slow(rng, n, 2.0)))
    chans = []
    for _ in range(2):
        a = lp(white(rng, n), 900, 2)
        a = a / a.std()
        b = bp(white(rng, n), 500, 900, 2)
        b = b / b.std() * 0.15 * (0.5 + 0.5 * np.tanh(slow(rng, n, 1.0)))
        chans.append((a + b) * env)
    return finalize(np.stack(chans, 1), fade_in=0.1, fade_out=0.3)


def frying_sizzle():
    rng = R(260)
    N, xf, lead = 8 * SR, SR, SR // 2

    def ch():
        n = N + xf + lead
        imp = np.zeros(n)
        k = rng.poisson(3500 * n / SR)
        imp[rng.integers(0, n, k)] = rng.exponential(1.0, k) * rng.choice([-1, 1], k)
        pops = np.zeros(n)
        kp = rng.poisson(5 * n / SR)
        pops[rng.integers(0, n, kp)] = rng.uniform(3, 8, kp)
        grain = bp(white(rng, 200), 3000, 9000) * np.exp(-tt(200) / 0.0008)
        y = np.convolve(imp, grain, mode="same")
        pg = bp(white(rng, 400), 1500, 6000) * np.exp(-tt(400) / 0.002)
        y += np.convolve(pops, pg, mode="same") * 0.6
        hiss = hp(white(rng, n), 4000) * (0.3 + 0.1 * slow(rng, n, 0.5))
        y = lp(y / y.std() + hiss, 7000, 2)
        return y[lead:]

    y = np.stack([make_loop(ch(), N, xf) for _ in range(2)], 1)
    return norm_only(y)


def crowd_murmur():
    rng = R(270)
    N, xf, lead = 15 * SR, 2 * SR, SR

    def vowel(src, f1, f2, f3):
        return bp(src, f1 * 0.85, f1 * 1.15) * 1.0 + bp(src, f2 * 0.88, f2 * 1.12) * 0.7 + bp(src, f3 * 0.9, f3 * 1.1) * 0.3

    def ch():
        n = N + xf + lead
        t = tt(n)
        out = np.zeros(n)
        for _ in range(8):
            f0 = rng.uniform(95, 230) * (1 + 0.06 * slow(rng, n, 0.8))
            ph = np.cumsum(f0) / SR
            glottal = (ph % 1.0) - 0.5  # saw
            glottal = np.diff(glottal, prepend=0) + 0.02 * glottal
            glottal += 0.03 * white(rng, n)
            va = vowel(glottal, rng.uniform(350, 800), rng.uniform(1000, 2300), rng.uniform(2600, 3200))
            vb = vowel(glottal, rng.uniform(350, 800), rng.uniform(1000, 2300), rng.uniform(2600, 3200))
            a = 0.5 + 0.5 * np.tanh(2 * slow(rng, n, 2.5))
            gp = np.arange(0, n / SR + 0.4, 0.2)
            syl = np.clip((np.interp(t, gp, rng.random(len(gp))) - 0.35) / 0.65, 0, 1) ** 1.5
            phrase = np.clip(0.5 + 0.8 * slow(rng, n, 0.25), 0, 1)
            v = (a * va + (1 - a) * vb) * syl * phrase
            out += v / (v.std() + 1e-9)
        out = lp(out, 3500, 2)
        return out[lead:]

    y = np.stack([make_loop(ch(), N, xf) for _ in range(2)], 1)
    return norm_only(y)


# ---------------------------------------------------------------- daftar
SFX = {}


def build_all():
    SFX["amb_street"] = amb_street()
    for v in "abc":
        SFX[f"footstep_{v}"] = footstep(v)
    SFX["footsteps_walk"] = footsteps_walk()
    SFX["tongs_clink"] = tongs_clink()
    SFX["paper_rustle"] = paper_rustle()
    SFX["bag_handoff"] = bag_handoff()
    SFX["wallet_open"] = wallet_open()
    SFX["sign_creak"] = sign_creak()
    SFX["qris_board_place"] = qris_board_place()
    SFX["phone_tap"] = phone_tap()
    SFX["qr_scan_beep"] = qr_scan_beep()
    SFX["notif_chime"] = notif_chime()
    SFX["pay_confirm_tap"] = pay_confirm_tap()
    SFX["car_pass_L2R"] = car_pass(280, False)
    SFX["car_pass_R2L"] = car_pass(281, True)
    SFX["bird_chirps"] = bird_chirps()
    SFX["wind_gust"] = wind_gust()
    SFX["frying_sizzle"] = frying_sizzle()
    SFX["crowd_murmur"] = crowd_murmur()


def write_wav(path, x):
    wavfile.write(path, SR, np.round(np.clip(x, -1, 1) * 32767).astype(np.int16))


# ---------------------------------------------------------------- mix
MIX_SECONDS = 90
clamped = []


def gain_for(name, x, target_lufs, extra_db=0.0, cap_db=-8.0):
    g = 10 ** ((target_lufs - lufs_active(x) + extra_db) / 20)
    cap = 10 ** (cap_db / 20) / np.abs(x).max()
    if g > cap:
        clamped.append(name)
        g = cap
    return g


def ramp_db(t_abs, ramp):
    ta, da, tb, db = ramp
    return np.interp(t_abs, [ta, tb], [da, db])


def place(buf, name, t, target=-20.0, extra=0.0, ramp=None, trunc=None, fade_tail=0.0):
    x = SFX[name]
    if trunc:
        x = x[:int(trunc * SR)].copy()
        if fade_tail:
            m = int(fade_tail * SR)
            x[-m:] *= np.linspace(1, 0, m)[:, None]
    g = gain_for(name, SFX[name], target, extra)
    y = x * g
    if ramp:
        tabs = t + tt(len(y))
        y = y * (10 ** (ramp_db(tabs, ramp) / 20))[:, None]
    add_at(buf, y, t * SR)


def build_mix():
    N = MIX_SECONDS * SR
    # --- bed kontinu
    def tile(name, rel_db):
        a = SFX[name]
        reps = int(np.ceil(N / len(a)))
        return np.tile(a, (reps, 1))[:N] * 10 ** (rel_db / 20)

    bed = tile("amb_street", 0) + tile("crowd_murmur", -8) + tile("frying_sizzle", -14)
    bed_l = lufs_integrated(bed)
    bed *= 10 ** ((-30 - bed_l) / 20)
    mix = bed.copy()
    info = {"bed_lufs_before": float(bed_l), "bed_lufs_after": float(lufs_integrated(bed))}

    amb_t, car_t = -27.0, -24.0
    for t in (5, 33, 47, 60):
        place(mix, "bird_chirps", t, amb_t, 0)
    for t in (2, 23, 44, 82):
        place(mix, "wind_gust", t, -27.0, 0)
    # mobil lewat (suasana)
    place(mix, "car_pass_L2R", 2.0, car_t)
    place(mix, "car_pass_R2L", 23.3, car_t)
    place(mix, "car_pass_L2R", 50.0, car_t)
    place(mix, "car_pass_R2L", 73.3, car_t)
    # 2-8 dagangan
    place(mix, "sign_creak", 3.0, -22, 0)
    place(mix, "tongs_clink", 2.5, -20, 0)
    place(mix, "tongs_clink", 4.0, -20, -1)
    place(mix, "paper_rustle", 5.0, -21, 0)
    place(mix, "tongs_clink", 6.5, -20, -1.5)
    # 8-13 langkah mendekat
    place(mix, "footsteps_walk", 8.1, -21, 0, ramp=(8.1, -14, 12.0, 0))
    place(mix, "paper_rustle", 15.0, -21, 0)
    place(mix, "wallet_open", 19.0, -20, 0)
    # 27-30 menjauh
    place(mix, "footsteps_walk", 27.5, -21, 0, ramp=(27.5, 0, 30.0, -22), trunc=2.9, fade_tail=0.4)
    for t in (38, 40, 42):
        place(mix, "phone_tap", t, -21, 0)
    place(mix, "qris_board_place", 44.1, -19, 0)
    # 49-51 mendekat (hanya 4 langkah pertama, lalu berhenti)
    place(mix, "footsteps_walk", 49.0, -21, 0, ramp=(49.0, -12, 51.0, 0), trunc=2.3, fade_tail=0.25)
    place(mix, "phone_tap", 58.5, -21, 0)
    place(mix, "qr_scan_beep", 60.0, -22, 0)
    place(mix, "pay_confirm_tap", 62.0, -20, 0)
    place(mix, "notif_chime", 66.5, -20, 0)
    place(mix, "paper_rustle", 72.5, -21, 0)
    place(mix, "bag_handoff", 73.5, -20, 0)
    # 77-86 menjauh (dua putaran langkah, fade panjang)
    place(mix, "footsteps_walk", 77.5, -21, 0, ramp=(77.5, 0, 86.0, -26), trunc=4.0, fade_tail=0.0)
    place(mix, "footsteps_walk", 81.5, -21, 0, ramp=(77.5, 0, 86.0, -26), trunc=4.3, fade_tail=0.5)

    fi, fo = int(0.05 * SR), int(0.5 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)[:, None]
    mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
    assert mix.shape == (N, 2)
    info["mix_peak_db"] = float(20 * np.log10(np.abs(mix).max()))
    info["mix_rms_db"] = float(20 * np.log10(np.sqrt((mix ** 2).mean())))
    info["mix_lufs"] = float(lufs_integrated(mix))
    return mix, info


def plot_mix(mix, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(2, 1, figsize=(14, 6.5), sharex=True, gridspec_kw={"height_ratios": [1, 1.4]})
    m = mix.mean(1)
    blk = SR // 50
    nb = len(m) // blk
    pk = np.abs(m[:nb * blk]).reshape(nb, blk).max(1)
    tx = np.arange(nb) * blk / SR
    ax[0].fill_between(tx, -pk, pk, color="#2a6f97", lw=0)
    ax[0].set_ylim(-0.5, 0.5)
    ax[0].set_ylabel("amplitudo")
    ax[0].set_title("sfx_mix.wav - waveform (mono) dan spektrogram")
    ax[1].specgram(m, NFFT=2048, Fs=SR, noverlap=1024, cmap="magma", vmin=-130, vmax=-40)
    ax[1].set_ylim(0, 10000)
    ax[1].set_ylabel("Hz")
    ax[1].set_xlabel("detik")
    ax[1].set_xlim(0, MIX_SECONDS)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def main():
    build_all()
    rows = []
    for name, x in SFX.items():
        x = np.asarray(x)
        write_wav(OUT / f"{name}.wav", x)
        pk = 20 * np.log10(np.abs(x).max())
        rms = 20 * np.log10(np.sqrt((x ** 2).mean()))
        rows.append((name, len(x) / SR, pk, rms))
    mix, info = build_mix()
    write_wav(OUT / "sfx_mix.wav", mix)
    plot_mix(mix, OUT / "sfx_mix_wave.png")

    # verifikasi dari file yang ditulis
    chk = []
    for name, dur, pk, rms in rows:
        sr, d = wavfile.read(OUT / f"{name}.wav")
        d = d.astype(np.float64) / 32768
        ok = (sr == SR and d.ndim == 2 and np.abs(d).max() < 0.999 and 20 * np.log10(np.sqrt((d ** 2).mean()) + 1e-12) > -80)
        chk.append(ok)
    sr, d = wavfile.read(OUT / "sfx_mix.wav")
    info["mix_samples"] = int(len(d))
    info["mix_seconds"] = len(d) / sr
    info["all_files_ok"] = bool(all(chk))
    info["peak_clamped_events"] = sorted(set(clamped))

    lines = ["# SFX - Satu Stiker, Satu Warung", "",
             "Semua suara **disintesis lewat kode** (numpy/scipy, seed tetap) - placeholder kualitas draf.",
             "Tim boleh menggantinya dengan SFX CC0 dari Freesound/Pixabay/Mixkit.", "",
             "Format: WAV 48 kHz, 16-bit, stereo. SFX individual dinormalisasi puncak -3 dBFS.", "",
             "## Membuat ulang", "",
             "```", "pip install numpy scipy matplotlib", "python \"..\\..\\scripts\\make_sfx.py\"", "```", "",
             "## Daftar file (hasil ukur)", "",
             "| File | Durasi (dtk) | Puncak (dBFS) | RMS (dBFS) |", "|---|---|---|---|"]
    for name, dur, pk, rms in rows:
        lines.append(f"| {name}.wav | {dur:.2f} | {pk:.1f} | {rms:.1f} |")
    lines += ["", "`amb_street`, `frying_sizzle`, `crowd_murmur` dibuat sebagai loop (crossfade ekor ke kepala).", "",
              "## sfx_mix.wav", "",
              f"- Durasi: {info['mix_seconds']:.3f} dtk ({info['mix_samples']} sampel), 48 kHz stereo.",
              f"- Puncak: {info['mix_peak_db']:.1f} dBFS, RMS: {info['mix_rms_db']:.1f} dBFS.",
              f"- Loudness terintegrasi (K-weighting BS.1770, implementasi sendiri, perkiraan): {info['mix_lufs']:.1f} LUFS.",
              f"- Bed ambience (jalan + gumaman + gorengan) diskalakan ke {info['bed_lufs_after']:.1f} LUFS (terukur).",
              "- SFX ditargetkan sekitar -22..-18 LUFS (diukur pada blok aktif 20 ms, bukan LUFS terintegrasi resmi);",
              "  burung/angin sekitar -27, mobil -24.",
              "- Cue sheet ada di bagian `build_mix()` pada `make_sfx.py`. Grafik: `sfx_mix_wave.png`.", "",
              "## Catatan", "",
              "- Belum didengarkan manusia; keseimbangan level dihitung, bukan dinilai telinga. Cek dan setel ulang bila perlu.",
              "- Angka LUFS adalah perkiraan, bukan pengukuran meter berlisensi."]
    if info["peak_clamped_events"]:
        lines.append(f"- Event yang levelnya dibatasi agar puncak tidak melebihi -8 dBFS: {', '.join(info['peak_clamped_events'])}.")
    (OUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"{'file':20s} {'dur':>7s} {'peak':>7s} {'rms':>7s}")
    for name, dur, pk, rms in rows:
        print(f"{name:20s} {dur:7.2f} {pk:7.1f} {rms:7.1f}")
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
