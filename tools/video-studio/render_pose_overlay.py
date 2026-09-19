#!/usr/bin/env python3
"""Render a visual QA overlay for a normalized COCO WholeBody 133 JSONL track.

This tool does not run DWPose or any renderer. It reads an already-generated
pose JSONL and samples the corresponding source-video frames at the stored
timestamps, drawing body, face and hand landmarks for human inspection.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path


class OverlayError(RuntimeError):
    pass


BODY_EDGES = [
    (0, 1), (0, 2), (1, 3), (2, 4),
    (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),
    (5, 11), (6, 12), (11, 12),
    (11, 13), (13, 15), (12, 14), (14, 16),
    (15, 17), (15, 18), (16, 20), (16, 21),
    (17, 19), (18, 19), (20, 22), (21, 22),
]

HAND_LOCAL_EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20),
]


def load_track(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                raise OverlayError(f"Invalid JSONL at line {line_no}: {exc}") from exc
            if rec.get("schema") != "coco_wholebody_133":
                raise OverlayError(f"Unsupported schema at line {line_no}: {rec.get('schema')}")
            kp = rec.get("keypoints")
            if not isinstance(kp, list) or len(kp) != 133:
                raise OverlayError(f"Expected 133 keypoints at line {line_no}")
            records.append(rec)
    if not records:
        raise OverlayError("Pose track is empty")
    return records


def point_xy(kp, width: int, height: int, min_score: float):
    x, y, score = kp
    if x is None or y is None:
        return None
    try:
        xf, yf, sf = float(x), float(y), float(score)
    except (TypeError, ValueError):
        return None
    if not (math.isfinite(xf) and math.isfinite(yf) and math.isfinite(sf)):
        return None
    if sf < min_score:
        return None
    return int(round(xf * width)), int(round(yf * height))


def draw_edge(cv2, frame, keypoints, a: int, b: int, min_score: float, thickness: int = 2):
    h, w = frame.shape[:2]
    pa = point_xy(keypoints[a], w, h, min_score)
    pb = point_xy(keypoints[b], w, h, min_score)
    if pa is not None and pb is not None:
        cv2.line(frame, pa, pb, (255, 255, 255), thickness, cv2.LINE_AA)


def draw_point(cv2, frame, kp, min_score: float, radius: int):
    h, w = frame.shape[:2]
    p = point_xy(kp, w, h, min_score)
    if p is not None:
        cv2.circle(frame, p, radius, (255, 255, 255), -1, cv2.LINE_AA)


def draw_hand(cv2, frame, keypoints, offset: int, min_score: float):
    for a, b in HAND_LOCAL_EDGES:
        draw_edge(cv2, frame, keypoints, offset + a, offset + b, min_score, 1)
    for idx in range(offset, offset + 21):
        draw_point(cv2, frame, keypoints[idx], min_score, 2)


def ffmpeg_path(name: str) -> str:
    found = shutil.which(name)
    if not found:
        raise OverlayError(f"Executable not found: {name}")
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--track", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--fps", type=float, default=6.0)
    ap.add_argument("--long-side", type=int, default=960)
    ap.add_argument("--min-score", type=float, default=0.05)
    ap.add_argument("--ffmpeg", default="ffmpeg")
    args = ap.parse_args()

    if not args.source.is_file():
        raise OverlayError(f"Missing source video: {args.source}")
    if not args.track.is_file():
        raise OverlayError(f"Missing pose track: {args.track}")
    if args.fps <= 0:
        raise OverlayError("--fps must be > 0")

    records = load_track(args.track)
    try:
        import cv2
    except Exception as exc:
        raise OverlayError(f"OpenCV import failed: {exc}") from exc

    cap = cv2.VideoCapture(str(args.source))
    if not cap.isOpened():
        raise OverlayError(f"Could not open source video: {args.source}")
    src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if src_w <= 0 or src_h <= 0:
        raise OverlayError("Could not read source dimensions")
    if src_w >= src_h:
        out_w = args.long_side
        out_h = max(2, int(round(src_h * args.long_side / src_w / 2.0)) * 2)
    else:
        out_h = args.long_side
        out_w = max(2, int(round(src_w * args.long_side / src_h / 2.0)) * 2)

    ffmpeg = ffmpeg_path(args.ffmpeg)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "bgr24",
        "-s", f"{out_w}x{out_h}", "-r", f"{args.fps:g}", "-i", "pipe:0",
        "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", str(args.output),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdin is not None

    rendered = 0
    try:
        for rec in records:
            t = float(rec["t"])
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000.0)
            ok, frame = cap.read()
            if not ok or frame is None:
                raise OverlayError(f"Could not decode source frame at t={t:.6f}")
            frame = cv2.resize(frame, (out_w, out_h), interpolation=cv2.INTER_AREA)
            kp = rec["keypoints"]

            for a, b in BODY_EDGES:
                draw_edge(cv2, frame, kp, a, b, args.min_score, 2)
            for idx in range(23):
                draw_point(cv2, frame, kp[idx], args.min_score, 3)
            for idx in range(23, 91):
                draw_point(cv2, frame, kp[idx], args.min_score, 1)
            draw_hand(cv2, frame, kp, 91, args.min_score)
            draw_hand(cv2, frame, kp, 112, args.min_score)

            label = f"t={t:.3f}s  fallback={bool(rec.get('detector_fallback'))}"
            cv2.putText(frame, label, (16, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            proc.stdin.write(frame.tobytes())
            rendered += 1
    finally:
        cap.release()
        try:
            proc.stdin.close()
        except Exception:
            pass

    stderr = proc.stderr.read().decode("utf-8", "replace") if proc.stderr is not None else ""
    rc = proc.wait()
    if rc != 0:
        raise OverlayError("ffmpeg overlay encode failed: " + stderr.strip())

    print(json.dumps({
        "track": str(args.track.resolve()),
        "output": str(args.output.resolve()),
        "frames": rendered,
        "fps": args.fps,
        "width": out_w,
        "height": out_h,
        "min_score": args.min_score,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OverlayError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
