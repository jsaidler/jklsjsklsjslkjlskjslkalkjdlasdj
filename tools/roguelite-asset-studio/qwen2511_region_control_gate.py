#!/usr/bin/env python3
"""Runner64 second phase: Qwen2511 crop edit + deterministic regional composite.

This is not a masked manual workflow. The masks/crops come from the automatic
GroundingDINO + SAM2 localizer. Qwen2511 edits a context crop, receives a second
visual reference that marks the target, and the final full-resolution composite
is constrained to an automatically dilated/feathered mask.
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
    p.add_argument("--localization-dir", type=Path, required=True)
    p.add_argument("--port", type=int, default=8193)
    p.add_argument("--timeout-minutes", type=int, default=480)
    p.add_argument("--comfy-commit", required=True)
    return p.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def make_target_guide(crop: Image.Image, mask: Image.Image) -> Image.Image:
    base = crop.convert("RGBA")
    m = mask.convert("L")
    tint = Image.new("RGBA", crop.size, (255, 32, 32, 0))
    tint.putalpha(m.point(lambda v: int(v * 0.55)))
    return Image.alpha_composite(base, tint).convert("RGB")


def edit_mask(mask: Image.Image, task_id: str) -> Image.Image:
    # Allow a small automatically generated neighborhood around the localized object
    # so removal can synthesize the newly exposed background and join cleanly.
    base = mask.convert("L")
    if task_id == "plank":
        dilated = base.filter(ImageFilter.MaxFilter(31))
        return dilated.filter(ImageFilter.GaussianBlur(5.0))
    dilated = base.filter(ImageFilter.MaxFilter(25))
    return dilated.filter(ImageFilter.GaussianBlur(4.0))


def composite_region(original: Image.Image, crop_box: list[int], raw_edit: Image.Image, crop_mask: Image.Image, task_id: str) -> tuple[Image.Image, Image.Image]:
    x1, y1, x2, y2 = crop_box
    cw, ch = x2 - x1, y2 - y1
    edited = raw_edit.convert("RGB").resize((cw, ch), Image.Resampling.LANCZOS)
    orig_crop = original.crop((x1, y1, x2, y2)).convert("RGB")
    blend_mask = edit_mask(crop_mask.resize((cw, ch), Image.Resampling.NEAREST), task_id)
    merged_crop = Image.composite(edited, orig_crop, blend_mask)
    full = original.copy().convert("RGB")
    full.paste(merged_crop, (x1, y1))
    return full, blend_mask


def difference_metrics(a: Image.Image, b: Image.Image, allowed_mask: Image.Image | None = None) -> dict[str, float]:
    aa = np.asarray(a.convert("RGB"), dtype=np.int16)
    bb = np.asarray(b.convert("RGB"), dtype=np.int16)
    delta = np.abs(aa - bb).mean(axis=2)
    result = {
        "mean_abs_rgb": float(np.abs(aa - bb).mean()),
        "changed_ratio_gt_12": float((delta > 12).mean()),
        "changed_ratio_gt_24": float((delta > 24).mean()),
    }
    if allowed_mask is not None:
        m = np.asarray(allowed_mask.convert("L"), dtype=np.uint8) > 2
        outside = ~m
        result["outside_allowed_mean_abs"] = float(delta[outside].mean()) if outside.any() else 0.0
        result["outside_allowed_changed_ratio_gt_12"] = float((delta[outside] > 12).mean()) if outside.any() else 0.0
    return result


def make_full_allowed_mask(size: tuple[int, int], crop_box: list[int], crop_blend: Image.Image) -> Image.Image:
    result = Image.new("L", size, 0)
    result.paste(crop_blend, (crop_box[0], crop_box[1]))
    return result


def contact_sheet(original: Path, rows: list[dict[str, Path]], destination: Path) -> None:
    cell = 512
    label_h = 34
    cols = 5
    canvas = Image.new("RGB", (cols * cell, len(rows) * (cell + label_h)), (32, 32, 32))
    labels_by_col = ["ORIGINAL", "AUTO LOCALIZATION", "QWEN RAW CROP", "REGION FINAL", "RUNNER63 GLOBAL"]
    font = ImageFont.load_default()
    source = Image.open(original).convert("RGB")
    for r, row in enumerate(rows):
        imgs = [
            source,
            Image.open(row["overlay"]).convert("RGB"),
            Image.open(row["raw"]).convert("RGB"),
            Image.open(row["final"]).convert("RGB"),
            Image.open(row["global"]).convert("RGB"),
        ]
        for c, img in enumerate(imgs):
            thumb = img.copy()
            thumb.thumbnail((cell, cell), Image.Resampling.LANCZOS)
            tile = Image.new("RGB", (cell, cell), (205, 208, 208))
            tile.paste(thumb, ((cell - thumb.width)//2, (cell - thumb.height)//2))
            y = r * (cell + label_h)
            canvas.paste(tile, (c * cell, y))
            draw = ImageDraw.Draw(canvas)
            draw.text((c * cell + 6, y + cell + 8), f"{row['task'].upper()} / {labels_by_col[c]}", fill=(235, 235, 235), font=font)
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination)


def main() -> int:
    args = parse_args()
    module_root = Path(__file__).resolve().parent
    print(f"RUNNER64-REGION: Asset Studio module root={module_root}", flush=True)

    original_path = (args.klein_workspace / "spike" / "flux2_klein_4b_t2i_probe.png").resolve()
    localization_manifest_path = (args.localization_dir / "runner64_localization_manifest.json").resolve()
    if not original_path.is_file():
        raise FileNotFoundError(original_path)
    if not localization_manifest_path.is_file():
        raise FileNotFoundError(localization_manifest_path)

    loc = load_json(localization_manifest_path)
    original = Image.open(original_path).convert("RGB")
    output_dir = (args.workspace / "automatic_region_control").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    adapter = QwenImageEdit2511Adapter(
        comfy_root=args.comfy_root,
        base_url=f"http://127.0.0.1:{args.port}",
        timeout_seconds=args.timeout_minutes * 60,
    )
    adapter.verify_runtime()

    prompts = {
        "plank": (
            "Image 1 is the source crop. Image 2 is the same crop with a translucent RED overlay marking the ONLY target component. "
            "The red overlay is a locator only; do not reproduce red color. Preserve everything outside that marked plank. "
            "Remove exactly the single marked vertical wooden plank from top to bottom, leaving a narrow open gap where that plank existed. "
            "Do not remove neighboring planks. Keep nearby iron hardware and stone unchanged. Fill only the newly exposed space naturally as an opening through the doorway."
        ),
        "strap": (
            "Image 1 is the source crop. Image 2 is the same crop with a translucent RED overlay marking the ONLY target component. "
            "The red overlay is a locator only; do not reproduce red color. Preserve everything outside that marked iron strap. "
            "Break only the marked lower horizontal iron strap: remove a clear middle section and leave two short snapped or bent surviving ends. "
            "Do not add a replacement bar. Do not alter neighboring hinges, straps, wooden planks, stone, vines or door proportions."
        ),
    }
    global_runner63 = {
        "plank": args.workspace / "qwen2511_precision_gate" / "qwen2511_atomic_plank_steps20.png",
        "strap": args.workspace / "qwen2511_precision_gate" / "qwen2511_atomic_strap_steps20.png",
    }

    records: list[dict[str, Any]] = []
    sheet_rows: list[dict[str, Path]] = []
    started_all = time.time()

    for task_id in ("plank", "strap"):
        task = loc["tasks"][task_id]
        crop_box = [int(v) for v in task["crop_box"]]
        crop_path = Path(task["crop"])
        crop_mask_path = Path(task["crop_mask"])
        overlay_path = Path(task["mask_overlay"])
        for p in (crop_path, crop_mask_path, overlay_path, global_runner63[task_id]):
            if not p.is_file():
                raise FileNotFoundError(p)

        crop = Image.open(crop_path).convert("RGB")
        crop_mask = Image.open(crop_mask_path).convert("L")
        guide = make_target_guide(crop, crop_mask)
        guide_path = output_dir / f"{task_id}_target_guide.png"
        guide.save(guide_path)

        # StaticGenerationRequest requires multiples of 16; the Qwen reference path
        # derives actual generation geometry from Image 1, but dimensions remain useful provenance.
        rw = max(16, ((crop.width + 15) // 16) * 16)
        rh = max(16, ((crop.height + 15) // 16) * 16)
        raw_path = output_dir / f"{task_id}_raw_crop_edit.png"
        request = StaticGenerationRequest(
            job_id=f"runner64_region_{task_id}",
            asset_type="architecture_module",
            output_contract="static_master",
            prompt=prompts[task_id],
            negative="text, logo, UI, people, creatures, red paint, red overlay copied into the result",
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
        print(f"RUNNER64-REGION: {task_id} -> Qwen2511 crop edit submitting", flush=True)
        result = adapter.generate(request, raw_path)
        print(f"RUNNER64-REGION: {task_id} Qwen complete in {result.elapsed_seconds:.3f}s", flush=True)

        raw = Image.open(raw_path).convert("RGB")
        final, crop_blend = composite_region(original, crop_box, raw, crop_mask, task_id)
        final_path = output_dir / f"{task_id}_region_controlled_final.png"
        final.save(final_path)
        full_allowed = make_full_allowed_mask(original.size, crop_box, crop_blend)
        full_allowed_path = output_dir / f"{task_id}_allowed_region.png"
        full_allowed.save(full_allowed_path)

        metrics = difference_metrics(original, final, full_allowed)
        records.append({
            "task": task_id,
            "prompt": prompts[task_id],
            "crop_box": crop_box,
            "localizer_selected_box": task["selected"]["box"],
            "detector_score": task["selected"]["detector_score"],
            "selector_score": task["selected"]["selector_score"],
            "sam_iou_score": task["sam_iou_score"],
            "mask_area_ratio": task["mask_area_ratio"],
            "qwen_elapsed_seconds": result.elapsed_seconds,
            "raw_edit": str(raw_path),
            "raw_edit_sha256": sha256_file(raw_path),
            "final": str(final_path),
            "final_sha256": sha256_file(final_path),
            "allowed_region": str(full_allowed_path),
            "difference_from_original": metrics,
        })
        sheet_rows.append({
            "task": task_id,
            "overlay": overlay_path,
            "raw": raw_path,
            "final": final_path,
            "global": global_runner63[task_id],
        })

    sheet_path = output_dir / "runner64_automatic_region_control_contact_sheet.png"
    contact_sheet(original_path, sheet_rows, sheet_path)
    manifest = {
        "gate": "ASSET_STUDIO_AUTOMATIC_LOCALIZATION_PLUS_REGION_CONTROL",
        "technical_status": "COMPLETE",
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "source": str(original_path),
        "source_sha256": sha256_file(original_path),
        "comfy_commit": args.comfy_commit,
        "localization_manifest": str(localization_manifest_path),
        "localization_manifest_sha256": sha256_file(localization_manifest_path),
        "editor": "qwen_image_edit_2511_fp8mixed",
        "editor_recipe": {"steps": 20, "cfg": 4.0, "sampler": "euler", "scheduler": "simple", "denoise": 1.0},
        "composition_contract": "automatic SAM2 mask -> deterministic dilation/feather -> only masked neighborhood may alter full-resolution source",
        "results": records,
        "contact_sheet": str(sheet_path),
        "contact_sheet_sha256": sha256_file(sheet_path),
        "elapsed_total_seconds": round(time.time() - started_all, 3),
        "visual_pass_contract": {
            "localization": "GroundingDINO+SAM2 must isolate the intended plank and intended lower-right strap without user-drawn boxes/masks.",
            "plank": "Final full image must remove approximately the localized one-plank component while preserving unrelated geometry outside the automatic region.",
            "strap": "Final full image must create a visible break in only the localized lower-right strap without a global replacement bar or unrelated door redesign.",
            "outside_region": "Full-resolution pixels outside the automatically generated allowed region must remain effectively identical by construction.",
        },
    }
    manifest_path = output_dir / "runner64_automatic_region_control_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("RUNNER64-AUTOMATIC-REGION-CONTROL: PASS - PIPELINE COMPLETE / VISUAL VERDICT PENDING", flush=True)
    print(f"Contact sheet: {sheet_path}", flush=True)
    print(f"Manifest: {manifest_path}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        import traceback
        print(f"RUNNER64-REGION-FAIL: {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc(file=sys.stdout)
        raise SystemExit(1)
