# HANDOFF — untuk agent cloud yang mulai dari nol

Dokumen ini cukup untuk: (1) menyiapkan Blender + MCP di mesin kosong, (2) memahami kondisi proyek, (3) melanjutkan pekerjaan yang belum selesai.
Baca urut. Bahasa komunikasi dengan pemilik: **Bahasa Indonesia**, singkat, jujur.

---
## 0. Aturan dari pemilik (WAJIB)
1. **Fokus gaya Ghibli saja.** Gaya "Pocari" dibatalkan — jangan dikerjakan.
2. **Kualitas > kecepatan.** Pemilik bilang boleh berjam-jam/berhari-hari. Jangan menyarankan jalan pintas demi cepat. Target: mirip desain Ghibli di **semua** aspek — wajah/desain karakter, anatomi & topologi, rig halus, animasi (prinsip animasi: anticipation, overlap, follow-through, ease), latar, cahaya, cuaca, daun gugur realistis.
3. **QA harus menilai tampilan akhir** (lihat video/frame, bukan hanya angka tembusan). Kesalahan sebelumnya: melapor "QA bersih" dari angka padahal hasil terlihat kaku/glitch.
4. **Jangan** menambahkan baris `Co-Authored-By` / atribusi AI di pesan commit atau PR. Jangan force-push/ubah riwayat tanpa diminta.
5. **Jangan upload/posting/submit** apa pun (Drive, TikTok, IG, form BIDCC) tanpa persetujuan eksplisit pemilik. Layanan generatif (Meshy, Tripo, Hyper3D, Higgsfield, 3D AI Studio…) sengaja **tidak** dipakai; AI hanya alat bantu & wajib dilaporkan jujur di form lomba (BIDCC).
6. Catatan/memori kerja ditaruh di `Agent/` (bukan di tempat lain). Tambahkan progres ke `Agent/UAS_Satu_Stiker_Satu_Warung.md` (bagian 13+).
7. Deadline lomba BIDCC 2026: **31 Okt 2026 23:59 WIB**; link UAS dosen 30 Nov 2026 23:00. Isu terbuka: konfirmasi panitia soal aturan alat AI (disarankan email ke admin@bidcc.id) & konfirmasi dosen soal durasi 90 detik vs aturan 7–15 menit.

---
## 1. Tentang proyek
Animasi 3D 90 detik "**Satu Stiker, Satu Warung**" (UMKM Berdaya): Bu Lastri (penjual gorengan) memasang stiker QRIS, Mahasiswa membayar dengan HP. 9:16, **1080x1920**, 30 fps (scene Blender 25 fps; 2700 frame → encode 30 fps = 90 dtk), EEVEE. Untuk UAS Grafika Komputer (10 poin rubrik) + lomba BIDCC 2026.
Peran yang dikerjakan agent: cerita, modeling/lingkungan, karakter/animasi, kamera/lampu/simulasi, compositing/audio/dokumen. Tim hanya mereview; suara asli akan direkam tim (SFX sintetis yang ada hanya draf).

Dokumen inti (baca setelah ini):
- `Agent/UAS_Satu_Stiker_Satu_Warung.md` — keputusan, urutan build, gotcha, QA, status (bagian 11–13 = terbaru).
- `Agent/UAS_docs/` — Anatomi_dan_Genggaman, Caption_dan_Email, Laporan_Bukti_Rubrik, Laporan_QA(+v2), Naskah_dan_Cue_Audio.
- `AGENTS.md` — gotcha Blender/MCP dari praktikum (operator edit-mode Blender 5, dll).
- `Agent/Reference/*.blend` — referensi Ghibli (landscape/field) dari pemilik.

---
## 2. Menyiapkan mesin kosong
### 2.1 Ambil repo
```bash
git clone https://github.com/Sadamdi/comgraph.git && cd comgraph
git lfs install && git lfs pull        # mengunduh .blend (±392 MB) dan HDR
```
Repo privat — perlu kredensial pemilik (`gh auth login`). Frame render **tidak** ada di repo (dibuat ulang).

### 2.2 Pasang Blender **5.2.1 LTS** (harus 5.1+; proyek dibangun di 5.2.1)
- Windows: unduh installer dari https://www.blender.org/download/ → `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`.
- Linux: unduh `blender-5.2.1-linux-x64.tar.xz` dari https://download.blender.org/release/ lalu ekstrak; jalankan `./blender`.
- Pasang `uv` (Python tool runner): https://docs.astral.sh/uv/ (`pip install uv` atau installer resminya).

