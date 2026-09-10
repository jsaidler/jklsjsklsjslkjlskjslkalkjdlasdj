#!/usr/bin/env python3
"""Runner63: Qwen-Image-Edit-2511 FP8mixed atomic precision gate.

Compares Qwen 2511 at 20 and 40 steps against the preserved Runner62 Qwen 2509
outputs and Runner61 Klein Base failures using the same original architecture asset.
No masks or manual localization are introduced.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parent
if str(MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE_ROOT))

from PIL import Image, ImageChops, ImageDraw, ImageStat

from adapter_protocol import ReferenceInput, StaticGenerationRequest
from flux2_klein_adapter import sha256_file
from qwen_image_edit_2511_adapter import QwenImageEdit2511Adapter

CFG = 4.0
SAMPLER = "euler"
SEED = 0
STEP_SERIES = (20, 40)

COMMON = """Edit Image 1 only. Preserve the exact same ruined gate identity, front-three-quarter camera, doorway proportions, masonry footprint, neutral authoring background, natural gray stone, brown wood, dark aged iron, roots and moss. Keep all unrelated geometry unchanged. Do not redesign the gate. No people, creatures, text, logo, UI or landscape."""

PROMPT_PLANK = COMMON + """ Make exactly ONE structural change: remove EXACTLY ONE SINGLE vertical wooden plank from the LEFT door leaf, not the whole door leaf and not multiple boards. The removed area must be approximately one existing plank-width only and absent from top to bottom, leaving one narrow full-height dark open gap. Every neighboring plank must remain present with its original width and position. The right door leaf, masonry and every iron strap must remain otherwise unchanged."""

PROMPT_STRAP = COMMON + """ Make exactly ONE structural change: break and partially remove ONLY the LOWER horizontal iron strap on the RIGHT door leaf. Remove only a substantial middle segment of that specific strap; leave its two surviving ends visibly snapped or bent. Keep every wooden plank present and unchanged. Keep every other hinge, strap, ornament, handle and all masonry unchanged. Do not replace the target strap with a new larger bar and do not damage the lower wooden edge of the door."""


def diff_metrics(reference: Path, candidate: Path) -> dict:
    with Image.open(reference) as a_open, Image.open(candidate) as b_open:
        a = a_open.convert("RGB")
        b = b_open.convert("RGB")
        if b.size != a.size:
            b = b.resize(a.size, Image.Resampling.LANCZOS)
        diff = ImageChops.difference(a, b)
        stat = ImageStat.Stat(diff)
        gray = diff.convert("L")
        hist = gray.histogram()
        total = sum(hist) or 1
        return {
            "mean_abs_rgb": [round(v, 4) for v in stat.mean],
            "mean_abs_luma": round(ImageStat.Stat(gray).mean[0], 4),
            "changed_ratio_gt_12": round(sum(hist[13:]) / total, 6),
            "changed_ratio_gt_24": round(sum(hist[25:]) / total, 6),
        }


def run_edit(adapter, output_dir: Path, label: str, prompt: str, source: Path, steps: int, filename: str):
    request = StaticGenerationRequest(
        job_id=f"runner63_{label}_steps{steps}",
        asset_type="architecture_module",
        output_contract="static_master",
        prompt=prompt,
        negative="",
        references=(ReferenceInput("previous_approved_state", source),),
        width=1024,
        height=1024,
        steps=steps,
        cfg=CFG,
        sampler=SAMPLER,
        seed=SEED,
    )
    destination = output_dir / filename
    print(f"RUNNER63: {label} / {steps} steps -> submitting", flush=True)
    result = adapter.generate(request, destination)
    print(f"RUNNER63: {label} / {steps} complete in {result.elapsed_seconds:.3f}s -> {destination}", flush=True)
    return result


def result_record(result, original: Path) -> dict:
    with Image.open(result.output_path) as image:
        size = list(image.size)
    return {
        "adapter_id": result.adapter_id,
        "prompt_id": result.prompt_id,
        "output": str(result.output_path),
        "output_sha256": result.output_sha256,
        "elapsed_seconds": round(result.elapsed_seconds, 3),
        "reference_roles": [r.role for r in result.request.references],
        "reference_hashes": list(result.reference_hashes),
        "prompt": result.request.prompt,
        "steps": result.request.steps,
        "cfg": result.request.cfg,
        "sampler": result.request.sampler,
        "seed": result.request.seed,
        "image_size": size,
        "difference_from_original": diff_metrics(original, result.output_path),
    }


def make_contact_sheet(rows: list[list[tuple[str, Path]]], destination: Path) -> None:
    thumb = 384
    label_h = 34
    cols = max(len(r) for r in rows)
    canvas = Image.new("RGB", (cols * thumb, len(rows) * (thumb + label_h)), (154, 154, 154))
    draw = ImageDraw.Draw(canvas)
    for row_index, row in enumerate(rows):
        for col_index, (label, path) in enumerate(row):
            with Image.open(path) as opened:
                image = opened.convert("RGB")
                image.thumbnail((thumb, thumb), Image.Resampling.LANCZOS)
                x = col_index * thumb + (thumb - image.width) // 2
                y = row_index * (thumb + label_h) + (thumb - image.height) // 2
                canvas.paste(image, (x, y))
            label_y = row_index * (thumb + label_h) + thumb
            draw.rectangle((col_index * thumb, label_y, (col_index + 1) * thumb - 1, label_y + label_h - 1), fill=(38, 38, 38))
            draw.text((col_index * thumb + 7, label_y + 9), label, fill=(240, 240, 240))
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, "PNG")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comfy-root", required=True, type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--klein-workspace", required=True, type=Path)
    parser.add_argument("--port", type=int, default=8193)
    parser.add_argument("--timeout-minutes", type=int, default=480)
    parser.add_argument("--comfy-commit", required=True)
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    klein = args.klein_workspace.resolve()
    output_dir = workspace / "qwen2511_precision_gate"
    output_dir.mkdir(parents=True, exist_ok=True)

    original = klein / "spike" / "flux2_klein_4b_t2i_probe.png"
    klein_plank = klein / "base_atomic_sequence" / "atomic_plank.png"
    klein_strap = klein / "base_atomic_sequence" / "atomic_strap.png"
    q2509_plank = workspace / "feasibility_gate" / "qwen2509_atomic_plank.png"
    q2509_strap = workspace / "feasibility_gate" / "qwen2509_atomic_strap.png"
    for required in (original, klein_plank, klein_strap, q2509_plank, q2509_strap):
        if not required.is_file():
            raise FileNotFoundError(required)

    print(f"RUNNER63-PYTHON: Asset Studio module root={MODULE_ROOT}", flush=True)
    adapter = QwenImageEdit2511Adapter(
        args.comfy_root,
        f"http://127.0.0.1:{args.port}",
        timeout_minutes=args.timeout_minutes,
    )
    started = time.time()

    plank_results = []
    strap_results = []
    for steps in STEP_SERIES:
        plank_results.append(run_edit(
            adapter, output_dir, "atomic_plank", PROMPT_PLANK, original, steps,
            f"qwen2511_atomic_plank_steps{steps:02d}.png"
        ))
    for steps in STEP_SERIES:
        strap_results.append(run_edit(
            adapter, output_dir, "atomic_strap", PROMPT_STRAP, original, steps,
            f"qwen2511_atomic_strap_steps{steps:02d}.png"
        ))

    contact = output_dir / "runner63_qwen2511_precision_contact_sheet.png"
    make_contact_sheet([
        [
            ("ORIGINAL", original),
            ("KLEIN PLANK", klein_plank),
            ("QWEN2509 PLANK", q2509_plank),
            ("QWEN2511 PLANK 20", plank_results[0].output_path),
            ("QWEN2511 PLANK 40", plank_results[1].output_path),
        ],
        [
            ("ORIGINAL", original),
            ("KLEIN STRAP", klein_strap),
            ("QWEN2509 STRAP", q2509_strap),
            ("QWEN2511 STRAP 20", strap_results[0].output_path),
            ("QWEN2511 STRAP 40", strap_results[1].output_path),
        ],
    ], contact)

    manifest = {
        "gate": "ASSET_STUDIO_QWEN_IMAGE_EDIT_2511_ATOMIC_PRECISION",
        "technical_status": "QWEN2511_PRECISION_MATRIX_COMPLETE",
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "comfy_commit": args.comfy_commit,
        "source": str(original),
        "source_sha256": sha256_file(original),
        "comparison_qwen2509": {
            "plank": str(q2509_plank), "plank_sha256": sha256_file(q2509_plank),
            "strap": str(q2509_strap), "strap_sha256": sha256_file(q2509_strap),
        },
        "comparison_klein": {
            "plank": str(klein_plank), "plank_sha256": sha256_file(klein_plank),
            "strap": str(klein_strap), "strap_sha256": sha256_file(klein_strap),
        },
        "runtime_recipe": {
            "model": "qwen_image_edit_2511_fp8mixed.safetensors",
            "text_encoder": "qwen_2.5_vl_7b_fp8_scaled.safetensors",
            "text_encoder_device": "cpu",
            "vae": "qwen_image_vae.safetensors",
            "reference_latents_method": "index_timestep_zero",
            "model_sampling": "AuraFlow shift 3.1",
            "cfg_norm": 1.0,
            "step_series": list(STEP_SERIES),
            "cfg": CFG,
            "sampler": SAMPLER,
            "scheduler": "simple",
            "denoise": 1.0,
            "lightning_lora": False,
        },
        "plank_results": [result_record(r, original) for r in plank_results],
        "strap_results": [result_record(r, original) for r in strap_results],
        "contact_sheet": str(contact),
        "contact_sheet_sha256": sha256_file(contact),
        "elapsed_total_seconds": round(time.time() - started, 3),
        "visual_pass_contract": {
            "plank": "At least one 2511 result must remove approximately one plank-width as a narrow full-height opening while retaining neighboring boards and unrelated gate geometry.",
            "strap": "At least one 2511 result must break only the named lower-right strap, leaving snapped/deformed surviving ends without redesigning other hardware or damaging door planks.",
            "comparison": "2511 must materially improve exact structural-fact compliance over both Runner62 Qwen 2509 and Runner61 Klein Base.",
            "next": "If precision passes, advance to multi-reference semantic-role and Character Lab validation. If it fails at both 20/40 steps, stop blind step tuning and move to automatic localization/control architecture or another editor family."
        },
    }
    manifest_path = output_dir / "runner63_qwen2511_precision_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print("RUNNER63-QWEN2511: PASS - TECHNICAL PRECISION MATRIX COMPLETE / VISUAL VERDICT PENDING", flush=True)
    print(f"Contact sheet: {contact}", flush=True)
    print(f"Manifest: {manifest_path}", flush=True)
    print(f"Total elapsed: {manifest['elapsed_total_seconds']:.3f}s", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as exc:
        print(f"RUNNER63-PYTHON-FAIL: {type(exc).__name__}: {exc}", file=sys.stdout, flush=True)
        traceback.print_exc(file=sys.stdout)
        raise SystemExit(1)
