# Laporan Bukti Rubrik UAS (poin 1–10) — "Satu Stiker, Satu Warung"
Frame = bukti di `Produksi/frames/f_####.png`; file Blender: `COMGRAPHTHEORYUASLOMBA.blend`; video: `Final_Satu_Stiker_Satu_Warung.mp4`.
| Poin | Bukti | Lokasi |
|---|---|---|
| 1 Cerita | Logline Bu Lastri belajar QRIS; 14 shot | `STORYBOARD_DATA.json`, PDF storyboard |
| 2 Storyboard + perspektif | 14 shot / 18 panel, lensa 24–70 mm, sudut 3/4 & OTS | PDF storyboard; frame 120, 460, 750, 1820 |
| 3 Walk cycle + osilasi | Pelanggan berjalan (kaki menapak, tanpa slide) S02 f241–390 & S09 f1501–; papan nama & lampu gantung berosilasi teredam `A·e^(-kt)·sin(ωt)` | f250, 385; skrip `11_props.py` (`run_oscillation`) |
| 4 Transformasi | translasi (jalan), rotasi (lengan/kepala), skala (properti, penjepit) | skrip akting 08a–c |
| 5 Model/environment | warung, jalan, ruko, properti | f120, 2680 |
| 6 Kamera/FOV | 14 kamera fisik, marker S01–S14, DOF f-stop | f1409 (close-up), f2680 (wide) |
| 7 Lighting + material | Sun + 3-point (key/fill/rim), HDRI, PBR (kayu, aspal, kain, logam), toon karakter | `13_light_comp.py`; f459 |
| 8 Simulasi fisika | Cloth spanduk + Wind, bake disk cache | `14_cloth.py`; f120–2700 |
| 9 Compositing | DOF, grading AgX, glare, vignette, grain | `13_light_comp.py` |
| 10 Render MP4 ≥1080p | 1080x1920, 30 fps, H.264, 90 dtk | Final_Satu_Stiker_Satu_Warung.mp4 |
Hasil QA fisika: lihat `Laporan_QA.md`.
