"""Ganti root path Windows pada skrip proyek ke root baru (mis. di Linux/cloud).

Pakai:  python remap_paths.py "<ROOT_BARU>"          # contoh: python remap_paths.py /workspace/comgraph
Hanya menyentuh .py/.ps1/.sh/.md di UAS UTS/Produksi dan Agent. Aman dijalankan ulang. Tanpa argumen = bantuan.

Yang dilakukan:
 1. String berisi 'D:\\adam kuliah\\Semester 5\\Computer Graphic' -> ROOT_BARU, backslash di dalam literal itu jadi '/'
 2. '+ "\\\\"' (penyambung path gaya Windows) -> '+ "/"'
Best-effort: setelah menjalankan, uji dengan smoke test di HANDOFF.md bagian 4.
"""
import os, re, sys

OLD_ROOT = r"D:\adam kuliah\Semester 5\Computer Graphic"
EXT = (".py", ".ps1", ".sh")

def convert_literal(m):
    s = m.group(0)
    s = s.replace(OLD_ROOT.replace("\\", "\\\\"), "@@ROOT@@").replace(OLD_ROOT, "@@ROOT@@")
    s = s.replace("\\\\", "/").replace("\\", "/")
    return s

def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    new_root = sys.argv[1].rstrip("/")
    here = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.abspath(os.path.join(here, "..", ".."))
    pat = re.compile(r"""[rR]?(["'])[^"'\n]*Computer Graphic[^"'\n]*\1""")
    changed = 0
    for base in ("UAS UTS/Produksi", "Agent"):
        for dp, dn, fn in os.walk(os.path.join(repo, base)):
            dn[:] = [d for d in dn if d not in ("frames_ghibli", "__pycache__", "blender-lab", "blender_extension_mcp")]
            for f in fn:
                if not f.endswith(EXT): continue
                p = os.path.join(dp, f)
                try: t = open(p, encoding="utf8").read()
                except Exception: continue
                t2 = pat.sub(lambda m: convert_literal(m).replace("@@ROOT@@", new_root), t)
                t2 = t2.replace('+ "\\\\"', '+ "/"')
                if t2 != t:
                    open(p, "w", encoding="utf8", newline="\n").write(t2); changed += 1
    print("file diubah:", changed)

main()
