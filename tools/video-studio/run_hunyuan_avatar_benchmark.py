#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any

WAN_GP_ROOT = Path(r"Z:\AI\WanGP")
OUTPUT_ROOT = Path(r"Z:\AI\VideoStudioRuns\hunyuan-avatar-gates")
REFERENCE_IMAGE = WAN_GP_ROOT / "inputs" / "video_studio" / "hunyuan_avatar_benchmark" / "joao_hunyuan_avatar_ref.png"
SPEECH_AUDIO = WAN_GP_ROOT / "inputs" / "video_studio" / "hunyuan_avatar_benchmark" / "joao_hunyuan_avatar_test_4p5s.wav"
MODEL_FILE = WAN_GP_ROOT / "ckpts" / "hunyuan_video_avatar_720_quanto_bf16_int8.safetensors"
TEXT_ENCODER_FILE = WAN_GP_ROOT / "ckpts" / "llava-llama-3-8b" / "llava-llama-3-8b-v1_1_vlm_quanto_int8.safetensors"
CUSTOM_VAE_FILE = WAN_GP_ROOT / "ckpts" / "hunyuan_video_custom_VAE_fp32.safetensors"
CUSTOM_VAE_CONFIG = WAN_GP_ROOT / "ckpts" / "hunyuan_video_custom_VAE_config.json"

MODEL_NAME = "Hunyuan Video Avatar 720p 13B"
MODEL_ARCH = "hunyuan_avatar"
DEFAULT_RESOLUTION = "720x1280"
DEFAULT_FRAMES = 129
DEFAULT_STEPS = 30
DEFAULT_GUIDANCE = 7.5
DEFAULT_FLOW_SHIFT = 5.0
EXPECTED_FPS = 25

POSITIVE = (
    "A realistic adult man from the reference image speaks naturally toward the camera. "
    "Preserve his facial identity, face proportions, eyeglasses, beard, hairline, apparent age, clothing and body build. "
    "Natural blinking, breathing, subtle head motion and restrained asymmetric conversational gestures. "
    "Stable anatomy, realistic hands, coherent skin texture, photographic detail, stable background and lighting, "
    "no dramatic camera movement and no repetitive presenter-like gestures."
)

NEGATIVE = (
    "low detail, blurry face, unstable identity, deformed face, malformed mouth, malformed teeth, "
    "deformed hands, extra fingers, fused fingers, extra limbs, duplicated body parts, unstable anatomy, "
    "texture crawling, flicker, oversmoothed skin, subtitles, illustration, painting, camera shake"
)


