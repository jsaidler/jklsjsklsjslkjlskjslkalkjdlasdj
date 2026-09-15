#!/usr/bin/env python3
"""Codec-isolation benchmark for Local Video Studio.

Runs ONE H3 inference and saves the exact same decoded frame/audio stream twice:

1. current/default H.264 save path;
2. H.264 CRF 14.

This isolates output-encoding loss from H3/VAE/generative softness. No preset is
promoted automatically.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOOL_ROOT = Path(__file__).resolve().parent
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

import video_studio as vs  # noqa: E402

DEFAULT_TEXT = "Eu desenvolvo este processo de positivo direto em filme de raio-X há quase oito anos."
DEFAULT_SCENARIO = (
    "um estúdio de fotografia analógica sóbrio e realista, claramente diferente do ambiente das "
    "referências de identidade; paredes escuras foscas, bancada de madeira organizada, uma câmera "
    "de grande formato ao fundo e iluminação lateral suave e coerente"
)
DEFAULT_APPEARANCE = "camiseta preta simples, sem estampas"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def find_ffprobe(config: vs.Config) -> str | None:
    ffmpeg = vs.ffmpeg_executable(config)
    ffmpeg_path = Path(ffmpeg)
    if ffmpeg_path.is_file():
        candidate = ffmpeg_path.with_name("ffprobe.exe" if sys.platform.startswith("win") else "ffprobe")
        if candidate.is_file():
            return str(candidate)
    return shutil.which("ffprobe")


def probe_video(ffprobe: str | None, path: Path) -> dict[str, Any]:
    if not ffprobe:
        return {}
    completed = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if completed.returncode != 0:
        return {"ffprobe_error": completed.stdout[-4000:]}
    try:
        return json.loads(completed.stdout)
    except Exception:
        return {"ffprobe_error": "invalid json", "raw": completed.stdout[-4000:]}


def locate(config: vs.Config, prefix: str, started: float) -> Path:
    found = vs.newest_output(config.comfy_root, prefix, started)
    if found is None:
        raise vs.StudioError(f"Output não localizado para prefixo {prefix}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description="VIDEO-STUDIO-RESOLUTION-01 codec isolation")
    parser.add_argument("--config", default=str(TOOL_ROOT / "config.json"))
    parser.add_argument("--preset", choices=sorted(vs.PRESETS), default="quality")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--text", default=DEFAULT_TEXT)
    parser.add_argument("--scenario", default=DEFAULT_SCENARIO)
    parser.add_argument("--appearance", default=DEFAULT_APPEARANCE)
    parser.add_argument("--framing", choices=sorted(vs.FRAMING), default="medium")
    parser.add_argument("--crf", type=float, default=14.0)
    args = parser.parse_args()

    config = vs.load_config(Path(args.config))
    chunks = vs.split_dialogue(args.text)
    if len(chunks) != 1:
        raise vs.StudioError("O resolution gate exige uma única fala curta.")

    dialogue = chunks[0]
    duration = min(vs.MAX_CLIP_SECONDS, max(4.5, vs.estimated_dialogue_seconds(dialogue)))
    duration = vs.aligned_seconds(duration)

    print("VIDEO-STUDIO-RESOLUTION-01")
    print("==========================")
    print("Purpose: isolate MP4 encoder loss from H3/VAE softness")
    print(f"Preset: {args.preset}")
    print(f"Seed: {args.seed}")
    print(f"Target duration: {duration:.3f}s")
    print(f"High-quality branch: H.264 CRF {args.crf:g}")
    print()

    report = vs.preflight(config, start_comfy=True)
    if not report["ok"]:
        print(json.dumps(report, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    image_inputs, voice_input = vs.sync_profile(config)
    prompt = vs.build_h3_prompt(
        config,
        dialogue,
        args.scenario,
        args.appearance,
        args.framing,
    )

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = config.output_root / "resolution-gates" / run_id
    evidence_dir = run_dir / "evidence"
    outputs_dir = run_dir / "outputs"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    prefix_auto = f"video/video_studio_resolution_gate/{run_id}/01_auto"
    prefix_crf = f"video/video_studio_resolution_gate/{run_id}/02_crf14"

    graph = vs.build_graph(
        config=config,
        image_inputs=image_inputs,
        voice_input=voice_input,
        prompt=prompt,
        preset_name=args.preset,
        duration_seconds=duration,
        seed=args.seed,
        output_prefix=prefix_auto,
    )

    # Branch 1: preserve the current/default SaveVideo behavior for an exact codec baseline.
    graph["63"]["inputs"]["filename_prefix"] = prefix_auto

    # Branch 2: same CreateVideo object / same decoded frames / explicit high-quality H.264.
    graph["64"] = {
        "inputs": {
            "filename_prefix": prefix_crf,
            "format": "mp4",
            "codec": "h264",
            "codec.encoding": "re-encode",
            "codec.encoding.crf": float(args.crf),
            "video": ["62", 0],
        },
        "class_type": "SaveVideo",
        "_meta": {"title": f"Same decoded frames - H264 CRF {args.crf:g}"},
    }

    request = {
        "gate": "VIDEO-STUDIO-RESOLUTION-01",
        "created_utc": utc_now(),
        "preset": args.preset,
        "seed": args.seed,
        "duration_seconds": duration,
        "dialogue": dialogue,
        "scenario": args.scenario,
        "appearance": args.appearance,
        "framing": args.framing,
        "crf": args.crf,
        "identity_references": [
            {"path": str(p), "sha256": vs.sha256_file(p)} for p in config.identity_images
        ],
        "voice_reference": {
            "path": str(config.voice_reference),
            "sha256": vs.sha256_file(config.voice_reference),
        },
    }
    write_json(run_dir / "request.json", request)
    (evidence_dir / "compiled_prompt.txt").write_text(prompt, encoding="utf-8")
    write_json(evidence_dir / "api_prompt_dual_encode.json", graph)

    client = vs.ComfyClient(config)
    started = time.time()
    prompt_id = client.submit(graph)
    print(f"prompt_id={prompt_id}", flush=True)
    client.wait(
        prompt_id,
        timeout_minutes=300 if args.preset in ("quality", "max") else 120,
        progress_cb=lambda msg: print(msg, flush=True),
    )

    source_auto = locate(config, prefix_auto, started)
    source_crf = locate(config, prefix_crf, started)

    target_auto = outputs_dir / "01_same_frames_auto_h264.mp4"
    target_crf = outputs_dir / f"02_same_frames_h264_crf{int(args.crf):02d}.mp4"
    shutil.copy2(source_auto, target_auto)
    shutil.copy2(source_crf, target_crf)

    ffprobe = find_ffprobe(config)
    results = []
    for label, path in (("auto_h264", target_auto), (f"h264_crf_{args.crf:g}", target_crf)):
        results.append(
            {
                "label": label,
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": vs.sha256_file(path),
                "probe": probe_video(ffprobe, path),
            }
        )

    manifest = {
        **request,
        "prompt_id": prompt_id,
        "elapsed_seconds": round(time.time() - started, 2),
        "results": results,
        "human_verdict": "PENDING",
        "decision_rule": (
            "If CRF14 is materially cleaner, fix Studio output encoding before further model comparisons. "
            "If both look essentially identical, effective-detail softness is upstream of SaveVideo."
        ),
    }
    write_json(run_dir / "resolution_gate_manifest.json", manifest)

    print()
    print("RESOLUTION GATE OUTPUT")
    print("======================")
    print(run_dir)
    print(f"- AUTO : {target_auto} ({target_auto.stat().st_size / 1024 / 1024:.2f} MiB)")
    print(f"- CRF14: {target_crf} ({target_crf.stat().st_size / 1024 / 1024:.2f} MiB)")
    print()
    print("Both files come from the SAME decoded H3 frames. Compare them at 100% zoom.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
