#!/usr/bin/env python3
"""Behavioral pose-driver compositor v3.

v3 keeps the validated multi-source architecture and fixes the two remaining v2
failure modes:
- hand framing is a retrieval constraint coupled to base-pose selection;
- face donors prefer forward/adjacent source units and velocity-compatible seams.

After composition, one constant similarity transform normalizes camera framing for
the whole 4.5 s driver. This preserves relative body/hand/face motion and removes
source-camera placement from the behavioral signal. It never invokes DWPose or Wan.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

import synthesize_behavioral_pose_driver_v2 as v2

CONF = v2.CONF
RELEVANT_FRAME_IDS = list(range(0, 13)) + list(range(23, 133))


def exp_score(x: float, tau: float) -> float:
    return math.exp(-max(0.0, x) / max(tau, 1e-9))


def source_gap(u0, u1):
    """Forward source-time gap. None means reverse/overlapping order."""
    e0 = float(u0["source_end_s"])
    s1 = float(u1["source_start_s"])
    if s1 < e0 - 0.05:
        return None
    return max(0.0, s1 - e0)


def normalized_face_coords(kp):
    n = v2.normalize_face(kp)
    if n is None:
        return {}
    return n[1]


def face_velocity_distance(u0, u1, alpha0, track_for):
    step = 0.06
    a0 = v2.unit_pose(u0, alpha0, track_for)
    a1 = v2.unit_pose(u0, min(1.0, alpha0 + step), track_for)
    b0 = v2.unit_pose(u1, 0.0, track_for)
    b1 = v2.unit_pose(u1, min(1.0, step), track_for)
    ca0, ca1 = normalized_face_coords(a0), normalized_face_coords(a1)
    cb0, cb1 = normalized_face_coords(b0), normalized_face_coords(b1)
    ids = set(ca0) & set(ca1) & set(cb0) & set(cb1) & set(range(17, 68))
    if len(ids) < 12:
        return 1.0
    ds = []
    for i in ids:
        vax = (ca1[i][0] - ca0[i][0]) / step
        vay = (ca1[i][1] - ca0[i][1]) / step
        vbx = (cb1[i][0] - cb0[i][0]) / step
        vby = (cb1[i][1] - cb0[i][1]) / step
        ds.append((vax - vbx) ** 2 + (vay - vby) ** 2)
    return math.sqrt(statistics.fmean(ds))


def select_face_pair_v3(units, targets, seg_d, blend, track_for):
    alpha0 = (seg_d - blend) / seg_d
    c0 = v2.enabled_candidates(units, "face", "secondary", targets[0], seg_d)[:60]
    c1 = v2.enabled_candidates(units, "face", "secondary", targets[1], seg_d)[:60]
    best = None
    for s0, u0 in c0:
        pose0 = v2.unit_pose(u0, alpha0, track_for)
        for s1, u1 in c1:
            if u0["library_unit_id"] == u1["library_unit_id"]:
                continue
            gap = source_gap(u0, u1)
            if gap is None or gap > 8.0:
                continue
            pose1 = v2.unit_pose(u1, 0.0, track_for)
            shape_d = v2.face_shape_distance(pose0, pose1)
            shape_cont = 1.0 / (1.0 + 4.0 * shape_d)
            vel_d = face_velocity_distance(u0, u1, alpha0, track_for)
            vel_cont = 1.0 / (1.0 + 3.0 * vel_d)
            adjacency = exp_score(gap, 1.5)
            retrieval = (s0 + s1) / 2.0
            score = .32 * retrieval + .27 * shape_cont + .23 * adjacency + .18 * vel_cont
            rec = (score, shape_cont, vel_cont, adjacency, gap, (s0, u0), (s1, u1))
            if best is None or rec[0] > best[0]:
                best = rec
    if best is None:
        # Conservative fallback to v2 pair selection rather than silently failing.
        old = v2.select_face_pair(units, targets, seg_d, blend, track_for)
        score, cont, r0, r1 = old
        return (score, cont, None, None, None, r0, r1)
    return best


def base_pair_options(units, targets, seg_d, blend, track_for, limit=32):
    overlap_start = seg_d - blend
    alpha_a = overlap_start / seg_d
    options = []
    for order in (("primary", "tertiary"), ("tertiary", "primary")):
        lists = []
        for i, src in enumerate(order):
            c = v2.enabled_candidates(units, "posture", src, targets[i], seg_d)
            lists.append(v2.top_scored(c, 22, lambda u: v2.base_framing(u, track_for)))
        for s0, u0, raw0, fr0 in lists[0]:
            p0 = v2.unit_pose(u0, alpha_a, track_for)
            for s1, u1, raw1, fr1 in lists[1]:
                p1 = v2.unit_pose(u1, 0.0, track_for)
                dist = v2.normalized_boundary_distance(p0, p1)
                cont = 1.0 / (1.0 + 5.0 * dist)
                score = .52 * ((s0 + s1) / 2.0) + .48 * cont
                options.append((score, cont, order, (s0, u0, raw0, fr0), (s1, u1, raw1, fr1)))
    options.sort(key=lambda x: x[0], reverse=True)
    return options[:limit]


def select_hand_pair_for_base(units, targets, seg_d, blend, b0, b1, base_align, track_for, min_frame):
    alpha_a = (seg_d - blend) / seg_d
    c0 = v2.enabled_candidates(units, "both_hands", "primary", targets[0], seg_d)
    c1 = v2.enabled_candidates(units, "both_hands", "primary", targets[1], seg_d)
    scored0 = []
    scored1 = []
    for s, u in c0:
        f = v2.retargeted_hand_framing(b0, u, None, track_for)
        if f >= min_frame:
            scored0.append((.42 * s + .58 * f, s, u, f))
    for s, u in c1:
        f = v2.retargeted_hand_framing(b1, u, base_align, track_for)
        if f >= min_frame:
            scored1.append((.42 * s + .58 * f, s, u, f))
    scored0.sort(key=lambda x: x[0], reverse=True)
    scored1.sort(key=lambda x: x[0], reverse=True)
    scored0 = scored0[:48]
    scored1 = scored1[:48]
    if not scored0 or not scored1:
        return None

    best = None
    for _, s0, u0, f0 in scored0:
        a = v2.unit_pose(u0, alpha_a, track_for)
        for _, s1, u1, f1 in scored1:
            if u0["library_unit_id"] == u1["library_unit_id"]:
                continue
            b = v2.unit_pose(u1, 0.0, track_for)
            shape_d = v2.hand_shape_distance(a, b)
            shape_cont = 1.0 / (1.0 + 2.5 * shape_d)
            gap = source_gap(u0, u1)
            adjacency = exp_score(gap, 2.0) if gap is not None else 0.10
            framing = (f0 + f1) / 2.0
            retrieval = (s0 + s1) / 2.0
            score = .27 * retrieval + .33 * framing + .22 * shape_cont + .18 * adjacency
            rec = (score, shape_cont, framing, adjacency, gap, (s0, u0, f0), (s1, u1, f1))
            if best is None or rec[0] > best[0]:
                best = rec
    return best


def select_coupled_base_and_hands(units, targets, seg_d, blend, track_for):
    options = base_pair_options(units, targets, seg_d, blend, track_for)
    # Hard hand-framing constraint first. Only relax if the current library cannot
    # provide a valid multi-source body pair at the stricter level.
    for threshold in (0.90, 0.86, 0.82, 0.78, 0.74):
        joint = []
        for bp in options:
            bscore, bcont, order, b0rec, b1rec = bp
            b0, b1 = b0rec[1], b1rec[1]
            p0 = v2.unit_pose(b0, (seg_d - blend) / seg_d, track_for)
            p1 = v2.unit_pose(b1, 0.0, track_for)
            align = v2.similarity(p1, p0)
            hp = select_hand_pair_for_base(units, targets, seg_d, blend, b0, b1, align, track_for, threshold)
            if hp is None:
                continue
            hscore = hp[0]
            combined = .68 * bscore + .32 * hscore
            joint.append((combined, threshold, bp, hp, align))
        if joint:
            joint.sort(key=lambda x: x[0], reverse=True)
            return joint[0]
    raise SystemExit("No base+hand pair meets even the relaxed v3 in-frame constraint")


def robust_quantile(values, q):
    vals = sorted(values)
    if not vals:
        return None
    p = v2.clamp(q, 0.0, 1.0) * (len(vals) - 1)
    lo = int(math.floor(p)); hi = int(math.ceil(p))
    if lo == hi:
        return vals[lo]
    return vals[lo] * (hi - p) + vals[hi] * (p - lo)


def canonical_frame_transform(frames, qlo=.005, qhi=.995, margin=.035, min_scale=.82):
    xs, ys = [], []
    for rec in frames:
        kp = rec["keypoints"]
        for i in RELEVANT_FRAME_IDS:
            x, y, c = kp[i]
            if not (v2.finite(x) and v2.finite(y) and v2.finite(c) and float(c) >= CONF):
                continue
            xs.append(float(x)); ys.append(float(y))
    if not xs or not ys:
        return {"scale": 1.0, "dx": 0.0, "dy": 0.0, "required_scale": 1.0,
                "source_bbox": None, "quantiles": [qlo, qhi]}
    x0, x1 = robust_quantile(xs, qlo), robust_quantile(xs, qhi)
    y0, y1 = robust_quantile(ys, qlo), robust_quantile(ys, qhi)
    sx = (1.0 - 2 * margin) / max(x1 - x0, 1e-8)
    sy = (1.0 - 2 * margin) / max(y1 - y0, 1e-8)
    required = min(1.0, sx, sy)
    scale = max(min_scale, required)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    dx, dy = 0.5 - scale * cx, 0.5 - scale * cy
    return {"scale": scale, "dx": dx, "dy": dy, "required_scale": required,
            "source_bbox": [x0, y0, x1, y1], "quantiles": [qlo, qhi],
            "margin": margin, "min_scale": min_scale}


def apply_global_frame_transform(frames, tr):
    sc, dx, dy = float(tr["scale"]), float(tr["dx"]), float(tr["dy"])
    for rec in frames:
        for p in rec["keypoints"]:
            if v2.finite(p[0]) and v2.finite(p[1]):
                p[0] = sc * float(p[0]) + dx
                p[1] = sc * float(p[1]) + dy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--library", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--audio", type=Path)
    ap.add_argument("--duration", type=float, default=4.5)
    ap.add_argument("--fps", type=float, default=24.0)
    ap.add_argument("--blend-duration", type=float, default=.75)
    ap.add_argument("--ffmpeg", default="ffmpeg")
    args = ap.parse_args()
    if not (4.0 <= args.duration <= 5.0):
        raise SystemExit("--duration must be 4..5 s")
    if not (.5 <= args.blend_duration <= 1.0):
        raise SystemExit("--blend-duration must be 0.5..1.0 s")

    lib = v2.load_json(args.library)
    if lib.get("schema") != "joao-motion-library/v1":
        raise SystemExit("Unexpected library schema")
    if args.audio is not None and not args.audio.is_file():
        raise SystemExit(f"Audio missing: {args.audio}")

    units = lib.get("units") or []
    targets = v2.audio_targets(args.audio, args.duration, 2, args.ffmpeg)
    seg_d = (args.duration + args.blend_duration) / 2.0
    overlap_start = seg_d - args.blend_duration
    overlap_end = seg_d

    cache = {}
    def track_for(u):
        p = Path(u["pose_track"])
        if p not in cache:
            cache[p] = v2.load_pose(p)
        return cache[p]

    joint = select_coupled_base_and_hands(units, targets, seg_d, args.blend_duration, track_for)
    joint_score, hand_floor, bp, hp, base_align = joint
    _, base_cont, order, b0rec, b1rec = bp
    b0, b1 = b0rec[1], b1rec[1]
    _, hand_cont, hand_framing, hand_adj, hand_gap, h0rec, h1rec = hp
    h0, h1 = h0rec[1], h1rec[1]

    fp = select_face_pair_v3(units, targets, seg_d, args.blend_duration, track_for)
    _, face_cont, face_vel_cont, face_adj, face_gap, f0rec, f1rec = fp
    f0, f1 = f0rec[1], f1rec[1]

    def compose(bu, hu, fu, progress, align=None):
        base = v2.unit_pose(bu, progress, track_for)
        if align is not None:
            base = v2.apply_similarity(base, align)
        donor = v2.unit_pose(hu, progress, track_for)
        v2.hand_retarget(donor, base, True)
        v2.hand_retarget(donor, base, False)
        face = v2.unit_pose(fu, progress, track_for)
        face_ref = v2.unit_pose(fu, 0.0, track_for)
        v2.transfer_face_and_head(face, face_ref, base)
        return base

    frames = []
    count = int(round(args.duration * args.fps))
    for fi in range(count):
        t = fi / args.fps
        p0 = v2.clamp(t / seg_d, 0.0, 1.0)
        p1 = v2.clamp((t - overlap_start) / seg_d, 0.0, 1.0)
        if t < overlap_start:
            pose = compose(b0, h0, f0, p0, None); base_unit = b0
        elif t > overlap_end:
            pose = compose(b1, h1, f1, p1, base_align); base_unit = b1
        else:
            a = compose(b0, h0, f0, p0, None)
            b = compose(b1, h1, f1, p1, base_align)
            beta = v2.smooth5((t - overlap_start) / args.blend_duration)
            pose = v2.blend_pose(a, b, beta)
            base_unit = b0 if beta < .5 else b1
        frames.append({
            "t": round(t, 6), "schema": "coco_wholebody_133", "keypoints": pose,
            "provenance": {
                "base_unit": base_unit["library_unit_id"],
                "base_pair": [b0["library_unit_id"], b1["library_unit_id"]],
                "hand_pair": [h0["library_unit_id"], h1["library_unit_id"]],
                "face_pair": [f0["library_unit_id"], f1["library_unit_id"]],
                "transition_overlap": overlap_start <= t <= overlap_end,
            }
        })

    frame_tr = canonical_frame_transform(frames)
    apply_global_frame_transform(frames, frame_tr)

    plan = {
        "schema": "behavioral-pose-driver-plan/v3",
        "duration_s": args.duration, "fps": args.fps,
        "transition_blend_s": args.blend_duration, "segment_duration_s": seg_d,
        "overlap_start_s": overlap_start, "overlap_end_s": overlap_end,
        "target_audio": str(args.audio.resolve()) if args.audio else None,
        "target_windows": targets, "base_source_order": list(order),
        "base_boundary_continuity": round(base_cont, 6),
        "face_pair_continuity": round(face_cont, 6),
        "face_velocity_continuity": None if face_vel_cont is None else round(face_vel_cont, 6),
        "face_source_gap_s": face_gap,
        "hand_pair_continuity": round(hand_cont, 6),
        "hand_source_gap_s": hand_gap,
        "predicted_hand_inframe_ratio": round(hand_framing, 6),
        "hand_framing_floor": hand_floor,
        "joint_base_hand_score": round(joint_score, 6),
        "canonical_frame_transform": frame_tr,
        "windows": []
    }
    for i, (bu, hu, fu, brec, hrec, frec) in enumerate(((b0,h0,f0,b0rec,h0rec,f0rec),(b1,h1,f1,b1rec,h1rec,f1rec))):
        plan["windows"].append({
            "index": i, "target": targets[i],
            "base": {"unit": bu["library_unit_id"], "retrieval_score": round(brec[2],6), "base_framing": round(brec[3],6)},
            "hands": {"unit": hu["library_unit_id"], "retrieval_score": round(hrec[0],6), "predicted_inframe": round(hrec[2],6)},
            "face": {"unit": fu["library_unit_id"], "retrieval_score": round(frec[0],6)},
        })

    args.output_dir.mkdir(parents=True, exist_ok=True)
    plan_path = args.output_dir / "driver_plan.json"
    track_path = args.output_dir / "behavioral_driver_coco133.jsonl"
    preview = args.output_dir / "behavioral_driver_pose_preview.mp4"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    with track_path.open("w", encoding="utf-8", newline="\n") as fh:
        for rec in frames:
            fh.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")
    v2.draw_preview(frames, preview, args.fps)

    print("MULTI-SOURCE BEHAVIORAL POSE DRIVER v3")
    print("======================================")
    print(f"Duration: {args.duration}s / fps={args.fps} / frames={len(frames)}")
    print(f"Base source order: {order[0]} -> {order[1]}")
    print(f"Overlap: {overlap_start:.3f}-{overlap_end:.3f}s / blend={args.blend_duration:.3f}s")
    print(f"Base continuity: {base_cont:.6f}")
    print(f"Hand framing floor used: {hand_floor:.2f}")
    print(f"Predicted retargeted-hand in-frame ratio: {hand_framing:.6f}")
    print(f"Hand continuity: {hand_cont:.6f} / source gap={hand_gap}")
    print(f"Face shape continuity: {face_cont:.6f} / velocity continuity={face_vel_cont} / source gap={face_gap}")
    print(f"Canonical framing: required_scale={frame_tr['required_scale']:.6f} applied_scale={frame_tr['scale']:.6f} dx={frame_tr['dx']:.6f} dy={frame_tr['dy']:.6f}")
    for w in plan["windows"]:
        print(f"Window {w['index']}: base={w['base']['unit']} hands={w['hands']['unit']} face={w['face']['unit']}")
        print(f"  framing base={w['base']['base_framing']} hands={w['hands']['predicted_inframe']}")
    print(f"Plan: {plan_path}")
    print(f"Pose track: {track_path}")
    print(f"Preview: {preview}")
    print("Wan-Animate-2: NOT INVOKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
