# 05 - Rig kustom: tulang tubuh + IK tangan/kaki + pole, bobot dari jarak ke segmen tulang (ternormalisasi radius)
import bpy, math
import numpy as np
from mathutils import Vector, Matrix, Euler, Quaternion

def seg_dist(P, a, b):
    ab = b - a; t = np.clip(((P - a) @ ab) / (ab @ ab + 1e-12), 0, 1)
    q = a + t[:, None] * ab
    return np.linalg.norm(P - q, axis=1)

def build_rig(kind, A, coll, name):
    f = kind == "lastri"
    S = A["S"]; Z = S["z"]; k = S["H"] / 1.55
    J = {key: Vector(v) for key, v in A["body"]["_J"].items()}
    hs = 1.22
    head_c = Vector((0, 0.002, 1.455 if f else 1.61))
    # --- armature object ---
    arm = bpy.data.armatures.new("ARM_" + name); arm.display_type = 'OCTAHEDRAL'
    obj = bpy.data.objects.new("RIG_" + name, arm); coll.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    for o in bpy.context.selected_objects: o.select_set(False)
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.edit_bones
    def bone(n, head, tail, parent=None, deform=True, roll=0.0, connect=False):
        b = eb.new(n); b.head = Vector(head); b.tail = Vector(tail); b.roll = roll
        if parent: b.parent = eb[parent]; b.use_connect = connect
        b.use_deform = deform
        return b
    P_ = lambda key: J[key]
    bone("root", (0, 0, 0), (0, 0.001 + 0.0, 0.15), None, False)
    bone("hips", J["pelvis"], J["waist"], "root")
    bone("spine", J["waist"], J["chest"], "hips", connect=True)
    bone("chest", J["chest"], J["sh_mid"], "spine", connect=True)
    bone("neck", J["neck0"], J["neck1"], "chest")
    bone("head", J["neck1"], head_c + Vector((0, 0, 0.12 * hs)), "neck", connect=True)
    ik_roll = 0.0
    for sd, side in ((1, "L"), (-1, "R")):
        bone(f"clavicle.{side}", J["sh_mid"], J[f"sho_{side}"], "chest")
        bone(f"upper_arm.{side}", J[f"sho_{side}"], J[f"elb_{side}"], f"clavicle.{side}", connect=True)
        bone(f"forearm.{side}", J[f"elb_{side}"], J[f"wri_{side}"], f"upper_arm.{side}", connect=True)
        bone(f"hand.{side}", J[f"wri_{side}"], J[f"middle0_{side}"], f"forearm.{side}", connect=True)
        # --- jari: 4 jari x 3 ruas + jempol x 3 ruas. Sumbu X lokal = sumbu tekuk; rotasi + = menekuk ke arah telapak ---
        palmdir = Vector((-sd, 0, 0))
        def fbone(n, a_key, b_key, parent, connect):
            h = J[a_key]; t = J[b_key]; d = (t - h).normalized()
            bn = bone(n, h, t, parent, connect=connect)
            A = d.cross(palmdir)
            if A.length > 1e-6:
                A.normalize(); bn.align_roll(A.cross(d))
            return bn
        for fn in ("index", "middle", "ring", "pinky"):
            fbone(f"{fn}1.{side}", f"{fn}0_{side}", f"{fn}1_{side}", f"hand.{side}", False)
            fbone(f"{fn}2.{side}", f"{fn}1_{side}", f"{fn}2_{side}", f"{fn}1.{side}", True)
            fbone(f"{fn}3.{side}", f"{fn}2_{side}", f"{fn}3_{side}", f"{fn}2.{side}", True)
        fbone(f"thumb1.{side}", f"thumb0_{side}", f"thumb1_{side}", f"hand.{side}", False)
        fbone(f"thumb2.{side}", f"thumb1_{side}", f"thumb2_{side}", f"thumb1.{side}", True)
        fbone(f"thumb3.{side}", f"thumb2_{side}", f"thumb3_{side}", f"thumb2.{side}", True)
        bone(f"thigh.{side}", J[f"hip_{side}"], J[f"knee_{side}"], "hips")
        bone(f"shin.{side}", J[f"knee_{side}"], J[f"ank_{side}"], f"thigh.{side}", connect=True)
        bone(f"foot.{side}", J[f"ank_{side}"], J[f"toe_{side}"], f"shin.{side}", connect=True)
        # kontrol IK (menunjuk +Y agar sumbu lokal = sumbu armature)
        w = J[f"wri_{side}"]
        dh = (J[f"middle0_{side}"] - w).normalized()
        bone(f"hand_ik.{side}", w, w + dh * 0.06, "root", False)      # orientasi sama dengan tulang tangan
        a = J[f"ank_{side}"]
        df = (J[f"toe_{side}"] - a).normalized()
        bone(f"foot_ik.{side}", a, a + df * 0.06, "root", False)       # orientasi sama dengan tulang kaki
        e = J[f"elb_{side}"]
        bone(f"elbow_pole.{side}", e + Vector((sd * 0.05, 0.38, 0)), e + Vector((sd * 0.05, 0.44, 0)), "root", False)
        kn = J[f"knee_{side}"]
        bone(f"knee_pole.{side}", kn + Vector((0, -0.55, 0)), kn + Vector((0, -0.49, 0)), "root", False)
    bpy.ops.object.mode_set(mode='OBJECT')
    for pbn in obj.pose.bones: pbn.rotation_mode = 'XYZ'
    # --- constraints IK + copy rotation ---
    bpy.ops.object.mode_set(mode='POSE')
    pb = obj.pose.bones
    for side in ("L", "R"):
        c = pb[f"forearm.{side}"].constraints.new('IK')
        c.target = obj; c.subtarget = f"hand_ik.{side}"; c.pole_target = obj; c.pole_subtarget = f"elbow_pole.{side}"
        c.chain_count = 2; c.use_stretch = False
        c2 = pb[f"hand.{side}"].constraints.new('COPY_ROTATION'); c2.target = obj; c2.subtarget = f"hand_ik.{side}"
        c3 = pb[f"shin.{side}"].constraints.new('IK')
        c3.target = obj; c3.subtarget = f"foot_ik.{side}"; c3.pole_target = obj; c3.pole_subtarget = f"knee_pole.{side}"
        c3.chain_count = 2; c3.use_stretch = False
        c4 = pb[f"foot.{side}"].constraints.new('COPY_ROTATION'); c4.target = obj; c4.subtarget = f"foot_ik.{side}"
    bpy.ops.object.mode_set(mode='OBJECT')
    # sudut pole otomatis: pilih sudut yang membuat siku/lutut paling dekat bone pole
    dg = bpy.context.evaluated_depsgraph_get
    def best_pole(side, limb):
        tgt = f"{'elbow' if limb == 'arm' else 'knee'}_pole.{side}"
        cb = pb["forearm." + side] if limb == "arm" else pb["shin." + side]
        joint = pb[("upper_arm." if limb == "arm" else "thigh.") + side]
        ik = [c for c in cb.constraints if c.type == 'IK'][0]
        pole_pos = obj.matrix_world @ pb[tgt].head
        best = (1e9, 0)
        for deg in range(-180, 181, 15):
            ik.pole_angle = math.radians(deg)
            bpy.context.view_layer.update()
            elbow_pos = obj.matrix_world @ cb.head
            d = (elbow_pos - pole_pos).length
            if d < best[0]: best = (d, deg)
        ik.pole_angle = math.radians(best[1])
        return best
    res = {}
    for side in ("L", "R"):
        res["arm." + side] = best_pole(side, "arm"); res["leg." + side] = best_pole(side, "leg")
    # --- bobot kulit ---
    bones = {}
    rad = {"hips": 0.15, "spine": 0.13, "chest": 0.145, "neck": 0.032, "head": 0.09, "clavicle": 0.05,
           "upper_arm": 0.040, "forearm": 0.032, "hand": 0.045, "thigh": 0.075, "shin": 0.052, "foot": 0.045}
    for _fn in ("index", "middle", "ring", "pinky"):
        for _i in (1, 2, 3): rad[f"{_fn}{_i}"] = 0.0105
    for _i in (1, 2, 3): rad[f"thumb{_i}"] = 0.0125
    for b in obj.data.bones:
        if b.use_deform:
            base = b.name.split(".")[0]
            bones[b.name] = (np.array(b.head_local), np.array(b.tail_local), rad[base])
    names = list(bones.keys())
    def weights_for(o, tau=0.38, topn=3, mode="normal"):
        me = o.data
        n = len(me.vertices)
        P = np.empty(n * 3, dtype=np.float32); me.vertices.foreach_get("co", P); P = P.reshape(-1, 3).astype(np.float64)
        P = np.array([(o.matrix_world @ Vector(p))[:] for p in P]) if o.parent is None and o.location.length > 1e-6 else P
        D = np.stack([seg_dist(P, bones[nm][0], bones[nm][1]) / bones[nm][2] for nm in names], axis=1)
        if mode == "skirt":
            W = np.zeros_like(D)
            zi = P[:, 2]
            ih = names.index("hips"); W[:, ih] = 1.0
            for side, sgn in (("L", 1), ("R", -1)):
                it = names.index("thigh." + side)
                t = np.clip((0.88 - zi) / 0.42, 0, 1) * 0.60 * (np.sign(P[:, 0]) == sgn)
                W[:, it] = t; W[:, ih] -= t
            return W
        if mode == "apron":
            keep = [i for i, nm in enumerate(names) if nm.split(".")[0] in ("hips", "spine", "chest", "neck")]
            D2 = np.full_like(D, 1e3); D2[:, keep] = D[:, keep]; D = D2
        dm = D.min(axis=1, keepdims=True)
        W = np.exp(-(D - dm) / tau)
        if topn:
            idx = np.argsort(-W, axis=1)[:, topn:]
            np.put_along_axis(W, idx, 0, axis=1)
        W /= W.sum(axis=1, keepdims=True)
        return W
    def smooth_weights(o, W, iters=12, alpha=0.55):
        me = o.data; n = len(me.vertices)
        e = np.empty(len(me.edges) * 2, dtype=np.int32); me.edges.foreach_get("vertices", e); e = e.reshape(-1, 2)
        deg = np.zeros(n); np.add.at(deg, e[:, 0], 1); np.add.at(deg, e[:, 1], 1)
        for _ in range(iters):
            S_ = np.zeros_like(W); np.add.at(S_, e[:, 0], W[e[:, 1]]); np.add.at(S_, e[:, 1], W[e[:, 0]])
            W = (1 - alpha) * W + alpha * S_ / np.maximum(deg, 1)[:, None]
        # simpan maksimal 4 pengaruh terkuat
        idx = np.argsort(-W, axis=1)[:, 4:]
        np.put_along_axis(W, idx, 0, axis=1)
        W /= np.maximum(W.sum(axis=1, keepdims=True), 1e-9)
        return W
    body_cache = {}
    def body_transfer(o):
        """Bobot pakaian = bobot verteks badan TERDEKAT (pakaian bergerak persis seperti kulit di bawahnya -> tidak ada kulit menembus di siku/bahu)."""
        bme = body_cache["o"].data; n = len(o.data.vertices)
        P = np.empty(n * 3, dtype=np.float32); o.data.vertices.foreach_get("co", P); P = P.reshape(-1, 3).astype(np.float64)
        Q = body_cache["P"]; W = np.zeros((n, body_cache["W"].shape[1]))
        for s in range(0, n, 256):
            d = ((P[s:s + 256, None, :] - Q[None, :, :]) ** 2).sum(-1)
            W[s:s + 256] = body_cache["W"][np.argmin(d, axis=1)]
        return W
    for o in A["deform"]:
        mode = "skirt" if o.name.endswith("_skirt") else ("apron" if "_apron" in o.name else "normal")
        if body_cache and any(k in o.name for k in ("_jacket", "_blouse", "_jeans")):
            W = body_transfer(o)
        else:
            W = weights_for(o, mode=mode)
        if any(k in o.name for k in ("_jacket", "_blouse", "_jeans")):
            for side in ("L", "R"):
                srcs = [("hand." + side, "forearm." + side), ("foot." + side, "shin." + side)]
                for fn_ in ("index", "middle", "ring", "pinky", "thumb"):
                    for i_ in (1, 2, 3): srcs.append((f"{fn_}{i_}." + side, "forearm." + side))
                for src, dst in srcs:
                    if src in names and dst in names:
                        W[:, names.index(dst)] += W[:, names.index(src)]; W[:, names.index(src)] = 0
        is_cloth = body_cache and any(k in o.name for k in ("_jacket", "_blouse", "_jeans"))
        if mode == "normal" and not is_cloth:
            W0 = W.copy(); W = smooth_weights(o, W)
            fidx = [names.index(n_) for n_ in names if n_.split(".")[0][:-1] in ("index", "middle", "ring", "pinky", "thumb")]
            if o.name.endswith("_BODY") and fidx:
                fm = (W0[:, fidx].sum(axis=1) > 0.25)[:, None]               # verteks jari: pertahankan bobot tajam (75% asli)
                W = np.where(fm, 0.75 * W0 + 0.25 * W, W)
        if not body_cache and mode == "normal":          # badan: simpan bobot akhir & posisi verteks untuk disalin ke pakaian
            n_ = len(o.data.vertices); P_ = np.empty(n_ * 3, dtype=np.float32); o.data.vertices.foreach_get("co", P_)
            body_cache.update(o=o, P=P_.reshape(-1, 3).astype(np.float64), W=W.copy())
        for nm in names:
            o.vertex_groups.new(name=nm)
        for i in range(W.shape[0]):
            for j, nm in enumerate(names):
                w = float(W[i, j])
                if w > 0.004: o.vertex_groups[nm].add([i], w, 'REPLACE')
        if o.name.endswith("_BODY"):                 # outline lebih tipis pada jari (hindari duri outline di ujung jari)
            vgT = o.vertex_groups.new(name="OUTLINE_T")
            fcols = [j for j, n_ in enumerate(names) if n_.split(".")[0][:-1] in ("index", "middle", "ring", "pinky", "thumb")]
            for i in range(W.shape[0]):
                fw = float(W[i, fcols].sum()) if fcols else 0.0
                vgT.add([i], max(0.0, 1.0 - 0.75 * min(1.0, fw * 1.4)), 'REPLACE')
            for m_ in o.modifiers:
                if m_.type == 'SOLIDIFY':
                    m_.vertex_group = "OUTLINE_T"; m_.thickness_vertex_group = 0.25
        for c in list(o.constraints): pass
        mod = o.modifiers.new("Armature", 'ARMATURE'); mod.object = obj
        # Armature harus berada sebelum Solidify/outline agar tebal ikut terdeformasi
        mods = o.modifiers
        mods.move(len(mods) - 1, 0)
        o.parent = obj
    # --- rigid -> tulang ---
    def parent_bone(o, bname):
        bpy.context.view_layer.update()
        mw = o.matrix_world.copy()
        o.parent = obj; o.parent_type = 'BONE'; o.parent_bone = bname
        bpy.context.view_layer.update()
        pbn = obj.pose.bones[bname]
        for tail in (True, False):
            M = obj.matrix_world @ pbn.matrix
            if tail: M = M @ Matrix.Translation((0, pbn.bone.length, 0))
            o.matrix_parent_inverse = M.inverted()
            bpy.context.view_layer.update()
            if (o.matrix_world.translation - mw.translation).length < 1e-4: return
    for o, bname in A["rigid"].items():
        parent_bone(o, bname)
    return obj, res

print("rig lib ok")
