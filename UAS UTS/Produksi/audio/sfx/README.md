# SFX - Satu Stiker, Satu Warung

Semua suara **disintesis lewat kode** (numpy/scipy, seed tetap) - placeholder kualitas draf.
Tim boleh menggantinya dengan SFX CC0 dari Freesound/Pixabay/Mixkit.

Format: WAV 48 kHz, 16-bit, stereo. SFX individual dinormalisasi puncak -3 dBFS.

## Membuat ulang

```
pip install numpy scipy matplotlib
python "..\..\scripts\make_sfx.py"
```

## Daftar file (hasil ukur)

| File | Durasi (dtk) | Puncak (dBFS) | RMS (dBFS) |
|---|---|---|---|
| amb_street.wav | 20.00 | -3.0 | -16.3 |
| footstep_a.wav | 0.28 | -3.0 | -20.2 |
| footstep_b.wav | 0.28 | -3.0 | -21.3 |
| footstep_c.wav | 0.28 | -3.0 | -20.1 |
| footsteps_walk.wav | 4.40 | -3.0 | -30.0 |
| tongs_clink.wav | 0.90 | -3.0 | -23.4 |
| paper_rustle.wav | 1.60 | -3.0 | -30.6 |
| bag_handoff.wav | 1.40 | -3.0 | -34.2 |
| wallet_open.wav | 0.90 | -3.0 | -24.0 |
| sign_creak.wav | 2.20 | -3.0 | -23.9 |
| qris_board_place.wav | 0.70 | -3.0 | -24.1 |
| phone_tap.wav | 0.25 | -3.0 | -24.3 |
| qr_scan_beep.wav | 0.14 | -3.0 | -5.1 |
| notif_chime.wav | 1.80 | -3.0 | -18.2 |
| pay_confirm_tap.wav | 0.32 | -3.0 | -24.7 |
| car_pass_L2R.wav | 6.00 | -3.0 | -23.2 |
| car_pass_R2L.wav | 6.00 | -3.0 | -21.7 |
| bird_chirps.wav | 6.00 | -3.0 | -18.1 |
| wind_gust.wav | 3.00 | -3.0 | -19.5 |
| frying_sizzle.wav | 8.00 | -3.0 | -24.4 |
| crowd_murmur.wav | 15.00 | -3.0 | -23.2 |

`amb_street`, `frying_sizzle`, `crowd_murmur` dibuat sebagai loop (crossfade ekor ke kepala).

## sfx_mix.wav

- Durasi: 90.000 dtk (4320000 sampel), 48 kHz stereo.
- Puncak: -6.4 dBFS, RMS: -27.4 dBFS.
- Loudness terintegrasi (K-weighting BS.1770, implementasi sendiri, perkiraan): -25.4 LUFS.
- Bed ambience (jalan + gumaman + gorengan) diskalakan ke -30.0 LUFS (terukur).
- SFX ditargetkan sekitar -22..-18 LUFS (diukur pada blok aktif 20 ms, bukan LUFS terintegrasi resmi);
  burung/angin sekitar -27, mobil -24.
- Cue sheet ada di bagian `build_mix()` pada `make_sfx.py`. Grafik: `sfx_mix_wave.png`.

## Catatan

- Belum didengarkan manusia; keseimbangan level dihitung, bukan dinilai telinga. Cek dan setel ulang bila perlu.
- Angka LUFS adalah perkiraan, bukan pengukuran meter berlisensi.
- Event yang levelnya dibatasi agar puncak tidak melebihi -8 dBFS: bag_handoff, car_pass_L2R, car_pass_R2L, footsteps_walk, paper_rustle, pay_confirm_tap, qris_board_place, sign_creak, tongs_clink, wallet_open.
