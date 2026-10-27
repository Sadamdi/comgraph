# Laporan QA v2 — sebelum render (26 Okt 2026, malam)

## Pemeriksaan fisika & kontak (sampel tiap 20 frame, frame 10–2690)
| Pemeriksaan | Hasil |
|---|---|
| Tembus antar-karakter (BVH overlap) | 0 frame |
| Kaki menapak (z sol) | semua dalam −0,004…+0,02 m, tidak ada kaki melayang/tertanam |
| Tembus meja/nampan/tiang (BVH nearest, ambang 1,2 cm) | 1 frame tersisa: f670 badan mahasiswa vs papan meja 1,3 cm (4 verteks, sentuhan) |
| Peregangan kulit | lihat Laporan_QA.md (tidak berubah) |

## Temuan & perbaikan putaran ini
1. Bu Lastri menembus badan meja 3,6 cm (f1440, tangan kanan menyilang badan meja saat transisi S07→S08) -> posisi berdiri digeser +3,5 cm ke belakang, ditambah pose perantara tangan kanan di atas meja (f1336).
2. Lengan kiri Bu Lastri menyenggol nampan 2,5 cm (f130–170, f710, f2140) -> target tangan istirahat dinaikkan (z 1,37), tepi belakang nampan dipangkas 5 cm.
3. Jaket mahasiswa menembus bibir meja 2,5 cm saat serah-terima (f2260–2320) -> titik serah-terima dinaikkan 7 cm, target tangan Bu Lastri dinaikkan.
4. Mahasiswa ikut berjalan mengikuti NPC (Action terbagi pada `object.copy()`) -> animasi klon dikosongkan, animasi utama dibangun ulang.
5. Tangan menembus papan QRIS (S08) -> tangan memegang dari belakang papan.
6. Mulut/pipi/hidung melayang di depan dagu -> ditempel ke permukaan kulit (BVH).
7. Rambut mahasiswa tidak menutupi pelipis/tengkuk -> bentuk rambut diperpanjang.
8. Bidang miring di panel depan meja (artefak) -> panel disembunyikan.

## Daun & lingkungan
- Pohon besar Poly Haven (CC0) ×6, daun bergetar (Displace + vertex group), nuansa musim gugur.
- Daun gugur dari verteks tajuk pohon sungguhan (288 daun, driver ekspresi), daun di tanah 120.
- Cek: tidak ada daun jatuh menembus lantai (z minimum 0,02 m, lalu memudar).

## Belum diverifikasi manusia
- Kenyamanan visual gerak (tonton video pratinjau), flicker Kuwahara per-frame (lihat laporan frame-diff).
- Audio asli; SFX sintesis belum diaudisi.
