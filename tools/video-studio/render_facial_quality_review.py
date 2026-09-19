#!/usr/bin/env python3
"""Render a contact sheet for facial QA suspect timestamps.

No pose inference. Uses the original video plus facial-quality-audit/v1 JSON.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path


def find_exe(name: str) -> str:
    p = shutil.which(name)
    if not p:
        raise RuntimeError(f"Executable not found: {name}")
    return p


def extract_frame(source: Path, t: float, ffmpeg: str, cv2, np):
    run = subprocess.run(
        [ffmpeg, "-hide_banner", "-loglevel", "error", "-ss", f"{max(0.0,t):.3f}", "-i", str(source),
         "-frames:v", "1", "-vf", "scale=360:-2:flags=area", "-f", "image2pipe", "-vcodec", "mjpeg", "pipe:1"],
        capture_output=True,
    )
    if run.returncode or not run.stdout:
        raise RuntimeError(run.stderr.decode("utf-8", "replace").strip() or f"ffmpeg failed at {t:.3f}s")
    arr = np.frombuffer(run.stdout, dtype=np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise RuntimeError(f"Could not decode frame at {t:.3f}s")
    return frame


def short_reason(reasons: list[str]) -> str:
    aliases = {
        "normalization_failed": "NORM_FAIL",
        "log_intereye_scale:low": "EYE_SCALE_LOW",
        "log_intereye_scale:high": "EYE_SCALE_HIGH",
        "face_extent:low": "EXTENT_LOW",
        "face_extent:high": "EXTENT_HIGH",
        "mouth_open:low": "MOUTH_OPEN_LOW",
        "mouth_open:high": "MOUTH_OPEN_HIGH",
        "mouth_width:low": "MOUTH_WIDTH_LOW",
        "mouth_width:high": "MOUTH_WIDTH_HIGH",
        "eye_open:low": "EYE_OPEN_LOW",
        "eye_open:high": "EYE_OPEN_HIGH",
        "brow_eye_distance:low": "BROW_EYE_LOW",
        "brow_eye_distance:high": "BROW_EYE_HIGH",
        "expression_step:high": "TEMP_JUMP",
    }
    return ",".join(aliases.get(x, x) for x in reasons)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--audit", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--max-items", type=int, default=24)
    ap.add_argument("--ffmpeg", default="ffmpeg")
    args = ap.parse_args()

    if not args.source.is_file():
        raise RuntimeError(f"Source missing: {args.source}")
    if not args.audit.is_file():
        raise RuntimeError(f"Audit missing: {args.audit}")

    try:
        import cv2
        import numpy as np
    except Exception as exc:
        raise RuntimeError(f"OpenCV/NumPy import failed: {exc}") from exc

    audit = json.loads(args.audit.read_text(encoding="utf-8-sig"))
    suspects = list(audit.get("suspect_frames") or [])[: max(1, args.max_items)]
    if not suspects:
        raise RuntimeError("Audit contains no suspect frames to render.")

    ffmpeg = find_exe(args.ffmpeg)
    tiles = []
    font = cv2.FONT_HERSHEY_SIMPLEX
    for item in suspects:
        t = float(item["t"])
        frame = extract_frame(args.source, t, ffmpeg, cv2, np)
        h, w = frame.shape[:2]
        band_h = 84
        canvas = np.zeros((h + band_h, w, 3), dtype=np.uint8)
        canvas[band_h:, :] = frame
        hard = "HARD" if item.get("hard_suspect") else "REVIEW"
        cv2.putText(canvas, f"t={t:.3f}s  {hard}", (8, 24), font, 0.62, (255,255,255), 2, cv2.LINE_AA)
        reason = short_reason(list(item.get("reasons") or []))
        cv2.putText(canvas, reason[:52], (8, 50), font, 0.44, (255,255,255), 1, cv2.LINE_AA)
        cv2.putText(canvas, f"severity_iqr={item.get('severity_iqr',0)}", (8, 72), font, 0.42, (255,255,255), 1, cv2.LINE_AA)
        tiles.append(canvas)

    cols = min(4, len(tiles))
    rows = int(math.ceil(len(tiles) / cols))
    th = max(t.shape[0] for t in tiles)
    tw = max(t.shape[1] for t in tiles)
    sheet = np.zeros((rows * th, cols * tw, 3), dtype=np.uint8)
    for i, tile in enumerate(tiles):
        r, c = divmod(i, cols)
        if tile.shape[:2] != (th, tw):
            tile = cv2.resize(tile, (tw, th))
        sheet[r*th:(r+1)*th, c*tw:(c+1)*tw] = tile

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(args.output), sheet):
        raise RuntimeError(f"Could not write: {args.output}")
    print(json.dumps({"output": str(args.output), "items": len(tiles), "total_suspects": len(audit.get("suspect_frames") or [])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
