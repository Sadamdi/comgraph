#!/bin/bash
# Pakai: bash encode.sh [audio.wav]   (tanpa argumen = video senyap)
cd "$(dirname "$0")"
GAYA=${GAYA:-ghibli}   # ghibli | pocari  (pakai: GAYA=pocari bash encode.sh [audio.wav])
VF="subtitles=docs/subtitle.srt:force_style='FontName=Arial,FontSize=8,Bold=1,Outline=2,Shadow=0,MarginV=150,Alignment=2',\
drawtext=fontfile='C\:/Windows/Fonts/arialbd.ttf':text='Beberapa hari kemudian':fontcolor=white:fontsize=60:borderw=4:bordercolor=black@0.7:x=(w-text_w)/2:y=h*0.16:enable='between(t,44.1,48)',\
drawtext=fontfile='C\:/Windows/Fonts/arialbd.ttf':text='Satu Stiker, Satu Warung':fontcolor=white:fontsize=64:borderw=4:bordercolor=black@0.7:x=(w-text_w)/2:y=h*0.10:enable='between(t,85,90)',\
drawtext=fontfile='C\:/Windows/Fonts/arialbd.ttf':text='Peserta BI Digital Content Competition 2026  #BIDCC2026':fontcolor=white:fontsize=30:borderw=3:bordercolor=black@0.7:x=(w-text_w)/2:y=h*0.145:enable='between(t,85,90)',\
noise=alls=2:allf=t"
if [ -n "$1" ]; then A="-i $1 -c:a aac -b:a 192k -shortest"; else A="-an"; fi
ffmpeg -y -framerate 30 -i frames_${GAYA}/f_%04d.png $A -vf "$VF" -c:v libx264 -preset medium -crf 22 -pix_fmt yuv420p -movflags +faststart Final_Satu_Stiker_Satu_Warung_${GAYA}.mp4
