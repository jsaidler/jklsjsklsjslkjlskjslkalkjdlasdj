#!/usr/bin/env python3
"""Inspect a synthesized COCO WholeBody 133 behavioral driver.

No model inference. Reports continuity and geometry diagnostics without inventing a
pass/fail threshold. The visual preview remains authoritative for the first gate.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

CONF = 0.20
GROUPS = {
    "body_head": list(range(0, 13)),
    "face": list(range(23, 91)),
    "left_hand": list(range(91, 112)),
    "right_hand": list(range(112, 133)),
}
LIMBS = {
    "left_upper_arm": (5, 7),
    "left_forearm": (7, 9),
    "right_upper_arm": (6, 8),
    "right_forearm": (8, 10),
}


def finite(v):
    return v is not None and math.isfinite(float(v))


def percentile(values, q):
    vals = sorted(float(v) for v in values if finite(v))
    if not vals:
        return None
    if len(vals) == 1:
        return vals[0]
    p = max(0.0, min(1.0, q)) * (len(vals) - 1)
    lo, hi = int(math.floor(p)), int(math.ceil(p))
    if lo == hi:
        return vals[lo]
    return vals[lo] * (hi - p) + vals[hi] * (p - lo)


def quantiles(values):
    return {"q10": percentile(values, .10), "median": percentile(values, .50), "q90": percentile(values, .90), "max": max(values) if values else None}


def load_track(path: Path):
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("schema") != "coco_wholebody_133" or len(row.get("keypoints") or []) != 133:
            raise SystemExit(f"Invalid pose row at line {line_no}")
        rows.append(row)
    if len(rows) < 2:
        raise SystemExit("Driver track needs at least two frames")
    return rows


def shoulder_width(kp):
    a, b = kp[5], kp[6]
    vals = (a[0], a[1], a[2], b[0], b[1], b[2])
    if not all(finite(v) for v in vals) or float(a[2]) < CONF or float(b[2]) < CONF:
        return None
    return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))


def group_jump(a, b, ids):
    wa, wb = shoulder_width(a), shoulder_width(b)
    scale_vals = [x for x in (wa, wb) if x is not None and x > 1e-8]
    if not scale_vals:
        return None
    scale = statistics.fmean(scale_vals)
    dsq = []
    for i in ids:
        pa, pb = a[i], b[i]
        if not all(finite(v) for v in (pa[0], pa[1], pa[2], pb[0], pb[1], pb[2])):
            continue
        if float(pa[2]) < CONF or float(pb[2]) < CONF:
            continue
        dx, dy = float(pb[0]) - float(pa[0]), float(pb[1]) - float(pa[1])
        dsq.append(dx*dx + dy*dy)
    if len(dsq) < 2:
        return None
    return math.sqrt(statistics.fmean(dsq)) / scale


def pair_distance(kp, a, b):
    pa, pb = kp[a], kp[b]
    if not all(finite(v) for v in (pa[0], pa[1], pa[2], pb[0], pb[1], pb[2])):
        return None
    if float(pa[2]) < CONF or float(pb[2]) < CONF:
        return None
    return math.hypot(float(pa[0]) - float(pb[0]), float(pa[1]) - float(pb[1]))


def intereye_scale(kp):
    def mean_xy(ids):
        pts=[]
        for i in ids:
            p=kp[i]
            if all(finite(v) for v in p[:3]) and float(p[2]) >= CONF:
                pts.append((float(p[0]),float(p[1])))
        if len(pts) < 2:
            return None
        return statistics.fmean(x for x,_ in pts), statistics.fmean(y for _,y in pts)
    ea=mean_xy(range(59,65))  # face-relative 36..41 => wholebody 59..64
    eb=mean_xy(range(65,71))  # face-relative 42..47 => wholebody 65..70
    if ea is None or eb is None:
        return None
    return math.hypot(eb[0]-ea[0], eb[1]-ea[1])


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--track",type=Path,required=True)
    ap.add_argument("--plan",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    if not args.track.is_file(): raise SystemExit(f"Missing track: {args.track}")
    if not args.plan.is_file(): raise SystemExit(f"Missing plan: {args.plan}")
    frames=load_track(args.track)
    plan=json.loads(args.plan.read_text(encoding="utf-8-sig"))
    fps=float(plan.get("fps") or 0.0)
    if fps <= 0: raise SystemExit("Plan has invalid fps")

    times=[float(r["t"]) for r in frames]
    boundary_times=[float(w["target_start_s"]) for w in (plan.get("windows") or [])[1:]]
    boundary_pairs=set()
    for bt in boundary_times:
        idx=min(range(1,len(times)), key=lambda i: abs(times[i]-bt))
        boundary_pairs.add(idx)  # pair idx-1 -> idx

    jumps={name:[] for name in GROUPS}
    boundary_jumps={name:[] for name in GROUPS}
    normal_jumps={name:[] for name in GROUPS}
    for i in range(1,len(frames)):
        a,b=frames[i-1]["keypoints"],frames[i]["keypoints"]
        for name,ids in GROUPS.items():
            v=group_jump(a,b,ids)
            if v is None: continue
            jumps[name].append(v)
            if i in boundary_pairs: boundary_jumps[name].append(v)
            else: normal_jumps[name].append(v)

    oob=0; finite_xy=0
    shoulder=[]
    limb={name:[] for name in LIMBS}
    eye_to_shoulder=[]
    wrist_root_left=[]; wrist_root_right=[]
    for rec in frames:
        kp=rec["keypoints"]
        for x,y,c in kp:
            if finite(x) and finite(y):
                finite_xy += 1
                if float(x) < 0.0 or float(x) > 1.0 or float(y) < 0.0 or float(y) > 1.0:
                    oob += 1
        sw=shoulder_width(kp)
        if sw is not None and sw > 1e-8:
            shoulder.append(sw)
            for name,(a,b) in LIMBS.items():
                d=pair_distance(kp,a,b)
                if d is not None: limb[name].append(d/sw)
            ies=intereye_scale(kp)
            if ies is not None: eye_to_shoulder.append(ies/sw)
            dl=pair_distance(kp,9,91)
            dr=pair_distance(kp,10,112)
            if dl is not None: wrist_root_left.append(dl/sw)
            if dr is not None: wrist_root_right.append(dr/sw)

    continuity={}
    for name in GROUPS:
        nq=quantiles(normal_jumps[name])
        bvals=boundary_jumps[name]
        ratios=[]
        q90=nq.get("q90")
        if q90 is not None and q90 > 1e-12:
            ratios=[v/q90 for v in bvals]
        continuity[name]={
            "all_step_jump_norm_by_shoulder": quantiles(jumps[name]),
            "nonboundary_step_jump_norm_by_shoulder": nq,
            "boundary_jumps_norm_by_shoulder": bvals,
            "boundary_to_nonboundary_q90_ratio": ratios,
        }

    result={
        "schema":"behavioral-pose-driver-qa/v1",
        "track":str(args.track.resolve()),
        "plan":str(args.plan.resolve()),
        "frames":len(frames),
        "fps":fps,
        "duration_s":float(plan.get("duration_s") or 0.0),
        "boundary_times_s":boundary_times,
        "base_source_order":plan.get("base_source_order"),
        "planner_boundary_continuity":plan.get("base_boundary_continuity"),
        "coordinate_out_of_bounds": {"count":oob,"finite_xy":finite_xy,"ratio":(oob/finite_xy if finite_xy else 0.0)},
        "continuity":continuity,
        "geometry": {
            "shoulder_width_image_norm":quantiles(shoulder),
            "limb_length_over_shoulder":{name:quantiles(vals) for name,vals in limb.items()},
            "intereye_over_shoulder":quantiles(eye_to_shoulder),
            "left_hand_root_to_body_wrist_over_shoulder":quantiles(wrist_root_left),
            "right_hand_root_to_body_wrist_over_shoulder":quantiles(wrist_root_right),
        },
        "note":"No automatic pass/fail threshold is applied. Compare boundary jumps with the driver's own non-boundary distribution and inspect the preview visually."
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")

    print("BEHAVIORAL POSE DRIVER NUMERIC QA")
    print("=================================")
    print(f"Frames: {len(frames)} / fps={fps} / duration={result['duration_s']} s")
    print(f"Base source order: {result['base_source_order']}")
    print(f"Planner boundary continuity: {result['planner_boundary_continuity']}")
    print(f"Coordinate out-of-bounds: {oob}/{finite_xy} ({result['coordinate_out_of_bounds']['ratio']:.6f})")
    for name in GROUPS:
        c=continuity[name]; nq=c['nonboundary_step_jump_norm_by_shoulder']; bj=c['boundary_jumps_norm_by_shoulder']; br=c['boundary_to_nonboundary_q90_ratio']
        print(f"{name}: nonboundary jump q10/median/q90/max={nq['q10']}/{nq['median']}/{nq['q90']}/{nq['max']} boundary={bj} boundary/q90={br}")
    print("Limb length / shoulder quantiles:")
    for name,q in result['geometry']['limb_length_over_shoulder'].items():
        print(f"  {name}: {q['q10']}/{q['median']}/{q['q90']}/{q['max']}")
    print(f"Intereye/shoulder q10/median/q90/max: {result['geometry']['intereye_over_shoulder']}")
    print(f"Left hand-root/wrist: {result['geometry']['left_hand_root_to_body_wrist_over_shoulder']}")
    print(f"Right hand-root/wrist: {result['geometry']['right_hand_root_to_body_wrist_over_shoulder']}")
    print(f"JSON: {args.output}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
