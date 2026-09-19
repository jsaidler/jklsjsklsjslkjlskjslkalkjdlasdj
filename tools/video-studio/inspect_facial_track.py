#!/usr/bin/env python3
"""Inspect normalized facial descriptors on a COCO WholeBody 133 JSONL track.

No model inference. Reads an existing pose track and reports facial coverage,
normalized deformation, and region/signal statistics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from facial_descriptors import DEFAULT_CONF, load_pose_jsonl, summarize_facial_frames


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pose-track", type=Path, required=True)
    ap.add_argument("--start", type=float)
    ap.add_argument("--duration", type=float)
    ap.add_argument("--confidence", type=float, default=DEFAULT_CONF)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    if not args.pose_track.is_file():
        raise SystemExit(f"Pose track missing: {args.pose_track}")
    end = None if args.duration is None or args.start is None else args.start + args.duration
    frames = load_pose_jsonl(args.pose_track, start_s=args.start, end_s=end)
    if not frames:
        raise SystemExit("No pose frames in requested interval.")

    summary = summarize_facial_frames(frames, conf=args.confidence)
    summary["pose_track"] = str(args.pose_track.resolve())
    summary["start_s"] = args.start
    summary["end_s"] = end
    summary["first_frame_s"] = frames[0].t
    summary["last_frame_s"] = frames[-1].t

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("FACIAL TRACK INSPECTION")
    print("=======================")
    print(f"Frames: {summary['frames_total']} / normalized: {summary['frames_normalized']} ({summary['normalized_frame_ratio']})")
    print(f"Mean face-point presence: {summary['mean_face_point_presence']}")
    print(f"Mean landmark confidence: {summary['mean_landmark_confidence']}")
    print(f"Normalization: {summary['normalization']}")
    deformation = summary.get("deformation") or {}
    print("Expression deformation mean/peak/net: " + "/".join(str(deformation.get(k)) for k in ("mean_speed_norm_s","peak_speed_norm_s","net_displacement_norm")))
    for region in ("brows", "eyes", "mouth"):
        r = (summary.get("regions") or {}).get(region) or {}
        print(f"{region} mean/peak/net: " + "/".join(str(r.get(k)) for k in ("mean_speed_norm_s","peak_speed_norm_s","net_displacement_norm")))
    for signal in ("mouth_open", "mouth_width", "eye_open", "brow_eye_distance"):
        s = (summary.get("signals") or {}).get(signal)
        if s:
            print(f"{signal} mean/range: {s['mean']}/{s['range']}")
        else:
            print(f"{signal}: unavailable")
    if args.output:
        print(f"JSON: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
