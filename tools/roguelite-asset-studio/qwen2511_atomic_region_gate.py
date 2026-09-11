#!/usr/bin/env python3
"""Runner67: Qwen-Image-Edit-2511 behind approved automatic atomic masks.

Consumes Runner66 evidence only. No perception is executed here and the user draws
no box/mask. Qwen edits a contextual crop plus an automatically generated target
guide; the final full-resolution composite is deterministically limited to the
approved atomic mask neighborhood.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

MODULE_ROOT = Path(__file__).resolve().parent
if str(MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE_ROOT))

from adapter_protocol import ReferenceInput, StaticGenerationRequest
from qwen_image_edit_2511_adapter import QwenImageEdit2511Adapter


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--comfy-root", type=Path, required=True)
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--klein-workspace", type=Path, required=True)
    p.add_argument("--runner66-dir", type=Path, required=True)
    p.add_argument("--port", type=int, default=8194)
    p.add_argument("--timeout-minutes", type=int, default=480)
    p.add_argument("--comfy-commit", required=True)
    return p.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def mask_bbox(mask: Image.Image) -> list[int]:
    arr = np.asarray(mask.convert("L"), dtype=np.uint8)
    ys, xs = np.where(arr > 16)
    if xs.size == 0:
        raise RuntimeError("automatic mask is empty")
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def context_crop_box(mask_box: list[int], size: tuple[int, int], task_id: str) -> list[int]:
    w, h = size
    x1, y1, x2, y2 = mask_box
    bw = max(1, x2 - x1)
    bh = max(1, y2 - y1)
    if task_id == "plank":
        mx = max(110, int(bw * 3.2))
        my = max(55, int(bh * 0.18))
    else:
        mx = max(95, int(bw * 1.1))
        my = max(80, int(bh * 2.0))
    return [max(0, x1 - mx), max(0, y1 - my), min(w, x2 + mx), min(h, y2 + my)]


def make_target_guide(crop: Image.Image, mask: Image.Image) -> Image.Image:
    base = crop.convert("RGBA")
    tint = Image.new("RGBA", crop.size, (255, 32, 32, 0))
    alpha = mask.convert("L").point(lambda v: int(v * 0.58))
    tint.putalpha(alpha)
    return Image.alpha_composite(base, tint).convert("RGB")


def allowed_blend_mask(mask: Image.Image, task_id: str) -> Image.Image:
    base = mask.convert("L")
    # Small deterministic reconstruction margin. The entire asset outside this
    # neighborhood remains source pixels by construction.
    if task_id == "plank":
        return base.filter(ImageFilter.MaxFilter(21)).filter(ImageFilter.GaussianBlur(4.0))
    return base.filter(ImageFilter.MaxFilter(19)).filter(ImageFilter.GaussianBlur(3.5))


def composite_region(
    original: Image.Image,
    crop_box: list[int],
    raw_edit: Image.Image,
    crop_mask: Image.Image,
    task_id: str,
) -> tuple[Image.Image, Image.Image]:
    x1, y1, x2, y2 = crop_box
    cw, ch = x2 - x1, y2 - y1
    edited = raw_edit.convert("RGB").resize((cw, ch), Image.Resampling.LANCZOS)
    orig_crop = original.crop((x1, y1, x2, y2)).convert("RGB")
    blend = allowed_blend_mask(crop_mask.resize((cw, ch), Image.Resampling.NEAREST), task_id)
    merged = Image.composite(edited, orig_crop, blend)
    full = original.copy().convert("RGB")
    full.paste(merged, (x1, y1))
    return full, blend


def full_allowed_mask(size: tuple[int, int], crop_box: list[int], crop_blend: Image.Image) -> Image.Image:
    m = Image.new("L", size, 0)
    m.paste(crop_blend, (crop_box[0], crop_box[1]))
    return m


def difference_metrics(a: Image.Image, b: Image.Image, allowed: Image.Image) -> dict[str, float]:
    aa = np.asarray(a.convert("RGB"), dtype=np.int16)
    bb = np.asarray(b.convert("RGB"), dtype=np.int16)
    delta = np.abs(aa - bb).mean(axis=2)
    m = np.asarray(allowed.convert("L"), dtype=np.uint8) > 2
    outside = ~m
    inside = m
    return {
        "mean_abs_rgb": float(np.abs(aa - bb).mean()),
        "changed_ratio_gt_12": float((delta > 12).mean()),
        "changed_ratio_gt_24": float((delta > 24).mean()),
        "inside_allowed_changed_ratio_gt_12": float((delta[inside] > 12).mean()) if inside.any() else 0.0,
        "outside_allowed_mean_abs": float(delta[outside].mean()) if outside.any() else 0.0,
        "outside_allowed_changed_ratio_gt_12": float((delta[outside] > 12).mean()) if outside.any() else 0.0,
    }


def make_overlay(original: Image.Image, mask: Image.Image) -> Image.Image:
    base = original.convert("RGBA")
    tint = Image.new("RGBA", original.size, (255, 32, 32, 0))
    tint.putalpha(mask.convert("L").point(lambda v: int(v * 0.48)))
    return Image.alpha_composite(base, tint).convert("RGB")


def make_contact_sheet(original_path: Path, rows: list[dict[str, Path]], destination: Path) -> None:
    cell = 448
    label_h = 30
    labels = ["ORIGINAL", "APPROVED AUTO MASK", "QWEN RAW CROP", "REGION FINAL", "RUNNER63 GLOBAL"]
    source = Image.open(original_path).convert("RGB")
    canvas = Image.new("RGB", (cell * len(labels), len(rows) * (cell + label_h)), (32, 32, 32))
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(canvas)
    for r, row in enumerate(rows):
        images = [
            source,
            Image.open(row["overlay"]).convert("RGB"),
            Image.open(row["raw"]).convert("RGB"),
            Image.open(row["final"]).convert("RGB"),
            Image.open(row["global"]).convert("RGB"),
        ]
        for c, img in enumerate(images):
            thumb = img.copy()
            thumb.thumbnail((cell, cell), Image.Resampling.LANCZOS)
            tile = Image.new("RGB", (cell, cell), (205, 208, 208))
            tile.paste(thumb, ((cell - thumb.width)//2, (cell - thumb.height)//2))
            y = r * (cell + label_h)
            canvas.paste(tile, (c * cell, y))
            draw.text((c * cell + 5, y + cell + 7), f"{row['task'].upper()} / {labels[c]}", fill=(235,235,235), font=font)
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination)


def main() -> int:
    args = parse_args()
    original_path = (args.klein_workspace / "spike" / "flux2_klein_4b_t2i_probe.png").resolve()
    runner66_manifest_path = (args.runner66_dir / "runner66_repeated_element_manifest.json").resolve()
    if not original_path.is_file():
        raise FileNotFoundError(original_path)
    if not runner66_manifest_path.is_file():
        raise FileNotFoundError(runner66_manifest_path)

    r66 = load_json(runner66_manifest_path)
    if not bool(r66.get("auto_geometry_gate_pass")):
        raise RuntimeError("Runner66 automatic geometry gate did not pass")

    original = Image.open(original_path).convert("RGB")
    output_dir = (args.workspace / "runner67_atomic_region_edit").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    masks = {
        "plank": Path(r66["outputs"]["plank_atomic_mask"]),
        "strap": Path(r66["outputs"]["strap_retained_mask"]),
    }
    for p in masks.values():
        if not p.is_file():
            raise FileNotFoundError(p)

    global_runner63 = {
        "plank": args.workspace / "qwen2511_precision_gate" / "qwen2511_atomic_plank_steps20.png",
        "strap": args.workspace / "qwen2511_precision_gate" / "qwen2511_atomic_strap_steps20.png",
    }
    for p in global_runner63.values():
        if not p.is_file():
            raise FileNotFoundError(p)

    prompts = {
        "plank": (
            "Image 1 is the source crop. Image 2 is the same crop with a translucent RED overlay marking exactly ONE vertical wooden plank. "
            "The red is a locator only; never reproduce red. Remove exactly the marked plank from top to bottom and create a narrow open gap of the same width. "
            "Do not remove or widen neighboring planks. Preserve the door frame, stone, vines and all unrelated geometry. Where iron hardware crosses the removed plank, keep the surrounding hardware coherent without redesigning the door."
        ),
        "strap": (
            "Image 1 is the source crop. Image 2 is the same crop with a translucent RED overlay marking exactly ONE lower-right horizontal iron strap. "
            "The red is a locator only; never reproduce red. Break only that marked strap by removing a clear middle section and leaving two short snapped or bent ends. "
            "Do not create a replacement bar and do not alter other hinges, straps, planks, stone, vines or door proportions."
        ),
    }

    adapter = QwenImageEdit2511Adapter(
        comfy_root=args.comfy_root,
        base_url=f"http://127.0.0.1:{args.port}",
        timeout_minutes=args.timeout_minutes,
    )
    adapter.verify_runtime()

    rows: list[dict[str, Path]] = []
    records: list[dict[str, Any]] = []
    started_all = time.time()

    for task_id in ("plank", "strap"):
        full_mask = Image.open(masks[task_id]).convert("L")
        bbox = mask_bbox(full_mask)
        crop_box = context_crop_box(bbox, original.size, task_id)
        x1, y1, x2, y2 = crop_box
        crop = original.crop((x1, y1, x2, y2)).convert("RGB")
        crop_mask = full_mask.crop((x1, y1, x2, y2)).convert("L")

        crop_path = output_dir / f"{task_id}_source_crop.png"
        crop_mask_path = output_dir / f"{task_id}_crop_mask.png"
        overlay_path = output_dir / f"{task_id}_approved_mask_overlay.png"
        guide_path = output_dir / f"{task_id}_target_guide.png"
        crop.save(crop_path)
        crop_mask.save(crop_mask_path)
        make_overlay(original, full_mask).save(overlay_path)
        make_target_guide(crop, crop_mask).save(guide_path)

        rw = max(16, int(math.ceil(crop.width / 16.0) * 16))
        rh = max(16, int(math.ceil(crop.height / 16.0) * 16))
        raw_path = output_dir / f"{task_id}_raw_crop_edit.png"
        request = StaticGenerationRequest(
            job_id=f"runner67_atomic_region_{task_id}",
            asset_type="architecture_module",
            output_contract="static_master",
            prompt=prompts[task_id],
            negative="text, logo, UI, people, creatures, red paint, red overlay copied into result, global redesign",
            references=(
                ReferenceInput("previous_approved_state", crop_path),
                ReferenceInput("structure", guide_path),
            ),
            width=rw,
            height=rh,
            steps=20,
            cfg=4.0,
            sampler="euler",
            seed=0,
        )
        print(f"RUNNER67: {task_id} -> Qwen2511 atomic regional edit submitting", flush=True)
        result = adapter.generate(request, raw_path)
        print(f"RUNNER67: {task_id} complete in {result.elapsed_seconds:.3f}s", flush=True)

        raw = Image.open(raw_path).convert("RGB")
        final, crop_blend = composite_region(original, crop_box, raw, crop_mask, task_id)
        final_path = output_dir / f"{task_id}_atomic_region_final.png"
        final.save(final_path)
        allowed = full_allowed_mask(original.size, crop_box, crop_blend)
        allowed_path = output_dir / f"{task_id}_allowed_region.png"
        allowed.save(allowed_path)
        metrics = difference_metrics(original, final, allowed)

        records.append({
            "task": task_id,
            "prompt": prompts[task_id],
            "approved_mask": str(masks[task_id]),
            "approved_mask_sha256": sha256_file(masks[task_id]),
            "mask_bbox": bbox,
            "crop_box": crop_box,
            "qwen_elapsed_seconds": result.elapsed_seconds,
            "raw_edit": str(raw_path),
            "raw_edit_sha256": sha256_file(raw_path),
            "final": str(final_path),
            "final_sha256": sha256_file(final_path),
            "allowed_region": str(allowed_path),
            "difference_from_original": metrics,
        })
        rows.append({"task": task_id, "overlay": overlay_path, "raw": raw_path, "final": final_path, "global": global_runner63[task_id]})

    sheet_path = output_dir / "runner67_atomic_region_contact_sheet.png"
    make_contact_sheet(original_path, rows, sheet_path)
    manifest = {
        "gate": "ASSET_STUDIO_QWEN2511_APPROVED_ATOMIC_REGION_EDIT",
        "technical_status": "COMPLETE",
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "source": str(original_path),
        "source_sha256": sha256_file(original_path),
        "runner66_manifest": str(runner66_manifest_path),
        "runner66_manifest_sha256": sha256_file(runner66_manifest_path),
        "comfy_commit": args.comfy_commit,
        "editor": "qwen_image_edit_2511_fp8mixed",
        "editor_recipe": {"steps": 20, "cfg": 4.0, "sampler": "euler", "scheduler": "simple", "denoise": 1.0},
        "control_contract": "Runner66 approved automatic masks -> contextual Qwen edit -> deterministic dilation/feather -> full-resolution composite; no user-drawn mask or box",
        "results": records,
        "contact_sheet": str(sheet_path),
        "contact_sheet_sha256": sha256_file(sheet_path),
        "elapsed_total_seconds": round(time.time() - started_all, 3),
        "visual_pass_contract": {
            "plank": "Remove only the automatically isolated one-plank member and create a narrow same-width opening; neighboring planks/door/frame remain stable.",
            "strap": "Break only the automatically localized lower-right strap with no replacement bar and no unrelated redesign.",
            "outside_region": "Pixels outside the automatic allowed neighborhood remain source pixels by construction.",
        },
    }
    manifest_path = output_dir / "runner67_atomic_region_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("RUNNER67-QWEN2511-ATOMIC-REGION: PASS - TECHNICAL EDIT MATRIX COMPLETE / VISUAL VERDICT PENDING", flush=True)
    print(f"Contact sheet: {sheet_path}", flush=True)
    print(f"Manifest: {manifest_path}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        import traceback
        print(f"RUNNER67-FAIL: {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc(file=sys.stdout)
        raise SystemExit(1)
