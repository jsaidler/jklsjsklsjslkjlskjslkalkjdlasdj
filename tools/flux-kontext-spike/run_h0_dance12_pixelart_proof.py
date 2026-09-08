#!/usr/bin/env python3
import argparse
import glob
import hashlib
import json
import math
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

import numpy as np
from PIL import Image

try:
    import av
except Exception as exc:  # pragma: no cover - runtime precondition
    av = None
    AV_IMPORT_ERROR = str(exc)
else:
    AV_IMPORT_ERROR = None

MODEL = "flux1-dev-kontext_fp8_scaled.safetensors"
CLIP_L = "clip_l.safetensors"
T5 = "t5xxl_fp16.safetensors"
VAE = "ae.safetensors"

MODEL_SHA256 = "630ba795ec64283b4230ea23cf79406c2c68b7c578229ed139f30043eadb30a2"
CLIP_L_SHA256 = "660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c0c8576cd796491d9a6cdd"
T5_SHA256 = "6e480b09fae049a72d2a8c5fbccb8d3e92febeb233bbe9dfe7256958a9167635"
VAE_SHA256 = "afc8e28272cd15db3919bacdb6918ce9c1ed22e96cb12c4d5ed0fba823529e38"

H0_VIDEO = "h0_exilada_ref2va_448x800_124f_base50.mp4"
REFERENCE_REL = os.path.join("assets", "source", "characters", "exilada", "reference", "exilada_master.png")

SOURCE_FRAME_COUNT = 124
SOURCE_FPS = 24
SELECTED_ZERO_BASED = [0, 11, 22, 34, 45, 56, 67, 78, 89, 101, 112, 123]
SELECTED_ONE_BASED = [x + 1 for x in SELECTED_ZERO_BASED]

SHEET_SIZE = 1024
GRID_Y = 128
CELL_SIZE = 256
GRID_COLS = 4
GRID_ROWS = 3
WORKING_SUBJECT_HEIGHT = 176
RUNTIME_CELL = 192

STEPS = 20
CFG = 1.0
GUIDANCE = 2.5
SAMPLER = "euler"
SCHEDULER = "simple"
SEED = 0

ACTION_INPUT = "roguelite_kontext/h0_dance12_action_sheet.png"
REFERENCE_INPUT = "roguelite_kontext/exilada_master.png"
OUTPUT_PREFIX = "roguelite_kontext/h0_dance12_kontext_pixelart"

PROMPT = """Edit the square 4-by-3 action spritesheet into deliberate high-end modern pixel art. The 4 columns by 3 rows contain 12 ordered frames of the same adult woman performing one dance/gesture action. Preserve the exact square canvas, exact 4-by-3 panel layout, exact frame order, exact pose in every cell, limb count, body topology, silhouette, relative scale, foot placement, body lean, hand direction, hair mass, torn clothing, cuffs, shackles and chain fragments. Do not change the action or invent new poses.

Use the separate full-character reference image only as the identity and art-direction authority for the same woman: mature severe adult face, olive-brown skin, lean resilient natural feminine proportions, very long heavy messy black hair, degraded captivity clothing and restraint details. Keep the character recognizably the same across all 12 cells.

Render the whole animation set as authored-looking high-quality pixel art suitable for a contemporary 640x360 sword-and-sorcery belt-scroller, with the final character intended to read around 128 pixels tall in gameplay. Use intentional coherent pixel clusters, crisp aliased edges, controlled palette and clear material separation. Preserve the physical, mature 1980s sword-and-sorcery charge. No painterly brush texture, no smooth illustration look, no antialiased blur, no soft miniature painting, no text, no panel borders, no extra objects, no extra limbs and no duplicated body parts. Keep one consistent palette and one consistent sprite-artist language across all 12 frames. Keep the flat neutral background unchanged so it can be removed automatically afterward."""

REQUIRED_NODES = [
    "UNETLoader",
    "DualCLIPLoader",
    "VAELoader",
    "LoadImage",
    "FluxKontextImageScale",
    "VAEEncode",
    "CLIPTextEncode",
    "ConditioningZeroOut",
    "ReferenceLatent",
    "FluxGuidance",
    "KSampler",
    "VAEDecode",
    "SaveImage",
]


