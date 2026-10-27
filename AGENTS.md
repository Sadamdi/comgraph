# Instruksi untuk AI Agent

Dibaca otomatis oleh Claude Code / Cursor / Codex saat bekerja di project root ini.

## Konteks

Repo tugas **Praktikum Grafika Komputer** semester 5. Tiap pertemuan punya folder
sendiri berisi PDF modul; hasil kerja disimpan sebagai `.blend` di folder yang sama.

```
Computer Graphic Praktikum/
├── Agent/           <- dokumentasi + script setup MCP
├── Pertemuan 1/
├── Pertemuan 2/     <- Modul 2 - Modelling Basket.pdf
└── ...
```

## Aturan kerja

1. **Baca PDF modulnya dulu.** `pdftoppm` tidak terpasang; pakai `pypdf`:
   ```python
   from pypdf import PdfReader
   r = PdfReader(path)
   for p in r.pages: print(p.extract_text())
   for p in r.pages:
       for im in p.images: open(name,'wb').write(im.data)   # gambar langkah
   ```
   Teks saja sering tidak cukup — banyak parameter ada **di gambar**. Ekstrak gambarnya.

2. **Ikuti modul apa adanya.** Jangan menambah material, lighting sinematik, atau
   detail yang tidak diminta kecuali diminta eksplisit. Kalau modul bilang
   "torus major radius 0.75, minor 0.05", pakai angka itu persis.

3. **Satu file `.blend` per modul**, disimpan di folder pertemuannya:
   `Pertemuan N/Modul N - <nama>.blend`

4. **Mulai bersih** sebelum modelling:
   ```python
   bpy.ops.wm.read_homefile(use_empty=True)
   ```
   Panggil ini **sendirian** dalam satu eksekusi. Setelah `read_homefile`,
   `bpy.context.object` bisa `None` — pakai `bpy.context.view_layer.objects.active`.

## Gotcha yang sudah terbukti

| Masalah | Solusi |
|---|---|
| `'Context' object has no attribute 'object'` | pakai `bpy.context.view_layer.objects.active` |
| `BMesh data of type BMFace has been removed` | ambil `f.index` **sebelum** `bm.free()`, dan `bm.faces.index_update()` dulu |
| `'Object' object has no attribute 'shade_smooth'` | itu operator, bukan method. Pakai `for p in me.polygons: p.use_smooth = True` |
| MCP putus saat render lama | lihat pola di bawah |
| Viewport screenshot kosong / bukan camera view | render ke file saja, jangan andalkan `get_viewport_screenshot` |

## Operator edit-mode dari script (Blender 5)

| Yang sering salah | Yang benar |
|---|---|
| `bpy.ops.mesh.inset_faces` | tidak ada — pakai **`bpy.ops.mesh.inset(thickness=...)`** |
| `bpy.ops.transform.shear(value=...)` | di Blender 5 parameternya **`angle=`** (radian), bukan `value` |
| `transform.shear` langsung dipanggil | `poll() failed` — butuh override konteks VIEW_3D (lihat di bawah) |
| Simpan referensi `BMFace` lalu panggil operator | referensi jadi invalid. Ambil ulang bmesh **setelah** tiap operator |
| Edit vertex pakai koordinat world | `v.co` itu **lokal**. Objek dengan location != 0 akan tergeser |

Override konteks untuk operator transform:

```python
area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
region = next(r for r in area.regions if r.type == 'WINDOW')
with bpy.context.temp_override(area=area, region=region, space_data=area.spaces.active):
    bpy.ops.transform.shear(angle=math.radians(15), orient_axis='Y',
                            orient_axis_ortho='X', orient_type='GLOBAL')
```

Cek nama parameter operator yang benar:

```python
print([p.identifier for p in bpy.ops.transform.shear.get_rna_type().properties])
```

Operator yang **tidak** bisa dipakai dari script (butuh mouse): `mesh.knife_tool`,
`mesh.loopcut_slide`, `mesh.bisect` (interaktif). Gantinya:
- knife / bisect → `bmesh.ops.bisect_plane(...)`
- loop cut → `bmesh.ops.subdivide_edges(bm, edges=<edge vertikal>, cuts=N, use_grid_fill=True)`

