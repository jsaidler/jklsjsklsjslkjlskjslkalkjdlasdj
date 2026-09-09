#!/usr/bin/env python3
"""Runner60: FLUX.2 Klein 4B Base official-parity diagnostic gate.

Runner59 proved that the Base checkpoint can execute on the target workstation, but its
cyan/posterized output cannot be treated as a model-quality verdict because the custom
adapter diverged from the official ComfyUI Base edit graph at CFG 5.

Runner60 isolates the stack in layers:

1. full-encoder/small-decoder VAE round-trip with no diffusion;
2. proven full FLUX.2 VAE round-trip as a control;
3. Base text-to-image with the corrected Base conditioning graph;
4. Base single-reference edit at the official 20-step / CFG 5 / Euler recipe;
5. Base two-reference edit using the same corrected conditioning semantics.

No new model payload is downloaded by this executor.
"""

from __future__ import annotations

import argparse
import json
import shutil
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
from flux2_klein_adapter import VAE as FULL_VAE, VAE_SHA256 as FULL_VAE_SHA256, sha256_file
from flux2_klein_base_adapter import BASE_VAE, BASE_VAE_SHA256, Flux2KleinBaseAdapter

WIDTH = 1024
HEIGHT = 1024
STEPS = 20
CFG = 5.0
SAMPLER = "euler"
SEED = 0

T2I_PROMPT = """One isolated old ruined stone gate asset on a plain neutral gray authoring background. Gray chipped masonry, dark brown warped wooden double doors, black aged wrought-iron straps and hinges, muted green moss and roots, physically believable materials, coherent front-three-quarter view, full object visible with margin. Natural neutral color balance, no cyan cast, no illustration outline effect, no people, creatures, text, UI or landscape."""

SINGLE_PROMPT = """Edit Image 1. It is the authoritative identity and construction of the same ruined gate. Keep exactly one gate, the same front-three-quarter camera, the same overall masonry footprint and doorway proportions. Execute these changes as clear structural facts: remove one entire vertical plank from the LEFT door leaf leaving a full-height open gap; break away one large top-left lintel/capstone block so that mass is visibly absent from the silhouette; snap and partially remove the LOWER iron strap on the RIGHT door leaf; add strong orange-brown corrosion and black grime to surviving iron; make surviving timber visibly warped, split and water-damaged. Preserve the rest of the recognizable gate and believable load-bearing construction. Keep natural gray stone, brown wood, dark iron and muted green vegetation. Do not merely add small cracks. Do not create a different gate. Neutral authoring background only. No people, creatures, text, logo, UI or landscape."""

MULTI_PROMPT = """Revise one gate using two ordered references. Image 1 is absolute authority for gate identity, camera, masonry footprint and doorway proportions. Image 2 is authority only for material severity: corroded iron, black grime, warped split timber, chipped stone, packed dirt, moss and opportunistic roots. Preserve one recognizable gate from Image 1 while clearly importing the material language of Image 2. Also execute these structural facts: remove one entire vertical plank from the LEFT door leaf; break away one large top-left capstone/lintel block; snap and partially remove the LOWER iron strap on the RIGHT door leaf. Keep natural gray stone, brown wood, dark/rusted iron and muted green vegetation. Do not average the images, reproduce the material board as scenery, create two gates, or change the camera. Neutral authoring background only. No people, creatures, text, logo, UI or landscape."""


def image_stats(path: Path) -> dict:
    with Image.open(path) as opened:
        image = opened.convert("RGB")
        rgb = ImageStat.Stat(image)
        hsv = image.convert("HSV")
        hsv_stat = ImageStat.Stat(hsv)
        return {
            "size": list(image.size),
            "mean_rgb": [round(v, 4) for v in rgb.mean],
            "stddev_rgb": [round(v, 4) for v in rgb.stddev],
            "mean_saturation_0_255": round(hsv_stat.mean[1], 4),
            "mean_value_0_255": round(hsv_stat.mean[2], 4),
        }


def diff_metrics(reference: Path, candidate: Path) -> dict:
    with Image.open(reference) as a_open, Image.open(candidate) as b_open:
        a = a_open.convert("RGB")
        b = b_open.convert("RGB")
        if a.size != b.size:
            a = a.resize(b.size, Image.Resampling.LANCZOS)
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
        "requested_width": result.request.width,
        "requested_height": result.request.height,
        "steps": result.request.steps,
        "cfg": result.request.cfg,
        "sampler": result.request.sampler,
        "seed": result.request.seed,
        "image_stats": image_stats(result.output_path),
        "difference_from_original": diff_metrics(original, result.output_path),
    }


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


def submit_graph(adapter: Flux2KleinBaseAdapter, graph: dict, destination: Path, label: str) -> tuple[str, float]:
    print(f"RUNNER60: {label} -> submitting", flush=True)
    started = time.time()
    submission = adapter._request_json(adapter.base_url + "/prompt", {"prompt": graph}, timeout=60)
    prompt_id = submission.get("prompt_id")
    if not prompt_id:
        raise RuntimeError(f"ComfyUI did not return prompt_id for {label}: {submission}")
    generated = adapter._wait_for_output(prompt_id)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(generated, destination)
    elapsed = time.time() - started
    print(f"RUNNER60: {label} complete in {elapsed:.3f}s -> {destination}", flush=True)
    return prompt_id, elapsed


