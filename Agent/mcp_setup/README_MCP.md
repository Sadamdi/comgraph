# Blender MCP — Panduan Setup & Pemakaian

Dokumentasi supaya **AI agent mana pun** (Claude Code, Cursor, Codex, Windsurf, dll.)
bisa langsung mengontrol Blender di komputer ini untuk mengerjakan tugas
Praktikum Grafika Komputer.

- **Project root:** `D:\adam kuliah\Semester 5\Computer Graphic Praktikum`
- **Blender:** 5.2.1 LTS — `C:\Program Files\Blender Foundation\Blender 5.2\`
- **MCP server:** [`blender-mcp`](https://github.com/ahujasid/blender-mcp) dijalankan via `uvx`

---

## 1. Arsitektur

```
AI Agent  ──stdio──>  uvx blender-mcp  ──TCP :9876──>  Add-on di dalam Blender
(Claude/Cursor/…)     (MCP server)                     (eksekusi bpy)
```

Dua bagian yang harus hidup **dua-duanya**:

| Bagian | Cara hidup | Cek |
|---|---|---|
| MCP server | Dijalankan otomatis oleh AI agent dari config | tool `mcp__blender__*` muncul |
| Add-on + socket di Blender | Auto-start saat Blender dibuka | port 9876 LISTENING |

Kalau Blender tidak terbuka, semua tool MCP akan error. **Buka Blender dulu.**

---

## 2. Catatan penting: Blender 5.x

Blender 5.0 **menghapus dukungan add-on legacy** (`scripts/addons/`). Installer bawaan
`uvx blender-mcp install-addon` menaruh file ke sana, jadi **tidak akan terbaca**.
Sistem Extensions yang baru pun gagal memuat add-on ini.

**Solusi yang dipakai di sini:** add-on dipasang sebagai **startup script**, yang masih
didukung penuh dan otomatis ter-register setiap Blender dibuka.

```
C:\Users\<user>\AppData\Roaming\Blender Foundation\Blender\5.2\scripts\startup\
├── blender_mcp.py            <- add-on (copy dari paket blender-mcp)
└── blender_mcp_autostart.py  <- menyalakan server otomatis di port 9876
```

Konsekuensi: **BlenderMCP tidak muncul di Edit > Preferences > Add-ons.** Itu normal.
Yang menandakan berhasil adalah tab **BlenderMCP** di sidebar `N` viewport 3D.

---

## 3. Instalasi dari nol

Prasyarat: Blender terpasang, dan `uv`/`uvx` ada di PATH.

```powershell
powershell -ExecutionPolicy Bypass -File "D:\adam kuliah\Semester 5\Computer Graphic Praktikum\Agent\tools\install_blender_mcp.ps1"
```

Script itu akan:
1. cek `uvx` dan lokasi Blender
2. download paket `blender-mcp` ke cache uv
3. copy `addon.py` ke folder `scripts/startup/`
4. pasang `blender_mcp_autostart.py`
5. verifikasi add-on ter-register (mode background)

Setelah itu daftarkan MCP server ke agent-nya (lihat bagian 4).

---

## 4. Konfigurasi per AI agent

### Claude Code (CLI)
```bash
claude mcp add blender -s user -- uvx blender-mcp
```

### Cursor / Windsurf / Claude Desktop
Tambahkan ke `mcp.json` (contoh siap pakai: `Agent/config/mcp.json`):
```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"]
    }
  }
}
```
Lokasi file:
- Cursor: `%USERPROFILE%\.cursor\mcp.json`
- Claude Desktop: `%APPDATA%\Claude\claude_desktop_config.json`

### Codex CLI
`~/.codex/config.toml` (contoh: `Agent/config/codex_config.toml`):
```toml
[mcp_servers.blender]
command = "uvx"
args = ["blender-mcp"]
```

> Kalau agent gagal connect dengan *timeout*, biasanya karena `uvx` sedang
> mengunduh paket. Jalankan `uvx blender-mcp --help` sekali dulu untuk mengisi cache.

---

## 5. Pemakaian harian

```powershell
# 1. buka Blender (server nyala sendiri ~1.5 detik setelah UI siap)
powershell -File "...\Agent\tools\start_blender.ps1"

