#!/usr/bin/env python3
"""Local Video Studio.

A small local front-end for the already-installed MiniMax H3 Ref2VA + ComfyUI
stack. It keeps ComfyUI as the inference runtime but hides the graph from normal
use. The intended workflow is:

    text + scene -> identity references + voice reference -> H3 clips -> MP4

The implementation is deliberately stdlib-only so it can run with ComfyUI's
portable embedded Python without installing another environment.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import webbrowser
from dataclasses import dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

FPS = 24
DIFFUSION_MODEL = "minimax_h3_ref2va_pruned_int8_convrot.safetensors"
TEXT_ENCODER = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
VIDEO_VAE = "minimax_h3_video_vae_fp16.safetensors"
AUDIO_VAE = "minimax_h3_audio_vae_fp32.safetensors"
TURBO_LORA = "minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors"

MAX_TOTAL_SECONDS = 60.0
MAX_CLIP_SECONDS = 12.5
WORDS_PER_SECOND = 2.20

REQUIRED_NODES = [
    "UNETLoader",
    "LoraLoaderModelOnly",
    "CLIPLoader",
    "VAELoader",
    "LoadImage",
    "LoadAudio",
    "MiniMaxH3ReferenceToVideo",
    "MiniMaxH3SigmaShift",
    "RandomNoise",
    "KSamplerSelect",
    "BasicScheduler",
    "BasicGuider",
    "SamplerCustomAdvanced",
    "VAEDecode",
    "VAEDecodeAudio",
    "CreateVideo",
    "SaveVideo",
]

PRESETS: dict[str, dict[str, Any]] = {
    "draft": {
        "label": "Rascunho rapido",
        "width": 480,
        "height": 864,
        "steps": 4,
        "scheduler": "simple",
        "turbo": True,
        "ref_image_size": "match",
        "description": "Turbo 4 passos, 480x864. Para testar texto e cena.",
    },
    "production": {
        "label": "Producao validada",
        "width": 768,
        "height": 1344,
        "steps": 4,
        "scheduler": "simple",
        "turbo": True,
        "ref_image_size": "max",
        "description": "Turbo 4 passos, 768x1344. Caminho validado nos testes de identidade/voz/cenario.",
    },
    "quality": {
        "label": "Qualidade experimental",
        "width": 768,
        "height": 1344,
        "steps": 20,
        "scheduler": "beta",
        "turbo": False,
        "ref_image_size": "max",
        "description": "Base H3, 20 passos. Mais lento; ainda requer A/B formal contra Producao.",
    },
    "max": {
        "label": "Maximo experimental",
        "width": 768,
        "height": 1344,
        "steps": 50,
        "scheduler": "beta",
        "turbo": False,
        "ref_image_size": "max",
        "description": "Base H3, 50 passos. Muito lento na RTX 3060; reservado para comparacao final.",
    },
}

FRAMING = {
    "close": "vertical close shot, head and upper shoulders, camera at eye level",
    "medium": "vertical medium shot, approximately waist/chest-up, camera at eye level",
    "american": "vertical American shot, framed roughly from mid-thigh upward, camera at eye level",
}


class StudioError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def request_json(url: str, payload: Any | None = None, timeout: float = 120.0) -> Any:
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise StudioError(f"HTTP {exc.code} from {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise StudioError(f"Could not reach {url}: {exc}") from exc
    if not data:
        return {}
    return json.loads(data.decode("utf-8"))


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def estimated_dialogue_seconds(text: str) -> float:
    return max(2.5, word_count(text) / WORDS_PER_SECOND + 1.0)


def aligned_frame_count(seconds: float) -> int:
    n = max(5, int(round(seconds * FPS)))
    while n % 17 != 5:
        n += 1
    return n


def aligned_seconds(seconds: float) -> float:
    return aligned_frame_count(seconds) / FPS


def split_long_sentence(sentence: str, max_words: int) -> list[str]:
    parts = [p.strip() for p in re.split(r"(?<=[,;:])\s+", sentence) if p.strip()]
    if len(parts) > 1 and all(word_count(p) <= max_words for p in parts):
        packed: list[str] = []
        cur = ""
        for part in parts:
            candidate = f"{cur} {part}".strip()
            if cur and word_count(candidate) > max_words:
                packed.append(cur)
                cur = part
            else:
                cur = candidate
        if cur:
            packed.append(cur)
        return packed

    words = sentence.split()
    return [" ".join(words[i : i + max_words]) for i in range(0, len(words), max_words)]


def split_dialogue(text: str, max_clip_seconds: float = MAX_CLIP_SECONDS) -> list[str]:
    text = normalize_text(text)
    if not text:
        raise StudioError("O texto da fala esta vazio.")

    max_words = max(8, int((max_clip_seconds - 1.0) * WORDS_PER_SECOND))
    raw_sentences = [s.strip() for s in re.split(r"(?<=[.!?…])\s+", text) if s.strip()]
    if not raw_sentences:
        raw_sentences = [text]

    sentences: list[str] = []
    for sentence in raw_sentences:
        if word_count(sentence) > max_words:
            sentences.extend(split_long_sentence(sentence, max_words))
        else:
            sentences.append(sentence)

    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        candidate = f"{current} {sentence}".strip()
        if current and (word_count(candidate) > max_words or estimated_dialogue_seconds(candidate) > max_clip_seconds):
            chunks.append(current)
            current = sentence
        else:
            current = candidate
    if current:
        chunks.append(current)

    safe: list[str] = []
    for chunk in chunks:
        if estimated_dialogue_seconds(chunk) <= max_clip_seconds:
            safe.append(chunk)
        else:
            safe.extend(split_long_sentence(chunk, max_words))

    total = sum(aligned_seconds(min(MAX_CLIP_SECONDS, max(4.0, estimated_dialogue_seconds(c)))) for c in safe)
    if total > MAX_TOTAL_SECONDS + 1.0:
        raise StudioError(
            f"O roteiro estimado da {total:.1f}s. O limite desta versao e {MAX_TOTAL_SECONDS:.0f}s. "
            "Reduza o texto ou gere em duas partes."
        )
    return safe


def split_scenes(scene_text: str) -> list[str]:
    scene_text = normalize_text(scene_text)
    if not scene_text:
        return [
            "a restrained, realistic analog-photography studio with dark matte surfaces, a wooden workbench, "
            "large-format photographic equipment and subtle practical lighting"
        ]
    scenes = [s.strip() for s in re.split(r"\n\s*---\s*\n", scene_text) if s.strip()]
    return scenes or [scene_text]


def select_scene(scenes: list[str], index: int) -> str:
    return scenes[min(index, len(scenes) - 1)]


@dataclass
class Config:
    path: Path
    repo_root: Path
    comfy_root: Path
    comfy_port: int
    comfy_launch_bat: Path
    ffmpeg: str
    identity_images: list[Path]
    voice_reference: Path
    output_root: Path
    web_host: str
    web_port: int
    subject_description: str
    default_preset: str
    default_seed: int

    @property
    def input_dir(self) -> Path:
        return self.comfy_root / "input"

    @property
    def output_dir(self) -> Path:
        return self.comfy_root / "output"

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.comfy_port}"


def load_config(path: Path) -> Config:
    path = path.resolve()
    if not path.is_file():
        raise StudioError(f"Config nao encontrado: {path}")
    with path.open("r", encoding="utf-8-sig") as fh:
        raw = json.load(fh)

    def p(name: str) -> Path:
        value = str(raw[name])
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = (path.parent / candidate).resolve()
        return candidate

    repo_value = str(raw.get("repo_root", "../.."))
    repo_root = Path(repo_value)
    if not repo_root.is_absolute():
        repo_root = (path.parent / repo_root).resolve()

    preset = str(raw.get("default_preset", "production"))
    if preset not in PRESETS:
        raise StudioError(f"default_preset invalido: {preset}")

    return Config(
        path=path,
        repo_root=repo_root,
        comfy_root=p("comfy_root"),
        comfy_port=int(raw.get("comfy_port", 8188)),
        comfy_launch_bat=p("comfy_launch_bat"),
        ffmpeg=str(raw.get("ffmpeg", "ffmpeg")),
        identity_images=[Path(x) if Path(x).is_absolute() else (path.parent / x).resolve() for x in raw["identity_images"]],
        voice_reference=Path(raw["voice_reference"]) if Path(raw["voice_reference"]).is_absolute() else (path.parent / raw["voice_reference"]).resolve(),
        output_root=p("output_root"),
        web_host=str(raw.get("web_host", "127.0.0.1")),
        web_port=int(raw.get("web_port", 8765)),
        subject_description=str(raw.get("subject_description", "the same adult Brazilian man shown in the identity reference pictures")),
        default_preset=preset,
        default_seed=int(raw.get("default_seed", 0)),
    )


class ComfyClient:
    def __init__(self, config: Config):
        self.config = config

    def ping(self, timeout: float = 2.0) -> bool:
        try:
            request_json(self.config.base_url + "/system_stats", timeout=timeout)
            return True
        except Exception:
            return False

    def ensure_running(self, wait_seconds: int = 180) -> None:
        if self.ping():
            return
        bat = self.config.comfy_launch_bat
        if not bat.is_file():
            raise StudioError(f"Launcher do ComfyUI nao encontrado: {bat}")
        creationflags = 0
        if os.name == "nt":
            creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
            cmd = ["cmd.exe", "/c", str(bat)]
        else:
            cmd = [str(bat)]
        subprocess.Popen(
            cmd,
            cwd=str(bat.parent),
            creationflags=creationflags,
        )
        deadline = time.time() + wait_seconds
        while time.time() < deadline:
            if self.ping(timeout=3):
                return
            time.sleep(2)
        raise StudioError(f"ComfyUI nao respondeu em {self.config.base_url} apos {wait_seconds}s.")

    def check_nodes(self) -> None:
        missing = []
        for node in REQUIRED_NODES:
            try:
                info = request_json(self.config.base_url + f"/object_info/{node}", timeout=30)
            except Exception as exc:
                raise StudioError(f"Falha consultando o ComfyUI ({node}): {exc}") from exc
            if node not in info:
                missing.append(node)
        if missing:
            raise StudioError("Nos obrigatorios ausentes no ComfyUI: " + ", ".join(missing))

    def submit(self, graph: dict[str, Any]) -> str:
        response = request_json(self.config.base_url + "/prompt", {"prompt": graph}, timeout=180)
        prompt_id = response.get("prompt_id") if isinstance(response, dict) else None
        if not prompt_id:
            raise StudioError(f"ComfyUI nao retornou prompt_id: {response}")
        return str(prompt_id)

    def wait(self, prompt_id: str, timeout_minutes: int, progress_cb=None) -> dict[str, Any]:
        started = time.time()
        deadline = started + timeout_minutes * 60
        next_report = started + 20
        while time.time() < deadline:
            history = request_json(self.config.base_url + f"/history/{prompt_id}", timeout=120)
            item = history.get(prompt_id) if isinstance(history, dict) else None
            if item:
                status = item.get("status") or {}
                for message in status.get("messages") or []:
                    if isinstance(message, (list, tuple)) and message and message[0] == "execution_error":
                        raise StudioError(f"ComfyUI execution_error: {message}")
                if status.get("completed") is True:
                    return item
            now = time.time()
            if progress_cb and now >= next_report:
                progress_cb(f"Inferencia ativa ha {int(now - started)}s")
                next_report = now + 20
            time.sleep(3)
        raise StudioError(f"Timeout apos {timeout_minutes} minutos para prompt {prompt_id}")


def ffmpeg_executable(config: Config) -> str:
    candidate = Path(config.ffmpeg)
    if candidate.is_file():
        return str(candidate)
    found = shutil.which(config.ffmpeg)
    if not found:
        raise StudioError(f"ffmpeg nao encontrado: {config.ffmpeg}")
    return found


def model_path(config: Config, group: str, name: str) -> Path:
    return config.comfy_root / "models" / group / name


def preflight(config: Config, start_comfy: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not config.comfy_root.is_dir():
        errors.append(f"ComfyUI root ausente: {config.comfy_root}")
    if not config.input_dir.is_dir():
        errors.append(f"ComfyUI input ausente: {config.input_dir}")
    if not config.comfy_launch_bat.is_file():
        errors.append(f"Launcher ausente: {config.comfy_launch_bat}")

    required_models = [
        model_path(config, "diffusion_models", DIFFUSION_MODEL),
        model_path(config, "text_encoders", TEXT_ENCODER),
        model_path(config, "vae", VIDEO_VAE),
        model_path(config, "vae", AUDIO_VAE),
        model_path(config, "loras", TURBO_LORA),
    ]
    for path in required_models:
        if not path.is_file():
            errors.append(f"Modelo ausente: {path}")

    if len(config.identity_images) < 1:
        errors.append("Nenhuma imagem de identidade configurada.")
    if len(config.identity_images) > 9:
        errors.append("H3 aceita no maximo 9 imagens de identidade.")
    for path in config.identity_images:
        if not path.is_file():
            errors.append(f"Referencia de identidade ausente: {path}")
    if not config.voice_reference.is_file():
        errors.append(f"Referencia de voz ausente: {config.voice_reference}")

    try:
        ffmpeg_executable(config)
    except StudioError as exc:
        errors.append(str(exc))

    client = ComfyClient(config)
    if not errors and start_comfy:
        try:
            client.ensure_running()
            client.check_nodes()
        except StudioError as exc:
            errors.append(str(exc))
    elif not client.ping():
        warnings.append("ComfyUI nao esta ativo; o Studio tentara inicia-lo na primeira geracao.")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "comfy_online": client.ping(),
        "identity_images": [str(x) for x in config.identity_images],
        "voice_reference": str(config.voice_reference),
        "output_root": str(config.output_root),
    }


def sync_reference(config: Config, source: Path, target_name: str) -> str:
    target_dir = config.input_dir / "video_studio" / "profile"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / target_name
    need_copy = True
    if target.is_file():
        src_stat = source.stat()
        dst_stat = target.stat()
        need_copy = src_stat.st_size != dst_stat.st_size or int(src_stat.st_mtime) != int(dst_stat.st_mtime)
    if need_copy:
        shutil.copy2(source, target)
    return target.relative_to(config.input_dir).as_posix()


def sync_profile(config: Config) -> tuple[list[str], str]:
    images: list[str] = []
    for index, source in enumerate(config.identity_images, start=1):
        suffix = source.suffix.lower() or ".png"
        images.append(sync_reference(config, source, f"identity_{index:02d}{suffix}"))
    voice_suffix = config.voice_reference.suffix.lower() or ".wav"
    voice = sync_reference(config, config.voice_reference, f"voice_reference{voice_suffix}")
    return images, voice


def build_h3_prompt(config: Config, dialogue: str, scene: str, appearance: str, framing: str) -> str:
    picture_tags = ", ".join(f"<Picture {i}>" for i in range(1, len(config.identity_images) + 1))
    identity_sentence = (
        f"<Subject 1> is {config.subject_description}. {picture_tags} are identity references for the same person. "
        "Use them only for the person, not for their rooms, objects, windows, tables, bottles, equipment, colors, or lighting."
    )
    appearance_text = appearance.strip() if appearance.strip() else "natural contemporary dark clothing appropriate to the scene"
    frame_text = FRAMING.get(framing, FRAMING["medium"])
    return f"""subject_definitions:
{identity_sentence}
Preserve <Subject 1>'s facial identity, face proportions, eyeglasses, beard, hairline, apparent age, skin characteristics and physical build from the reference pictures.
<Audio 1> is the voice identity reference for <Subject 1>. Preserve his Brazilian Portuguese timbre, accent and natural cadence, but do not reproduce the words spoken in the reference recording.