### 2.3 Pasang MCP (pilih A; B sebagai cadangan)
**A. Blender Lab MCP** (yang dipakai proyek ini; tool `execute_blender_code` mengembalikan variabel dict `result`)
1. Add-on di dalam Blender: sumber ada di `Agent/mcp_setup/blender_extension_mcp/` (extension "MCP" v1.0.3, Blender Lab). Pasang: zip isi foldernya (`blender_manifest.toml` harus di akar zip) → Blender: *Edit > Preferences > Get Extensions > ▾ > Install from Disk*. (Atau cari "MCP" di Extensions.) Aktifkan; di preferensinya set **Port** (proyek ini memakai **9877**; bawaan 9876) dan **Auto Start** = on. Auto start diabaikan di mode background.
2. Server MCP (sisi agent): `Agent/mcp_setup/blender-lab/` (paket `blender-mcp`, `uv run`). Daftarkan ke agent, contoh Claude Code:
```bash
claude mcp add blender-lab -s user \
  -e BLENDER_MCP_PORT=9877 -e BLENDER_PATH="<path blender.exe/blender>" -e UV_LINK_MODE=copy \
  -- uv run --directory "<REPO>/Agent/mcp_setup/blender-lab" blender-mcp
```
3. Verifikasi: Blender GUI terbuka → port 9877 LISTENING (`netstat -an | findstr 9877` / `ss -ltn | grep 9877`) → panggil tool `execute_blender_code` dengan `result = {"v": bpy.app.version_string}` harus mengembalikan `5.2.1 LTS`.

**B. `blender-mcp` (ahujasid) via uvx** — panduan lengkap di `Agent/mcp_setup/README_MCP.md`, skrip di `Agent/mcp_setup/tools/` (`install_blender_mcp.ps1`, `blender_mcp_autostart.py`). Catatan Blender 5: add-on legacy tak terbaca; dipasang sebagai *startup script* (`scripts/startup/`). Port 9876. Di sini `execute_blender_code` mengembalikan stdout (bukan `result`).

**C. Tanpa GUI (headless)** — bila mesin tak punya layar:
`blender -b "UAS UTS/COMGRAPH_V3_GHIBLI.blend" --python skrip.py`. Cocok untuk QA/penghitungan/render batch (lihat `UAS UTS/Produksi/render/qa_motion_bg.py`, `preview_bg.py`). Renderer = **EEVEE** → butuh OpenGL. Tanpa GPU, EEVEE hanya jalan lewat software GL (xvfb + mesa llvmpipe) dan **sangat lambat**; render akhir lebih baik di mesin pemilik (GPU). Pekerjaan modeling/rig/animasi/QA numerik bisa dilakukan di cloud.

### 2.4 Path Windows di skrip
Skrip memakai root Windows `D:\adam kuliah\Semester 5\Computer Graphic\...` (24 file). Di mesin lain:
```bash
python Agent/mcp_setup/remap_paths.py "/abs/path/ke/comgraph"      # best-effort, lalu uji smoke test
```
Smoke test: di Blender buka `UAS UTS/COMGRAPH_V3_GHIBLI.blend`, jalankan `exec(open(SD+"15_qa.py").read())` lalu `check_frames([1, 600, 1350, 2250])` — harus selesai tanpa error (`SD` = folder `UAS UTS/Produksi/scripts/` + pemisah path).

---
## 3. Cara bekerja dengan skrip (pola yang terbukti)
- File kerja terbaru: **`UAS UTS/COMGRAPH_V3_GHIBLI.blend`** (satu-satunya .blend di repo untuk produksi; gaya Ghibli aktif; 1080x1920, 2700 frame, EEVEE 20 sampel). Salinan gaya lain tidak dipakai.
- Skrip dijalankan dari file: `SD = r"<root>/UAS UTS/Produksi/scripts" + sep`; `exec(open(SD+"xx.py", encoding="utf8").read())`. Hasil dikembalikan lewat `result = {...}` (harus dict).
- **Timeout MCP ≈ 100–150 dtk** per panggilan. Pecah pekerjaan; untuk yang lama pakai proses Blender latar (`blender -b file --python skrip`), jangan lewat MCP. `frame_set` di file ini ±1 dtk/frame (kain, daun, ribuan objek) → sapuan 2700 frame lewat Blender latar, bukan MCP.
- `bpy.ops.wm.open_mainfile(...)` harus **dipanggil sendirian** dalam satu eksekusi (konteks hilang sesudahnya).
- `object.copy()` **berbagi Action** → klon karakter wajib `animation_data_clear()` (dan shape-key anim).
- Cloth banner (`Spanduk_Kain`) harus tetap **baked** (disk cache). Jangan ganti fps scene (cache kain bisa usang).
- Timeline markers menimpa kamera aktif → untuk render kamera uji, kosongkan `marker.camera` sementara (lihat `scripts/30_closeup.py`).
- Render kecil untuk cek: `resolution_percentage=40`, `taa_render_samples=8`.

