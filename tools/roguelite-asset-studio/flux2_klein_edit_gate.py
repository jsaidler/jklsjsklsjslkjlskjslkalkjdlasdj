#!/usr/bin/env python3
"""Runner57 execution payload: validate Klein single/multi-reference editing.

The gate uses the Runner56 architecture module rather than a character-specific graph.
It first performs one controlled single-reference revision, then performs a two-reference
composition where the original is explicitly the structure authority and the first edit
is the damage/material authority. The adapter receives only generic Asset Studio roles.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

WIDTH = 768
HEIGHT = 768

SINGLE_PROMPT = """Edit Image 1, which is the authoritative existing architectural master. Keep the same gate identity, overall front-three-quarter camera, masonry mass, doorway proportions and complete isolated-object framing. Make the ruin materially harsher and less like a neat fantasy asset-store model: introduce stronger asymmetry in the broken lintel, remove the decorative feeling of evenly distributed cracks, make several losses and fractures causally larger, warp and damage the wooden doors, remove or break some planks and iron straps, deepen corrosion and accumulated dirt, and make roots/debris feel opportunistic rather than decoratively placed. Preserve believable load-bearing construction. Keep the whole gate visible on a simple neutral authoring background. No people, creatures, text, UI or scenic landscape. Do not redesign it into a different building."""

MULTI_PROMPT = """Create one revised version of the same gate using two ordered references. Image 1 is authoritative for identity, silhouette, camera, doorway proportions and underlying construction. Image 2 is authoritative only for the harsher damage state, material aging, corrosion, broken-door treatment and loss of neat symmetry. Preserve the recognizable gate from Image 1 while carrying forward the most convincing physical decay from Image 2. Do not average the camera or create two gates. Keep one complete isolated gate with margin on a simple neutral authoring background. No people, creatures, lettering, UI or landscape."""


def result_record(result) -> dict:
    return {
        "adapter_id": result.adapter_id,
        "prompt_id": result.prompt_id,
        "output": str(result.output_path),
        "output_sha256": result.output_sha256,
        "elapsed_seconds": round(result.elapsed_seconds, 3),
        "reference_roles": [reference.role for reference in result.request.references],
        "reference_hashes": list(result.reference_hashes),
        "prompt": result.request.prompt,
        "width": result.request.width,
        "height": result.request.height,
        "steps": result.request.steps,
        "cfg": result.request.cfg,
        "sampler": result.request.sampler,
        "seed": result.request.seed,
    }


def make_comparison(paths: list[Path], destination: Path) -> None:
    images = []
    for path in paths:
        with Image.open(path) as opened:
            opened.load()
            images.append(opened.convert("RGB"))
    width = sum(image.width for image in images)
    height = max(image.height for image in images)
    canvas = Image.new("RGB", (width, height), (128, 128, 128))
    x = 0
    for image in images:
        canvas.paste(image, (x, 0))
        x += image.width
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, format="PNG")


def main() -> int:
    # Import project adapter modules inside main so import-time failures are caught by
    # the top-level diagnostic handler instead of disappearing into PowerShell stderr.
    from adapter_protocol import ReferenceInput, StaticGenerationRequest
    from flux2_klein_adapter import Flux2KleinAdapter, sha256_file

    print("RUNNER57-PYTHON: project adapter imports OK", flush=True)

    parser = argparse.ArgumentParser()
    parser.add_argument("--comfy-root", required=True, type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--port", type=int, default=8192)
    parser.add_argument("--timeout-minutes", type=int, default=180)
    parser.add_argument("--comfy-commit", required=True)
    args = parser.parse_args()

    print("RUNNER57-PYTHON: arguments parsed", flush=True)
    workspace = args.workspace.resolve()
    gate_dir = workspace / "edit_gate"
    gate_dir.mkdir(parents=True, exist_ok=True)
    original = workspace / "spike" / "flux2_klein_4b_t2i_probe.png"
    if not original.is_file():
        raise FileNotFoundError(
            f"Runner56 source output is required before Runner57: {original}"
        )
    print(f"RUNNER57-PYTHON: Runner56 source verified: {original}", flush=True)

    adapter = Flux2KleinAdapter(
        args.comfy_root,
        f"http://127.0.0.1:{args.port}",
        timeout_minutes=args.timeout_minutes,
    )
    print("RUNNER57-PYTHON: adapter constructed", flush=True)

    single_destination = gate_dir / "flux2_klein_single_reference_edit.png"
    single_request = StaticGenerationRequest(
        job_id="runner57_single_reference_gate",
        asset_type="architecture_module",
        output_contract="static_master",
        prompt=SINGLE_PROMPT,
        references=(ReferenceInput("previous_approved_state", original),),
        width=WIDTH,
        height=HEIGHT,
        steps=4,
        cfg=1.0,
        sampler="euler",
        seed=0,
    )
    print("RUNNER57: single-reference edit -> submitting", flush=True)
    single_result = adapter.generate(single_request, single_destination)
    print(
        f"RUNNER57: single-reference edit complete in {single_result.elapsed_seconds:.3f}s",
        flush=True,
    )

    multi_destination = gate_dir / "flux2_klein_multi_reference_edit.png"
    multi_request = StaticGenerationRequest(
        job_id="runner57_multi_reference_gate",
        asset_type="architecture_module",
        output_contract="static_master",
        prompt=MULTI_PROMPT,
        references=(
            ReferenceInput("structure", original),
            ReferenceInput("material", single_destination),
        ),
        width=WIDTH,
        height=HEIGHT,
        steps=4,
        cfg=1.0,
        sampler="euler",
        seed=0,
    )
    print("RUNNER57: multi-reference edit -> submitting", flush=True)
    multi_result = adapter.generate(multi_request, multi_destination)
    print(
        f"RUNNER57: multi-reference edit complete in {multi_result.elapsed_seconds:.3f}s",
        flush=True,
    )

    comparison = gate_dir / "flux2_klein_edit_gate_comparison_original_single_multi.png"
    make_comparison([original, single_destination, multi_destination], comparison)

    manifest = {
        "gate": "ASSET_STUDIO_FLUX2_KLEIN_4B_DISTILLED_REFERENCE_EDIT",
        "technical_status": "SINGLE_AND_MULTI_REFERENCE_INFERENCE_COMPLETE",
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "comfy_commit": args.comfy_commit,
        "source_runner56_output": str(original),
        "source_runner56_sha256": sha256_file(original),
        "single_reference": result_record(single_result),
        "multi_reference": result_record(multi_result),
        "comparison": str(comparison),
        "comparison_sha256": sha256_file(comparison),
        "pass_contract": {
            "technical": "Both one-reference and ordered two-reference jobs complete through the generic FLUX.2 Klein adapter at 768x768 / 4 steps without OOM or graph failure.",
            "single_visual": "The first edit must remain recognizably the same gate while making the requested damage/material changes instead of replacing the asset wholesale.",
            "multi_visual": "The two-reference result must preserve Image 1 structure/identity while carrying forward useful damage/material information from Image 2, without duplicating or averaging the object into incoherence.",
            "scope": "This proves generic still editing; it does not yet prove Exilada identity/anatomy preservation or final pixel-art reconstruction.",
        },
    }
    manifest_path = gate_dir / "flux2_klein_edit_gate_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print("RUNNER57-FLUX2-KLEIN-EDIT: PASS - TECHNICAL SINGLE+MULTI REFERENCE COMPLETE / VISUAL VERDICT PENDING", flush=True)
    print(f"Single: {single_destination}", flush=True)
    print(f"Multi: {multi_destination}", flush=True)
    print(f"Comparison: {comparison}", flush=True)
    print(f"Manifest: {manifest_path}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as exc:
        # Windows PowerShell 5.x can promote native stderr to NativeCommandError
        # when ErrorActionPreference=Stop. Emit every diagnostic to stdout so the
        # runner can preserve the full traceback deterministically.
        print(
            f"RUNNER57-PYTHON-FAIL: {type(exc).__name__}: {exc}",
            file=sys.stdout,
            flush=True,
        )
        traceback.print_exc(file=sys.stdout)
        raise SystemExit(1)