class BenchError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="One direct WanGP HunyuanVideo-Avatar quality benchmark.")
    p.add_argument("--wangp-root", default=str(WAN_GP_ROOT))
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    p.add_argument("--resolution", default=DEFAULT_RESOLUTION)
    p.add_argument("--timeout-minutes", type=int, default=180)
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [jsonable(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(jsonable(value), indent=2, ensure_ascii=False), encoding="utf-8")


def nested_value(record: dict[str, Any], key: str) -> Any:
    if key in record:
        return record.get(key)
    metadata = record.get("metadata")
    if isinstance(metadata, dict):
        return metadata.get(key)
    return None


def validate_resolution(value: str) -> tuple[int, int]:
    try:
        w_text, h_text = value.lower().split("x", 1)
        width, height = int(w_text), int(h_text)
    except Exception as exc:
        raise BenchError(f"Invalid resolution '{value}'. Expected WIDTHxHEIGHT.") from exc
    if width <= 0 or height <= 0 or width % 16 or height % 16:
        raise BenchError("Resolution dimensions must be positive multiples of 16.")
    return width, height


def critical_files(root: Path) -> dict[str, Path]:
    return {
        "runtime_python": root / "env_uv" / "Scripts" / "python.exe",
        "api": root / "shared" / "api.py",
        "reference_image": root / "inputs" / "video_studio" / "hunyuan_avatar_benchmark" / "joao_hunyuan_avatar_ref.png",
        "speech_audio": root / "inputs" / "video_studio" / "hunyuan_avatar_benchmark" / "joao_hunyuan_avatar_test_4p5s.wav",
        "avatar_int8": root / "ckpts" / "hunyuan_video_avatar_720_quanto_bf16_int8.safetensors",
        "llava_int8": root / "ckpts" / "llava-llama-3-8b" / "llava-llama-3-8b-v1_1_vlm_quanto_int8.safetensors",
        "custom_vae": root / "ckpts" / "hunyuan_video_custom_VAE_fp32.safetensors",
        "custom_vae_config": root / "ckpts" / "hunyuan_video_custom_VAE_config.json",
    }


def main() -> int:
    args = parse_args()
    root = Path(args.wangp_root).resolve()
    validate_resolution(args.resolution)
    if args.steps < 1:
        raise BenchError("Steps must be >= 1.")
    if args.timeout_minutes < 1:
        raise BenchError("Timeout must be >= 1 minute.")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_ROOT / stamp
    run_dir.mkdir(parents=True, exist_ok=False)
    runner_log = run_dir / "runner.log"

    def log(message: str = "") -> None:
        print(message, flush=True)
        with runner_log.open("a", encoding="utf-8") as handle:
            handle.write(message + "\n")

    log("HUNYUAN-AVATAR-BENCHMARK-01")
    log("============================")
    log(f"WanGP root: {root}")
    log(f"Run dir: {run_dir}")
    log(f"Resolution: {args.resolution}")
    log(f"Requested frames: {DEFAULT_FRAMES}")
    log(f"Expected native FPS: {EXPECTED_FPS}")
    log(f"Steps: {args.steps}")
    log(f"Seed: {args.seed}")
    log(f"Timeout: {args.timeout_minutes} min")
    log(f"Dry run: {args.dry_run}")
    log("")

    files = critical_files(root)
    missing = [f"{name}: {path}" for name, path in files.items() if not path.is_file() or path.stat().st_size <= 0]
    if missing:
        raise BenchError("Critical benchmark files are missing:\n" + "\n".join(missing))

    # Keep any incidental Hugging Face/Xet cache traffic off the model volume.
    cache_root = Path(os.environ.get("LOCALAPPDATA", str(root))) / "VideoStudio" / "huggingface"
    os.environ.setdefault("HF_HOME", str(cache_root))
    os.environ.setdefault("HF_HUB_CACHE", str(cache_root / "hub"))
    os.environ.setdefault("HF_XET_CACHE", str(cache_root / "xet"))

    # WanGP's supported Python API lives in shared/api.py. Import it from the actual
    # installed runtime rather than reimplementing internal Gradio or model calls.
    sys.path.insert(0, str(root))
    old_cwd = Path.cwd()
    os.chdir(root)
    try:
        from shared.api import init  # type: ignore

        log("Initializing WanGP Python API with profile 4 and SDPA; TeaCache is disabled in task settings...")
        session = init(
            root=root,
            output_dir=run_dir,
            cli_args=["--profile", "4", "--attention", "sdpa", "--verbose", "2"],
            console_output=True,
            console_isatty=True,
        )

        required_methods = [
            "list_model_metadata",
            "get_default_settings",
            "get_model_schema",
            "get_model_availability",
            "submit_task",
        ]
        absent_methods = [name for name in required_methods if not hasattr(session, name)]
        if absent_methods:
            raise BenchError("Installed WanGP API is too old; missing: " + ", ".join(absent_methods))

        candidates = session.list_model_metadata(query="Hunyuan Video Avatar", include_availability=True)
        write_json(run_dir / "model_search.json", candidates)
        exact = [
            item for item in candidates
            if str(nested_value(item, "name") or "").strip() == MODEL_NAME
            or str(nested_value(item, "base_model_type") or "").strip() == MODEL_ARCH
            or str(nested_value(item, "architecture") or "").strip() == MODEL_ARCH
        ]
        if len(exact) != 1:
            raise BenchError(f"Expected exactly one {MODEL_NAME!r} candidate; found {len(exact)}. See model_search.json.")

        model = exact[0]
        model_type = str(nested_value(model, "model_type") or "").strip()
        if not model_type:
            raise BenchError("WanGP model discovery did not expose model_type.")

        defaults = session.get_default_settings(model_type)
        schema = session.get_model_schema(model_type)
        availability = session.get_model_availability(model_type)
        write_json(run_dir / "model_metadata.json", model)
        write_json(run_dir / "model_defaults.json", defaults)
        write_json(run_dir / "model_schema.json", schema)
        write_json(run_dir / "model_availability.json", availability)

        availability_status = ""
        if isinstance(availability, dict):
            availability_status = str(availability.get("status") or availability.get("availability") or "").lower()
        if availability_status == "missing":
            raise BenchError("WanGP reports the Hunyuan Avatar payload as missing. See model_availability.json.")

        runtime_video_mode = str(defaults.get("video_prompt_type") or "")
        runtime_audio_mode = str(defaults.get("audio_prompt_type") or "")
        if "I" not in runtime_video_mode:
            raise BenchError(f"Unexpected Hunyuan Avatar default video_prompt_type={runtime_video_mode!r}; refusing to invent a reference mode.")
        if "A" not in runtime_audio_mode:
            raise BenchError(f"Unexpected Hunyuan Avatar default audio_prompt_type={runtime_audio_mode!r}; refusing to invent an audio mode.")

        log("Runtime/model discovery: PASS")
        log(f"Model type: {model_type}")
        log(f"Availability: {availability_status or 'reported without simple status'}")
        log(f"Runtime default reference mode: {runtime_video_mode}")
        log(f"Runtime default audio mode: {runtime_audio_mode}")
        log(f"Runtime default frames: {defaults.get('video_length')}")
        log(f"Runtime default steps: {defaults.get('num_inference_steps')}")
        log(f"Runtime default CFG: {defaults.get('guidance_scale')}")
        log(f"Runtime default flow shift: {defaults.get('flow_shift')}")
        log("")

        settings = dict(defaults)
        settings.update(
            {
                "model_type": model_type,
                "prompt": POSITIVE,
                "negative_prompt": NEGATIVE,
                "image_mode": 0,
                "resolution": args.resolution,
                "video_length": DEFAULT_FRAMES,
                "num_inference_steps": int(args.steps),
                "seed": int(args.seed),
                "guidance_scale": DEFAULT_GUIDANCE,
                "flow_shift": DEFAULT_FLOW_SHIFT,
                "video_prompt_type": runtime_video_mode,
                "image_refs": [str(files["reference_image"])],
                "remove_background_images_ref": 0,
                "audio_prompt_type": runtime_audio_mode,
                "audio_guide": str(files["speech_audio"]),
                "repeat_generation": 1,
                "skip_steps_cache_type": "",
                "temporal_upsampling": "",
                "spatial_upsampling": "",
                "film_grain_intensity": 0,
                "postprocess_audio": "",
                "force_fps": "",
            }
        )
        write_json(run_dir / "settings.json", settings)

        preflight = {
            "schema": "HUNYUAN-AVATAR-BENCHMARK-01",
            "state": "PREFLIGHT_PASS" if not args.dry_run else "DRY_RUN_PASS",
            "created": datetime.now().isoformat(timespec="seconds"),
            "wangp_root": str(root),
            "run_dir": str(run_dir),
            "model_name": MODEL_NAME,
            "model_type": model_type,
            "model_file": str(files["avatar_int8"]),
            "text_encoder_file": str(files["llava_int8"]),
            "reference_image": str(files["reference_image"]),
            "speech_audio": str(files["speech_audio"]),
            "resolution": args.resolution,
            "video_length": DEFAULT_FRAMES,
            "expected_fps": EXPECTED_FPS,
            "steps": args.steps,
            "seed": args.seed,
            "guidance_scale": DEFAULT_GUIDANCE,
            "flow_shift": DEFAULT_FLOW_SHIFT,
            "attention": "sdpa",
            "profile": 4,
            "teacache": "disabled_by_skip_steps_cache_type",
            "postprocessing": False,
            "availability": availability,
        }
        write_json(run_dir / "manifest.json", preflight)

        if args.dry_run:
            log("DRY RUN PASS — no generation submitted.")
            log(f"Evidence: {run_dir}")
            return 0

        log("Submitting one direct Hunyuan Avatar generation...")
        started = time.monotonic()
        job = session.submit_task(settings)
        timeout_fired = threading.Event()

        def cancel_on_timeout() -> None:
            try:
                if not getattr(job, "done", False):
                    timeout_fired.set()
                    log(f"Timeout reached after {args.timeout_minutes} min; requesting WanGP cancellation.")
                    job.cancel()
            except Exception as exc:
                log(f"Timeout cancellation raised: {exc}")

        timer = threading.Timer(args.timeout_minutes * 60, cancel_on_timeout)
        timer.daemon = True
        timer.start()
        try:
            try:
                for event in job.events.iter(timeout=0.5):
                    kind = getattr(event, "kind", "")
                    data = getattr(event, "data", None)
                    if kind == "progress" and data is not None:
                        phase = getattr(data, "phase", "") or getattr(data, "status", "")
                        progress = getattr(data, "progress", None)
                        current = getattr(data, "current_step", None)
                        total = getattr(data, "total_steps", None)
                        log(f"PROGRESS phase={phase} progress={progress} step={current}/{total}")
                    elif kind == "stream" and data is not None:
                        text = str(getattr(data, "text", data)).rstrip()
                        if text:
                            log(f"WANGP {text}")
            except Exception as event_exc:
                log(f"Event stream ended with: {event_exc}")

            result = job.result()
        finally:
            timer.cancel()

        elapsed = time.monotonic() - started
        if timeout_fired.is_set():
            raise BenchError(f"Generation exceeded the {args.timeout_minutes}-minute benchmark timeout and was cancelled.")

        result_record = {
            "success": bool(getattr(result, "success", False)),
            "generated_files": [str(p) for p in (getattr(result, "generated_files", None) or [])],
            "errors": [str(getattr(e, "message", e)) for e in (getattr(result, "errors", None) or [])],
            "elapsed_seconds": elapsed,
        }
        write_json(run_dir / "result.json", result_record)

        if not result_record["success"]:
            raise BenchError("WanGP generation failed: " + " | ".join(result_record["errors"] or ["unknown error"]))

        generated = [Path(p) for p in result_record["generated_files"]]
        videos = [p for p in generated if p.suffix.lower() in {".mp4", ".mkv", ".mov", ".webm"} and p.is_file()]
        if not videos:
            raise BenchError("WanGP reported success but no generated video file was found. See result.json.")

        source_video = max(videos, key=lambda p: p.stat().st_mtime)
        final_video = run_dir / f"hunyuan_avatar_{args.resolution.replace('x', 'x')}_{args.steps}step_seed{args.seed}{source_video.suffix.lower()}"
        if source_video.resolve() != final_video.resolve():
            shutil.copy2(source_video, final_video)

        manifest = dict(preflight)
        manifest.update(
            {
                "state": "RENDER_COMPLETE",
                "completed": datetime.now().isoformat(timespec="seconds"),
                "elapsed_seconds": elapsed,
                "elapsed_minutes": elapsed / 60.0,
                "generated_files": result_record["generated_files"],
                "final_video": str(final_video),
            }
        )
        write_json(run_dir / "manifest.json", manifest)

        log("")
        log("RESULT")
        log("======")
        log("HUNYUAN AVATAR DIRECT RENDER COMPLETE")
        log(f"Elapsed: {elapsed:.1f} s ({elapsed / 60.0:.2f} min)")
        log(f"Final video: {final_video}")
        log(f"Evidence: {run_dir}")
        log("Quality verdict is NOT automatic; inspect the video against the Wan 10-step baseline.")
        return 0
    finally:
        os.chdir(old_cwd)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BenchError as exc:
        print(f"BENCHMARK FAILED: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(2)
    except KeyboardInterrupt:
        print("BENCHMARK INTERRUPTED", file=sys.stderr, flush=True)
        raise SystemExit(130)
