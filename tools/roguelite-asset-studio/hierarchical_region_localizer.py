#!/usr/bin/env python3
"""Runner65 perception-only hierarchical localizer.

Architecture:
1) localize the parent object (the wooden double door) in the full image;
2) crop/upscale only that parent region;
3) run Grounding DINO Tiny again for the requested subcomponent with lower thresholds;
4) map component proposals back to full-image coordinates;
5) rerank the top proposals with SAM2.1 masks plus geometry/spatial constraints;
6) persist diagnostics only. No Qwen generation is launched by this gate.

The production invariant remains: the user draws no boxes or masks.
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont

MODULE_ROOT = Path(__file__).resolve().parent
if str(MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE_ROOT))

from automatic_region_localizer import (
    DINO_REPO,
    DINO_REVISION,
    DINO_WEIGHT_SHA256,
    SAM_REPO,
    SAM_REVISION,
    SAM_WEIGHT_SHA256,
    _best_sam_mask,
    _to_device,
)


@dataclass
class RawCandidate:
    box: list[float]
    detector_score: float
    label: str
    phrase: str


@dataclass
class RankedCandidate:
    box: list[float]
    detector_score: float
    label: str
    phrase: str
    pre_score: float
    center_rel_parent: list[float]
    box_aspect: float
    box_area_rel_parent: float
    sam_iou_score: float | None = None
    mask_area_rel_parent: float | None = None
    mask_inside_parent_ratio: float | None = None
    mask_bbox: list[int] | None = None
    mask_aspect: float | None = None
    mask_center_rel_parent: list[float] | None = None
    final_score: float | None = None
    auto_valid: bool = False
    invalid_reasons: list[str] | None = None


@dataclass(frozen=True)
class ComponentSpec:
    task_id: str
    phrases: tuple[str, ...]
    orientation: str
    side: str
    vertical_zone: str
    target_x: float
    target_y: float
    min_mask_aspect: float
    max_mask_area_rel_parent: float
    lexical_tokens: tuple[str, ...]


COMPONENTS = (
    ComponentSpec(
        task_id="plank",
        phrases=(
            "single vertical wooden plank",
            "vertical wooden plank",
            "wooden door plank",
            "vertical wooden board",
            "single wooden board",
        ),
        orientation="vertical",
        side="left",
        vertical_zone="middle",
        target_x=0.34,
        target_y=0.56,
        min_mask_aspect=1.60,
        max_mask_area_rel_parent=0.32,
        lexical_tokens=("plank", "board", "wooden"),
    ),
    ComponentSpec(
        task_id="strap",
        phrases=(
            "lower horizontal iron strap",
            "horizontal iron strap",
            "metal door strap",
            "horizontal iron hinge strap",
            "iron hinge",
        ),
        orientation="horizontal",
        side="right",
        vertical_zone="lower",
        target_x=0.70,
        target_y=0.73,
        min_mask_aspect=1.60,
        max_mask_area_rel_parent=0.22,
        lexical_tokens=("strap", "hinge", "iron", "metal"),
    ),
)

PARENT_PHRASES = (
    "wooden double door",
    "double wooden door",
    "wooden door",
    "double door",
    "door",
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--model-cache", type=Path, required=True)
    p.add_argument("--device", default="cuda")
    p.add_argument("--component-long-side", type=int, default=1280)
    p.add_argument("--max-sam-candidates", type=int, default=10)
    return p.parse_args()


def postprocess(
    processor: Any,
    outputs: Any,
    input_ids: Any,
    target_h: int,
    target_w: int,
    box_threshold: float,
    text_threshold: float,
) -> dict[str, Any]:
    kwargs = dict(text_threshold=text_threshold, target_sizes=[(target_h, target_w)])
    try:
        return processor.post_process_grounded_object_detection(
            outputs,
            input_ids,
            box_threshold=box_threshold,
            **kwargs,
        )[0]
    except TypeError:
        return processor.post_process_grounded_object_detection(
            outputs,
            input_ids,
            threshold=box_threshold,
            **kwargs,
        )[0]


def detect(
    processor: Any,
    model: Any,
    image: Image.Image,
    phrases: tuple[str, ...],
    device: torch.device,
    box_threshold: float,
    text_threshold: float,
) -> list[RawCandidate]:
    w, h = image.size
    found: list[RawCandidate] = []
    for phrase in phrases:
        inputs = processor(images=image, text=phrase, return_tensors="pt")
        input_ids = inputs["input_ids"]
        gpu_inputs = _to_device(inputs, device)
        with torch.inference_mode():
            outputs = model(**gpu_inputs)
        result = postprocess(
            processor,
            outputs,
            input_ids,
            h,
            w,
            box_threshold=box_threshold,
            text_threshold=text_threshold,
        )
        boxes = result.get("boxes", [])
        scores = result.get("scores", [])
        labels = result.get("labels", [])
        for i, box in enumerate(boxes):
            values = box.detach().float().cpu().tolist() if hasattr(box, "detach") else list(box)
            if i < len(scores):
                score_v = scores[i]
                score = float(score_v.detach().float().cpu()) if hasattr(score_v, "detach") else float(score_v)
            else:
                score = 0.0
            label = str(labels[i]) if i < len(labels) else phrase
            found.append(
                RawCandidate(
                    box=[float(v) for v in values],
                    detector_score=score,
                    label=label,
                    phrase=phrase,
                )
            )
    return found


def clamp_box(box: list[float], w: int, h: int) -> list[float]:
    x1, y1, x2, y2 = box
    x1 = max(0.0, min(float(w - 1), x1))
    y1 = max(0.0, min(float(h - 1), y1))
    x2 = max(x1 + 1.0, min(float(w), x2))
    y2 = max(y1 + 1.0, min(float(h), y2))
    return [x1, y1, x2, y2]


def parent_score(c: RawCandidate, w: int, h: int) -> tuple[float, dict[str, float]]:
    x1, y1, x2, y2 = clamp_box(c.box, w, h)
    bw = x2 - x1
    bh = y2 - y1
    area = (bw * bh) / float(w * h)
    cx = (x1 + x2) * 0.5 / w
    cy = (y1 + y2) * 0.5 / h
    aspect = bh / max(1.0, bw)

    center = 1.0 - min(1.0, math.hypot(cx - 0.53, cy - 0.56) / 0.55)
    aspect_score = min(1.0, aspect / 1.55)
    area_score = 1.0 - min(1.0, abs(area - 0.16) / 0.24)
    lexical = 1.0 if "door" in c.label.lower() or "door" in c.phrase.lower() else 0.0
    penalty = 0.0
    if area > 0.45:
        penalty += min(0.75, (area - 0.45) * 2.2)
    if area < 0.035:
        penalty += 0.25
    if aspect < 1.05:
        penalty += 0.12

    score = (
        0.42 * c.detector_score
        + 0.20 * center
        + 0.16 * aspect_score
        + 0.14 * area_score
        + 0.08 * lexical
        - penalty
    )
    return float(score), {
        "area_ratio": float(area),
        "center_x": float(cx),
        "center_y": float(cy),
        "vertical_aspect": float(aspect),
        "center_score": float(center),
        "area_score": float(area_score),
        "aspect_score": float(aspect_score),
        "penalty": float(penalty),
    }


def choose_parent(candidates: list[RawCandidate], w: int, h: int) -> tuple[RawCandidate, list[dict[str, Any]]]:
    if not candidates:
        raise RuntimeError("Grounding DINO produced no parent-door candidate")
    ranked: list[tuple[float, RawCandidate, dict[str, float]]] = []
    for c in candidates:
        score, metrics = parent_score(c, w, h)
        ranked.append((score, c, metrics))
    ranked.sort(key=lambda x: x[0], reverse=True)

    records: list[dict[str, Any]] = []
    for score, c, metrics in ranked[:30]:
        records.append(
            {
                "box": c.box,
                "detector_score": c.detector_score,
                "label": c.label,
                "phrase": c.phrase,
                "parent_selector_score": score,
                **metrics,
            }
        )

    for score, c, metrics in ranked:
        area = metrics["area_ratio"]
        aspect = metrics["vertical_aspect"]
        cx = metrics["center_x"]
        cy = metrics["center_y"]
        if 0.04 <= area <= 0.42 and aspect >= 1.05 and 0.25 <= cx <= 0.78 and 0.22 <= cy <= 0.82:
            return c, records
    raise RuntimeError("No plausible parent-door candidate survived hierarchical parent constraints")


def expand_box(box: list[float], w: int, h: int, x_frac: float = 0.08, y_frac: float = 0.05) -> list[int]:
    x1, y1, x2, y2 = clamp_box(box, w, h)
    bw = x2 - x1
    bh = y2 - y1
    return [
        max(0, int(math.floor(x1 - bw * x_frac))),
        max(0, int(math.floor(y1 - bh * y_frac))),
        min(w, int(math.ceil(x2 + bw * x_frac))),
        min(h, int(math.ceil(y2 + bh * y_frac))),
    ]


def map_crop_box_to_full(box: list[float], parent_box: list[int], scale: float, full_w: int, full_h: int) -> list[float]:
    px1, py1, _, _ = parent_box
    x1, y1, x2, y2 = box
    mapped = [
        px1 + x1 / scale,
        py1 + y1 / scale,
        px1 + x2 / scale,
        py1 + y2 / scale,
    ]
    return clamp_box(mapped, full_w, full_h)


def rel_to_parent(box: list[float], parent_box: list[int]) -> tuple[float, float, float]:
    px1, py1, px2, py2 = parent_box
    pw = max(1.0, px2 - px1)
    ph = max(1.0, py2 - py1)
    x1, y1, x2, y2 = box
    cx = ((x1 + x2) * 0.5 - px1) / pw
    cy = ((y1 + y2) * 0.5 - py1) / ph
    area = ((x2 - x1) * (y2 - y1)) / (pw * ph)
    return float(cx), float(cy), float(area)


def orientation_aspect(spec: ComponentSpec, box: list[float]) -> float:
    x1, y1, x2, y2 = box
    bw = max(1.0, x2 - x1)
    bh = max(1.0, y2 - y1)
    return float(bh / bw if spec.orientation == "vertical" else bw / bh)


def component_pre_score(spec: ComponentSpec, c: RawCandidate, parent_box: list[int]) -> RankedCandidate:
    cx, cy, area = rel_to_parent(c.box, parent_box)
    aspect = orientation_aspect(spec, c.box)
    orient = min(1.0, aspect / 4.0)
    pos = 1.0 - min(1.0, math.hypot(cx - spec.target_x, cy - spec.target_y) / 0.80)

    if area <= 0:
        size = 0.0
    elif area <= 0.22:
        size = 1.0 - min(1.0, abs(area - 0.06) / 0.18)
    else:
        size = max(0.0, 1.0 - (area - 0.22) / 0.35)

    label_l = c.label.lower()
    phrase_l = c.phrase.lower()
    lexical = 1.0 if any(tok in label_l for tok in spec.lexical_tokens) else (
        0.65 if any(tok in phrase_l for tok in spec.lexical_tokens) else 0.0
    )
    side = 1.0
    if spec.side == "left":
        side = max(0.0, min(1.0, (0.68 - cx) / 0.68))
    elif spec.side == "right":
        side = max(0.0, min(1.0, cx / 0.68))
    zone = 1.0
    if spec.vertical_zone == "lower":
        zone = max(0.0, min(1.0, cy / 0.68))
    elif spec.vertical_zone == "middle":
        zone = 1.0 - min(1.0, abs(cy - 0.55) / 0.55)

    penalty = 0.0
    if area > 0.42:
        penalty += 0.60
    if aspect < 1.05:
        penalty += 0.18
    if not (-0.05 <= cx <= 1.05 and -0.05 <= cy <= 1.05):
        penalty += 0.50

    score = (
        0.34 * c.detector_score
        + 0.24 * orient
        + 0.15 * pos
        + 0.10 * size
        + 0.07 * lexical
        + 0.05 * side
        + 0.05 * zone
        - penalty
    )
    return RankedCandidate(
        box=c.box,
        detector_score=c.detector_score,
        label=c.label,
        phrase=c.phrase,
        pre_score=float(score),
        center_rel_parent=[cx, cy],
        box_aspect=aspect,
        box_area_rel_parent=area,
        invalid_reasons=[],
    )


def mask_metrics(mask: np.ndarray, parent_box: list[int], spec: ComponentSpec) -> dict[str, Any]:
    ys, xs = np.where(mask > 0)
    if xs.size == 0:
        return {
            "mask_area_rel_parent": 0.0,
            "inside_parent_ratio": 0.0,
            "bbox": [0, 0, 0, 0],
            "aspect": 0.0,
            "center_rel_parent": [0.0, 0.0],
        }
    x1, x2 = int(xs.min()), int(xs.max()) + 1
    y1, y2 = int(ys.min()), int(ys.max()) + 1
    bbox = [x1, y1, x2, y2]
    px1, py1, px2, py2 = parent_box
    parent_area = max(1, (px2 - px1) * (py2 - py1))
    mask_area = int(mask.sum())

    ix1, iy1 = max(0, px1), max(0, py1)
    ix2, iy2 = min(mask.shape[1], px2), min(mask.shape[0], py2)
    inside = int(mask[iy1:iy2, ix1:ix2].sum()) if ix2 > ix1 and iy2 > iy1 else 0
    inside_ratio = inside / max(1, mask_area)

    bw = max(1, x2 - x1)
    bh = max(1, y2 - y1)
    aspect = bh / bw if spec.orientation == "vertical" else bw / bh
    cx = (float(xs.mean()) - px1) / max(1.0, px2 - px1)
    cy = (float(ys.mean()) - py1) / max(1.0, py2 - py1)

    return {
        "mask_area_rel_parent": float(mask_area / parent_area),
        "inside_parent_ratio": float(inside_ratio),
        "bbox": bbox,
        "aspect": float(aspect),
        "center_rel_parent": [float(cx), float(cy)],
    }


def validate_mask(spec: ComponentSpec, metrics: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    area = metrics["mask_area_rel_parent"]
    inside = metrics["inside_parent_ratio"]
    aspect = metrics["aspect"]
    cx, cy = metrics["center_rel_parent"]

    if inside < 0.90:
        reasons.append(f"inside_parent_ratio<{0.90:.2f}")
    if area < 0.003:
        reasons.append("mask_too_small")
    if area > spec.max_mask_area_rel_parent:
        reasons.append("mask_too_large")
    if aspect < spec.min_mask_aspect:
        reasons.append(f"orientation_aspect<{spec.min_mask_aspect:.2f}")

    if spec.side == "left" and cx > 0.62:
        reasons.append("wrong_parent_side")
    if spec.side == "right" and cx < 0.45:
        reasons.append("wrong_parent_side")
    if spec.vertical_zone == "lower" and cy < 0.48:
        reasons.append("wrong_parent_vertical_zone")
    if spec.vertical_zone == "middle" and not (0.16 <= cy <= 0.90):
        reasons.append("wrong_parent_vertical_zone")
    return reasons


def final_candidate_score(
    spec: ComponentSpec,
    candidate: RankedCandidate,
    sam_iou: float,
    metrics: dict[str, Any],
) -> float:
    cx, cy = metrics["center_rel_parent"]
    pos = 1.0 - min(1.0, math.hypot(cx - spec.target_x, cy - spec.target_y) / 0.80)
    orient = min(1.0, metrics["aspect"] / 4.0)
    inside = metrics["inside_parent_ratio"]
    area = metrics["mask_area_rel_parent"]
    if area <= spec.max_mask_area_rel_parent:
        size = 1.0 - min(1.0, abs(area - 0.055) / max(0.055, spec.max_mask_area_rel_parent))
    else:
        size = 0.0
    return float(
        0.28 * candidate.pre_score
        + 0.24 * sam_iou
        + 0.20 * orient
        + 0.12 * pos
        + 0.10 * inside
        + 0.06 * size
    )


def draw_parent(source: Image.Image, candidates: list[dict[str, Any]], selected_box: list[float], path: Path) -> None:
    canvas = source.copy().convert("RGB")
    draw = ImageDraw.Draw(canvas)
    for idx, rec in enumerate(candidates[:20]):
        x1, y1, x2, y2 = rec["box"]
        is_sel = all(abs(a - b) < 1e-4 for a, b in zip(rec["box"], selected_box))
        color = (0, 255, 80) if is_sel else (255, 190, 0)
        width = 5 if is_sel else 2
        draw.rectangle((x1, y1, x2, y2), outline=color, width=width)
        draw.text((x1 + 3, max(2, y1 - 13)), f"{idx}:{rec['detector_score']:.2f}/{rec['parent_selector_score']:.2f}", fill=color)
    canvas.save(path)


def draw_component_candidates(
    source: Image.Image,
    parent_box: list[int],
    candidates: list[RankedCandidate],
    selected: RankedCandidate,
    path: Path,
) -> None:
    canvas = source.copy().convert("RGB")
    draw = ImageDraw.Draw(canvas)
    px1, py1, px2, py2 = parent_box
    draw.rectangle((px1, py1, px2, py2), outline=(0, 180, 255), width=3)
    for idx, c in enumerate(candidates[:20]):
        x1, y1, x2, y2 = c.box
        is_sel = c is selected
        color = (0, 255, 80) if is_sel else (255, 190, 0)
        width = 5 if is_sel else 2
        draw.rectangle((x1, y1, x2, y2), outline=color, width=width)
        fs = c.final_score if c.final_score is not None else c.pre_score
        draw.text((x1 + 3, max(2, y1 - 13)), f"{idx}:{c.detector_score:.2f}/{fs:.2f}", fill=color)
    canvas.save(path)


def save_mask_assets(source: Image.Image, mask: np.ndarray, task_id: str, output_dir: Path) -> tuple[Path, Path]:
    mask_img = Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
    mask_path = output_dir / f"{task_id}_mask.png"
    mask_img.save(mask_path)

    overlay = source.convert("RGBA")
    tint = Image.new("RGBA", source.size, (255, 40, 40, 0))
    alpha = Image.fromarray((mask.astype(np.uint8) * 120), mode="L")
    tint.putalpha(alpha)
    overlay = Image.alpha_composite(overlay, tint).convert("RGB")
    overlay_path = output_dir / f"{task_id}_mask_overlay.png"
    overlay.save(overlay_path)
    return mask_path, overlay_path


def context_crop(box: list[int], parent_box: list[int], w: int, h: int) -> list[int]:
    x1, y1, x2, y2 = box
    bw = max(1, x2 - x1)
    bh = max(1, y2 - y1)
    px1, py1, px2, py2 = parent_box
    mx = max(48, int(bw * 1.8))
    my = max(48, int(bh * 1.0))
    return [
        max(0, min(px1, x1 - mx)),
        max(0, min(py1, y1 - my)),
        min(w, max(px2, x2 + mx)),
        min(h, max(py2, y2 + my)),
    ]


def make_contact_sheet(source: Image.Image, parent_img: Path, task_overlays: dict[str, Path], destination: Path) -> None:
    cell = 512
    label_h = 28
    items = [
        ("ORIGINAL", source),
        ("PARENT DOOR", Image.open(parent_img).convert("RGB")),
        ("PLANK MASK", Image.open(task_overlays["plank"]).convert("RGB")),
        ("STRAP MASK", Image.open(task_overlays["strap"]).convert("RGB")),
    ]
    canvas = Image.new("RGB", (cell * len(items), cell + label_h), (32, 32, 32))
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(canvas)
    for i, (label, img) in enumerate(items):
        thumb = img.copy()
        thumb.thumbnail((cell, cell), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (cell, cell), (205, 208, 208))
        tile.paste(thumb, ((cell - thumb.width) // 2, (cell - thumb.height) // 2))
        canvas.paste(tile, (i * cell, 0))
        draw.text((i * cell + 6, cell + 7), label, fill=(235, 235, 235), font=font)
    canvas.save(destination)


def main() -> int:
    args = parse_args()
    source_path = args.source.resolve()
    output_dir = args.output_dir.resolve()
    cache = args.model_cache.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    if not source_path.is_file():
        raise FileNotFoundError(source_path)

    source = Image.open(source_path).convert("RGB")
    w, h = source.size
    device = torch.device(args.device if args.device == "cpu" or torch.cuda.is_available() else "cpu")
    started = time.time()
    print(f"RUNNER65: source={source_path} size={w}x{h} device={device}", flush=True)

    from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor, Sam2Model, Sam2Processor

    print("RUNNER65: loading cached Grounding DINO Tiny...", flush=True)
    dino_processor = AutoProcessor.from_pretrained(
        DINO_REPO,
        revision=DINO_REVISION,
        cache_dir=cache,
        local_files_only=True,
    )
    dino_model = AutoModelForZeroShotObjectDetection.from_pretrained(
        DINO_REPO,
        revision=DINO_REVISION,
        cache_dir=cache,
        use_safetensors=True,
        local_files_only=True,
    ).to(device)
    dino_model.eval()

    parent_raw = detect(
        dino_processor,
        dino_model,
        source,
        PARENT_PHRASES,
        device,
        box_threshold=0.10,
        text_threshold=0.10,
    )
    parent_selected, parent_records = choose_parent(parent_raw, w, h)
    parent_box = expand_box(parent_selected.box, w, h, x_frac=0.08, y_frac=0.05)
    parent_detection_path = output_dir / "parent_detection.png"
    draw_parent(source, parent_records, parent_selected.box, parent_detection_path)

    px1, py1, px2, py2 = parent_box
    parent_crop = source.crop((px1, py1, px2, py2))
    parent_crop_path = output_dir / "parent_crop.png"
    parent_crop.save(parent_crop_path)
    print(f"RUNNER65: parent selected={parent_selected.box} expanded={parent_box}", flush=True)

    long_side = max(parent_crop.size)
    scale = max(1.0, float(args.component_long_side) / float(long_side))
    scale = min(scale, 5.0)
    up_w = max(16, int(round(parent_crop.width * scale)))
    up_h = max(16, int(round(parent_crop.height * scale)))
    parent_up = parent_crop.resize((up_w, up_h), Image.Resampling.LANCZOS)
    parent_up_path = output_dir / "parent_crop_upscaled.png"
    parent_up.save(parent_up_path)

    mapped_candidates: dict[str, list[RankedCandidate]] = {}
    for spec in COMPONENTS:
        raw = detect(
            dino_processor,
            dino_model,
            parent_up,
            spec.phrases,
            device,
            box_threshold=0.045,
            text_threshold=0.045,
        )
        mapped_raw: list[RawCandidate] = []
        for c in raw:
            mapped_raw.append(
                RawCandidate(
                    box=map_crop_box_to_full(c.box, parent_box, scale, w, h),
                    detector_score=c.detector_score,
                    label=c.label,
                    phrase=c.phrase,
                )
            )
        ranked = [component_pre_score(spec, c, parent_box) for c in mapped_raw]
        ranked.sort(key=lambda c: c.pre_score, reverse=True)
        mapped_candidates[spec.task_id] = ranked
        print(f"RUNNER65: {spec.task_id} GroundingDINO candidates={len(ranked)}", flush=True)
        if not ranked:
            raise RuntimeError(f"no component proposals for {spec.task_id}")

    del dino_model
    del dino_processor
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    print("RUNNER65: loading cached SAM2.1 Hiera Small...", flush=True)
    sam_processor = Sam2Processor.from_pretrained(
        SAM_REPO,
        revision=SAM_REVISION,
        cache_dir=cache,
        local_files_only=True,
    )
    sam_model = Sam2Model.from_pretrained(
        SAM_REPO,
        revision=SAM_REVISION,
        cache_dir=cache,
        use_safetensors=True,
        local_files_only=True,
    ).to(device)
    sam_model.eval()

    manifest: dict[str, Any] = {
        "gate": "ASSET_STUDIO_HIERARCHICAL_COMPONENT_LOCALIZATION",
        "technical_status": "COMPLETE",
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "source": str(source_path),
        "source_size": [w, h],
        "device": str(device),
        "architecture": "full-image parent grounding -> parent crop/upscale -> component grounding -> SAM2 rerank -> diagnostics only",
        "grounding_dino": {
            "repo": DINO_REPO,
            "revision": DINO_REVISION,
            "weight_sha256": DINO_WEIGHT_SHA256,
        },
        "sam2": {
            "repo": SAM_REPO,
            "revision": SAM_REVISION,
            "weight_sha256": SAM_WEIGHT_SHA256,
        },
        "parent": {
            "phrases": list(PARENT_PHRASES),
            "selected_raw_box": parent_selected.box,
            "expanded_box": parent_box,
            "selected_label": parent_selected.label,
            "selected_phrase": parent_selected.phrase,
            "detector_score": parent_selected.detector_score,
            "candidates": parent_records,
            "crop": str(parent_crop_path),
            "upscaled_crop": str(parent_up_path),
            "upscale_factor": scale,
            "detection_image": str(parent_detection_path),
        },
        "tasks": {},
    }

    overlays: dict[str, Path] = {}

    for spec in COMPONENTS:
        candidates = mapped_candidates[spec.task_id]
        evaluated: list[tuple[RankedCandidate, np.ndarray]] = []
        for candidate in candidates[: max(1, args.max_sam_candidates)]:
            mask, sam_iou = _best_sam_mask(sam_processor, sam_model, source, candidate.box, device)
            metrics = mask_metrics(mask, parent_box, spec)
            reasons = validate_mask(spec, metrics)
            candidate.sam_iou_score = float(sam_iou)
            candidate.mask_area_rel_parent = metrics["mask_area_rel_parent"]
            candidate.mask_inside_parent_ratio = metrics["inside_parent_ratio"]
            candidate.mask_bbox = metrics["bbox"]
            candidate.mask_aspect = metrics["aspect"]
            candidate.mask_center_rel_parent = metrics["center_rel_parent"]
            candidate.final_score = final_candidate_score(spec, candidate, float(sam_iou), metrics)
            candidate.auto_valid = len(reasons) == 0
            candidate.invalid_reasons = reasons
            evaluated.append((candidate, mask))

        if not evaluated:
            raise RuntimeError(f"SAM2 evaluated no candidate for {spec.task_id}")

        valid = [item for item in evaluated if item[0].auto_valid]
        pool = valid if valid else evaluated
        pool.sort(key=lambda item: item[0].final_score if item[0].final_score is not None else -999.0, reverse=True)
        selected, selected_mask = pool[0]

        all_ranked = [item[0] for item in evaluated]
        all_ranked.sort(key=lambda c: c.final_score if c.final_score is not None else -999.0, reverse=True)
        det_path = output_dir / f"{spec.task_id}_hierarchical_detection.png"
        draw_component_candidates(source, parent_box, all_ranked, selected, det_path)

        mask_path, overlay_path = save_mask_assets(source, selected_mask, spec.task_id, output_dir)
        overlays[spec.task_id] = overlay_path

        assert selected.mask_bbox is not None
        crop_box = context_crop(selected.mask_bbox, parent_box, w, h)
        crop_img = source.crop(tuple(crop_box))
        crop_path = output_dir / f"{spec.task_id}_crop.png"
        crop_img.save(crop_path)
        crop_mask_img = Image.fromarray((selected_mask.astype(np.uint8) * 255), mode="L").crop(tuple(crop_box))
        crop_mask_path = output_dir / f"{spec.task_id}_crop_mask.png"
        crop_mask_img.save(crop_mask_path)

        manifest["tasks"][spec.task_id] = {
            "spec": asdict(spec),
            "auto_valid": selected.auto_valid,
            "selected": asdict(selected),
            "candidate_count_grounding": len(candidates),
            "candidate_count_sam_evaluated": len(evaluated),
            "detection_image": str(det_path),
            "mask": str(mask_path),
            "mask_overlay": str(overlay_path),
            "crop_box": crop_box,
            "crop": str(crop_path),
            "crop_mask": str(crop_mask_path),
            "evaluated_candidates": [asdict(c) for c in all_ranked],
        }
        print(
            f"RUNNER65: {spec.task_id} selected auto_valid={selected.auto_valid} "
            f"label={selected.label!r} det={selected.detector_score:.4f} "
            f"sam_iou={selected.sam_iou_score:.4f} final={selected.final_score:.4f} "
            f"reasons={selected.invalid_reasons}",
            flush=True,
        )

    del sam_model
    del sam_processor
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    sheet_path = output_dir / "runner65_hierarchical_localization_contact_sheet.png"
    make_contact_sheet(source, parent_detection_path, overlays, sheet_path)
    manifest["contact_sheet"] = str(sheet_path)
    manifest["auto_geometry_gate_pass"] = all(manifest["tasks"][t]["auto_valid"] for t in ("plank", "strap"))
    manifest["elapsed_seconds"] = round(time.time() - started, 3)
    manifest_path = output_dir / "runner65_hierarchical_localization_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        "RUNNER65-HIERARCHICAL-LOCALIZATION: PASS - TECHNICAL PERCEPTION GATE COMPLETE / VISUAL VERDICT PENDING",
        flush=True,
    )
    print(f"Auto geometry gate pass: {manifest['auto_geometry_gate_pass']}", flush=True)
    print(f"Contact sheet: {sheet_path}", flush=True)
    print(f"Manifest: {manifest_path}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        import traceback

        print(f"RUNNER65-FAIL: {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc(file=sys.stdout)
        raise SystemExit(1)
