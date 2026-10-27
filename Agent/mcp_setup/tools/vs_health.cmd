@echo off
set OUT=D:\adam kuliah\Semester 5\Computer Graphic Praktikum\Agent\tools\vs_health.log
set SUA=D:\adam kuliah\Semester 5\Computer Graphic Praktikum\Agent\UAS\suara
echo === %date% %time% > "%OUT%"
for /L %%i in (1,1,80) do (
  curl -s -m 3 http://localhost:3900/health > "%TEMP%\vs_h.txt" 2>nul
  findstr /C:"starting" "%TEMP%\vs_h.txt" >nul || (for %%A in ("%TEMP%\vs_h.txt") do if %%~zA GTR 0 goto ok)
  timeout /t 3 /nobreak >nul
)
echo NO_HEALTH >> "%OUT%"
type "%TEMP%\vs_h.txt" >> "%OUT%"
goto end
:ok
type "%TEMP%\vs_h.txt" >> "%OUT%"
echo. >> "%OUT%"
curl -s -m 20 http://localhost:3900/openapi.json -o "%SUA%\openapi.json"
curl -s -m 20 http://localhost:3900/models -o "%SUA%\models.json"
:end
echo DONE >> "%OUT%"
