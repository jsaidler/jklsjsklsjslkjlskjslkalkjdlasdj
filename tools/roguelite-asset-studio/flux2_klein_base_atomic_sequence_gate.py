#!/usr/bin/env python3
"""Runner61: FLUX.2 Klein 4B Base atomic + sequential edit obedience gate.

Runner60 established a parity-valid Base graph and showed sane VAE/T2I/reference-edit
colour behavior, but one prompt containing several independent structural edits still did
not satisfy the full production contract. Runner61 tests the remaining same-family
hypothesis: whether the Base model is useful when each structural instruction is atomic
and complex revisions are composed through successive approved-state edits.

No new model or graph variant is introduced. The exact official-parity Base adapter from
Runner60 is reused.
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

WIDTH = 1024
HEIGHT = 1024
STEPS = 20
CFG = 5.0
SAMPLER = "euler"
SEED = 0

COMMON_IDENTITY = """Image 1 is the authoritative identity, camera and construction of this same ruined gate. Keep exactly one recognizable gate, the same front-three-quarter camera, the same doorway proportions, the same neutral authoring background and all unrelated geometry unchanged. Preserve natural gray stone, brown wood, dark aged iron and muted green vegetation. Do not redesign the whole gate. No people, creatures, text, logo, UI or landscape."""

PROMPT_PLANK = COMMON_IDENTITY + """ Make exactly one primary structural change: REMOVE ONE ENTIRE VERTICAL WOODEN PLANK from the LEFT door leaf. The plank must be completely absent from top to bottom, leaving a clear full-height open gap through which the dark interior/background is visible. Do not merely split, darken, narrow or weather a plank. Do not change the top masonry or the right door hardware."""

PROMPT_CAPSTONE = COMMON_IDENTITY + """ Make exactly one primary structural change: REMOVE ONE LARGE TOP-LEFT CAPSTONE/LINTEL BLOCK from the broken upper masonry so that a conspicuous chunk of mass is physically absent and the top silhouette has a clear new notch/open void. Do not merely add a crack or recolor the stone. Do not alter the door planks or lower iron straps."""

PROMPT_STRAP = COMMON_IDENTITY + """ Make exactly one primary structural change: BREAK AND PARTIALLY REMOVE THE LOWER IRON STRAP on the RIGHT door leaf. The strap must no longer span the door normally: one substantial section is missing and the surviving end is visibly snapped/deformed. Keep the door planks and top masonry otherwise unchanged. Add realistic rust only to the surviving broken metal."""

PROMPT_STAGE2 = """Image 1 is the authoritative current approved state of the same ruined gate. Preserve the full-height missing plank already present in the LEFT door leaf exactly as it is. Preserve the same camera, doorway proportions, neutral background and all unrelated geometry. Make exactly one new structural change: REMOVE ONE LARGE TOP-LEFT CAPSTONE/LINTEL BLOCK so that a conspicuous mass is physically absent and the top silhouette gains a clear notch/open void. Do not restore or close the missing door-plank gap. Natural gray stone, brown wood, dark iron and muted vegetation. No people, text, UI or landscape."""

PROMPT_STAGE3 = """Image 1 is the authoritative current approved state of the same ruined gate. Preserve BOTH existing structural changes exactly: the full-height missing plank in the LEFT door leaf and the missing top-left capstone/lintel mass. Preserve the same camera, proportions and neutral background. Make exactly one new structural change: BREAK AND PARTIALLY REMOVE THE LOWER IRON STRAP on the RIGHT door leaf so one substantial section is absent and the surviving end is visibly snapped/deformed. Do not restore either earlier structural change. Natural gray stone, brown wood, dark aged iron and muted vegetation. No people, text, UI or landscape."""

PROMPT_MATERIAL = """Revise one gate using two ordered references. Image 1 is absolute authority for identity, camera, geometry and EVERY structural change already present, including any missing door plank, missing upper masonry mass and broken lower-right iron strap. Image 2 is authority ONLY for material severity: orange-brown flaking corrosion, dark grime, warped split water-damaged timber, chipped stone, dirt, moss and opportunistic roots. Import the material aging from Image 2 while preserving all Image 1 geometry and openings. Do not restore missing pieces, do not move the camera, do not average the two images, and do not reproduce the material board as scenery. Neutral authoring background only. No people, creatures, text, logo, UI or landscape."""


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


def result_record(result, comparison_reference: Path) -> dict:
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
        "image_size": list(Image.open(result.output_path).size),
        "difference_from_comparison_reference": diff_metrics(comparison_reference, result.output_path),
    }


def run_edit(adapter, output_dir: Path, job_id: str, prompt: str, refs: tuple[ReferenceInput, ...], filename: str, label: str):
    destination = output_dir / filename
    request = StaticGenerationRequest(
        job_id=job_id,
        asset_type="architecture_module",
        output_contract="static_master",
        prompt=prompt,
        negative="",
        references=refs,
        width=WIDTH,
        height=HEIGHT,
        steps=STEPS,
        cfg=CFG,
        sampler=SAMPLER,
        seed=SEED,
    )
    print(f"RUNNER61: {label} -> submitting", flush=True)
    result = adapter.generate(request, destination)
    print(f"RUNNER61: {label} complete in {result.elapsed_seconds:.3f}s -> {destination}", flush=True)
    return result


def make_contact_sheet(items: list[tuple[str, Path]], destination: Path) -> None:
    thumb_w = 512
    thumb_h = 512
    label_h = 34
    cols = 4
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comfy-root", required=True, type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--port", type=int, default=8192)
    parser.add_argument("--timeout-minutes", type=int, default=240)
    parser.add_argument("--comfy-commit", required=True)
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    output_dir = workspace / "base_atomic_sequence"
    output_dir.mkdir(parents=True, exist_ok=True)
    original = workspace / "spike" / "flux2_klein_4b_t2i_probe.png"
    material = workspace / "edit_strength_calibration" / "material_decay_reference.png"
    for required in (original, material):
        if not required.is_file():
            raise FileNotFoundError(required)

    print(f"RUNNER61-PYTHON: Asset Studio module root={MODULE_ROOT}", flush=True)
    adapter = Flux2KleinBaseAdapter(
        args.comfy_root,
        f"http://127.0.0.1:{args.port}",
        timeout_minutes=args.timeout_minutes,
    )
    started_all = time.time()

    independent = []
    independent.append(run_edit(
        adapter, output_dir, "runner61_atomic_plank", PROMPT_PLANK,
        (ReferenceInput("previous_approved_state", original),),
        "atomic_plank.png", "atomic plank removal"
    ))
    independent.append(run_edit(
        adapter, output_dir, "runner61_atomic_capstone", PROMPT_CAPSTONE,
        (ReferenceInput("previous_approved_state", original),),
        "atomic_capstone.png", "atomic capstone removal"
    ))
    independent.append(run_edit(
        adapter, output_dir, "runner61_atomic_strap", PROMPT_STRAP,
        (ReferenceInput("previous_approved_state", original),),
        "atomic_strap.png", "atomic strap break"
    ))

    stage1 = run_edit(
        adapter, output_dir, "runner61_chain_stage1_plank", PROMPT_PLANK,
        (ReferenceInput("previous_approved_state", original),),
        "chain_stage1_plank.png", "chain stage 1 / plank"
    )
    stage2 = run_edit(
        adapter, output_dir, "runner61_chain_stage2_capstone", PROMPT_STAGE2,
        (ReferenceInput("previous_approved_state", stage1.output_path),),
        "chain_stage2_capstone.png", "chain stage 2 / preserve plank + remove capstone"
    )
    stage3 = run_edit(
        adapter, output_dir, "runner61_chain_stage3_strap", PROMPT_STAGE3,
        (ReferenceInput("previous_approved_state", stage2.output_path),),
        "chain_stage3_strap.png", "chain stage 3 / preserve prior + break strap"
    )
    materialized = run_edit(
        adapter, output_dir, "runner61_chain_stage4_material", PROMPT_MATERIAL,
        (
            ReferenceInput("structure", stage3.output_path),
            ReferenceInput("material", material),
        ),
        "chain_stage4_material.png", "chain stage 4 / preserve geometry + material authority"
    )

    contact_sheet = output_dir / "runner61_atomic_sequence_contact_sheet.png"
    make_contact_sheet([
        ("ORIGINAL", original),
        ("ATOMIC PLANK", independent[0].output_path),
        ("ATOMIC CAPSTONE", independent[1].output_path),
        ("ATOMIC STRAP", independent[2].output_path),
        ("CHAIN 1 PLANK", stage1.output_path),
        ("CHAIN 2 + CAPSTONE", stage2.output_path),
        ("CHAIN 3 + STRAP", stage3.output_path),
        ("CHAIN 4 + MATERIAL", materialized.output_path),
    ], contact_sheet)

    manifest = {
        "gate": "ASSET_STUDIO_FLUX2_KLEIN_BASE_ATOMIC_SEQUENCE",
        "technical_status": "ATOMIC_SEQUENCE_MATRIX_COMPLETE",
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "comfy_commit": args.comfy_commit,
        "source_original": str(original),
        "source_original_sha256": sha256_file(original),
        "source_material": str(material),
        "source_material_sha256": sha256_file(material),
        "purpose": "Determine whether parity-valid Klein Base can obey one structural fact per inference and compose complex edits sequentially before the project moves to another editor family.",
        "controlled_settings": {"steps": STEPS, "cfg": CFG, "sampler": SAMPLER, "seed": SEED, "reference_target_megapixels": 1.0},
        "independent_atomic_results": [result_record(r, original) for r in independent],
        "sequential_results": [
            {**result_record(stage1, original), "comparison_basis": "original"},
            {**result_record(stage2, stage1.output_path), "comparison_basis": "chain_stage1_plank"},
            {**result_record(stage3, stage2.output_path), "comparison_basis": "chain_stage2_capstone"},
            {**result_record(materialized, stage3.output_path), "comparison_basis": "chain_stage3_strap"},
        ],
        "contact_sheet": str(contact_sheet),
        "contact_sheet_sha256": sha256_file(contact_sheet),
        "elapsed_total_seconds": round(time.time() - started_all, 3),
        "visual_pass_contract": {
            "atomic": "Each independent atomic output should execute its one requested structural fact visibly while retaining gate identity/camera and leaving unrelated geometry substantially intact.",
            "sequence": "The sequential chain must preserve earlier successful structural facts while adding each new fact; later stages must not silently restore previously removed geometry.",
            "material": "The final two-reference pass must preserve all accumulated geometry while importing clearly stronger decay/material qualities from the material board.",
            "production_decision": "If atomic edits and the chain are useful, Base can be exposed as an iterative single-reference editor even if complex one-shot multi-edit prompts remain unsupported. If atomic edits themselves remain unreliable, the Base structural-edit hypothesis is exhausted and the project moves to the specialized editor branch.",
        },
    }
    manifest_path = output_dir / "runner61_atomic_sequence_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print("RUNNER61-FLUX2-KLEIN-BASE-ATOMIC: PASS - MATRIX COMPLETE / VISUAL VERDICT PENDING", flush=True)
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
        print(f"RUNNER61-PYTHON-FAIL: {type(exc).__name__}: {exc}", file=sys.stdout, flush=True)
        traceback.print_exc(file=sys.stdout)
        raise SystemExit(1)
