#!/usr/bin/env python3
"""Reusable facial/microexpression descriptors for COCO WholeBody 133 tracks.

Face landmarks are COCO WholeBody keypoints 23..90 (68 points, standard 68-point order).
The descriptor removes image translation, in-plane roll and scale by normalizing every
usable frame to the eye line before measuring internal facial deformation.

Stdlib only. No model inference is performed here.
"""

from __future__ import annotations

import json
import math
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

POSE_SCHEMA = "coco_wholebody_133"
FACE_OFFSET = 23
FACE_COUNT = 68
DEFAULT_CONF = 0.20

# Standard 68-point facial layout, expressed as face-relative indices.
JAW = tuple(range(0, 17))
BROWS = tuple(range(17, 27))
NOSE = tuple(range(27, 36))
EYE_A = tuple(range(36, 42))
EYE_B = tuple(range(42, 48))
EYES = tuple(range(36, 48))
MOUTH = tuple(range(48, 68))
EXPRESSION = tuple(range(17, 68))  # excludes jaw, which is more head-pose sensitive


@dataclass(frozen=True)
class FaceFrame:
    t: float
    keypoints: tuple[tuple[float | None, float | None, float | None], ...]


def _finite(v) -> bool:
    return v is not None and math.isfinite(float(v))


def load_pose_jsonl(path: Path, start_s: float | None = None, end_s: float | None = None) -> list[FaceFrame]:
    frames: list[FaceFrame] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("schema") != POSE_SCHEMA:
            raise ValueError(f"Pose schema mismatch at line {line_no}: {row.get('schema')!r}")
        raw = row.get("keypoints")
        if not isinstance(raw, list) or len(raw) != 133:
            raise ValueError(f"Expected 133 keypoints at line {line_no}")
        t = float(row["t"])
        if start_s is not None and t < start_s:
            continue
        if end_s is not None and t > end_s:
            continue
        pts = []
        for p in raw:
            if not isinstance(p, list) or len(p) < 3:
                pts.append((None, None, None))
                continue
            x, y, c = p[:3]
            pts.append((None if x is None else float(x), None if y is None else float(y), None if c is None else float(c)))
        frames.append(FaceFrame(t=t, keypoints=tuple(pts)))
    return frames


def _face_point(frame: FaceFrame, rel_idx: int, conf: float) -> tuple[float, float, float] | None:
    idx = FACE_OFFSET + rel_idx
    if idx >= len(frame.keypoints):
        return None
    x, y, c = frame.keypoints[idx]
    if not (_finite(x) and _finite(y) and _finite(c)) or float(c) < conf:
        return None
    return float(x), float(y), float(c)


def _mean_xy(frame: FaceFrame, ids: Sequence[int], conf: float) -> tuple[float, float] | None:
    pts = [_face_point(frame, i, conf) for i in ids]
    xy = [(p[0], p[1]) for p in pts if p is not None]
    if len(xy) < 2:
        return None
    return statistics.fmean(x for x, _ in xy), statistics.fmean(y for _, y in xy)


def normalize_face_frame(frame: FaceFrame, conf: float = DEFAULT_CONF):
    """Return eye-line normalized coordinates and confidence diagnostics for one frame.

    Coordinates are centered at the eye-line midpoint, rotated so the eye line is horizontal,
    and divided by inter-eye-center distance. This removes image translation, in-plane roll
    and scale. Perspective/yaw/pitch are intentionally not claimed to be removed.
    """
    eye_a = _mean_xy(frame, EYE_A, conf)
    eye_b = _mean_xy(frame, EYE_B, conf)
    if eye_a is None or eye_b is None:
        return None
    vx, vy = eye_b[0] - eye_a[0], eye_b[1] - eye_a[1]
    scale = math.hypot(vx, vy)
    if scale <= 1e-8:
        return None
    cx, cy = (eye_a[0] + eye_b[0]) * 0.5, (eye_a[1] + eye_b[1]) * 0.5
    angle = math.atan2(vy, vx)
    ca, sa = math.cos(angle), math.sin(angle)

    coords: dict[int, tuple[float, float]] = {}
    confs: list[float] = []
    present = 0
    for rel in range(FACE_COUNT):
        p = _face_point(frame, rel, conf)
        if p is None:
            continue
        x, y, c = p
        dx, dy = x - cx, y - cy
        # rotate by -angle, then scale by inter-eye distance
        nx = (dx * ca + dy * sa) / scale
        ny = (-dx * sa + dy * ca) / scale
        coords[rel] = (nx, ny)
        confs.append(c)
        present += 1

    if not coords:
        return None
    return {
        "t": frame.t,
        "coords": coords,
        "mean_confidence": statistics.fmean(confs) if confs else 0.0,
        "presence_ratio": present / FACE_COUNT,
        "intereye_scale_image_norm": scale,
    }


def _shape_distance(a: dict[int, tuple[float, float]], b: dict[int, tuple[float, float]], ids: Sequence[int], min_common: int = 2) -> float | None:
    common = [i for i in ids if i in a and i in b]
    if len(common) < min_common:
        return None
    dsq = []
    for i in common:
        dx = b[i][0] - a[i][0]
        dy = b[i][1] - a[i][1]
        dsq.append(dx * dx + dy * dy)
    return math.sqrt(statistics.fmean(dsq))


