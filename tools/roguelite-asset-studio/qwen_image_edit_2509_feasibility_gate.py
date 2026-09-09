#!/usr/bin/env python3
"""Runner62: Qwen-Image-Edit-2509 native FP8 low-VRAM + atomic precision gate."""

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
from qwen_image_edit_2509_adapter import QwenImageEdit2509Adapter

STEPS = 20
CFG = 4.0
SAMPLER = "euler"
SEED = 0

COMMON = """Edit Image 1 only. Preserve the exact same ruined gate identity, front-three-quarter camera, doorway proportions, masonry footprint, neutral authoring background, natural gray stone, brown wood, dark aged iron, roots and moss. Keep all unrelated geometry unchanged. Do not redesign the gate. No people, creatures, text, logo, UI or landscape."""

PLANK_PROMPT = COMMON + """ Make exactly ONE structural change: remove ONE SINGLE vertical wooden plank from the LEFT door leaf, not the whole door leaf. The removed plank must be one plank-width only and absent from top to bottom, leaving a narrow full-height open gap. Every neighboring plank must remain present. The right door leaf, all masonry and all iron straps must remain otherwise unchanged."""

STRAP_PROMPT = COMMON + """ Make exactly ONE structural change: break and partially remove ONLY the LOWER horizontal iron strap on the RIGHT door leaf. Remove a substantial middle section of that one strap and leave a visibly snapped/deformed surviving end. Keep every wooden plank present, keep the other iron hardware unchanged, and keep all upper masonry unchanged. Do not replace or redesign the hardware set."""


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


def record(result, source: Path) -> dict:
    with Image.open(result.output_path) as opened:
        size = list(opened.size)
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
        "difference_from_original": diff_metrics(source, result.output_path),
    }


def make_contact_sheet(items: list[tuple[str, Path]], destination: Path) -> None:
    thumb_w = 512
    thumb_h = 512
    label_h = 34
    cols = 3
    rows = (len(items) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (150, 150, 150))
    draw = ImageDraw.Draw(canvas)
    for index, (label, path) in enumerate(items):
        with Image.open(path) as opened:
            image = opened.convert("RGB")
            image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            col = index % cols
            row = index // cols
            x0 = col * thumb_w + (thumb_w - image.width) // 2
            y0 = row * (thumb_h + label_h) + (thumb_h - image.height) // 2
            canvas.paste(image, (x0, y0))
            y_label = row * (thumb_h + label_h) + thumb_h
            draw.rectangle((col * thumb_w, y_label, (col + 1) * thumb_w - 1, y_label + label_h - 1), fill=(40, 40, 40))
            draw.text((col * thumb_w + 8, y_label + 9), label, fill=(240, 240, 240))
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, format="PNG")


