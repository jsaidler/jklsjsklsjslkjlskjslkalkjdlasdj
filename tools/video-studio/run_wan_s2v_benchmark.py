#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

WAN_ROOT = Path(r"Z:\AI\WanAnimate2")
OUTPUT_ROOT = Path(r"Z:\AI\VideoStudioRuns\wan-s2v-gates")
PORTABLE_CANDIDATES = [
    Path(r"Z:\AI\Flux2Klein\ComfyUI_windows_portable"),
    Path(r"Z:\AI\MiniMaxH3\ComfyUI_windows_portable"),
    Path(r"Z:\AI\QwenImageEdit\ComfyUI_windows_portable"),
]

DIFFUSION = "wan2.2_s2v_14B_fp8_scaled.safetensors"
TEXT_ENCODER = "umt5_xxl_fp16.safetensors"
VAE = "Wan2_1_VAE_bf16.safetensors"
AUDIO_ENCODER = "wav2vec2_large_english_fp16.safetensors"

WIDTH = 480
HEIGHT = 832
LENGTH = 77
FPS = 16
STEPS = 20
CFG = 6.0
SAMPLER = "uni_pc"
SCHEDULER = "simple"
SHIFT = 8.0

POSITIVE = (
    "A realistic adult man from the reference image speaks naturally toward the camera. "
    "Preserve his facial identity, face proportions, eyeglasses, beard, hairline, apparent age and body build. "
    "Natural blinking, breathing, subtle head motion and restrained conversational hand gestures. "
    "Stable anatomy, realistic hands, coherent skin texture, photographic detail, soft neutral lighting, "
    "no dramatic camera movement, no presenter-like repetitive gestures."
)

NEGATIVE = (
    "overexposed, oversaturated, static, blurred details, subtitles, illustration, painting, low quality, "
    "jpeg artifacts, ugly, deformed, extra fingers, malformed hands, malformed face, fused fingers, "
    "extra limbs, frozen frame, cluttered background, duplicated body parts, unstable anatomy"
)

REQUIRED_NODES = [
    "UNETLoader",
    "ModelSamplingSD3",
    "CLIPLoader",
    "CLIPTextEncode",
    "VAELoader",
    "AudioEncoderLoader",
    "LoadAudio",
    "AudioEncoderEncode",
    "LoadImage",
    "WanSoundImageToVideo",
    "KSampler",
    "LatentCut",
    "LatentConcat",
    "VAEDecode",
    "ImageFromBatch",
    "CreateVideo",
    "SaveVideo",
]


class BenchError(RuntimeError):
    pass


