#!/usr/bin/env python3
"""Runner72: PowerPaint v2.1 task-conditioned object-removal gate.

Reuses Runner71's exact source contexts, mask-boundary variants and deterministic
allowed regions so the only meaningful variable is the removal backend.
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
from PIL import Image, ImageDraw, ImageFont

MODULE_ROOT = Path(__file__).resolve().parent
if str(MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE_ROOT))

from adapter_protocol import ReferenceInput, StaticGenerationRequest
from powerpaint_brushnet_adapter import PowerPaintBrushNetAdapter


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--comfy-root", type=Path, required=True)
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--runner71-dir", type=Path, required=True)
    p.add_argument("--port", type=int, default=8194)
    p.add_argument("--timeout-minutes", type=int, default=180)
    p.add_argument("--comfy-commit", required=True)
    p.add_argument("--brushnet-commit", required=True)
    return p.parse_args()


def mask_bbox(mask: Image.Image) -> list[int]:
    arr = np.asarray(mask.convert("L"), dtype=np.uint8)
    ys, xs = np.where(arr > 8)
    if xs.size == 0:
        raise ValueError("mask is empty")
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
    labels = [
        "ORIGINAL",
        "APPROVED TARGET",
        "POWERPAINT TIGHT RAW",
        "POWERPAINT TIGHT FINAL",
        "POWERPAINT EXPANDED RAW",
        "POWERPAINT EXPANDED FINAL",
        "BIG-LAMA EXPANDED FINAL",
    ]
    font = ImageFont.load_default()
    canvas = Image.new("RGB", (len(labels) * cell, len(rows) * (cell + label_h)), (32, 32, 32))
    source = Image.open(original_path).convert("RGB")
    for r, row in enumerate(rows):
        imgs = [
            source,
            Image.open(row["approved_overlay"]).convert("RGB"),
            Image.open(row["tight_raw"]).convert("RGB"),
            Image.open(row["tight_final"]).convert("RGB"),
            Image.open(row["expanded_raw"]).convert("RGB"),
            Image.open(row["expanded_final"]).convert("RGB"),
            Image.open(row["lama_expanded"]).convert("RGB"),
        ]
        for c, img in enumerate(imgs):
            thumb = img.copy()
            thumb.thumbnail((cell, cell), Image.Resampling.LANCZOS)
            tile = Image.new("RGB", (cell, cell), (205, 208, 208))
            tile.paste(thumb, ((cell - thumb.width) // 2, (cell - thumb.height) // 2))
            y = r * (cell + label_h)
            canvas.paste(tile, (c * cell, y))
            ImageDraw.Draw(canvas).text(
                (c * cell + 5, y + cell + 7),
                f"{row['task'].upper()} / {labels[c]}",
                fill=(235, 235, 235),
                font=font,
            )
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination)


def main() -> int:
    args = parse_args()
    print(f"RUNNER72: Asset Studio module root={MODULE_ROOT}", flush=True)

    runner71_manifest_path = (args.runner71_dir / "runner71_lama_object_removal_manifest.json").resolve()
    if not runner71_manifest_path.is_file():
        raise FileNotFoundError(runner71_manifest_path)
    m71 = json.loads(runner71_manifest_path.read_text(encoding="utf-8"))
    if str(m71.get("technical_status")) != "COMPLETE":
        raise RuntimeError("Runner71 technical evidence is not complete")

    original_path = Path(m71["source"]).resolve()
    if not original_path.is_file():
        raise FileNotFoundError(original_path)
    if sha256_file(original_path) != str(m71["source_sha256"]):
        raise RuntimeError("Runner71 source SHA256 no longer matches")
    original = Image.open(original_path).convert("RGB")

    output_dir = (args.workspace / "runner72_object_removal_gate").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    adapter = PowerPaintBrushNetAdapter(
        comfy_root=args.comfy_root,
        base_url=f"http://127.0.0.1:{args.port}",
        timeout_minutes=args.timeout_minutes,
    )
    adapter.verify_runtime()

    task_text = {
        "plank": {
            "positive": "empty scene blur, narrow empty opening through the medieval doorway, neutral background visible through the missing board",
            "negative": "wooden plank, vertical board, replacement wood, extra board, continuous door",
        },
        "strap": {
            "positive": "empty scene blur, aged dark wooden door surface visible where the iron is removed",
            "negative": "iron strap, hinge strap, metal bar, rivets, replacement metal, continuous iron",
        },
    }

    records: list[dict[str, Any]] = []
    rows: list[dict[str, Path]] = []
    started_all = time.time()

    result71 = {str(item["task"]): item for item in m71["results"]}
    for task in ("plank", "strap"):
        evidence = result71[task]
        crop_box = [int(v) for v in evidence["source_context_box"]]
        x1, y1, x2, y2 = crop_box
        source_crop = original.crop((x1, y1, x2, y2)).convert("RGB")
        if source_crop.size != tuple(evidence["source_context_size"]):
            raise RuntimeError(f"{task}: source context size changed: {source_crop.size}")
        if source_crop.width % 8 or source_crop.height % 8:
            raise RuntimeError(f"{task}: context is not divisible by 8: {source_crop.size}")

        approved_mask_path = Path(evidence["approved_mask"]).resolve()
        allowed_path = Path(evidence["allowed_region"]).resolve()
        for p in (approved_mask_path, allowed_path):
            if not p.is_file():
                raise FileNotFoundError(p)
        if sha256_file(approved_mask_path) != str(evidence["approved_mask_sha256"]):
            raise RuntimeError(f"{task}: approved mask SHA256 changed")
        approved_full = Image.open(approved_mask_path).convert("L")
        operation_full = approved_full if task == "plank" else strap_break_core(approved_full)
        allowed_full = Image.open(allowed_path).convert("L")
        crop_allowed = allowed_full.crop((x1, y1, x2, y2)).convert("L")

        source_crop_path = output_dir / f"{task}_source_context.png"
        approved_overlay_path = output_dir / f"{task}_approved_target_overlay.png"
        source_crop.save(source_crop_path)
        overlay(original, operation_full, (235, 45, 45), 155).save(approved_overlay_path)

        variant_outputs: dict[str, dict[str, Any]] = {}
        for variant in ("tight", "expanded"):
            mask_path = Path(evidence["variants"][variant]["mask"]).resolve()
            if not mask_path.is_file():
                raise FileNotFoundError(mask_path)
            if sha256_file(mask_path) != str(evidence["variants"][variant]["mask_sha256"]):
                raise RuntimeError(f"{task}/{variant}: Runner71 mask SHA256 changed")
            with Image.open(mask_path) as mask_img:
                if mask_img.size != source_crop.size:
                    raise RuntimeError(f"{task}/{variant}: mask/source size mismatch {mask_img.size} vs {source_crop.size}")

            raw_path = output_dir / f"{task}_powerpaint_{variant}_raw.png"
            final_path = output_dir / f"{task}_powerpaint_{variant}_final.png"
            request = StaticGenerationRequest(
                job_id=f"runner72_{task}_{variant}",
                asset_type="architecture_module",
                output_contract="static_master",
                prompt=task_text[task]["positive"],
                negative=task_text[task]["negative"],
                references=(ReferenceInput("previous_approved_state", source_crop_path),),
                width=source_crop.width,
                height=source_crop.height,
                steps=20,
                cfg=7.5,
                sampler="euler",
                seed=0,
            )
            print(f"RUNNER72: {task}/{variant} -> PowerPaint object removal submitting ({source_crop.width}x{source_crop.height})", flush=True)
            generated = adapter.generate_masked(request, mask_path, raw_path)
            print(f"RUNNER72: {task}/{variant} complete in {generated.elapsed_seconds:.3f}s", flush=True)

            raw = Image.open(raw_path).convert("RGB")
            final = composite_region(original, crop_box, raw, crop_allowed)
            final.save(final_path)
            metrics = difference_metrics(original, final, allowed_full)
            variant_outputs[variant] = {
                "mask": str(mask_path),
                "mask_sha256": sha256_file(mask_path),
                "prompt": request.prompt,
                "negative": request.negative,
                "elapsed_seconds": generated.elapsed_seconds,
                "prompt_id": generated.prompt_id,
                "raw": str(raw_path),
                "raw_sha256": sha256_file(raw_path),
                "final": str(final_path),
                "final_sha256": sha256_file(final_path),
                "difference_from_original": metrics,
            }

        lama_expanded = Path(evidence["variants"]["expanded"]["final"]).resolve()
        if not lama_expanded.is_file():
            raise FileNotFoundError(lama_expanded)
        records.append({
            "task": task,
            "approved_mask": str(approved_mask_path),
            "approved_mask_sha256": sha256_file(approved_mask_path),
            "approved_bbox": evidence["approved_bbox"],
            "operation_bbox": evidence["operation_bbox"],
            "operation_contract": evidence["operation_contract"],
            "source_context_box": crop_box,
            "source_context_size": list(source_crop.size),
            "allowed_region": str(allowed_path),
            "variants": variant_outputs,
            "runner71_expanded_final": str(lama_expanded),
            "runner71_expanded_final_sha256": sha256_file(lama_expanded),
        })
        rows.append({
            "task": task,
            "approved_overlay": approved_overlay_path,
            "tight_raw": Path(variant_outputs["tight"]["raw"]),
            "tight_final": Path(variant_outputs["tight"]["final"]),
            "expanded_raw": Path(variant_outputs["expanded"]["raw"]),
            "expanded_final": Path(variant_outputs["expanded"]["final"]),
            "lama_expanded": lama_expanded,
        })

    contact = output_dir / "runner72_powerpaint_object_removal_contact_sheet.png"
    contact_sheet(original_path, rows, contact)
    manifest = {
        "gate": "ASSET_STUDIO_POWERPAINT_V2_1_OBJECT_REMOVAL",
        "technical_status": "COMPLETE",
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "source": str(original_path),
        "source_sha256": sha256_file(original_path),
        "runner71_manifest": str(runner71_manifest_path),
        "runner71_manifest_sha256": sha256_file(runner71_manifest_path),
        "editor": "powerpaint_v2_1_brushnet_object_removal",
        "comfy_commit": args.comfy_commit,
        "brushnet_custom_node_commit": args.brushnet_commit,
        "recipe": {
            "function": "object removal",
            "task_tokens": "P_ctxt positive / P_obj negative (inside PowerPaint node)",
            "fitting": 1.0,
            "brushnet_scale": 1.0,
            "brushnet_start_at": 0,
            "brushnet_end_at": 10000,
            "save_memory": "max",
            "steps": 20,
            "cfg": 7.5,
            "sampler": "euler",
            "scheduler": "normal",
            "denoise": 1.0,
            "seed": 0,
        },
        "control_contract": "Runner66/71 approved automatic masks -> PowerPaint task-conditioned object removal -> deterministic full-resolution composite; no manual prompt-localization/mask/box",
        "results": records,
        "contact_sheet": str(contact),
        "contact_sheet_sha256": sha256_file(contact),
        "elapsed_total_seconds": round(time.time() - started_all, 3),
        "visual_pass_contract": {
            "plank": "at least one boundary variant removes the one atomic plank and reads as a real narrow opening with no replacement board",
            "strap": "at least one boundary variant removes the strap center and exposes coherent aged wood while both outside ends survive",
            "preservation": "unrelated geometry remains source-authoritative through deterministic final composite",
        },
    }
    manifest_path = output_dir / "runner72_powerpaint_object_removal_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("RUNNER72-POWERPAINT: PASS - TECHNICAL TASK-CONDITIONED REMOVAL MATRIX COMPLETE / VISUAL VERDICT PENDING", flush=True)
    print(f"Contact sheet: {contact}", flush=True)
    print(f"Manifest: {manifest_path}", flush=True)
    print(f"Total elapsed: {manifest['elapsed_total_seconds']:.3f}s", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        import traceback
        print(f"RUNNER72-PYTHON-FAIL: {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc(file=sys.stdout)
        raise SystemExit(1)
