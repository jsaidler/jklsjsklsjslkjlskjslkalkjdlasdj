#!/usr/bin/env python3
import argparse
import importlib.util
import json
import os
import shutil
from datetime import datetime, timezone

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.join(HERE, "run_h0_dance12_single_action_row_structure_lock.py")
_spec = importlib.util.spec_from_file_location("runner52_impl", BASE_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Could not load Runner52 helper module: {BASE_PATH}")
r52 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r52)
legacy = r52.legacy

LORA_NAME = "ume_modern_pixelart.safetensors"
LORA_SHA256 = "ed226c149dca6286ae345b6900d807f791a52b1746ed8f524af41efdfda6f0a4"
LORA_STRENGTH = 1.0
TARGET_CHUNK_INDEX = 1  # zero-based: Runner52 chunk2 / final action frames 5-8
MASTER_CELL = 384

STYLE_SUFFIX = """

STYLE ADAPTER REQUIREMENT: a dedicated Modern Pixel Art FLUX LoRA is active. Use its intended modern pixel-art language and the trigger concept 'umempart' as style guidance. Strengthen deliberate authored pixel clusters, clean aliased contour decisions, controlled color grouping, material separation and readable sprite masses. Do not turn the figure into retro-cute/chibi art and do not redesign anatomy. The LoRA is for rendering language only; Image 1 pose/structure and Image 2 mature Exilada identity remain authoritative.
"""


def fail(message, classification="INTEGRATION_FAIL", code=2):
    legacy.fail(message, classification, code)


def build_prompt_with_lora(chunk_spec, action_input, output_prefix):
    prompt_text, prompt = r52.build_prompt(chunk_spec, action_input, output_prefix)
    prompt_text = prompt_text + STYLE_SUFFIX
    prompt["10"]["inputs"]["text"] = prompt_text
    prompt["18"] = {
        "inputs": {
            "model": ["1", 0],
            "lora_name": LORA_NAME,
            "strength_model": LORA_STRENGTH,
        },
        "class_type": "LoraLoaderModelOnly",
    }
    prompt["15"]["inputs"]["model"] = ["18", 0]
    return prompt_text, prompt