def run_edit(adapter, output_dir: Path, source: Path, job_id: str, prompt: str, filename: str, label: str):
    request = StaticGenerationRequest(
        job_id=job_id,
        asset_type="architecture_module",
        output_contract="static_master",
        prompt=prompt,
        negative="",
        references=(ReferenceInput("previous_approved_state", source),),
        width=1024,
        height=1024,
        steps=STEPS,
        cfg=CFG,
        sampler=SAMPLER,
        seed=SEED,
    )
    destination = output_dir / filename
    print(f"RUNNER62: {label} -> submitting", flush=True)
    result = adapter.generate(request, destination)
    print(f"RUNNER62: {label} complete in {result.elapsed_seconds:.3f}s -> {destination}", flush=True)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comfy-root", required=True, type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--klein-plank", required=True, type=Path)
    parser.add_argument("--klein-strap", required=True, type=Path)
    parser.add_argument("--port", type=int, default=8193)
    parser.add_argument("--timeout-minutes", type=int, default=360)
    parser.add_argument("--comfy-commit", required=True)
    args = parser.parse_args()

    source = args.source.resolve()
    klein_plank = args.klein_plank.resolve()
    klein_strap = args.klein_strap.resolve()
    for required in (source, klein_plank, klein_strap):
        if not required.is_file():
            raise FileNotFoundError(required)

    workspace = args.workspace.resolve()
    output_dir = workspace / "feasibility_gate"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"RUNNER62-PYTHON: Asset Studio module root={MODULE_ROOT}", flush=True)
    print(f"RUNNER62-PYTHON: source={source}", flush=True)

    adapter = QwenImageEdit2509Adapter(
        args.comfy_root,
        f"http://127.0.0.1:{args.port}",
        timeout_minutes=args.timeout_minutes,
    )
    started_all = time.time()

    plank = run_edit(
        adapter, output_dir, source,
        "runner62_qwen2509_atomic_plank", PLANK_PROMPT,
        "qwen2509_atomic_plank.png", "Qwen 2509 atomic one-plank removal",
    )
    strap = run_edit(
        adapter, output_dir, source,
        "runner62_qwen2509_atomic_strap", STRAP_PROMPT,
        "qwen2509_atomic_strap.png", "Qwen 2509 atomic one-strap break",
    )

    contact = output_dir / "runner62_qwen2509_vs_klein_contact_sheet.png"
    make_contact_sheet([
        ("ORIGINAL", source),
        ("KLEIN ATOMIC PLANK", klein_plank),
        ("QWEN 2509 ATOMIC PLANK", plank.output_path),
        ("ORIGINAL", source),
        ("KLEIN ATOMIC STRAP", klein_strap),
        ("QWEN 2509 ATOMIC STRAP", strap.output_path),
    ], contact)

    manifest = {
        "gate": "ASSET_STUDIO_QWEN_IMAGE_EDIT_2509_LOWVRAM_ATOMIC_PRECISION",
        "technical_status": "QWEN2509_ATOMIC_MATRIX_COMPLETE",
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "comfy_commit": args.comfy_commit,
        "source": str(source),
        "source_sha256": sha256_file(source),
        "klein_comparison": {
            "plank": str(klein_plank),
            "plank_sha256": sha256_file(klein_plank),
            "strap": str(klein_strap),
            "strap_sha256": sha256_file(klein_strap),
        },
        "purpose": "Determine whether native Qwen-Image-Edit-2509 FP8 is feasible on RTX 3060 12GB with CPU text encoder/offload and whether it improves atomic structural precision over parity-valid Klein Base.",
        "runtime_recipe": {
            "model": "qwen_image_edit_2509_fp8_e4m3fn.safetensors",
            "text_encoder": "qwen_2.5_vl_7b_fp8_scaled.safetensors",
            "text_encoder_device": "cpu",
            "vae": "qwen_image_vae.safetensors",
            "model_sampling": "AuraFlow shift 3",
            "cfg_norm": 1.0,
            "steps": STEPS,
            "cfg": CFG,
            "sampler": SAMPLER,
            "scheduler": "simple",
            "denoise": 1.0,
            "lightning_lora": False,
        },
        "plank_result": record(plank, source),
        "strap_result": record(strap, source),
        "contact_sheet": str(contact),
        "contact_sheet_sha256": sha256_file(contact),
        "elapsed_total_seconds": round(time.time() - started_all, 3),
        "visual_pass_contract": {
            "plank": "Remove one plank-width only, preserve neighboring planks and unrelated gate geometry; this must be materially more precise than Klein Runner61, which removed almost the whole left leaf.",
            "strap": "Break only the specified lower-right strap while preserving the remaining hardware/planks/masonry; this must be materially more precise than Klein Runner61's broad hardware reinterpretation.",
            "production_decision": "Technical success plus clear precision improvement promotes Qwen 2509 to the next multi-reference/character validation. OOM/runtime failure triggers a lower-memory implementation study; visual failure triggers reconsideration of the editor branch rather than blind step increases.",
        },
    }
    manifest_path = output_dir / "runner62_qwen2509_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print("RUNNER62-QWEN2509: PASS - TECHNICAL ATOMIC MATRIX COMPLETE / VISUAL VERDICT PENDING", flush=True)
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
        print(f"RUNNER62-PYTHON-FAIL: {type(exc).__name__}: {exc}", file=sys.stdout, flush=True)
        traceback.print_exc(file=sys.stdout)
        raise SystemExit(1)