### Urutan skrip (ringkas; detail di `Agent/UAS_Satu_Stiker_Satu_Warung.md`)
`02b_toon` (shader toon) → `04a-d` (badan/kepala/pakaian) → `05_rig` (rig kustom 58 tulang + jari + IK) → `06_anim_core`/`07_acting_lib` (API `act()`, `walk()`, genggaman) → `08a/b/c_scenes` (akting S01–S14) → `09_boot` → `10_cameras` → `11_props` → `13_light_comp` → `14_cloth` → `16_ghibli_look`/`17_styles`/`18a-b`/`19_extras`/`20_cars`/`21_npc`/`22a-d`/`23_plants`/`24*_autumn`/`25_atmos`/`26_dress`/`27_camera_polish` (lingkungan & gaya) → `15_qa` (QA).
**Skrip baru sesi V3**: `30_closeup.py` (render close-up diagnostik), `31_hands.py` (tangan baru), `32_twist.py` (tulang puntir lengan bawah), `33b_nape_cap.py` (rambut tengkuk), `34_straps.py` (tali celemek/ransel).

### Siklus bangun-ulang animasi (≈ 8 menit; harus berurutan, tiap blok < 150 dtk)
1. A: `CLEAR_ANIM=True; exec 09_boot; exec 08a/b/c; S01()…S07(); save_state()`
2. B: `CLEAR_ANIM=False; exec 09_boot; exec 08a/b/c; S08()…S14(); save_state()`
3. `exec 06_anim_core, 07_acting_lib, 11_props, 22b_screens_apply, 22d_screens_seq`
(`12_rebuild_chars.py` membangun ulang karakter dari nol → akan **menghapus tangan baru**; jangan dijalankan tanpa menjalankan ulang `31/32/33b/34`.)

---
## 4. Kondisi saat ini (jujur)
**Sudah**: lingkungan jalanan+warung lengkap (pohon besar, daun gugur dari tajuk, mobil Kenney, NPC, awan, atmosfer volumetrik, spanduk kain), papan QRIS & layar HP nyata (QR dummy), kamera per shot, 8 rig; tangan baru (metaball→mesh) + tulang puntir `forearm_tw1/2`; batas pergelangan (`WRIST_LIMIT` Euler YXZ, `_limit_wrist` ≤42°); regangan jari; Bu Lastri di `Lantai_Warung` (z 0,22); rambut tengkuk; tali celemek/ransel; batas gerak mata (`EYE_LIMIT`); QA numerik 0 tembusan ≥1,2 cm & 0 overlap (sampel tiap 12 frame).
**Penilaian pemilik terhadap hasil sekarang: BELUM BAGUS.** Alasan (diakui jujur):
- Karakter dibuat dari kode (Skin modifier, metaball), bukan modeling dengan topologi animator → lipatan/tembus muncul terus. Wajah = anime generik, **bukan desain Ghibli**.
- Gerakan = pose kunci dari kode + IK → kaku, tanpa overlap/follow-through/ease alami; tangan masih terasa kaku dan kadang tembus objek/fisika tak benar.
- "Gaya Ghibli" saat ini hanya filter (Kuwahara + tekstur kanvas) + shader toon; bukan karakter/garis/latar bergaya Ghibli.
- Frame render lama (Pocari & Ghibli) usang — semua harus dirender ulang.