Temuan tambahan dari Modul 3:

| Hal | Catatan |
|---|---|
| Shade Auto Smooth | `bpy.ops.object.shade_auto_smooth(angle=...)` **ada** di Blender 5.2; ia menambah modifier bertipe `NODES` (Smooth by Angle), bukan flag di mesh |
| `bpy.ops.uv.export_layout` | butuh `temp_override(area=<VIEW_3D>)`; objek harus di Edit Mode dengan semua face terseleksi |
| `bmesh.ops.bevel` pada satu edge | ujung edge jadi "duri". Setelah bevel, ratakan verteks yang melewati bidang tepi aslinya |

Yang tetap jalan normal: `mesh.inset`, `mesh.extrude_region_move`, `mesh.bevel`,
`mesh.spin`, `mesh.unsubdivide`, `mesh.remove_doubles`, `mesh.delete`, `transform.resize`.

## Pola render yang aman

`execute_blender_code` punya timeout socket. Render berat akan memutus koneksi
walaupun Blender tetap bekerja. Jangan panik dan jangan restart Blender —
render ke file lalu tunggu filenya stabil:

```python
sc.render.filepath = r"C:\...\hasil.png"
sc.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
```

Lalu dari shell, tunggu ukuran file berhenti bertambah:

```bash
for i in $(seq 1 20); do
  if [ -f "$F" ]; then
    a=$(stat -c%s "$F"); sleep 4; b=$(stat -c%s "$F")
    [ "$a" = "$b" ] && { echo SELESAI; break; }
  fi
  sleep 10
done
```

Untuk cek cepat komposisi, render kecil dulu:
`resolution_percentage = 45`, `cycles.samples = 48`.

## Setup GPU (opsional, untuk Cycles)

```python
cp = bpy.context.preferences.addons['cycles'].preferences
cp.compute_device_type = 'OPTIX'      # atau CUDA / HIP / ONEAPI
cp.get_devices()
for d in cp.devices: d.use = (d.type == 'OPTIX')
scene.cycles.device = 'GPU'
```

## Sebelum mulai — pastikan koneksi hidup

```powershell
netstat -an | Select-String 9876     # harus LISTENING
```

Kalau tidak: buka Blender. Server nyala sendiri lewat startup script
(`Agent/scripts/blender_mcp_autostart.py`). Detail di `README.md`.

## Hasil yang sudah ada

| Modul | File | Status |
|---|---|---|
| Modul 1 — Interface Blender | `Pertemuan 1/` | **tidak ada tugas** (tertulis di halaman terakhir PDF) |
| Modul 2 — Modelling Basket | `Pertemuan 2/Modul 2 - Modelling Basket.blend` | selesai — bola basket + ring basket, dikerjakan dengan operator sesuai modul |
| Modul 3 — Modelling Roket | `Pertemuan 3/` | selesai — praktikum + tugas UV template |

Modul 2 dibangun mengikuti langkah aslinya: UV Sphere 16x8 -> hapus oktan -> knife ->
Mirror X/Y/Z -> bevel + extrude + scale -> Subsurf 2; tiang: cube -> inset/extrude
berulang -> Spin sumbu Y -75 derajat 12 steps -> extrude + shear -> extrude/scale jadi
papan; Torus major 0.75 minor 0.05; jaring: cylinder -> 8 edge loop -> hapus face
atas-bawah -> unsubdivide -> hapus edge bawah -> Wireframe modifier.

Objek di file Modul 2 mengikuti penamaan modul: `bola`, `Cube` (tiang), `Cube.001`
(balok penyangga), `Torus` (ring), `Cylinder` (jaring + Wireframe modifier).

### Modul 3 — Modelling Roket

Dua file di `Pertemuan 3/`:

