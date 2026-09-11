#!/usr/bin/env python3
"""Runner68: automatic latent-mask regional editing with Qwen2511.

Consumes only automatic Runner66 control data. No user box/mask is accepted and
no colored target guide is passed to Qwen. The source crop is the sole semantic
image reference; the automatic operation mask is attached to the source latent
through native ComfyUI SetLatentNoiseMask.
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
from qwen_image_edit_2511_masked_adapter import QwenImageEdit2511MaskedAdapter


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
    p.add_argument("--port", type=int, default=8195)
    p.add_argument("--timeout-minutes", type=int, default=480)
    p.add_argument("--comfy-commit", required=True)
    return p.parse_args()


def mask_bbox(mask: Image.Image) -> list[int]:
    arr = np.asarray(mask.convert("L"), dtype=np.uint8)
    ys, xs = np.where(arr > 8)
    if len(xs) == 0:
        raise ValueError("automatic mask is empty")
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def crop_box_for(mask: Image.Image, size: tuple[int, int], task_id: str) -> list[int]:
    x1, y1, x2, y2 = mask_bbox(mask)
    w, h = x2 - x1, y2 - y1
    if task_id == "plank":
        mx = max(90, int(round(w * 3.0)))
        my = max(48, int(round(h * 0.18)))
    else:
        mx = max(96, int(round(w * 1.1)))
        my = max(64, int(round(h * 1.5)))
    W, H = size
    return [max(0, x1 - mx), max(0, y1 - my), min(W, x2 + mx), min(H, y2 + my)]


def strap_break_core(mask: Image.Image) -> Image.Image:
    """Operation semantics for 'break strap': edit only the central 40%.

    The full automatically localized strap remains semantic provenance, while
    this deterministic submask guarantees both outer strap ends stay outside
    the latent-noise region.
    """
    m = mask.convert("L")
    arr = np.asarray(m, dtype=np.uint8)
    x1, y1, x2, y2 = mask_bbox(m)
    width = x2 - x1
    cx1 = int(round(x1 + 0.30 * width))
    cx2 = int(round(x1 + 0.70 * width))
    core = np.zeros_like(arr)
    core[:, cx1:cx2] = arr[:, cx1:cx2]
    if not np.any(core > 8):
        raise ValueError("derived strap-break core is empty")
    return Image.fromarray(core, mode="L")


def latent_noise_mask(operation_mask: Image.Image, task_id: str) -> Image.Image:
    base = operation_mask.convert("L")
    kernel = 9 if task_id == "plank" else 11
    dilated = base.filter(ImageFilter.MaxFilter(kernel))
    return dilated.filter(ImageFilter.GaussianBlur(1.25))


def allowed_mask(operation_mask: Image.Image, task_id: str) -> Image.Image:
    base = operation_mask.convert("L")
    kernel = 13 if task_id == "plank" else 15
    return base.filter(ImageFilter.MaxFilter(kernel)).filter(ImageFilter.GaussianBlur(2.0))


def overlay(image: Image.Image, mask: Image.Image, color: tuple[int, int, int], alpha: int = 150) -> Image.Image:
    base = image.convert("RGBA")
    m = mask.convert("L")
    tint = Image.new("RGBA", image.size, (*color, 0))
    tint.putalpha(m.point(lambda v: int((v / 255.0) * alpha)))
    return Image.alpha_composite(base, tint).convert("RGB")


def composite_region(
    original: Image.Image,
    crop_box: list[int],
    raw_edit: Image.Image,
    crop_allowed_mask: Image.Image,
) -> Image.Image:
    x1, y1, x2, y2 = crop_box
    cw, ch = x2 - x1, y2 - y1
    edited = raw_edit.convert("RGB").resize((cw, ch), Image.Resampling.LANCZOS)
    orig_crop = original.crop((x1, y1, x2, y2)).convert("RGB")
    blend = crop_allowed_mask.convert("L").resize((cw, ch), Image.Resampling.LANCZOS)
    merged = Image.composite(edited, orig_crop, blend)
    full = original.copy().convert("RGB")
    full.paste(merged, (x1, y1))
    return full


def make_full_mask(size: tuple[int, int], crop_box: list[int], crop_mask: Image.Image) -> Image.Image:
    result = Image.new("L", size, 0)
    x1, y1, x2, y2 = crop_box
    result.paste(crop_mask.resize((x2 - x1, y2 - y1), Image.Resampling.LANCZOS), (x1, y1))
    return result


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
    labels = ["ORIGINAL", "APPROVED TARGET", "LATENT OP MASK", "QWEN RAW CROP", "MASKED REGION FINAL", "RUNNER67 FINAL"]
    for r, row in enumerate(rows):
        imgs = [
            source,
            Image.open(row["approved_overlay"]).convert("RGB"),
            Image.open(row["operation_overlay"]).convert("RGB"),
            Image.open(row["raw"]).convert("RGB"),
            Image.open(row["final"]).convert("RGB"),
            Image.open(row["runner67"]).convert("RGB"),
        ]
        for c, img in enumerate(imgs):
            thumb = img.copy()
            thumb.thumbnail((cell, cell), Image.Resampling.LANCZOS)
            tile = Image.new("RGB", (cell, cell), (205, 208, 208))
            tile.paste(thumb, ((cell - thumb.width)//2, (cell - thumb.height)//2))
            y = r * (cell + label_h)
            canvas.paste(tile, (c * cell, y))
            ImageDraw.Draw(canvas).text((c * cell + 5, y + cell + 8), f"{row['task'].upper()} / {labels[c]}", fill=(235,235,235), font=font)
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination)


def main() -> int:
    args = parse_args()
    print(f"RUNNER68: Asset Studio module root={MODULE_ROOT}", flush=True)

    original_path = (args.klein_workspace / "spike" / "flux2_klein_4b_t2i_probe.png").resolve()
    manifest66_path = (args.runner66_dir / "runner66_repeated_element_manifest.json").resolve()
    if not original_path.is_file():
        raise FileNotFoundError(original_path)
    if not manifest66_path.is_file():
        raise FileNotFoundError(manifest66_path)
    m66 = json.loads(manifest66_path.read_text(encoding="utf-8"))
    if not bool(m66.get("auto_geometry_gate_pass")):
        raise RuntimeError("Runner66 auto geometry gate is not true")

    original = Image.open(original_path).convert("RGB")
    approved_paths = {
        "plank": (args.runner66_dir / "plank_atomic_mask.png").resolve(),
        "strap": (args.runner66_dir / "strap_retained_mask.png").resolve(),
    }
    for p in approved_paths.values():
        if not p.is_file():
            raise FileNotFoundError(p)

    output_dir = (args.workspace / "runner68_latent_mask_region_edit").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    adapter = QwenImageEdit2511MaskedAdapter(
        comfy_root=args.comfy_root,
        base_url=f"http://127.0.0.1:{args.port}",
        timeout_minutes=args.timeout_minutes,
    )
    adapter.verify_runtime()

    prompts = {
        "plank": (
            "This is a tight crop of a wooden double door. Remove the narrow central vertical wooden plank from top to bottom. "
            "Leave a clean narrow open gap where that one plank existed. Do not reconstruct wood inside the gap. "
            "Preserve neighboring planks, iron hardware, stone and vines. The sampling pipeline already restricts which pixels may change."
        ),
        "strap": (
            "This is a tight crop of the lower-right horizontal iron door strap. Create a clean physical break in the middle of that strap: "
            "the central metal section must be absent and the left and right surviving ends must remain. Do not bridge the gap, do not add a new bar, "
            "and preserve wood, stone, vines and other hardware. The sampling pipeline already restricts which pixels may change."
        ),
    }

    records: list[dict[str, Any]] = []
    rows: list[dict[str, Path]] = []
    started_all = time.time()

    for task_id in ("plank", "strap"):
        approved = Image.open(approved_paths[task_id]).convert("L")
        operation = approved if task_id == "plank" else strap_break_core(approved)
        noise = latent_noise_mask(operation, task_id)
        allowed_full = allowed_mask(operation, task_id)
        crop_box = crop_box_for(approved, original.size, task_id)
        x1, y1, x2, y2 = crop_box
        source_crop = original.crop((x1, y1, x2, y2)).convert("RGB")
        crop_noise = noise.crop((x1, y1, x2, y2)).convert("L")
        crop_allowed = allowed_full.crop((x1, y1, x2, y2)).convert("L")

        source_crop_path = output_dir / f"{task_id}_source_crop.png"
        latent_mask_path = output_dir / f"{task_id}_latent_noise_mask.png"
        approved_overlay_path = output_dir / f"{task_id}_approved_target_overlay.png"
        operation_overlay_path = output_dir / f"{task_id}_latent_operation_overlay.png"
        source_crop.save(source_crop_path)
        crop_noise.save(latent_mask_path)
        overlay(original, approved, (235, 45, 45), 155).save(approved_overlay_path)
        overlay(original, operation, (0, 210, 255), 180).save(operation_overlay_path)

        rw = max(16, ((source_crop.width + 15) // 16) * 16)
        rh = max(16, ((source_crop.height + 15) // 16) * 16)
        request = StaticGenerationRequest(
            job_id=f"runner68_masked_{task_id}",
            asset_type="architecture_module",
            output_contract="static_master",
            prompt=prompts[task_id],
            negative="text, logo, UI, people, creatures, red paint, colored locator overlay, replacement metal bar",
            references=(ReferenceInput("previous_approved_state", source_crop_path),),
            width=rw,
            height=rh,
            steps=20,
            cfg=4.0,
            sampler="euler",
            seed=0,
        )
        raw_path = output_dir / f"{task_id}_masked_raw_crop_edit.png"
        print(f"RUNNER68: {task_id} -> Qwen2511 latent-mask edit submitting", flush=True)
        result = adapter.generate_masked(request, latent_mask_path, raw_path)
        print(f"RUNNER68: {task_id} complete in {result.elapsed_seconds:.3f}s", flush=True)

        raw = Image.open(raw_path).convert("RGB")
        final = composite_region(original, crop_box, raw, crop_allowed)
        final_path = output_dir / f"{task_id}_latent_mask_region_final.png"
        final.save(final_path)
        full_allowed_path = output_dir / f"{task_id}_allowed_region.png"
        allowed_full.save(full_allowed_path)

        metrics = difference_metrics(original, final, allowed_full)
        runner67 = args.workspace / "runner67_atomic_region_edit" / f"{task_id}_atomic_region_final.png"
        if not runner67.is_file():
            raise FileNotFoundError(runner67)

        records.append({
            "task": task_id,
            "prompt": prompts[task_id],
            "approved_mask": str(approved_paths[task_id]),
            "approved_mask_sha256": sha256_file(approved_paths[task_id]),
            "approved_bbox": mask_bbox(approved),
            "operation_bbox": mask_bbox(operation),
            "operation_contract": "full atomic plank" if task_id == "plank" else "central 40 percent of approved strap, intersected with automatic strap mask",
            "crop_box": crop_box,
            "latent_noise_mask": str(latent_mask_path),
            "latent_noise_mask_sha256": sha256_file(latent_mask_path),
            "qwen_elapsed_seconds": result.elapsed_seconds,
            "raw_edit": str(raw_path),
            "raw_edit_sha256": sha256_file(raw_path),
            "final": str(final_path),
            "final_sha256": sha256_file(final_path),
            "allowed_region": str(full_allowed_path),
            "difference_from_original": metrics,
        })
        rows.append({
            "task": task_id,
            "approved_overlay": approved_overlay_path,
            "operation_overlay": operation_overlay_path,
            "raw": raw_path,
            "final": final_path,
            "runner67": runner67,
        })

    sheet = output_dir / "runner68_latent_mask_contact_sheet.png"
    contact_sheet(original_path, rows, sheet)
    manifest = {
        "gate": "ASSET_STUDIO_QWEN2511_AUTOMATIC_LATENT_MASK_EDIT",
        "technical_status": "COMPLETE",
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "source": str(original_path),
        "source_sha256": sha256_file(original_path),
        "runner66_manifest": str(manifest66_path),
        "runner66_manifest_sha256": sha256_file(manifest66_path),
        "comfy_commit": args.comfy_commit,
        "editor": "qwen_image_edit_2511_fp8mixed_masked_latent",
        "recipe": {"steps": 20, "cfg": 4.0, "sampler": "euler", "scheduler": "simple", "denoise": 1.0},
        "control_contract": "automatic operation mask -> native SetLatentNoiseMask; source crop is sole visual reference; no colored guide; deterministic final composite",
        "results": records,
        "contact_sheet": str(sheet),
        "contact_sheet_sha256": sha256_file(sheet),
        "elapsed_total_seconds": round(time.time() - started_all, 3),
        "visual_pass_contract": {
            "plank": "one atomic plank is replaced by a clean same-width opening with aligned neighboring geometry",
            "strap": "only the middle of the approved strap is absent; two ends remain and no replacement bar appears",
            "guide_leak": "no colored locator guide exists in the Qwen inputs, so no locator color may leak",
            "outside_region": "pixels outside the deterministic allowed neighborhood remain source pixels by construction",
        },
    }
    manifest_path = output_dir / "runner68_latent_mask_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("RUNNER68-QWEN2511-LATENT-MASK: PASS - TECHNICAL MASKED MATRIX COMPLETE / VISUAL VERDICT PENDING", flush=True)
    print(f"Contact sheet: {sheet}", flush=True)
    print(f"Manifest: {manifest_path}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        import traceback
        print(f"RUNNER68-FAIL: {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc(file=sys.stdout)
        raise SystemExit(1)
