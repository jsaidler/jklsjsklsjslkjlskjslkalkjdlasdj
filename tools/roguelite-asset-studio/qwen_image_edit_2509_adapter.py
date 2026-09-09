#!/usr/bin/env python3
"""Native ComfyUI adapter for Qwen-Image-Edit-2509.

This adapter is UI-independent and follows the ComfyUI 2509 blueprint pinned by the
Roguelite Asset Studio runtime. It is intentionally separate from the Klein adapters.

Key graph semantics:
- Qwen 2509 FP8 edit diffusion checkpoint;
- Qwen2.5-VL 7B FP8 text/vision encoder loaded on CPU for 12 GB VRAM feasibility;
- qwen_image_vae;
- primary image scaled through FluxKontextImageScale;
- primary scaled image VAE-encoded as the KSampler latent image;
- TextEncodeQwenImageEditPlus receives the same semantic image references on positive
  and negative branches (negative prompt defaults to empty);
- ModelSamplingAuraFlow shift=3;
- CFGNorm strength=1;
- native non-Lightning recipe: Euler / simple / denoise=1, 20 steps, CFG 4.

The model supports up to three images. Asset Studio semantic roles remain in the request
layer; this adapter preserves their declared order as image1/image2/image3.
"""

from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import Any

from PIL import Image

from adapter_protocol import GenerationResult, StaticGenerationRequest
from flux2_klein_adapter import Flux2KleinAdapter, sha256_file

MODEL = "qwen_image_edit_2509_fp8_e4m3fn.safetensors"
MODEL_SHA256 = "318568f61951ab9da21100c7b896e3c1da67f0d2efad6421545e022cfaa2b2b4"
TEXT_ENCODER = "qwen_2.5_vl_7b_fp8_scaled.safetensors"
TEXT_ENCODER_SHA256 = "cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4"
VAE = "qwen_image_vae.safetensors"
VAE_SHA256 = "a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f"

REQUIRED_NODES = (
    "UNETLoader",
    "CLIPLoader",
    "VAELoader",
    "LoadImage",
    "FluxKontextImageScale",
    "TextEncodeQwenImageEditPlus",
    "VAEEncode",
    "ModelSamplingAuraFlow",
    "CFGNorm",
    "KSampler",
    "VAEDecode",
    "SaveImage",
)


