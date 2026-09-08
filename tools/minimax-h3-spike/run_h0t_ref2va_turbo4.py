#!/usr/bin/env python3
import argparse
import importlib.util
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone

TURBO_LORA = "minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors"
AUDIO_VAE = "minimax_h3_audio_vae_fp32.safetensors"
STEPS = 4
SCHEDULER = "simple"
SAMPLER = "res_multistep"
OUTPUT_PREFIX = "video/roguelite_h3/h0t_exilada_ref2va_448x800_124f_turbo4"
CANONICAL_OUTPUT = "h0t_exilada_ref2va_448x800_124f_turbo4.mp4"
PROMPT_FILE = "h0t_api_prompt.json"
MANIFEST_FILE = "h0t_run_manifest.json"


def fail(message, classification="INTEGRATION_FAIL", code=2):
    print(f"H3-H0T: FAIL [{classification}] - {message}", file=sys.stderr, flush=True)
    raise SystemExit(code)


def load_base():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_h0_ref2va.py")
    if not os.path.isfile(path):
        fail(f"base H0 executor missing: {path}", "PRECONDITION_FAIL")
    spec = importlib.util.spec_from_file_location("roguelite_h3_h0_base", path)
    if spec is None or spec.loader is None:
        fail(f"could not import base H0 executor: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_prompt(base):
    prompt = base.build_prompt()

    # Ref2VA in pinned ComfyUI v0.34.0 requires audio_vae even when no audio reference is used.
    prompt["8"] = {
        "inputs": {"vae_name": AUDIO_VAE},
        "class_type": "VAELoader",
        "_meta": {"title": "H3 required audio VAE"},
    }
    prompt["7"].setdefault("inputs", {})["audio_vae"] = ["8", 0]

    # Official Ref2V Lightning/Turbo path: LoRA strength 1 + 4 steps.
    prompt["9"] = {
        "inputs": {
            "model": ["1", 0],
            "lora_name": TURBO_LORA,
            "strength_model": 1.0,
        },
        "class_type": "LoraLoaderModelOnly",
        "_meta": {"title": "MiniMax H3 Ref2V Turbo4 LoRA"},
    }

    prompt["12"]["inputs"]["model"] = ["9", 0]
    prompt["12"]["inputs"]["steps"] = STEPS
    prompt["12"]["inputs"]["scheduler"] = SCHEDULER
    prompt["12"]["_meta"] = {"title": "H3 Turbo4 scheduler"}
    prompt["13"]["inputs"]["model"] = ["9", 0]
    prompt["13"]["_meta"] = {"title": "H3 Turbo4 Basic Guider"}
    prompt["22"]["inputs"]["filename_prefix"] = OUTPUT_PREFIX
    prompt["22"]["_meta"] = {"title": "Save H0T Turbo4 proof"}
    return prompt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--comfy-root", required=True)
    ap.add_argument("--port", type=int, default=8190)
    ap.add_argument("--timeout-minutes", type=int, default=180)
    args = ap.parse_args()

    base_mod = load_base()
    workspace = os.path.abspath(args.workspace)
    comfy_root = os.path.abspath(args.comfy_root)
    api = f"http://127.0.0.1:{args.port}"

    h0_manifest_path = os.path.join(workspace, "h0_run_manifest.json")
    bootstrap_path = os.path.join(workspace, "h3_bootstrap_manifest.json")
    driver_manifest_path = os.path.join(workspace, "h0_driver_manifest.json")
    for path in (h0_manifest_path, bootstrap_path, driver_manifest_path):
        if not os.path.isfile(path):
            fail(f"required prior evidence missing: {path}", "PRECONDITION_FAIL")

    with open(h0_manifest_path, "r", encoding="utf-8-sig") as fh:
        h0_manifest = json.load(fh)
    if h0_manifest.get("status") != "INFERENCE_COMPLETE":
        fail("H0 Base50 must be complete before H0T throughput comparison", "PRECONDITION_FAIL")

    with open(driver_manifest_path, "r", encoding="utf-8-sig") as fh:
        driver_manifest = json.load(fh)
    if driver_manifest.get("output_frames") != base_mod.FRAME_COUNT or driver_manifest.get("output_fps") != base_mod.FPS:
        fail("H0 driver no longer matches 124f/24fps baseline", "PRECONDITION_FAIL")
    if driver_manifest.get("crop") != "NONE" or driver_manifest.get("resize") != "NONE":
        fail("H0 driver was spatially altered; refusing comparison", "PRECONDITION_FAIL")

    reference_abs = os.path.join(comfy_root, "input", *base_mod.REFERENCE_INPUT.split("/"))
    driver_abs = os.path.join(comfy_root, "input", *base_mod.DRIVER_INPUT.split("/"))
    required_files = [
        reference_abs,
        driver_abs,
        os.path.join(comfy_root, "models", "diffusion_models", base_mod.DIFFUSION_MODEL),
        os.path.join(comfy_root, "models", "text_encoders", base_mod.TEXT_ENCODER),
        os.path.join(comfy_root, "models", "vae", base_mod.VIDEO_VAE),
        os.path.join(comfy_root, "models", "vae", AUDIO_VAE),
        os.path.join(comfy_root, "models", "loras", TURBO_LORA),
    ]
    for path in required_files:
        if not os.path.isfile(path):
            fail(f"required H0T input/model missing: {path}", "PRECONDITION_FAIL")

    required_nodes = list(base_mod.REQUIRED_NODES) + ["LoraLoaderModelOnly"]
    for node_name in required_nodes:
        info = base_mod.request_json(api + f"/object_info/{node_name}", timeout=60)
        if node_name not in info:
            fail(f"required node unavailable from live ComfyUI: {node_name}")

    prompt = build_prompt(base_mod)
    prompt_path = os.path.join(workspace, PROMPT_FILE)
    with open(prompt_path, "w", encoding="utf-8") as fh:
        json.dump(prompt, fh, ensure_ascii=False, indent=2)

    print(
        "H3-H0T: submitting official Ref2V Turbo4 throughput gate: same H0 Picture1/Video1, "
        f"{base_mod.WIDTH}x{base_mod.HEIGHT}, {base_mod.FRAME_COUNT}f@{base_mod.FPS}, "
        f"ref_image_size={base_mod.REF_IMAGE_SIZE}, LoRA strength=1.0, {STEPS} steps, "
        f"{SAMPLER}/{SCHEDULER}, seed={base_mod.SEED}.",
        flush=True,
    )
    print("H3-H0T: this is a throughput/quality comparison; final pixel-art rendering is a later stage.", flush=True)

    started = time.time()
    try:
        response = base_mod.request_json(api + "/prompt", {"prompt": prompt}, timeout=180)
    except Exception as exc:
        fail(f"prompt submission failed before inference: {exc}")
    prompt_id = response.get("prompt_id")
    if not prompt_id:
        fail(f"ComfyUI did not return prompt_id: {response}")
    print(f"H3-H0T: prompt_id={prompt_id}", flush=True)

    deadline = started + args.timeout_minutes * 60
    next_report = started + 30
    history_item = None
    while time.time() < deadline:
        try:
            history = base_mod.request_json(api + f"/history/{prompt_id}", timeout=120)
        except Exception as exc:
            fail(f"lost ComfyUI API while prompt was active: {exc}", "INFRASTRUCTURE_FAIL")
        item = history.get(prompt_id) if isinstance(history, dict) else None
        if item:
            history_item = item
            status = item.get("status") or {}
            for message in status.get("messages") or []:
                if isinstance(message, (list, tuple)) and message and message[0] == "execution_error":
                    fail(
                        f"ComfyUI execution_error after prompt submission: {message}",
                        "EXECUTION_FAIL_REQUIRES_LOG_CLASSIFICATION",
                    )
            if status.get("completed") is True:
                break
        now = time.time()
        if now >= next_report:
            print(f"H3-H0T: inference running for {int(now - started)} seconds...", flush=True)
            next_report = now + 30
        time.sleep(5)
    else:
        fail(f"timeout after {args.timeout_minutes} minutes", "INFRASTRUCTURE_FAIL")

    elapsed = round(time.time() - started, 2)
    output_path = base_mod.newest_output(comfy_root, OUTPUT_PREFIX, started)
    if not output_path:
        fail(f"prompt completed but no output matching {OUTPUT_PREFIX} was found", "OUTPUT_INTEGRATION_FAIL")

    canonical_output = os.path.join(workspace, CANONICAL_OUTPUT)
    shutil.copy2(output_path, canonical_output)

    baseline_elapsed = float(h0_manifest.get("elapsed_seconds") or 0.0)
    speedup = round(baseline_elapsed / elapsed, 3) if baseline_elapsed > 0 and elapsed > 0 else None

    manifest = {
        "gate": "MINIMAX_H3_REF2VA_H0T_TURBO4_448X800",
        "status": "INFERENCE_COMPLETE",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "task": "ref2va",
        "experiment_policy": "THROUGHPUT_QUALITY_GATE",
        "parent_gate": h0_manifest.get("gate"),
        "parent_prompt_id": h0_manifest.get("prompt_id"),
        "width": base_mod.WIDTH,
        "height": base_mod.HEIGHT,
        "frame_count": base_mod.FRAME_COUNT,
        "fps": base_mod.FPS,
        "duration_seconds": base_mod.FRAME_COUNT / base_mod.FPS,
        "reference_image_size": base_mod.REF_IMAGE_SIZE,
        "steps": STEPS,
        "sampler": SAMPLER,
        "scheduler": SCHEDULER,
        "seed": base_mod.SEED,
        "diffusion_model": base_mod.DIFFUSION_MODEL,
        "text_encoder": base_mod.TEXT_ENCODER,
        "video_vae": base_mod.VIDEO_VAE,
        "audio_vae": AUDIO_VAE,
        "turbo_lora": TURBO_LORA,
        "turbo_lora_strength": 1.0,
        "reference_image": base_mod.REFERENCE_INPUT,
        "reference_image_sha256": base_mod.sha256_file(reference_abs),
        "driver": base_mod.DRIVER_INPUT,
        "driver_sha256": base_mod.sha256_file(driver_abs),
        "prompt_text": base_mod.PROMPT,
        "prompt_file": prompt_path,
        "prompt_id": prompt_id,
        "elapsed_seconds": elapsed,
        "base50_elapsed_seconds": baseline_elapsed,
        "wall_clock_speedup_vs_h0": speedup,
        "comfy_output": output_path,
        "canonical_output": canonical_output,
        "output_bytes": os.path.getsize(canonical_output),
        "output_sha256": base_mod.sha256_file(canonical_output),
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "pass_criteria": [
            "material wall-clock reduction versus H0 Base50",
            "body topology remains H0-level stable",
            "motion transfer remains faithful",
            "identity/hair/costume remain coherent",
            "secondary hair/cloth/restraint motion remains readable",
            "no destructive global smear or ghost body",
        ],
        "history_status": (history_item or {}).get("status"),
    }
    manifest_path = os.path.join(workspace, MANIFEST_FILE)
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print(f"H3-H0T: PASS - inference completed: {canonical_output}", flush=True)
    print(f"H3-H0T: manifest {manifest_path}", flush=True)
    print(f"H3-H0T: elapsed {elapsed} seconds", flush=True)
    if speedup is not None:
        print(f"H3-H0T: wall-clock speedup vs H0 Base50 = {speedup}x", flush=True)
    print("H3-H0T: QUALITY VERDICT PENDING; compare directly against H0 before using Turbo for H1-S.", flush=True)


if __name__ == "__main__":
    main()
