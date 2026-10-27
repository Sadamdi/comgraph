---
name: feedback-qa-before-render
description: "Preferensi user untuk animasi Blender — wajib QA fisika/tembus objek dan kualitas \"real world\" sebelum render; simpan memori di folder Agent"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 9b31a844-a023-4df1-b2d6-04f4531e4325
  modified: 2026-10-25T19:23:59.272Z
---

User ingin animasi benar-benar halus, sesuai fisika, tanpa tembus tembok/objek, topologi/deformasi karakter bagus, pencahayaan & objek rapi, dan sudah **dicek sebelum dirender**.
Gaya yang diminta: terasa dunia nyata tetapi karakter bergaya anime; bukan "mentahan 3D" / "AI slop".
User juga minta semua catatan disimpan di folder `Agent/` pada workspace Computer Graphic agar tidak hilang.

**Why:** ini tugas yang dinilai dosen dan lomba berhadiah; kesalahan seperti tembus meja atau lengan "sayap" langsung terlihat.
**How to apply:** jalankan QA otomatis (tembus statis, antar karakter, kontak lantai, IK) + tinjauan visual contact sheet tiap shot sebelum render; perbarui `Agent/UAS_Satu_Stiker_Satu_Warung.md` tiap ada temuan baru.
Terkait [[project-uas-satu-stiker-warung]].
