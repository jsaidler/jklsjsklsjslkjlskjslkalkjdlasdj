#!/usr/bin/env python3
"""Render a compact visual review sheet for selected behavior motion units.

Uses only the original source video + manifest + inventory analysis. It does not
run DWPose, diffusion, training or any remote service.
"""
from __future__ import annotations

import argparse, json, math, sys
from pathlib import Path

class ReviewError(RuntimeError):
    pass

def fit_frame(cv2, frame, width, height):
    h, w = frame.shape[:2]
    if w <= 0 or h <= 0:
        raise ReviewError("Invalid decoded frame size")
    scale = min(width / w, height / h)
    nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    resized = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_AREA)
    canvas = __import__("numpy").zeros((height, width, 3), dtype=frame.dtype)
    x = (width - nw) // 2; y = (height - nh) // 2
    canvas[y:y+nh, x:x+nw] = resized
    return canvas

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--analysis", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--columns", type=int, default=4)
    args = ap.parse_args()

    try:
        import cv2, numpy as np
    except Exception as exc:
        raise ReviewError(f"OpenCV/NumPy import failed: {exc}") from exc

    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    analysis = json.loads(args.analysis.read_text(encoding="utf-8-sig"))
    unit_map = {u["id"]: u for u in manifest.get("motion_units") or []}
    detail_map = {u["id"]: u for u in analysis.get("units_detail") or []}
    ids = analysis.get("selected_review_unit_ids") or []
    if not ids:
        raise ReviewError("No selected review units in analysis")

    cap = cv2.VideoCapture(str(args.source))
    if not cap.isOpened():
        raise ReviewError(f"Could not open source video: {args.source}")

    cols = max(1, args.columns)
    rows = int(math.ceil(len(ids) / cols))
    cell_w, cell_h = 430, 300
    header_h = 58
    frame_h = cell_h - header_h
    thumb_w = cell_w // 3
    sheet = np.zeros((rows * cell_h, cols * cell_w, 3), dtype=np.uint8)

    for idx, uid in enumerate(ids):
        unit = unit_map.get(uid)
        detail = detail_map.get(uid)
        if not unit or not detail:
            continue
        r, c = divmod(idx, cols)
        x0, y0 = c * cell_w, r * cell_h
        st, en = float(unit["start_s"]), float(unit["end_s"])
        pad = min(0.12, max(0.0, (en - st) * 0.08))
        times = [st + pad, (st + en) * 0.5, max(st, en - pad)]
        for j, t in enumerate(times):
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000.0)
            ok, frame = cap.read()
            if not ok or frame is None:
                continue
            thumb = fit_frame(cv2, frame, thumb_w, frame_h)
            xs = x0 + j * thumb_w
            sheet[y0 + header_h:y0 + cell_h, xs:xs + thumb_w] = thumb

        tags = ",".join(detail.get("review_tags") or []) or "representative"
        line1 = f"{uid}  {st:.1f}-{en:.1f}s  {detail.get('speech_class','?')}"
        line2 = f"hand={detail.get('hand_speed',0):.3f} body={detail.get('body_speed',0):.3f} cov={detail.get('min_upper_confident_ratio',0):.2f}"
        line3 = tags[:62]
        for k, text in enumerate((line1, line2, line3)):
            cv2.putText(sheet, text, (x0 + 6, y0 + 17 + 17*k), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255,255,255), 1, cv2.LINE_AA)

    cap.release()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(args.output), sheet, [int(cv2.IMWRITE_JPEG_QUALITY), 92]):
        raise ReviewError(f"Could not write {args.output}")

    print("BEHAVIOR INVENTORY VISUAL REVIEW")
    print("================================")
    print(f"Selected units: {len(ids)}")
    print(f"Sheet: {args.output}")
    print("Each cell shows start / midpoint / end of one motion unit.")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReviewError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
