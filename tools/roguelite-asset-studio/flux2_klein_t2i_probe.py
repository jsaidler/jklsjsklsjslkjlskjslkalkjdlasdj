#!/usr/bin/env python3
"""Controlled FLUX.2 Klein 4B distilled text-to-image feasibility probe.

This is an Asset Studio backend probe, not an Exilada-specific tool. It submits a
native ComfyUI graph for one reference-free architecture-module source image and
records enough provenance to decide whether this model can become the first generic
static generation adapter on the target workstation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image

MODEL = "flux-2-klein-4b-fp8.safetensors"
MODEL_SHA256 = "97ed34fe0567e436200f2faee3939b88f2b5d99f8af2a4dc16532c4245c0ccb6"
TEXT_ENCODER = "qwen_3_4b.safetensors"
TEXT_ENCODER_SHA256 = "6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a"
VAE = "flux2-vae.safetensors"
VAE_SHA256 = "868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3"

WIDTH = 768
HEIGHT = 768
STEPS = 4
CFG = 1.0
SEED = 0
SAMPLER = "euler"

PROMPT = """A production source asset for a dark sword-and-sorcery belt-scroller game: one modular ruined stone gate, shown as a complete isolated architectural module in a readable front-three-quarter view. Ancient heavy masonry, cracked blocks, eroded carved details, battered dark iron fittings, broken lintel edges, accumulated dirt and age, a few restrained roots and debris integrated into the structure. Strong unmistakable silhouette and physical construction, believable load-bearing stone, tactile materials, severe dangerous late-1970s/1980s pulp fantasy atmosphere. The design should feel specific and authored rather than generic MMO fantasy, but must not copy any existing artwork or franchise design. No people, no creatures, no lettering, no signs, no UI, no frame, no weapon display, no scenic landscape composition. Keep the entire gate visible with generous margin on a simple neutral studio-like background so it can later be isolated, revised, damaged, tiled into a level, or reconstructed into the final game rendering language. High-quality illustrated game-asset master, not a tiny sprite and not a full gameplay screenshot."""
NEGATIVE = "people, character, creature, text, logo, border, UI, cropped object, full landscape, clean polished MMO architecture"

REQUIRED_NODES = [
    "UNETLoader",
    "CLIPLoader",
    "VAELoader",
    "CLIPTextEncode",
    "CFGGuider",
    "RandomNoise",
    "KSamplerSelect",
    "Flux2Scheduler",
    "EmptyFlux2LatentImage",
    "SamplerCustomAdvanced",
    "VAEDecode",
    "SaveImage",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def request_json(url: str, payload: dict[str, Any] | None = None, timeout: int = 60) -> Any:
    data = None
    method = "GET"
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        method = "POST"
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {body[:8000]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach {url}: {exc}") from exc


def verify_file(path: Path, expected_sha: str, label: str) -> str:
    if not path.is_file():
        raise RuntimeError(f"required {label} missing: {path}")
    actual = sha256_file(path)
    if actual.lower() != expected_sha.lower():
        raise RuntimeError(f"{label} SHA256 mismatch: expected {expected_sha}, got {actual}")
    return actual


def verify_nodes(base: str) -> None:
    for node_name in REQUIRED_NODES:
        info = request_json(base + f"/object_info/{node_name}", timeout=30)
        if node_name not in info:
            raise RuntimeError(f"required native ComfyUI node unavailable: {node_name}")


def build_prompt(output_prefix: str) -> dict[str, Any]:
    return {
        "1": {
            "inputs": {"unet_name": MODEL, "weight_dtype": "default"},
            "class_type": "UNETLoader",
        },
        "2": {
            "inputs": {"clip_name": TEXT_ENCODER, "type": "flux2", "device": "default"},
            "class_type": "CLIPLoader",
        },
        "3": {"inputs": {"vae_name": VAE}, "class_type": "VAELoader"},
        "4": {"inputs": {"text": PROMPT, "clip": ["2", 0]}, "class_type": "CLIPTextEncode"},
        "5": {"inputs": {"text": NEGATIVE, "clip": ["2", 0]}, "class_type": "CLIPTextEncode"},
        "6": {
            "inputs": {
                "model": ["1", 0],
                "positive": ["4", 0],
                "negative": ["5", 0],
                "cfg": CFG,
            },
            "class_type": "CFGGuider",
        },
        "7": {"inputs": {"noise_seed": SEED}, "class_type": "RandomNoise"},
        "8": {"inputs": {"sampler_name": SAMPLER}, "class_type": "KSamplerSelect"},
        "9": {
            "inputs": {"steps": STEPS, "width": WIDTH, "height": HEIGHT},
            "class_type": "Flux2Scheduler",
        },
        "10": {
            "inputs": {"width": WIDTH, "height": HEIGHT, "batch_size": 1},
            "class_type": "EmptyFlux2LatentImage",
        },
        "11": {
            "inputs": {
                "noise": ["7", 0],
                "guider": ["6", 0],
                "sampler": ["8", 0],
                "sigmas": ["9", 0],
                "latent_image": ["10", 0],
            },
            "class_type": "SamplerCustomAdvanced",
        },
        "12": {"inputs": {"samples": ["11", 0], "vae": ["3", 0]}, "class_type": "VAEDecode"},
        "13": {
            "inputs": {"filename_prefix": output_prefix, "images": ["12", 0]},
            "class_type": "SaveImage",
        },
    }


def wait_for_output(base: str, prompt_id: str, comfy_root: Path, timeout_minutes: int) -> tuple[Path, dict[str, Any]]:
    deadline = time.time() + timeout_minutes * 60
    last_status: dict[str, Any] = {}
    while time.time() < deadline:
        history = request_json(base + f"/history/{prompt_id}", timeout=30)
        item = history.get(prompt_id)
        if item:
            last_status = item.get("status") or {}
            outputs = item.get("outputs") or {}
            for node_output in outputs.values():
                for image in node_output.get("images") or []:
                    filename = image.get("filename")
                    if not filename:
                        continue
                    image_type = image.get("type", "output")
                    subfolder = image.get("subfolder") or ""
                    root = comfy_root / ("output" if image_type == "output" else image_type)
                    candidate = root / subfolder / filename
                    if candidate.is_file():
                        return candidate, last_status
            serialized = json.dumps(last_status, ensure_ascii=False).lower()
            if "error" in serialized:
                raise RuntimeError(f"ComfyUI reported an execution error: {last_status}")
        time.sleep(2)
    raise TimeoutError(f"timed out after {timeout_minutes} minutes waiting for prompt {prompt_id}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--comfy-root", required=True, type=Path)
    ap.add_argument("--workspace", required=True, type=Path)
    ap.add_argument("--port", type=int, default=8192)
    ap.add_argument("--timeout-minutes", type=int, default=180)
    ap.add_argument("--comfy-commit", required=True)
    args = ap.parse_args()

    comfy_root = args.comfy_root.resolve()
    spike_dir = args.workspace.resolve() / "spike"
    spike_dir.mkdir(parents=True, exist_ok=True)
    base = f"http://127.0.0.1:{args.port}"

    model_hashes = {
        "diffusion": verify_file(comfy_root / "models" / "diffusion_models" / MODEL, MODEL_SHA256, MODEL),
        "text_encoder": verify_file(comfy_root / "models" / "text_encoders" / TEXT_ENCODER, TEXT_ENCODER_SHA256, TEXT_ENCODER),
        "vae": verify_file(comfy_root / "models" / "vae" / VAE, VAE_SHA256, VAE),
    }
    verify_nodes(base)

    output_prefix = "roguelite_asset_studio/flux2_klein_4b_t2i_probe"
    prompt = build_prompt(output_prefix)
    prompt_path = spike_dir / "flux2_klein_4b_t2i_prompt.json"
    prompt_path.write_text(json.dumps(prompt, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        f"FLUX2-KLEIN-PROBE: submitting generic architecture_module T2I at {WIDTH}x{HEIGHT}, "
        f"{STEPS} steps, cfg={CFG}, seed={SEED}",
        flush=True,
    )
    started = time.time()
    submission = request_json(base + "/prompt", {"prompt": prompt}, timeout=60)
    prompt_id = submission.get("prompt_id")
    if not prompt_id:
        raise RuntimeError(f"ComfyUI did not return prompt_id: {submission}")

    generated, history_status = wait_for_output(base, prompt_id, comfy_root, args.timeout_minutes)
    elapsed = time.time() - started
    final_path = spike_dir / "flux2_klein_4b_t2i_probe.png"
    shutil.copy2(generated, final_path)

    with Image.open(final_path) as image:
        image.load()
        result_size = list(image.size)
        image_mode = image.mode
    if result_size != [WIDTH, HEIGHT]:
        raise RuntimeError(f"generated image size {result_size} differs from requested {[WIDTH, HEIGHT]}")

    manifest = {
        "gate": "ASSET_STUDIO_FLUX2_KLEIN_4B_DISTILLED_T2I_FEASIBILITY",
        "technical_status": "INFERENCE_COMPLETE",
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "asset_type": "architecture_module",
        "output_contract": "static_master",
        "purpose": "Prove one generic reference-free static generation route before integrating FLUX.2 Klein as an Asset Studio adapter.",
        "comfy_commit": args.comfy_commit,
        "model": MODEL,
        "model_sha256": model_hashes["diffusion"],
        "text_encoder": TEXT_ENCODER,
        "text_encoder_sha256": model_hashes["text_encoder"],
        "vae": VAE,
        "vae_sha256": model_hashes["vae"],
        "width": WIDTH,
        "height": HEIGHT,
        "steps": STEPS,
        "cfg": CFG,
        "sampler": SAMPLER,
        "seed": SEED,
        "prompt": PROMPT,
        "negative": NEGATIVE,
        "prompt_id": prompt_id,
        "elapsed_seconds": round(elapsed, 3),
        "history_status": history_status,
        "output": str(final_path),
        "output_sha256": sha256_file(final_path),
        "output_size": result_size,
        "output_mode": image_mode,
        "pass_contract": {
            "technical": "ComfyUI loads all three verified files and produces one valid 768x768 image without OOM/crash.",
            "visual": "Human review must confirm coherent architecture, useful authored detail and enough quality to continue to generic editing tests. This probe does not yet prove final game pixel-art rendering language.",
        },
    }
    manifest_path = spike_dir / "flux2_klein_4b_t2i_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print("FLUX2-KLEIN-PROBE: PASS - TECHNICAL INFERENCE COMPLETE / VISUAL VERDICT PENDING", flush=True)
    print(f"FLUX2-KLEIN-PROBE: output {final_path}", flush=True)
    print(f"FLUX2-KLEIN-PROBE: manifest {manifest_path}", flush=True)
    print(f"FLUX2-KLEIN-PROBE: elapsed_seconds={elapsed:.3f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
