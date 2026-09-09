#!/usr/bin/env python3
"""FLUX.2 Klein 4B Base static-generation/edit adapter.

This is a sibling of the already-proven distilled adapter. It deliberately inherits
reference preparation, HTTP execution, output handling and provenance behavior while
keeping the Base checkpoint/VAE graph explicit and isolated.
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
        for node_name in REQUIRED_NODES:
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
        graph[noise_id] = {
            "inputs": {"noise_seed": int(request.seed)},
            "class_type": "RandomNoise",
        }
        sampler_id = self._next_id(counter)
        graph[sampler_id] = {
            "inputs": {"sampler_name": request.sampler},
            "class_type": "KSamplerSelect",
        }
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
