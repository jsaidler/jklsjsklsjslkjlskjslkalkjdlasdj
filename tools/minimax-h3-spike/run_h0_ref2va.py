#!/usr/bin/env python3
import argparse
import glob
import hashlib
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from fractions import Fraction

WIDTH = 448
HEIGHT = 800
FRAME_COUNT = 124
FPS = 24
STEPS = 50
SEED = 0
SAMPLER = "res_multistep"
SCHEDULER = "beta"
REF_IMAGE_SIZE = "match"

DIFFUSION_MODEL = "minimax_h3_ref2va_pruned_int8_convrot.safetensors"
TEXT_ENCODER = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
VIDEO_VAE = "minimax_h3_video_vae_fp16.safetensors"

REFERENCE_INPUT = "roguelite_h3/exilada_master.png"
DRIVER_INPUT = "roguelite_h3/h0_driver_24fps_124f.mp4"
OUTPUT_PREFIX = "video/roguelite_h3/h0_exilada_ref2va_448x800_124f_base50"

PROMPT = """<Picture 1> is the ONLY appearance, identity, anatomy, clothing, hair and art-style reference for the target character. Preserve the same adult woman: her mature severe face, olive-brown skin, lean resilient natural feminine proportions, very long heavy messy black hair, degraded captivity clothing, cuffs/shackles and broken-chain details. Preserve the painterly illustrated dark-fantasy look of <Picture 1>. No weapon.

<Video 1> is the ONLY movement and performance reference. Transfer its full-body motion, timing, weight transfer, footwork, limb trajectories, momentum and body inertia. Use that motion to infer physically coherent secondary response in the target woman's long hair, soft tissue, torn cloth and restraints. IGNORE the identity, face, sex, body shape, hair, clothing, colors, environment and visual style of <Video 1>.

Generate one continuous fixed-camera shot of the same complete woman. Keep her full body visible throughout, with stable scale and framing. Preserve one head, one torso, two arms, two hands, two legs and two feet with stable attachment and ordering across every frame. No duplicated, detached, fused, swapped or disappearing limbs; no transient extra body parts; no body-part morphing; no anatomy reconfiguration. Keep face, breast/torso anatomy, hips, hands and feet temporally coherent. Hair and cloth may move dynamically but must remain attached and physically plausible. Cuffs, shackles and chain fragments remain accessories, never transform into limbs or flesh.

Prefer clear temporal structure over cinematic smear. Avoid global motion blur, ghost trails, double exposure, translucent duplicate bodies and destructive frame-to-frame smearing. Localized restrained motion blur on fast extremities or hair is acceptable only when anatomy remains readable. Background should stay visually simple and unobtrusive so the character silhouette remains easy to extract for a 2D game sprite."""

REQUIRED_NODES = [
    "UNETLoader", "CLIPLoader", "VAELoader", "LoadImage", "LoadVideo", "GetVideoComponents",
    "MiniMaxH3ReferenceToVideo", "RandomNoise", "KSamplerSelect", "BasicScheduler", "BasicGuider",
    "SamplerCustomAdvanced", "VAEDecode", "CreateVideo", "SaveVideo",
]


def fail(message, classification="INTEGRATION_FAIL", code=2):
    print(f"H3-H0: FAIL [{classification}] - {message}", file=sys.stderr, flush=True)
    raise SystemExit(code)


def request_json(url, payload=None, timeout=120):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach {url}: {exc}") from exc
    return json.loads(raw.decode("utf-8")) if raw else {}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def newest_output(comfy_root, prefix, since_epoch):
    output_root = os.path.join(comfy_root, "output")
    normalized = prefix.replace("/", os.sep).replace("\\", os.sep)
    patterns = [
        os.path.join(output_root, normalized + "*.mp4"),
        os.path.join(output_root, normalized + "*.mkv"),
        os.path.join(output_root, normalized + "*.webm"),
    ]
    candidates = []
    for pattern in patterns:
        candidates.extend(glob.glob(pattern))
    candidates = [p for p in candidates if os.path.getmtime(p) >= since_epoch - 2]
    return max(candidates, key=os.path.getmtime) if candidates else None


