# comgraph — Grafika Komputer (Semester 5)

Repo ini berisi tugas praktikum dan UAS **"Satu Stiker, Satu Warung"** (animasi 90 detik, 9:16, 1080x1920, untuk UAS + lomba BIDCC 2026, deadline lomba 31 Okt 2026 23:59 WIB).

## Mulai dari sini
- **`HANDOFF.md` — panduan lengkap untuk agent cloud (setup Blender + MCP, kondisi, TODO). Baca ini dulu.**
- `AGENTS.md` — instruksi untuk AI agent (Claude Code/Cursor/Codex) di repo ini.
- `Agent/UAS_Satu_Stiker_Satu_Warung.md` — **catatan utama**: keputusan, urutan build, gotcha, status, cara melanjutkan (baca bagian 11–13).
- `Agent/UAS_docs/` — laporan QA, naskah & cue audio, caption/email, bukti rubrik.
- `UAS UTS/Produksi/scripts/` — seluruh skrip build (urut nomor). Skrip dijalankan di Blender 5.2.1 LTS lewat MCP (`execute_blender_code`).
- `UAS UTS/COMGRAPH_V3_GHIBLI.blend` — file kerja terbaru (**Git LFS**, 392 MB; jalankan `git lfs pull`).

## Yang TIDAK ada di repo (dibuat ulang / terlalu besar)
Frame hasil render (`frames_*`), pratinjau, salinan `.blend` lama, cache simulasi. Lihat `.gitignore`.

## Status ringkas (28 Okt 2026)
Tangan baru (metaball→mesh), tulang puntir lengan bawah, batas pergelangan, lantai panggung Bu Lastri, QA numerik bersih.
**Masih kurang** (arah berikutnya): wajah & desain karakter belum bergaya Ghibli, gerakan masih kaku, rig perlu lebih detail
(twist lengan atas, rig wajah shape key, sekunder rambut/kain), QA harus menilai tampilan akhir video (bukan hanya angka).
Gaya Pocari dibatalkan — fokus Ghibli.

## Aturan
AI hanya alat bantu dan harus dilaporkan jujur di form lomba BIDCC; layanan generatif (Meshy, Tripo, dsb.) tidak dipakai.
Jangan upload/submit ke platform apa pun tanpa persetujuan pemilik.
