#!/usr/bin/env python3
"""Build a contact sheet of clean-segment candidates from the primary behavior video.

This is a visual sampling helper only. It does not run DWPose and does not run any renderer.
Each candidate row shows start/mid/end frames across a 5-second window so object occlusion
or framing problems are visible before spending pose-inference time.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path


def find_exe(name: str) -> str:
    found = shutil.which(name)
    if not found:
        raise RuntimeError(f"Executable not found: {name}")
    return found


def ffprobe_duration(source: Path, ffprobe: str) -> float:
    run = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(source)],
        capture_output=True,
        text=True,
    )
    if run.returncode:
        raise RuntimeError(run.stderr.strip() or "ffprobe failed")
    return float(run.stdout.strip())


def extract_frame(source: Path, t: float, ffmpeg: str, cv2, np):
    run = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{t:.3f}",
            "-i",
            str(source),
            "-frames:v",
            "1",
            "-vf",
            "scale=480:-2:flags=area",
            "-f",
            "image2pipe",
            "-vcodec",
            "mjpeg",
            "pipe:1",
        ],
        capture_output=True,
    )
    if run.returncode or not run.stdout:
        raise RuntimeError(run.stderr.decode("utf-8", "replace").strip() or f"ffmpeg frame extraction failed at {t:.3f}s")
    arr = np.frombuffer(run.stdout, dtype=np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise RuntimeError(f"Could not decode sampled frame at {t:.3f}s")
    return frame


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--window", type=float, default=5.0)
    ap.add_argument("--candidates", type=int, default=8)
    ap.add_argument("--margin", type=float, default=10.0)
    ap.add_argument("--ffmpeg", default="ffmpeg")
    ap.add_argument("--ffprobe", default="ffprobe")
    args = ap.parse_args()

    if args.window <= 0:
        raise RuntimeError("--window must be > 0")
    if args.candidates < 2:
        raise RuntimeError("--candidates must be >= 2")

    source = args.source.resolve()
    if not source.is_file():
        raise RuntimeError(f"Source missing: {source}")

    try:
        import cv2
        import numpy as np
    except Exception as exc:
        raise RuntimeError(f"OpenCV/NumPy import failed: {exc}") from exc

    ffmpeg = find_exe(args.ffmpeg)
    ffprobe = find_exe(args.ffprobe)
    duration = ffprobe_duration(source, ffprobe)

    first = max(0.0, args.margin)
    last = max(first, duration - args.margin - args.window)
    if args.candidates == 1:
        starts = [first]
    else:
        starts = [first + (last - first) * i / (args.candidates - 1) for i in range(args.candidates)]

    rows = []
    manifest = []
    font = cv2.FONT_HERSHEY_SIMPLEX

    for idx, start in enumerate(starts, start=1):
        times = [start, start + args.window * 0.5, start + args.window]
        tiles = []
        for j, t in enumerate(times):
            frame = extract_frame(source, min(t, duration - 0.01), ffmpeg, cv2, np)
            h, w = frame.shape[:2]
            target_w = 480
            scale = target_w / float(w)
            frame = cv2.resize(frame, (target_w, max(2, int(round(h * scale)))))
            label = f"C{idx}  t={t:.1f}s" if j == 0 else f"t={t:.1f}s"
            cv2.rectangle(frame, (0, 0), (220, 38), (0, 0, 0), -1)
            cv2.putText(frame, label, (10, 27), font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            tiles.append(frame)
        row_h = min(tile.shape[0] for tile in tiles)
        norm = [cv2.resize(tile, (480, row_h)) for tile in tiles]
        row = np.hstack(norm)
        rows.append(row)
        manifest.append({"candidate": idx, "start_s": round(start, 3), "mid_s": round(start + args.window * 0.5, 3), "end_s": round(start + args.window, 3)})

    width = max(row.shape[1] for row in rows)
    rows = [cv2.resize(row, (width, row.shape[0])) for row in rows]
    sheet = np.vstack(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(args.output), sheet):
        raise RuntimeError(f"Could not write contact sheet: {args.output}")

    manifest_path = args.output.with_suffix(args.output.suffix + ".json")
    manifest_path.write_text(
        json.dumps(
            {
                "source": str(source),
                "duration_s": duration,
                "window_s": args.window,
                "candidates": manifest,
                "output": str(args.output),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(json.dumps({"output": str(args.output), "manifest": str(manifest_path), "candidates": manifest}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
