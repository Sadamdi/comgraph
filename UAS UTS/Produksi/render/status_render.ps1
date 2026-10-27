# Lihat progres render: powershell -ExecutionPolicy Bypass -File status_render.ps1 -Gaya Ghibli
param([ValidateSet("Ghibli","Pocari")][string]$Gaya = "Ghibli", [int]$Total = 2700)
$out = Join-Path (Split-Path -Parent $PSScriptRoot) ("frames_" + $Gaya.ToLower())
if (-not (Test-Path $out)) { Write-Host "Belum ada render untuk $Gaya"; exit }
$n = (Get-ChildItem $out -Filter "f_*.png" | Where-Object { $_.Length -gt 20000 } | Measure-Object).Count
$gb = [math]::Round(((Get-ChildItem $out -Filter "f_*.png" | Measure-Object Length -Sum).Sum) / 1GB, 2)
Write-Host ("{0}: {1}/{2} frame ({3:P0}), {4} GB" -f $Gaya, $n, $Total, ($n / $Total), $gb)
$log = Join-Path $out "_progress.txt"
if (Test-Path $log) {
  $t = Get-Content $log -Tail 40 | ForEach-Object { [double](($_ -split "`t")[1]) }
  if ($t.Count) { $avg = ($t | Measure-Object -Average).Average; Write-Host ("rata-rata {0:N1} dtk/frame, sisa ~{1:N1} jam" -f $avg, (($Total - $n) * $avg / 3600)) }
}