| File | Isi |
|---|---|
| `Modul 3 - Modelling Rocket.blend` | hasil praktikum, objek masih terpisah + modifier utuh |
| `Modul 3 - Tugas UV Template.blend` | tugas: semua di-join jadi `Roket` + image texture (di-pack) |
| `roket_uv_template.png` | hasil Export UV Layout 2048² |
| `Roket.png` | texture jadi (badan putih + logo UIN, sayap merah, ekor abu) |
| `Modul 3 - Hasil Render.png` | render Cycles 1600², GPU OPTIX |

Penamaan sesuai modul: `Cube` (badan), `Cylinder` (ekor), `Cube.001`/`Cube.002` (sayap).

**Angka yang dibaca dari screenshot PDF** (bukan dari teks — teksnya tidak menyebut angka):

| Langkah | Nilai | Sumber |
|---|---|---|
| Subsurf badan | Viewport 1 → 2, Render 2 | hal. 1 & 4 |
| Geser edge loop badan | `D: 1.236 m along global Z` | hal. 2 |
| Scale edge loop badan | `0.9552` | hal. 3 |
| Cylinder ekor | 16 vertices | hal. 5 |
| Inset face ekor | `Thickness 0.1418` | hal. 6 |
| Extrude face dalam ekor | `D: 1.221 m along global Z` | hal. 7 |
| Scale face ekor | `Resize 0.600` | hal. 7 |
| Geser edge atas sayap | `D: 0.3967 m along global Y` | hal. 9 |
| Bevel sayap | `Width 0.606, Segments 3` | hal. 10 (status bar) |
| Mirror sayap | Axis Y, `Mirror Object = Cube`; duplikat → Rotate Z 90° → Axis X | hal. 11–12 |

Catatan penting: **halaman 6 menulis `Scale 0.9593` untuk face atas silinder, tapi
gambarnya jelas menunjukkan kerucut.** Screenshot-nya tertangkap di tengah drag.
Kalau angka dan gambar bertabrakan, **ikuti gambarnya** — bentuk akhirlah yang dinilai.
Hal yang sama berlaku untuk `Move Y: 0.003486` di hal. 10.

Arah geser edge atas sayap: di hal. 9–10 gizmo-nya terputar, `+Y` menunjuk **ke arah
badan**. Jadi edge atas bergerak masuk (sayap menyempit di atas), bukan keluar.

Cara verifikasi yang dipakai: render halaman PDF jadi PNG (`pymupdf`, dpi 150), crop
header operator untuk baca angkanya, lalu bandingkan screenshot viewport sendiri
berdampingan dengan gambar PDF di tahap yang sama. Iterasi sampai siluetnya sama.

Proses tugas: apply semua modifier → join → mark seam (sudut > 35°, meridian x=0 sisi
−Y, ring bawah badan) → unwrap → `average_islands_scale` + `pack_islands` →
`uv.export_layout` → texture di-generate dengan Pillow dengan me-rasterize poligon UV
per material → node Image Texture ke Base Color.

Orientasi logo di texture **jangan ditebak**: hitung korelasi antara `v` island dan `z`
dunia (dan `u` vs `x`) untuk menentukan perlu flip atau tidak. Untuk face di sisi `+Y`
yang dilihat dari depan, `u` memang menurun terhadap `x` — itu normal, jangan dibalik.

### Modul 4-8 — Karakter, Rigging, Animasi

Modul 5-8 diawali "Buka dan Lanjutkan File Blender Minggu Lalu" — **berantai**, harus berurutan.

| File | Isi |
|---|---|
| `Pertemuan 4/Modul 4 - Modelling Character Part 1.blend` | kepala + leher + badan (objek `Karakter`) |
| `Pertemuan 5/Modul 5 - Modelling Character Part 2.blend` | + lengan, telapak, kaki, telapak kaki. Mirror + Clipping |
| `Pertemuan 6/Modul 6 - Modelling Character Part 3.blend` | + `Baju` `Celana` `Sepatu` `Rambut`, mata, mulut, warna |
| `Pertemuan 7/Modul 7 - Rigging.blend` | + `Armature` 20 tulang, symmetrize, parent, pose |
| `Pertemuan 8/Modul 8 - Animating.blend` | + animasi jalan, keyframe 1/10/20, frame 1-20 |
| `Pertemuan 8/Modul 8 - Tugas Mixamo (export).fbx` | export FBX untuk diunggah ke mixamo.com |

