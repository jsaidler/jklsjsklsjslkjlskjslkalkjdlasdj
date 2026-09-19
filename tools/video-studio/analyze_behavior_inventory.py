#!/usr/bin/env python3
"""Analyze behavior-profile motion-unit quality without rendering or model inference.

Reads a complete behavior-profile manifest plus its normalized COCO WholeBody 133
pose track. Produces source-relative confidence/coverage diagnostics and a shortlist
of representative + suspicious units for human review.
"""
from __future__ import annotations

import argparse, csv, json, math, statistics, sys
from pathlib import Path

CONF = 0.20
GROUPS = {
    "head": list(range(0, 5)),
    "body": list(range(5, 13)),
    "left_hand": list(range(91, 112)),
    "right_hand": list(range(112, 133)),
}

class InventoryError(RuntimeError):
    pass

def percentile(values, q):
    vals = sorted(float(v) for v in values)
    if not vals:
        return None
    if len(vals) == 1:
        return vals[0]
    p = max(0.0, min(1.0, q)) * (len(vals) - 1)
    lo, hi = int(math.floor(p)), int(math.ceil(p))
    if lo == hi:
        return vals[lo]
    return vals[lo] * (hi - p) + vals[hi] * (p - lo)

def load_pose(path: Path):
    out = []
    with path.open("r", encoding="utf-8-sig") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            rec = json.loads(line)
            kp = rec.get("keypoints")
            if rec.get("schema") != "coco_wholebody_133" or not isinstance(kp, list) or len(kp) != 133:
                raise InventoryError(f"Invalid pose record at line {line_no}")
            out.append(rec)
    if not out:
        raise InventoryError("Pose track is empty")
    return out

