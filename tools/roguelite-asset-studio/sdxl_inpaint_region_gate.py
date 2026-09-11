#!/usr/bin/env python3
"""Runner69: dedicated mask-native SDXL inpainting behind accepted automatic masks.

Runner68 proved that Qwen2511 respects the automatic latent region but does not
perform the requested structural removal reliably. Runner69 preserves the entire
perception/decomposition/compositor architecture and replaces only the regional
editor with SDXL Inpainting 0.1, a model explicitly trained for mask-native
inpainting.
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
from sdxl_inpaint_adapter import SDXLInpaintAdapter


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
    p.add_argument("--port", type=int, default=8196)
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
    # Dedicated inpainting gets a small hard expansion so it can synthesize the
    # immediate boundary instead of being forced to meet an exact antialiased edge.
    kernel = 7 if task_id == "plank" else 5
    return operation.convert("L").filter(ImageFilter.MaxFilter(kernel))


def final_allowed_mask(operation: Image.Image, task_id: str) -> Image.Image:
    kernel = 15 if task_id == "plank" else 11
    return operation.convert("L").filter(ImageFilter.MaxFilter(kernel)).filter(ImageFilter.GaussianBlur(2.0))


def _aligned_axis(low: int, high: int, limit: int, margin: int, multiple: int = 64) -> tuple[int, int]:
    desired_low = max(0, low - margin)
    desired_high = min(limit, high + margin)
    desired = max(multiple, desired_high - desired_low)
    length = min(limit, int(math.ceil(desired / multiple) * multiple))
    if length == limit:
        return 0, limit
    center = (low + high) / 2.0
    start = int(round(center - length / 2.0))
    start = max(0, min(start, limit - length))
    return start, start + length


def aligned_crop_box(mask: Image.Image, size: tuple[int, int], task_id: str) -> list[int]:
    x1, y1, x2, y2 = mask_bbox(mask)
    w, h = x2 - x1, y2 - y1
    if task_id == "plank":
        mx = max(96, int(round(w * 3.0)))
        my = max(64, int(round(h * 0.18)))
    else:
        mx = max(128, int(round(w * 1.35)))
        my = max(96, int(round(h * 2.0)))
    W, H = size
    ax1, ax2 = _aligned_axis(x1, x2, W, mx)
    ay1, ay2 = _aligned_axis(y1, y2, H, my)
    return [ax1, ay1, ax2, ay2]


def overlay(image: Image.Image, mask: Image.Image, color: tuple[int, int, int], alpha: int = 155) -> Image.Image:
    base = image.convert("RGBA")
    m = mask.convert("L")
    tint = Image.new("RGBA", image.size, (*color, 0))
    tint.putalpha(m.point(lambda v: int((v / 255.0) * alpha)))
    return Image.alpha_composite(base, tint).convert("RGB")


def composite_region(original: Image.Image, crop_box: list[int], raw_edit: Image.Image, crop_allowed: Image.Image) -> Image.Image:
    x1, y1, x2, y2 = crop_box
    cw, ch = x2 - x1, y2 - y1
    edited = raw_edit.convert("RGB")
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
    cell = 420
    label_h = 32
    cols = 6
    font = ImageFont.load_default()
    canvas = Image.new("RGB", (cols * cell, len(rows) * (cell + label_h)), (32, 32, 32))
    source = Image.open(original_path).convert("RGB")
    labels = ["ORIGINAL", "APPROVED TARGET", "INPAINT MASK", "SDXL RAW CROP", "SDXL REGION FINAL", "RUNNER68 FINAL"]
    for r, row in enumerate(rows):
        imgs = [
            source,
            Image.open(row["approved_overlay"]).convert("RGB"),
            Image.open(row["operation_overlay"]).convert("RGB"),
            Image.open(row["raw"]).convert("RGB"),
            Image.open(row["final"]).convert("RGB"),
            Image.open(row["runner68"]).convert("RGB"),
        ]
        for c, img in enumerate(imgs):
            thumb = img.copy()
            thumb.thumbnail((cell, cell), Image.Resampling.LANCZOS)
            tile = Image.new("RGB", (cell, cell), (205, 208, 208))
            tile.paste(thumb, ((cell - thumb.width) // 2, (cell - thumb.height) // 2))
            y = r * (cell + label_h)
            canvas.paste(tile, (c * cell, y))
            ImageDraw.Draw(canvas).text((c * cell + 5, y + cell + 8), f"{row['task'].upper()} / {labels[c]}", fill=(235, 235, 235), font=font)
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination)


def main() -> int:
    args = parse_args()
    print(f"RUNNER69: Asset Studio module root={MODULE_ROOT}", flush=True)

    original_path = (args.klein_workspace / "spike" / "flux2_klein_4b_t2i_probe.png").resolve()
    manifest66_path = (args.runner66_dir / "runner66_repeated_element_manifest.json").resolve()
    runner68_manifest = (args.qwen_workspace / "runner68_latent_mask_region_edit" / "runner68_latent_mask_manifest.json").resolve()
    for p in (original_path, manifest66_path, runner68_manifest):
        if not p.is_file():
            raise FileNotFoundError(p)
    m66 = json.loads(manifest66_path.read_text(encoding="utf-8"))
    if not bool(m66.get("auto_geometry_gate_pass")):
        raise RuntimeError("Runner66 automatic geometry gate is not true")

    original = Image.open(original_path).convert("RGB")
    approved_paths = {
        "plank": (args.runner66_dir / "plank_atomic_mask.png").resolve(),
        "strap": (args.runner66_dir / "strap_retained_mask.png").resolve(),
    }
    for p in approved_paths.values():
        if not p.is_file():
            raise FileNotFoundError(p)

    output_dir = (args.workspace / "runner69_precision_gate").resolve()
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
            "natural empty gap, preserve adjacent dark aged wooden planks and black iron hardware, realistic matching lighting and texture"
        ),
        "strap": (
            "aged dark wooden door visible underneath, broken black wrought iron strap with the middle section missing, two short original iron ends remain on left and right, "
            "natural chipped fracture ends, preserve the wood grain and surrounding medieval door"
        ),
    }
    negatives = {
        "plank": "new plank, replacement wood, bridge across gap, extra boards, new hardware, text, logo, people, bright colors",
        "strap": "replacement bar, continuous iron bar, new hinge, extra metal, red paint, text, logo, people, bright colors",
    }

    records: list[dict[str, Any]] = []
    rows: list[dict[str, Path]] = []
    started_all = time.time()

    for task_id in ("plank", "strap"):
        approved = Image.open(approved_paths[task_id]).convert("L")
        operation = approved if task_id == "plank" else strap_break_core(approved)
        inpaint = model_inpaint_mask(operation, task_id)
        allowed = final_allowed_mask(operation, task_id)
        crop_box = aligned_crop_box(approved, original.size, task_id)
        x1, y1, x2, y2 = crop_box
        source_crop = original.crop((x1, y1, x2, y2)).convert("RGB")
        crop_inpaint = inpaint.crop((x1, y1, x2, y2)).convert("L")
        crop_allowed = allowed.crop((x1, y1, x2, y2)).convert("L")

        source_crop_path = output_dir / f"{task_id}_source_crop.png"
        inpaint_mask_path = output_dir / f"{task_id}_inpaint_mask.png"
        approved_overlay_path = output_dir / f"{task_id}_approved_target_overlay.png"
        operation_overlay_path = output_dir / f"{task_id}_inpaint_operation_overlay.png"
        source_crop.save(source_crop_path)
        crop_inpaint.save(inpaint_mask_path)
        overlay(original, approved, (235, 45, 45), 155).save(approved_overlay_path)
        overlay(original, operation, (0, 210, 255), 180).save(operation_overlay_path)

        rw, rh = source_crop.size
        if rw % 16 or rh % 16:
            raise RuntimeError(f"aligned crop is not divisible by 16: {source_crop.size}")
        request = StaticGenerationRequest(
            job_id=f"runner69_sdxl_inpaint_{task_id}",
            asset_type="architecture_module",
            output_contract="static_master",
            prompt=prompts[task_id],
            negative=negatives[task_id],
            references=(ReferenceInput("previous_approved_state", source_crop_path),),
            width=rw,
            height=rh,
            steps=30,
            cfg=6.0,
            sampler="dpmpp_2m",
            seed=0,
        )
        raw_path = output_dir / f"{task_id}_sdxl_raw_crop.png"
        print(f"RUNNER69: {task_id} -> SDXL dedicated inpaint submitting ({rw}x{rh})", flush=True)
        result = adapter.generate_masked(request, inpaint_mask_path, raw_path)
        print(f"RUNNER69: {task_id} complete in {result.elapsed_seconds:.3f}s", flush=True)

        raw = Image.open(raw_path).convert("RGB")
        final = composite_region(original, crop_box, raw, crop_allowed)
        final_path = output_dir / f"{task_id}_sdxl_region_final.png"
        final.save(final_path)
        allowed_path = output_dir / f"{task_id}_allowed_region.png"
        allowed.save(allowed_path)
        metrics = difference_metrics(original, final, allowed)

        previous = args.qwen_workspace / "runner68_latent_mask_region_edit" / f"{task_id}_latent_mask_region_final.png"
        if not previous.is_file():
            raise FileNotFoundError(previous)
        records.append({
            "task": task_id,
            "prompt": prompts[task_id],
            "negative": negatives[task_id],
            "approved_mask": str(approved_paths[task_id]),
            "approved_mask_sha256": sha256_file(approved_paths[task_id]),
            "approved_bbox": mask_bbox(approved),
            "operation_bbox": mask_bbox(operation),
            "operation_contract": "full atomic plank" if task_id == "plank" else "central 40 percent of approved strap",
            "crop_box": crop_box,
            "crop_size": [rw, rh],
            "inpaint_mask": str(inpaint_mask_path),
            "inpaint_mask_sha256": sha256_file(inpaint_mask_path),
            "elapsed_seconds": result.elapsed_seconds,
            "raw_edit": str(raw_path),
            "raw_edit_sha256": sha256_file(raw_path),
            "final": str(final_path),
            "final_sha256": sha256_file(final_path),
            "allowed_region": str(allowed_path),
            "difference_from_original": metrics,
        })
        rows.append({
            "task": task_id,
            "approved_overlay": approved_overlay_path,
            "operation_overlay": operation_overlay_path,
            "raw": raw_path,
            "final": final_path,
            "runner68": previous,
        })

    sheet = output_dir / "runner69_sdxl_inpaint_contact_sheet.png"
    contact_sheet(original_path, rows, sheet)
    manifest = {
        "gate": "ASSET_STUDIO_DEDICATED_MASK_NATIVE_INPAINT",
        "technical_status": "COMPLETE",
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "source": str(original_path),
        "source_sha256": sha256_file(original_path),
        "runner66_manifest": str(manifest66_path),
        "runner66_manifest_sha256": sha256_file(manifest66_path),
        "runner68_manifest": str(runner68_manifest),
        "runner68_manifest_sha256": sha256_file(runner68_manifest),
        "comfy_commit": args.comfy_commit,
        "editor": "sdxl_inpaint_0_1_fp16",
        "recipe": {"steps": 30, "cfg": 6.0, "sampler": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0},
        "control_contract": "Runner66 approved automatic operation masks -> dedicated SDXL InpaintModelConditioning -> deterministic full-resolution composite; no manual mask/box",
        "results": records,
        "contact_sheet": str(sheet),
        "contact_sheet_sha256": sha256_file(sheet),
        "elapsed_total_seconds": round(time.time() - started_all, 3),
        "visual_pass_contract": {
            "plank": "the atomic plank is absent and the masked region becomes a clean same-width opening/background continuation; no replacement board",
            "strap": "the central section of the approved strap is absent, wood is reconstructed underneath, and both outside strap ends remain",
            "preservation": "unrelated geometry remains source-authoritative through deterministic final composite",
        },
    }
    manifest_path = output_dir / "runner69_sdxl_inpaint_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("RUNNER69-SDXL-INPAINT: PASS - TECHNICAL MASK-NATIVE MATRIX COMPLETE / VISUAL VERDICT PENDING", flush=True)
    print(f"Contact sheet: {sheet}", flush=True)
    print(f"Manifest: {manifest_path}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        import traceback
        print(f"RUNNER69-SDXL-INPAINT-FAIL: {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc(file=sys.stdout)
        raise SystemExit(1)