def request_json(url: str, payload: Any | None = None, timeout: float = 120.0) -> Any:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise BenchError(f"HTTP {exc.code} from {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise BenchError(f"Could not reach {url}: {exc}") from exc
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def find_portable() -> Path:
    for root in PORTABLE_CANDIDATES:
        if (root / "python_embeded" / "python.exe").is_file() and (root / "ComfyUI" / "main.py").is_file():
            return root
    raise BenchError("No usable current ComfyUI portable runtime was found in the protected AI roots.")


def write_extra_model_paths() -> Path:
    path = WAN_ROOT / "wan_s2v_extra_model_paths.yaml"
    text = (
        "wan_s2v:\n"
        "    base_path: \"Z:/AI/WanAnimate2\"\n"
        "    diffusion_models: models/diffusion_models/\n"
        "    text_encoders: models/text_encoders/\n"
        "    vae: models/vae/\n"
        "    audio_encoders: models/audio_encoders/\n"
    )
    path.write_text(text, encoding="utf-8")
    return path


def ping(base_url: str, timeout: float = 2.0) -> bool:
    try:
        request_json(base_url + "/system_stats", timeout=timeout)
        return True
    except Exception:
        return False


def copy_inputs(comfy_root: Path) -> tuple[str, str]:
    source_dir = WAN_ROOT / "input" / "video_studio" / "wan_s2v_benchmark"
    src_image = source_dir / "joao_wan_s2v_ref.png"
    src_audio = source_dir / "joao_wan_s2v_test_4p5s.wav"
    if not src_image.is_file():
        raise BenchError(f"Prepared reference image missing: {src_image}")
    if not src_audio.is_file():
        raise BenchError(f"Prepared speech audio missing: {src_audio}")

    input_dir = comfy_root / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    image_name = "wan_s2v_joao_ref.png"
    audio_name = "wan_s2v_joao_audio.wav"
    shutil.copy2(src_image, input_dir / image_name)
    shutil.copy2(src_audio, input_dir / audio_name)
    return image_name, audio_name


def start_comfy(portable: Path, port: int, extra_paths: Path, server_log: Path, lowvram: bool) -> tuple[subprocess.Popen | None, Any]:
    base_url = f"http://127.0.0.1:{port}"
    if ping(base_url):
        return None, None

    python = portable / "python_embeded" / "python.exe"
    main_py = portable / "ComfyUI" / "main.py"
    cmd = [
        str(python),
        "-s",
        str(main_py),
        "--windows-standalone-build",
        "--listen",
        "127.0.0.1",
        "--port",
        str(port),
        "--extra-model-paths-config",
        str(extra_paths),
    ]
    if lowvram:
        cmd.append("--lowvram")

    log_handle = server_log.open("w", encoding="utf-8", errors="replace")
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
    proc = subprocess.Popen(
        cmd,
        cwd=str(portable),
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        creationflags=creationflags,
    )

    deadline = time.time() + 300
    while time.time() < deadline:
        if proc.poll() is not None:
            log_handle.flush()
            raise BenchError(f"ComfyUI exited during startup. See: {server_log}")
        if ping(base_url, timeout=3):
            return proc, log_handle
        time.sleep(2)

    raise BenchError(f"ComfyUI did not answer on port {port} within 300 seconds. See: {server_log}")


def node_info(base_url: str, name: str) -> dict[str, Any]:
    info = request_json(base_url + f"/object_info/{name}", timeout=60)
    if name not in info:
        raise BenchError(f"Required node missing: {name}")
    return info[name]


def combo_values(info: dict[str, Any], field: str) -> list[str]:
    input_block = info.get("input") or {}
    for section in ("required", "optional"):
        spec = (input_block.get(section) or {}).get(field)
        if isinstance(spec, (list, tuple)) and spec:
            first = spec[0]
            if isinstance(first, (list, tuple)):
                return [str(x) for x in first]
    return []


def validate_runtime(base_url: str) -> None:
    infos: dict[str, dict[str, Any]] = {}
    for name in REQUIRED_NODES:
        infos[name] = node_info(base_url, name)

    checks = [
        ("UNETLoader", "unet_name", DIFFUSION),
        ("CLIPLoader", "clip_name", TEXT_ENCODER),
        ("VAELoader", "vae_name", VAE),
        ("AudioEncoderLoader", "audio_encoder_name", AUDIO_ENCODER),
    ]
    for node, field, expected in checks:
        values = combo_values(infos[node], field)
        if values and expected not in values:
            raise BenchError(f"{node} cannot see required model {expected}. Visible count: {len(values)}")


def build_graph(image_name: str, audio_name: str, seed: int, prefix: str) -> dict[str, Any]:
    return {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {"unet_name": DIFFUSION, "weight_dtype": "default"},
        },
        "2": {
            "class_type": "ModelSamplingSD3",
            "inputs": {"model": ["1", 0], "shift": SHIFT},
        },
        "3": {
            "class_type": "CLIPLoader",
            "inputs": {"clip_name": TEXT_ENCODER, "type": "wan", "device": "default"},
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": POSITIVE, "clip": ["3", 0]},
        },
        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": NEGATIVE, "clip": ["3", 0]},
        },
        "6": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": VAE},
        },
        "7": {
            "class_type": "AudioEncoderLoader",
            "inputs": {"audio_encoder_name": AUDIO_ENCODER},
        },
        "8": {
            "class_type": "LoadAudio",
            "inputs": {"audio": audio_name},
        },
        "9": {
            "class_type": "AudioEncoderEncode",
            "inputs": {"audio_encoder": ["7", 0], "audio": ["8", 0]},
        },
        "10": {
            "class_type": "LoadImage",
            "inputs": {"image": image_name},
        },
        "11": {
            "class_type": "WanSoundImageToVideo",
            "inputs": {
                "positive": ["4", 0],
                "negative": ["5", 0],
                "vae": ["6", 0],
                "width": WIDTH,
                "height": HEIGHT,
                "length": LENGTH,
                "batch_size": 1,
                "audio_encoder_output": ["9", 0],
                "ref_image": ["10", 0],
            },
        },
        "12": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["2", 0],
                "positive": ["11", 0],
                "negative": ["11", 1],
                "latent_image": ["11", 2],
                "seed": int(seed),
                "steps": STEPS,
                "cfg": CFG,
                "sampler_name": SAMPLER,
                "scheduler": SCHEDULER,
                "denoise": 1.0,
            },
        },
        "13": {
            "class_type": "LatentCut",
            "inputs": {"samples": ["12", 0], "dim": "t", "index": 0, "amount": 1},
        },
        "14": {
            "class_type": "LatentConcat",
            "inputs": {"samples1": ["13", 0], "samples2": ["12", 0], "dim": "t"},
        },
        "15": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["14", 0], "vae": ["6", 0]},
        },
        "16": {
            "class_type": "ImageFromBatch",
            "inputs": {"image": ["15", 0], "batch_index": 3, "length": LENGTH},
        },
        "17": {
            "class_type": "CreateVideo",
            "inputs": {"images": ["16", 0], "fps": float(FPS), "audio": ["8", 0]},
        },
        "18": {
            "class_type": "SaveVideo",
            "inputs": {
                "video": ["17", 0],
                "filename_prefix": prefix,
                "format": {
                    "format": "mp4",
                    "codec": {
                        "codec": "h264",
                        "encoding": {"encoding": "re-encode", "crf": 14.0},
                    },
                },
            },
        },
    }


