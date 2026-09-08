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
ROW_COUNT = 3
FRAMES_PER_ROW = 4
WINDOW_LENGTH = 16
WINDOW_OFFSETS = [0, 5, 10, 15]

SQUARE_SIZE = 1024
SQUARE_CELL = 512
WORKING_SUBJECT_HEIGHT = 356
RUNTIME_CELL = 192
FINAL_COLS = 4
FINAL_ROWS = 3

STEPS = 20
CFG = 1.0
GUIDANCE = 2.5
DENOISE = 0.45
SAMPLER = "euler"
SCHEDULER = "simple"
SEED = 0

REFERENCE_INPUT = "roguelite_kontext/exilada_master.png"

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

ROW_PROMPT_TEMPLATE = """Edit image 1 into deliberate high-end pixel art while preserving its physical structure. Image 1 is a 2-by-2 contact sheet containing four TEMPORALLY ORDERED frames from one short continuous animation segment. Read them in this exact order: top-left, top-right, bottom-left, bottom-right. These four cells are one animation sequence, not four independent character designs. Preserve the exact 2-by-2 layout and preserve each source pose, silhouette, foot placement, body lean, hand direction, hair mass, torn cloth, cuffs, shackles and chain fragments.

Image 2 is the canonical identity and art-direction reference for the same character. Change the rendering language, not the character's physical design. Preserve the mature adult woman's body proportions and age exactly: mature severe adult face, adult head-to-body ratio, long adult torso and limbs, lean resilient athletic build with natural feminine adult proportions, adult bust, hips and legs consistent with the source/reference, olive-brown skin, very long heavy messy black hair. DO NOT shorten torso or limbs, enlarge the head, widen/round the face, thicken or soften the anatomy into a juvenile shape, reduce adult sexual dimorphism, make her cute, chibi, childlike, adolescent-looking or infantilized.

Art direction is a hard requirement: mature 1980s sword-and-sorcery charge informed by Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell. Preserve danger, grime, sensuality, heroic adult anatomy, tactile cloth/metal/skin and pulp-fantasy physicality without copying a specific existing composition. Keep the Exilada severe and adult, never sanitized or cute.

Render as authored-looking high-quality contemporary pixel art for a 640x360 belt-scroller. Use crisp aliased silhouettes, intentional coherent pixel clusters, controlled palette, strong anatomy/material separation and readable hair/cloth/chain masses. No painterly miniature look, no soft illustration, no blur, no anti-aliased mush, no extra/missing/fused limbs, no duplicated body parts, no new costume, no new pose, no text, no panel borders. Keep one consistent sprite-artist language across all four frames. Keep the flat neutral background unchanged for automatic removal afterward.

This is row {row_number} of the final spritesheet. The final spritesheet rule is HARD: one temporal animation sequence per row."""


def fail(message, classification="INTEGRATION_FAIL", code=2):
    print(f"KONTEXT-H0-ROWS: FAIL [{classification}] - {message}", file=sys.stderr, flush=True)
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


def grayscale_proxy(frame, size=(96, 160)):
    return np.asarray(frame.convert("L").resize(size, Image.Resampling.BILINEAR), dtype=np.float32)


def motion_scores(frames):
    proxies = [grayscale_proxy(frame) for frame in frames]
    scores = [0.0]
    for i in range(1, len(proxies)):
        scores.append(float(np.mean(np.abs(proxies[i] - proxies[i - 1]))))
    return scores


