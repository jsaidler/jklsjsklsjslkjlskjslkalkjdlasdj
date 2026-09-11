#!/usr/bin/env python3
"""Runner66 deterministic repeated-element decomposition gate.

This gate consumes Runner65's semantically correct parent/leaf localization and
splits an oversized repeated structure (for example one full door leaf) into an
atomic repeated element (one plank) using persistent image structure.

No generative model is run. No user box/mask is accepted.

Current proven case:
    parent door -> left door leaf -> vertical seam projection -> one plank

The implementation is intentionally generic around an oriented repeated element.
The same projection/splitting contract can later be reused for slats, bars, ribs,
boards, repeated armor plates, fence elements, etc.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--runner65-dir", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--peak-relative-threshold", type=float, default=0.45)
    return p.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def bbox_from_mask(mask: np.ndarray) -> list[int]:
    ys, xs = np.where(mask > 0)
    if xs.size == 0:
        raise RuntimeError("input mask is empty")
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def moving_average(values: np.ndarray, radius: int = 1) -> np.ndarray:
    width = radius * 2 + 1
    kernel = np.ones(width, dtype=np.float64) / float(width)
    return np.convolve(values.astype(np.float64), kernel, mode="same")


def vertical_seam_profile(gray: np.ndarray, mask: np.ndarray, box: list[int]) -> np.ndarray:
    x1, y1, x2, y2 = box
    roi = gray[y1:y2, x1:x2].astype(np.float64)
    m = mask[y1:y2, x1:x2] > 0
    if roi.shape[1] < 8 or roi.shape[0] < 16:
        raise RuntimeError("localized repeated structure is too small for seam decomposition")

    # Ignore a small top/bottom margin. Persistent vertical board seams survive
    # the median across height; local texture and horizontal hardware are strongly
    # attenuated by this aggregation.
    ya = max(0, int(round(roi.shape[0] * 0.08)))
    yb = min(roi.shape[0], int(round(roi.shape[0] * 0.95)))
    diff = np.abs(np.diff(roi, axis=1))
    valid = m[:, :-1] & m[:, 1:]

    profile = np.zeros(diff.shape[1], dtype=np.float64)
    for ix in range(diff.shape[1]):
        vals = diff[ya:yb, ix][valid[ya:yb, ix]]
        profile[ix] = float(np.median(vals)) if vals.size else 0.0
    return moving_average(profile, radius=1)


def local_peaks(profile: np.ndarray, min_distance: int, relative_threshold: float) -> list[tuple[int, float]]:
    if profile.size < 5:
        return []
    maximum = float(profile.max())
    if maximum <= 0:
        return []
    threshold = maximum * float(relative_threshold)
    raw: list[tuple[int, float]] = []
    for i in range(2, profile.size - 2):
        if profile[i] >= threshold and profile[i] >= profile[i - 1] and profile[i] >= profile[i + 1]:
            raw.append((i, float(profile[i])))

    # Non-maximum suppression by structural distance.
    raw.sort(key=lambda x: x[1], reverse=True)
    kept: list[tuple[int, float]] = []
    for index, energy in raw:
        if all(abs(index - k) >= min_distance for k, _ in kept):
            kept.append((index, energy))
    kept.sort(key=lambda x: x[0])
    return kept[:6]


def interval_candidates(
    leaf_box: list[int],
    seam_peaks: list[tuple[int, float]],
    profile: np.ndarray,
    parent_box: list[int],
    target_x_rel_parent: float,
    leaf_mask: np.ndarray,
) -> list[dict[str, Any]]:
    x1, y1, x2, y2 = leaf_box
    leaf_w = max(1, x2 - x1)
    parent_x1, _, parent_x2, _ = parent_box
    target_x = parent_x1 + target_x_rel_parent * max(1, parent_x2 - parent_x1)

    seam_xs = [x1 + int(idx) for idx, _ in seam_peaks]
    boundaries = [x1] + seam_xs + [x2]
    boundaries = sorted(set(boundaries))

    max_energy = max([e for _, e in seam_peaks], default=1.0)
    peak_map = {x1 + idx: energy for idx, energy in seam_peaks}
    candidates: list[dict[str, Any]] = []

    for left, right in zip(boundaries[:-1], boundaries[1:]):
        width = right - left
        width_rel_leaf = width / float(leaf_w)
        if width_rel_leaf < 0.12 or width_rel_leaf > 0.55:
            continue
        center = (left + right) * 0.5
        target_distance = abs(center - target_x) / max(1.0, leaf_w)
        target_score = max(0.0, 1.0 - target_distance / 0.65)

        left_energy = peak_map.get(left, max_energy * 0.70 if left == x1 else 0.0)
        right_energy = peak_map.get(right, max_energy * 0.70 if right == x2 else 0.0)
        boundary_score = min(1.0, ((left_energy + right_energy) * 0.5) / max(1e-6, max_energy))

        strip = leaf_mask[y1:y2, left:right] > 0
        occupancy = float(strip.mean()) if strip.size else 0.0
        width_score = 1.0 - min(1.0, abs(width_rel_leaf - 0.33) / 0.25)
        score = 0.42 * target_score + 0.28 * boundary_score + 0.18 * occupancy + 0.12 * width_score

        candidates.append(
            {
                "left": int(left),
                "right": int(right),
                "center": float(center),
                "width": int(width),
                "width_rel_leaf": float(width_rel_leaf),
                "target_score": float(target_score),
                "boundary_score": float(boundary_score),
                "leaf_occupancy": float(occupancy),
                "width_score": float(width_score),
                "score": float(score),
            }
        )

    candidates.sort(key=lambda r: r["score"], reverse=True)
    return candidates


def make_atomic_mask(leaf_mask: np.ndarray, leaf_box: list[int], interval: dict[str, Any]) -> np.ndarray:
    x1, y1, x2, y2 = leaf_box
    left, right = int(interval["left"]), int(interval["right"])
    result = np.zeros_like(leaf_mask, dtype=np.uint8)
    result[y1:y2, left:right] = (leaf_mask[y1:y2, left:right] > 0).astype(np.uint8)
    return result


def mask_metrics(mask: np.ndarray, parent_box: list[int], leaf_box: list[int]) -> dict[str, Any]:
    ys, xs = np.where(mask > 0)
    if xs.size == 0:
        return {
            "area_rel_parent": 0.0,
            "bbox": [0, 0, 0, 0],
            "vertical_aspect": 0.0,
            "width_rel_parent": 0.0,
            "height_rel_leaf": 0.0,
            "center_rel_parent": [0.0, 0.0],
        }
    x1, x2 = int(xs.min()), int(xs.max()) + 1
    y1, y2 = int(ys.min()), int(ys.max()) + 1
    px1, py1, px2, py2 = parent_box
    lx1, ly1, lx2, ly2 = leaf_box
    pw = max(1, px2 - px1)
    ph = max(1, py2 - py1)
    leaf_h = max(1, ly2 - ly1)
    area_parent = float(max(1, pw * ph))
    bw, bh = max(1, x2 - x1), max(1, y2 - y1)
    return {
        "area_rel_parent": float(mask.sum() / area_parent),
        "bbox": [x1, y1, x2, y2],
        "vertical_aspect": float(bh / bw),
        "width_rel_parent": float(bw / pw),
        "height_rel_leaf": float(bh / leaf_h),
        "center_rel_parent": [float(((x1 + x2) * 0.5 - px1) / pw), float(((y1 + y2) * 0.5 - py1) / ph)],
    }


def draw_atomic_detection(
    source: Image.Image,
    parent_box: list[int],
    leaf_box: list[int],
    seam_peaks_abs: list[tuple[int, float]],
    selected: dict[str, Any],
    path: Path,
) -> None:
    canvas = source.copy().convert("RGB")
    draw = ImageDraw.Draw(canvas)
    draw.rectangle(tuple(parent_box), outline=(0, 180, 255), width=3)
    draw.rectangle(tuple(leaf_box), outline=(190, 80, 255), width=3)
    for sx, _ in seam_peaks_abs:
        draw.line((sx, leaf_box[1], sx, leaf_box[3]), fill=(255, 190, 0), width=2)
    draw.rectangle((selected["left"], leaf_box[1], selected["right"], leaf_box[3]), outline=(0, 255, 80), width=5)
    canvas.save(path)


def save_mask_overlay(source: Image.Image, mask: np.ndarray, mask_path: Path, overlay_path: Path) -> None:
    Image.fromarray((mask.astype(np.uint8) * 255), mode="L").save(mask_path)
    overlay = source.convert("RGBA")
    tint = Image.new("RGBA", source.size, (255, 40, 40, 0))
    alpha = Image.fromarray((mask.astype(np.uint8) * 120), mode="L")
    tint.putalpha(alpha)
    Image.alpha_composite(overlay, tint).convert("RGB").save(overlay_path)


def draw_profile(profile: np.ndarray, leaf_box: list[int], seam_peaks: list[tuple[int, float]], path: Path) -> None:
    width, height = 720, 260
    margin = 34
    canvas = Image.new("RGB", (width, height), (245, 245, 245))
    draw = ImageDraw.Draw(canvas)
    draw.line((margin, height - margin, width - margin, height - margin), fill=(40, 40, 40), width=1)
    draw.line((margin, margin, margin, height - margin), fill=(40, 40, 40), width=1)
    maximum = max(1e-6, float(profile.max()))
    usable_w = width - margin * 2
    usable_h = height - margin * 2
    points = []
    for i, value in enumerate(profile):
        x = margin + usable_w * i / max(1, profile.size - 1)
        y = height - margin - usable_h * float(value) / maximum
        points.append((x, y))
    if len(points) > 1:
        draw.line(points, fill=(30, 80, 180), width=2)
    for index, energy in seam_peaks:
        x = margin + usable_w * index / max(1, profile.size - 1)
        draw.line((x, margin, x, height - margin), fill=(220, 120, 0), width=2)
        draw.text((x + 3, margin + 3), f"x={leaf_box[0] + index} e={energy:.1f}", fill=(100, 60, 0))
    draw.text((margin, 8), "Persistent vertical seam energy across localized leaf", fill=(20, 20, 20))
    canvas.save(path)


def make_contact_sheet(source: Image.Image, leaf_overlay: Path, atomic_detection: Path, atomic_overlay: Path, strap_overlay: Path, destination: Path) -> None:
    items = [
        ("ORIGINAL", source),
        ("RUNNER65 LEAF", Image.open(leaf_overlay).convert("RGB")),
        ("SEAMS / SELECTED STRIP", Image.open(atomic_detection).convert("RGB")),
        ("ATOMIC PLANK MASK", Image.open(atomic_overlay).convert("RGB")),
        ("RUNNER65 STRAP RETAINED", Image.open(strap_overlay).convert("RGB")),
    ]
    cell, label_h = 430, 28
    canvas = Image.new("RGB", (cell * len(items), cell + label_h), (32, 32, 32))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    for i, (label, image) in enumerate(items):
        thumb = image.copy()
        thumb.thumbnail((cell, cell), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (cell, cell), (205, 208, 208))
        tile.paste(thumb, ((cell - thumb.width) // 2, (cell - thumb.height) // 2))
        canvas.paste(tile, (i * cell, 0))
        draw.text((i * cell + 6, cell + 7), label, fill=(235, 235, 235), font=font)
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination)


def main() -> int:
    args = parse_args()
    source_path = args.source.resolve()
    r65_dir = args.runner65_dir.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()

    manifest_path = r65_dir / "runner65_hierarchical_localization_manifest.json"
    plank_mask_path = r65_dir / "plank_mask.png"
    plank_overlay_path = r65_dir / "plank_mask_overlay.png"
    strap_mask_path = r65_dir / "strap_mask.png"
    strap_overlay_path = r65_dir / "strap_mask_overlay.png"
    for p in (source_path, manifest_path, plank_mask_path, plank_overlay_path, strap_mask_path, strap_overlay_path):
        if not p.is_file():
            raise FileNotFoundError(p)

    source = Image.open(source_path).convert("RGB")
    gray = np.array(source.convert("L"), dtype=np.float64)
    leaf_mask = (np.array(Image.open(plank_mask_path).convert("L")) > 127).astype(np.uint8)
    strap_mask = (np.array(Image.open(strap_mask_path).convert("L")) > 127).astype(np.uint8)
    manifest65 = load_json(manifest_path)

    parent_box = [int(v) for v in manifest65["parent"]["expanded_box"]]
    leaf_box = bbox_from_mask(leaf_mask)
    spec65 = manifest65["tasks"]["plank"]["spec"]
    target_x_rel_parent = float(spec65.get("target_x", 0.34))

    profile = vertical_seam_profile(gray, leaf_mask, leaf_box)
    min_distance = max(6, int(round((leaf_box[2] - leaf_box[0]) * 0.15)))
    peaks = local_peaks(profile, min_distance=min_distance, relative_threshold=args.peak_relative_threshold)
    if len(peaks) < 2:
        raise RuntimeError(f"atomic decomposition found only {len(peaks)} persistent seam(s); at least two are required")

    candidates = interval_candidates(leaf_box, peaks, profile, parent_box, target_x_rel_parent, leaf_mask)
    if not candidates:
        raise RuntimeError("no plausible atomic intervals survived repeated-element decomposition")
    selected = candidates[0]
    atomic_mask = make_atomic_mask(leaf_mask, leaf_box, selected)
    metrics = mask_metrics(atomic_mask, parent_box, leaf_box)

    reasons: list[str] = []
    if metrics["area_rel_parent"] > 0.12:
        reasons.append("atomic_mask_too_large")
    if metrics["area_rel_parent"] < 0.02:
        reasons.append("atomic_mask_too_small")
    if metrics["vertical_aspect"] < 5.0:
        reasons.append("atomic_mask_not_narrow_vertical")
    if metrics["width_rel_parent"] > 0.18:
        reasons.append("atomic_mask_too_wide")
    if metrics["height_rel_leaf"] < 0.80:
        reasons.append("atomic_mask_does_not_span_leaf_height")
    if selected["width_rel_leaf"] > 0.45:
        reasons.append("selected_interval_too_wide_relative_to_leaf")
    auto_valid = len(reasons) == 0

    atomic_detection = output_dir / "plank_atomic_decomposition.png"
    atomic_mask_path = output_dir / "plank_atomic_mask.png"
    atomic_overlay = output_dir / "plank_atomic_mask_overlay.png"
    profile_path = output_dir / "plank_vertical_seam_profile.png"
    strap_copy_mask = output_dir / "strap_retained_mask.png"
    strap_copy_overlay = output_dir / "strap_retained_mask_overlay.png"
    contact_sheet = output_dir / "runner66_repeated_element_contact_sheet.png"

    peaks_abs = [(leaf_box[0] + i, e) for i, e in peaks]
    draw_atomic_detection(source, parent_box, leaf_box, peaks_abs, selected, atomic_detection)
    save_mask_overlay(source, atomic_mask, atomic_mask_path, atomic_overlay)
    draw_profile(profile, leaf_box, peaks, profile_path)
    Image.fromarray((strap_mask * 255).astype(np.uint8), mode="L").save(strap_copy_mask)
    Image.open(strap_overlay_path).convert("RGB").save(strap_copy_overlay)
    make_contact_sheet(source, plank_overlay_path, atomic_detection, atomic_overlay, strap_copy_overlay, contact_sheet)

    strap65 = manifest65["tasks"]["strap"]
    strap_visual_precondition = bool(strap65.get("auto_valid", False))
    gate_pass = bool(auto_valid and strap_visual_precondition)

    out_manifest = {
        "gate": "ASSET_STUDIO_REPEATED_ELEMENT_ATOMIC_DECOMPOSITION",
        "technical_status": "COMPLETE",
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "architecture": "Runner65 semantic leaf -> persistent vertical seam projection -> atomic interval -> deterministic leaf intersection",
        "source": str(source_path),
        "runner65_manifest": str(manifest_path),
        "parent_box": parent_box,
        "runner65_leaf_bbox": leaf_box,
        "runner65_leaf_area_rel_parent": manifest65["tasks"]["plank"]["selected"].get("mask_area_rel_parent"),
        "target_x_rel_parent": target_x_rel_parent,
        "seam_peaks": [{"x": int(leaf_box[0] + i), "energy": float(e)} for i, e in peaks],
        "interval_candidates": candidates,
        "selected_interval": selected,
        "atomic_plank_metrics": metrics,
        "atomic_plank_auto_valid": auto_valid,
        "atomic_plank_invalid_reasons": reasons,
        "strap_reused_from_runner65": True,
        "strap_runner65_auto_valid": strap_visual_precondition,
        "auto_geometry_gate_pass": gate_pass,
        "outputs": {
            "plank_atomic_decomposition": str(atomic_detection),
            "plank_atomic_mask": str(atomic_mask_path),
            "plank_atomic_mask_overlay": str(atomic_overlay),
            "plank_vertical_seam_profile": str(profile_path),
            "strap_retained_mask": str(strap_copy_mask),
            "strap_retained_mask_overlay": str(strap_copy_overlay),
            "contact_sheet": str(contact_sheet),
        },
        "elapsed_seconds": round(time.time() - started, 3),
    }
    manifest_out = output_dir / "runner66_repeated_element_manifest.json"
    manifest_out.write_text(json.dumps(out_manifest, indent=2), encoding="utf-8")

    print(f"RUNNER66: leaf bbox={leaf_box}", flush=True)
    print(f"RUNNER66: persistent seams={[p['x'] for p in out_manifest['seam_peaks']]}", flush=True)
    print(f"RUNNER66: selected interval={selected['left']}..{selected['right']} width={selected['width']} score={selected['score']:.4f}", flush=True)
    print(f"RUNNER66: atomic metrics={metrics}", flush=True)
    print(f"RUNNER66: plank auto_valid={auto_valid} reasons={reasons}", flush=True)
    print(f"RUNNER66: strap retained Runner65 auto_valid={strap_visual_precondition}", flush=True)
    print(f"RUNNER66: auto geometry gate={gate_pass}", flush=True)
    print(f"RUNNER66: contact sheet={contact_sheet}", flush=True)
    print(f"RUNNER66: manifest={manifest_out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