---
## 5. Yang harus dikerjakan (urut prioritas)
1. **Desain karakter & wajah ala Ghibli.** Riset referensi (proporsi lebih realistis & lembut dari anime umum; mata ekspresif tapi tidak berlebihan; hidung sederhana; pipi/wajah anak berisi). Bangun ulang kepala/wajah kedua tokoh + rambut (kepingan/ribbon berlapis, bukan blob). Opsi yang ditawarkan ke pemilik: pakai model dasar benar (mis. VRoid Studio → VRM, alat modeling biasa, bukan AI generatif, wajib dikreditkan) atau modeling manual dengan edge-loop anatomis (mata, mulut, bahu, siku, pergelangan, jari). **Tanyakan pilihannya ke pemilik di awal** bila belum jelas.
2. **Rig lebih detail & halus**: twist lengan atas (upper_arm_tw), klavikula/bahu dengan corrective shape key, rantai tulang belakang 3–4 ruas, kaki/telapak (roll), rig wajah berbasis shape key (alis, kelopak, pipi, mulut vokal/viseme, tersenyum), tulang sekunder rambut/kain (spring), bobot dirapikan (≤4 pengaruh/vertex, uji dengan pose ekstrem), jari dengan pose library genggam. Verifikasi dengan close-up multi-sudut (30_closeup) pada pose ekstrem.
3. **Animasi**: terapkan prinsip animasi + referensi gerak (mocap/BVH berlisensi jelas yang diretarget, atau animasi tangan di graph editor); ritme, arc, anticipation, overlap/follow-through, hold & ease; pernapasan, kedip, pergeseran bobot; tangan memegang benda lewat constraint (Child Of / empty di tulang tangan) dengan pose jari yang benar; tidak ada tembus. Adegan bermasalah yang diketahui: **S08 (serah papan QRIS, f1321–1440)**, penjepit gorengan (hentakan f2203–2207), serah kantong (f2230–2300).
4. **Gaya Ghibli sungguhan**: shading toon/painterly yang konsisten, garis tepi tipis berwarna, tekstur cat tangan (langit, awan, dinding, kayu), palet hangat; cek `Agent/Reference/*.blend`. Tetap realistis soal cuaca/udara/cahaya/daun.
5. **QA berbasis tampilan** (wajib sebelum render penuh): render pratinjau resolusi rendah seluruh durasi (`render/preview_bg.py`), lihat contact sheet + tonton videonya per adegan, close-up tiap genggaman dari 3 sudut, `15_qa.py` (tembus/overlap), `render/qa_motion_bg.py` (hentakan/tekuk pergelangan; hasil JSON), `render/qa_framediff.py` (lonjakan antar-frame). Perbaiki sampai tidak ada glitch yang terlihat; **laporkan hasil dengan jujur** termasuk yang belum beres.
6. **Render akhir** (setelah QA bersih & disetujui pemilik): `UAS UTS/Produksi/render/mulai_render.ps1` (resumable, per sesi, aman dimatikan); Ghibli ≈ 25 dtk/frame (Kuwahara) ≈ 19 jam. Encode: `encode.sh` (ffmpeg; subtitle `docs/subtitle.srt` + kartu judul). Audio asli dari tim di-mux belakangan.
7. Dokumen pengumpulan (siap, belum dikirim): caption wajib memuat "Peserta BI Digital Content Competition 2026", #BIDCC2026, @bank_indonesia; deklarasi pemakaian AI yang jujur; draf email ke admin@bidcc.id — semuanya di `Agent/UAS_docs/Caption_dan_Email.md`. **Kirim hanya setelah pemilik setuju.**

---
## 6. Gotcha cepat
- Blender 5.2: `action.fcurves` tak ada (pakai `layers[0].strips[0].channelbag(slot).fcurves`); `Kuwahara` node tidak punya `.variation` (peringatan tak berbahaya saat `17_styles`).
- Metaball: radius permukaan ≈ 0,56 × radius elemen (stiffness 2, threshold 0,6).
- Sumbu jari: rotasi X = menekuk, Z = merenggang (kanan: + ke arah kelingking, kiri: kebalikan), Y = roll. `Euler XYZ` pada Limit Rotation mencampur puntiran ke tekuk → gunakan `YXZ`.
- Gaze: `DAMPED_TRACK` ke `LOOK_<NAMA>`; tanpa batas, mata bisa berputar >60° (iris hilang) → ada `EYE_LIMIT`.
- Particle falling leaves memunculkan NaN → daun memakai driver ekspresi (`24b_fall_from_trees.py`).
- Hasil QA numerik tidak menggantikan melihat video.
