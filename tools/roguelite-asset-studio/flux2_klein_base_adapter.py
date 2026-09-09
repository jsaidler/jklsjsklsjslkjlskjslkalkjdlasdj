#!/usr/bin/env python3
"""FLUX.2 Klein 4B Base static-generation/edit adapter.

This is a sibling of the proven distilled adapter. It inherits the generic Asset Studio
HTTP/provenance boundary but keeps the Base checkpoint/VAE graph explicit.

Important: Base edit conditioning follows the current official ComfyUI Klein 4B Base
workflow rather than reusing the distilled harness shortcut. In particular:

- positive text is encoded normally;
- negative text is encoded separately (empty by default), not made by zeroing the
  positive conditioning;
- every reference is scaled to 1 MP with ImageScaleToTotalPixels/nearest-exact;
- the same encoded reference latent is appended to positive and negative conditioning;
- for reference edits, scheduler/empty-latent dimensions are derived from the first
  scaled reference, matching the official workflow's geometry contract.

This distinction matters for Base because its official recipe uses CFG 5. At CFG 1 the
negative branch is effectively inert, which is why the earlier distilled tests did not
expose the same failure mode.
"""

from __future__ import annotations

from typing import Any

from flux2_klein_adapter import (
    REQUIRED_NODES,
    TEXT_ENCODER,
    TEXT_ENCODER_SHA256,
    Flux2KleinAdapter,
)

BASE_MODEL = "flux-2-klein-base-4b-fp8.safetensors"
BASE_MODEL_SHA256 = "44bab3a86fe98b85d21dd2a4729ebdc3ae51fb8a39f76e457e18c724219e6840"
BASE_VAE = "full_encoder_small_decoder.safetensors"
BASE_VAE_SHA256 = "ea4273f02d1fafbf8e1d1c2cf6018ed8748652eb0bf34f2dd91171f16f15ab62"

BASE_EXTRA_NODES = (
    "ImageScaleToTotalPixels",
    "GetImageSize",
)


class Flux2KleinBaseAdapter(Flux2KleinAdapter):
    adapter_id = "flux2_klein_4b_base"

    def verify_runtime(self) -> None:
        if self._verified:
            return
        self._request_json(self.base_url + "/system_stats", timeout=15)
        self._verify_file(
            self.comfy_root / "models" / "diffusion_models" / BASE_MODEL,
            BASE_MODEL_SHA256,
            BASE_MODEL,
        )
        self._verify_file(
            self.comfy_root / "models" / "text_encoders" / TEXT_ENCODER,
            TEXT_ENCODER_SHA256,
            TEXT_ENCODER,
        )
        self._verify_file(
            self.comfy_root / "models" / "vae" / BASE_VAE,
            BASE_VAE_SHA256,
            BASE_VAE,
        )
        for node_name in (*REQUIRED_NODES, *BASE_EXTRA_NODES):
            info = self._request_json(self.base_url + f"/object_info/{node_name}", timeout=30)
            if node_name not in info:
                raise RuntimeError(f"required native ComfyUI node unavailable: {node_name}")
        self._verified = True

    def _build_prompt(
        self,
        request,
        reference_names: list[str],
        output_prefix: str,
    ) -> dict[str, Any]:
        counter = [1]
        graph: dict[str, Any] = {}

        model_id = self._next_id(counter)
        graph[model_id] = {
            "inputs": {"unet_name": BASE_MODEL, "weight_dtype": "default"},
            "class_type": "UNETLoader",
        }
        clip_id = self._next_id(counter)
        graph[clip_id] = {
            "inputs": {"clip_name": TEXT_ENCODER, "type": "flux2", "device": "default"},
            "class_type": "CLIPLoader",
        }
        vae_id = self._next_id(counter)
        graph[vae_id] = {"inputs": {"vae_name": BASE_VAE}, "class_type": "VAELoader"}

        positive_id = self._next_id(counter)
        graph[positive_id] = {
            "inputs": {"text": request.prompt, "clip": [clip_id, 0]},
            "class_type": "CLIPTextEncode",
        }
        negative_id = self._next_id(counter)
        graph[negative_id] = {
            "inputs": {"text": request.negative or "", "clip": [clip_id, 0]},
            "class_type": "CLIPTextEncode",
        }

        positive_ref: list[Any] = [positive_id, 0]
        negative_ref: list[Any] = [negative_id, 0]
        first_size_id: str | None = None

        for reference_name in reference_names:
            load_id = self._next_id(counter)
            graph[load_id] = {
                "inputs": {"image": reference_name},
                "class_type": "LoadImage",
            }
            scale_id = self._next_id(counter)
            graph[scale_id] = {
                "inputs": {
                    "image": [load_id, 0],
                    "upscale_method": "nearest-exact",
                    "megapixels": 1.0,
                    "resolution_steps": 1,
                },
                "class_type": "ImageScaleToTotalPixels",
            }
            if first_size_id is None:
                first_size_id = self._next_id(counter)
                graph[first_size_id] = {
                    "inputs": {"image": [scale_id, 0]},
                    "class_type": "GetImageSize",
                }
            encode_id = self._next_id(counter)
            graph[encode_id] = {
                "inputs": {"pixels": [scale_id, 0], "vae": [vae_id, 0]},
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
        graph[noise_id] = {
            "inputs": {"noise_seed": int(request.seed)},
            "class_type": "RandomNoise",
        }
        sampler_id = self._next_id(counter)
        graph[sampler_id] = {
            "inputs": {"sampler_name": request.sampler},
            "class_type": "KSamplerSelect",
        }

        if first_size_id is not None:
            width_input: Any = [first_size_id, 0]
            height_input: Any = [first_size_id, 1]
        else:
            width_input = int(request.width)
            height_input = int(request.height)

        scheduler_id = self._next_id(counter)
        graph[scheduler_id] = {
            "inputs": {
                "steps": int(request.steps),
                "width": width_input,
                "height": height_input,
            },
            "class_type": "Flux2Scheduler",
        }
        latent_id = self._next_id(counter)
        graph[latent_id] = {
            "inputs": {
                "width": width_input,
                "height": height_input,
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
