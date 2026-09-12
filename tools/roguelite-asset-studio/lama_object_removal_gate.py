#!/usr/bin/env python3
"""Runner71: Big-LaMa object-removal gate behind accepted automatic masks."""

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

from lama_inpaint_adapter import LaMaInpaintAdapter, MODEL_BYTES, MODEL_NAME, MODEL_SHA256


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--klein-workspace", type=Path, required=True)
    p.add_argument("--runner66-dir", type=Path, required=True)
    p.add_argument("--runner70-dir", type=Path, required=True)
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


def variant_mask(operation: Image.Image, task: str, variant: str) -> Image.Image:
    if variant == "tight":
        kernel = 3
    elif variant == "expanded":
        kernel = 9 if task == "plank" else 7
    else:
        raise ValueError(variant)
    return operation.convert("L").filter(ImageFilter.MaxFilter(kernel))


def final_allowed_mask(operation: Image.Image, task: str) -> Image.Image:
    kernel = 15 if task == "plank" else 11
    return operation.convert("L").filter(ImageFilter.MaxFilter(kernel)).filter(ImageFilter.GaussianBlur(2.0))


def overlay(image: Image.Image, mask: Image.Image, color: tuple[int, int, int], alpha: int = 155) -> Image.Image:
    base = image.convert("RGBA")
    m = mask.convert("L")
    tint = Image.new("RGBA", image.size, (*color, 0))
    tint.putalpha(m.point(lambda v: int((v / 255.0) * alpha)))
    return Image.alpha_composite(base, tint).convert("RGB")


