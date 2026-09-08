#!/usr/bin/env python3
import argparse
import importlib.util
import json
import os
import shutil
from datetime import datetime, timezone

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
LEGACY_PATH = os.path.join(HERE, "run_h0_dance3x4_temporal_rows_structure_lock.py")
_spec = importlib.util.spec_from_file_location("runner51_impl", LEGACY_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Could not load Runner51 helper module: {LEGACY_PATH}")
legacy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(legacy)

ACTION = "dance_or_gesture"
ACTION_FRAME_COUNT = 12
CHUNK_COUNT = 3
FRAMES_PER_CHUNK = 4
RUNTIME_CELL = 192
FINAL_COLS = ACTION_FRAME_COUNT
FINAL_ROWS = 1
FINAL_WIDTH = FINAL_COLS * RUNTIME_CELL
FINAL_HEIGHT = RUNTIME_CELL

STEPS = 20
CFG = 1.0
GUIDANCE = 2.5
DENOISE = 0.45
SAMPLER = "euler"
SCHEDULER = "simple"
SEED = 0

CHUNK_PROMPT_TEMPLATE = """Edit image 1 into deliberate high-end pixel art while preserving its physical structure.

Image 1 is a temporary 2-by-2 PROCESSING TILE containing four consecutive ordered samples from ONE continuous dance_or_gesture action. Read the four cells in this exact temporal order: top-left, top-right, bottom-left, bottom-right. This 2-by-2 arrangement is NOT the final spritesheet layout. After rendering, these four frames will be extracted and concatenated with the other processing tiles into ONE SINGLE HORIZONTAL ACTION ROW. Therefore preserve the exact pose and identity inside every cell; do not invent a new pose, merge cells, reorder frames, or reinterpret the four cells as separate character designs.

This tile is chunk {chunk_number} of {chunk_count}, representing global action frames {global_start} through {global_end} of 12. All 12 final frames belong to the same action and must remain compatible in scale, body design, palette and sprite-artist language.

Image 2 is the canonical identity and art-direction reference for the same character. Change the rendering language, not the character's physical design. Preserve the mature adult woman's body proportions and age exactly: mature severe adult face, adult head-to-body ratio, long adult torso and limbs, lean resilient athletic build with natural feminine adult proportions, adult bust, hips and legs consistent with the source/reference, olive-brown skin, very long heavy messy black hair. DO NOT shorten torso or limbs, enlarge the head, widen or round the face, thicken or soften the anatomy into a juvenile shape, reduce adult sexual dimorphism, make her cute, chibi, childlike, adolescent-looking or infantilized.

Preserve source pose, silhouette, foot placement, body lean, hand direction, hair mass, torn cloth, cuffs, shackles and chain fragments in every cell. Keep the complete character visible; do not crop hair, hands, feet, cloth or chain.

Art direction is a hard requirement: mature 1980s sword-and-sorcery charge informed by Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell. Preserve danger, grime, sensuality, heroic adult anatomy, tactile cloth/metal/skin and pulp-fantasy physicality without copying a specific existing composition. Keep the Exilada severe and adult, never sanitized or cute.

Render as authored-looking high-quality contemporary pixel art for a 640x360 belt-scroller. Use crisp aliased silhouettes, intentional coherent pixel clusters, controlled palette, strong anatomy/material separation and readable hair/cloth/chain masses. No painterly miniature look, no soft illustration, no global blur, no anti-aliased mush, no extra/missing/fused limbs, no duplicated body parts, no new costume, no text, no panel borders. Keep one consistent sprite-artist language across all four frames. Keep the flat neutral background unchanged for automatic removal afterward.

HARD FINAL LAYOUT CONTRACT: one action equals one spritesheet row. The final dance_or_gesture asset is 12 frames in one horizontal row, left-to-right in time. This 2-by-2 tile is only an internal high-resolution processing device."""


def fail(message, classification="INTEGRATION_FAIL", code=2):
    legacy.fail(message, classification, code)


def select_full_action_frames(frame_count):
    if frame_count < ACTION_FRAME_COUNT:
        fail(f"source has only {frame_count} frames; need at least {ACTION_FRAME_COUNT}", "PRECONDITION_FAIL")
    selected = np.linspace(0, frame_count - 1, ACTION_FRAME_COUNT).round().astype(int).tolist()
    if len(set(selected)) != ACTION_FRAME_COUNT:
        fail(f"full-action selection produced duplicate frames: {selected}", "CONFIGURATION_FAIL")
    return selected


def frame_durations_ms(selected, source_frame_count, fps):
    centers = np.asarray(selected, dtype=np.float64)
    boundaries = [0.0]
    for a, b in zip(centers[:-1], centers[1:]):
        boundaries.append((a + b + 1.0) / 2.0)
    boundaries.append(float(source_frame_count))
    durations = []
    for start, end in zip(boundaries[:-1], boundaries[1:]):
        durations.append(max(1, int(round((end - start) * 1000.0 / fps))))
    return durations


def make_source_strip(frames, selected, workspace):
    strip = Image.new("RGB", (FINAL_WIDTH, FINAL_HEIGHT), (96, 96, 96))
    for i, frame_index in enumerate(selected):
        cutout, _, _ = legacy.estimate_cutout(frames[frame_index])
        ratio = min(150 / max(1, cutout.height), 160 / max(1, cutout.width))
        resized = cutout.resize(
            (max(1, int(round(cutout.width * ratio))), max(1, int(round(cutout.height * ratio)))),
            Image.Resampling.LANCZOS,
        )
        cell = Image.new("RGBA", (RUNTIME_CELL, RUNTIME_CELL), (96, 96, 96, 255))
        x = (RUNTIME_CELL - resized.width) // 2
        y = RUNTIME_CELL - resized.height - 12
        cell.alpha_composite(resized, (x, y))
        strip.paste(cell.convert("RGB"), (i * RUNTIME_CELL, 0))
    path = os.path.join(workspace, "h0_dance12_source_action_strip.png")
    strip.save(path)
    return path


def make_chunk_specs(selected):
    chunks = []
    for chunk_index in range(CHUNK_COUNT):
        start = chunk_index * FRAMES_PER_CHUNK
        chunk_frames = selected[start : start + FRAMES_PER_CHUNK]
        chunks.append(
            {
                "chunk": chunk_index + 1,
                "row": chunk_index + 1,  # compatibility with Runner51 helper used only to make a 2x2 processing tile
                "global_action_frame_range_one_based": [start + 1, start + FRAMES_PER_CHUNK],
                "selected_zero_based": chunk_frames,
                "selected_one_based": [i + 1 for i in chunk_frames],
            }
        )
    return chunks


def build_prompt(chunk_spec, action_input, output_prefix):
    prompt_text = CHUNK_PROMPT_TEMPLATE.format(
        chunk_number=chunk_spec["chunk"],
        chunk_count=CHUNK_COUNT,
        global_start=chunk_spec["global_action_frame_range_one_based"][0],
        global_end=chunk_spec["global_action_frame_range_one_based"][1],
    )
    return prompt_text, {
        "1": {
            "inputs": {"unet_name": legacy.MODEL, "weight_dtype": "default"},
            "class_type": "UNETLoader",
        },
        "2": {
            "inputs": {
                "clip_name1": legacy.CLIP_L,
                "clip_name2": legacy.T5,
                "type": "flux",
                "device": "default",
            },
            "class_type": "DualCLIPLoader",
        },
        "3": {"inputs": {"vae_name": legacy.VAE}, "class_type": "VAELoader"},
        "4": {"inputs": {"image": action_input}, "class_type": "LoadImage"},
        "5": {"inputs": {"image": ["4", 0]}, "class_type": "FluxKontextImageScale"},
        "6": {"inputs": {"pixels": ["5", 0], "vae": ["3", 0]}, "class_type": "VAEEncode"},
        "7": {"inputs": {"image": legacy.REFERENCE_INPUT}, "class_type": "LoadImage"},
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


def finalize_chunk(full_output, chunk_spec, workspace):
    image = Image.open(full_output).convert("RGB")
    if image.size != (legacy.SQUARE_SIZE, legacy.SQUARE_SIZE):
        fail(
            f"chunk {chunk_spec['chunk']} output size {image.size} differs from expected 1024x1024",
            "MODEL/TASK_FAIL",
        )

    frames_dir = os.path.join(workspace, "h0_dance12_pixelart_frames")
    os.makedirs(frames_dir, exist_ok=True)
    cells = []
    records = []
    global_start = chunk_spec["global_action_frame_range_one_based"][0] - 1

    for local_index in range(FRAMES_PER_CHUNK):
        col = local_index % 2
        row = local_index // 2
        cell = image.crop(
            (
                col * legacy.SQUARE_CELL,
                row * legacy.SQUARE_CELL,
                (col + 1) * legacy.SQUARE_CELL,
                (row + 1) * legacy.SQUARE_CELL,
            )
        )
        cell = cell.resize((RUNTIME_CELL, RUNTIME_CELL), Image.Resampling.NEAREST)
        rgba, bg = legacy.alpha_from_neutral(cell)
        action_index = global_start + local_index
        frame_path = os.path.join(frames_dir, f"frame_{action_index:02d}.png")
        rgba.save(frame_path)
        cells.append((cell, rgba))
        records.append(
            {
                "action_frame_index_zero_based": action_index,
                "source_frame_one_based": chunk_spec["selected_one_based"][local_index],
                "file": frame_path,
                "alpha_background_sample": bg,
            }
        )
    return cells, records


def pack_single_action_row(all_cells, durations_ms, workspace):
    if len(all_cells) != ACTION_FRAME_COUNT:
        fail(f"expected {ACTION_FRAME_COUNT} rendered cells, got {len(all_cells)}", "OUTPUT_INTEGRATION_FAIL")

    opaque = Image.new("RGB", (FINAL_WIDTH, FINAL_HEIGHT), (96, 96, 96))
    rgba = Image.new("RGBA", (FINAL_WIDTH, FINAL_HEIGHT), (0, 0, 0, 0))
    gif_frames = []

    for i, (opaque_cell, rgba_cell) in enumerate(all_cells):
        x = i * RUNTIME_CELL
        opaque.paste(opaque_cell, (x, 0))
        rgba.alpha_composite(rgba_cell, (x, 0))
        preview = Image.new("RGBA", (RUNTIME_CELL, RUNTIME_CELL), (48, 48, 48, 255))
        preview.alpha_composite(rgba_cell)
        gif_frames.append(preview.convert("P", palette=Image.Palette.ADAPTIVE))

    opaque_path = os.path.join(workspace, "h0_dance12_pixelart_sheet_opaque.png")
    rgba_path = os.path.join(workspace, "h0_dance12_pixelart_sheet_rgba.png")
    gif_path = os.path.join(workspace, "h0_dance12_preview.gif")
    opaque.save(opaque_path)
    rgba.save(rgba_path)
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=durations_ms,
        loop=0,
        disposal=2,
    )
    return opaque_path, rgba_path, gif_path


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

    h0_video = os.path.join(h3_workspace, legacy.H0_VIDEO)
    reference = os.path.join(project_root, legacy.REFERENCE_REL)
    if not os.path.isfile(h0_video):
        fail(f"canonical H0 video missing: {h0_video}", "PRECONDITION_FAIL")
    if not os.path.isfile(reference):
        fail(f"canonical character reference missing: {reference}", "PRECONDITION_FAIL")

    model_hashes = {
        "diffusion": legacy.verify_model(
            os.path.join(comfy_root, "models", "diffusion_models", legacy.MODEL),
            legacy.MODEL_SHA256,
            legacy.MODEL,
        ),
        "clip_l": legacy.verify_model(
            os.path.join(comfy_root, "models", "text_encoders", legacy.CLIP_L),
            legacy.CLIP_L_SHA256,
            legacy.CLIP_L,
        ),
        "t5": legacy.verify_model(
            os.path.join(comfy_root, "models", "text_encoders", legacy.T5),
            legacy.T5_SHA256,
            legacy.T5,
        ),
        "vae": legacy.verify_model(
            os.path.join(comfy_root, "models", "vae", legacy.VAE),
            legacy.VAE_SHA256,
            legacy.VAE,
        ),
    }

    frames = legacy.decode_video(h0_video)
    if len(frames) != legacy.SOURCE_FRAME_COUNT:
        fail(
            f"canonical H0 source has {len(frames)} decoded frames, expected {legacy.SOURCE_FRAME_COUNT}",
            "PRECONDITION_FAIL",
        )

    selected = select_full_action_frames(len(frames))
    durations_ms = frame_durations_ms(selected, len(frames), legacy.SOURCE_FPS)
    chunks = make_chunk_specs(selected)
    source_strip = make_source_strip(frames, selected, workspace)

    selection_manifest = {
        "policy": "single known action interval = complete 124-frame H0; select 12 ordered full-action samples across the entire interval; processing chunks never change final one-row action semantics",
        "action": ACTION,
        "source_frame_count": len(frames),
        "source_fps": legacy.SOURCE_FPS,
        "selected_zero_based": selected,
        "selected_one_based": [i + 1 for i in selected],
        "frame_durations_ms": durations_ms,
        "final_layout": {"rows": 1, "columns": ACTION_FRAME_COUNT, "cell": [RUNTIME_CELL, RUNTIME_CELL]},
        "chunks": chunks,
        "source_action_strip": source_strip,
    }
    selection_manifest_path = os.path.join(workspace, "h0_dance12_action_selection_manifest.json")
    with open(selection_manifest_path, "w", encoding="utf-8") as fh:
        json.dump(selection_manifest, fh, ensure_ascii=False, indent=2)

    input_dir = os.path.join(comfy_root, "input", "roguelite_kontext")
    os.makedirs(input_dir, exist_ok=True)
    shutil.copy2(reference, os.path.join(input_dir, "exilada_master.png"))

    base = f"http://127.0.0.1:{args.port}"
    for node_name in legacy.REQUIRED_NODES:
        info = legacy.request_json(base + f"/object_info/{node_name}", timeout=60)
        if node_name not in info:
            fail(f"required native ComfyUI node unavailable: {node_name}", "INTEGRATION_FAIL")

    run_records = []
    all_cells = []
    frame_records = []

    for chunk_spec in chunks:
        chunk_number = chunk_spec["chunk"]
        chunk_input_path = os.path.join(workspace, f"h0_dance12_chunk{chunk_number:02d}_input_2x2.png")
        chunk_input_manifest = legacy.make_row_square(frames, chunk_spec, chunk_input_path)
        chunk_input_manifest["semantic_role"] = "internal processing tile only; final asset remains one 12-frame action row"
        chunk_input_manifest["global_action_frame_range_one_based"] = chunk_spec[
            "global_action_frame_range_one_based"
        ]
        chunk_manifest_path = os.path.join(workspace, f"h0_dance12_chunk{chunk_number:02d}_input_manifest.json")
        with open(chunk_manifest_path, "w", encoding="utf-8") as fh:
            json.dump(chunk_input_manifest, fh, ensure_ascii=False, indent=2)

        comfy_input_name = f"roguelite_kontext/h0_dance12_chunk{chunk_number:02d}_input_2x2.png"
        shutil.copy2(chunk_input_path, os.path.join(input_dir, os.path.basename(comfy_input_name)))
        output_prefix = f"roguelite_kontext/h0_dance12_chunk{chunk_number:02d}_structure_lock"
        prompt_text, prompt = build_prompt(chunk_spec, comfy_input_name, output_prefix)
        prompt_path = os.path.join(workspace, f"h0_dance12_chunk{chunk_number:02d}_kontext_api_prompt.json")
        with open(prompt_path, "w", encoding="utf-8") as fh:
            json.dump(prompt, fh, ensure_ascii=False, indent=2)

        print(
            f"KONTEXT-H0-DANCE12: chunk={chunk_number}/{CHUNK_COUNT} global_action_frames="
            f"{chunk_spec['global_action_frame_range_one_based']} source_frames={chunk_spec['selected_one_based']} "
            f"denoise={DENOISE}; final layout remains ONE 12-frame row.",
            flush=True,
        )

        prompt_id, elapsed, generated, history_status = legacy.run_prompt(
            base, prompt, comfy_root, output_prefix, args.timeout_minutes, chunk_number
        )
        full_output = os.path.join(workspace, f"h0_dance12_chunk{chunk_number:02d}_kontext_full.png")
        shutil.copy2(generated, full_output)
        cells, records = finalize_chunk(full_output, chunk_spec, workspace)
        all_cells.extend(cells)
        frame_records.extend(records)
        run_records.append(
            {
                "chunk": chunk_number,
                "global_action_frame_range_one_based": chunk_spec["global_action_frame_range_one_based"],
                "selected_source_frames_one_based": chunk_spec["selected_one_based"],
                "input": chunk_input_path,
                "input_sha256": legacy.sha256_file(chunk_input_path),
                "prompt_file": prompt_path,
                "prompt_text": prompt_text,
                "prompt_id": prompt_id,
                "elapsed_seconds": elapsed,
                "comfy_output": generated,
                "full_output": full_output,
                "full_output_sha256": legacy.sha256_file(full_output),
                "history_status": history_status,
            }
        )

    opaque_sheet, rgba_sheet, preview_gif = pack_single_action_row(all_cells, durations_ms, workspace)

    for i, record in enumerate(frame_records):
        record["duration_ms"] = durations_ms[i]
        record["sheet_cell"] = [i * RUNTIME_CELL, 0, RUNTIME_CELL, RUNTIME_CELL]

    manifest = {
        "gate": "FLUX_KONTEXT_H0_DANCE12_SINGLE_ACTION_ROW_STRUCTURE_LOCK",
        "status": "INFERENCE_COMPLETE",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Convert the existing H0 dance_or_gesture motion master into one correct 12-frame horizontal action row while using three internal 2x2 high-resolution Kontext processing tiles.",
        "source_action": ACTION,
        "source_h0_video": h0_video,
        "source_h0_video_sha256": legacy.sha256_file(h0_video),
        "source_reference": reference,
        "source_reference_sha256": legacy.sha256_file(reference),
        "selection_manifest": selection_manifest_path,
        "source_action_strip": source_strip,
        "selected_source_frames_one_based": [i + 1 for i in selected],
        "frame_durations_ms": durations_ms,
        "model": legacy.MODEL,
        "model_sha256": model_hashes["diffusion"],
        "clip_l": legacy.CLIP_L,
        "clip_l_sha256": model_hashes["clip_l"],
        "t5": legacy.T5,
        "t5_sha256": model_hashes["t5"],
        "vae": legacy.VAE,
        "vae_sha256": model_hashes["vae"],
        "steps": STEPS,
        "guidance": GUIDANCE,
        "cfg": CFG,
        "denoise": DENOISE,
        "sampler": SAMPLER,
        "scheduler": SCHEDULER,
        "seed": SEED,
        "processing_chunks": run_records,
        "frames": frame_records,
        "final_sheet_opaque": opaque_sheet,
        "final_sheet_rgba": rgba_sheet,
        "preview_gif": preview_gif,
        "final_sheet_size": [FINAL_WIDTH, FINAL_HEIGHT],
        "runtime_cell_size": RUNTIME_CELL,
        "final_layout": "12 columns x 1 row; one action = one row; left-to-right temporal order",
        "hard_invariants": [
            "one action equals one spritesheet row",
            "all 12 dance_or_gesture frames remain in one horizontal temporal sequence",
            "2x2 Kontext tiles are internal processing chunks only and never define final sheet rows",
            "mature adult anatomy and proportions must not be infantilized",
            "Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell sword-and-sorcery charge remains active",
            "renderer changes rendering language, not character body design",
            "complete character remains visible in every cell",
        ],
        "visual_verdict": "PENDING_HUMAN_REVIEW",
    }
    manifest_path = os.path.join(workspace, "h0_dance12_kontext_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print("KONTEXT-H0-DANCE12: PASS - three internal chunk inferences complete / visual verdict pending.", flush=True)
    print(f"KONTEXT-H0-DANCE12: source 1x12 strip {source_strip}", flush=True)
    print(f"KONTEXT-H0-DANCE12: final opaque 1x12 sheet {opaque_sheet}", flush=True)
    print(f"KONTEXT-H0-DANCE12: final RGBA 1x12 sheet   {rgba_sheet}", flush=True)
    print(f"KONTEXT-H0-DANCE12: full-action preview GIF {preview_gif}", flush=True)
    print(f"KONTEXT-H0-DANCE12: manifest {manifest_path}", flush=True)
    print(
        "KONTEXT-H0-DANCE12: final layout contract is one action = one row. Do not call the renderer proven until body maturity, pose fidelity, cross-chunk consistency, pixel-art quality and art direction are visually reviewed.",
        flush=True,
    )


if __name__ == "__main__":
    main()
