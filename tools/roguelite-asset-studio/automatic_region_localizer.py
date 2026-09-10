#!/usr/bin/env python3
"""Automatic text-driven region localization for Roguelite Asset Studio.

Purpose
-------
Turn a semantic component request into a deterministic image region without manual
mask painting. The first production hypothesis deliberately separates perception
from generation:

1. Grounding DINO Tiny proposes boxes from text.
2. deterministic spatial/shape selectors choose the intended instance.
3. SAM2.1 Hiera Small segments the selected box.
4. masks, overlays, crop bounds and provenance are persisted for downstream editing.

The gate currently exercises two generic selector modes used by Runner64:
- vertical component on the left side (one door plank);
- horizontal component on the lower-right side (one iron strap).

These selectors are represented as data and are not embedded in the Qwen adapter.
Future Studio parsing can map user language to the same selector schema.
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
from typing import Any, Iterable

import numpy as np
import torch
from PIL import Image, ImageDraw

DINO_REPO = "IDEA-Research/grounding-dino-tiny"
DINO_REVISION = "a2bb814dd30d776dcf7e30523b00659f4f141c71"
DINO_WEIGHT_SHA256 = "1a2412ef99bd74bcd3c2a246fa1e48581f8889a1300c9051974741314fc042f3"
SAM_REPO = "facebook/sam2.1-hiera-small"
SAM_REVISION = "e07df6aa19f5c6545121551bf89957b7663ee715"
SAM_WEIGHT_SHA256 = "0a4067b11ce1e23d5229203f11c718a823060d15a4b23fa2372a7d4b77cbbc60"


@dataclass
class Candidate:
    box: list[float]
    detector_score: float
    label: str
    selector_score: float
    aspect: float
    center_norm: list[float]


@dataclass
class TaskSpec:
    task_id: str
    phrases: list[str]
    orientation: str
    side: str
    vertical_zone: str
    box_threshold: float
    text_threshold: float


TASKS = [
    TaskSpec(
        task_id="plank",
        phrases=["vertical wooden plank", "wooden door plank", "vertical wooden board"],
        orientation="vertical",
        side="left",
        vertical_zone="middle",
        box_threshold=0.16,
        text_threshold=0.14,
    ),
    TaskSpec(
        task_id="strap",
        phrases=["horizontal iron strap", "metal door strap", "horizontal iron hinge"],
        orientation="horizontal",
        side="right",
        vertical_zone="lower",
        box_threshold=0.12,
        text_threshold=0.12,
    ),
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--model-cache", type=Path, required=True)
    p.add_argument("--device", default="cuda")
    return p.parse_args()


def _to_device(batch: Any, device: torch.device) -> Any:
    if hasattr(batch, "to"):
        return batch.to(device)
    if isinstance(batch, dict):
        return {k: (v.to(device) if hasattr(v, "to") else v) for k, v in batch.items()}
    return batch


def _postprocess_grounding(processor: Any, outputs: Any, input_ids: Any, task: TaskSpec, h: int, w: int) -> dict[str, Any]:
    kwargs = dict(text_threshold=task.text_threshold, target_sizes=[(h, w)])
    try:
        result = processor.post_process_grounded_object_detection(
            outputs,
            input_ids,
            box_threshold=task.box_threshold,
            **kwargs,
        )[0]
    except TypeError:
        result = processor.post_process_grounded_object_detection(
            outputs,
            input_ids,
            threshold=task.box_threshold,
            **kwargs,
        )[0]
    return result


def _shape_score(task: TaskSpec, box: Iterable[float], det_score: float, w: int, h: int) -> tuple[float, float, list[float]]:
    x1, y1, x2, y2 = [float(v) for v in box]
    bw = max(1.0, x2 - x1)
    bh = max(1.0, y2 - y1)
    cx = (x1 + x2) * 0.5 / w
    cy = (y1 + y2) * 0.5 / h
    aspect = bh / bw if task.orientation == "vertical" else bw / bh
    orient = min(1.0, aspect / 4.0)

    if task.side == "left":
        side = max(0.0, min(1.0, (0.62 - cx) / 0.42))
        side_target = 0.39
    elif task.side == "right":
        side = max(0.0, min(1.0, (cx - 0.38) / 0.42))
        side_target = 0.61
    else:
        side = 1.0
        side_target = 0.5

    if task.vertical_zone == "lower":
        zone = max(0.0, min(1.0, (cy - 0.42) / 0.45))
        zone_target = 0.69
    elif task.vertical_zone == "upper":
        zone = max(0.0, min(1.0, (0.58 - cy) / 0.45))
        zone_target = 0.31
    else:
        zone = 1.0 - min(1.0, abs(cy - 0.56) / 0.5)
        zone_target = 0.56

    proximity = 1.0 - min(1.0, math.hypot(cx - side_target, cy - zone_target) / 0.65)
    area_ratio = (bw * bh) / float(w * h)
    area_penalty = 0.0
    if area_ratio > 0.20:
        area_penalty = min(0.45, (area_ratio - 0.20) * 2.0)
    if task.orientation == "vertical" and bw / w > 0.22:
        area_penalty += 0.18
    if task.orientation == "horizontal" and bh / h > 0.18:
        area_penalty += 0.18

    total = 0.47 * float(det_score) + 0.23 * orient + 0.12 * side + 0.10 * zone + 0.08 * proximity - area_penalty
    return float(total), float(aspect), [float(cx), float(cy)]


def _merge_candidates(task: TaskSpec, detections: list[tuple[str, dict[str, Any]]], w: int, h: int) -> list[Candidate]:
    merged: list[Candidate] = []
    for phrase, result in detections:
        boxes = result.get("boxes", [])
        scores = result.get("scores", [])
        labels = result.get("labels", [])
        for idx, box in enumerate(boxes):
            values = box.detach().cpu().tolist() if hasattr(box, "detach") else list(box)
            det = float(scores[idx].detach().cpu()) if idx < len(scores) and hasattr(scores[idx], "detach") else float(scores[idx]) if idx < len(scores) else 0.0
            label = str(labels[idx]) if idx < len(labels) else phrase
            selector, aspect, center = _shape_score(task, values, det, w, h)
            merged.append(Candidate([float(v) for v in values], det, label, selector, aspect, center))
    merged.sort(key=lambda c: c.selector_score, reverse=True)
    return merged


def _draw_candidates(source: Image.Image, candidates: list[Candidate], selected: Candidate, path: Path) -> None:
    canvas = source.copy().convert("RGB")
    draw = ImageDraw.Draw(canvas)
    for index, c in enumerate(candidates[:20]):
        x1, y1, x2, y2 = c.box
        color = (255, 190, 0) if c is not selected else (0, 255, 80)
        width = 2 if c is not selected else 5
        draw.rectangle((x1, y1, x2, y2), outline=color, width=width)
        draw.text((x1 + 3, max(2, y1 - 14)), f"{index}:{c.detector_score:.2f}/{c.selector_score:.2f}", fill=color)
    canvas.save(path)


def _crop_bounds(task: TaskSpec, box: list[float], w: int, h: int) -> list[int]:
    x1, y1, x2, y2 = box
    bw = max(1.0, x2 - x1)
    bh = max(1.0, y2 - y1)
    if task.task_id == "plank":
        px = max(96.0, bw * 1.55)
        py = max(56.0, bh * 0.16)
    else:
        px = max(96.0, bw * 0.38)
        py = max(96.0, bh * 3.2)
    return [
        max(0, int(math.floor(x1 - px))),
        max(0, int(math.floor(y1 - py))),
        min(w, int(math.ceil(x2 + px))),
        min(h, int(math.ceil(y2 + py))),
    ]


def _best_sam_mask(processor: Any, model: Any, image: Image.Image, box: list[float], device: torch.device) -> tuple[np.ndarray, float]:
    inputs = processor(images=image, input_boxes=[[box]], return_tensors="pt")
    inputs = _to_device(inputs, device)
    with torch.inference_mode():
        outputs = model(**inputs, multimask_output=True)
    masks = processor.post_process_masks(outputs.pred_masks.detach().cpu(), inputs["original_sizes"].detach().cpu())[0]
    masks_t = masks.detach().cpu() if hasattr(masks, "detach") else torch.as_tensor(masks)
    while masks_t.ndim > 3:
        masks_t = masks_t[0]
    if masks_t.ndim == 2:
        masks_t = masks_t.unsqueeze(0)
    scores = outputs.iou_scores.detach().float().cpu().reshape(-1)
    count = masks_t.shape[0]
    best_idx = int(torch.argmax(scores[:count]).item()) if scores.numel() >= count else 0
    mask = (masks_t[best_idx] > 0).numpy().astype(np.uint8)
    score = float(scores[best_idx].item()) if scores.numel() > best_idx else float("nan")
    return mask, score


def _save_mask_assets(source: Image.Image, mask: np.ndarray, task_id: str, output_dir: Path) -> tuple[Path, Path]:
    mask_img = Image.fromarray(mask * 255, mode="L")
    mask_path = output_dir / f"{task_id}_mask.png"
    mask_img.save(mask_path)

    overlay = source.convert("RGBA")
    tint = Image.new("RGBA", source.size, (255, 40, 40, 0))
    alpha = Image.fromarray((mask * 120).astype(np.uint8), mode="L")
    tint.putalpha(alpha)
    overlay = Image.alpha_composite(overlay, tint).convert("RGB")
    overlay_path = output_dir / f"{task_id}_mask_overlay.png"
    overlay.save(overlay_path)
    return mask_path, overlay_path


def main() -> int:
    args = parse_args()
    source_path = args.source.resolve()
    output_dir = args.output_dir.resolve()
    cache = args.model_cache.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    if not source_path.is_file():
        raise FileNotFoundError(source_path)

    device = torch.device(args.device if args.device == "cpu" or torch.cuda.is_available() else "cpu")
    source = Image.open(source_path).convert("RGB")
    w, h = source.size
    print(f"RUNNER64-LOCALIZER: source={source_path} size={w}x{h} device={device}", flush=True)

    try:
        from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor, Sam2Model, Sam2Processor
    except Exception as exc:
        print(f"RUNNER64-LOCALIZER-IMPORT-FAIL: {type(exc).__name__}: {exc}", flush=True)
        raise

    started = time.time()
    print("RUNNER64-LOCALIZER: loading Grounding DINO Tiny...", flush=True)
    dino_processor = AutoProcessor.from_pretrained(DINO_REPO, revision=DINO_REVISION, cache_dir=cache)
    dino_model = AutoModelForZeroShotObjectDetection.from_pretrained(
        DINO_REPO,
        revision=DINO_REVISION,
        cache_dir=cache,
        use_safetensors=True,
    ).to(device)
    dino_model.eval()

    selected_by_task: dict[str, Candidate] = {}
    candidates_by_task: dict[str, list[Candidate]] = {}
    for task in TASKS:
        detections: list[tuple[str, dict[str, Any]]] = []
        for phrase in task.phrases:
            inputs = dino_processor(images=source, text=phrase, return_tensors="pt")
            input_ids = inputs["input_ids"]
            gpu_inputs = _to_device(inputs, device)
            with torch.inference_mode():
                outputs = dino_model(**gpu_inputs)
            result = _postprocess_grounding(dino_processor, outputs, input_ids, task, h, w)
            detections.append((phrase, result))
        candidates = _merge_candidates(task, detections, w, h)
        if not candidates:
            raise RuntimeError(f"Grounding DINO produced no candidate for task {task.task_id}")
        selected = candidates[0]
        candidates_by_task[task.task_id] = candidates
        selected_by_task[task.task_id] = selected
        _draw_candidates(source, candidates, selected, output_dir / f"{task.task_id}_detection.png")
        print(
            f"RUNNER64-LOCALIZER: {task.task_id} selected box={selected.box} detector={selected.detector_score:.4f} selector={selected.selector_score:.4f}",
            flush=True,
        )

    del dino_model
    del dino_processor
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    print("RUNNER64-LOCALIZER: loading SAM2.1 Hiera Small...", flush=True)
    sam_processor = Sam2Processor.from_pretrained(SAM_REPO, revision=SAM_REVISION, cache_dir=cache)
    sam_model = Sam2Model.from_pretrained(
        SAM_REPO,
        revision=SAM_REVISION,
        cache_dir=cache,
        use_safetensors=True,
    ).to(device)
    sam_model.eval()

    manifest: dict[str, Any] = {
        "gate": "ASSET_STUDIO_AUTOMATIC_REGION_LOCALIZATION",
        "source": str(source_path),
        "source_size": [w, h],
        "device": str(device),
        "grounding_dino": {"repo": DINO_REPO, "revision": DINO_REVISION, "weight_sha256": DINO_WEIGHT_SHA256},
        "sam2": {"repo": SAM_REPO, "revision": SAM_REVISION, "weight_sha256": SAM_WEIGHT_SHA256},
        "tasks": {},
    }

    for task in TASKS:
        selected = selected_by_task[task.task_id]
        mask, sam_score = _best_sam_mask(sam_processor, sam_model, source, selected.box, device)
        area_ratio = float(mask.mean())
        if area_ratio <= 0.00005 or area_ratio >= 0.35:
            raise RuntimeError(f"SAM2 mask area is implausible for {task.task_id}: {area_ratio:.6f}")
        mask_path, overlay_path = _save_mask_assets(source, mask, task.task_id, output_dir)
        crop = _crop_bounds(task, selected.box, w, h)
        crop_img = source.crop(tuple(crop))
        crop_path = output_dir / f"{task.task_id}_crop.png"
        crop_img.save(crop_path)
        crop_mask = Image.fromarray(mask * 255, mode="L").crop(tuple(crop))
        crop_mask_path = output_dir / f"{task.task_id}_crop_mask.png"
        crop_mask.save(crop_mask_path)

        manifest["tasks"][task.task_id] = {
            "task": asdict(task),
            "selected": asdict(selected),
            "sam_iou_score": sam_score,
            "mask_area_ratio": area_ratio,
            "crop_box": crop,
            "detection_image": str(output_dir / f"{task.task_id}_detection.png"),
            "mask": str(mask_path),
            "mask_overlay": str(overlay_path),
            "crop": str(crop_path),
            "crop_mask": str(crop_mask_path),
            "candidate_count": len(candidates_by_task[task.task_id]),
            "candidates": [asdict(c) for c in candidates_by_task[task.task_id][:20]],
        }
        print(f"RUNNER64-LOCALIZER: {task.task_id} SAM mask area={area_ratio:.5f} iou={sam_score:.4f} crop={crop}", flush=True)

    del sam_model
    del sam_processor
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    manifest["elapsed_seconds"] = round(time.time() - started, 3)
    manifest_path = output_dir / "runner64_localization_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"RUNNER64-LOCALIZER: PASS -> {manifest_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