def build_prompt():
    return {
        "1": {
            "inputs": {"unet_name": DIFFUSION_MODEL, "weight_dtype": "default"},
            "class_type": "UNETLoader",
            "_meta": {"title": "H3 Ref2VA diffusion"},
        },
        "2": {
            "inputs": {"clip_name": TEXT_ENCODER, "type": "minimax", "device": "default"},
            "class_type": "CLIPLoader",
            "_meta": {"title": "H3 Qwen3-VL encoder"},
        },
        "3": {
            "inputs": {"vae_name": VIDEO_VAE},
            "class_type": "VAELoader",
            "_meta": {"title": "H3 video VAE"},
        },
        "4": {
            "inputs": {"image": REFERENCE_INPUT},
            "class_type": "LoadImage",
            "_meta": {"title": "Exilada appearance reference"},
        },
        "5": {
            "inputs": {"file": DRIVER_INPUT},
            "class_type": "LoadVideo",
            "_meta": {"title": "H0 24fps raw-motion reference"},
        },
        "6": {
            "inputs": {"video": ["5", 0]},
            "class_type": "GetVideoComponents",
            "_meta": {"title": "Reference video frames"},
        },
        "7": {
            "inputs": {
                "clip": ["2", 0],
                "vae": ["3", 0],
                "prompt": PROMPT,
                "width": WIDTH,
                "height": HEIGHT,
                "length": FRAME_COUNT,
                "ref_image_size": REF_IMAGE_SIZE,
                "ref_images.ref_image_0": ["4", 0],
                "ref_videos.ref_video_0": ["6", 0],
            },
            "class_type": "MiniMaxH3ReferenceToVideo",
            "_meta": {"title": "MiniMax H3 Reference to Video"},
        },
        "10": {
            "inputs": {"noise_seed": SEED},
            "class_type": "RandomNoise",
            "_meta": {"title": "Fixed H0 seed"},
        },
        "11": {
            "inputs": {"sampler_name": SAMPLER},
            "class_type": "KSamplerSelect",
            "_meta": {"title": "H3 sampler"},
        },
        "12": {
            "inputs": {"scheduler": SCHEDULER, "steps": STEPS, "denoise": 1.0, "model": ["1", 0]},
            "class_type": "BasicScheduler",
            "_meta": {"title": "H3 Base 50-step scheduler"},
        },
        "13": {
            "inputs": {"model": ["1", 0], "conditioning": ["7", 0]},
            "class_type": "BasicGuider",
            "_meta": {"title": "H3 Basic Guider"},
        },
        "14": {
            "inputs": {
                "noise": ["10", 0],
                "guider": ["13", 0],
                "sampler": ["11", 0],
                "sigmas": ["12", 0],
                "latent_image": ["7", 1],
            },
            "class_type": "SamplerCustomAdvanced",
            "_meta": {"title": "H3 sampler"},
        },
        "20": {
            "inputs": {"samples": ["14", 0], "vae": ["3", 0]},
            "class_type": "VAEDecode",
            "_meta": {"title": "Decode H3 video stream"},
        },
        "21": {
            "inputs": {"fps": FPS, "bit_depth": 8, "color_space": "sRGB", "images": ["20", 0]},
            "class_type": "CreateVideo",
            "_meta": {"title": "Create H0 video"},
        },
        "22": {
            "inputs": {
                "filename_prefix": OUTPUT_PREFIX,
                "format": "mp4",
                "codec": "h264",
                "codec.encoding": "auto",
                "video": ["21", 0],
            },
            "class_type": "SaveVideo",
            "_meta": {"title": "Save H0 proof"},
        },
    }


