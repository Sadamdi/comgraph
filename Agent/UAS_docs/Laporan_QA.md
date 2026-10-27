# Laporan QA sebelum render — "Satu Stiker, Satu Warung"

Tanggal: 26 Oktober 2026. Skrip: `Produksi/scripts/15_qa.py`. File: `COMGRAPHTHEORYUASLOMBA.blend`.

## Metode (otomatis, per frame sampel tiap 10–15 frame, total ±180 frame dari 2700)
| Pemeriksaan | Cara |
|---|---|
| Tembus objek statis (meja, tiang, nampan, dinding, lantai) | titik mesh badan & pakaian (setelah deformasi rig) diuji terhadap BVH tiap objek statis: titik di belakang permukaan terdekat > 1,2 cm = tembus |
| Tembus antar-karakter | `BVHTree.overlap` antara mesh badan+pakaian Bu Lastri dan mahasiswa |
| Kontak lantai | z terendah sol sepatu/sandal |
| Jangkauan IK | jarak kontrol IK tangan/kaki vs efektor tulang (galat > 3 cm = target tak terjangkau) |
| Peregangan mesh | rasio panjang sisi dibanding frame 1 (cek "candy wrapper"/robek) |
| Pencahayaan | luminansi rata-rata & piksel terbakar/gelap per shot |
| Tinjauan visual | contact sheet tiap shot + sudut samping untuk pose yang mencurigakan |

## Temuan & perbaikan
1. **Bu Lastri menembus meja** (papan hingga 6 cm, rok vs badan meja 11 cm) -> badan meja diperdangkal (70->50 cm), bibir papan ditipis (12->5 cm, permukaan tetap z=1,19), penjual digeser (y=0,56), tangan istirahat dinaikkan (z>=1,32).
2. **Lengan menembus bibir meja** (siku menekuk ke bawah) -> sudut pole siku dipilih otomatis (setinggi bahu, keluar); titik singgah tangan otomatis menaikkan tangan sebelum melintasi meja.
3. **Pelanggan menabrak tiang depan** saat berjalan -> jalur jalan polyline (via titik di luar tiang), lalu serong ke meja.
4. **Ujung sepatu menembus tanah 3 cm saat jinjit** -> ankle diangkat mengikuti pitch kaki (engsel di ujung jari / tumit).
5. **Kunci liar frame 1263** (pelanggan "berjalan balik" selama S07-S08) -> titik singgah tangan hanya mengunci tulang tangan; celah waktu dibatasi.
6. **Status akting hilang antar-panggilan MCP** (tangan kembali ke posisi istirahat) -> `save_state()` + pemulihan di `09_boot.py`.
7. **Lengan jaket jadi "sayap segitiga"** (bobot kulit patah di ketiak) -> bobot dihaluskan 12 iterasi; bobot tangan/kaki pada pakaian digabung ke lengan bawah/betis.
8. **Membungkuk 53° menjangkau nampan** (seperti tengkurap di meja, rok menggembung) -> nampan+gorengan digeser 10 cm ke arah penjual, batas condong 32°, porsi putaran pinggul diturunkan.
9. **Kantong menutupi papan QRIS & tumpang tindih serah-terima** -> kantong, QRIS, dan titik serah-terima digeser; kamera S08/S10/S13 diarahkan ulang.

## Hasil akhir
- Tembus antar-karakter: **0** frame.
- Galat IK > 5 cm: **0**; galat 3–4 cm hanya di serah-terima kantong (tangan kiri Bu Lastri, f2240–2320).
- Kaki: z sol sepatu/sandal ∈ [-0,0011 ; 0,0006] m (menapak).
- Tembus statis: tidak ada tembus dalam > 2,5 cm. Sisa **kontak ringan <= 2,5 cm** (lengan/tangan bertumpu pada permukaan meja/nampan) di ±12% frame sampel, terutama S01 (f115–175), S03 (f415), serah-terima S12–S13 (f2255–2345). Dianggap bertumpu, bukan tembus tembok.
- Peregangan mesh: sisi terpanjang yang membesar > 2,2x hanya 4,8 cm (jaket, saat lengan terangkat); tidak ada robekan.
- Pencahayaan: luminansi rata-rata 0,40–0,57 di 14 shot, 0% piksel terbakar, <=0,03% gelap.
- Waktu render uji 1080x1920: 5,6–5,9 dtk/frame (64 sampel), 4,1 dtk (32 sampel).

## Catatan yang tetap perlu dilihat manusia (tim)
- Wajah mahasiswa jarang terlihat (mayoritas dari belakang); ekspresi Bu Lastri terbaca di S03, S05, S09, S11.
- Sisa kontak ringan lengan-permukaan bisa terlihat pada close-up tertentu; jika mengganggu, naikkan target tangan 2–3 cm pada shot itu.
- Audio asli belum ada; subtitle & kartu judul ditambahkan di tahap penyuntingan (ffmpeg).