def choose_row_windows(frames):
    scores = motion_scores(frames)
    n = len(frames)
    thirds = [
        (0, n // 3),
        (n // 3, (2 * n) // 3),
        ((2 * n) // 3, n),
    ]
    rows = []
    for row_index, (seg_start, seg_end) in enumerate(thirds, start=1):
        latest_start = seg_end - WINDOW_LENGTH
        if latest_start < seg_start:
            fail(f"temporal segment {row_index} too short for {WINDOW_LENGTH}-frame window", "PRECONDITION_FAIL")
        best_start = seg_start
        best_energy = -1.0
        for start in range(seg_start, latest_start + 1):
            end = start + WINDOW_LENGTH
            energy = float(sum(scores[start + 1:end]))
            if energy > best_energy:
                best_energy = energy
                best_start = start
        selected = [best_start + offset for offset in WINDOW_OFFSETS]
        rows.append(
            {
                "row": row_index,
                "segment_zero_based": [seg_start, seg_end - 1],
                "window_zero_based": [best_start, best_start + WINDOW_LENGTH - 1],
                "window_motion_energy": best_energy,
                "selected_zero_based": selected,
                "selected_one_based": [i + 1 for i in selected],
            }
        )
    return rows, scores


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
    return Image.fromarray(rgba, "RGBA").crop((x0, y0, x1, y1)), (x0, y0, x1, y1), bg.tolist()


def make_row_square(frames, row_spec, out_path):
    indices = row_spec["selected_zero_based"]
    selected = [frames[i] for i in indices]
    cutouts = []
    bboxes = []
    bg_samples = []
    for frame in selected:
        cutout, bbox, bg = estimate_cutout(frame)
        cutouts.append(cutout)
        bboxes.append(bbox)
        bg_samples.append(bg)

    heights = np.array([c.height for c in cutouts], dtype=np.float32)
    widths = np.array([c.width for c in cutouts], dtype=np.float32)
    scale = min(
        WORKING_SUBJECT_HEIGHT / max(1.0, float(np.median(heights))),
        456.0 / max(1.0, float(np.max(heights))),
        456.0 / max(1.0, float(np.max(widths))),
    )

    centers = np.array([(b[0] + b[2]) / 2.0 for b in bboxes], dtype=np.float32)
    bottoms = np.array([b[3] for b in bboxes], dtype=np.float32)
    median_center = float(np.median(centers))
    median_bottom = float(np.median(bottoms))

    neutral = (96, 96, 96, 255)
    square = Image.new("RGBA", (SQUARE_SIZE, SQUARE_SIZE), neutral)
    cells = []
    for index, (cutout, bbox) in enumerate(zip(cutouts, bboxes)):
        nw = max(1, int(round(cutout.width * scale)))
        nh = max(1, int(round(cutout.height * scale)))
        resized = cutout.resize((nw, nh), Image.Resampling.LANCZOS)
        col = index % 2
        row = index // 2
        cell_x = col * SQUARE_CELL
        cell_y = row * SQUARE_CELL

        center_delta = (((bbox[0] + bbox[2]) / 2.0) - median_center) * scale
        bottom_delta = (bbox[3] - median_bottom) * scale
        target_center_x = cell_x + SQUARE_CELL / 2.0 + center_delta
        target_bottom_y = cell_y + SQUARE_CELL - 54.0 + bottom_delta
        x = int(round(target_center_x - nw / 2.0))
        y = int(round(target_bottom_y - nh))
        x = max(cell_x + 12, min(x, cell_x + SQUARE_CELL - nw - 12))
        y = max(cell_y + 12, min(y, cell_y + SQUARE_CELL - nh - 12))
        square.alpha_composite(resized, (x, y))
        cells.append(
            {
                "sequence_index": index,
                "source_frame_zero_based": indices[index],
                "source_frame_one_based": indices[index] + 1,
                "source_bbox": list(map(int, bbox)),
                "input_cell": [cell_x, cell_y, SQUARE_CELL, SQUARE_CELL],
                "input_paste": [x, y, nw, nh],
            }
        )

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    square.convert("RGB").save(out_path, quality=95)
    return {
        "row": row_spec["row"],
        "selected_zero_based": indices,
        "selected_one_based": [i + 1 for i in indices],
        "square_size": [SQUARE_SIZE, SQUARE_SIZE],
        "cell_size": SQUARE_CELL,
        "global_scale": scale,
        "background_samples": bg_samples,
        "cells": cells,
    }


def build_prompt(row_number, action_input, output_prefix):
    prompt_text = ROW_PROMPT_TEMPLATE.format(row_number=row_number)
    return prompt_text, {
        "1": {
            "inputs": {"unet_name": MODEL, "weight_dtype": "default"},
            "class_type": "UNETLoader",
        },
        "2": {
            "inputs": {"clip_name1": CLIP_L, "clip_name2": T5, "type": "flux", "device": "default"},
            "class_type": "DualCLIPLoader",
        },
        "3": {"inputs": {"vae_name": VAE}, "class_type": "VAELoader"},
        "4": {"inputs": {"image": action_input}, "class_type": "LoadImage"},
        "5": {"inputs": {"image": ["4", 0]}, "class_type": "FluxKontextImageScale"},
        "6": {"inputs": {"pixels": ["5", 0], "vae": ["3", 0]}, "class_type": "VAEEncode"},
        "7": {"inputs": {"image": REFERENCE_INPUT}, "class_type": "LoadImage"},
        "8": {"inputs": {"image": ["7", 0]}, "class_type": "FluxKontextImageScale"},
        "9": {"inputs": {"pixels": ["8", 0], "vae": ["3", 0]}, "class_type": "VAEEncode"},
        "10": {"inputs": {"text": prompt_text, "clip": ["2", 0]}, "class_type": "CLIPTextEncode"},
        "11": {"inputs": {"conditioning": ["10", 0]}, "class_type": "ConditioningZeroOut"},
        "12": {
            "inputs": {"conditioning": ["10", 0], "latent": ["6", 0]},
            "class_type": "ReferenceLatent",
        },
        "13": {
            "inputs": {"conditioning": ["12", 0], "latent": ["9", 0]},
            "class_type": "ReferenceLatent",
        },
        "14": {"inputs": {"conditioning": ["13", 0], "guidance": GUIDANCE}, "class_type": "FluxGuidance"},
        "15": {
            "inputs": {
                "seed": SEED,
                "steps": STEPS,
                "cfg": CFG,
                "sampler_name": SAMPLER,
                "scheduler": SCHEDULER,
                "denoise": DENOISE,
                "model": ["1", 0],
                "positive": ["14", 0],
                "negative": ["11", 0],
                "latent_image": ["6", 0],
            },
            "class_type": "KSampler",
        },
        "16": {"inputs": {"samples": ["15", 0], "vae": ["3", 0]}, "class_type": "VAEDecode"},
        "17": {
            "inputs": {"filename_prefix": output_prefix, "images": ["16", 0]},
            "class_type": "SaveImage",
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


def verify_model(path, expected_sha, label):
    if not os.path.isfile(path):
        fail(f"required {label} missing: {path}", "PRECONDITION_FAIL")
    actual = sha256_file(path)
    if actual.lower() != expected_sha.lower():
        fail(f"{label} SHA mismatch: expected {expected_sha}, got {actual}", "PRECONDITION_FAIL")
    return actual


def run_prompt(base, prompt, comfy_root, prefix, timeout_minutes, row_number):
    started = time.time()
    try:
        response = request_json(base + "/prompt", {"prompt": prompt}, timeout=180)
    except Exception as exc:
        fail(f"row {row_number} prompt submission failed before inference: {exc}", "INTEGRATION_FAIL")
    prompt_id = response.get("prompt_id")
    if not prompt_id:
        fail(f"row {row_number} ComfyUI did not return prompt_id: {response}", "INTEGRATION_FAIL")
    print(f"KONTEXT-H0-ROWS: row={row_number} prompt_id={prompt_id}", flush=True)

    deadline = started + timeout_minutes * 60
    next_report = started + 30
    history_item = None
    while time.time() < deadline:
        history = request_json(base + f"/history/{prompt_id}", timeout=120)
        item = history.get(prompt_id) if isinstance(history, dict) else None
        if item:
            history_item = item
            status = item.get("status") or {}
            for message in status.get("messages") or []:
                if isinstance(message, (list, tuple)) and message and message[0] == "execution_error":
                    fail(
                        f"row {row_number} ComfyUI execution_error after prompt submission: {message}",
                        "EXECUTION_FAIL_REQUIRES_LOG_CLASSIFICATION",
                    )
            if status.get("completed") is True:
                break
        now = time.time()
        if now >= next_report:
            print(f"KONTEXT-H0-ROWS: row={row_number} inference running for {int(now - started)} seconds...", flush=True)
            next_report = now + 30
        time.sleep(4)
    else:
        fail(f"row {row_number} timeout after {timeout_minutes} minutes", "INFRASTRUCTURE_FAIL")

    elapsed = round(time.time() - started, 2)
    generated = newest_png(comfy_root, prefix, started)
    if not generated:
        fail(f"row {row_number} prompt completed but no new PNG was found", "OUTPUT_INTEGRATION_FAIL")
    return prompt_id, elapsed, generated, (history_item or {}).get("status")


def finalize_row(full_output, row_number, workspace):
    image = Image.open(full_output).convert("RGB")
    if image.size != (SQUARE_SIZE, SQUARE_SIZE):
        fail(f"row {row_number} output size {image.size} differs from expected 1024x1024", "MODEL/TASK_FAIL")
    frames_dir = os.path.join(workspace, "h0_dance_rows_pixelart_frames", f"row_{row_number:02d}")
    os.makedirs(frames_dir, exist_ok=True)
    opaque_cells = []
    rgba_cells = []
    alpha_bgs = []
    frame_paths = []
    for i in range(FRAMES_PER_ROW):
        col = i % 2
        row = i // 2
        cell = image.crop((col * SQUARE_CELL, row * SQUARE_CELL, (col + 1) * SQUARE_CELL, (row + 1) * SQUARE_CELL))
        cell = cell.resize((RUNTIME_CELL, RUNTIME_CELL), Image.Resampling.NEAREST)
        rgba, bg = alpha_from_neutral(cell)
        opaque_cells.append(cell)
        rgba_cells.append(rgba)
        alpha_bgs.append(bg)
        frame_path = os.path.join(frames_dir, f"frame_{i:02d}.png")
        rgba.save(frame_path)
        frame_paths.append(frame_path)

    row_opaque = Image.new("RGB", (FINAL_COLS * RUNTIME_CELL, RUNTIME_CELL), (96, 96, 96))
    row_rgba = Image.new("RGBA", (FINAL_COLS * RUNTIME_CELL, RUNTIME_CELL), (0, 0, 0, 0))
    for i in range(FRAMES_PER_ROW):
        row_opaque.paste(opaque_cells[i], (i * RUNTIME_CELL, 0))
        row_rgba.alpha_composite(rgba_cells[i], (i * RUNTIME_CELL, 0))

    row_opaque_path = os.path.join(workspace, f"h0_dance_row{row_number:02d}_pixelart_opaque.png")
    row_rgba_path = os.path.join(workspace, f"h0_dance_row{row_number:02d}_pixelart_rgba.png")
    row_opaque.save(row_opaque_path)
    row_rgba.save(row_rgba_path)

    previews = []
    for rgba in rgba_cells:
        preview = Image.new("RGBA", (RUNTIME_CELL, RUNTIME_CELL), (48, 48, 48, 255))
        preview.alpha_composite(rgba)
        previews.append(preview.convert("P", palette=Image.Palette.ADAPTIVE))
    gif_path = os.path.join(workspace, f"h0_dance_row{row_number:02d}_preview.gif")
    previews[0].save(gif_path, save_all=True, append_images=previews[1:], duration=120, loop=0, disposal=2)

    return {
        "row": row_number,
        "full_output": full_output,
        "row_opaque": row_opaque_path,
        "row_rgba": row_rgba_path,
        "preview_gif": gif_path,
        "frame_files": frame_paths,
        "alpha_background_samples": alpha_bgs,
    }


def pack_final_sheet(row_outputs, workspace):
    opaque = Image.new("RGB", (FINAL_COLS * RUNTIME_CELL, FINAL_ROWS * RUNTIME_CELL), (96, 96, 96))
    rgba = Image.new("RGBA", (FINAL_COLS * RUNTIME_CELL, FINAL_ROWS * RUNTIME_CELL), (0, 0, 0, 0))
    for row_index, out in enumerate(row_outputs):
        row_opaque = Image.open(out["row_opaque"]).convert("RGB")
        row_rgba = Image.open(out["row_rgba"]).convert("RGBA")
        opaque.paste(row_opaque, (0, row_index * RUNTIME_CELL))
        rgba.alpha_composite(row_rgba, (0, row_index * RUNTIME_CELL))
    opaque_path = os.path.join(workspace, "h0_dance3x4_pixelart_sheet_opaque.png")
    rgba_path = os.path.join(workspace, "h0_dance3x4_pixelart_sheet_rgba.png")
    opaque.save(opaque_path)
    rgba.save(rgba_path)
    return opaque_path, rgba_path


def make_source_contact_sheet(frames, row_specs, workspace):
    sheet = Image.new("RGB", (FINAL_COLS * RUNTIME_CELL, FINAL_ROWS * RUNTIME_CELL), (96, 96, 96))
    for r, row_spec in enumerate(row_specs):
        for c, frame_index in enumerate(row_spec["selected_zero_based"]):
            frame = frames[frame_index]
            cutout, _, _ = estimate_cutout(frame)
            ratio = min(150 / cutout.height, 160 / cutout.width)
            resized = cutout.resize((max(1, int(cutout.width * ratio)), max(1, int(cutout.height * ratio))), Image.Resampling.LANCZOS)
            cell = Image.new("RGBA", (RUNTIME_CELL, RUNTIME_CELL), (96, 96, 96, 255))
            cell.alpha_composite(resized, ((RUNTIME_CELL - resized.width) // 2, RUNTIME_CELL - resized.height - 12))
            sheet.paste(cell.convert("RGB"), (c * RUNTIME_CELL, r * RUNTIME_CELL))
    path = os.path.join(workspace, "h0_dance3x4_source_temporal_rows.png")
    sheet.save(path)
    return path


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

    row_specs, scores = choose_row_windows(frames)
    source_contact = make_source_contact_sheet(frames, row_specs, workspace)

    selection_manifest = {
        "policy": "three temporal rows; one coherent high-motion 16-frame window selected independently inside each third of the 124-frame H0; four ordered frames per row at offsets 0,5,10,15",
        "source_frame_count": len(frames),
        "source_fps": SOURCE_FPS,
        "rows": row_specs,
        "motion_scores": scores,
        "source_contact_sheet": source_contact,
    }
    selection_manifest_path = os.path.join(workspace, "h0_dance3x4_temporal_selection_manifest.json")
    with open(selection_manifest_path, "w", encoding="utf-8") as fh:
        json.dump(selection_manifest, fh, ensure_ascii=False, indent=2)

    input_dir = os.path.join(comfy_root, "input", "roguelite_kontext")
    os.makedirs(input_dir, exist_ok=True)
    shutil.copy2(reference, os.path.join(input_dir, "exilada_master.png"))

    base = f"http://127.0.0.1:{args.port}"
    for node_name in REQUIRED_NODES:
        info = request_json(base + f"/object_info/{node_name}", timeout=60)
        if node_name not in info:
            fail(f"required native ComfyUI node unavailable: {node_name}", "INTEGRATION_FAIL")

    run_records = []
    finalized_rows = []
    for row_spec in row_specs:
        row_number = row_spec["row"]
        row_input_path = os.path.join(workspace, f"h0_dance_row{row_number:02d}_input_2x2.png")
        row_input_manifest = make_row_square(frames, row_spec, row_input_path)
        row_manifest_path = os.path.join(workspace, f"h0_dance_row{row_number:02d}_input_manifest.json")
        with open(row_manifest_path, "w", encoding="utf-8") as fh:
            json.dump(row_input_manifest, fh, ensure_ascii=False, indent=2)

        comfy_input_name = f"roguelite_kontext/h0_dance_row{row_number:02d}_input_2x2.png"
        shutil.copy2(row_input_path, os.path.join(input_dir, os.path.basename(comfy_input_name)))
        output_prefix = f"roguelite_kontext/h0_dance_row{row_number:02d}_structure_lock"
        prompt_text, prompt = build_prompt(row_number, comfy_input_name, output_prefix)
        prompt_path = os.path.join(workspace, f"h0_dance_row{row_number:02d}_kontext_api_prompt.json")
        with open(prompt_path, "w", encoding="utf-8") as fh:
            json.dump(prompt, fh, ensure_ascii=False, indent=2)

        print(
            f"KONTEXT-H0-ROWS: row={row_number} frames={row_spec['selected_one_based']} -> 2x2 high-detail Kontext edit; "
            f"denoise={DENOISE}; one animation sequence per final row.",
            flush=True,
        )
        prompt_id, elapsed, generated, history_status = run_prompt(
            base, prompt, comfy_root, output_prefix, args.timeout_minutes, row_number
        )
        full_output = os.path.join(workspace, f"h0_dance_row{row_number:02d}_kontext_full.png")
        shutil.copy2(generated, full_output)
        finalized = finalize_row(full_output, row_number, workspace)
        finalized_rows.append(finalized)
        run_records.append(
            {
                "row": row_number,
                "selected_source_frames_one_based": row_spec["selected_one_based"],
                "input": row_input_path,
                "input_sha256": sha256_file(row_input_path),
                "prompt_file": prompt_path,
                "prompt_text": prompt_text,
                "prompt_id": prompt_id,
                "elapsed_seconds": elapsed,
                "comfy_output": generated,
                "full_output": full_output,
                "full_output_sha256": sha256_file(full_output),
                "finalized": finalized,
                "history_status": history_status,
            }
        )

    opaque_sheet, rgba_sheet = pack_final_sheet(finalized_rows, workspace)
    manifest = {
        "gate": "FLUX_KONTEXT_H0_DANCE3X4_TEMPORAL_ROWS_STRUCTURE_LOCK",
        "status": "INFERENCE_COMPLETE",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Repair Runner50 visual failure by enforcing one coherent temporal animation per row, larger per-character renderer inputs and adult-body structure preservation.",
        "source_action": "dance_or_gesture",
        "source_h0_video": h0_video,
        "source_h0_video_sha256": sha256_file(h0_video),
        "source_reference": reference,
        "source_reference_sha256": sha256_file(reference),
        "selection_manifest": selection_manifest_path,
        "source_contact_sheet": source_contact,
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
        "denoise": DENOISE,
        "sampler": SAMPLER,
        "scheduler": SCHEDULER,
        "seed": SEED,
        "row_runs": run_records,
        "final_sheet_opaque": opaque_sheet,
        "final_sheet_rgba": rgba_sheet,
        "final_sheet_size": [FINAL_COLS * RUNTIME_CELL, FINAL_ROWS * RUNTIME_CELL],
        "runtime_cell_size": RUNTIME_CELL,
        "hard_invariants": [
            "one temporal animation sequence per row",
            "mature adult anatomy and proportions must not be infantilized",
            "Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell sword-and-sorcery charge remains active",
            "renderer changes rendering language, not character body design",
            "complete character remains visible in every cell",
        ],
        "visual_verdict": "PENDING_HUMAN_REVIEW",
    }
    manifest_path = os.path.join(workspace, "h0_dance3x4_kontext_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print("KONTEXT-H0-ROWS: PASS - three row inferences complete / visual verdict pending.", flush=True)
    print(f"KONTEXT-H0-ROWS: source temporal rows {source_contact}", flush=True)
    print(f"KONTEXT-H0-ROWS: final opaque sheet {opaque_sheet}", flush=True)
    print(f"KONTEXT-H0-ROWS: final RGBA sheet   {rgba_sheet}", flush=True)
    for out in finalized_rows:
        print(f"KONTEXT-H0-ROWS: row {out['row']} preview {out['preview_gif']}", flush=True)
    print(f"KONTEXT-H0-ROWS: manifest {manifest_path}", flush=True)
    print("KONTEXT-H0-ROWS: do not call the renderer proven until body maturity/proportions, row temporal coherence and 1980s art direction are visually reviewed.", flush=True)


if __name__ == "__main__":
    main()