# 2. cek koneksi
powershell -File "...\Agent\tools\check_mcp.ps1"
```

Lalu di agent, cukup minta hal seperti:
> "bikin bola basket sesuai Modul 2, tanpa material"

Agent akan memakai `mcp__blender__execute_blender_code` untuk menjalankan `bpy`.

---

## 6. Troubleshooting

| Gejala | Penyebab | Solusi |
|---|---|---|
| Tool `mcp__blender__*` tidak ada | MCP server belum terdaftar / agent belum restart | daftarkan config, restart agent |
| `Connection refused` / `No data received` | Blender tertutup atau server mati | buka Blender, cek port 9876 |
| Tab BlenderMCP tidak ada di sidebar `N` | startup script hilang | jalankan ulang `install_blender_mcp.ps1` |
| Tidak muncul di Preferences > Add-ons | **normal** untuk Blender 5.x | abaikan, cek sidebar `N` |
| MCP putus di tengah render | render lebih lama dari timeout socket | render ke file, lalu polling filenya (lihat AGENTS.md) |
| `WinError 3 ... extensions\user_default` | folder repo extension belum ada | `mkdir` folder tersebut, tidak mempengaruhi fungsi |

Cek manual port:
```powershell
netstat -an | Select-String 9876
```

---

## 7. Isi folder

Aturan: **semua script, catatan agent, dan riwayat kode ada di `Agent/`.** Folder
`Pertemuan N/` dan `UAS/` hanya berisi **hasil**: PDF modul, `.blend`, `.docx`/`.pdf`, render, video.

```
Computer Graphic Praktikum/
├── CLAUDE.md                    <- penunjuk 1 baris ke Agent/CLAUDE.md (wajib di root agar auto-dibaca)
├── Pertemuan N/                 <- HASIL saja: modul PDF, .blend, render
├── UAS/                         <- HASIL saja: laporan .docx/.pdf, .blend, storyboard/*.png
└── Agent/
    ├── CLAUDE.md, AGENTS.md     <- instruksi & aturan untuk AI agent
    ├── README.md                <- file ini
    ├── config/                  <- config MCP (Cursor, Claude Desktop, Codex)
    ├── mcp/                     <- blender-lab/ (MCP resmi v1.0.3), mcp-1.0.3.zip (add-on), praktikum_server.py + praktikum_ops.py
    ├── tools/                   <- bl.py (jembatan TCP), cek_kemiripan.py, *.ps1 setup MCP
    ├── hasil_cek/               <- gambar banding kemiripan
    ├── Pertemuan N/             <- script / riwayat_kode_blender.py per pertemuan
    ├── UAS/                     <- uas_scene.py, uas_panel.py, panels.txt, laporan_uas.py
    └── _riwayat/                <- kode lama yang tidak jelas milik modul mana
```

## 8. Tiga server MCP

Lihat tabel di `AGENTS.md` bagian "MCP: 3 server". Pendaftaran (sekali saja, scope user):

```bash
claude mcp add blender -s user -- uvx blender-mcp
claude mcp add blender-lab -s user -e BLENDER_MCP_PORT=9877 -e UV_LINK_MODE=copy -- uv run --directory "D:/adam kuliah/Semester 5/Computer Graphic Praktikum/Agent/mcp/blender-lab" blender-mcp
claude mcp add praktikum -s user -e UV_LINK_MODE=copy -- uv run -q --with "mcp[cli]<2" python "D:/adam kuliah/Semester 5/Computer Graphic Praktikum/Agent/mcp/praktikum_server.py"
```
Add-on resmi dipasang dari `Agent/mcp/mcp-1.0.3.zip` (Preferences > Get Extensions > Install from Disk), lalu port diubah ke 9877.