def run_vae_roundtrip(
    adapter: Flux2KleinBaseAdapter,
    source: Path,
    vae_name: str,
    destination: Path,
    job_id: str,
    label: str,
) -> dict:
    relative, source_hash = adapter._prepare_reference(source, job_id, 1)
    graph = {
        "1": {"inputs": {"vae_name": vae_name}, "class_type": "VAELoader"},
        "2": {"inputs": {"image": relative}, "class_type": "LoadImage"},
        "3": {
            "inputs": {
                "image": ["2", 0],
                "upscale_method": "nearest-exact",
                "megapixels": 1.0,
                "resolution_steps": 1,
            },
            "class_type": "ImageScaleToTotalPixels",
        },
        "4": {"inputs": {"pixels": ["3", 0], "vae": ["1", 0]}, "class_type": "VAEEncode"},
        "5": {"inputs": {"samples": ["4", 0], "vae": ["1", 0]}, "class_type": "VAEDecode"},
        "6": {
            "inputs": {"filename_prefix": f"roguelite_asset_studio/{job_id}", "images": ["5", 0]},
            "class_type": "SaveImage",
        },
    }
    prompt_id, elapsed = submit_graph(adapter, graph, destination, label)
    return {
        "prompt_id": prompt_id,
        "elapsed_seconds": round(elapsed, 3),
        "vae_name": vae_name,
        "source_sha256": source_hash,
        "output": str(destination),
        "output_sha256": sha256_file(destination),
        "image_stats": image_stats(destination),
        "difference_from_original": diff_metrics(source, destination),
    }