**Modul 4 — counter status bar PDF** (cocokkan persis):
26/48/24 (hal.2) -> 32/60/30 (hal.5) -> 38/72/36 (hal.7 atas) -> 56/108/54 (hal.7 bawah)
-> 68/132/66 (hal.11). Topologinya: mulai 26, lalu **5x extrude region 2-face** +
**2x loop cut** (masing-masing +6v/+12e/+6f). Sudah diverifikasi kena di tiap checkpoint.

Angka operator Modul 4: subdivide `Cuts 1, Smoothness 1.000, N-Gons, Inner Vert`;
proportional edit kepala `Y 0.161, Z -0.482, Smooth, Size 2.358`; move leher
`Y -1.16, Z -0.581, Size 1.331`; ratakan `S,Z,0 Size 0.83`.

**Proporsi karakter — diukur dari hal.17 Modul 5 (Front Orthographic), satuan = lebar badan:**

| Ukuran | Rasio |
|---|---|
| tinggi torso (bahu->pinggul) | 1.93 |
| panjang kaki | 3.36 |
| tebal kaki | 0.49 |
| jangkauan lengan (dari tengah) | 3.55 |
| tebal lengan | 0.34 |

Ini **paling menentukan**. Kesalahan terbesar sebelumnya: kaki & lengan dibuat setengah
panjang seharusnya -> karakter jadi cebol dan jelek. Ukur dulu dari hal.17, jangan mengarang.

**Bentuk telapak tangan** (hal.7 Modul 5): objek terpisah **28 vertex**, bentuk *mitten*
menggembung — pipih di Z, melebar di Y, ujung membulat, plus ibu jari. **Bukan** jari-jari
terpisah. Hasil akhir Modul 5 setengah badan ~119 vertex.

**Anggota badan harus bulat**: modul menyuruh *loop cut badan dulu* (hal.3) sebelum bikin
lengan, supaya bukaan bahu jadi 8 vertex. Kalau langsung LoopTools Circle pada face
4-vertex, lengannya jadi pipa segi-4 seperti tongkat.

**Modul 6 thickness Solidify (eksak):** baju `-0.1`, celana `-0.08`, sepatu `-0.07`,
rambut `-0.05`. Mata: UV sphere `segments 8, ring_count 8`, hitam.

**Gotcha yang mahal:**

| Hal | Catatan |
|---|---|
| `bpy.ops.object.armature_add(location=(0,0,z))` | **jangan**. Koordinat `edit_bones` itu ruang LOKAL armature; kalau objeknya digeser, semua tulang meleset sejauh itu dan bobot jadi ngawur (mesh melar seperti kawat). Selalu `location=(0,0,0)`, lalu tulis head/tail dalam angka dunia. Verifikasi: `(arm.matrix_world @ bone.head_local).z` harus sama dengan nilai yang dimaksud |
| `parent_set(type='ARMATURE_AUTO')` | **gagal diam-diam** di karakter ini — semua bobot 0, mesh tidak bergerak. Cek `sum(g.weight for v in mesh.vertices for g in v.groups)`; kalau 0, hitung bobot sendiri dari jarak ke segmen tulang (2 tulang terdekat, dicampur) |
| Pose tulang lewat `rotation_euler` | sumbu lokal tulang tidak intuitif (`Y` = roll sepanjang tulang). Pakai quaternion: `ql.inverted() @ rest.rotation_difference(arah) @ ql`, `ql = bone.matrix_local.to_quaternion()` |
| `bmesh.ops.subdivide_edges(smooth=1.0)` | bukan padanan `bpy.ops.mesh.subdivide(smoothness=1.0)`. Yang pertama bikin bentuk berlian (radius 2.65); yang benar radius seragam 1.732 |
| `bpy.context.screen` sesudah `wm.open_mainfile` | jadi `None`. Ambil `bpy.context.window_manager.windows[0].screen`, lalu `temp_override(window=,screen=,area=,region=)` agar `mode_set` bisa jalan |
| `action.fcurves` | tidak ada di Blender 5.x. Pakai `action.layers[0].strips[0].channelbag(slot).fcurves` |
| Skrip batch multi-file | kalau gagal di tengah loop, file yang sudah lewat **sudah tersimpan**. Jalankan ulang = transformasi dobel. Ukur dulu sebelum menskala ulang |

