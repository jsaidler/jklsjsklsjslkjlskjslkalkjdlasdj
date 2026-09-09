#!/usr/bin/env python3
"""Runner59: validate FLUX.2 Klein 4B Base as the stronger edit branch.

Runner58 exhausted the distilled 4B recipe enough to show that stronger step counts
increase visual drift without reliably executing major structural edits. Runner59 keeps
the same model family, license, source gate, material reference and semantic roles, but
switches to the non-distilled 4B Base model and its official small-decoder path.
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
from flux2_klein_base_adapter import Flux2KleinBaseAdapter

WIDTH = 768
HEIGHT = 768
CFG = 5.0
SAMPLER = "euler"
SEED = 0
STEP_SERIES = (20, 50)

SINGLE_PROMPT = """Edit Image 1. It is the authoritative identity and construction of the same ruined gate. Keep exactly one gate, the same front-three-quarter camera, the same overall masonry footprint, doorway proportions and neutral authoring background. Execute these changes as clear structural facts, not subtle decoration: (1) remove one entire vertical plank from the LEFT door leaf, leaving a full-height open gap; (2) break away one large top-left lintel/capstone block so the top silhouette is visibly missing that mass; (3) snap and partially remove the LOWER iron strap on the RIGHT door leaf; (4) add strong orange-brown corrosion and black grime to surviving iron; (5) make surviving timber visibly warped, split and water-damaged. Preserve the rest of the recognizable gate and believable load-bearing construction. Do not merely add small cracks. Do not create a different gate. No people, creatures, text, logo, UI or landscape."""

MULTI_PROMPT = """Revise one gate using two ordered references. Image 1 is absolute authority for gate identity, camera, masonry footprint and doorway proportions. Image 2 is authority only for material severity: corroded iron, black grime, warped split timber, chipped stone, packed dirt, moss and opportunistic roots. Preserve one recognizable gate from Image 1 while strongly importing the material language of Image 2. Also execute these structural facts: remove one entire vertical plank from the LEFT door leaf; break away one large top-left capstone/lintel block; snap and partially remove the LOWER iron strap on the RIGHT door leaf. Do not average the images, do not reproduce the material board as scenery, do not create two gates, and do not change the camera. Neutral authoring background only. No people, creatures, text, logo, UI or landscape."""


def diff_metrics(reference: Path, candidate: Path) -> dict:
    with Image.open(reference) as a_open, Image.open(candidate) as b_open:
        a = a_open.convert("RGB")
        b = b_open.convert("RGB")
        if a.size != b.size:
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


def result_record(result, original: Path) -> dict:
    return {
        "adapter_id": result.adapter_id,
        "prompt_id": result.prompt_id,
        "output": str(result.output_path),
        "output_sha256": result.output_sha256,
        "elapsed_seconds": round(result.elapsed_seconds, 3),
        "reference_roles": [r.role for r in result.request.references],
        "reference_hashes": list(result.reference_hashes),
        "prompt": result.request.prompt,
        "width": result.request.width,
        "height": result.request.height,
        "steps": result.request.steps,
        "cfg": result.request.cfg,
        "sampler": result.request.sampler,
        "seed": result.request.seed,
        "difference_from_original": diff_metrics(original, result.output_path),
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
            draw.rectangle(
                (col * thumb_w, row * (thumb_h + label_h) + thumb_h, (col + 1) * thumb_w - 1, (row + 1) * (thumb_h + label_h) - 1),
                fill=(40, 40, 40),
            )
            draw.text((col * thumb_w + 8, row * (thumb_h + label_h) + thumb_h + 9), label, fill=(240, 240, 240))
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, format="PNG")


def run_request(adapter, request, output: Path, label: str):
    print(f"RUNNER59: {label} -> submitting", flush=True)
    result = adapter.generate(request, output)
    print(f"RUNNER59: {label} complete in {result.elapsed_seconds:.3f}s -> {output}", flush=True)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comfy-root", required=True, type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--port", type=int, default=8192)
    parser.add_argument("--timeout-minutes", type=int, default=180)
    parser.add_argument("--comfy-commit", required=True)
    args = parser.parse_args()

    print(f"RUNNER59-PYTHON: Asset Studio module root={MODULE_ROOT}", flush=True)
    workspace = args.workspace.resolve()
    output_dir = workspace / "base_edit_gate"
    output_dir.mkdir(parents=True, exist_ok=True)

    original = workspace / "spike" / "flux2_klein_4b_t2i_probe.png"
    material = workspace / "edit_strength_calibration" / "material_decay_reference.png"
    if not original.is_file():
        raise FileNotFoundError(f"Runner56 original is required: {original}")
    if not material.is_file():
        raise FileNotFoundError(f"Runner58 material reference is required: {material}")

    adapter = Flux2KleinBaseAdapter(
        args.comfy_root,
        f"http://127.0.0.1:{args.port}",
        timeout_minutes=args.timeout_minutes,
    )

    started_all = time.time()
    singles = []
    for steps in STEP_SERIES:
        destination = output_dir / f"base_single_binary_steps{steps:02d}.png"
        request = StaticGenerationRequest(
            job_id=f"runner59_base_single_steps{steps:02d}",
            asset_type="architecture_module",
            output_contract="static_master",
            prompt=SINGLE_PROMPT,
            references=(ReferenceInput("previous_approved_state", original),),
            width=WIDTH,
            height=HEIGHT,
            steps=steps,
            cfg=CFG,
            sampler=SAMPLER,
            seed=SEED,
        )
        singles.append(run_request(adapter, request, destination, f"Base single-reference {steps} steps"))

    multis = []
    for steps in STEP_SERIES:
        destination = output_dir / f"base_multi_structure_material_steps{steps:02d}.png"
        request = StaticGenerationRequest(
            job_id=f"runner59_base_multi_steps{steps:02d}",
            asset_type="architecture_module",
            output_contract="static_master",
            prompt=MULTI_PROMPT,
            references=(
                ReferenceInput("structure", original),
                ReferenceInput("material", material),
            ),
            width=WIDTH,
            height=HEIGHT,
            steps=steps,
            cfg=CFG,
            sampler=SAMPLER,
            seed=SEED,
        )
        multis.append(run_request(adapter, request, destination, f"Base multi-reference {steps} steps"))

    contact_sheet = output_dir / "runner59_base_contact_sheet.png"
    sheet_items = [("ORIGINAL", original)]
    sheet_items.extend((f"BASE SINGLE {r.request.steps}", r.output_path) for r in singles)
    sheet_items.append(("MATERIAL REF", material))
    sheet_items.extend((f"BASE MULTI {r.request.steps}", r.output_path) for r in multis)
    make_contact_sheet(sheet_items, contact_sheet)

    manifest = {
        "gate": "ASSET_STUDIO_FLUX2_KLEIN_BASE_EDIT_GATE",
        "technical_status": "BASE_EDIT_MATRIX_COMPLETE",
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "comfy_commit": args.comfy_commit,
        "source_original": str(original),
        "source_original_sha256": sha256_file(original),
        "source_material_reference": str(material),
        "source_material_reference_sha256": sha256_file(material),
        "purpose": "Test the non-distilled Apache-2.0 FLUX.2 Klein 4B Base branch after the distilled branch failed the production edit-strength gate.",
        "controlled_settings": {
            "width": WIDTH,
            "height": HEIGHT,
            "cfg": CFG,
            "sampler": SAMPLER,
            "seed": SEED,
            "step_series": list(STEP_SERIES),
            "recipe_basis": "Current official ComfyUI Base edit template uses Euler, CFG 5 and 20 steps; 50 steps is included because the Base family is documented as the full-step/flexibility branch.",
        },
        "single_reference_results": [result_record(r, original) for r in singles],
        "multi_reference_results": [result_record(r, original) for r in multis],
        "contact_sheet": str(contact_sheet),
        "contact_sheet_sha256": sha256_file(contact_sheet),
        "elapsed_total_seconds": round(time.time() - started_all, 3),
        "visual_pass_contract": {
            "single_reference": "At least one Base result must preserve recognizable gate identity/camera while clearly executing the missing full plank, missing large top-left block and broken lower-right strap, with materially stronger decay.",
            "multi_reference": "At least one Base result must preserve Image 1 structure/camera while visibly importing the material authority of Image 2 and executing the same structural facts.",
            "failure_consequence": "If Base also fails, keep Klein 4B family for static concept/T2I only and move reference editing to a stronger specialized editor branch; do not keep increasing steps blindly.",
        },
    }
    manifest_path = output_dir / "runner59_base_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print("RUNNER59-FLUX2-KLEIN-BASE-EDIT: PASS - TECHNICAL MATRIX COMPLETE / VISUAL VERDICT PENDING", flush=True)
    print(f"Contact sheet: {contact_sheet}", flush=True)
    print(f"Manifest: {manifest_path}", flush=True)
    print(f"Total elapsed: {manifest['elapsed_total_seconds']:.3f}s", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as exc:
        print(f"RUNNER59-PYTHON-FAIL: {type(exc).__name__}: {exc}", file=sys.stdout, flush=True)
        traceback.print_exc(file=sys.stdout)
        raise SystemExit(1)
