@echo off
curl -s -m 5 http://localhost:3900/health > "D:\adam kuliah\Semester 5\Computer Graphic Praktikum\Agent\tools\vs_chk.log" 2>&1
echo. >> "D:\adam kuliah\Semester 5\Computer Graphic Praktikum\Agent\tools\vs_chk.log"
echo DONE >> "D:\adam kuliah\Semester 5\Computer Graphic Praktikum\Agent\tools\vs_chk.log"
