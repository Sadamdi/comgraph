# Buka Blender lalu tunggu sampai server MCP siap
$blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender-launcher.exe"
if (-not (Test-Path $blender)) {
    Write-Host "Blender tidak ditemukan di $blender" -ForegroundColor Red
    exit 1
}

if (-not (Get-Process blender -ErrorAction SilentlyContinue)) {
    Write-Host "Membuka Blender..."
    Start-Process $blender
} else {
    Write-Host "Blender sudah jalan."
}

Write-Host "Menunggu server MCP di port 9876..."
for ($i = 0; $i -lt 40; $i++) {
    Start-Sleep -Seconds 2
    if (Test-NetConnection -ComputerName 127.0.0.1 -Port 9876 -InformationLevel Quiet -WarningAction SilentlyContinue) {
        Write-Host "Server siap - agent bisa mulai." -ForegroundColor Green
        exit 0
    }
}
Write-Host "Server belum nyala setelah 80 detik." -ForegroundColor Yellow
Write-Host "Buka sidebar N di viewport 3D, tab BlenderMCP, klik Connect to MCP server." -ForegroundColor Yellow
exit 1