reference_separation:
The reference pictures are identity-only evidence. The generated environment must NOT inherit or reconstruct the background, room, furniture, windows, bottles, equipment, light direction, or composition seen in the identity pictures unless the target scene below independently requests such an element.

scene:
Create a completely new realistic photographic scene: {scene.strip()}.
The location must read as a new physical scene rather than a reconstruction of the identity-reference background.

appearance:
<Subject 1> wears {appearance_text}. Preserve his identity even when clothing or environment changes.

camera:
{frame_text}. Realistic photographic rendering, coherent perspective, stable subject scale, restrained camera movement.

performance:
<Subject 1> speaks naturally toward the camera. Generate autonomous natural performance without any driving video: breathing, blinking, small head movements and restrained conversational hand gestures. Avoid repetitive symmetrical presenter gestures, exaggerated arm waving, frozen posture, or sudden body reconfiguration. Keep face, hands and body temporally coherent.

speech:
Using the Brazilian Portuguese voice identity from <Audio 1>, <Subject 1> (S1) says:
<d>[Portuguese] {dialogue.strip()}</d>
Mouth movement must synchronize naturally with the newly generated speech.

overall_soundscape:
Only the clear natural voice of <Subject 1> with subtle realistic room ambience appropriate to the scene. No background music and no additional voices.

