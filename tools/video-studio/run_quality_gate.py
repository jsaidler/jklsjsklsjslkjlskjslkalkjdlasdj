#!/usr/bin/env python3
"""Controlled single-shot visual quality benchmark for Local Video Studio.

This runner deliberately keeps identity references, voice reference, dialogue,
scenario, framing and seed fixed while changing only the H3 sampling preset.
It exists to answer a quality question, not to auto-promote any preset.

Backend preset key `production` is a legacy name for the fast Turbo4 baseline;
it is NOT a production-quality verdict.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import video_studio as vs

DEFAULT_TEXT = (
    "Eu desenvolvo este processo de positivo direto em filme de raio-X há quase oito anos."
)

DEFAULT_SCENARIO = (
    "um estúdio de fotografia analógica sóbrio e realista, claramente diferente do ambiente das "
    "referências de identidade; paredes escuras foscas, bancada de madeira organizada, uma câmera "
    "de grande formato ao fundo e iluminação lateral suave e coerente"
)

DEFAULT_APPEARANCE = "camiseta preta simples, sem estampas"

LABELS = {
    "production": "Q0 Turbo4 high-resolution functional baseline (NOT production-approved)",
    "quality": "Q1 Base20 quality candidate",
    "max": "Q2 Base50 maximum H3 quality candidate",
    "draft": "Draft only",
}

TIMEOUT_MINUTES = {
    "draft": 90,
    "production": 120,
    "quality": 300,
    "max": 600,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_presets(raw: str) -> list[str]:
    values = [x.strip() for x in raw.split(",") if x.strip()]
    if not values:
        raise vs.StudioError("Nenhum preset informado.")
    invalid = [x for x in values if x not in vs.PRESETS]
    if invalid:
        raise vs.StudioError("Preset invalido: " + ", ".join(invalid))
    # Preserve caller order while removing duplicates.
    out: list[str] = []
    for value in values:
        if value not in out:
            out.append(value)
    return out


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Controlled MiniMax H3 visual-quality benchmark for Local Video Studio"
    )
    parser.add_argument(
        "--config",
        default=str(Path(__file__).with_name("config.json")),
        help="Video Studio config.json",
    )
    parser.add_argument(
        "--presets",
        default="production,quality",
        help="Comma-separated preset keys. Recommended first run: production,quality. Then max if warranted.",
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--text", default=DEFAULT_TEXT)
    parser.add_argument("--scenario", default=DEFAULT_SCENARIO)
    parser.add_argument("--appearance", default=DEFAULT_APPEARANCE)
    parser.add_argument(
        "--framing",
        choices=sorted(vs.FRAMING),
        default="medium",
    )
    args = parser.parse_args()

    config = vs.load_config(Path(args.config))
    presets = parse_presets(args.presets)

    chunks = vs.split_dialogue(args.text)
    if len(chunks) != 1:
        raise vs.StudioError(
            "O quality gate exige exatamente um clip curto. Reduza --text para uma unica fala."
        )
    dialogue = chunks[0]
    duration = min(
        vs.MAX_CLIP_SECONDS,
        max(4.5, vs.estimated_dialogue_seconds(dialogue)),
    )
    duration = vs.aligned_seconds(duration)

    print("VIDEO-STUDIO-QUALITY-01")
    print("=======================")
    print("Status: PRODUCTION QUALITY NOT APPROVED")
    print("This run does not auto-promote any preset.")
    print()
    print("Presets:", ", ".join(f"{p} [{LABELS.get(p, p)}]" for p in presets))
    print(f"Seed: {args.seed}")
    print(f"Target duration: {duration:.3f}s")
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
    run_dir = config.output_root / "quality-gates" / run_id
    evidence_dir = run_dir / "evidence"
    outputs_dir = run_dir / "outputs"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    request = {
        "gate": "VIDEO-STUDIO-QUALITY-01",
        "classification_before_run": "FUNCTIONAL_PASS__PRODUCTION_QUALITY_NOT_APPROVED",
        "created_utc": utc_now(),
        "presets": presets,
        "seed": args.seed,
        "dialogue": dialogue,
        "scenario": args.scenario,
        "appearance": args.appearance,
        "framing": args.framing,
        "duration_seconds": duration,
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

    client = vs.ComfyClient(config)
    records: list[dict[str, Any]] = []
    had_error = False

    for index, preset in enumerate(presets, start=1):
        label = LABELS.get(preset, preset)
        print()
        print(f"[{index}/{len(presets)}] {label}")
        print("-" * 72)

        output_prefix = f"video/video_studio_quality_gate/{run_id}/{preset}"
        graph = vs.build_graph(
            config=config,
            image_inputs=image_inputs,
            voice_input=voice_input,
            prompt=prompt,
            preset_name=preset,
            duration_seconds=duration,
            seed=args.seed,
            output_prefix=output_prefix,
        )
        graph_path = evidence_dir / f"{preset}_api_prompt.json"
        write_json(graph_path, graph)

        started = time.time()
        record: dict[str, Any] = {
            "preset_key": preset,
            "label": label,
            "preset_config": vs.PRESETS[preset],
            "seed": args.seed,
            "prompt_file": str(evidence_dir / "compiled_prompt.txt"),
            "api_graph": str(graph_path),
            "status": "RUNNING",
            "human_visual_verdict": "PENDING",
        }

        try:
            prompt_id = client.submit(graph)
            record["prompt_id"] = prompt_id
            print(f"prompt_id={prompt_id}", flush=True)
            client.wait(
                prompt_id,
                timeout_minutes=TIMEOUT_MINUTES.get(preset, 300),
                progress_cb=lambda msg: print(msg, flush=True),
            )
            source = vs.newest_output(config.comfy_root, output_prefix, started)
            if source is None:
                raise vs.StudioError(
                    f"ComfyUI terminou {preset}, mas o MP4 correspondente nao foi encontrado."
                )
            target = outputs_dir / f"{index:02d}_{preset}.mp4"
            shutil.copy2(source, target)
            record.update(
                {
                    "status": "INFERENCE_COMPLETE__PENDING_HUMAN_VISUAL_REVIEW",
                    "elapsed_seconds": round(time.time() - started, 2),
                    "comfy_output": str(source),
                    "output": str(target),
                    "output_bytes": target.stat().st_size,
                    "sha256": vs.sha256_file(target),
                }
            )
            print(f"OUTPUT: {target}")
            print(f"elapsed={record['elapsed_seconds']}s")
        except Exception as exc:
            had_error = True
            record.update(
                {
                    "status": "EXECUTION_FAIL",
                    "elapsed_seconds": round(time.time() - started, 2),
                    "error": str(exc),
                }
            )
            print(f"ERROR: {exc}", file=sys.stderr, flush=True)

        records.append(record)
        write_json(run_dir / "quality_gate_manifest.partial.json", {**request, "results": records})

    manifest = {
        **request,
        "results": records,
        "acceptance_document": "docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md",
        "automatic_verdict": None,
        "final_human_verdict": "PENDING",
        "note": (
            "Inference completion is not a quality pass. Review the MP4s side-by-side at full size and "
            "classify visible defects before promoting any preset."
        ),
    }
    write_json(run_dir / "quality_gate_manifest.json", manifest)

    print()
    print("QUALITY GATE OUTPUT")
    print("===================")
    print(run_dir)
    for record in records:
        print(f"- {record['preset_key']}: {record.get('output', record['status'])}")
    print()
    print("NO PRESET HAS BEEN AUTO-APPROVED FOR PRODUCTION.")

    return 2 if had_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
