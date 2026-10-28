# Render per sesi yang bisa dilanjutkan. Klik kanan > Run with PowerShell, atau:
#   powershell -ExecutionPolicy Bypass -File mulai_render.ps1 -Gaya Ghibli
#   powershell -ExecutionPolicy Bypass -File mulai_render.ps1 -Gaya Ghibli -Dari 1 -Sampai 900     (render sebagian)
# BOLEH DITUTUP / KOMPUTER DIMATIKAN kapan saja. Jalankan lagi perintah yang sama = lanjut dari frame terakhir yang selesai.
param(
  [ValidateSet("Ghibli")][string]$Gaya = "Ghibli",      # Pocari dibatalkan; fokus Ghibli
  [int]$Dari = 1, [int]$Sampai = 2700, [int]$Sampel = 20,
  [string]$Blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
)
$root = Split-Path -Parent $PSScriptRoot            # ...\UAS UTS\Produksi
$blend = Join-Path (Split-Path -Parent $root) ("COMGRAPH_V3_" + $Gaya.ToUpper() + ".blend")
$out = Join-Path $root ("frames_" + $Gaya.ToLower())
if (-not (Test-Path $blend)) { Write-Host "File tidak ada: $blend"; exit 1 }
Write-Host "Gaya   : $Gaya"; Write-Host "File   : $blend"; Write-Host "Output : $out"; Write-Host "Rentang: $Dari - $Sampai, sampel $Sampel"
& $Blender -b $blend --python (Join-Path $PSScriptRoot "render_resume.py") -- $out $Dari $Sampai $Sampel
Write-Host "Berhenti. Jalankan lagi untuk melanjutkan bila belum selesai."