def submit(base_url: str, graph: dict[str, Any]) -> str:
    result = request_json(base_url + "/prompt", {"prompt": graph}, timeout=180)
    prompt_id = result.get("prompt_id") if isinstance(result, dict) else None
    if not prompt_id:
        raise BenchError(f"ComfyUI did not return prompt_id: {result}")
    return str(prompt_id)


def wait_for_prompt(base_url: str, prompt_id: str, timeout_minutes: int) -> dict[str, Any]:
    started = time.time()
    deadline = started + timeout_minutes * 60
    next_report = started + 20
    while time.time() < deadline:
        history = request_json(base_url + f"/history/{prompt_id}", timeout=120)
        item = history.get(prompt_id) if isinstance(history, dict) else None
        if item:
            status = item.get("status") or {}
            for message in status.get("messages") or []:
                if isinstance(message, (list, tuple)) and message and message[0] == "execution_error":
                    raise BenchError(f"ComfyUI execution_error: {message}")
            if status.get("completed") is True:
                return item
        now = time.time()
        if now >= next_report:
            print(f"Inference active: {int(now - started)} s", flush=True)
            next_report = now + 20
        time.sleep(3)
    raise BenchError(f"Timeout after {timeout_minutes} minutes waiting for prompt {prompt_id}")


def find_output(comfy_root: Path, prefix_leaf: str, started_at: float) -> Path:
    output = comfy_root / "output"
    candidates = []
    if output.is_dir():
        for path in output.rglob("*.mp4"):
            try:
                if prefix_leaf in path.name and path.stat().st_mtime >= started_at - 5:
                    candidates.append(path)
            except OSError:
                pass
    if not candidates:
        raise BenchError(f"Inference completed but benchmark MP4 was not found under {output}")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one controlled Wan2.2-S2V quality benchmark.")
    parser.add_argument("--port", type=int, default=8192)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--timeout-minutes", type=int, default=360)
    parser.add_argument("--lowvram", action="store_true")
    args = parser.parse_args()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_ROOT / stamp
    run_dir.mkdir(parents=True, exist_ok=True)
    server_log = run_dir / "comfy_server.log"
    graph_path = run_dir / "api_graph.json"
    manifest_path = run_dir / "manifest.json"

    portable = find_portable()
    comfy_root = portable / "ComfyUI"
    extra_paths = write_extra_model_paths()
    image_name, audio_name = copy_inputs(comfy_root)
    base_url = f"http://127.0.0.1:{args.port}"

    print("WAN-S2V-BENCHMARK-01")
    print("====================")
    print(f"Runtime: {portable}")
    print(f"Model: {DIFFUSION}")
    print(f"Resolution: {WIDTH}x{HEIGHT}")
    print(f"Frames/FPS: {LENGTH} / {FPS}")
    print(f"Sampling: {STEPS} steps, CFG {CFG:g}, {SAMPLER}/{SCHEDULER}, shift {SHIFT:g}")
    print(f"Seed: {args.seed}")
    print(f"Run dir: {run_dir}")
    print("")

    proc = None
    log_handle = None
    inference_started = None
    try:
        proc, log_handle = start_comfy(portable, args.port, extra_paths, server_log, args.lowvram)
        validate_runtime(base_url)
        print("Runtime/model visibility: PASS")

        prefix = f"video/wan_s2v_benchmark_{stamp}"
        graph = build_graph(image_name, audio_name, args.seed, prefix)
        graph_path.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")

        inference_started = time.time()
        prompt_id = submit(base_url, graph)
        print(f"Prompt submitted: {prompt_id}")
        wait_for_prompt(base_url, prompt_id, args.timeout_minutes)
        elapsed = time.time() - inference_started

        source = find_output(comfy_root, f"wan_s2v_benchmark_{stamp}", inference_started)
        final = run_dir / "wan_s2v_fp8_20step.mp4"
        shutil.copy2(source, final)

        manifest = {
            "schema": "WAN-S2V-BENCHMARK-01",
            "created": datetime.now().isoformat(),
            "runtime": str(portable),
            "model_root": str(WAN_ROOT),
            "source_output": str(source),
            "final_output": str(final),
            "settings": {
                "width": WIDTH,
                "height": HEIGHT,
                "length": LENGTH,
                "fps": FPS,
                "steps": STEPS,
                "cfg": CFG,
                "sampler": SAMPLER,
                "scheduler": SCHEDULER,
                "shift": SHIFT,
                "seed": args.seed,
                "lowvram": bool(args.lowvram),
            },
            "models": {
                "diffusion": DIFFUSION,
                "text_encoder": TEXT_ENCODER,
                "vae": VAE,
                "audio_encoder": AUDIO_ENCODER,
            },
            "prompt": {"positive": POSITIVE, "negative": NEGATIVE},
            "elapsed_seconds": elapsed,
            "human_quality_verdict": "PENDING",
        }
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

        print("")
        print("RESULT")
        print("======")
        print(f"Elapsed: {elapsed / 60:.1f} min")
        print(f"VIDEO: {final}")
        print(f"MANIFEST: {manifest_path}")
        print("")
        print("Inference success is NOT a production-quality approval.")
        return 0

    except Exception as exc:
        print("")
        print("FAILED")
        print("======")
        print(str(exc))
        print(f"Run dir: {run_dir}")
        if server_log.exists():
            print(f"Server log: {server_log}")
        return 1
    finally:
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=20)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        if log_handle is not None:
            try:
                log_handle.close()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
