#!/usr/bin/env python3
"""Build facial-behavior-profile/v1 aligned to an existing behavior-profile/v1.

No model inference. Reads:
- base behavior manifest (motion-unit IDs/timestamps)
- existing COCO WholeBody 133 pose JSONL
- facial-quality-audit/v1

Hard facial QA suspects are excluded only from facial descriptor calculation. They do not
remove the underlying motion unit from the base behavior profile.
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from facial_descriptors import DEFAULT_CONF, load_pose_jsonl, summarize_facial_frames


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--pose-track", type=Path, required=True)
    ap.add_argument("--audit", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    for label, path in (("manifest", args.manifest), ("pose track", args.pose_track), ("audit", args.audit)):
        if not path.is_file():
            raise SystemExit(f"Missing {label}: {path}")

    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    audit = json.loads(args.audit.read_text(encoding="utf-8-sig"))
    if manifest.get("schema_version") != "behavior-profile/v1":
        raise SystemExit(f"Unexpected base schema: {manifest.get('schema_version')!r}")
    if audit.get("schema") != "facial-quality-audit/v1":
        raise SystemExit(f"Unexpected audit schema: {audit.get('schema')!r}")

    frames = load_pose_jsonl(args.pose_track)
    hard_times = {
        round(float(row["t"]), 6)
        for row in audit.get("suspect_frames", [])
        if row.get("hard_suspect")
    }
    temporal_review_times = {
        round(float(row["t"]), 6)
        for row in audit.get("suspect_frames", [])
        if (not row.get("hard_suspect")) and "expression_step:high" in (row.get("reasons") or [])
    }

    units_out = []
    for unit in manifest.get("motion_units") or []:
        uid = str(unit["id"])
        start = float(unit["start_s"])
        end = float(unit["end_s"])
        span_frames = [f for f in frames if start <= f.t <= end]
        accepted = [f for f in span_frames if round(float(f.t), 6) not in hard_times]
        summary = summarize_facial_frames(accepted, conf=DEFAULT_CONF) if accepted else None

        total = len(span_frames)
        accepted_n = len(accepted)
        accepted_ratio = accepted_n / total if total else 0.0
        presence = float((summary or {}).get("mean_face_point_presence") or 0.0)
        confidence = float((summary or {}).get("mean_landmark_confidence") or 0.0)
        quality_weight = accepted_ratio * presence * confidence

        hard_n = sum(1 for f in span_frames if round(float(f.t), 6) in hard_times)
        temporal_n = sum(1 for f in span_frames if round(float(f.t), 6) in temporal_review_times)

        units_out.append({
            "id": uid,
            "start_s": round(start, 3),
            "end_s": round(end, 3),
            "duration_s": round(float(unit["duration_s"]), 3),
            "frames_total": total,
            "frames_accepted": accepted_n,
            "accepted_frame_ratio": round(accepted_ratio, 6),
            "hard_suspect_frames": hard_n,
            "temporal_review_frames": temporal_n,
            "mean_face_point_presence": round(presence, 6),
            "mean_landmark_confidence": round(confidence, 6),
            "face_quality_weight": round(quality_weight, 6),
            "deformation": (summary or {}).get("deformation"),
            "regions": (summary or {}).get("regions"),
            "signals": (summary or {}).get("signals"),
        })

    quality_values = [float(u["face_quality_weight"]) for u in units_out]
    accepted_ratios = [float(u["accepted_frame_ratio"]) for u in units_out]

    sidecar = {
        "schema_version": "facial-behavior-profile/v1",
        "profile_id": f"{manifest.get('profile_id')}/face",
        "subject_id": str(manifest.get("subject_id") or "joao"),
        "source_file": str((manifest.get("source") or {}).get("file") or ""),
        "base_profile": {
            "schema_version": "behavior-profile/v1",
            "profile_id": str(manifest.get("profile_id") or ""),
            "manifest_path": str(args.manifest.resolve()),
        },
        "analysis": {
            "landmark_schema": "coco_wholebody_face68_23_90",
            "pose_track": str(args.pose_track.resolve()),
            "quality_audit": str(args.audit.resolve()),
            "confidence_floor": DEFAULT_CONF,
            "normalization": "eye_line_midpoint + remove_inplane_roll + intereye_scale",
            "hard_facial_exclusion_policy": "normalization failures + source-relative static Tukey outer-fence suspects; facial layer only",
            "temporal_jump_policy": "review signal only; not automatically excluded",
            "face_quality_weight_formula": "accepted_frame_ratio * mean_face_point_presence * mean_landmark_confidence",
            "units": len(units_out),
            "median_accepted_frame_ratio": round(statistics.median(accepted_ratios), 6) if accepted_ratios else None,
            "median_face_quality_weight": round(statistics.median(quality_values), 6) if quality_values else None,
        },
        "units": units_out,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")

    print("FACIAL BEHAVIOR SIDECAR BUILD")
    print("=============================")
    print(f"Units: {len(units_out)}")
    print(f"Hard facial suspect timestamps: {len(hard_times)}")
    print(f"Median accepted frame ratio: {sidecar['analysis']['median_accepted_frame_ratio']}")
    print(f"Median face quality weight: {sidecar['analysis']['median_face_quality_weight']}")
    print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
