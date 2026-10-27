# Health check koneksi Blender MCP
$ok = $true

$proc = Get-Process blender -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host "[OK]   Blender jalan (PID $($proc.Id -join ', '))" -ForegroundColor Green
} else {
    Write-Host "[GAGAL] Blender tidak jalan - buka Blender dulu" -ForegroundColor Red
    $ok = $false
}

$port = Test-NetConnection -ComputerName 127.0.0.1 -Port 9876 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($port) {
    Write-Host "[OK]   Port 9876 LISTENING - add-on siap" -ForegroundColor Green
} else {
    Write-Host "[GAGAL] Port 9876 mati" -ForegroundColor Red
    Write-Host "        Cek tab BlenderMCP di sidebar N, klik Connect to MCP server" -ForegroundColor Yellow
    $ok = $false
}

$startup = Join-Path $env:APPDATA "Blender Foundation\Blender\5.2\scripts\startup"
foreach ($f in @("blender_mcp.py", "blender_mcp_autostart.py")) {
    if (Test-Path (Join-Path $startup $f)) {
        Write-Host "[OK]   $f terpasang" -ForegroundColor Green
    } else {
        Write-Host "[GAGAL] $f hilang - jalankan install_blender_mcp.ps1" -ForegroundColor Red
        $ok = $false
    }
}

if (Get-Command uvx -ErrorAction SilentlyContinue) {
    Write-Host "[OK]   uvx tersedia" -ForegroundColor Green
} else {
    Write-Host "[GAGAL] uvx tidak ada di PATH" -ForegroundColor Red
    $ok = $false
}

Write-Host ""
if ($ok) { Write-Host "Semua siap." -ForegroundColor Green }
else     { Write-Host "Ada yang perlu dibetulkan - lihat Agent\README.md bagian Troubleshooting" -ForegroundColor Yellow }
