#!/usr/bin/env python3
"""Native ComfyUI adapter for SDXL Inpainting 0.1.

This backend is deliberately narrow: it is the mask-native structural fill/remove
specialist behind the Roguelite Asset Studio automatic-mask contract.

The user never draws the production mask. The mask comes from the accepted
perception/structural pipeline (GroundingDINO/SAM2/repeated-element decomposition).

Runtime graph:
- dedicated SDXL Inpainting 0.1 FP16 UNet;
- SDXL Base 1.0 checkpoint used only as CLIP/VAE authority;
- source image + automatic mask;
- InpaintModelConditioning;
- KSampler;
- VAEDecode.

The base checkpoint MODEL output is intentionally unused.
"""

from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import Any

from PIL import Image

from adapter_protocol import GenerationResult, StaticGenerationRequest
from flux2_klein_adapter import Flux2KleinAdapter, sha256_file

INPAINT_UNET = "sdxl_inpaint_0.1_fp16.safetensors"
INPAINT_UNET_SHA256 = "6470840731e98cc16713ddf3ac7ee458c9fdbcb881a98c6727cd4a938f227d3f"
BASE_CHECKPOINT = "sd_xl_base_1.0.safetensors"
BASE_CHECKPOINT_SHA256 = "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b"

REQUIRED_NODES = (
    "UNETLoader",
    "CheckpointLoaderSimple",
    "LoadImage",
    "ImageToMask",
    "CLIPTextEncode",
    "InpaintModelConditioning",
    "KSampler",
    "VAEDecode",
    "SaveImage",
)


class SDXLInpaintAdapter(Flux2KleinAdapter):
    adapter_id = "sdxl_inpaint_0_1_fp16"

    def verify_runtime(self) -> None:
        if self._verified:
            return
        self._request_json(self.base_url + "/system_stats", timeout=15)
        self._verify_file(
            self.comfy_root / "models" / "diffusion_models" / INPAINT_UNET,
            INPAINT_UNET_SHA256,
            INPAINT_UNET,
        )
        self._verify_file(
            self.comfy_root / "models" / "checkpoints" / BASE_CHECKPOINT,
            BASE_CHECKPOINT_SHA256,
            BASE_CHECKPOINT,
        )
        for node_name in REQUIRED_NODES:
            info = self._request_json(self.base_url + f"/object_info/{node_name}", timeout=30)
            if node_name not in info:
                raise RuntimeError(f"required native ComfyUI node unavailable: {node_name}")
        self._verified = True

    def _prepare_image_native(self, source: Path, job_id: str, filename: str, mask: bool = False) -> tuple[str, str]:
        source = Path(source).resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        target_dir = self.comfy_root / "input" / "roguelite_asset_studio" / job_id
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / filename
        with Image.open(source) as opened:
            opened.load()
            if mask:
                m = opened.convert("L")
                Image.merge("RGB", (m, m, m)).save(target, format="PNG")
            elif "A" in opened.getbands():
                rgba = opened.convert("RGBA")
                background = Image.new("RGBA", rgba.size, (128, 128, 128, 255))
                background.alpha_composite(rgba)
                background.convert("RGB").save(target, format="PNG")
            else:
                opened.convert("RGB").save(target, format="PNG")
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
        source_name: str,
        mask_name: str,
        output_prefix: str,
    ) -> dict[str, Any]:
        counter = [1]
        graph: dict[str, Any] = {}

        unet_id = self._next_id(counter)
        graph[unet_id] = {
            "inputs": {"unet_name": INPAINT_UNET, "weight_dtype": "default"},
            "class_type": "UNETLoader",
        }
        base_id = self._next_id(counter)
        graph[base_id] = {
            "inputs": {"ckpt_name": BASE_CHECKPOINT},
            "class_type": "CheckpointLoaderSimple",
        }
        source_id = self._next_id(counter)
        graph[source_id] = {"inputs": {"image": source_name}, "class_type": "LoadImage"}
        mask_load_id = self._next_id(counter)
        graph[mask_load_id] = {"inputs": {"image": mask_name}, "class_type": "LoadImage"}
        mask_id = self._next_id(counter)
        graph[mask_id] = {
            "inputs": {"image": [mask_load_id, 0], "channel": "red"},
            "class_type": "ImageToMask",
        }

        pos_id = self._next_id(counter)
        graph[pos_id] = {
            "inputs": {"text": request.prompt, "clip": [base_id, 1]},
            "class_type": "CLIPTextEncode",
        }
        neg_id = self._next_id(counter)
        graph[neg_id] = {
            "inputs": {"text": request.negative or "", "clip": [base_id, 1]},
            "class_type": "CLIPTextEncode",
        }
        inpaint_id = self._next_id(counter)
        graph[inpaint_id] = {
            "inputs": {
                "positive": [pos_id, 0],
                "negative": [neg_id, 0],
                "vae": [base_id, 2],
                "pixels": [source_id, 0],
                "mask": [mask_id, 0],
                "noise_mask": True,
            },
            "class_type": "InpaintModelConditioning",
        }
        sampler_id = self._next_id(counter)
        graph[sampler_id] = {
            "inputs": {
                "seed": int(request.seed),
                "steps": int(request.steps),
                "cfg": float(request.cfg),
                "sampler_name": request.sampler,
                "scheduler": "karras",
                "denoise": 1.0,
                "model": [unet_id, 0],
                "positive": [inpaint_id, 0],
                "negative": [inpaint_id, 1],
                "latent_image": [inpaint_id, 2],
            },
            "class_type": "KSampler",
        }
        decode_id = self._next_id(counter)
        graph[decode_id] = {
            "inputs": {"samples": [sampler_id, 0], "vae": [base_id, 2]},
            "class_type": "VAEDecode",
        }
        save_id = self._next_id(counter)
        graph[save_id] = {
            "inputs": {"filename_prefix": output_prefix, "images": [decode_id, 0]},
            "class_type": "SaveImage",
        }
        return graph

    def generate_masked(
        self,
        request: StaticGenerationRequest,
        automatic_mask: Path,
        destination: Path,
    ) -> GenerationResult:
        request.validate()
        if len(request.references) != 1:
            raise ValueError("SDXL inpaint path requires exactly one source-image reference")
        self.verify_runtime()

        source_name, source_hash = self._prepare_image_native(
            Path(request.references[0].path), request.job_id, "source.png", mask=False
        )
        mask_name, mask_hash = self._prepare_image_native(
            Path(automatic_mask), request.job_id, "automatic_mask.png", mask=True
        )
        output_prefix = f"roguelite_asset_studio/{request.job_id}"
        prompt = self._build_prompt(request, source_name, mask_name, output_prefix)

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
            reference_hashes=(source_hash, mask_hash),
            output_sha256=sha256_file(destination),
        )