def run_request(adapter, request, output: Path, label: str):
    print(f"RUNNER60: {label} -> submitting", flush=True)
    result = adapter.generate(request, output)
    print(f"RUNNER60: {label} complete in {result.elapsed_seconds:.3f}s -> {output}", flush=True)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comfy-root", required=True, type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--port", type=int, default=8192)
    parser.add_argument("--timeout-minutes", type=int, default=240)
    parser.add_argument("--comfy-commit", required=True)
    args = parser.parse_args()

    print(f"RUNNER60-PYTHON: Asset Studio module root={MODULE_ROOT}", flush=True)
    workspace = args.workspace.resolve()
    output_dir = workspace / "base_official_parity"
    output_dir.mkdir(parents=True, exist_ok=True)

    original = workspace / "spike" / "flux2_klein_4b_t2i_probe.png"
    material = workspace / "edit_strength_calibration" / "material_decay_reference.png"
    if not original.is_file():
        raise FileNotFoundError(f"Runner56 original is required: {original}")
    if not material.is_file():
        raise FileNotFoundError(f"Runner58 material reference is required: {material}")

    comfy_root = args.comfy_root.resolve()
    base_vae_path = comfy_root / "models" / "vae" / BASE_VAE
    full_vae_path = comfy_root / "models" / "vae" / FULL_VAE
    if sha256_file(base_vae_path) != BASE_VAE_SHA256:
        raise RuntimeError(f"Base VAE SHA mismatch: {base_vae_path}")
    if sha256_file(full_vae_path) != FULL_VAE_SHA256:
        raise RuntimeError(f"Full FLUX.2 VAE SHA mismatch: {full_vae_path}")

    adapter = Flux2KleinBaseAdapter(
        comfy_root,
        f"http://127.0.0.1:{args.port}",
        timeout_minutes=args.timeout_minutes,
    )
    adapter.verify_runtime()

    started_all = time.time()

    base_roundtrip_path = output_dir / "base_small_decoder_roundtrip.png"
    base_roundtrip = run_vae_roundtrip(
        adapter,
        original,
        BASE_VAE,
        base_roundtrip_path,
        "runner60_base_small_decoder_roundtrip",
        "Base small-decoder VAE round-trip",
    )

    full_roundtrip_path = output_dir / "full_flux2_vae_roundtrip.png"
    full_roundtrip = run_vae_roundtrip(
        adapter,
        original,
        FULL_VAE,
        full_roundtrip_path,
        "runner60_full_vae_roundtrip",
        "Full FLUX.2 VAE round-trip control",
    )

    t2i_path = output_dir / "base_official_t2i_steps20.png"
    t2i_request = StaticGenerationRequest(
        job_id="runner60_base_official_t2i_steps20",
        asset_type="architecture_module",
        output_contract="static_master",
        prompt=T2I_PROMPT,
        negative="",
        references=(),
        width=WIDTH,
        height=HEIGHT,
        steps=STEPS,
        cfg=CFG,
        sampler=SAMPLER,
        seed=6001,
    )
    t2i_result = run_request(adapter, t2i_request, t2i_path, "Base official-parity T2I 20 steps")

    single_path = output_dir / "base_official_single_steps20.png"
    single_request = StaticGenerationRequest(
        job_id="runner60_base_official_single_steps20",
        asset_type="architecture_module",
        output_contract="static_master",
        prompt=SINGLE_PROMPT,
        negative="",
        references=(ReferenceInput("previous_approved_state", original),),
        width=WIDTH,
        height=HEIGHT,
        steps=STEPS,
        cfg=CFG,
        sampler=SAMPLER,
        seed=SEED,
    )
    single_result = run_request(adapter, single_request, single_path, "Base official-parity single edit 20 steps")

    multi_path = output_dir / "base_official_multi_steps20.png"
    multi_request = StaticGenerationRequest(
        job_id="runner60_base_official_multi_steps20",
        asset_type="architecture_module",
        output_contract="static_master",
        prompt=MULTI_PROMPT,
        negative="",
        references=(
            ReferenceInput("structure", original),
            ReferenceInput("material", material),
        ),
        width=WIDTH,
        height=HEIGHT,
        steps=STEPS,
        cfg=CFG,
        sampler=SAMPLER,
        seed=SEED,
    )
    multi_result = run_request(adapter, multi_request, multi_path, "Base official-parity multi edit 20 steps")

    contact_sheet = output_dir / "runner60_official_parity_contact_sheet.png"
    make_contact_sheet(
        [
            ("ORIGINAL", original),
            ("BASE VAE ROUNDTRIP", base_roundtrip_path),
            ("FULL VAE CONTROL", full_roundtrip_path),
            ("BASE T2I 20", t2i_path),
            ("MATERIAL REF", material),
            ("BASE SINGLE 20", single_path),
            ("BASE MULTI 20", multi_path),
        ],
        contact_sheet,
    )

    manifest = {
        "gate": "ASSET_STUDIO_FLUX2_KLEIN_BASE_OFFICIAL_PARITY",
        "technical_status": "OFFICIAL_PARITY_DIAGNOSTIC_COMPLETE",
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "comfy_commit": args.comfy_commit,
        "source_original": str(original),
        "source_original_sha256": sha256_file(original),
        "source_material_reference": str(material),
        "source_material_reference_sha256": sha256_file(material),
        "runner59_classification": "TECHNICAL_PASS_RECIPE_PARITY_INVALID_FOR_MODEL_VERDICT",
        "parity_fixes": [
            "Base negative conditioning is a separate CLIPTextEncode of an empty string; it is no longer ConditioningZeroOut(positive).",
            "References are scaled with ImageScaleToTotalPixels nearest-exact to 1 MP before VAEEncode.",
            "Reference-edit scheduler and EmptyFlux2LatentImage dimensions derive from the first scaled reference, matching the official graph.",
            "Official Base sampling recipe is Euler / CFG 5 / 20 steps.",
        ],
        "controlled_settings": {
            "reference_target_megapixels": 1.0,
            "reference_upscale_method": "nearest-exact",
            "expected_square_edit_size": [WIDTH, HEIGHT],
            "steps": STEPS,
            "cfg": CFG,
            "sampler": SAMPLER,
            "edit_seed": SEED,
        },
        "base_small_decoder_roundtrip": base_roundtrip,
        "full_flux2_vae_roundtrip_control": full_roundtrip,
        "base_t2i": result_record(t2i_result, original),
        "base_single_reference": result_record(single_result, original),
        "base_multi_reference": result_record(multi_result, original),
        "contact_sheet": str(contact_sheet),
        "contact_sheet_sha256": sha256_file(contact_sheet),
        "elapsed_total_seconds": round(time.time() - started_all, 3),
        "decision_contract": {
            "vae_roundtrip": "If the Base small-decoder round-trip itself shows the cyan/posterized Runner59 failure while the full-VAE control does not, classify the issue as Base VAE/decode path before judging the diffusion model.",
            "t2i": "If both VAE round-trips are sane but Base T2I is cyan/posterized, classify the issue in Base sampling/checkpoint integration rather than reference editing.",
            "single": "If Base T2I is sane, single edit must preserve natural color/identity and execute the explicit structural facts strongly enough for interactive art direction.",
            "multi": "Multi edit must preserve Image 1 structure/camera, visibly import Image 2 material authority, remain naturally colored, and execute the explicit structural facts.",
            "next_branch": "Only after this parity gate yields a valid visual model verdict may the project either accept Base editing or move to a different specialized editor such as Qwen-Image-Edit.",
        },
    }
    manifest_path = output_dir / "runner60_official_parity_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print("RUNNER60-FLUX2-KLEIN-BASE-PARITY: PASS - DIAGNOSTIC MATRIX COMPLETE / VISUAL VERDICT PENDING", flush=True)
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
        print(f"RUNNER60-PYTHON-FAIL: {type(exc).__name__}: {exc}", file=sys.stdout, flush=True)
        traceback.print_exc(file=sys.stdout)
        raise SystemExit(1)
