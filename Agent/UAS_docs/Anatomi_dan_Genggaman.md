# Anatomi tubuh, tangan, dan cara memegang benda — dasar yang dipakai di animasi

## Tubuh & sendi (rig `RIG_LASTRI` / `RIG_MHS`)
| Bagian | Prinsip | Implementasi |
|---|---|---|
| Tulang belakang | Membungkuk dibagi ke pinggul–tulang belakang–dada (±0,15 / 0,425 / 0,425) agar tidak "patah" di satu titik | `act()` `lean`, batas condong otomatis 32° |
| Bahu | Tulang selangka (clavicle) ikut naik saat lengan terangkat (ritme skapulohumeral) | tulang `clavicle.L/R`, kunci di `act(clavL/clavR)` |
| Siku | Engsel satu sumbu (tekuk 0–145°), arah tekuk ditentukan pole; siku tidak boleh di dalam badan/meja | IK 2 tulang + `pole_angle` dipilih otomatis (`_elbow_score`) |
| Pergelangan | Orientasi tangan mengikuti kontrol `hand_ik` (arah jari + arah telapak) | mode `("frame", ...)` + `G()`/`Hold()` di `07_acting_lib.py` |
| Kaki | Langkah terencana, tumit→telapak→jari; sol tidak menembus tanah; tanpa meluncur | `walk()` + IK kaki |
| Berat badan | Pinggul bergeser ke kaki tumpu, dada berlawanan | `walk()` (sway, twist) |

## Tangan: 4 jari (3 ruas) + jempol (3 ruas), 30 tulang jari
- Geometri jari dibuat dari kerangka Skin di `04a_body.py` (telapak lebar ±7 cm, jari proporsional: telunjuk 0,95; tengah 1,00; manis 0,93; kelingking 0,78).
- Tulang jari: `index1..3`, `middle1..3`, `ring1..3`, `pinky1..3`, `thumb1..3` (`.L/.R`). Sumbu X lokal = sumbu tekuk; rotasi positif = menekuk ke arah telapak (`05_rig.py`).
- Bobot kulit: jarak ke ruas jari (dinormalisasi radius 1,05–1,25 cm); lengan baju memakai lengan bawah saja.

## Pose genggam (`GRIPS` di `07_acting_lib.py`)
`open`, `flat`, `relaxed`, `point`, `pinch`, `board` (tepi papan), `phone`, `tongs` (penjepit), `bag`, `cup` (telapak menopang), `wallet`.
Interval pegangan dicatat di `HOLDS` (siapa, tangan, frame ambil, frame lepas, pose). Otomatis:
1. 12 frame sebelum menyentuh: jari **membuka**,
2. selama memegang: jari **menggenggam** sesuai pose,
3. 10 frame setelah melepas: jari **membuka** lalu santai.

## Cara tangan menemui benda (bukan sekadar menempel)
1. Titik genggam ditentukan pada **benda** (tepi samping papan QRIS, tepi lipatan kantong, lembar bawah dompet).
2. Arah jari dan arah telapak ditentukan dari posisi/hadap benda (`Hold()`, `G()`), pergelangan dihitung mundur dari titik genggam.
3. Benda mengikuti tangan lewat Copy Transforms dengan offset yang dibekukan saat genggaman (pegangan konsisten dengan jari).
4. Saat dilepas: jari membuka dulu, benda turun/berdiri (papan QRIS), baru tangan menarik mundur.
5. QA: tangan/jari tidak menembus meja/nampan (BVH), dua tangan tidak menembus satu sama lain (overlap antar-karakter = 0).

## Fisika yang diterapkan
- Gravitasi sederhana: benda dilepas turun 1–2 cm ke permukaan (influence ramp 4–7 frame).
- Angin: spanduk kain (Cloth+Wind, cache disk), daun pohon (Displace + noise bergeser), daun gugur (driver: jatuh ±0,25 m/dtk, ayunan sinus, mendarat rebah lalu memudar).
- Osilasi teredam papan nama & lampu (`A·e^(−kt)·sin(ωt)`).
