#!/usr/bin/env python3
"""FLUX.2 Klein 4B distilled static-generation/edit adapter.

The adapter is intentionally UI-independent. It implements the Asset Studio static
request contract against the isolated ComfyUI runtime proven by Runner56.

For reference editing it follows the official distilled ComfyUI workflow semantics:
encode each reference with the FLUX.2 VAE and append the latent to both positive and
zeroed-negative conditioning through ReferenceLatent. Multiple references are chained
in declared order, so semantic reference roles remain an Asset Studio concern rather
than a hard-coded model graph concern.
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from PIL import Image

from adapter_protocol import GenerationResult, StaticGenerationRequest

MODEL = "flux-2-klein-4b-fp8.safetensors"
MODEL_SHA256 = "97ed34fe0567e436200f2faee3939b88f2b5d99f8af2a4dc16532c4245c0ccb6"
TEXT_ENCODER = "qwen_3_4b.safetensors"
TEXT_ENCODER_SHA256 = "6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a"
VAE = "flux2-vae.safetensors"
VAE_SHA256 = "868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3"

REQUIRED_NODES = (
    "UNETLoader",
    "CLIPLoader",
    "VAELoader",
    "CLIPTextEncode",
    "ConditioningZeroOut",
    "LoadImage",
    "VAEEncode",
    "ReferenceLatent",
    "CFGGuider",
    "RandomNoise",
    "KSamplerSelect",
    "Flux2Scheduler",
    "EmptyFlux2LatentImage",
    "SamplerCustomAdvanced",
    "VAEDecode",
    "SaveImage",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class Flux2KleinAdapter:
    adapter_id = "flux2_klein_4b_distilled"

    def __init__(self, comfy_root: Path, base_url: str, timeout_minutes: int = 180) -> None:
        self.comfy_root = comfy_root.resolve()
        self.base_url = base_url.rstrip("/")
        self.timeout_minutes = int(timeout_minutes)
        self._verified = False

    def _request_json(self, url: str, payload: dict[str, Any] | None = None, timeout: int = 60) -> Any:
        data = None
        method = "GET"
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            method = "POST"
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} from {url}: {body[:10000]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach {url}: {exc}") from exc

    def _verify_file(self, path: Path, expected_sha: str, label: str) -> None:
        if not path.is_file():
            raise RuntimeError(f"required {label} missing: {path}")
        actual = sha256_file(path)
        if actual.lower() != expected_sha.lower():
            raise RuntimeError(f"{label} SHA256 mismatch: expected {expected_sha}, got {actual}")

    def verify_runtime(self) -> None:
        if self._verified:
            return
        self._request_json(self.base_url + "/system_stats", timeout=15)
        self._verify_file(
            self.comfy_root / "models" / "diffusion_models" / MODEL,
            MODEL_SHA256,
            MODEL,
        )
        self._verify_file(
            self.comfy_root / "models" / "text_encoders" / TEXT_ENCODER,
            TEXT_ENCODER_SHA256,
            TEXT_ENCODER,
        )
        self._verify_file(self.comfy_root / "models" / "vae" / VAE, VAE_SHA256, VAE)
        for node_name in REQUIRED_NODES:
            info = self._request_json(self.base_url + f"/object_info/{node_name}", timeout=30)
            if node_name not in info:
                raise RuntimeError(f"required native ComfyUI node unavailable: {node_name}")
        self._verified = True

    @staticmethod
    def _round_multiple_16(value: int) -> int:
        return max(16, int(round(value / 16.0)) * 16)

    def _prepare_reference(self, source: Path, job_id: str, index: int) -> tuple[str, str]:
        source = Path(source).resolve()
        if not source.is_file():
            raise FileNotFoundError(source)

        target_dir = self.comfy_root / "input" / "roguelite_asset_studio" / job_id
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"reference_{index:02d}.png"

        with Image.open(source) as opened:
            opened.load()
            if "A" in opened.getbands():
                rgba = opened.convert("RGBA")
                background = Image.new("RGBA", rgba.size, (128, 128, 128, 255))
                background.alpha_composite(rgba)
                image = background.convert("RGB")
            else:
                image = opened.convert("RGB")

            # Match the official workflow's intent of keeping reference conditioning
            # around one megapixel while preserving aspect ratio. This is a model
            # conditioning copy only; the authored source file is never modified.
            max_pixels = 1_048_576
            width, height = image.size
            if width * height > max_pixels:
                scale = math.sqrt(max_pixels / float(width * height))
                width = max(16, int(width * scale))
                height = max(16, int(height * scale))
            width = self._round_multiple_16(width)
            height = self._round_multiple_16(height)
            if image.size != (width, height):
                image = image.resize((width, height), Image.Resampling.LANCZOS)
            image.save(target, format="PNG")

        relative = target.relative_to(self.comfy_root / "input").as_posix()
        return relative, sha256_file(source)

    @staticmethod
    def _next_id(counter: list[int]) -> str:
        value = str(counter[0])
        counter[0] += 1
        return value

    def _build_prompt(
        self,
        request: StaticGenerationRequest,
        reference_names: list[str],
        output_prefix: str,
    ) -> dict[str, Any]:
        counter = [1]
        graph: dict[str, Any] = {}

        model_id = self._next_id(counter)
        graph[model_id] = {
            "inputs": {"unet_name": MODEL, "weight_dtype": "default"},
            "class_type": "UNETLoader",
        }
        clip_id = self._next_id(counter)
        graph[clip_id] = {
            "inputs": {"clip_name": TEXT_ENCODER, "type": "flux2", "device": "default"},
            "class_type": "CLIPLoader",
        }
        vae_id = self._next_id(counter)
        graph[vae_id] = {"inputs": {"vae_name": VAE}, "class_type": "VAELoader"}
        positive_id = self._next_id(counter)
        graph[positive_id] = {
            "inputs": {"text": request.prompt, "clip": [clip_id, 0]},
            "class_type": "CLIPTextEncode",
        }

        if reference_names:
            negative_id = self._next_id(counter)
            graph[negative_id] = {
                "inputs": {"conditioning": [positive_id, 0]},
                "class_type": "ConditioningZeroOut",
            }
            positive_ref: list[Any] = [positive_id, 0]
            negative_ref: list[Any] = [negative_id, 0]
        else:
            if request.negative.strip():
                negative_id = self._next_id(counter)
                graph[negative_id] = {
                    "inputs": {"text": request.negative, "clip": [clip_id, 0]},
                    "class_type": "CLIPTextEncode",
                }
            else:
                negative_id = self._next_id(counter)
                graph[negative_id] = {
                    "inputs": {"conditioning": [positive_id, 0]},
                    "class_type": "ConditioningZeroOut",
                }
            positive_ref = [positive_id, 0]
            negative_ref = [negative_id, 0]

        for reference_name in reference_names:
            load_id = self._next_id(counter)
            graph[load_id] = {"inputs": {"image": reference_name}, "class_type": "LoadImage"}
            encode_id = self._next_id(counter)
            graph[encode_id] = {
                "inputs": {"pixels": [load_id, 0], "vae": [vae_id, 0]},
                "class_type": "VAEEncode",
            }
            positive_ref_id = self._next_id(counter)
            graph[positive_ref_id] = {
                "inputs": {"conditioning": positive_ref, "latent": [encode_id, 0]},
                "class_type": "ReferenceLatent",
            }
            negative_ref_id = self._next_id(counter)
            graph[negative_ref_id] = {
                "inputs": {"conditioning": negative_ref, "latent": [encode_id, 0]},
                "class_type": "ReferenceLatent",
            }
            positive_ref = [positive_ref_id, 0]
            negative_ref = [negative_ref_id, 0]

        guider_id = self._next_id(counter)
        graph[guider_id] = {
            "inputs": {
                "model": [model_id, 0],
                "positive": positive_ref,
                "negative": negative_ref,
                "cfg": float(request.cfg),
            },
            "class_type": "CFGGuider",
        }
        noise_id = self._next_id(counter)
        graph[noise_id] = {"inputs": {"noise_seed": int(request.seed)}, "class_type": "RandomNoise"}
        sampler_id = self._next_id(counter)
        graph[sampler_id] = {"inputs": {"sampler_name": request.sampler}, "class_type": "KSamplerSelect"}
        scheduler_id = self._next_id(counter)
        graph[scheduler_id] = {
            "inputs": {
                "steps": int(request.steps),
                "width": int(request.width),
                "height": int(request.height),
            },
            "class_type": "Flux2Scheduler",
        }
        latent_id = self._next_id(counter)
        graph[latent_id] = {
            "inputs": {
                "width": int(request.width),
                "height": int(request.height),
                "batch_size": 1,
            },
            "class_type": "EmptyFlux2LatentImage",
        }
        sample_id = self._next_id(counter)
        graph[sample_id] = {
            "inputs": {
                "noise": [noise_id, 0],
                "guider": [guider_id, 0],
                "sampler": [sampler_id, 0],
                "sigmas": [scheduler_id, 0],
                "latent_image": [latent_id, 0],
            },
            "class_type": "SamplerCustomAdvanced",
        }
        decode_id = self._next_id(counter)
        graph[decode_id] = {
            "inputs": {"samples": [sample_id, 0], "vae": [vae_id, 0]},
            "class_type": "VAEDecode",
        }
        save_id = self._next_id(counter)
        graph[save_id] = {
            "inputs": {"filename_prefix": output_prefix, "images": [decode_id, 0]},
            "class_type": "SaveImage",
        }
        return graph

    def _wait_for_output(self, prompt_id: str) -> Path:
        deadline = time.time() + self.timeout_minutes * 60
        last_status: dict[str, Any] = {}
        while time.time() < deadline:
            history = self._request_json(self.base_url + f"/history/{prompt_id}", timeout=30)
            item = history.get(prompt_id)
            if item:
                last_status = item.get("status") or {}
                outputs = item.get("outputs") or {}
                for node_output in outputs.values():
                    for image in node_output.get("images") or []:
                        filename = image.get("filename")
                        if not filename:
                            continue
                        image_type = image.get("type", "output")
                        subfolder = image.get("subfolder") or ""
                        root = self.comfy_root / ("output" if image_type == "output" else image_type)
                        candidate = root / subfolder / filename
                        if candidate.is_file():
                            return candidate
                serialized = json.dumps(last_status, ensure_ascii=False).lower()
                if "error" in serialized:
                    raise RuntimeError(f"ComfyUI reported an execution error: {last_status}")
            time.sleep(2)
        raise TimeoutError(f"timed out waiting for ComfyUI prompt {prompt_id}: {last_status}")

    def generate(self, request: StaticGenerationRequest, destination: Path) -> GenerationResult:
        request.validate()
        self.verify_runtime()

        reference_names: list[str] = []
        reference_hashes: list[str] = []
        for index, reference in enumerate(request.references, start=1):
            relative_name, source_hash = self._prepare_reference(Path(reference.path), request.job_id, index)
            reference_names.append(relative_name)
            reference_hashes.append(source_hash)

        output_prefix = f"roguelite_asset_studio/{request.job_id}"
        prompt = self._build_prompt(request, reference_names, output_prefix)
        started = time.time()
        submission = self._request_json(self.base_url + "/prompt", {"prompt": prompt}, timeout=60)
        prompt_id = submission.get("prompt_id")
        if not prompt_id:
            raise RuntimeError(f"ComfyUI did not return prompt_id: {submission}")
        generated = self._wait_for_output(prompt_id)
        elapsed = time.time() - started

        destination = Path(destination).resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(generated, destination)
        with Image.open(destination) as image:
            image.load()
            if image.size != (request.width, request.height):
                raise RuntimeError(
                    f"generated size {image.size} differs from requested {(request.width, request.height)}"
                )

        return GenerationResult(
            adapter_id=self.adapter_id,
            prompt_id=prompt_id,
            output_path=destination,
            elapsed_seconds=elapsed,
            request=request,
            reference_hashes=tuple(reference_hashes),
            output_sha256=sha256_file(destination),
        )
