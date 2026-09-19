#!/usr/bin/env python3
"""Inspect a generated behavior-profile/v1 manifest without extra dependencies."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

EXPECTED_SCHEMA = "behavior-profile/v1"
POSE_SCHEMA = "coco_wholebody_133"


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def valid_pose_snapshot(snap) -> bool:
    return (
        isinstance(snap, dict)
        and snap.get("schema") == POSE_SCHEMA
        and isinstance(snap.get("keypoints"), list)
        and len(snap["keypoints"]) == 133
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    if not args.manifest.is_file():
        fail(f"Manifest not found: {args.manifest}")
    if not args.csv.is_file():
        fail(f"CSV not found: {args.csv}")

    profile = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    with args.csv.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    issues: list[str] = []
    warnings: list[str] = []
    units = profile.get("motion_units") or []

    if profile.get("schema_version") != EXPECTED_SCHEMA:
        issues.append(f"schema_version={profile.get('schema_version')!r}")
    if profile.get("status") != "complete":
        issues.append(f"status={profile.get('status')!r}, expected 'complete'")
    if not units:
        issues.append("motion_units is empty")
    if len(rows) != len(units):
        issues.append(f"CSV row count {len(rows)} != manifest units {len(units)}")

    ids = [str(u.get("id")) for u in units]
    if len(ids) != len(set(ids)):
        issues.append("motion unit IDs are not unique")

    duration = float((profile.get("source") or {}).get("duration_s") or 0.0)
    if units:
        if abs(float(units[0].get("start_s", 999.0))) > 0.01:
            issues.append(f"first unit does not start at source start: {units[0].get('start_s')}")
        if duration > 0 and abs(float(units[-1].get("end_s", 0.0)) - duration) > 0.02:
            issues.append(f"last unit does not reach source end: {units[-1].get('end_s')} vs {duration}")

    discontinuities = []
    for prev, cur in zip(units, units[1:]):
        delta = float(cur.get("start_s", 0.0)) - float(prev.get("end_s", 0.0))
        if abs(delta) > 0.002:
            discontinuities.append({"after": prev.get("id"), "before": cur.get("id"), "delta_s": delta})
    if discontinuities:
        issues.append(f"timeline discontinuities={len(discontinuities)}")

    invalid_pose_units = []
    activity_counts = Counter()
    speech_counts = Counter()
    boundary_counts = Counter()
    durations = []
    hand_rank = []
    body_rank = []

    for u in units:
        uid = str(u.get("id"))
        try:
            durations.append(float(u.get("duration_s")))
        except Exception:
            issues.append(f"invalid duration in {uid}")

        if not valid_pose_snapshot(u.get("pose_start")) or not valid_pose_snapshot(u.get("pose_end")):
            invalid_pose_units.append(uid)

        if u.get("head_motion") is not None:
            activity_counts["head"] += 1
        if u.get("body_activity") is not None:
            activity_counts["body"] += 1
        hand = u.get("hand_activity") or {}
        if hand.get("left") is not None:
            activity_counts["left_hand"] += 1
        if hand.get("right") is not None:
            activity_counts["right_hand"] += 1
        if hand.get("combined") is not None:
            activity_counts["combined_hands"] += 1
            hand_rank.append((float(hand["combined"].get("mean_speed_norm_s", 0.0)), uid))
        body = u.get("body_activity")
        if body is not None:
            body_rank.append((float(body.get("mean_speed_norm_s", 0.0)), uid))

        speech_counts[str((u.get("speech") or {}).get("class", "unknown"))] += 1
        boundary_counts[str((u.get("transition") or {}).get("boundary_reason", "unknown"))] += 1

    if invalid_pose_units:
        issues.append(f"units with invalid pose snapshots={len(invalid_pose_units)}")
    for name in ("head", "body", "left_hand", "right_hand", "combined_hands"):
        if units and activity_counts[name] == 0:
            issues.append(f"no usable {name} activity in any unit")

    analysis = profile.get("analysis") or {}
    if analysis.get("motion_analysis_width") and analysis.get("motion_analysis_height"):
        motion_geometry = f"{analysis['motion_analysis_width']}x{analysis['motion_analysis_height']}"
    else:
        motion_geometry = "legacy/unknown"
        warnings.append("motion analysis geometry not recorded")

    summary = {
        "structural_pass": not issues,
        "schema_version": profile.get("schema_version"),
        "status": profile.get("status"),
        "profile_id": profile.get("profile_id"),
        "source": (profile.get("source") or {}).get("file"),
        "source_duration_s": duration,
        "units": len(units),
        "csv_rows": len(rows),
        "coverage": {
            "first_start_s": units[0].get("start_s") if units else None,
            "last_end_s": units[-1].get("end_s") if units else None,
            "discontinuities": discontinuities,
        },
        "unit_duration_s": {
            "min": min(durations) if durations else None,
            "median": statistics.median(durations) if durations else None,
            "max": max(durations) if durations else None,
        },
        "pose_snapshots_valid_units": len(units) - len(invalid_pose_units),
        "activity_available_units": dict(activity_counts),
        "speech_class_counts": dict(speech_counts),
        "boundary_reason_counts": dict(boundary_counts),
        "top_hand_activity_units": [uid for _, uid in sorted(hand_rank, reverse=True)[:8]],
        "top_body_activity_units": [uid for _, uid in sorted(body_rank, reverse=True)[:8]],
        "motion_analysis_geometry": motion_geometry,
        "pose_backend": analysis.get("pose_backend"),
        "pose_confidence_floor": analysis.get("pose_confidence_floor"),
        "issues": issues,
        "warnings": warnings,
    }

    output = args.output or args.manifest.with_name("profile_inspection.json")
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("BEHAVIOR PROFILE INSPECTION")
    print("===========================")
    print(f"Structural pass: {summary['structural_pass']}")
    print(f"Status: {summary['status']}")
    print(f"Units: {summary['units']} / CSV rows: {summary['csv_rows']}")
    print(f"Coverage: {summary['coverage']['first_start_s']} -> {summary['coverage']['last_end_s']} s / source={duration} s")
    print(f"Motion analysis: {motion_geometry}")
    print(f"Pose snapshots valid: {summary['pose_snapshots_valid_units']}/{summary['units']}")
    print("Activity units: " + ", ".join(f"{k}={activity_counts[k]}" for k in ("head","body","left_hand","right_hand","combined_hands")))
    print("Speech classes: " + ", ".join(f"{k}={v}" for k,v in sorted(speech_counts.items())))
    if durations:
        print(f"Unit duration min/median/max: {min(durations):.3f}/{statistics.median(durations):.3f}/{max(durations):.3f} s")
    if issues:
        for item in issues:
            print("FAIL: " + item)
    for item in warnings:
        print("WARN: " + item)
    print("Inspection JSON: " + str(output))

    return 0 if not issues else 2


if __name__ == "__main__":
    raise SystemExit(main())
