#!/usr/bin/env python3
"""Runner70: SDXL Inpainting 0.1 resolution-parity gate.

Runner69 used native 256x512 / 384x256 contextual crops even though the official
SDXL Inpainting 0.1 model was trained at 1024x1024. Runner70 changes only the
model-input geometry: it extracts a 512x512 source-authoritative context square
around the accepted automatic operation target, upscales image+mask together to
1024x1024, runs the exact same SDXL inpainting recipe, downsamples the generated
result back to the 512x512 source coordinate system, then applies the same
full-resolution deterministic composite.

No new model, localization, segmentation, manual mask, prompt family, sampler,
seed or final-compositor hypothesis is introduced.
"""

from __future__ import annotations

import argparse
import hashlib
import json
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
from sdxl_inpaint_adapter import SDXLInpaintAdapter

MODEL_SIZE = 1024
SOURCE_CONTEXT_SIZE = 512


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
    p.add_argument("--qwen-workspace", type=Path, required=True)
    p.add_argument("--klein-workspace", type=Path, required=True)
    p.add_argument("--runner66-dir", type=Path, required=True)
    p.add_argument("--port", type=int, default=8197)
    p.add_argument("--timeout-minutes", type=int, default=180)
    p.add_argument("--comfy-commit", required=True)
    return p.parse_args()


def mask_bbox(mask: Image.Image) -> list[int]:
    arr = np.asarray(mask.convert("L"), dtype=np.uint8)
    ys, xs = np.where(arr > 8)
    if len(xs) == 0:
        raise ValueError("automatic mask is empty")
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def strap_break_core(mask: Image.Image) -> Image.Image:
    arr = np.asarray(mask.convert("L"), dtype=np.uint8)
    x1, y1, x2, y2 = mask_bbox(mask)
    width = x2 - x1
    cx1 = int(round(x1 + 0.30 * width))
    cx2 = int(round(x1 + 0.70 * width))
    core = np.zeros_like(arr)
    core[:, cx1:cx2] = arr[:, cx1:cx2]
    if not np.any(core > 8):
        raise ValueError("derived strap break core is empty")
    return Image.fromarray(core, mode="L")


def model_inpaint_mask(operation: Image.Image, task_id: str) -> Image.Image:
    kernel = 7 if task_id == "plank" else 5
    return operation.convert("L").filter(ImageFilter.MaxFilter(kernel))


def final_allowed_mask(operation: Image.Image, task_id: str) -> Image.Image:
    kernel = 15 if task_id == "plank" else 11
    return operation.convert("L").filter(ImageFilter.MaxFilter(kernel)).filter(ImageFilter.GaussianBlur(2.0))


def square_context_box(mask: Image.Image, size: tuple[int, int], side: int = SOURCE_CONTEXT_SIZE) -> list[int]:
    """Return a square source-coordinate crop containing the full target.

    The source is 768x768 in this gate and side=512. If a future source is
    smaller, fail closed rather than silently invent padding outside the asset.
    """
    W, H = size
    if W < side or H < side:
        raise ValueError(f"source {size} is smaller than required square context {side}")
    x1, y1, x2, y2 = mask_bbox(mask)
    if (x2 - x1) > side or (y2 - y1) > side:
        raise ValueError(f"target bbox {x1,y1,x2,y2} does not fit {side}x{side} context")
    cx = (x1 + x2) / 2.0
    cy = (y1 + y2) / 2.0
    sx = int(round(cx - side / 2.0))
    sy = int(round(cy - side / 2.0))
    sx = max(0, min(sx, W - side))
    sy = max(0, min(sy, H - side))
    box = [sx, sy, sx + side, sy + side]
    if not (box[0] <= x1 and box[1] <= y1 and box[2] >= x2 and box[3] >= y2):
        raise RuntimeError(f"square context failed to contain target: target={x1,y1,x2,y2} box={box}")
    return box


def overlay(image: Image.Image, mask: Image.Image, color: tuple[int, int, int], alpha: int = 155) -> Image.Image:
    base = image.convert("RGBA")
    m = mask.convert("L")
    tint = Image.new("RGBA", image.size, (*color, 0))
    tint.putalpha(m.point(lambda v: int((v / 255.0) * alpha)))
    return Image.alpha_composite(base, tint).convert("RGB")