def shape_activity(norm_frames: Sequence[dict], ids: Sequence[int], min_common: int = 2) -> dict[str, float] | None:
    if len(norm_frames) < 2:
        return None
    speeds: list[float] = []
    for a, b in zip(norm_frames, norm_frames[1:]):
        dt = float(b["t"]) - float(a["t"])
        if dt <= 1e-8:
            continue
        d = _shape_distance(a["coords"], b["coords"], ids, min_common=min_common)
        if d is not None:
            speeds.append(d / dt)
    net = _shape_distance(norm_frames[0]["coords"], norm_frames[-1]["coords"], ids, min_common=min_common)
    if not speeds and net is None:
        return None
    return {
        "mean_speed_norm_s": round(statistics.fmean(speeds) if speeds else 0.0, 6),
        "peak_speed_norm_s": round(max(speeds) if speeds else 0.0, 6),
        "net_displacement_norm": round(net or 0.0, 6),
    }


def _coord(coords: dict[int, tuple[float, float]], idx: int):
    return coords.get(idx)


def _pair_distance(coords: dict[int, tuple[float, float]], a: int, b: int) -> float | None:
    pa, pb = _coord(coords, a), _coord(coords, b)
    if pa is None or pb is None:
        return None
    return math.hypot(pa[0] - pb[0], pa[1] - pb[1])


def _mean_point(coords: dict[int, tuple[float, float]], ids: Sequence[int]):
    pts = [coords[i] for i in ids if i in coords]
    if not pts:
        return None
    return statistics.fmean(p[0] for p in pts), statistics.fmean(p[1] for p in pts)


def facial_signals(coords: dict[int, tuple[float, float]]) -> dict[str, float | None]:
    # Standard 68-point indices. Values are already normalized by inter-eye distance.
    mouth_open = _pair_distance(coords, 62, 66)

    eye_pairs = ((37, 41), (38, 40), (43, 47), (44, 46))
    eye_vals = [v for v in (_pair_distance(coords, a, b) for a, b in eye_pairs) if v is not None]
    eye_open = statistics.fmean(eye_vals) if eye_vals else None

    brow_a = _mean_point(coords, range(17, 22))
    brow_b = _mean_point(coords, range(22, 27))
    eye_a = _mean_point(coords, EYE_A)
    eye_b = _mean_point(coords, EYE_B)
    brow_eye_vals = []
    if brow_a is not None and eye_a is not None:
        brow_eye_vals.append(abs(eye_a[1] - brow_a[1]))
    if brow_b is not None and eye_b is not None:
        brow_eye_vals.append(abs(eye_b[1] - brow_b[1]))
    brow_eye = statistics.fmean(brow_eye_vals) if brow_eye_vals else None

    mouth_width = _pair_distance(coords, 48, 54)

    return {
        "mouth_open": mouth_open,
        "mouth_width": mouth_width,
        "eye_open": eye_open,
        "brow_eye_distance": brow_eye,
    }


def _signal_stats(values: Iterable[float | None]):
    vals = [float(v) for v in values if v is not None and math.isfinite(float(v))]
    if not vals:
        return None
    lo, hi = min(vals), max(vals)
    return {
        "mean": round(statistics.fmean(vals), 6),
        "min": round(lo, 6),
        "max": round(hi, 6),
        "range": round(hi - lo, 6),
    }


def summarize_facial_frames(frames: Sequence[FaceFrame], conf: float = DEFAULT_CONF) -> dict:
    normalized = []
    raw_face_confs: list[float] = []
    raw_presence: list[float] = []

    for frame in frames:
        present = []
        for rel in range(FACE_COUNT):
            p = _face_point(frame, rel, conf)
            if p is not None:
                present.append(p[2])
        raw_presence.append(len(present) / FACE_COUNT)
        raw_face_confs.extend(present)
        nf = normalize_face_frame(frame, conf=conf)
        if nf is not None:
            normalized.append(nf)

    sig_rows = [facial_signals(nf["coords"]) for nf in normalized]
    total = len(frames)
    return {
        "landmark_schema": "coco_wholebody_face68_23_90",
        "confidence_floor": conf,
        "normalization": "eye_line_midpoint + remove_inplane_roll + intereye_scale",
        "frames_total": total,
        "frames_normalized": len(normalized),
        "normalized_frame_ratio": round(len(normalized) / total, 6) if total else 0.0,
        "mean_face_point_presence": round(statistics.fmean(raw_presence), 6) if raw_presence else 0.0,
        "mean_landmark_confidence": round(statistics.fmean(raw_face_confs), 6) if raw_face_confs else 0.0,
        "deformation": shape_activity(normalized, EXPRESSION, min_common=8),
        "regions": {
            "brows": shape_activity(normalized, BROWS, min_common=3),
            "eyes": shape_activity(normalized, EYES, min_common=4),
            "mouth": shape_activity(normalized, MOUTH, min_common=4),
        },
        "signals": {
            "mouth_open": _signal_stats(row["mouth_open"] for row in sig_rows),
            "mouth_width": _signal_stats(row["mouth_width"] for row in sig_rows),
            "eye_open": _signal_stats(row["eye_open"] for row in sig_rows),
            "brow_eye_distance": _signal_stats(row["brow_eye_distance"] for row in sig_rows),
        },
    }
