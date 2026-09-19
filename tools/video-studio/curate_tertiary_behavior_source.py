#!/usr/bin/env python3
"""Role-aware curation for SIENA_BRUTO.

No model inference. Consumes the already-generated inventory analysis plus reviewed
source annotations. SIENA is curated as alternate posture/head/coarse-arm vocabulary.
Hands and generic whole-upper retrieval stay disabled unless a later explicit review
changes that policy.
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


def overlap(a0: float, a1: float, b0: float, b1: float) -> bool:
    return max(a0, b0) < min(a1, b1)


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", type=Path, required=True)
    ap.add_argument("--annotations", type=Path, required=True)
    ap.add_argument("--output-json", type=Path, required=True)
    ap.add_argument("--output-csv", type=Path, required=True)
    args = ap.parse_args()

    for label, path in (("analysis", args.analysis), ("annotations", args.annotations)):
        if not path.is_file():
            raise SystemExit(f"Missing {label}: {path}")

    analysis = json.loads(args.analysis.read_text(encoding="utf-8-sig"))
    ann = json.loads(args.annotations.read_text(encoding="utf-8-sig"))
    units = analysis.get("units_detail") or []
    exclusions = ann.get("manual_exclusions") or []

    curated = []
    hard_count = 0
    head_count = 0
    posture_count = 0
    arm_count = 0

    for u in units:
        st = float(u["start_s"])
        en = float(u["end_s"])
        matched = [x for x in exclusions if overlap(st, en, float(x["start_s"]), float(x["end_s"]))]
        hard = bool(matched)
        reasons = []
        for x in matched:
            for reason in x.get("reasons") or []:
                if reason not in reasons:
                    reasons.append(reason)

        head_q = effective(u.get("head_confident_ratio"), u.get("head_frame_presence"))
        body_q = effective(u.get("body_confident_ratio"), u.get("body_frame_presence"))
        left_q = effective(u.get("left_hand_confident_ratio"), u.get("left_hand_frame_presence"))
        right_q = effective(u.get("right_hand_confident_ratio"), u.get("right_hand_frame_presence"))

        head_enabled = (not hard) and head_q > 0.0
        posture_enabled = (not hard) and body_q > 0.0
        arm_enabled = (not hard) and body_q > 0.0

        row = {
            **u,
            "global_hard_excluded": hard,
            "global_exclusion_reasons": reasons,
            "source_role": ann.get("source_role"),
            "pose_quality": {
                "head": round(head_q, 6),
                "body": round(body_q, 6),
                "left_hand": round(left_q, 6),
                "right_hand": round(right_q, 6),
            },
            "retrieval_roles": {
                "head": {"enabled": head_enabled, "weight": round(head_q if head_enabled else 0.0, 6)},
                "posture": {"enabled": posture_enabled, "weight": round(body_q if posture_enabled else 0.0, 6)},
                "coarse_arm": {"enabled": arm_enabled, "weight": round(body_q if arm_enabled else 0.0, 6)},
                "left_hand": {"enabled": False, "weight": 0.0},
                "right_hand": {"enabled": False, "weight": 0.0},
                "both_hands": {"enabled": False, "weight": 0.0},
                "generic_whole_upper": {"enabled": False, "weight": 0.0},
            },
        }
        curated.append(row)
        hard_count += int(hard)
        head_count += int(head_enabled)
        posture_count += int(posture_enabled)
        arm_count += int(arm_enabled)

    def enabled_weights(role: str):
        return [
            float(u["retrieval_roles"][role]["weight"])
            for u in curated
            if u["retrieval_roles"][role]["enabled"]
        ]

    def qs(values):
        return {
            "q10": percentile(values, 0.10),
            "median": percentile(values, 0.50),
            "q90": percentile(values, 0.90),
        }

    out = {
        "schema": "behavior-role-curated-inventory/v1",
        "source_file": ann.get("source_file"),
        "source_role": ann.get("source_role"),
        "analysis_source": str(args.analysis.resolve()),
        "annotations_source": str(args.annotations.resolve()),
        "retrieval_policy": ann.get("retrieval_policy"),
        "quality_policy": ann.get("quality_policy"),
        "manual_exclusions": exclusions,
        "units_total": len(curated),
        "global_hard_excluded": hard_count,
        "role_counts": {
            "head_eligible": head_count,
            "posture_eligible": posture_count,
            "coarse_arm_eligible": arm_count,
            "hands_retrieval_enabled": 0,
            "generic_whole_upper_enabled": 0,
        },
        "role_weight_quantiles": {
            "head": qs(enabled_weights("head")),
            "posture": qs(enabled_weights("posture")),
            "coarse_arm": qs(enabled_weights("coarse_arm")),
        },
        "units": curated,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    fields = [
        "id", "start_s", "end_s", "duration_s", "speech_class",
        "global_hard_excluded", "exclusion_reasons",
        "head_eligible", "head_weight", "posture_eligible", "posture_weight",
        "coarse_arm_eligible", "coarse_arm_weight",
        "head_pose_quality", "body_pose_quality", "left_hand_pose_quality", "right_hand_pose_quality",
        "head_speed", "body_speed", "hand_speed", "motion_mean", "entry_score", "exit_score",
    ]
    with args.output_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for u in curated:
            rr = u["retrieval_roles"]
            pq = u["pose_quality"]
            w.writerow({
                "id": u["id"],
                "start_s": u["start_s"],
                "end_s": u["end_s"],
                "duration_s": u["duration_s"],
                "speech_class": u["speech_class"],
                "global_hard_excluded": u["global_hard_excluded"],
                "exclusion_reasons": ";".join(u["global_exclusion_reasons"]),
                "head_eligible": rr["head"]["enabled"],
                "head_weight": rr["head"]["weight"],
                "posture_eligible": rr["posture"]["enabled"],
                "posture_weight": rr["posture"]["weight"],
                "coarse_arm_eligible": rr["coarse_arm"]["enabled"],
                "coarse_arm_weight": rr["coarse_arm"]["weight"],
                "head_pose_quality": pq["head"],
                "body_pose_quality": pq["body"],
                "left_hand_pose_quality": pq["left_hand"],
                "right_hand_pose_quality": pq["right_hand"],
                "head_speed": u.get("head_speed"),
                "body_speed": u.get("body_speed"),
                "hand_speed": u.get("hand_speed"),
                "motion_mean": u.get("motion_mean"),
                "entry_score": u.get("entry_score"),
                "exit_score": u.get("exit_score"),
            })

    print("SIENA ROLE-AWARE CURATION")
    print("=========================")
    print(f"Source: {out['source_file']}")
    print(f"Units total: {out['units_total']}")
    print(f"Global hard excluded: {hard_count}")
    print(f"Head eligible: {head_count}")
    print(f"Posture eligible: {posture_count}")
    print(f"Coarse-arm eligible: {arm_count}")
    print("Hands retrieval: disabled by source role")
    print("Generic whole-upper retrieval: disabled by source role")
    for x in exclusions:
        print(f"Manual exclusion: {x['start_s']}-{x['end_s']} s / {','.join(x.get('reasons') or [])}")
    for role in ("head", "posture", "coarse_arm"):
        q = out["role_weight_quantiles"][role]
        print(f"{role} weight q10/median/q90: {q['q10']}/{q['median']}/{q['q90']}")
    print(f"JSON: {args.output_json}")
    print(f"CSV: {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
