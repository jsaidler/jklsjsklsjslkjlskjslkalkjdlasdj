#!/usr/bin/env python3
import importlib.util
import json
import os
import sys

AUDIO_VAE = "minimax_h3_audio_vae_fp32.safetensors"


def fail(message: str, code: int = 2) -> None:
    print(f"H3-H0R: FAIL [INTEGRATION_FAIL] - {message}", file=sys.stderr, flush=True)
    raise SystemExit(code)


def load_base_module():
    base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_h0_ref2va.py")
    if not os.path.isfile(base_path):
        fail(f"base H0 executor missing: {base_path}")
    spec = importlib.util.spec_from_file_location("roguelite_h3_h0_base", base_path)
    if spec is None or spec.loader is None:
        fail(f"could not import base H0 executor: {base_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def arg_value(name: str):
    try:
        idx = sys.argv.index(name)
    except ValueError:
        return None
    if idx + 1 >= len(sys.argv):
        return None
    return sys.argv[idx + 1]


def main() -> None:
    base = load_base_module()
    comfy_root = arg_value("--comfy-root")
    workspace = arg_value("--workspace")
    if not comfy_root or not workspace:
        fail("--comfy-root and --workspace are required")

    audio_path = os.path.join(os.path.abspath(comfy_root), "models", "vae", AUDIO_VAE)
    if not os.path.isfile(audio_path):
        fail(f"required Ref2VA audio VAE missing: {audio_path}")

    original_build_prompt = base.build_prompt

    def build_prompt_fixed():
        prompt = original_build_prompt()
        if "7" not in prompt or prompt["7"].get("class_type") != "MiniMaxH3ReferenceToVideo":
            fail("base H0 prompt no longer has expected MiniMaxH3ReferenceToVideo node 7")
        prompt["8"] = {
            "inputs": {"vae_name": AUDIO_VAE},
            "class_type": "VAELoader",
            "_meta": {"title": "H3 required audio VAE for Ref2VA conditioning"},
        }
        prompt["7"].setdefault("inputs", {})["audio_vae"] = ["8", 0]
        return prompt

    base.build_prompt = build_prompt_fixed

    print(
        "H3-H0R: integration fix active: MiniMaxH3ReferenceToVideo in pinned ComfyUI v0.34.0 requires audio_vae even when H0 supplies no audio reference and does not decode audio.",
        flush=True,
    )
    print(f"H3-H0R: using required schema-only audio VAE input: {AUDIO_VAE}", flush=True)

    base.main()

    manifest_path = os.path.join(os.path.abspath(workspace), "h0_run_manifest.json")
    if os.path.isfile(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8-sig") as fh:
                manifest = json.load(fh)
            manifest["integration_fix"] = {
                "incident": "Runner47 initial prompt validation failed before inference because MiniMaxH3ReferenceToVideo.audio_vae is required in ComfyUI v0.34.0",
                "classification": "INTEGRATION_FAIL",
                "audio_vae": AUDIO_VAE,
                "audio_reference_used": False,
                "audio_decoded": False,
                "quality_settings_changed": False,
                "note": "The audio VAE is wired only because the Ref2VA node schema requires it; H0 remains a video-only quality experiment with identical Picture1, Video1, canvas, frames, steps, sampler, scheduler and seed.",
            }
            with open(manifest_path, "w", encoding="utf-8") as fh:
                json.dump(manifest, fh, ensure_ascii=False, indent=2)
        except Exception as exc:
            print(f"H3-H0R: WARNING - inference completed but manifest augmentation failed: {exc}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