def fail(message, classification="INTEGRATION_FAIL", code=2):
    print(f"KONTEXT-H0-DANCE12: FAIL [{classification}] - {message}", file=sys.stderr, flush=True)
    raise SystemExit(code)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def newest_png(comfy_root, prefix, since_epoch):
    output_root = os.path.join(comfy_root, "output")
    normalized = prefix.replace("/", os.sep).replace("\\", os.sep)
    candidates = glob.glob(os.path.join(output_root, normalized + "*.png"))
    candidates = [p for p in candidates if os.path.getmtime(p) >= since_epoch - 2]
    return max(candidates, key=os.path.getmtime) if candidates else None


def decode_video(path):
    if av is None:
        fail(f"PyAV unavailable in pinned ComfyUI Python: {AV_IMPORT_ERROR}", "PRECONDITION_FAIL")
    container = av.open(path)
    streams = [s for s in container.streams if s.type == "video"]
    if not streams:
        container.close()
        fail("H0 source has no video stream", "PRECONDITION_FAIL")
    stream = streams[0]
    frames = []
    try:
        for frame in container.decode(stream):
            frames.append(Image.fromarray(frame.to_ndarray(format="rgb24"), "RGB"))
    finally:
        container.close()
    return frames


def estimate_cutout(frame):
    arr = np.asarray(frame.convert("RGB"), dtype=np.float32)
    h, w, _ = arr.shape
    pad = max(8, min(h, w) // 24)
    corners = np.concatenate(
        [
            arr[:pad, :pad].reshape(-1, 3),
            arr[:pad, -pad:].reshape(-1, 3),
            arr[-pad:, :pad].reshape(-1, 3),
            arr[-pad:, -pad:].reshape(-1, 3),
        ],
        axis=0,
    )
    bg = np.median(corners, axis=0)
    dist = np.sqrt(((arr - bg) ** 2).sum(axis=2))

    alpha = np.clip((dist - 10.0) / 30.0 * 255.0, 0, 255).astype(np.uint8)
    hard = alpha > 32
    row_counts = hard.sum(axis=1)
    col_counts = hard.sum(axis=0)
    ys = np.where(row_counts > 3)[0]
    xs = np.where(col_counts > 3)[0]
    if len(xs) == 0 or len(ys) == 0:
        fail("automatic H0 subject extraction found an empty frame", "MODEL/TASK_FAIL")

    x0 = max(0, int(xs[0]) - 6)
    x1 = min(w, int(xs[-1]) + 7)
    y0 = max(0, int(ys[0]) - 6)
    y1 = min(h, int(ys[-1]) + 7)

    rgba = np.dstack([arr.astype(np.uint8), alpha])
    image = Image.fromarray(rgba, "RGBA")
    bbox = (x0, y0, x1, y1)
    return image.crop(bbox), bbox, bg.tolist()


def make_action_sheet(frames, out_path):
    selected = [frames[i] for i in SELECTED_ZERO_BASED]
    cutouts = []
    bboxes = []
    bg_samples = []
    for frame in selected:
        cutout, bbox, bg = estimate_cutout(frame)
        cutouts.append(cutout)
        bboxes.append(bbox)
        bg_samples.append(bg)

    widths = np.array([b[2] - b[0] for b in bboxes], dtype=np.float32)
    heights = np.array([b[3] - b[1] for b in bboxes], dtype=np.float32)
    centers = np.array([(b[0] + b[2]) / 2.0 for b in bboxes], dtype=np.float32)
    bottoms = np.array([b[3] for b in bboxes], dtype=np.float32)

    median_h = float(np.median(heights))
    max_h = float(np.max(heights))
    max_w = float(np.max(widths))
    scale = min(
        WORKING_SUBJECT_HEIGHT / max(1.0, median_h),
        224.0 / max(1.0, max_h),
        224.0 / max(1.0, max_w),
    )

    median_center = float(np.median(centers))
    median_bottom = float(np.median(bottoms))
    neutral = (96, 96, 96, 255)
    sheet = Image.new("RGBA", (SHEET_SIZE, SHEET_SIZE), neutral)

    cells = []
    for index, (cutout, bbox) in enumerate(zip(cutouts, bboxes)):
        nw = max(1, int(round(cutout.width * scale)))
        nh = max(1, int(round(cutout.height * scale)))
        resized = cutout.resize((nw, nh), Image.Resampling.LANCZOS)

        col = index % GRID_COLS
        row = index // GRID_COLS
        cell_x = col * CELL_SIZE
        cell_y = GRID_Y + row * CELL_SIZE

        center_delta = (((bbox[0] + bbox[2]) / 2.0) - median_center) * scale
        bottom_delta = (bbox[3] - median_bottom) * scale
        target_center_x = cell_x + CELL_SIZE / 2.0 + center_delta
        target_bottom_y = cell_y + CELL_SIZE - 24.0 + bottom_delta
        x = int(round(target_center_x - nw / 2.0))
        y = int(round(target_bottom_y - nh))

        x = max(cell_x + 4, min(x, cell_x + CELL_SIZE - nw - 4))
        y = max(cell_y + 4, min(y, cell_y + CELL_SIZE - nh - 4))
        sheet.alpha_composite(resized, (x, y))

        cells.append(
            {
                "source_frame_zero_based": SELECTED_ZERO_BASED[index],
                "source_frame_one_based": SELECTED_ONE_BASED[index],
                "source_bbox": list(map(int, bbox)),
                "working_cell": [cell_x, cell_y, CELL_SIZE, CELL_SIZE],
                "working_paste": [x, y, nw, nh],
            }
        )

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sheet.convert("RGB").save(out_path, quality=95)
    return {
        "selected_frames_zero_based": SELECTED_ZERO_BASED,
        "selected_frames_one_based": SELECTED_ONE_BASED,
        "sheet_size": [SHEET_SIZE, SHEET_SIZE],
        "grid_region": [0, GRID_Y, GRID_COLS * CELL_SIZE, GRID_ROWS * CELL_SIZE],
        "cell_size": CELL_SIZE,
        "global_scale": scale,
        "background_samples": bg_samples,
        "cells": cells,
    }


def build_prompt():
    return {
        "1": {
            "inputs": {"unet_name": MODEL, "weight_dtype": "default"},
            "class_type": "UNETLoader",
            "_meta": {"title": "Flux Kontext FP8 scaled"},
        },
        "2": {
            "inputs": {
                "clip_name1": CLIP_L,
                "clip_name2": T5,
                "type": "flux",
                "device": "default",
            },
            "class_type": "DualCLIPLoader",
            "_meta": {"title": "Flux dual text encoder"},
        },
        "3": {
            "inputs": {"vae_name": VAE},
            "class_type": "VAELoader",
            "_meta": {"title": "Flux VAE"},
        },
        "4": {
            "inputs": {"image": ACTION_INPUT},
            "class_type": "LoadImage",
            "_meta": {"title": "H0 dance 12-frame action sheet"},
        },
        "5": {
            "inputs": {"image": ["4", 0]},
            "class_type": "FluxKontextImageScale",
            "_meta": {"title": "Kontext action-sheet scale"},
        },
        "6": {
            "inputs": {"pixels": ["5", 0], "vae": ["3", 0]},
            "class_type": "VAEEncode",
            "_meta": {"title": "Encode action sheet"},
        },
        "7": {
            "inputs": {"image": REFERENCE_INPUT},
            "class_type": "LoadImage",
            "_meta": {"title": "Canonical Exilada reference"},
        },
        "8": {
            "inputs": {"image": ["7", 0]},
            "class_type": "FluxKontextImageScale",
            "_meta": {"title": "Kontext reference scale"},
        },
        "9": {
            "inputs": {"pixels": ["8", 0], "vae": ["3", 0]},
            "class_type": "VAEEncode",
            "_meta": {"title": "Encode canonical reference"},
        },
        "10": {
            "inputs": {"text": PROMPT, "clip": ["2", 0]},
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "Pixel-art edit instruction"},
        },
        "11": {
            "inputs": {"conditioning": ["10", 0]},
            "class_type": "ConditioningZeroOut",
            "_meta": {"title": "Zero negative conditioning"},
        },
        "12": {
            "inputs": {"conditioning": ["10", 0], "latent": ["6", 0]},
            "class_type": "ReferenceLatent",
            "_meta": {"title": "Action-sheet reference latent"},
        },
        "13": {
            "inputs": {"conditioning": ["12", 0], "latent": ["9", 0]},
            "class_type": "ReferenceLatent",
            "_meta": {"title": "Canonical identity reference latent"},
        },
        "14": {
            "inputs": {"conditioning": ["13", 0], "guidance": GUIDANCE},
            "class_type": "FluxGuidance",
            "_meta": {"title": "Flux guidance"},
        },
        "15": {
            "inputs": {
                "seed": SEED,
                "steps": STEPS,
                "cfg": CFG,
                "sampler_name": SAMPLER,
                "scheduler": SCHEDULER,
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["14", 0],
                "negative": ["11", 0],
                "latent_image": ["6", 0],
            },
            "class_type": "KSampler",
            "_meta": {"title": "Kontext pixel-art reconstruction"},
        },
        "16": {
            "inputs": {"samples": ["15", 0], "vae": ["3", 0]},
            "class_type": "VAEDecode",
            "_meta": {"title": "Decode reconstructed sheet"},
        },
        "17": {
            "inputs": {"filename_prefix": OUTPUT_PREFIX, "images": ["16", 0]},
            "class_type": "SaveImage",
            "_meta": {"title": "Save Kontext pixel-art proof"},
        },
    }


