# QA tembus/overlap/kaki (15_qa.check_frames) di Blender latar -> render/qa_pen.json
import bpy, json
SD = r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\scripts" + "\\"
exec(open(SD + "15_qa.py", encoding="utf8").read())
rep = check_frames(list(range(1, 2701, 8)))
json.dump({"pen": [(f, n, {k: list(v) for k, v in h.items()}) for f, n, h in rep["penetrasi"]], "overlap": rep["antar_karakter"], "kaki_min": min(k[2] for k in rep["kaki"]), "kaki_n": len(rep["kaki"])}, open(r"D:\adam kuliah\Semester 5\Computer Graphic\UAS UTS\Produksi\render\qa_pen.json", "w"))
print("QA_PEN_DONE", len(rep["penetrasi"]))
