#!/usr/bin/env python3
"""Robust source-relative QA for normalized facial behavior tracks.

No model inference. The audit detects gross normalization/geometry failures using
Tukey outer fences (3*IQR) derived from the source itself. Temporal jumps are
reported separately as review suspects and are not automatic hard exclusions.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

from facial_descriptors import (
    DEFAULT_CONF,
    EXPRESSION,
    facial_signals,
    load_pose_jsonl,
    normalize_face_frame,
    summarize_facial_frames,
)


def quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    p = max(0.0, min(1.0, q)) * (len(s) - 1)
    lo = int(math.floor(p))
    hi = int(math.ceil(p))
    if lo == hi:
        return s[lo]
    return s[lo] * (hi - p) + s[hi] * (p - lo)


def outer_fence(values: list[float], k: float = 3.0):
    vals = [float(v) for v in values if math.isfinite(float(v))]
    if len(vals) < 8:
        return None
    q1 = quantile(vals, 0.25)
    q3 = quantile(vals, 0.75)
    iqr = q3 - q1
    if iqr <= 1e-12:
        return None
    return {
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "lower": q1 - k * iqr,
        "upper": q3 + k * iqr,
        "k": k,
    }


def shape_distance(a: dict[int, tuple[float, float]], b: dict[int, tuple[float, float]], ids) -> float | None:
    common = [i for i in ids if i in a and i in b]
    if len(common) < 8:
        return None
    dsq = []
    for i in common:
        dx = b[i][0] - a[i][0]
        dy = b[i][1] - a[i][1]
        dsq.append(dx * dx + dy * dy)
    return math.sqrt(statistics.fmean(dsq))


def face_extent(coords: dict[int, tuple[float, float]]) -> float | None:
    if len(coords) < 8:
        return None
    xs = [p[0] for p in coords.values()]
    ys = [p[1] for p in coords.values()]
    return max(max(xs) - min(xs), max(ys) - min(ys))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pose-track", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--confidence", type=float, default=DEFAULT_CONF)
    ap.add_argument("--fence-k", type=float, default=3.0)
    args = ap.parse_args()

    if not args.pose_track.is_file():
        raise SystemExit(f"Pose track missing: {args.pose_track}")

    frames = load_pose_jsonl(args.pose_track)
    norm_rows = []
    failed_times = []
    for frame in frames:
        nf = normalize_face_frame(frame, conf=args.confidence)
        if nf is None:
            failed_times.append(frame.t)
            continue
        sig = facial_signals(nf["coords"])
        ext = face_extent(nf["coords"])
        row = {
            "t": frame.t,
            "nf": nf,
            "intereye_scale": float(nf["intereye_scale_image_norm"]),
            "log_intereye_scale": math.log(max(float(nf["intereye_scale_image_norm"]), 1e-12)),
            "face_extent": ext,
            **sig,
        }
        norm_rows.append(row)

    static_features = [
        "log_intereye_scale",
        "face_extent",
        "mouth_open",
        "mouth_width",
        "eye_open",
        "brow_eye_distance",
    ]
    fences = {}
    for key in static_features:
        vals = [float(r[key]) for r in norm_rows if r.get(key) is not None and math.isfinite(float(r[key]))]
        fences[key] = outer_fence(vals, k=args.fence_k)

    static_suspects: dict[float, list[str]] = {}
    severity: dict[float, float] = {}
    for row in norm_rows:
        reasons = []
        sev = 0.0
        for key in static_features:
            f = fences.get(key)
            v = row.get(key)
            if f is None or v is None or not math.isfinite(float(v)):
                continue
            v = float(v)
            if v < f["lower"]:
                reasons.append(f"{key}:low")
                sev = max(sev, (f["lower"] - v) / max(f["iqr"], 1e-12))
            elif v > f["upper"]:
                reasons.append(f"{key}:high")
                sev = max(sev, (v - f["upper"]) / max(f["iqr"], 1e-12))
        if reasons:
            static_suspects[row["t"]] = reasons
            severity[row["t"]] = sev

    temporal_rows = []
    for a, b in zip(norm_rows, norm_rows[1:]):
        dt = float(b["t"]) - float(a["t"])
        if dt <= 1e-8 or dt > 0.5:
            continue
        d = shape_distance(a["nf"]["coords"], b["nf"]["coords"], EXPRESSION)
        if d is None:
            continue
        temporal_rows.append({"from_t": a["t"], "to_t": b["t"], "speed": d / dt})
    temporal_fence = outer_fence([r["speed"] for r in temporal_rows], k=args.fence_k)
    temporal_suspect_times: dict[float, list[str]] = {}
    if temporal_fence is not None:
        for r in temporal_rows:
            if r["speed"] > temporal_fence["upper"]:
                # Both endpoints are review candidates. This does not hard-reject either one.
                temporal_suspect_times.setdefault(r["from_t"], []).append("expression_step:high")
                temporal_suspect_times.setdefault(r["to_t"], []).append("expression_step:high")

    accepted_times = {r["t"] for r in norm_rows if r["t"] not in static_suspects}
    accepted_frames = [f for f in frames if f.t in accepted_times]
    filtered_summary = summarize_facial_frames(accepted_frames, conf=args.confidence) if accepted_frames else None
    raw_summary = summarize_facial_frames(frames, conf=args.confidence)

    suspects = []
    all_times = sorted(set(failed_times) | set(static_suspects) | set(temporal_suspect_times))
    for t in all_times:
        reasons = []
        hard = False
        if t in failed_times:
            reasons.append("normalization_failed")
            hard = True
        if t in static_suspects:
            reasons.extend(static_suspects[t])
            hard = True
        reasons.extend(temporal_suspect_times.get(t, []))
        suspects.append({
            "t": round(float(t), 6),
            "hard_suspect": hard,
            "severity_iqr": round(float(severity.get(t, 0.0)), 6),
            "reasons": sorted(set(reasons)),
        })
    suspects.sort(key=lambda x: (not x["hard_suspect"], -x["severity_iqr"], x["t"]))

    result = {
        "schema": "facial-quality-audit/v1",
        "pose_track": str(args.pose_track.resolve()),
        "confidence_floor": args.confidence,
        "outlier_policy": "source-relative Tukey outer fence (3*IQR by default); temporal jumps are review-only",
        "fence_k": args.fence_k,
        "frames_total": len(frames),
        "normalized_frames": len(norm_rows),
        "normalization_failed_frames": len(failed_times),
        "static_hard_suspect_frames": len(static_suspects),
        "temporal_review_suspect_frames": len(temporal_suspect_times),
        "accepted_static_geometry_frames": len(accepted_frames),
        "accepted_static_geometry_ratio": round(len(accepted_frames) / len(frames), 6) if frames else 0.0,
        "static_fences": fences,
        "temporal_expression_speed_fence": temporal_fence,
        "raw_summary": raw_summary,
        "filtered_static_geometry_summary": filtered_summary,
        "suspect_frames": suspects,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("FACIAL QUALITY AUDIT")
    print("====================")
    print(f"Frames total: {len(frames)}")
    print(f"Normalized: {len(norm_rows)}")
    print(f"Normalization failed: {len(failed_times)}")
    print(f"Static hard suspects: {len(static_suspects)}")
    print(f"Temporal review suspects: {len(temporal_suspect_times)}")
    print(f"Accepted static geometry: {len(accepted_frames)}/{len(frames)} ({result['accepted_static_geometry_ratio']})")
    print("Outlier policy: " + result["outlier_policy"])
    if filtered_summary:
        d = filtered_summary.get("deformation") or {}
        m = (filtered_summary.get("regions") or {}).get("mouth") or {}
        print("Filtered expression mean/peak: " + str(d.get("mean_speed_norm_s")) + "/" + str(d.get("peak_speed_norm_s")))
        print("Filtered mouth mean/peak: " + str(m.get("mean_speed_norm_s")) + "/" + str(m.get("peak_speed_norm_s")))
        for signal in ("mouth_open", "mouth_width", "eye_open", "brow_eye_distance"):
            s = (filtered_summary.get("signals") or {}).get(signal)
            if s:
                print(f"Filtered {signal} mean/range: {s['mean']}/{s['range']}")
    print(f"Suspect rows: {len(suspects)}")
    for item in suspects[:20]:
        print(f"  t={item['t']:.3f}s hard={item['hard_suspect']} severity_iqr={item['severity_iqr']} reasons={','.join(item['reasons'])}")
    if len(suspects) > 20:
        print(f"  ... {len(suspects) - 20} more in JSON")
    print("JSON: " + str(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