class QwenImageEdit2509Adapter(Flux2KleinAdapter):
    adapter_id = "qwen_image_edit_2509_fp8"

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
        self._verify_file(
            self.comfy_root / "models" / "vae" / VAE,
            VAE_SHA256,
            VAE,
        )
        for node_name in REQUIRED_NODES:
            info = self._request_json(self.base_url + f"/object_info/{node_name}", timeout=30)
            if node_name not in info:
                raise RuntimeError(f"required native ComfyUI node unavailable: {node_name}")
        self._verified = True

    def _prepare_reference_native(self, source: Path, job_id: str, index: int) -> tuple[str, str]:
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
            # Do not pre-scale. The native Qwen nodes own reference scaling/conditioning.
            image.save(target, format="PNG")
        relative = target.relative_to(self.comfy_root / "input").as_posix()
        return relative, sha256_file(source)

    @staticmethod
    def _next_id(counter: list[int]) -> str:
        value = str(counter[0])
        counter[0] += 1
        return value

    def _build_prompt(self, request: StaticGenerationRequest, reference_names: list[str], output_prefix: str) -> dict[str, Any]:
        if not reference_names:
            raise ValueError("Qwen-Image-Edit-2509 requires at least one reference image")
        if len(reference_names) > 3:
            raise ValueError("Qwen-Image-Edit-2509 native Plus node supports at most three images")

        counter = [1]
        graph: dict[str, Any] = {}

        model_id = self._next_id(counter)
        graph[model_id] = {
            "inputs": {"unet_name": MODEL, "weight_dtype": "default"},
            "class_type": "UNETLoader",
        }
        clip_id = self._next_id(counter)
        graph[clip_id] = {
            "inputs": {"clip_name": TEXT_ENCODER, "type": "qwen_image", "device": "cpu"},
            "class_type": "CLIPLoader",
        }
        vae_id = self._next_id(counter)
        graph[vae_id] = {"inputs": {"vae_name": VAE}, "class_type": "VAELoader"}

        load_ids: list[str] = []
        for name in reference_names:
            load_id = self._next_id(counter)
            graph[load_id] = {"inputs": {"image": name}, "class_type": "LoadImage"}
            load_ids.append(load_id)

        primary_scale_id = self._next_id(counter)
        graph[primary_scale_id] = {
            "inputs": {"image": [load_ids[0], 0]},
            "class_type": "FluxKontextImageScale",
        }

        primary_latent_id = self._next_id(counter)
        graph[primary_latent_id] = {
            "inputs": {"pixels": [primary_scale_id, 0], "vae": [vae_id, 0]},
            "class_type": "VAEEncode",
        }

        def qwen_conditioning(text: str) -> str:
            node_id = self._next_id(counter)
            inputs: dict[str, Any] = {
                "clip": [clip_id, 0],
                "vae": [vae_id, 0],
                "prompt": text,
                "image1": [primary_scale_id, 0],
            }
            if len(load_ids) >= 2:
                inputs["image2"] = [load_ids[1], 0]
            if len(load_ids) >= 3:
                inputs["image3"] = [load_ids[2], 0]
            graph[node_id] = {"inputs": inputs, "class_type": "TextEncodeQwenImageEditPlus"}
            return node_id

        positive_id = qwen_conditioning(request.prompt)
        negative_id = qwen_conditioning(request.negative or "")

        sampling_id = self._next_id(counter)
        graph[sampling_id] = {
            "inputs": {"model": [model_id, 0], "shift": 3.0},
            "class_type": "ModelSamplingAuraFlow",
        }
        cfgnorm_id = self._next_id(counter)
        graph[cfgnorm_id] = {
            "inputs": {"model": [sampling_id, 0], "strength": 1.0},
            "class_type": "CFGNorm",
        }
        sampler_id = self._next_id(counter)
        graph[sampler_id] = {
            "inputs": {
                "seed": int(request.seed),
                "steps": int(request.steps),
                "cfg": float(request.cfg),
                "sampler_name": request.sampler,
                "scheduler": "simple",
                "denoise": 1.0,
                "model": [cfgnorm_id, 0],
                "positive": [positive_id, 0],
                "negative": [negative_id, 0],
                "latent_image": [primary_latent_id, 0],
            },
            "class_type": "KSampler",
        }
        decode_id = self._next_id(counter)
        graph[decode_id] = {
            "inputs": {"samples": [sampler_id, 0], "vae": [vae_id, 0]},
            "class_type": "VAEDecode",
        }
        save_id = self._next_id(counter)
        graph[save_id] = {
            "inputs": {"filename_prefix": output_prefix, "images": [decode_id, 0]},
            "class_type": "SaveImage",
        }
        return graph

    def generate(self, request: StaticGenerationRequest, destination: Path) -> GenerationResult:
        request.validate()
        if not (1 <= len(request.references) <= 3):
            raise ValueError("Qwen-Image-Edit-2509 requires one to three references")
        self.verify_runtime()

        reference_names: list[str] = []
        reference_hashes: list[str] = []
        for index, reference in enumerate(request.references, start=1):
            name, digest = self._prepare_reference_native(Path(reference.path), request.job_id, index)
            reference_names.append(name)
            reference_hashes.append(digest)

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
            if image.width < 16 or image.height < 16:
                raise RuntimeError(f"invalid generated image size: {image.size}")

        return GenerationResult(
            adapter_id=self.adapter_id,
            prompt_id=prompt_id,
            output_path=destination,
            elapsed_seconds=elapsed,
            request=request,
            reference_hashes=tuple(reference_hashes),
            output_sha256=sha256_file(destination),
        )
