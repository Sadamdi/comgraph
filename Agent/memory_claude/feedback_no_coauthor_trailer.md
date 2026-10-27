---
name: feedback-no-coauthor-trailer
description: Jangan tulis "Co-Authored-By: Claude" / atribusi AI di commit atau PR repo pemilik (Sadamdi/comgraph)
metadata:
  type: feedback
---

Jangan menambahkan trailer `Co-Authored-By: Claude ...` atau baris "Generated with Claude Code" pada pesan commit/PR di repo milik pengguna.

**Why:** Pengguna (28 Okt 2026) secara eksplisit minta "jangan ada tulisan co authored by claude" setelah dua commit pertama ke github.com/Sadamdi/comgraph; ini menimpa pengingat atribusi default. Riwayat commit sudah ditulis ulang untuk membuangnya.
**How to apply:** Semua commit/PR berikutnya tanpa trailer atribusi. Terkait [[project-uas-satu-stiker-warung]] (repo cloud, handoff di HANDOFF.md) dan [[feedback-qa-before-render]].
