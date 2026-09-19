#!/usr/bin/env python3
"""Curate a behavior inventory using manual exclusions and continuous pose reliability.

No renderer or pose inference occurs here. The tool consumes the already-generated
inventory_analysis.json plus a source annotation file and emits source-preserving
curated JSON/CSV artifacts for later retrieval/library construction.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def overlap(a0: float, a1: float, b0: float, b1: float) -> bool:
    return max(a0, b0) < min(a1, b1)


def effective(confident_ratio: float | None, frame_presence: float | None) -> float:
    c = 0.0 if confident_ratio is None else float(confident_ratio)
    p = 0.0 if frame_presence is None else float(frame_presence)
    return max(0.0, min(1.0, c * p))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", type=Path, required=True)
    ap.add_argument("--annotations", type=Path, required=True)
    ap.add_argument("--output-json", type=Path, required=True)
    ap.add_argument("--output-csv", type=Path, required=True)
    args = ap.parse_args()

    analysis = json.loads(args.analysis.read_text(encoding="utf-8"))
    ann = json.loads(args.annotations.read_text(encoding="utf-8"))
    units = analysis.get("units_detail") or []
    exclusions = ann.get("manual_exclusions") or []

    curated: list[dict[str, Any]] = []
    excluded = 0
    eligible = 0

    for u in units:
        st = float(u["start_s"])
        en = float(u["end_s"])
        matched = [x for x in exclusions if overlap(st, en, float(x["start_s"]), float(x["end_s"]))]
        hard_excluded = bool(matched)
        reasons: list[str] = []
        for x in matched:
            for r in x.get("reasons") or []:
                if r not in reasons:
                    reasons.append(r)

        hq = effective(u.get("head_confident_ratio"), u.get("head_frame_presence"))
        bq = effective(u.get("body_confident_ratio"), u.get("body_frame_presence"))
        lq = effective(u.get("left_hand_confident_ratio"), u.get("left_hand_frame_presence"))
        rq = effective(u.get("right_hand_confident_ratio"), u.get("right_hand_frame_presence"))
        both_hands = min(lq, rq)
        whole_upper = min(hq, bq, lq, rq)

        row = {
            **u,
            "eligible": not hard_excluded,
            "hard_excluded": hard_excluded,
            "exclusion_reasons": reasons,
            "quality_weights": {
                "head": round(hq, 6),
                "body": round(bq, 6),
                "left_hand": round(lq, 6),
                "right_hand": round(rq, 6),
                "both_hands": round(both_hands, 6),
                "whole_upper": round(whole_upper, 6),
            },
        }
        curated.append(row)
        if hard_excluded:
            excluded += 1
        else:
            eligible += 1

    out = {
        "schema": "behavior-curated-inventory/v1",
        "source_file": ann.get("source_file"),
        "source_role": ann.get("source_role"),
        "analysis_source": str(args.analysis),
        "annotations_source": str(args.annotations),
        "quality_policy": ann.get("quality_policy"),
        "units_total": len(curated),
        "units_eligible": eligible,
        "units_hard_excluded": excluded,
        "manual_exclusions": exclusions,
        "units": curated,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    fields = [
        "id", "start_s", "end_s", "duration_s", "speech_class", "eligible", "hard_excluded",
        "exclusion_reasons", "head_quality", "body_quality", "left_hand_quality",
        "right_hand_quality", "both_hands_quality", "whole_upper_quality", "review_tags",
        "hand_speed", "body_speed", "motion_mean", "entry_score", "exit_score",
    ]
    with args.output_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for u in curated:
            q = u["quality_weights"]
            w.writerow({
                "id": u["id"],
                "start_s": u["start_s"],
                "end_s": u["end_s"],
                "duration_s": u["duration_s"],
                "speech_class": u["speech_class"],
                "eligible": u["eligible"],
                "hard_excluded": u["hard_excluded"],
                "exclusion_reasons": ";".join(u["exclusion_reasons"]),
                "head_quality": q["head"],
                "body_quality": q["body"],
                "left_hand_quality": q["left_hand"],
                "right_hand_quality": q["right_hand"],
                "both_hands_quality": q["both_hands"],
                "whole_upper_quality": q["whole_upper"],
                "review_tags": ";".join(u.get("review_tags") or []),
                "hand_speed": u.get("hand_speed"),
                "body_speed": u.get("body_speed"),
                "motion_mean": u.get("motion_mean"),
                "entry_score": u.get("entry_score"),
                "exit_score": u.get("exit_score"),
            })

    print("BEHAVIOR INVENTORY CURATION")
    print("===========================")
    print(f"Source: {ann.get('source_file')}")
    print(f"Units total: {len(curated)}")
    print(f"Eligible: {eligible}")
    print(f"Hard excluded: {excluded}")
    if exclusions:
        for x in exclusions:
            print(f"Manual exclusion: {x['start_s']}-{x['end_s']} s / {','.join(x.get('reasons') or [])}")
    print(f"JSON: {args.output_json}")
    print(f"CSV: {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
