# Render kedua gaya berurutan (Pocari lalu Ghibli). Aman dimatikan; jalankan lagi untuk melanjutkan.
#   powershell -ExecutionPolicy Bypass -File run_semua.ps1
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
foreach ($g in @("Pocari", "Ghibli")) {
  Write-Host "=== Render $g ===" -ForegroundColor Cyan
  & powershell -ExecutionPolicy Bypass -File (Join-Path $here "mulai_render.ps1") -Gaya $g
}
Write-Host "SEMUA SELESAI" -ForegroundColor Green