def group_stats(frames, ids):
    scores = []
    confident = 0
    total = 0
    frame_any = 0
    for rec in frames:
        any_conf = False
        for i in ids:
            score = rec["keypoints"][i][2]
            sf = float(score) if score is not None and math.isfinite(float(score)) else 0.0
            scores.append(sf)
            total += 1
            if sf >= CONF:
                confident += 1
                any_conf = True
        if any_conf:
            frame_any += 1
    return {
        "mean_score": statistics.fmean(scores) if scores else 0.0,
        "confident_keypoint_ratio": confident / total if total else 0.0,
        "frame_presence_ratio": frame_any / len(frames) if frames else 0.0,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--pose-track", type=Path, required=True)
    ap.add_argument("--output-json", type=Path, required=True)
    ap.add_argument("--output-csv", type=Path, required=True)
    args = ap.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    if manifest.get("status") != "complete":
        raise InventoryError("Manifest status must be complete")
    units = manifest.get("motion_units") or []
    if not units:
        raise InventoryError("Manifest contains no motion units")
    pose = load_pose(args.pose_track)

    rows = []
    for unit in units:
        st, en = float(unit["start_s"]), float(unit["end_s"])
        frames = [r for r in pose if st <= float(r["t"]) < en]
        if not frames:
            frames = [min(pose, key=lambda r: abs(float(r["t"]) - st))]
        gs = {name: group_stats(frames, ids) for name, ids in GROUPS.items()}
        activity = unit.get("hand_activity") or {}
        combined = activity.get("combined") or {}
        body = unit.get("body_activity") or {}
        head = unit.get("head_motion") or {}
        trans = unit.get("transition") or {}
        motion = unit.get("motion_energy") or {}
        row = {
            "id": unit["id"],
            "start_s": st,
            "end_s": en,
            "duration_s": float(unit["duration_s"]),
            "speech_class": (unit.get("speech") or {}).get("class"),
            "speech_ratio": float((unit.get("speech") or {}).get("speech_ratio", 0.0)),
            "motion_mean": float(motion.get("mean", 0.0)),
            "motion_peak": float(motion.get("peak", 0.0)),
            "head_speed": float(head.get("mean_speed_norm_s", 0.0)) if head else 0.0,
            "body_speed": float(body.get("mean_speed_norm_s", 0.0)) if body else 0.0,
            "hand_speed": float(combined.get("mean_speed_norm_s", 0.0)) if combined else 0.0,
            "hand_peak_speed": float(combined.get("peak_speed_norm_s", 0.0)) if combined else 0.0,
            "entry_score": float(trans.get("entry_score", 0.0)),
            "exit_score": float(trans.get("exit_score", 0.0)),
            "pose_frames": len(frames),
        }
        for name, stats in gs.items():
            row[f"{name}_mean_score"] = stats["mean_score"]
            row[f"{name}_confident_ratio"] = stats["confident_keypoint_ratio"]
            row[f"{name}_frame_presence"] = stats["frame_presence_ratio"]
        row["min_upper_confident_ratio"] = min(
            row["head_confident_ratio"], row["body_confident_ratio"],
            row["left_hand_confident_ratio"], row["right_hand_confident_ratio"]
        )
        rows.append(row)

    hand_speeds = [r["hand_speed"] for r in rows]
    body_speeds = [r["body_speed"] for r in rows]
    coverages = [r["min_upper_confident_ratio"] for r in rows]
    hand_q90 = percentile(hand_speeds, .90) or 0.0
    body_q90 = percentile(body_speeds, .90) or 0.0
    cov_q10 = percentile(coverages, .10) or 0.0
    motion_q90 = percentile([r["motion_mean"] for r in rows], .90) or 0.0

    for r in rows:
        tags = []
        if r["hand_speed"] >= hand_q90:
            tags.append("top_hand_motion")
        if r["body_speed"] >= body_q90:
            tags.append("top_body_motion")
        if r["motion_mean"] >= motion_q90:
            tags.append("top_rgb_motion")
        if r["min_upper_confident_ratio"] <= cov_q10:
            tags.append("low_relative_pose_coverage")
        if r["speech_class"] == "pause":
            tags.append("pause_unit")
        r["review_tags"] = tags

    selected = []
    seen = set()
    def add_sorted(tag, key, reverse=True, limit=6):
        candidates = [r for r in rows if tag in r["review_tags"]]
        for r in sorted(candidates, key=lambda x: x[key], reverse=reverse):
            if r["id"] not in seen:
                selected.append(r["id"]); seen.add(r["id"])
                if sum(1 for sid in selected if sid in {c["id"] for c in candidates}) >= limit:
                    break
    add_sorted("low_relative_pose_coverage", "min_upper_confident_ratio", reverse=False, limit=6)
    add_sorted("top_hand_motion", "hand_speed", limit=6)
    add_sorted("top_body_motion", "body_speed", limit=4)
    add_sorted("top_rgb_motion", "motion_mean", limit=4)
    add_sorted("pause_unit", "duration_s", limit=4)
    if len(selected) < 24:
        med = percentile([r["start_s"] for r in rows], .5) or 0.0
        for r in sorted(rows, key=lambda x: abs(x["start_s"] - med)):
            if r["id"] not in seen:
                selected.append(r["id"]); seen.add(r["id"])
            if len(selected) >= 24:
                break
    selected = selected[:24]

    summary = {
        "schema": "behavior-inventory-review/v1",
        "manifest": str(args.manifest),
        "pose_track": str(args.pose_track),
        "confidence_threshold": CONF,
        "units": len(rows),
        "source_relative_thresholds": {
            "hand_speed_q90": hand_q90,
            "body_speed_q90": body_q90,
            "motion_mean_q90": motion_q90,
            "upper_pose_coverage_q10": cov_q10,
        },
        "coverage_quantiles": {
            "q10": percentile(coverages, .10),
            "median": percentile(coverages, .50),
            "q90": percentile(coverages, .90),
        },
        "hand_speed_quantiles": {
            "q10": percentile(hand_speeds, .10),
            "median": percentile(hand_speeds, .50),
            "q90": percentile(hand_speeds, .90),
        },
        "body_speed_quantiles": {
            "q10": percentile(body_speeds, .10),
            "median": percentile(body_speeds, .50),
            "q90": percentile(body_speeds, .90),
        },
        "selected_review_unit_ids": selected,
        "units_detail": rows,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = list(rows[0].keys())
    with args.output_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader(); w.writerows(rows)

    print("BEHAVIOR INVENTORY QUALITY ANALYSIS")
    print("==================================")
    print(f"Units: {len(rows)}")
    print(f"Upper pose coverage q10/median/q90: {summary['coverage_quantiles']['q10']:.3f}/{summary['coverage_quantiles']['median']:.3f}/{summary['coverage_quantiles']['q90']:.3f}")
    print(f"Hand speed q10/median/q90: {summary['hand_speed_quantiles']['q10']:.4f}/{summary['hand_speed_quantiles']['median']:.4f}/{summary['hand_speed_quantiles']['q90']:.4f}")
    print(f"Body speed q10/median/q90: {summary['body_speed_quantiles']['q10']:.4f}/{summary['body_speed_quantiles']['median']:.4f}/{summary['body_speed_quantiles']['q90']:.4f}")
    print("Selected visual review units: " + ", ".join(selected))
    print(f"Analysis JSON: {args.output_json}")
    print(f"Unit CSV: {args.output_csv}")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except InventoryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
