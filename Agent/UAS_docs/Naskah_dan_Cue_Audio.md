# Naskah, Cue Sheet Audio & SFX — "Satu Stiker, Satu Warung" (90 dtk, 30 fps)
Waktu = frame/30. Rekam suara asli oleh tim (pelanggan/mahasiswa, Bu Lastri, narator). Volume: dialog -16 LUFS, SFX -26, ambience -32.

## A. Dialog & narasi (sinkron dengan docs/subtitle.srt)
| Waktu | Shot | Pengisi | Teks | Catatan arahan |
|---|---|---|---|---|
| 00:13.8 | S03 | Mahasiswa | "Seperti biasa, Bu." | ramah, akrab |
| 00:15.7 | S03 | Bu Lastri | "Masih hangat, nih." | hangat, ceria |
| 00:19.5 | S04 | Mahasiswa | "Waduh, lupa ambil tunai." | kaget ringan, menggerutu |
| 00:23.5 | S05 | Mahasiswa | "Bisa QRIS, Bu?" | bertanya sopan |
| 00:25.5 | S05 | Bu Lastri | "Belum, Nak." | sedikit menyesal |
| 00:29.0 | S06 | Mahasiswa | "Nanti saya balik lagi, Bu." | menenangkan |
| 00:37.0 | S07 | Narator | "Bu Lastri pun mulai belajar cara baru melayani." | tenang, hangat |
| 00:51.0 | S09 | Mahasiswa | "Sekarang sudah bisa, Bu?" | senang, kaget |
| 00:53.6 | S09 | Bu Lastri | "Bisa. Seperti biasa?" | percaya diri |
| 01:07.0 | S11 | Bu Lastri | "Sudah masuk." | lega, mengangguk |
| 01:11.0 | S12 | Mahasiswa | "Makasih, Bu." | tersenyum |
| 01:12.9 | S12 | Bu Lastri | "Hati-hati, masih hangat." | hangat |
| 01:23.5 | S14 | Narator | "Bank Indonesia mendukung digitalisasi pembayaran, membuka lebih banyak cara bagi usaha kecil untuk melayani." | jelas, tidak terburu-buru |
Jika tempo rekaman beda, geser waktu di `subtitle.srt` lalu jalankan ulang `encode.sh`.

## B. SFX cue sheet
| Waktu | Shot | SFX | Sumber (bebas hak cipta) |
|---|---|---|---|
| 00:00–01:30 | semua | ambience jalan lingkungan, kendaraan jauh, burung (loop, fade in/out) | Freesound CC0 / Pixabay / Mixkit "street ambience" |
| 00:02–00:08 | S01 | kertas dirapikan, penjepit logam kena baki | "tongs clink", "paper rustle" |
| 00:03–00:07 | S01 | papan nama berayun, kayu/rantai kecil | "wooden sign creak" |
| 00:08–00:13 | S02 | langkah sandal/sepatu di aspal, mendekat | "footsteps asphalt" |
| 00:13–00:18 | S03 | kantong kertas diangkat | "paper bag rustle" |
| 00:19–00:22 | S04 | dompet dibuka (velcro/kulit) | "wallet open" |
| 00:27–00:30 | S06 | langkah menjauh | "footsteps away" |
| 00:36–00:44 | S07 | sentuhan layar ponsel (tap lembut) | "phone tap soft" |
| 00:44–00:46 | S08 | papan QRIS diletakkan di meja | "wood/plastic place on table" |
| 00:49–00:51 | S09 | langkah mendekat lagi | "footsteps asphalt" |
| 00:58–01:03 | S10 | tap layar ponsel (tanpa bunyi sukses sebelum konfirmasi) | "phone tap" |
| 01:06.5 | S11 | notifikasi ponsel **hanya setelah** dicek | "notification soft" |
| 01:11–01:16 | S12–S13 | kertas/kantong berdesir saat berpindah | "paper bag handoff" |
| 01:22–01:30 | S14 | langkah menjauh, ambience mengecil, musik penutup naik | — |
| 00:00–01:30 | semua | musik latar akustik ringan, dikecilkan saat dialog (ducking) | Pixabay Music / YouTube Audio Library (cek lisensi, simpan bukti) |

## C. Kartu teks pada video (sudah dibakar oleh encode.sh)
- 00:44–00:48 (S08): "Beberapa hari kemudian"
- 01:25–01:30: "Satu Stiker, Satu Warung" + "Peserta BI Digital Content Competition 2026 · #BIDCC2026"
Catatan: papan QRIS bertuliskan "CONTOH / NONAKTIF" (mock-up, bukan QRIS sungguhan).
