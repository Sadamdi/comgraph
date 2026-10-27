# Instalasi Blender MCP dari nol untuk Blender 5.x
# Blender 5 menghapus add-on legacy, jadi add-on dipasang sebagai startup script.

$ErrorActionPreference = "Stop"
$BlenderVersion = "5.2"

Write-Host "=== Blender MCP Installer ===" -ForegroundColor Cyan

# 1. cek uvx
if (-not (Get-Command uvx -ErrorAction SilentlyContinue)) {
    Write-Host "uvx tidak ditemukan. Install dulu: https://docs.astral.sh/uv/" -ForegroundColor Red
    exit 1
}
Write-Host "[1/5] uvx OK"

# 2. cek Blender
$blenderExe = "C:\Program Files\Blender Foundation\Blender $BlenderVersion\blender.exe"
if (-not (Test-Path $blenderExe)) {
    Write-Host "Blender $BlenderVersion tidak ditemukan di $blenderExe" -ForegroundColor Red
    exit 1
}
Write-Host "[2/5] Blender $BlenderVersion OK"

# 3. isi cache uv + temukan addon.py di dalam paket
Write-Host "[3/5] Mengunduh paket blender-mcp..."
uvx blender-mcp --help | Out-Null

$addonSrc = Get-ChildItem -Path "$env:LOCALAPPDATA\uv\cache\archive-v0" -Recurse -Filter "addon.py" -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -like "*blender_mcp*" } |
            Select-Object -First 1
if (-not $addonSrc) {
    Write-Host "addon.py tidak ketemu di cache uv." -ForegroundColor Red
    exit 1
}

# 4. pasang sebagai startup script
$startup = Join-Path $env:APPDATA "Blender Foundation\Blender\$BlenderVersion\scripts\startup"
New-Item -ItemType Directory -Force -Path $startup | Out-Null
Copy-Item $addonSrc.FullName (Join-Path $startup "blender_mcp.py") -Force

$autostart = Join-Path $PSScriptRoot "blender_mcp_autostart.py"
if (Test-Path $autostart) {
    Copy-Item $autostart (Join-Path $startup "blender_mcp_autostart.py") -Force
} else {
    Write-Host "blender_mcp_autostart.py tidak ada di folder script ini." -ForegroundColor Yellow
}

# folder repo extension yang kadang bikin warning WinError 3
$ext = Join-Path $env:APPDATA "Blender Foundation\Blender\$BlenderVersion\extensions"
New-Item -ItemType Directory -Force -Path (Join-Path $ext "user_default") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ext "blender_org")  | Out-Null
Write-Host "[4/5] Startup script terpasang di $startup"

# 5. verifikasi di mode background
Write-Host "[5/5] Verifikasi..."
$expr = "import bpy; print('MCP_TYPES_FOUND=' + str(len([t for t in dir(bpy.types) if 'BLENDERMCP' in t.upper()])))"
$out = & $blenderExe -b --python-expr $expr 2>&1 | Select-String "MCP_TYPES_FOUND"

if ($out -and $out -notmatch "MCP_TYPES_FOUND=0") {
    Write-Host ""
    Write-Host "BERHASIL. $out" -ForegroundColor Green
    Write-Host "Buka Blender - server nyala otomatis di port 9876." -ForegroundColor Green
    Write-Host "Catatan: BlenderMCP TIDAK muncul di Preferences > Add-ons (normal untuk Blender 5)." -ForegroundColor Yellow
    Write-Host "         Yang muncul adalah tab BlenderMCP di sidebar N viewport 3D." -ForegroundColor Yellow
} else {
    Write-Host "Verifikasi gagal - add-on tidak ter-register." -ForegroundColor Red
    exit 1
}