non_diegetic_music:
None."""


def build_graph(
    *,
    config: Config,
    image_inputs: list[str],
    voice_input: str,
    prompt: str,
    preset_name: str,
    duration_seconds: float,
    seed: int,
    output_prefix: str,
) -> dict[str, Any]:
    if preset_name not in PRESETS:
        raise StudioError(f"Preset invalido: {preset_name}")
    preset = PRESETS[preset_name]

    graph: dict[str, Any] = {
        "1": {
            "inputs": {"unet_name": DIFFUSION_MODEL, "weight_dtype": "default"},
            "class_type": "UNETLoader",
            "_meta": {"title": "MiniMax H3 Ref2VA"},
        },
        "4": {
            "inputs": {"clip_name": TEXT_ENCODER, "type": "minimax", "device": "default"},
            "class_type": "CLIPLoader",
            "_meta": {"title": "MiniMax H3 Qwen3-VL"},
        },
        "5": {
            "inputs": {"vae_name": VIDEO_VAE},
            "class_type": "VAELoader",
            "_meta": {"title": "MiniMax H3 video VAE"},
        },
        "6": {
            "inputs": {"vae_name": AUDIO_VAE},
            "class_type": "VAELoader",
            "_meta": {"title": "MiniMax H3 audio VAE"},
        },
    }

    model_ref: list[Any] = ["1", 0]
    if preset["turbo"]:
        graph["2"] = {
            "inputs": {
                "model": ["1", 0],
                "lora_name": TURBO_LORA,
                "strength_model": 1.0,
            },
            "class_type": "LoraLoaderModelOnly",
            "_meta": {"title": "H3 Ref2V Turbo 4-step"},
        }
        model_ref = ["2", 0]

    graph["3"] = {
        "inputs": {
            "model": model_ref,
            "shift_video": 12.0,
            "shift_audio": 3.0,
        },
        "class_type": "MiniMaxH3SigmaShift",
        "_meta": {"title": "H3 sigma shifts 12/3"},
    }
    sampled_model = ["3", 0]

    h3_inputs: dict[str, Any] = {
        "clip": ["4", 0],
        "vae": ["5", 0],
        "audio_vae": ["6", 0],
        "prompt": prompt,
        "width": int(preset["width"]),
        "height": int(preset["height"]),
        "length": aligned_frame_count(duration_seconds),
        "ref_image_size": str(preset["ref_image_size"]),
    }

    for i, rel_path in enumerate(image_inputs):
        node_id = str(20 + i)
        graph[node_id] = {
            "inputs": {"image": rel_path},
            "class_type": "LoadImage",
            "_meta": {"title": f"Identity reference {i + 1}"},
        }
        h3_inputs[f"ref_images.ref_image_{i}"] = [node_id, 0]

    graph["30"] = {
        "inputs": {"audio": voice_input},
        "class_type": "LoadAudio",
        "_meta": {"title": "Voice identity reference"},
    }
    h3_inputs["ref_audios.ref_audio_0"] = ["30", 0]

    graph.update(
        {
            "40": {
                "inputs": h3_inputs,
                "class_type": "MiniMaxH3ReferenceToVideo",
                "_meta": {"title": "Identity + voice -> new video"},
            },
            "50": {
                "inputs": {"noise_seed": int(seed)},
                "class_type": "RandomNoise",
                "_meta": {"title": "Seed"},
            },
            "51": {
                "inputs": {"sampler_name": "res_multistep"},
                "class_type": "KSamplerSelect",
                "_meta": {"title": "H3 sampler"},
            },
            "52": {
                "inputs": {
                    "scheduler": str(preset["scheduler"]),
                    "steps": int(preset["steps"]),
                    "denoise": 1.0,
                    "model": sampled_model,
                },
                "class_type": "BasicScheduler",
                "_meta": {"title": f"{preset_name} scheduler"},
            },
            "53": {
                "inputs": {"model": sampled_model, "conditioning": ["40", 0]},
                "class_type": "BasicGuider",
                "_meta": {"title": "H3 guider"},
            },
            "54": {
                "inputs": {
                    "noise": ["50", 0],
                    "guider": ["53", 0],
                    "sampler": ["51", 0],
                    "sigmas": ["52", 0],
                    "latent_image": ["40", 1],
                },
                "class_type": "SamplerCustomAdvanced",
                "_meta": {"title": "H3 sampler"},
            },
            "60": {
                "inputs": {"samples": ["54", 0], "vae": ["5", 0]},
                "class_type": "VAEDecode",
                "_meta": {"title": "Decode video"},
            },
            "61": {
                "inputs": {"samples": ["54", 0], "vae": ["6", 0]},
                "class_type": "VAEDecodeAudio",
                "_meta": {"title": "Decode voice/audio"},
            },
            "62": {
                "inputs": {
                    "images": ["60", 0],
                    "audio": ["61", 0],
                    "fps": FPS,
                    "bit_depth": 8,
                    "color_space": "sRGB",
                },
                "class_type": "CreateVideo",
                "_meta": {"title": "Mux H3 video + audio"},
            },
            "63": {
                "inputs": {
                    "filename_prefix": output_prefix,
                    "format": "mp4",
                    "codec": "h264",
                    "codec.encoding": "auto",
                    "video": ["62", 0],
                },
                "class_type": "SaveVideo",
                "_meta": {"title": "Save Video Studio clip"},
            },
        }
    )
    return graph


def newest_output(comfy_root: Path, prefix: str, since_epoch: float) -> Path | None:
    normalized = prefix.replace("/", os.sep).replace("\\", os.sep)
    patterns = [
        str(comfy_root / "output" / (normalized + "*.mp4")),
        str(comfy_root / "output" / (normalized + "*.mkv")),
        str(comfy_root / "output" / (normalized + "*.webm")),
    ]
    candidates: list[Path] = []
    for pattern in patterns:
        candidates.extend(Path(p) for p in glob.glob(pattern))
    candidates = [p for p in candidates if p.stat().st_mtime >= since_epoch - 2]
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


def concat_videos(config: Config, clips: list[Path], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if len(clips) == 1:
        shutil.copy2(clips[0], output)
        return

    ffmpeg = ffmpeg_executable(config)
    concat_file = output.parent / "concat.txt"
    with concat_file.open("w", encoding="utf-8") as fh:
        for clip in clips:
            escaped = str(clip.resolve()).replace("'", "'\\''")
            fh.write(f"file '{escaped}'\n")

    cmd = [
        ffmpeg,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(output),
    ]
    completed = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if completed.returncode != 0:
        raise StudioError("ffmpeg falhou ao concatenar clips:\n" + completed.stdout[-6000:])


class JobStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: dict[str, dict[str, Any]] = {}

    def create(self, request_data: dict[str, Any]) -> dict[str, Any]:
        job_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        job = {
            "id": job_id,
            "status": "QUEUED",
            "created_utc": utc_now(),
            "updated_utc": utc_now(),
            "progress": 0,
            "message": "Na fila",
            "request": request_data,
            "error": None,
            "output": None,
            "clips": [],
        }
        with self._lock:
            self._jobs[job_id] = job
        return json.loads(json.dumps(job))

    def update(self, job_id: str, **changes: Any) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.update(changes)
            job["updated_utc"] = utc_now()

    def get(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return json.loads(json.dumps(job)) if job else None


class StudioEngine:
    def __init__(self, config: Config, jobs: JobStore):
        self.config = config
        self.jobs = jobs
        self.client = ComfyClient(config)
        self.gpu_lock = threading.Lock()

    def _log(self, job_id: str, message: str, progress: int | None = None) -> None:
        changes: dict[str, Any] = {"message": message}
        if progress is not None:
            changes["progress"] = progress
        self.jobs.update(job_id, **changes)
        print(f"[{job_id}] {message}", flush=True)

    def start_job(self, request_data: dict[str, Any]) -> dict[str, Any]:
        job = self.jobs.create(request_data)
        thread = threading.Thread(target=self._run_job, args=(job["id"],), daemon=True)
        thread.start()
        return job

    def _run_job(self, job_id: str) -> None:
        try:
            with self.gpu_lock:
                self.jobs.update(job_id, status="RUNNING")
                self._generate(job_id)
        except Exception as exc:
            self.jobs.update(job_id, status="FAILED", error=str(exc), message="Falha")
            print(f"[{job_id}] ERROR: {exc}", file=sys.stderr, flush=True)

    def _generate(self, job_id: str) -> None:
        job = self.jobs.get(job_id)
        assert job is not None
        req = job["request"]
        text = normalize_text(str(req.get("text", "")))
        scenario = str(req.get("scenario", ""))
        appearance = str(req.get("appearance", ""))
        framing = str(req.get("framing", "medium"))
        preset_name = str(req.get("preset", self.config.default_preset))
        seed = int(req.get("seed", self.config.default_seed))

        if preset_name not in PRESETS:
            raise StudioError(f"Preset invalido: {preset_name}")
        if framing not in FRAMING:
            raise StudioError(f"Enquadramento invalido: {framing}")

        chunks = split_dialogue(text)
        scenes = split_scenes(scenario)
        if len(chunks) > 8:
            raise StudioError("Roteiro criou mais de 8 clips; reduza o texto.")

        self._log(job_id, "Preflight e inicializacao do ComfyUI", 2)
        report = preflight(self.config, start_comfy=True)
        if not report["ok"]:
            raise StudioError("; ".join(report["errors"]))

        self._log(job_id, "Sincronizando referencias de identidade e voz", 5)
        image_inputs, voice_input = sync_profile(self.config)

        run_dir = self.config.output_root / job_id
        clips_dir = run_dir / "clips"
        evidence_dir = run_dir / "evidence"
        clips_dir.mkdir(parents=True, exist_ok=True)
        evidence_dir.mkdir(parents=True, exist_ok=True)

        request_path = run_dir / "request.json"
        with request_path.open("w", encoding="utf-8") as fh:
            json.dump(req, fh, ensure_ascii=False, indent=2)

        rendered: list[Path] = []
        clip_records: list[dict[str, Any]] = []
        started_job = time.time()

        for index, dialogue in enumerate(chunks):
            clip_no = index + 1
            scene = select_scene(scenes, index)
            duration = min(MAX_CLIP_SECONDS, max(4.5, estimated_dialogue_seconds(dialogue)))
            duration = aligned_seconds(duration)
            prompt = build_h3_prompt(self.config, dialogue, scene, appearance, framing)
            output_prefix = f"video/video_studio/{job_id}/clip_{clip_no:02d}"
            graph = build_graph(
                config=self.config,
                image_inputs=image_inputs,
                voice_input=voice_input,
                prompt=prompt,
                preset_name=preset_name,
                duration_seconds=duration,
                seed=seed + index,
                output_prefix=output_prefix,
            )

            with (evidence_dir / f"clip_{clip_no:02d}_prompt.txt").open("w", encoding="utf-8") as fh:
                fh.write(prompt)
            with (evidence_dir / f"clip_{clip_no:02d}_api_prompt.json").open("w", encoding="utf-8") as fh:
                json.dump(graph, fh, ensure_ascii=False, indent=2)

            base_progress = 8 + int((index / max(1, len(chunks))) * 80)
            self._log(
                job_id,
                f"Gerando clip {clip_no}/{len(chunks)} ({duration:.1f}s, {PRESETS[preset_name]['label']})",
                base_progress,
            )
            started_clip = time.time()
            prompt_id = self.client.submit(graph)
            self.client.wait(
                prompt_id,
                timeout_minutes=180 if preset_name in ("quality", "max") else 90,
                progress_cb=lambda msg, n=clip_no: self._log(job_id, f"Clip {n}: {msg}"),
            )
            source = newest_output(self.config.comfy_root, output_prefix, started_clip)
            if source is None:
                raise StudioError(f"Clip {clip_no} concluiu no ComfyUI, mas o MP4 nao foi localizado.")
            target = clips_dir / f"clip_{clip_no:02d}.mp4"
            shutil.copy2(source, target)
            rendered.append(target)
            record = {
                "clip": clip_no,
                "dialogue": dialogue,
                "scene": scene,
                "duration_requested_seconds": duration,
                "seed": seed + index,
                "prompt_id": prompt_id,
                "elapsed_seconds": round(time.time() - started_clip, 2),
                "source": str(source),
                "local_copy": str(target),
                "sha256": sha256_file(target),
            }
            clip_records.append(record)
            self.jobs.update(job_id, clips=clip_records)

        self._log(job_id, "Montando MP4 final", 92)
        final_path = run_dir / f"video_studio_{job_id}.mp4"
        concat_videos(self.config, rendered, final_path)

        manifest = {
            "project": "Local Video Studio",
            "created_utc": utc_now(),
            "job_id": job_id,
            "engine": "MiniMax H3 Ref2VA via ComfyUI",
            "preset": preset_name,
            "preset_config": PRESETS[preset_name],
            "framing": framing,
            "appearance": appearance,
            "script": text,
            "scenes": scenes,
            "identity_references": [
                {"path": str(p), "sha256": sha256_file(p)} for p in self.config.identity_images
            ],
            "voice_reference": {
                "path": str(self.config.voice_reference),
                "sha256": sha256_file(self.config.voice_reference),
            },
            "clips": clip_records,
            "final_output": str(final_path),
            "final_sha256": sha256_file(final_path),
            "elapsed_seconds": round(time.time() - started_job, 2),
        }
        with (run_dir / "manifest.json").open("w", encoding="utf-8") as fh:
            json.dump(manifest, fh, ensure_ascii=False, indent=2)

        self.jobs.update(
            job_id,
            status="COMPLETED",
            progress=100,
            message="Concluido",
            output=str(final_path),
            clips=clip_records,
        )
        print(f"[{job_id}] COMPLETE: {final_path}", flush=True)


def load_web_ui() -> bytes:
    ui_path = Path(__file__).with_name("index.html")
    if not ui_path.is_file():
        raise StudioError(f"UI ausente: {ui_path}")
    return ui_path.read_bytes()


def parse_range_header(value: str | None, size: int) -> tuple[int, int] | None:
    if not value or not value.startswith("bytes="):
        return None
    spec = value[6:].split(",", 1)[0].strip()
    if "-" not in spec:
        return None
    start_s, end_s = spec.split("-", 1)
    if not start_s:
        length = int(end_s)
        start = max(0, size - length)
        return start, size - 1
    start = int(start_s)
    end = int(end_s) if end_s else size - 1
    if start >= size:
        return None
    return start, min(end, size - 1)


class StudioHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, handler, *, config: Config, engine: StudioEngine, jobs: JobStore):
        super().__init__(address, handler)
        self.config = config
        self.engine = engine
        self.jobs = jobs


class Handler(BaseHTTPRequestHandler):
    server: StudioHTTPServer

    def log_message(self, fmt: str, *args: Any) -> None:
        print("[web] " + (fmt % args), flush=True)

    def _json(self, data: Any, status: int = 200) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _body_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise StudioError(f"JSON invalido: {exc}") from exc
        if not isinstance(data, dict):
            raise StudioError("O corpo deve ser um objeto JSON.")
        return data

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path == "/":
            payload = load_web_ui()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)
            return
        if path == "/api/config":
            self._json(
                {
                    "presets": PRESETS,
                    "default_preset": self.server.config.default_preset,
                    "framing": list(FRAMING.keys()),
                    "identity_reference_count": len(self.server.config.identity_images),
                    "max_total_seconds": MAX_TOTAL_SECONDS,
                }
            )
            return
        if path == "/api/status":
            report = preflight(self.server.config, start_comfy=False)
            self._json(report)
            return

        match = re.fullmatch(r"/api/jobs/([A-Za-z0-9-]+)", path)
        if match:
            job = self.server.jobs.get(match.group(1))
            if not job:
                self._json({"error": "job nao encontrado"}, 404)
            else:
                self._json(job)
            return

        match = re.fullmatch(r"/api/jobs/([A-Za-z0-9-]+)/video", path)
        if match:
            job = self.server.jobs.get(match.group(1))
            if not job or job.get("status") != "COMPLETED" or not job.get("output"):
                self.send_error(404, "Video unavailable")
                return
            file_path = Path(job["output"])
            if not file_path.is_file():
                self.send_error(404, "Video file missing")
                return
            self._send_file(file_path)
            return

        self.send_error(404, "Not found")

    def _send_file(self, path: Path) -> None:
        size = path.stat().st_size
        range_info = parse_range_header(self.headers.get("Range"), size)
        content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        if range_info:
            start, end = range_info
            length = end - start + 1
            self.send_response(HTTPStatus.PARTIAL_CONTENT)
            self.send_header("Content-Type", content_type)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.send_header("Content-Length", str(length))
            self.end_headers()
            with path.open("rb") as fh:
                fh.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = fh.read(min(1024 * 1024, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        else:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(size))
            self.end_headers()
            with path.open("rb") as fh:
                shutil.copyfileobj(fh, self.wfile)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/api/generate":
            self.send_error(404, "Not found")
            return
        try:
            data = self._body_json()
            if not normalize_text(str(data.get("text", ""))):
                raise StudioError("Escreva o texto que sera falado.")
            preset = str(data.get("preset", self.server.config.default_preset))
            if preset not in PRESETS:
                raise StudioError("Preset invalido.")
            framing = str(data.get("framing", "medium"))
            if framing not in FRAMING:
                raise StudioError("Enquadramento invalido.")
            split_dialogue(str(data.get("text", "")))
            job = self.server.engine.start_job(data)
            self._json(job, 202)
        except StudioError as exc:
            self._json({"error": str(exc)}, 400)
        except Exception as exc:
            self._json({"error": f"Erro interno: {exc}"}, 500)


def serve(config: Config, no_open: bool = False) -> None:
    config.output_root.mkdir(parents=True, exist_ok=True)
    jobs = JobStore()
    engine = StudioEngine(config, jobs)
    server = StudioHTTPServer((config.web_host, config.web_port), Handler, config=config, engine=engine, jobs=jobs)
    url = f"http://{config.web_host}:{config.web_port}/"
    print(f"Local Video Studio: {url}", flush=True)
    print("ComfyUI sera iniciado automaticamente quando necessario.", flush=True)
    if not no_open:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def cli_generate(config: Config, args: argparse.Namespace) -> None:
    jobs = JobStore()
    engine = StudioEngine(config, jobs)
    request_data = {
        "text": args.text,
        "scenario": args.scenario,
        "appearance": args.appearance,
        "framing": args.framing,
        "preset": args.preset,
        "seed": args.seed,
    }
    job = jobs.create(request_data)
    engine.jobs.update(job["id"], status="RUNNING")
    try:
        with engine.gpu_lock:
            engine._generate(job["id"])
    except Exception as exc:
        jobs.update(job["id"], status="FAILED", error=str(exc), message="Falha")
        raise
    final = jobs.get(job["id"])
    print(json.dumps(final, ensure_ascii=False, indent=2))


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local Video Studio - MiniMax H3 Ref2VA")
    parser.add_argument("--config", default=str(Path(__file__).with_name("config.json")))
    sub = parser.add_subparsers(dest="command", required=True)

    p_pre = sub.add_parser("preflight", help="Valida instalacao, modelos, referencias e ComfyUI")
    p_pre.add_argument("--no-start-comfy", action="store_true")

    p_serve = sub.add_parser("serve", help="Inicia a interface web local")
    p_serve.add_argument("--no-open", action="store_true")

    p_gen = sub.add_parser("generate", help="Gera um video sem abrir a interface web")
    p_gen.add_argument("--text", required=True)
    p_gen.add_argument("--scenario", default="")
    p_gen.add_argument("--appearance", default="")
    p_gen.add_argument("--framing", choices=sorted(FRAMING), default="medium")
    p_gen.add_argument("--preset", choices=sorted(PRESETS), default="production")
    p_gen.add_argument("--seed", type=int, default=0)
    return parser


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()
    config = load_config(Path(args.config))

    if args.command == "preflight":
        report = preflight(config, start_comfy=not args.no_start_comfy)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        raise SystemExit(0 if report["ok"] else 2)
    if args.command == "serve":
        serve(config, no_open=args.no_open)
        return
    if args.command == "generate":
        cli_generate(config, args)
        return


if __name__ == "__main__":
    main()