def alpha_from_neutral(cell):
    rgba = np.asarray(cell.convert("RGBA"), dtype=np.uint8).copy()
    rgb = rgba[:, :, :3].astype(np.float32)
    h, w, _ = rgb.shape
    pad = max(4, min(h, w) // 16)
    corners = np.concatenate(
        [
            rgb[:pad, :pad].reshape(-1, 3),
            rgb[:pad, -pad:].reshape(-1, 3),
            rgb[-pad:, :pad].reshape(-1, 3),
            rgb[-pad:, -pad:].reshape(-1, 3),
        ],
        axis=0,
    )
    bg = np.median(corners, axis=0)
    dist = np.sqrt(((rgb - bg) ** 2).sum(axis=2))
    alpha = np.clip((dist - 10.0) / 26.0 * 255.0, 0, 255).astype(np.uint8)
    alpha[alpha < 8] = 0
    rgba[:, :, 3] = alpha
    return Image.fromarray(rgba, "RGBA"), bg.tolist()


def finalize_output(full_output, workspace):
    image = Image.open(full_output).convert("RGB")
    w, h = image.size
    if w != h:
        fail(f"Kontext output is not square: {w}x{h}; exact-grid finalizer refuses to guess", "MODEL/TASK_FAIL")

    source_cell = w // GRID_COLS
    if source_cell * GRID_COLS != w:
        fail(f"Kontext output width {w} is not divisible by {GRID_COLS}", "MODEL/TASK_FAIL")
    grid_h = source_cell * GRID_ROWS
    if grid_h > h:
        fail("Kontext output cannot contain the expected 4x3 centered grid", "MODEL/TASK_FAIL")
    top = (h - grid_h) // 2
    grid = image.crop((0, top, w, top + grid_h))

    working_grid_path = os.path.join(workspace, "h0_dance12_kontext_working_grid.png")
    grid.save(working_grid_path)

    runtime_opaque = grid.resize((GRID_COLS * RUNTIME_CELL, GRID_ROWS * RUNTIME_CELL), Image.Resampling.NEAREST)
    runtime_opaque_path = os.path.join(workspace, "h0_dance12_pixelart_sheet_opaque.png")
    runtime_opaque.save(runtime_opaque_path)

    frames_dir = os.path.join(workspace, "h0_dance12_pixelart_frames")
    os.makedirs(frames_dir, exist_ok=True)
    runtime_rgba = Image.new("RGBA", runtime_opaque.size, (0, 0, 0, 0))
    gif_frames = []
    alpha_bgs = []
    frame_paths = []

    for i in range(len(SELECTED_ZERO_BASED)):
        col = i % GRID_COLS
        row = i // GRID_COLS
        x0 = col * RUNTIME_CELL
        y0 = row * RUNTIME_CELL
        cell = runtime_opaque.crop((x0, y0, x0 + RUNTIME_CELL, y0 + RUNTIME_CELL))
        rgba_cell, bg = alpha_from_neutral(cell)
        alpha_bgs.append(bg)
        runtime_rgba.alpha_composite(rgba_cell, (x0, y0))

        frame_path = os.path.join(frames_dir, f"frame_{i:02d}.png")
        rgba_cell.save(frame_path)
        frame_paths.append(frame_path)

        preview = Image.new("RGBA", (RUNTIME_CELL, RUNTIME_CELL), (48, 48, 48, 255))
        preview.alpha_composite(rgba_cell)
        gif_frames.append(preview.convert("P", palette=Image.Palette.ADAPTIVE))

    runtime_rgba_path = os.path.join(workspace, "h0_dance12_pixelart_sheet_rgba.png")
    runtime_rgba.save(runtime_rgba_path)

    gif_path = os.path.join(workspace, "h0_dance12_pixelart_preview.gif")
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=100,
        loop=0,
        disposal=2,
    )

    return {
        "working_grid": working_grid_path,
        "runtime_sheet_opaque": runtime_opaque_path,
        "runtime_sheet_rgba": runtime_rgba_path,
        "frames_dir": frames_dir,
        "frame_files": frame_paths,
        "preview_gif": gif_path,
        "alpha_background_samples": alpha_bgs,
        "output_source_size": [w, h],
        "runtime_sheet_size": list(runtime_rgba.size),
        "runtime_cell_size": RUNTIME_CELL,
    }


