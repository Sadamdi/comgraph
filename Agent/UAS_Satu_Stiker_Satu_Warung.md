# Memori Agen — Project UAS "Satu Stiker, Satu Warung" (BIDCC 2026 + Computer Graphic Teori)

Dokumen ini adalah **catatan kerja yang harus dibaca agen berikutnya** sebelum menyentuh file Blender proyek ini.
Dibuat 26 Okt 2026. Folder kerja: `Computer Graphic/UAS UTS/` (file utama `COMGRAPHTHEORYUASLOMBA.blend`).

## 1. Konteks & keputusan user
- Tim 5 orang, tugas UAS Computer Graphic (dosen Tri Mukti Lestari). Soal: `UAS UTS/SOAL UTS dan UAS.pdf`.
  Poin 1-5 UTS (cerita, storyboard+perspektif, walk cycle+osilasi, transformasi), poin 6-10 UAS (kamera/FOV, 3-point lighting + material,
  simulasi fisika, compositing DOF + color grading, render MP4 >=1080p). UAS dikumpulkan 30 Nov 2026 23.00.
- Ikut lomba **BIDCC 2026** (Bank Indonesia Digital Content Competition) kategori **Video Animasi**, sub-tema **UMKM Berdaya**.
  Deadline karya **31 Okt 2026 23.59 WIB**. Syarat: MP4/MOV, **9:16**, >=1080p, **maks 2 menit** (karya kita 90 detik), unggah ke TikTok/IG (akun publik,
  mention @bank_indonesia, caption "Peserta BI Digital Content Competition 2026" + #BIDCC2026), kumpulkan link Google Drive publik di bidcc.id.
  Aturan AI: AI hanya alat bantu; generative AI penghasil karya jadi dilarang; **alat AI wajib dilaporkan di form**. Karya jadi milik BI.
- User memilih: Claude mengerjakan **penuh lewat Blender** (AI sebagai alat di dalam Blender), tim review. Tafsiran user atas aturan AI itu **belum dikonfirmasi panitia**
  -> sarankan email ke admin@bidcc.id dan isi form jujur (Claude Code mengoperasikan Blender lewat skrip).
- Gaya: karakter bergaya **anime** (toon shading + outline) di dunia **realistis** (PBR, HDRI, bayangan matahari), grading sinematik. Hasil harus terasa real world & halus.
- Dialog/audio asli direkam tim. Agen hanya menyiapkan naskah teks, cue sheet, daftar SFX, subtitle.
- Bekerja LANGSUNG di file teman (satu file bersama). Cadangan ada di `UAS UTS/_backup/`.

## 2. Cerita (storyboard teman, 14 shot, 90 dtk, 2700 frame @30fps, 1080x1920)
Bu Lastri jualan gorengan, pelanggan (mahasiswa) lupa bawa tunai & bertanya "Bisa QRIS, Bu?" -> "Belum, Nak." -> Bu Lastri belajar lewat ponsel ->
"Beberapa hari kemudian" memasang papan QRIS (contoh, nonaktif) -> pelanggan kembali & membayar via scan -> Bu Lastri cek status ("Sudah masuk.") ->
menyerahkan gorengan -> penutup. Marker S01..S14 di timeline mengganti kamera. Jangan menjanjikan lonjakan omzet; layar/QRIS hanya mock-up.

## 3. Arsitektur skrip (`UAS UTS/Produksi/scripts/`)
Semua dijalankan lewat MCP: `exec(open(path, encoding="utf8").read())`. **Namespace TIDAK persisten antar panggilan MCP** (kecuali `bpy.app.driver_namespace`).
| Skrip | Isi |
|---|---|
| 00_tools | render uji 1 frame (`T["shot"]`), kamera debug (`dbg_cam`, `shotcam` – mematikan binding marker sementara) |
| 01_render_world | EEVEE, AgX, dunia (HDRI Poly Haven wide_street_02 *tanpa matahari*, kamera melihat langit Sky Texture), lampu Sun `SUN_Key` |
| 02_materials / 02b_toon | pustaka material PBR (tekstur Poly Haven CC0 di `Produksi/assets/tex`) & material toon karakter (Diffuse->ShaderToRGB->ColorRamp, cincin cahaya rambut, mata prosedural) |
| 03a/03b/03c | lingkungan (jalan, trotoar, deretan ruko, fasad prosedural), poles set warung, perbaikan geometri hasil QA |
| 04a-04d | badan (Skin modifier), kepala anime (mata+kelopak+kilau+alis+mulut shape key), rambut, pakaian (cut dari badan), perakit karakter |
| 05_rig | armature kustom + IK tangan/kaki + pole, bobot dari jarak ke segmen tulang **(dihaluskan)** |
| 06_anim_core / 07_acting_lib | `Char`, `walk()` (langkah terencana, polyline), `act()` (pose, auto-condong, titik singgah tangan, pole siku pintar) |
| 08a/b/c | akting S01-S14 (Bu Lastri = `L`, Mahasiswa = `M`) |
| 09_boot | memuat pustaka + membuat `L`,`M`; `CLEAR_ANIM`; `save_state()` untuk melanjutkan akting antar panggilan |
| 10_cameras / 11_props / 13_light_comp / 14_cloth | kamera fisik per shot+DOF, properti & pegangan tangan + osilasi, lampu 3-point + compositor, spanduk kain (Cloth + angin, bake ke disk) |
| 12_rebuild_chars / 15_qa / 99_build_all | bangun ulang tokoh, QA otomatis, urutan build penuh |

### Urutan build (jalankan terpisah, tiap panggilan < ±60 dtk)
1. `03c_fixes.py` -> `12_rebuild_chars.py` (7-60 dtk)
2. Panggilan A: `CLEAR_ANIM=True; exec 09_boot; exec 08a/b/c; S01()..S07(); save_state()`
3. Panggilan B: `CLEAR_ANIM=False; exec 09_boot (status dipulihkan); exec 08a/b/c; S08()..S14(); save_state(); 11_props; 10_cameras; save`
4. `13_light_comp.py` (lampu+compositor), `14_cloth.py` hanya bila perlu (lalu **bake ulang** ±2,5 menit, `use_disk_cache=True`).
5. QA: `15_qa.py` (`check_bones`, `check_frames`).

## 4. Gotcha yang sudah terbukti (JANGAN ulangi)
- **Jangan hapus objek dengan awalan nama** (`LASTRI_`, `PELANGGAN_`): objek milik teman ikut terhapus (`PELANGGAN_*` blockout lama, `LASTRI_PHONE*`). Dipulihkan dari `_backup`. Tokoh baru memakai awalan `LASTRI_`/`MHS_` + daftar PROT.
- Variabel bernama `P` ditimpa fungsi `P()` di skrip rambut; pakai `SD` untuk path skrip. String Python berisi `\U...` (path Windows) gagal -> tulis file skrip pakai alat Write, bukan heredoc `python -c`.
- `matrix_world` basi setelah mengubah transform; panggil `bpy.context.view_layer.update()` sebelum parent ke tulang / membaca matriks.
- Material pustaka: jangan `materials.remove()` lalu buat ulang (objek kehilangan slot). Pakai ulang nama yang sama.
- Enum Blender 5.2: sky `MULTIPLE_SCATTERING` (bukan NISHITA); view transform `AgX`; kompositor memakai **socket** untuk parameter & `scene.compositing_node_group`.
- Wind effector untuk Cloth butuh kekuatan ratusan (±330) untuk kain ringan; Cloth+SurfaceDeform dimatikan di viewport (`show_viewport=False`) agar build cepat, render tetap aktif.
- `Copy Transforms` ikut menyalin SKALA; empty pegangan harus memakai skala prop (penjepit memakai skala objek 0,25x0,03x0,03).
- Titik singgah tangan otomatis **hanya mengunci tulang tangan** (bukan seluruh pose/posisi rig); sebelumnya menciptakan kunci liar yang membuat pelanggan "berjalan balik".
- `walk()` dengan jalur polyline menghindari tiang depan; kaki pivot di ujung jari (ankle diangkat) agar sepatu tidak menembus tanah.
- Orphan data menumpuk saat membangun ulang: `bpy.ops.outliner.orphans_purge(...)` sebelum rebuild.
- Panggilan MCP >±120 dtk bisa putus ("No data received"); bake kain sendiri ±160 dtk masih lolos. Render panjang -> proses Blender background (`subprocess.Popen`).

## 5. Hasil QA (26 Okt 2026) — dijalankan sebelum render
Metode: BVH nearest-surface (tembus statis), BVH overlap (antar karakter), min z sol sepatu, galat IK efektor vs kontrol, lompatan tulang.
Perbaikan dari QA: meja diperdangkal (50 cm) & bibir papan ditipis (5 cm), staging L (y=0.56) & M (y=-0.60), jalur jalan polyline, tangan istirahat z>=1,32,
siku alami, titik singgah tangan, kantong digeser, QRIS/serah-terima digeser. Hasil terakhir: 0 tembus antar-karakter, 0 galat IK >5 cm,
kaki z∈[-0,001, 0,0006], sisa kontak ringan <=2,5 cm di <±7% frame sampel (lengan bertumpu di papan meja).

## 6. Yang belum selesai / harus dicek
- Render penuh 2700 frame 1080x1920 (ukur dtk/frame), subtitle & kartu judul ("Beberapa hari kemudian", penutup) lewat ffmpeg, mux audio asli tim.
- Naskah/cue sheet/SFX, laporan bukti rubrik per poin, draf email ke panitia, caption TikTok/IG.
- Konfirmasi ke dosen: 90 detik vs syarat 7-15 menit; tenggat UTS (poin 1-5).

## 7. Status 26 Okt 2026 (akhir)
- Render selesai: 2700 frame PNG di `UAS UTS/Produksi/frames` (EEVEE, 48 sampel, ±5 dtk/frame, ±4 jam).
- `Produksi/encode.sh` -> `Final_Satu_Stiker_Satu_Warung.mp4` (22 MB, subtitle + kartu judul dibakar, tanpa audio). Audio asli: `bash encode.sh audio/<file>.wav`.
- Dokumen di `Produksi/docs`: Naskah_dan_Cue_Audio, subtitle.srt, Caption_dan_Email, Laporan_Bukti_Rubrik, Laporan_QA.
- Sisa: rekam suara tim, upload (Drive/IG/TikTok/form BIDCC) -> butuh konfirmasi user; tanya dosen soal durasi & tenggat UTS.
- Catatan visual: wajah mahasiswa jarang terlihat; wajah Bu Lastri kadang tertutup properti.

## 8. Versi 2 (26 Okt 2026, malam) — look Ghibli/Pocari, 2 file siap render
- File: `UAS UTS/COMGRAPH_UAS_GHIBLI.blend` (Kuwahara lukisan, bloom lembut, hangat) dan `COMGRAPH_UAS_POCARI.blend` (cerah, biru jernih, bloom kuat). Dibuat dari `COMGRAPHTHEORYUASLOMBA.blend` (kerja utama, gaya Ghibli aktif). Ganti gaya: `exec(17_styles.py)` dengan `STYLE`.
- Skrip baru: `16_ghibli_look` (material dicat + langit/awan prosedural), `17_styles`, `18a/18b` (tekstur lukisan + pasang), `19_extras` (pohon; `MAKE_ALL=False` = pohon saja), `20_cars` (Kenney Car Kit CC0, `assets/kenney`), `21_npc` (klon MHS jadi NPC1-6 berjalan), `22a/22b` (papan QRIS + layar HP asli, kode QR dummy via `segno`).
- GOTCHA BESAR: `object.copy()` BERBAGI Action. Klon NPC wajib `animation_data_clear()` (+ shape key), kalau tidak tokoh asli ikut berjalan mengikuti NPC. Setelah klon, bangun ulang animasi utama (CLEAR_ANIM=True lalu A,B,C,props,cameras) lalu klon NPC.
- Urutan aman setelah rebuild animasi: 22b_screens_apply (props meng-key ulang teks layar lama), 21_npc, 17_styles.
- Papan QRIS: bidang `QR face` di depan kartu; UV dibalik u agar tidak cermin; UV layar HP dibuat ulang (bukan UV kubus).
- Panel meja (`Panel_0..2`) disembunyikan dari render (artefak bidang miring).
- Python sistem (3.14) punya Pillow + segno, TANPA numpy. Blender Python punya numpy tanpa PIL.
- Belum: render penuh; audio asli; kantong kertas dipendekkan (z 0.16) agar wajah Bu Lastri terlihat.

## 9. Versi 2b (26 Okt malam) — realisme + atmosfer + daun + SFX
- Dua file: GHIBLI = dunia dilukis (Emission toon + Kuwahara), POCARI = dunia PBR "real" + GI + volumetrik + bloom kuat, tokoh anime di keduanya. Pasang: `17_styles.py` lalu `25_atmos.py` (`set_realistic()` menyambung ulang Principled/Emission pada material berlabel GHIBLI).
- Tanaman realistis Poly Haven (CC0) `23_plants.py` (+getar angin `24_autumn.py` Displace+vertex group `canopy`); daun musim gugur GUGUR DARI POHON: `24a_leaf_tex.py` (tekstur) + `24b_fall_from_trees.py` (driver ekspresi `fmod`, tanpa partikel; simulasi partikel + Wind NaN/terbang -> ditinggalkan).
- UI ponsel generik "DompetKu" (referensi tata letak e-wallet, tanpa merek): `22c_screens_v2.py`, urutan layar `22d_screens_seq.py`.
- Rambut mahasiswa diperpanjang menutupi pelipis+tengkuk (`04c_hair.py` cabang `else`).
- SFX sintesis: `Produksi/audio/sfx` (21 WAV + `sfx_mix.wav` 90 dtk) dibuat `scripts/make_sfx.py`; placeholder, belum diaudisi.
- Waktu render uji 1080x1920 / 48 sampel: ±12 dtk per frame (volumetrik+raytracing) = ±9 jam per file. Opsi hemat: sampel 32, `volumetric_tile_size='8'`, tanpa volumetrik di shot close-up.
- Urutan rebuild penuh: 12_rebuild_chars -> 04e_face_fit -> 09_boot(CLEAR_ANIM) A,B -> C,props,cameras -> 22b,22d -> 21_npc -> 17,25.

## 10. Versi 2c (27 Okt) — tangan berjari, genggaman, QA diperketat
- TANGAN: 4 jari + jempol bertulang (30 tulang jari) di `04a_body.py` + `05_rig.py`; `KEYED` di `06_anim_core.py` memuat tulang jari. Pose genggam `GRIPS` + interval `HOLDS` + `Hold()/G()` (mode tangan `("frame", wrist, (arah_jari, arah_telapak))`) di `07_acting_lib.py`; `finish_grips()` dipanggil di akhir `11_props.run_props()`. Penjelasan: `Produksi/docs/Anatomi_dan_Genggaman.md`.
- Bug berat yang ditemukan QA: (1) teks spanduk meledak karena cache kain usang -> layar cokelat polos di S07 (bake ulang `Spanduk_Kain`, `is_baked` harus True); (2) lokasi objek rig tidak dipulihkan saat animasi dilanjutkan antar panggilan MCP -> mahasiswa "berdiri" di x=3,37 selama S11–S13 (perbaikan di `09_boot.py`: set `rig.location`); (3) object.copy() berbagi Action (lihat bagian 8).
- S08: papan QRIS dipegang dengan jepit tepi samping (jempol melingkar ke muka papan), Bu Lastri condong 30° agar sampai; papan sudah di tangan sejak frame pertama S08.
- Serah-terima kantong: kedua tangan memegang tepi lipatan kantong di sisi berlawanan, pusat kantong sama (`HAND + (-0.02,0,-0.07)`); tangan Bu Lastri mundur di f2300 agar tidak tabrakan.
- QA terakhir (frame 10–2690 tiap 20): 0 tembus >1,2 cm, 0 overlap antar-karakter, kaki menapak. Nampan dipangkas (tepi belakang y 0,252; tepi kanan x −0,20).
- Kamera: noise genggam `27_camera_polish.py`; S13 dari depan-kanan (1.75,-1.55,1.60).
- Skill/tool eksternal: 31 skill sudah ada di `UAS UTS/.claude/skills`; generator AI (Meshy/Tripo/Higgsfield/3D AI Studio) sengaja TIDAK dipakai (aturan BIDCC).


## 11. STATUS RENDER & CARA MELANJUTKAN (27 Okt 2026) — BACA INI DULU
- Semua catatan/memori proyek ada di folder `Computer Graphic/Agent/` (file ini, `UAS_docs/` = laporan QA/rubrik/naskah/caption/anatomi, `memory_claude/` = salinan memori Claude). Skrip kerja tetap di `UAS UTS/Produksi/scripts/` (jalur dipakai kode).
- File siap render: `UAS UTS/COMGRAPH_UAS_POCARI.blend` dan `COMGRAPH_UAS_GHIBLI.blend` (1080x1920, 30 fps, 2700 frame, EEVEE 20 sampel, volumetrik tile 8, tanpa motion blur). Kerja utama: `COMGRAPHTHEORYUASLOMBA.blend` (gaya Ghibli aktif).
- RENDER (bisa dilanjutkan/aman dimatikan): `UAS UTS/Produksi/render/run_semua.ps1` (Pocari lalu Ghibli) atau `mulai_render.ps1 -Gaya Pocari|Ghibli [-Dari N -Sampai M]`; pantau `status_render.ps1 -Gaya ...`. Frame ke `Produksi/frames_pocari|frames_ghibli/f_####.png` (tulis .tmp lalu rename; frame < 20 KB dianggap belum jadi). Estimasi ±9–12 dtk/frame -> ±7–9 jam per gaya.
- Setelah selesai: `GAYA=pocari bash Produksi/encode.sh [audio.wav]` -> `Final_Satu_Stiker_Satu_Warung_pocari.mp4` (subtitle dari `Produksi/docs/subtitle.srt`; kartu judul dibakar). SFX draf: `Produksi/audio/sfx/sfx_mix.wav`.
- Analisis glitch dari frame hasil render: `Produksi/render/qa_framediff.py` (ubah folder ke frames_*). Frame cacat: hapus PNG-nya lalu jalankan lagi mulai_render (hanya frame yang hilang dirender).
- Profil waktu (penting): pohon Poly Haven (mesh LOD1 hasil Decimate 0.26, `island_tree_02_LOD1`) ±3,5 dtk; bayangan pohon hanya T0/T1; kabut ATMOS ±1 dtk; sampel 48 -> 20 hemat 40%.
- Perubahan v2d: bobot jaket/celana = salinan bobot badan terdekat (hilangkan kulit menembus di siku); outline lebih tipis & berwarna, tipis di jari (grup `OUTLINE_T`); shader toon: bayangan berwarna, AO lukis, serat kain, helai rambut; kerah jaket diturunkan (tidak ada "sayap"); kamera S04 reverse-shot, S13 depan-kanan.
- Referensi gaya yang dipakai: Ghibli = bayangan BERWARNA (bukan sekadar gelap), daun = cahaya matahari + pantulan langit + pantulan hangat tanah, latar berlapis; Genshin-like = rampa bayangan, bayangan lukis di lipatan, rim light, outline tipis (Ben Ayers NPR shader, 80.lv, Godot toon).
- Batas jujur: tokoh tetap prosedural (bukan aset seniman) sehingga tidak setara Genshin/ZZZ; opsi lanjutan: VRoid Studio (gratis, GUI) lalu impor VRM, perlu kerja manual tim.

## 12. Update 27 Okt 2026 (pagi)
- POCARI SELESAI: 2700/2700 frame (6 GB) di `UAS UTS/Produksi/frames_pocari`; analisis frame-diff (1350 frame): 0 lonjakan, 0 terbakar, 0 gelap. Video: `UAS UTS/Produksi/Final_Satu_Stiker_Satu_Warung_pocari.mp4` (1080x1920, 30 fps, 90 dtk, 35 MB, tanpa suara, subtitle + kartu judul dibakar via `encode.sh`).
- GHIBLI DIJEDA di 139/2700 frame (`frames_ghibli`). Lanjut: `Produksi/render/mulai_render.ps1 -Gaya Ghibli` (±25 dtk/frame karena Kuwahara; sisa ±18 jam). Opsi percepat: kurangi sampel / ukuran Kuwahara, atau render sebagian shot.
- Belum: suara asli tim (mux: `GAYA=pocari bash encode.sh audio/<file>.wav`), cek aturan BIDCC soal alat AI, konfirmasi dosen soal durasi, upload (butuh persetujuan user).

## 13. V3 — perbaikan tangan/lengan (mulai 2026-10-27)
Keluhan user: tangan glitch, lengan tak sesuai anatomi, cara memegang benda aneh. Diagnosis (lihat frame f1395/f2300 + close-up):
- mesh tangan lama rusak (jari menyatu, retak bergerigi); lengan bawah terpuntir "bungkus permen"; sudut pergelangan 60-108 derajat (manusia <45).
Perbaikan (file kerja: `UAS UTS\COMGRAPH_UAS_V3.blend`, jangan timpa POCARI/GHIBLI lama):
- `scripts/31_hands.py`: tangan baru = metaball kapsul/elipsoid -> mesh utuh (K=0.56), bobot dari jarak segmen; BODY lama dipotong (bobot hand+jari >0.5). `rebuild_hands(rig)`.
- `scripts/32_twist.py`: tulang forearm_tw1/2.L/R (Copy Rotation Y dari hand, 0.34/0.68) + bobot ramp. `add_twist`, `reweight_forearm`, `twist_weights_for_hand`.
- `scripts/30_closeup.py`: close(frame, rig, bone, out, dist, off) render diagnostik (menimpa marker kamera).
- Urutan per rig: add_twist -> rebuild_hands -> reweight_forearm -> twist_weights_for_hand (panggil open_mainfile di call TERPISAH).
Sisa: penalti sudut pergelangan di `_set_pole` (07_acting_lib), re-tune GRIPS utk jari lebih tebal, rebuild animasi (09_boot + 08a/b/c + 11_props), wajah mahasiswa kosong (hidung/mulut), tambalan jaket bahu, gorengan melayang, tangan Lastri tumpuk di wajah, QA lihat-per-frame.

### 13b. Progres V3 (lanjutan, 2026-10-27)
Sudah selesai di `COMGRAPH_UAS_V3.blend` (disimpan): tangan baru semua 8 rig (+twist bone, WRIST_LIMIT constraint, `_limit_wrist` di 07: tekuk maks 42 deg), Bu Lastri berdiri di `Lantai_Warung` (L_POS z=0.22; gaze M ke wajahnya ikut +z), rambut belakang `*_HAIR_NAPE` (LASTRI & MHS), tali celemek & tali ransel dibangun ulang (`34_straps.py`, ray=True utk MHS), batas gerak mata (EYE_LIMIT), regangan jari (SPREAD di 07), bag grip x +-0.09, hand tray/counter dinaikkan.
QA numerik V3 (step 10 frame): tembus hanya 1.3 cm (f1331 tray, 4 verts) & 1.9 cm (f2231 MHS tangan vs counter top) ; overlap karakter 0.
Belum: ubah M 2226 target (clip counter), QA gerak (qa_motion_bg.py jalan di Blender latar -> render/qa_motion.json), jaket bahu (sliver kulit) kecil, 17_styles/25_atmos utk membuat 2 varian (Ghibli/Pocari) dari V3, render ulang SEMUA (frames lama usang), encode, audio.
Catatan teknis: frame_set di file ini ~1 dtk/frame (kain/daun) -> sapuan 2700 frame lewat Blender latar (`blender.exe --background file --python skrip`), bukan lewat MCP (timeout).

### 13c. Status akhir sesi V3 (2026-10-27 malam)
- File siap render: `UAS UTS\COMGRAPH_V3_POCARI.blend` dan `UAS UTS\COMGRAPH_V3_GHIBLI.blend` (animasi terbaru, tangan baru, QA numerik 0 tembus >=1.2 cm & 0 overlap pada sampel tiap 12 frame; QA dilakukan pada file Ghibli, Pocari dibuat dari file yg sama).
- Perubahan tambahan sejak 13b: WRIST_LIMIT urutan Euler YXZ (X +-45, Z +-22) -> tekuk pergelangan <= ~45; penalti siku di atas bahu (`_elbow_score`); jalur papan QRIS dipindah ke sisi tubuh & titik genggam diturunkan (08b `P()`); M 2226 target dinaikkan (08c).
- Pratinjau gerak resolusi rendah: `render/preview_bg.py` (frame_step 3, 33%, 4 sampel) -> `render/prev_pocari/p_*.png`; encode: `ffmpeg -framerate 10 -i p_%04d.png ...`.
- Belum: render penuh ulang (frames_pocari/ghibli lama USANG -> hapus sebelum render baru), encode, audio asli, baca hasil pratinjau.
- Rekomendasi: render Pocari penuh dulu (~9 jam), Ghibli (~19 jam) belakangan / per sesi dengan `mulai_render.ps1` (ganti nama file blend ke V3 di skrip render bila perlu).

### 13d. Sesi malam 28 Okt 2026 (kerja lokal; Pocari dibatalkan, fokus Ghibli)
File kerja: `UAS UTS/COMGRAPH_V3_GHIBLI.blend` (tersimpan). Tambahan sejak 13c:
- Wajah Ghibli (`35_ghibli_face.py`): mata skala 0.80, iris besar gelap (cos 0.58), sklera krem, garis kelopak tebal, EYE_LIMIT (X+-18, Z+-30), highlight dipindah; rahang dibulatkan (`soften_jaw` inline: x*(1+0.20*t^0.8), dagu maju 6 mm) lalu `nape_cap2` dibuat ulang; blush diperkecil 0.72; kelopak menyipit saat senyum (driver `location.z` lid/lidlow dari shape key `smile`).
- Poles animasi (`36_polish_anim.py`): overshoot+settle, anticipation, overlap jari (+1/2/3 frame), kepala menyusul mata, `smooth_poles` (sudut pole IK). WAJIB dijalankan SEKALI setelah rebuild animasi (A,B,props) -> urutan: polish(L), polish(M), smooth_poles(L/M), lalu hair spring.
- Rambut sekunder (`37_hair_spring.py`): pegas-peredam dari `render/head_rot.json` (hasil `qa_motion_bg.py`); jalankan ulang setelah animasi berubah.
- Papan QRIS tetap tegak (constraint LIMIT_ROTATION `KEEP_UPRIGHT` pada `QRIS_DUMMY_NONAKTIF`); rak `Shelf`+`Thermos` dinaikkan +0.42 (Lastri berdiri di lantai 0.22); tanah/aspal dicerahkan, exposure -0.55.
- QA: tekuk pergelangan max 45 deg (0 frame >45), 0 tembus >=1.2 cm, 0 overlap (sampel tiap 9 frame). Lonjakan sisa: teleport sah di batas shot (f241-243, 1502-1503), gerak penjepit f2172-2231 (0.11-0.14).
- `render/mulai_render.ps1` sekarang memakai `COMGRAPH_V3_GHIBLI.blend` (Pocari dihapus dari opsi).
- Belum: pratinjau penuh di `render/prev_ghibli/` (jalan di latar) -> encode & tonton; hapus `frames_ghibli` lama sebelum render; render penuh ~19 jam.