def finalize_probe(full_output, chunk_spec, workspace, durations_ms):
    image = Image.open(full_output).convert("RGB")
    if image.size != (legacy.SQUARE_SIZE, legacy.SQUARE_SIZE):
        fail(f"probe output size {image.size} differs from expected 1024x1024", "MODEL/TASK_FAIL")

    frames_dir = os.path.join(workspace, "h0_dance12_chunk02_lora_probe_frames")
    os.makedirs(frames_dir, exist_ok=True)
    opaque_cells = []
    rgba_cells = []
    records = []
    global_start = chunk_spec["global_action_frame_range_one_based"][0] - 1

    for local_index in range(r52.FRAMES_PER_CHUNK):
        col = local_index % 2
        row = local_index // 2
        cell = image.crop((
            col * legacy.SQUARE_CELL,
            row * legacy.SQUARE_CELL,
            (col + 1) * legacy.SQUARE_CELL,
            (row + 1) * legacy.SQUARE_CELL,
        ))
        # Preserve substantially more of the renderer output for art review/master use.
        # MASTER_CELL is intentionally decoupled from eventual gameplay apparent height.
        cell = cell.resize((MASTER_CELL, MASTER_CELL), Image.Resampling.NEAREST)
        rgba, bg = legacy.alpha_from_neutral(cell)
        action_index = global_start + local_index
        frame_path = os.path.join(frames_dir, f"frame_{action_index:02d}.png")
        rgba.save(frame_path)
        opaque_cells.append(cell)
        rgba_cells.append(rgba)
        records.append({
            "action_frame_index_zero_based": action_index,
            "source_frame_one_based": chunk_spec["selected_one_based"][local_index],
            "duration_ms": durations_ms[action_index],
            "file": frame_path,
            "alpha_background_sample": bg,
            "master_cell_size": [MASTER_CELL, MASTER_CELL],
        })

    opaque = Image.new("RGB", (4 * MASTER_CELL, MASTER_CELL), (96, 96, 96))
    rgba = Image.new("RGBA", (4 * MASTER_CELL, MASTER_CELL), (0, 0, 0, 0))
    gif_frames = []
    gif_durations = []
    for i, (oc, rc) in enumerate(zip(opaque_cells, rgba_cells)):
        opaque.paste(oc, (i * MASTER_CELL, 0))
        rgba.alpha_composite(rc, (i * MASTER_CELL, 0))
        preview = Image.new("RGBA", (MASTER_CELL, MASTER_CELL), (48, 48, 48, 255))
        preview.alpha_composite(rc)
        gif_frames.append(preview.convert("P", palette=Image.Palette.ADAPTIVE))
        gif_durations.append(records[i]["duration_ms"])

    opaque_path = os.path.join(workspace, "h0_dance12_chunk02_pixelart_lora_strip_opaque.png")
    rgba_path = os.path.join(workspace, "h0_dance12_chunk02_pixelart_lora_strip_rgba.png")
    gif_path = os.path.join(workspace, "h0_dance12_chunk02_pixelart_lora_preview.gif")
    opaque.save(opaque_path)
    rgba.save(rgba_path)
    gif_frames[0].save(gif_path, save_all=True, append_images=gif_frames[1:], duration=gif_durations, loop=0, disposal=2)
    return opaque_path, rgba_path, gif_path, records


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
    lora_path = os.path.join(comfy_root, "models", "loras", LORA_NAME)
    for path, label in [(h0_video, "canonical H0 video"), (reference, "canonical Exilada reference"), (lora_path, "Modern Pixel Art LoRA")]:
        if not os.path.isfile(path):
            fail(f"required {label} missing: {path}", "PRECONDITION_FAIL")
    lora_hash = legacy.sha256_file(lora_path)
    if lora_hash.lower() != LORA_SHA256.lower():
        fail(f"LoRA SHA mismatch: expected {LORA_SHA256}, got {lora_hash}", "PRECONDITION_FAIL")

    model_hashes = {
        "diffusion": legacy.verify_model(os.path.join(comfy_root, "models", "diffusion_models", legacy.MODEL), legacy.MODEL_SHA256, legacy.MODEL),
        "clip_l": legacy.verify_model(os.path.join(comfy_root, "models", "text_encoders", legacy.CLIP_L), legacy.CLIP_L_SHA256, legacy.CLIP_L),
        "t5": legacy.verify_model(os.path.join(comfy_root, "models", "text_encoders", legacy.T5), legacy.T5_SHA256, legacy.T5),
        "vae": legacy.verify_model(os.path.join(comfy_root, "models", "vae", legacy.VAE), legacy.VAE_SHA256, legacy.VAE),
    }

    frames = legacy.decode_video(h0_video)
    if len(frames) != legacy.SOURCE_FRAME_COUNT:
        fail(f"canonical H0 source has {len(frames)} decoded frames, expected {legacy.SOURCE_FRAME_COUNT}", "PRECONDITION_FAIL")

    selected = r52.select_full_action_frames(len(frames))
    durations_ms = r52.frame_durations_ms(selected, len(frames), legacy.SOURCE_FPS)
    chunks = r52.make_chunk_specs(selected)
    chunk_spec = chunks[TARGET_CHUNK_INDEX]

    input_dir = os.path.join(comfy_root, "input", "roguelite_kontext")
    os.makedirs(input_dir, exist_ok=True)
    shutil.copy2(reference, os.path.join(input_dir, "exilada_master.png"))

    chunk_input_path = os.path.join(workspace, "h0_dance12_chunk02_lora_input_2x2.png")
    chunk_input_manifest = legacy.make_row_square(frames, chunk_spec, chunk_input_path)
    chunk_input_manifest["semantic_role"] = "Runner53 style-adapter probe only; final action layout remains 12x1; master review scale is independent from gameplay apparent height"
    with open(os.path.join(workspace, "h0_dance12_chunk02_lora_input_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(chunk_input_manifest, fh, ensure_ascii=False, indent=2)

    comfy_input_name = "roguelite_kontext/h0_dance12_chunk02_lora_input_2x2.png"
    shutil.copy2(chunk_input_path, os.path.join(input_dir, os.path.basename(comfy_input_name)))

    base = f"http://127.0.0.1:{args.port}"
    for node_name in legacy.REQUIRED_NODES + ["LoraLoaderModelOnly"]:
        info = legacy.request_json(base + f"/object_info/{node_name}", timeout=60)
        if node_name not in info:
            fail(f"required native ComfyUI node unavailable: {node_name}", "INTEGRATION_FAIL")

    output_prefix = "roguelite_kontext/h0_dance12_chunk02_modern_pixelart_lora"
    prompt_text, prompt = build_prompt_with_lora(chunk_spec, comfy_input_name, output_prefix)
    prompt_path = os.path.join(workspace, "h0_dance12_chunk02_lora_api_prompt.json")
    with open(prompt_path, "w", encoding="utf-8") as fh:
        json.dump(prompt, fh, ensure_ascii=False, indent=2)

    print(
        f"KONTEXT-H0-LORA-PROBE: source_frames={chunk_spec['selected_one_based']} denoise={r52.DENOISE} "
        f"lora={LORA_NAME} strength={LORA_STRENGTH} master_cell={MASTER_CELL}; only one representative chunk will run.",
        flush=True,
    )
    prompt_id, elapsed, generated, history_status = legacy.run_prompt(
        base, prompt, comfy_root, output_prefix, args.timeout_minutes, 2
    )
    full_output = os.path.join(workspace, "h0_dance12_chunk02_pixelart_lora_full.png")
    shutil.copy2(generated, full_output)
    opaque_path, rgba_path, gif_path, records = finalize_probe(full_output, chunk_spec, workspace, durations_ms)

    baseline_chunk = os.path.join(workspace, "h0_dance12_chunk02_kontext_full.png")
    manifest = {
        "gate": "FLUX_KONTEXT_H0_DANCE_CHUNK2_MODERN_PIXELART_LORA_PROBE",
        "status": "INFERENCE_COMPLETE",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Test whether a dedicated FLUX pixel-art style LoRA can strengthen authored pixel-art construction while keeping Runner52 denoise0.45 structure preservation. Preserve a larger 384px-cell review/master output; do not treat it as gameplay apparent height.",
        "source_action": r52.ACTION,
        "selected_source_frames_one_based": chunk_spec["selected_one_based"],
        "baseline_runner52_chunk2": baseline_chunk if os.path.isfile(baseline_chunk) else None,
        "baseline_runner52_chunk2_sha256": legacy.sha256_file(baseline_chunk) if os.path.isfile(baseline_chunk) else None,
        "model": legacy.MODEL,
        "model_sha256": model_hashes["diffusion"],
        "lora": LORA_NAME,
        "lora_sha256": lora_hash,
        "lora_strength": LORA_STRENGTH,
        "steps": r52.STEPS,
        "guidance": r52.GUIDANCE,
        "cfg": r52.CFG,
        "denoise": r52.DENOISE,
        "sampler": r52.SAMPLER,
        "scheduler": r52.SCHEDULER,
        "seed": r52.SEED,
        "master_cell_size": [MASTER_CELL, MASTER_CELL],
        "gameplay_apparent_height": "UNLOCKED_PENDING_VIEWPORT_BENCHMARK",
        "prompt_id": prompt_id,
        "elapsed_seconds": elapsed,
        "prompt_file": prompt_path,
        "prompt_text": prompt_text,
        "full_output": full_output,
        "full_output_sha256": legacy.sha256_file(full_output),
        "strip_opaque": opaque_path,
        "strip_rgba": rgba_path,
        "preview_gif": gif_path,
        "frames": records,
        "history_status": history_status,
        "visual_verdict": "PENDING_HUMAN_REVIEW",
    }
    manifest_path = os.path.join(workspace, "h0_dance12_chunk02_pixelart_lora_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print("KONTEXT-H0-LORA-PROBE: PASS - one-chunk inference complete / visual verdict pending.", flush=True)
    print(f"KONTEXT-H0-LORA-PROBE: full output {full_output}", flush=True)
    print(f"KONTEXT-H0-LORA-PROBE: opaque master strip {opaque_path}", flush=True)
    print(f"KONTEXT-H0-LORA-PROBE: RGBA master strip {rgba_path}", flush=True)
    print(f"KONTEXT-H0-LORA-PROBE: preview {gif_path}", flush=True)
    print(f"KONTEXT-H0-LORA-PROBE: manifest {manifest_path}", flush=True)


if __name__ == "__main__":
    main()
