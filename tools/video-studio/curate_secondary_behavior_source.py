#!/usr/bin/env python3
"""Role-aware curation for the secondary face/head behavior source.

No model inference. Joins:
- behavior inventory analysis (pose/group reliability + motion-unit metadata)
- facial-behavior-profile/v1 sidecar
- source-role annotations

The secondary source is not treated like the primary gesture source. Face/head/body-support
retrieval roles are curated independently. Hands remain recorded diagnostically but are
explicitly disabled for retrieval from this source role.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def effective(confident_ratio, frame_presence) -> float:
    c = 0.0 if confident_ratio is None else float(confident_ratio)
    p = 0.0 if frame_presence is None else float(frame_presence)
    return max(0.0, min(1.0, c * p))


def percentile(values, q: float):
    vals = sorted(float(v) for v in values)
    if not vals:
        return None
    if len(vals) == 1:
        return vals[0]
    p = max(0.0, min(1.0, q)) * (len(vals) - 1)
    lo = int(math.floor(p))
    hi = int(math.ceil(p))
    if lo == hi:
        return vals[lo]
    return vals[lo] * (hi - p) + vals[hi] * (p - lo)


def overlap(a0: float, a1: float, b0: float, b1: float) -> bool:
    return max(a0, b0) < min(a1, b1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", type=Path, required=True)
    ap.add_argument("--facial-sidecar", type=Path, required=True)
    ap.add_argument("--annotations", type=Path, required=True)
    ap.add_argument("--output-json", type=Path, required=True)
    ap.add_argument("--output-csv", type=Path, required=True)
    args = ap.parse_args()

    for label, path in (("analysis", args.analysis), ("facial sidecar", args.facial_sidecar), ("annotations", args.annotations)):
        if not path.is_file():
            raise SystemExit(f"Missing {label}: {path}")

    analysis = json.loads(args.analysis.read_text(encoding="utf-8-sig"))
    face = json.loads(args.facial_sidecar.read_text(encoding="utf-8-sig"))
    ann = json.loads(args.annotations.read_text(encoding="utf-8-sig"))

    if face.get("schema_version") != "facial-behavior-profile/v1":
        raise SystemExit(f"Unexpected facial sidecar schema: {face.get('schema_version')!r}")

    units = analysis.get("units_detail") or []
    face_by_id = {str(u["id"]): u for u in face.get("units") or []}
    exclusions = ann.get("manual_exclusions") or []

    if len(face_by_id) != len(units):
        raise SystemExit(f"Unit-count mismatch: analysis={len(units)} facial={len(face_by_id)}")

    curated = []
    global_excluded = 0
    face_eligible_count = 0
    head_eligible_count = 0
    body_support_eligible_count = 0

    for u in units:
        uid = str(u["id"])
        fu = face_by_id.get(uid)
        if fu is None:
            raise SystemExit(f"Missing facial unit for {uid}")

        st = float(u["start_s"])
        en = float(u["end_s"])
        matched = [x for x in exclusions if overlap(st, en, float(x["start_s"]), float(x["end_s"]))]
        hard_excluded = bool(matched)
        reasons = []
        for x in matched:
            for r in x.get("reasons") or []:
                if r not in reasons:
                    reasons.append(r)

        head_q = effective(u.get("head_confident_ratio"), u.get("head_frame_presence"))
        body_q = effective(u.get("body_confident_ratio"), u.get("body_frame_presence"))
        left_q = effective(u.get("left_hand_confident_ratio"), u.get("left_hand_frame_presence"))
        right_q = effective(u.get("right_hand_confident_ratio"), u.get("right_hand_frame_presence"))

        face_q = max(0.0, min(1.0, float(fu.get("face_quality_weight") or 0.0)))
        accepted_frames = int(fu.get("frames_accepted") or 0)
        accepted_ratio = float(fu.get("accepted_frame_ratio") or 0.0)
        face_structurally_usable = accepted_frames >= 2

        face_eligible = (not hard_excluded) and face_structurally_usable and face_q > 0.0
        head_weight = head_q * face_q
        body_support_weight = body_q * face_q
        head_eligible = face_eligible and head_weight > 0.0
        body_support_eligible = face_eligible and body_support_weight > 0.0

        row = {
            **u,
            "global_hard_excluded": hard_excluded,
            "global_exclusion_reasons": reasons,
            "source_role": ann.get("source_role"),
            "pose_quality": {
                "head": round(head_q, 6),
                "body": round(body_q, 6),
                "left_hand": round(left_q, 6),
                "right_hand": round(right_q, 6),
            },
            "facial_quality": {
                "frames_total": int(fu.get("frames_total") or 0),
                "frames_accepted": accepted_frames,
                "accepted_frame_ratio": round(accepted_ratio, 6),
                "hard_suspect_frames": int(fu.get("hard_suspect_frames") or 0),
                "temporal_review_frames": int(fu.get("temporal_review_frames") or 0),
                "mean_face_point_presence": float(fu.get("mean_face_point_presence") or 0.0),
                "mean_landmark_confidence": float(fu.get("mean_landmark_confidence") or 0.0),
                "face_quality_weight": round(face_q, 6),
            },
            "retrieval_roles": {
                "face": {"enabled": face_eligible, "weight": round(face_q if face_eligible else 0.0, 6)},
                "head": {"enabled": head_eligible, "weight": round(head_weight if head_eligible else 0.0, 6)},
                "body_support": {"enabled": body_support_eligible, "weight": round(body_support_weight if body_support_eligible else 0.0, 6)},
                "left_hand": {"enabled": False, "weight": 0.0},
                "right_hand": {"enabled": False, "weight": 0.0},
                "both_hands": {"enabled": False, "weight": 0.0},
                "generic_whole_upper": {"enabled": False, "weight": 0.0},
            },
            "face_structurally_usable": face_structurally_usable,
        }
        curated.append(row)

        global_excluded += int(hard_excluded)
        face_eligible_count += int(face_eligible)
        head_eligible_count += int(head_eligible)
        body_support_eligible_count += int(body_support_eligible)

    face_weights = [float(u["retrieval_roles"]["face"]["weight"]) for u in curated]
    head_weights = [float(u["retrieval_roles"]["head"]["weight"]) for u in curated]
    body_weights = [float(u["retrieval_roles"]["body_support"]["weight"]) for u in curated]

    def qs(values):
        return {
            "q10": percentile(values, 0.10),
            "median": percentile(values, 0.50),
            "q90": percentile(values, 0.90),
        }

    lowest = sorted(curated, key=lambda x: (x["retrieval_roles"]["face"]["weight"], x["start_s"]))[:10]

    out = {
        "schema": "behavior-role-curated-inventory/v1",
        "source_file": ann.get("source_file"),
        "source_role": ann.get("source_role"),
        "analysis_source": str(args.analysis.resolve()),
        "facial_sidecar_source": str(args.facial_sidecar.resolve()),
        "annotations_source": str(args.annotations.resolve()),
        "retrieval_policy": ann.get("retrieval_policy"),
        "quality_policy": ann.get("quality_policy"),
        "units_total": len(curated),
        "global_hard_excluded": global_excluded,
        "role_counts": {
            "face_eligible": face_eligible_count,
            "head_eligible": head_eligible_count,
            "body_support_eligible": body_support_eligible_count,
            "hands_retrieval_enabled": 0,
            "generic_whole_upper_enabled": 0,
        },
        "role_weight_quantiles": {
            "face": qs(face_weights),
            "head": qs(head_weights),
            "body_support": qs(body_weights),
        },
        "lowest_face_quality_units": [
            {
                "id": u["id"],
                "start_s": u["start_s"],
                "end_s": u["end_s"],
                "face_weight": u["retrieval_roles"]["face"]["weight"],
                "accepted_frame_ratio": u["facial_quality"]["accepted_frame_ratio"],
                "frames_accepted": u["facial_quality"]["frames_accepted"],
            }
            for u in lowest
        ],
        "units": curated,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    fields = [
        "id", "start_s", "end_s", "duration_s", "speech_class",
        "global_hard_excluded", "face_structurally_usable",
        "face_eligible", "face_weight", "head_eligible", "head_weight",
        "body_support_eligible", "body_support_weight",
        "head_pose_quality", "body_pose_quality", "left_hand_pose_quality", "right_hand_pose_quality",
        "accepted_facial_frames", "accepted_frame_ratio", "hard_facial_suspect_frames", "temporal_review_frames",
        "mean_face_point_presence", "mean_landmark_confidence",
    ]
    with args.output_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for u in curated:
            rr = u["retrieval_roles"]
            pq = u["pose_quality"]
            fq = u["facial_quality"]
            w.writerow({
                "id": u["id"],
                "start_s": u["start_s"],
                "end_s": u["end_s"],
                "duration_s": u["duration_s"],
                "speech_class": u["speech_class"],
                "global_hard_excluded": u["global_hard_excluded"],
                "face_structurally_usable": u["face_structurally_usable"],
                "face_eligible": rr["face"]["enabled"],
                "face_weight": rr["face"]["weight"],
                "head_eligible": rr["head"]["enabled"],
                "head_weight": rr["head"]["weight"],
                "body_support_eligible": rr["body_support"]["enabled"],
                "body_support_weight": rr["body_support"]["weight"],
                "head_pose_quality": pq["head"],
                "body_pose_quality": pq["body"],
                "left_hand_pose_quality": pq["left_hand"],
                "right_hand_pose_quality": pq["right_hand"],
                "accepted_facial_frames": fq["frames_accepted"],
                "accepted_frame_ratio": fq["accepted_frame_ratio"],
                "hard_facial_suspect_frames": fq["hard_suspect_frames"],
                "temporal_review_frames": fq["temporal_review_frames"],
                "mean_face_point_presence": fq["mean_face_point_presence"],
                "mean_landmark_confidence": fq["mean_landmark_confidence"],
            })

    print("SECONDARY ROLE-AWARE CURATION")
    print("=============================")
    print(f"Source: {out['source_file']}")
    print(f"Units total: {out['units_total']}")
    print(f"Global hard excluded: {out['global_hard_excluded']}")
    print(f"Face eligible: {face_eligible_count}")
    print(f"Head eligible: {head_eligible_count}")
    print(f"Body-support eligible: {body_support_eligible_count}")
    print("Hands retrieval: disabled by source role")
    print("Generic whole-upper retrieval: disabled by source role")
    for role in ("face", "head", "body_support"):
        q = out["role_weight_quantiles"][role]
        print(f"{role} weight q10/median/q90: {q['q10']}/{q['median']}/{q['q90']}")
    print("Lowest face-quality units:")
    for u in out["lowest_face_quality_units"]:
        print(f"  {u['id']} weight={u['face_weight']} accepted={u['accepted_frame_ratio']} frames={u['frames_accepted']}")
    print(f"JSON: {args.output_json}")
    print(f"CSV: {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
