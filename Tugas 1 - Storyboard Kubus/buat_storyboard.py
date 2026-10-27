from PIL import Image, ImageDraw, ImageFont
F="C:/Windows/Fonts/"
def f(n,s): return ImageFont.truetype(F+n,s)
B,R=f("arialbd.ttf",15),f("arial.ttf",14)
S=[("Opening","Kotak berdiri sendirian di padang","Diam, bola-bola menggelinding","Extreme long shot (static)","3 detik","Musik ceria (fade in)"),
("Si Kotak","Kotak menatap bola dengan kagum","Rotasi kepala (Z) sedikit","Close-up","2 detik","Musik ceria"),
("Mencoba Menggelinding","Kotak mencoba ikut menggelinding","Rotasi 90° per sisi (flop)","Medium shot","2 detik","Efek \"tok\" kayu"),
("Gagal","Kotak jatuh gepeng, bola melaju","Squash (scale Z 0.76)","Medium shot, low angle","1,5 detik","Efek \"bruk\" + tawa bola"),
("Ditinggal","Kotak tertinggal jauh sendirian","Diam, kepala tertunduk","High angle (kecil & lemah)","2 detik","Musik pelan, sedih"),
("Masalah","Bola terhenti di tepi parit","Bola berhenti mendadak","Long shot, over the edge","2 detik","Efek rem \"ciit\""),
("Datang","Kotak datang, bola memberi jalan","Flop berulang ke arah parit","Medium shot, tracking","2 detik","Musik mulai naik"),
("Keputusan","Kotak menjatuhkan diri ke parit","Rotasi melewati tepi (pivot)","Close-up, low angle (heroik)","1,5 detik","Hening lalu \"duk\""),
("Jadi Jembatan","Kotak pas mengisi parit, bola lewat","Bola translasi di atas kotak","High angle 3/4","2 detik","Efek gelinding + musik"),
("Penutup","Kotak & bola bersama saat senja","Diam, cahaya hangat","Long shot (static)","3 detik","Musik hangat (fade out)")]
W,PW,PH=1900,360,460; H=150+2*(PH+20)+70
im=Image.new("RGB",(W,H),(236,243,250)); d=ImageDraw.Draw(im)
d.rectangle([0,0,W,120],fill=(24,58,110))
d.text((30,18),"STORYBOARD ANIMASI",font=f("arialbd.ttf",42),fill="white")
d.text((30,72),"\"Si Kotak\" — Kubus yang Tidak Bisa Menggelinding (3D / Grafika Komputer)",font=f("arialbd.ttf",22),fill="white")
d.text((1150,22),"Pesan: Bentuk yang berbeda bukan kekurangan —",font=R,fill="white")
d.text((1150,42),"justru sisi datar kubus yang bisa menjadi jembatan.",font=R,fill="white")
d.text((1150,72),"Konsep CG: transformasi (translasi, rotasi pivot, scale/squash),",font=R,fill="white")
d.text((1150,92),"komposisi kamera, lighting & warna (hangat vs dingin).",font=R,fill="white")
for i,s in enumerate(S):
    x=20+(i%5)*(PW+14); y=140+(i//5)*(PH+20)
    d.rounded_rectangle([x,y,x+PW,y+PH],8,fill="white",outline=(150,180,210),width=2)
    d.rectangle([x,y,x+PW,y+36],fill=(30,70,130)); d.ellipse([x+6,y+3,x+36,y+33],fill=(245,130,40))
    d.text((x+21,y+18),str(i+1),font=B,fill="white",anchor="mm"); d.text((x+46,y+9),s[0],font=B,fill="white")
    fr=Image.open(f"frames/scene{i+1:02d}.png").convert("RGB").resize((PW-20,(PW-20)*9//16)); im.paste(fr,(x+10,y+44))
    ty=y+44+fr.height+10
    for k,v in zip(["Scene","Objek","Action","Movement","Kamera","Timing","Audio"],[str(i+1),"Kotak (kubus)"+(" + bola" if i not in(1,) else "")]+list(s[1:])):
        d.text((x+12,ty),k,font=B,fill=(40,40,40)); d.text((x+95,ty),": "+v,font=R,fill=(40,40,40)); ty+=31
y=140+2*(PH+20); segs=[("1–2 Perkenalan",(106,176,76)),("3–5 Gagal & ditinggal",(240,150,50)),("6–8 Konflik & keputusan",(80,140,210)),("9–10 Resolusi",(60,170,150))]
sw=(W-40)//4
for j,(t,c) in enumerate(segs):
    d.rounded_rectangle([20+j*sw+4,y,20+(j+1)*sw-4,y+45],6,fill=c); d.text((20+j*sw+sw//2,y+22),t,font=B,fill="white",anchor="mm")
im.save("Storyboard Kubus.png"); print(im.size)
