#!/usr/bin/env python3
"""Inspect facial-behavior-profile/v1 alignment and quality distributions."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path


def q(values, p):
    vals = sorted(float(v) for v in values if v is not None and math.isfinite(float(v)))
    if not vals:
        return None
    x = max(0.0, min(1.0, p)) * (len(vals) - 1)
    lo = int(math.floor(x)); hi = int(math.ceil(x))
    if lo == hi:
        return vals[lo]
    return vals[lo] * (hi - x) + vals[hi] * (x - lo)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sidecar", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    if not args.sidecar.is_file():
        raise SystemExit(f"Sidecar missing: {args.sidecar}")
    if not args.manifest.is_file():
        raise SystemExit(f"Manifest missing: {args.manifest}")

    sidecar = json.loads(args.sidecar.read_text(encoding="utf-8-sig"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    issues = []
    if sidecar.get("schema_version") != "facial-behavior-profile/v1":
        issues.append("unexpected sidecar schema")
    if manifest.get("schema_version") != "behavior-profile/v1":
        issues.append("unexpected base manifest schema")

    su = sidecar.get("units") or []
    bu = manifest.get("motion_units") or []
    if len(su) != len(bu):
        issues.append(f"unit count mismatch sidecar={len(su)} base={len(bu)}")

    for i, (a, b) in enumerate(zip(su, bu), 1):
        if a.get("id") != b.get("id"):
            issues.append(f"unit id mismatch at {i}: {a.get('id')} vs {b.get('id')}")
            break
        if abs(float(a.get("start_s", 0)) - float(b.get("start_s", 0))) > 1e-6 or abs(float(a.get("end_s", 0)) - float(b.get("end_s", 0))) > 1e-6:
            issues.append(f"unit time mismatch for {a.get('id')}")
            break

    ratios = [float(u.get("accepted_frame_ratio") or 0.0) for u in su]
    weights = [float(u.get("face_quality_weight") or 0.0) for u in su]
    hard_counts = [int(u.get("hard_suspect_frames") or 0) for u in su]
    temporal_counts = [int(u.get("temporal_review_frames") or 0) for u in su]
    usable = [u for u in su if int(u.get("frames_accepted") or 0) >= 2]

    summary = {
        "structural_pass": not issues,
        "units": len(su),
        "units_with_at_least_2_accepted_frames": len(usable),
        "accepted_frame_ratio": {
            "q10": q(ratios, .10),
            "median": q(ratios, .50),
            "q90": q(ratios, .90),
            "min": min(ratios) if ratios else None,
        },
        "face_quality_weight": {
            "q10": q(weights, .10),
            "median": q(weights, .50),
            "q90": q(weights, .90),
            "min": min(weights) if weights else None,
            "max": max(weights) if weights else None,
        },
        "units_with_hard_suspects": sum(1 for n in hard_counts if n > 0),
        "hard_suspect_frames_across_units": sum(hard_counts),
        "units_with_temporal_review": sum(1 for n in temporal_counts if n > 0),
        "issues": issues,
        "lowest_quality_units": [
            {"id": u.get("id"), "weight": u.get("face_quality_weight"), "accepted_ratio": u.get("accepted_frame_ratio")}
            for u in sorted(su, key=lambda x: float(x.get("face_quality_weight") or 0.0))[:10]
        ],
    }

    out = args.output or args.sidecar.with_name("facial_sidecar_inspection.json")
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("FACIAL BEHAVIOR SIDECAR INSPECTION")
    print("==================================")
    print(f"Structural pass: {summary['structural_pass']}")
    print(f"Units: {summary['units']} / usable >=2 accepted facial frames: {summary['units_with_at_least_2_accepted_frames']}")
    r = summary["accepted_frame_ratio"]
    print(f"Accepted frame ratio q10/median/q90: {r['q10']}/{r['median']}/{r['q90']}")
    w = summary["face_quality_weight"]
    print(f"Face quality weight q10/median/q90: {w['q10']}/{w['median']}/{w['q90']}")
    print(f"Units with hard facial suspects: {summary['units_with_hard_suspects']}")
    print(f"Hard suspect frame references across units: {summary['hard_suspect_frames_across_units']}")
    print(f"Units with temporal review signal: {summary['units_with_temporal_review']}")
    if issues:
        for issue in issues:
            print("FAIL: " + issue)
    print("Lowest facial-quality units:")
    for row in summary["lowest_quality_units"]:
        print(f"  {row['id']} weight={row['weight']} accepted={row['accepted_ratio']}")
    print(f"Inspection JSON: {out}")
    return 0 if not issues else 2


if __name__ == "__main__":
    raise SystemExit(main())