def composite_region(original: Image.Image, crop_box: list[int], raw: Image.Image, crop_allowed: Image.Image) -> Image.Image:
    x1, y1, x2, y2 = crop_box
    cw, ch = x2 - x1, y2 - y1
    edited = raw.convert("RGB")
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
    cell = 360
    label_h = 30
    labels = ["ORIGINAL", "APPROVED TARGET", "LAMA TIGHT RAW", "LAMA TIGHT FINAL", "LAMA EXPANDED RAW", "LAMA EXPANDED FINAL", "RUNNER70 FINAL"]
    cols = len(labels)
    font = ImageFont.load_default()
    canvas = Image.new("RGB", (cols * cell, len(rows) * (cell + label_h)), (32, 32, 32))
    source = Image.open(original_path).convert("RGB")
    for r, row in enumerate(rows):
        imgs = [
            source,
            Image.open(row["approved_overlay"]).convert("RGB"),
            Image.open(row["tight_raw"]).convert("RGB"),
            Image.open(row["tight_final"]).convert("RGB"),
            Image.open(row["expanded_raw"]).convert("RGB"),
            Image.open(row["expanded_final"]).convert("RGB"),
            Image.open(row["runner70"]).convert("RGB"),
        ]
        for c, img in enumerate(imgs):
            thumb = img.copy()
            thumb.thumbnail((cell, cell), Image.Resampling.LANCZOS)
            tile = Image.new("RGB", (cell, cell), (205, 208, 208))
            tile.paste(thumb, ((cell - thumb.width) // 2, (cell - thumb.height) // 2))
            y = r * (cell + label_h)
            canvas.paste(tile, (c * cell, y))
            ImageDraw.Draw(canvas).text((c * cell + 5, y + cell + 7), f"{row['task'].upper()} / {labels[c]}", fill=(235, 235, 235), font=font)
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination)


def main() -> int:
    args = parse_args()
    print(f"RUNNER71: Asset Studio module root={MODULE_ROOT}", flush=True)

    original_path = (args.klein_workspace / "spike" / "flux2_klein_4b_t2i_probe.png").resolve()
    runner66_manifest_path = (args.runner66_dir / "runner66_repeated_element_manifest.json").resolve()
    runner70_manifest_path = (args.runner70_dir / "runner70_sdxl_1024_manifest.json").resolve()
    for p in (original_path, runner66_manifest_path, runner70_manifest_path, args.model):
        if not Path(p).is_file():
            raise FileNotFoundError(p)

    m66 = json.loads(runner66_manifest_path.read_text(encoding="utf-8"))
    m70 = json.loads(runner70_manifest_path.read_text(encoding="utf-8"))
    if not bool(m66.get("auto_geometry_gate_pass")):
        raise RuntimeError("Runner66 automatic geometry gate is not true")
    if str(m70.get("technical_status")) != "COMPLETE":
        raise RuntimeError("Runner70 evidence is not technically complete")

    result70 = {str(item["task"]): item for item in m70["results"]}
    original = Image.open(original_path).convert("RGB")
    approved_paths = {
        "plank": (args.runner66_dir / "plank_atomic_mask.png").resolve(),
        "strap": (args.runner66_dir / "strap_retained_mask.png").resolve(),
    }
    for p in approved_paths.values():
        if not p.is_file():
            raise FileNotFoundError(p)

    output_dir = (args.workspace / "runner71_object_removal_gate").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    adapter = LaMaInpaintAdapter(args.model, prefer_cuda=True)
    adapter.verify_runtime()
    print(f"RUNNER71: Big-LaMa verified ({MODEL_BYTES} bytes, {MODEL_SHA256}); device={adapter.device}", flush=True)

    records: list[dict[str, Any]] = []
    rows: list[dict[str, Path]] = []
    started_all = time.time()

    for task in ("plank", "strap"):
        approved = Image.open(approved_paths[task]).convert("L")
        operation = approved if task == "plank" else strap_break_core(approved)
        allowed = final_allowed_mask(operation, task)
        crop_box = [int(v) for v in result70[task]["source_context_box"]]
        x1, y1, x2, y2 = crop_box
        source_crop = original.crop((x1, y1, x2, y2)).convert("RGB")
        crop_allowed = allowed.crop((x1, y1, x2, y2)).convert("L")

        source_crop_path = output_dir / f"{task}_source_context.png"
        approved_overlay_path = output_dir / f"{task}_approved_target_overlay.png"
        source_crop.save(source_crop_path)
        overlay(original, operation if task == "strap" else approved, (235, 45, 45), 155).save(approved_overlay_path)

        variant_outputs: dict[str, dict[str, Any]] = {}
        for variant in ("tight", "expanded"):
            model_mask_full = variant_mask(operation, task, variant)
            crop_mask = model_mask_full.crop((x1, y1, x2, y2)).convert("L")
            mask_path = output_dir / f"{task}_lama_{variant}_mask.png"
            raw_path = output_dir / f"{task}_lama_{variant}_raw.png"
            final_path = output_dir / f"{task}_lama_{variant}_final.png"
            crop_mask.save(mask_path)

            print(f"RUNNER71: {task}/{variant} -> Big-LaMa submitting ({source_crop.width}x{source_crop.height})", flush=True)
            result = adapter.inpaint(source_crop_path, mask_path, raw_path)
            print(f"RUNNER71: {task}/{variant} complete in {result.elapsed_seconds:.3f}s", flush=True)

            raw = Image.open(raw_path).convert("RGB")
            final = composite_region(original, crop_box, raw, crop_allowed)
            final.save(final_path)
            metrics = difference_metrics(original, final, allowed)
            variant_outputs[variant] = {
                "mask": str(mask_path),
                "mask_sha256": sha256_file(mask_path),
                "elapsed_seconds": result.elapsed_seconds,
                "raw": str(raw_path),
                "raw_sha256": sha256_file(raw_path),
                "final": str(final_path),
                "final_sha256": sha256_file(final_path),
                "difference_from_original": metrics,
            }

        allowed_path = output_dir / f"{task}_allowed_region.png"
        allowed.save(allowed_path)
        runner70_final = Path(result70[task]["final"]).resolve()
        if not runner70_final.is_file():
            raise FileNotFoundError(runner70_final)

        records.append({
            "task": task,
            "approved_mask": str(approved_paths[task]),
            "approved_mask_sha256": sha256_file(approved_paths[task]),
            "approved_bbox": mask_bbox(approved),
            "operation_bbox": mask_bbox(operation),
            "operation_contract": "full atomic plank" if task == "plank" else "central 40 percent of approved strap",
            "source_context_box": crop_box,
            "source_context_size": list(source_crop.size),
            "allowed_region": str(allowed_path),
            "variants": variant_outputs,
            "runner70_final": str(runner70_final),
            "runner70_final_sha256": sha256_file(runner70_final),
        })
        rows.append({
            "task": task,
            "approved_overlay": approved_overlay_path,
            "tight_raw": Path(variant_outputs["tight"]["raw"]),
            "tight_final": Path(variant_outputs["tight"]["final"]),
            "expanded_raw": Path(variant_outputs["expanded"]["raw"]),
            "expanded_final": Path(variant_outputs["expanded"]["final"]),
            "runner70": runner70_final,
        })

    contact = output_dir / "runner71_lama_object_removal_contact_sheet.png"
    contact_sheet(original_path, rows, contact)
    manifest = {
        "gate": "ASSET_STUDIO_BIG_LAMA_OBJECT_REMOVAL",
        "technical_status": "COMPLETE",
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "source": str(original_path),
        "source_sha256": sha256_file(original_path),
        "runner66_manifest": str(runner66_manifest_path),
        "runner66_manifest_sha256": sha256_file(runner66_manifest_path),
        "runner70_manifest": str(runner70_manifest_path),
        "runner70_manifest_sha256": sha256_file(runner70_manifest_path),
        "editor": "big_lama_torchscript",
        "model": str(args.model.resolve()),
        "model_bytes": args.model.stat().st_size,
        "model_sha256": sha256_file(args.model),
        "device": str(adapter.device),
        "control_contract": "Runner66 approved automatic operation masks -> Big-LaMa object removal -> deterministic full-resolution composite; no prompt/manual mask/box",
        "mask_variants": {
            "tight": "small boundary expansion",
            "expanded": "larger boundary expansion to test object-edge removal without changing semantic target",
        },
        "results": records,
        "contact_sheet": str(contact),
        "contact_sheet_sha256": sha256_file(contact),
        "elapsed_total_seconds": round(time.time() - started_all, 3),
        "visual_pass_contract": {
            "plank": "at least one mask variant removes exactly the atomic plank and produces a plausible narrow opening/background continuation without reconstructing wood across the gap",
            "strap": "at least one mask variant removes the central strap section and reconstructs plausible underlying door/wood while preserving both outside strap ends",
            "preservation": "unrelated geometry remains source-authoritative through deterministic final composite",
        },
    }
    manifest_path = output_dir / "runner71_lama_object_removal_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("RUNNER71-BIG-LAMA: PASS - TECHNICAL OBJECT-REMOVAL MATRIX COMPLETE / VISUAL VERDICT PENDING", flush=True)
    print(f"Contact sheet: {contact}", flush=True)
    print(f"Manifest: {manifest_path}", flush=True)
    print(f"Total elapsed: {manifest['elapsed_total_seconds']:.3f}s", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        import traceback
        print(f"RUNNER71-PYTHON-FAIL: {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc(file=sys.stdout)
        raise SystemExit(1)