def composite_region(original: Image.Image, crop_box: list[int], source_scale_edit: Image.Image, crop_allowed: Image.Image) -> Image.Image:
    x1, y1, x2, y2 = crop_box
    cw, ch = x2 - x1, y2 - y1
    edited = source_scale_edit.convert("RGB")
    if edited.size != (cw, ch):
        edited = edited.resize((cw, ch), Image.Resampling.LANCZOS)
    orig_crop = original.crop((x1, y1, x2, y2)).convert("RGB")
    blend = crop_allowed.convert("L")
    if blend.size != (cw, ch):
        blend = blend.resize((cw, ch), Image.Resampling.LANCZOS)
    merged = Image.composite(edited, orig_crop, blend)
    full = original.copy().convert("RGB")
    full.paste(merged, (x1, y1))
    return full


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


def contact_sheet(original_path: Path, rows: list[dict[str, Path]], destination: Path) -> None:
    cell = 400
    label_h = 34
    cols = 7
    font = ImageFont.load_default()
    canvas = Image.new("RGB", (cols * cell, len(rows) * (cell + label_h)), (32, 32, 32))
    source = Image.open(original_path).convert("RGB")
    labels = [
        "ORIGINAL",
        "APPROVED TARGET",
        "1024 INPUT",
        "1024 MASK",
        "1024 RAW",
        "1024 FINAL",
        "RUNNER69 FINAL",
    ]
    for r, row in enumerate(rows):
        imgs = [
            source,
            Image.open(row["approved_overlay"]).convert("RGB"),
            Image.open(row["model_source"]).convert("RGB"),
            Image.open(row["model_mask"]).convert("RGB"),
            Image.open(row["raw"]).convert("RGB"),
            Image.open(row["final"]).convert("RGB"),
            Image.open(row["runner69"]).convert("RGB"),
        ]
        for c, img in enumerate(imgs):
            thumb = img.copy()
            thumb.thumbnail((cell, cell), Image.Resampling.LANCZOS)
            tile = Image.new("RGB", (cell, cell), (205, 208, 208))
            tile.paste(thumb, ((cell - thumb.width) // 2, (cell - thumb.height) // 2))
            y = r * (cell + label_h)
            canvas.paste(tile, (c * cell, y))
            ImageDraw.Draw(canvas).text((c * cell + 5, y + cell + 9), f"{row['task'].upper()} / {labels[c]}", fill=(235,235,235), font=font)
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination)


def main() -> int:
    args = parse_args()
    print(f"RUNNER70: Asset Studio module root={MODULE_ROOT}", flush=True)

    original_path = (args.klein_workspace / "spike" / "flux2_klein_4b_t2i_probe.png").resolve()
    manifest66_path = (args.runner66_dir / "runner66_repeated_element_manifest.json").resolve()
    runner69_manifest_path = (args.workspace / "runner69_precision_gate" / "runner69_sdxl_inpaint_manifest.json").resolve()
    for p in (original_path, manifest66_path, runner69_manifest_path):
        if not p.is_file():
            raise FileNotFoundError(p)
    m66 = json.loads(manifest66_path.read_text(encoding="utf-8"))
    if not bool(m66.get("auto_geometry_gate_pass")):
        raise RuntimeError("Runner66 automatic geometry gate is not true")
    m69 = json.loads(runner69_manifest_path.read_text(encoding="utf-8"))
    if str(m69.get("technical_status")) != "COMPLETE":
        raise RuntimeError("Runner69 technical evidence is not complete")

    original = Image.open(original_path).convert("RGB")
    approved_paths = {
        "plank": (args.runner66_dir / "plank_atomic_mask.png").resolve(),
        "strap": (args.runner66_dir / "strap_retained_mask.png").resolve(),
    }
    for p in approved_paths.values():
        if not p.is_file():
            raise FileNotFoundError(p)

    output_dir = (args.workspace / "runner70_1024_parity_gate").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    adapter = SDXLInpaintAdapter(
        comfy_root=args.comfy_root,
        base_url=f"http://127.0.0.1:{args.port}",
        timeout_minutes=args.timeout_minutes,
    )
    adapter.verify_runtime()

    prompts = {
        "plank": (
            "medieval ruined wooden double door, exact surrounding material continuity, empty narrow vertical opening through the doorway where one plank was removed, "
            "natural empty gap showing the same neutral space behind the door, preserve adjacent dark aged wooden planks and black iron hardware, realistic matching lighting and texture"
        ),
        "strap": (
            "aged dark wooden door visible underneath, broken black wrought iron strap with the middle section missing, two short original iron ends remain on left and right, "
            "natural chipped fracture ends, reconstruct only matching aged wood where the metal is absent, preserve surrounding medieval door"
        ),
    }
    negatives = {
        "plank": "new plank, replacement wood, bridge across gap, shiny metal, chrome, extra boards, new hardware, text, logo, people, bright colors",
        "strap": "replacement bar, continuous iron bar, new hinge, extra metal, shiny metal, chrome, red paint, text, logo, people, bright colors",
    }

    records: list[dict[str, Any]] = []
    rows: list[dict[str, Path]] = []
    started_all = time.time()

    for task_id in ("plank", "strap"):
        approved = Image.open(approved_paths[task_id]).convert("L")
        operation = approved if task_id == "plank" else strap_break_core(approved)
        inpaint_full = model_inpaint_mask(operation, task_id)
        allowed_full = final_allowed_mask(operation, task_id)
        crop_box = square_context_box(approved, original.size, SOURCE_CONTEXT_SIZE)
        x1, y1, x2, y2 = crop_box

        source_crop = original.crop((x1, y1, x2, y2)).convert("RGB")
        crop_inpaint = inpaint_full.crop((x1, y1, x2, y2)).convert("L")
        crop_allowed = allowed_full.crop((x1, y1, x2, y2)).convert("L")
        if source_crop.size != (SOURCE_CONTEXT_SIZE, SOURCE_CONTEXT_SIZE):
            raise RuntimeError(f"source context is not {SOURCE_CONTEXT_SIZE} square: {source_crop.size}")

        model_source = source_crop.resize((MODEL_SIZE, MODEL_SIZE), Image.Resampling.LANCZOS)
        model_mask = crop_inpaint.resize((MODEL_SIZE, MODEL_SIZE), Image.Resampling.NEAREST)
        if np.asarray(model_mask, dtype=np.uint8).max() < 250:
            raise RuntimeError(f"scaled model mask is unexpectedly non-opaque for {task_id}")

        source_crop_path = output_dir / f"{task_id}_source_context_512.png"
        model_source_path = output_dir / f"{task_id}_model_source_1024.png"
        model_mask_path = output_dir / f"{task_id}_inpaint_mask_1024.png"
        approved_overlay_path = output_dir / f"{task_id}_approved_target_overlay.png"
        source_crop.save(source_crop_path)
        model_source.save(model_source_path)
        model_mask.save(model_mask_path)
        overlay(original, approved, (235, 45, 45), 155).save(approved_overlay_path)

        request = StaticGenerationRequest(
            job_id=f"runner70_sdxl_1024_{task_id}",
            asset_type="architecture_module",
            output_contract="static_master",
            prompt=prompts[task_id],
            negative=negatives[task_id],
            references=(ReferenceInput("previous_approved_state", model_source_path),),
            width=MODEL_SIZE,
            height=MODEL_SIZE,
            steps=30,
            cfg=6.0,
            sampler="dpmpp_2m",
            seed=0,
        )
        raw_path = output_dir / f"{task_id}_sdxl_1024_raw.png"
        print(f"RUNNER70: {task_id} -> SDXL dedicated inpaint submitting ({MODEL_SIZE}x{MODEL_SIZE})", flush=True)
        result = adapter.generate_masked(request, model_mask_path, raw_path)
        print(f"RUNNER70: {task_id} complete in {result.elapsed_seconds:.3f}s", flush=True)

        raw_model = Image.open(raw_path).convert("RGB")
        source_scale_edit = raw_model.resize((SOURCE_CONTEXT_SIZE, SOURCE_CONTEXT_SIZE), Image.Resampling.LANCZOS)
        source_scale_edit_path = output_dir / f"{task_id}_sdxl_1024_downsampled_512.png"
        source_scale_edit.save(source_scale_edit_path)

        final = composite_region(original, crop_box, source_scale_edit, crop_allowed)
        final_path = output_dir / f"{task_id}_sdxl_1024_region_final.png"
        final.save(final_path)
        allowed_path = output_dir / f"{task_id}_allowed_region.png"
        allowed_full.save(allowed_path)
        metrics = difference_metrics(original, final, allowed_full)

        runner69 = args.workspace / "runner69_precision_gate" / f"{task_id}_sdxl_region_final.png"
        if not runner69.is_file():
            raise FileNotFoundError(runner69)

        records.append({
            "task": task_id,
            "prompt": prompts[task_id],
            "negative": negatives[task_id],
            "approved_mask": str(approved_paths[task_id]),
            "approved_mask_sha256": sha256_file(approved_paths[task_id]),
            "approved_bbox": mask_bbox(approved),
            "operation_bbox": mask_bbox(operation),
            "operation_contract": "full atomic plank" if task_id == "plank" else "central 40 percent of approved strap",
            "source_context_box": crop_box,
            "source_context_size": [SOURCE_CONTEXT_SIZE, SOURCE_CONTEXT_SIZE],
            "model_input_size": [MODEL_SIZE, MODEL_SIZE],
            "model_scale_factor": MODEL_SIZE / SOURCE_CONTEXT_SIZE,
            "model_source": str(model_source_path),
            "model_source_sha256": sha256_file(model_source_path),
            "model_mask": str(model_mask_path),
            "model_mask_sha256": sha256_file(model_mask_path),
            "elapsed_seconds": result.elapsed_seconds,
            "raw_edit": str(raw_path),
            "raw_edit_sha256": sha256_file(raw_path),
            "downsampled_edit": str(source_scale_edit_path),
            "downsampled_edit_sha256": sha256_file(source_scale_edit_path),
            "final": str(final_path),
            "final_sha256": sha256_file(final_path),
            "allowed_region": str(allowed_path),
            "difference_from_original": metrics,
        })
        rows.append({
            "task": task_id,
            "approved_overlay": approved_overlay_path,
            "model_source": model_source_path,
            "model_mask": model_mask_path,
            "raw": raw_path,
            "final": final_path,
            "runner69": runner69,
        })

    sheet = output_dir / "runner70_sdxl_1024_contact_sheet.png"
    contact_sheet(original_path, rows, sheet)
    manifest = {
        "gate": "ASSET_STUDIO_SDXL_INPAINT_1024_RESOLUTION_PARITY",
        "technical_status": "COMPLETE",
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "source": str(original_path),
        "source_sha256": sha256_file(original_path),
        "runner66_manifest": str(manifest66_path),
        "runner66_manifest_sha256": sha256_file(manifest66_path),
        "runner69_manifest": str(runner69_manifest_path),
        "runner69_manifest_sha256": sha256_file(runner69_manifest_path),
        "editor": "sdxl_inpaint_0_1_fp16",
        "resolution_hypothesis": "Runner69 native crops were 256x512 and 384x256; Runner70 uses source-authoritative 512x512 context upscaled jointly with mask to the model training regime 1024x1024 before downsampling and deterministic composite",
        "recipe": {"steps": 30, "cfg": 6.0, "sampler": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0, "seed": 0},
        "results": records,
        "contact_sheet": str(sheet),
        "contact_sheet_sha256": sha256_file(sheet),
        "elapsed_total_seconds": round(time.time() - started_all, 3),
        "visual_pass_contract": {
            "plank": "one atomic plank is absent and reads as a clean narrow opening without shiny/reconstructed vertical artifact",
            "strap": "central strap section is absent and matching aged wood is visible while both external strap ends survive",
            "preservation": "unrelated geometry remains source-authoritative through deterministic final composite",
        },
    }
    manifest_path = output_dir / "runner70_sdxl_1024_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("RUNNER70-SDXL-1024: PASS - TECHNICAL RESOLUTION-PARITY MATRIX COMPLETE / VISUAL VERDICT PENDING", flush=True)
    print(f"Contact sheet: {sheet}", flush=True)
    print(f"Manifest: {manifest_path}", flush=True)
    print(f"Total elapsed: {manifest['elapsed_total_seconds']:.3f}s", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        import traceback
        print(f"RUNNER70-PYTHON-FAIL: {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc(file=sys.stdout)
        raise SystemExit(1)
