# H3 H0 Runner47 — required audio VAE integration incident

Status date: **2026-09-08**

Status: **CANONICAL / PRE-INFERENCE INTEGRATION FAIL / FIXED BY RUNNER48**

## Incident

Runner47 started the pinned ComfyUI v0.34.0 server and attempted to submit the H0 Base Ref2VA graph.

ComfyUI rejected the prompt with HTTP 400 before any `prompt_id` was issued:

```text
prompt_outputs_failed_validation
MiniMaxH3ReferenceToVideo
Required input is missing: audio_vae
```

Exact classification: **INTEGRATION_FAIL / PROMPT VALIDATION / PRE-INFERENCE**.

No MiniMax H3 denoising/inference occurred and this incident provides **zero model-quality evidence**.

## Root cause

The initial H0 tooling assumed that the audio VAE could be omitted because:

- H0 supplies no audio reference;
- H0 does not decode/output audio;
- audio is irrelevant to the sprite-production quality decision.

That assumption was wrong for the pinned ComfyUI v0.34.0 API contract. `MiniMaxH3ReferenceToVideo` declares `audio_vae` as a **required** input even when no audio reference is connected. The official ComfyUI R2V workflow also includes the audio VAE.

Therefore the audio VAE is an **integration/schema dependency**, not a change to the intended video-only H0 experiment.

## Required additional file

`models/vae/minimax_h3_audio_vae_fp32.safetensors`

- remote size: **605,254,808 bytes** (~605 MB);
- SHA256: `8e505d95dd1561d47abd43d4238fd40d9bb1ae9e147ed0a4cba778d76ae4db48`;
- source: `Comfy-Org/MiniMax-H3`.

The corrected H0 model payload is therefore approximately **42.5 GB**, not 41.9 GB.

## Fix

New tooling:

- `tools/minimax-h3-spike/run_h0_ref2va_audio_vae_required.py`
- `tools/structured-2d-character-pipeline/48_run_minimax_h3_ref2va_h0_audio_vae_fix.ps1`

Runner48:

1. downloads/resumes the official audio VAE only if absent;
2. verifies exact SHA256 and byte size;
3. starts the same pinned ComfyUI v0.34.0 environment;
4. wires the audio VAE to `MiniMaxH3ReferenceToVideo.audio_vae`;
5. keeps **all H0 quality variables unchanged**;
6. still supplies no audio reference and performs no audio decode;
7. submits the repaired H0 graph.

## H0 quality settings remain unchanged

- Picture1 = canonical Exilada appearance;
- Video1 = same motion driver;
- `448×800`;
- 124 frames at24fps;
- `ref_image_size=match`;
- Base 50 steps;
- `res_multistep` sampler;
- `beta` scheduler;
- seed0;
- default H3 video/audio sigma shifts12/3;
- no FL2VA;
- no Turbo LoRA;
- no style embedding;
- no audio reference;
- no audio output/decode.

## Current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\48_run_minimax_h3_ref2va_h0_audio_vae_fix.ps1"
```

If Runner48 emits `H3-H0: prompt_id=...`, the integration fix passed prompt validation and actual H3 inference started.