def verify_model(path, expected_sha, label):
    if not os.path.isfile(path):
        fail(f"required {label} missing: {path}", "PRECONDITION_FAIL")
    actual = sha256_file(path)
    if actual.lower() != expected_sha.lower():
        fail(f"{label} SHA mismatch: expected {expected_sha}, got {actual}", "PRECONDITION_FAIL")
    return actual


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True)
    ap.add_argument("--h3-workspace", required=True)
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--comfy-root", required=True)
    ap.add_argument("--port", type=int, default=8191)
    ap.add_argument("--timeout-minutes", type=int, default=180)
    args = ap.parse_args()

    project_root = os.path.abspath(args.project_root)
    h3_workspace = os.path.abspath(args.h3_workspace)
    workspace = os.path.abspath(args.workspace)
    comfy_root = os.path.abspath(args.comfy_root)
    os.makedirs(workspace, exist_ok=True)

    h0_video = os.path.join(h3_workspace, H0_VIDEO)
    reference = os.path.join(project_root, REFERENCE_REL)
    if not os.path.isfile(h0_video):
        fail(f"canonical H0 video missing: {h0_video}", "PRECONDITION_FAIL")
    if not os.path.isfile(reference):
        fail(f"canonical character reference missing: {reference}", "PRECONDITION_FAIL")

    model_hashes = {
        "diffusion": verify_model(os.path.join(comfy_root, "models", "diffusion_models", MODEL), MODEL_SHA256, MODEL),
        "clip_l": verify_model(os.path.join(comfy_root, "models", "text_encoders", CLIP_L), CLIP_L_SHA256, CLIP_L),
        "t5": verify_model(os.path.join(comfy_root, "models", "text_encoders", T5), T5_SHA256, T5),
        "vae": verify_model(os.path.join(comfy_root, "models", "vae", VAE), VAE_SHA256, VAE),
    }

    frames = decode_video(h0_video)
    if len(frames) != SOURCE_FRAME_COUNT:
        fail(f"canonical H0 source has {len(frames)} decoded frames, expected {SOURCE_FRAME_COUNT}", "PRECONDITION_FAIL")

    sheet_path = os.path.join(workspace, "h0_dance12_input_sheet.png")
    selection = make_action_sheet(frames, sheet_path)
    selection_manifest_path = os.path.join(workspace, "h0_dance12_selection_manifest.json")
    with open(selection_manifest_path, "w", encoding="utf-8") as fh:
        json.dump(selection, fh, ensure_ascii=False, indent=2)

    input_dir = os.path.join(comfy_root, "input", "roguelite_kontext")
    os.makedirs(input_dir, exist_ok=True)
    comfy_sheet = os.path.join(input_dir, "h0_dance12_action_sheet.png")
    comfy_reference = os.path.join(input_dir, "exilada_master.png")
    shutil.copy2(sheet_path, comfy_sheet)
    shutil.copy2(reference, comfy_reference)

    base = f"http://127.0.0.1:{args.port}"
    for node_name in REQUIRED_NODES:
        info = request_json(base + f"/object_info/{node_name}", timeout=60)
        if node_name not in info:
            fail(f"required native ComfyUI node unavailable: {node_name}", "INTEGRATION_FAIL")

    prompt = build_prompt()
    prompt_path = os.path.join(workspace, "h0_dance12_kontext_api_prompt.json")
    with open(prompt_path, "w", encoding="utf-8") as fh:
        json.dump(prompt, fh, ensure_ascii=False, indent=2)

    print(
        "KONTEXT-H0-DANCE12: submitting first downstream pixel-art proof: existing H0 Base50 video -> "
        "12-frame square action sheet + canonical Exilada reference -> FLUX.1 Kontext [dev] FP8-scaled.",
        flush=True,
    )
    print(
        f"KONTEXT-H0-DANCE12: {STEPS} steps, guidance={GUIDANCE}, cfg={CFG}, "
        f"{SAMPLER}/{SCHEDULER}, seed={SEED}; no new H3 inference.",
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
    print(f"KONTEXT-H0-DANCE12: prompt_id={prompt_id}", flush=True)

    deadline = started + args.timeout_minutes * 60
    next_report = started + 30
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
            print(f"KONTEXT-H0-DANCE12: inference running for {int(now - started)} seconds...", flush=True)
            next_report = now + 30
        time.sleep(4)
    else:
        fail(f"timeout after {args.timeout_minutes} minutes", "INFRASTRUCTURE_FAIL")

    elapsed = round(time.time() - started, 2)
    generated = newest_png(comfy_root, OUTPUT_PREFIX, started)
    if not generated:
        fail("prompt completed but no new Kontext PNG output was found", "OUTPUT_INTEGRATION_FAIL")

    full_output = os.path.join(workspace, "h0_dance12_kontext_full.png")
    shutil.copy2(generated, full_output)
    finalized = finalize_output(full_output, workspace)

    manifest = {
        "gate": "FLUX_KONTEXT_H0_DANCE12_PIXELART_PROOF",
        "status": "INFERENCE_COMPLETE",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Validate the downstream all-local pixel-art renderer on the existing H0 dance/gesture motion master without another H3 run.",
        "source_action": "dance_or_gesture",
        "source_h0_video": h0_video,
        "source_h0_video_sha256": sha256_file(h0_video),
        "source_reference": reference,
        "source_reference_sha256": sha256_file(reference),
        "selected_source_frames_one_based": SELECTED_ONE_BASED,
        "selection_policy": "deterministic even temporal coverage of the existing 124-frame H0 gesture sequence; semantic action distillation comes later",
        "input_sheet": sheet_path,
        "input_sheet_sha256": sha256_file(sheet_path),
        "selection_manifest": selection_manifest_path,
        "model": MODEL,
        "model_sha256": model_hashes["diffusion"],
        "clip_l": CLIP_L,
        "clip_l_sha256": model_hashes["clip_l"],
        "t5": T5,
        "t5_sha256": model_hashes["t5"],
        "vae": VAE,
        "vae_sha256": model_hashes["vae"],
        "steps": STEPS,
        "guidance": GUIDANCE,
        "cfg": CFG,
        "sampler": SAMPLER,
        "scheduler": SCHEDULER,
        "seed": SEED,
        "prompt_text": PROMPT,
        "prompt_file": prompt_path,
        "prompt_id": prompt_id,
        "elapsed_seconds": elapsed,
        "comfy_output": generated,
        "canonical_full_output": full_output,
        "canonical_full_output_sha256": sha256_file(full_output),
        "finalized": finalized,
        "license_note": "FLUX.1 Kontext [dev] open weights are governed by the FLUX.1 dev non-commercial license; technical validation does not settle commercial shipping rights.",
        "visual_verdict": "PENDING_HUMAN_REVIEW",
        "pass_criteria": [
            "all 12 action poses remain recognizably the same source poses",
            "same Exilada identity/design remains coherent across all cells",
            "output reads as deliberate high-quality pixel art rather than a blurred miniature illustration",
            "no extra/missing/fused limbs or destructive pose rewriting",
            "hair, torn cloth and restraint/accessory masses remain recognizable",
            "the 192px-cell runtime review sheet remains legible near the intended ~128px character scale",
            "automatic background removal is good enough to avoid mandatory manual masks",
        ],
        "history_status": (history_item or {}).get("status"),
    }
    manifest_path = os.path.join(workspace, "h0_dance12_kontext_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print("KONTEXT-H0-DANCE12: PASS - inference complete / visual verdict pending.", flush=True)
    print(f"KONTEXT-H0-DANCE12: input sheet   {sheet_path}", flush=True)
    print(f"KONTEXT-H0-DANCE12: full output   {full_output}", flush=True)
    print(f"KONTEXT-H0-DANCE12: RGBA sheet    {finalized['runtime_sheet_rgba']}", flush=True)
    print(f"KONTEXT-H0-DANCE12: preview GIF   {finalized['preview_gif']}", flush=True)
    print(f"KONTEXT-H0-DANCE12: manifest      {manifest_path}", flush=True)
    print(f"KONTEXT-H0-DANCE12: elapsed       {elapsed} seconds", flush=True)
    print("KONTEXT-H0-DANCE12: do not call the pixel-art renderer proven until the generated sheet is visually reviewed.", flush=True)


if __name__ == "__main__":
    main()