def write_gameplay_preview(source_path, preview_path, target_frame_height=160):
    """Make a tiny whole-frame QA preview. It is not segmentation/extraction."""
    try:
        import av
    except Exception as exc:
        return {"status": "SKIPPED", "reason": f"PyAV unavailable: {exc}"}

    src = av.open(source_path)
    video_streams = [s for s in src.streams if s.type == "video"]
    if not video_streams:
        src.close()
        return {"status": "SKIPPED", "reason": "no video stream"}
    stream = video_streams[0]
    src_w = int(stream.codec_context.width)
    src_h = int(stream.codec_context.height)
    target_h = int(target_frame_height)
    target_w = max(2, int(round(src_w * target_h / src_h)))
    if target_w % 2:
        target_w += 1
    if target_h % 2:
        target_h += 1
    os.makedirs(os.path.dirname(preview_path), exist_ok=True)
    if os.path.exists(preview_path):
        os.remove(preview_path)

    dst = av.open(preview_path, mode="w")
    out = dst.add_stream("libx264", rate=FPS)
    out.width = target_w
    out.height = target_h
    out.pix_fmt = "yuv420p"
    out.options = {"crf": "16", "preset": "medium"}
    out.time_base = Fraction(1, FPS)
    count = 0
    try:
        for frame in src.decode(stream):
            scaled = frame.reformat(width=target_w, height=target_h, format="yuv420p")
            scaled.pts = count
            scaled.time_base = Fraction(1, FPS)
            for packet in out.encode(scaled):
                dst.mux(packet)
            count += 1
        for packet in out.encode():
            dst.mux(packet)
    finally:
        src.close()
        dst.close()

    return {
        "status": "GENERATED",
        "path": preview_path,
        "frame_width": target_w,
        "frame_height": target_h,
        "frames": count,
        "sha256": sha256_file(preview_path),
        "interpretation": "Whole-frame gameplay-scale proxy only. If the subject occupies ~80% of source height, a 160px frame makes the character roughly 128px tall. This is not alpha extraction.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--comfy-root", required=True)
    ap.add_argument("--port", type=int, default=8190)
    ap.add_argument("--timeout-minutes", type=int, default=480)
    args = ap.parse_args()

    workspace = os.path.abspath(args.workspace)
    comfy_root = os.path.abspath(args.comfy_root)
    base = f"http://127.0.0.1:{args.port}"

    bootstrap_path = os.path.join(workspace, "h3_bootstrap_manifest.json")
    driver_manifest_path = os.path.join(workspace, "h0_driver_manifest.json")
    for path in (bootstrap_path, driver_manifest_path):
        if not os.path.isfile(path):
            fail(f"Runner46 evidence missing: {path}", "PRECONDITION_FAIL")

    with open(bootstrap_path, "r", encoding="utf-8-sig") as fh:
        bootstrap = json.load(fh)
    if bootstrap.get("status") != "PREPARED":
        fail(f"bootstrap status is {bootstrap.get('status')}, expected PREPARED", "PRECONDITION_FAIL")

    with open(driver_manifest_path, "r", encoding="utf-8-sig") as fh:
        driver_manifest = json.load(fh)
    if driver_manifest.get("output_frames") != FRAME_COUNT or driver_manifest.get("output_fps") != FPS:
        fail("normalized driver does not match H0 124f/24fps contract", "PRECONDITION_FAIL")
    if driver_manifest.get("crop") != "NONE" or driver_manifest.get("resize") != "NONE":
        fail("H0 driver was spatially altered; refusing inference", "PRECONDITION_FAIL")

    reference_abs = os.path.join(comfy_root, "input", *REFERENCE_INPUT.split("/"))
    driver_abs = os.path.join(comfy_root, "input", *DRIVER_INPUT.split("/"))
    model_paths = [
        os.path.join(comfy_root, "models", "diffusion_models", DIFFUSION_MODEL),
        os.path.join(comfy_root, "models", "text_encoders", TEXT_ENCODER),
        os.path.join(comfy_root, "models", "vae", VIDEO_VAE),
    ]
    for path in [reference_abs, driver_abs] + model_paths:
        if not os.path.isfile(path):
            fail(f"required H0 input/model missing: {path}", "PRECONDITION_FAIL")

    # Validate the live pinned node set before queueing a multi-hour inference.
    for node_name in REQUIRED_NODES:
        info = request_json(base + f"/object_info/{node_name}", timeout=60)
        if node_name not in info:
            fail(f"required node unavailable from live ComfyUI: {node_name}", "INTEGRATION_FAIL")

    prompt = build_prompt()
    prompt_path = os.path.join(workspace, "h0_api_prompt.json")
    with open(prompt_path, "w", encoding="utf-8") as fh:
        json.dump(prompt, fh, ensure_ascii=False, indent=2)

    print(
        "H3-H0: submitting Base Ref2VA: Picture1=Exilada appearance only; Video1=motion only; "
        f"{WIDTH}x{HEIGHT}, {FRAME_COUNT}f@{FPS}, ref_image_size={REF_IMAGE_SIZE}, "
        f"{STEPS} steps, {SAMPLER}/{SCHEDULER}, seed={SEED}.",
        flush=True,
    )
    print(
        "H3-H0: no FL2VA weights, no Turbo LoRA, no style embedding, no audio decode. "
        "Model default H3 sigma shifts are video=12/audio=3 in the pinned Comfy build.",
        flush=True,
    )

    started = time.time()
    try:
        response = request_json(base + "/prompt", {"prompt": prompt}, timeout=180)
    except Exception as exc:
        fail(f"prompt submission failed before inference: {exc}", "INTEGRATION_FAIL")
    prompt_id = response.get("prompt_id")
    if not prompt_id:
        fail(f"ComfyUI did not return prompt_id: {response}", "INTEGRATION_FAIL")
    print(f"H3-H0: prompt_id={prompt_id}", flush=True)

    deadline = started + args.timeout_minutes * 60
    next_report = started + 60
    history_item = None
    while time.time() < deadline:
        try:
            history = request_json(base + f"/history/{prompt_id}", timeout=120)
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
            print(f"H3-H0: inference running for {int(now - started)} seconds...", flush=True)
            next_report = now + 60
        time.sleep(5)
    else:
        fail(f"timeout after {args.timeout_minutes} minutes", "INFRASTRUCTURE_FAIL")

    elapsed = round(time.time() - started, 2)
    output_path = newest_output(comfy_root, OUTPUT_PREFIX, started)
    if not output_path:
        fail(
            f"prompt {prompt_id} completed but no new video matching {OUTPUT_PREFIX} was found",
            "OUTPUT_INTEGRATION_FAIL",
        )

    canonical_output = os.path.join(workspace, "h0_exilada_ref2va_448x800_124f_base50.mp4")
    shutil.copy2(output_path, canonical_output)
    preview_path = os.path.join(workspace, "h0_gameplay_scale_proxy_frame160.mp4")
    preview = write_gameplay_preview(canonical_output, preview_path, 160)

    manifest = {
        "gate": "MINIMAX_H3_REF2VA_H0_BASE50_448X800",
        "status": "INFERENCE_COMPLETE",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "task": "ref2va",
        "experiment_policy": "BASELINE_SCREENING",
        "production_contract": "Picture1 appearance + Video1 real motion -> complete character video; no skeleton-only final and no manual rescue",
        "width": WIDTH,
        "height": HEIGHT,
        "frame_count": FRAME_COUNT,
        "fps": FPS,
        "duration_seconds": FRAME_COUNT / FPS,
        "reference_image_size": REF_IMAGE_SIZE,
        "steps": STEPS,
        "sampler": SAMPLER,
        "scheduler": SCHEDULER,
        "seed": SEED,
        "sigma_shift_video": 12,
        "sigma_shift_audio": 3,
        "diffusion_model": DIFFUSION_MODEL,
        "text_encoder": TEXT_ENCODER,
        "video_vae": VIDEO_VAE,
        "turbo_lora": None,
        "audio_vae": None,
        "reference_image": REFERENCE_INPUT,
        "reference_image_sha256": sha256_file(reference_abs),
        "driver": DRIVER_INPUT,
        "driver_sha256": sha256_file(driver_abs),
        "driver_manifest": driver_manifest_path,
        "prompt_text": PROMPT,
        "prompt_file": prompt_path,
        "prompt_id": prompt_id,
        "elapsed_seconds": elapsed,
        "comfy_output": output_path,
        "canonical_output": canonical_output,
        "output_bytes": os.path.getsize(canonical_output),
        "output_sha256": sha256_file(canonical_output),
        "gameplay_scale_proxy": preview,
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "pass_criteria": [
            "complete body and no major generated crop",
            "materially stable temporal body topology",
            "motion/performance follows Video1 while appearance follows Picture1",
            "long hair and cloth show coherent secondary motion",
            "no destructive global smear/ghost body",
            "gameplay-scale silhouette remains readable",
        ],
        "failure_policy": "Infrastructure/integration failures do not count as model failure. If H0 is structurally under-resolved, use the finite 480x864 -> 512x896 -> 768-short-edge diagnostic ladder. If motion is strong but identity alone is weak, test ref_image_size=max before increasing output resolution.",
        "bootstrap_manifest": bootstrap_path,
        "history_status": (history_item or {}).get("status"),
    }
    manifest_path = os.path.join(workspace, "h0_run_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print(f"H3-H0: PASS - inference completed: {canonical_output}", flush=True)
    print(f"H3-H0: manifest {manifest_path}", flush=True)
    if preview.get("status") == "GENERATED":
        print(f"H3-H0: gameplay-scale proxy {preview_path}", flush=True)
    else:
        print(f"H3-H0: gameplay-scale proxy skipped: {preview.get('reason')}", flush=True)
    print(f"H3-H0: elapsed {elapsed} seconds", flush=True)
    print("H3-H0: MODEL VERDICT IS NOT AUTOMATIC; inspect full resolution and gameplay-scale proxy.", flush=True)


if __name__ == "__main__":
    main()