**Cara verifikasi yang terbukti berguna:** ekstrak siluet gambar PDF secara terprogram
(threshold + lebar per baris), lalu bandingkan rasio terhadap satu fitur acuan
(lebar badan / lebar kepala). Jangan pakai tinggi total sebagai pembagi — ujung kepala
yang meruncing sering tidak terdeteksi dan hasilnya menyesatkan.

**Tugas Modul 8 (Mixamo) tidak bisa diselesaikan agen:** butuh login akun dan mengunggah
file ke situs pihak ketiga. Yang bisa hanya sampai export FBX.

## Cek kemiripan hasil vs ilustrasi PDF

```
python "Agent/scripts/cek_kemiripan.py"
```

Syarat: Blender terbuka dan port 9876 LISTENING.

Skrip ini merender tiap file `.blend` dari sudut yang sama dengan ilustrasi PDF,
lalu menghitung **IoU siluet** (irisan / gabungan) terhadap gambar modul.
Keluaran: tabel persentase di terminal + gambar `*_banding.png` di `Agent/hasil_cek/`
(merah = PDF, hijau = hasil sendiri, kuning = bagian yang cocok).

Batas metriknya — penting: IoU hanya membandingkan **garis luar**. Perubahan yang
tidak mengubah siluet (warna, lengan baju panjang, rambut, mulut) tidak menaikkan
angkanya sama sekali, bahkan bisa menurunkannya. Untuk Modul 6 ke atas, ukuran yang
lebih jujur adalah **porsi piksel per warna** (kulit / baju / celana) dibandingkan
gambar modul.

Cara melihat tulang (armature) di Blender: buka file Modul 7 atau 8, lalu pastikan
overlay viewport menyala — tombol dua lingkaran bertumpuk di kanan atas viewport,
atau `Shift+Alt+Z`. Tulang digambar sebagai overlay, jadi kalau overlay mati tulang
ikut hilang meski objeknya ada.

## Setup MCP

Semua ada di `Agent/`:
- `Agent/README.md` — instalasi, config per agent, troubleshooting
- `Agent/scripts/check_mcp.ps1` — jalankan ini dulu sebelum mulai
- `Agent/scripts/start_blender.ps1` — buka Blender + tunggu server siap


---

## UAS Teori — "Satu Stiker, Satu Warung" (BACA DULU: `Agent/UAS_Satu_Stiker_Satu_Warung.md`)

Folder `UAS UTS/` berisi tugas **teori** (animasi 90 detik untuk lomba BIDCC 2026 + UAS dosen), terpisah dari praktikum modul.
Semua catatan, urutan build, gotcha, hasil QA dan keputusan user ada di `Agent/UAS_Satu_Stiker_Satu_Warung.md`. Skrip di `UAS UTS/Produksi/scripts/`.
Aturan penting: kerja langsung di `COMGRAPHTHEORYUASLOMBA.blend` (satu file bersama, cadangan di `_backup/`); **jangan hapus objek dengan awalan nama**;
jalankan QA (`15_qa.py`) sebelum render; AI hanya alat bantu dan harus dilaporkan jujur di form lomba.


**Catatan terbaru:** semua memori/catatan UAS ada di `Agent/` (`UAS_Satu_Stiker_Satu_Warung.md` bagian 11 = status render + cara melanjutkan; `Agent/UAS_docs/` = laporan; `Agent/memory_claude/` = salinan memori).
