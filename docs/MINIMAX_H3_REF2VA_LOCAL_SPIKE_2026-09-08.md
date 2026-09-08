# MiniMax H3 Base Ref2VA — local production screening spike

Status date: **2026-09-08**

Status: **CANONICAL / H3 ACTIVE / RUNNER46 BOOTSTRAP PASS / RUNNER47 PRE-INFERENCE INTEGRATION FAIL / RUNNER48 CURRENT**

Canonical project state: `docs/PROJECT_STATE.md`.

Incident record: `docs/H3_H0_RUNNER47_AUDIO_VAE_INTEGRATION_FAIL_2026-09-08.md`.

## Purpose

Determine whether **MiniMax H3 Base Ref2VA** can satisfy the Roguelite complete-character production contract on Windows11 / RTX3060 12GB /48GB RAM:

`Exilada appearance reference + arbitrary real driving video -> complete coherent animated character -> automatic gameplay-scale conversion -> spritesheet`

No routine manual rigging, keyframing, repair, masks, repainting or hand compositing.

## Transition from Wan

Wan-Animate-2 is **PAUSED AFTER W1L**, not exhausted. Preserve local W1L evidence. Do not launch another Wan run while H3 is active.

## Why Ref2VA

`MiniMaxH3ReferenceToVideo` accepts multimodal references:

- `<Picture 1>` = Exilada appearance/identity/anatomy/clothing/hair/art language;
- `<Video 1>` = movement/performance/timing/weight transfer only.

The prompt explicitly ignores the driver's identity/body/clothing/hair/environment/style.

## Runner46 result

Runner46 completed successfully and proved:

- pinned ComfyUI v0.34.0 can launch locally;
- initial selected checkpoints hash correctly;
- Exilada and driver inputs are prepared;
- H3/core node classes and object-info are present.

This is an **infrastructure/bootstrap pass**, not a complete API graph-integration proof.

## Runner47 incident — integration only

First H0 submission was rejected before `prompt_id`:

```text
HTTP 400
prompt_outputs_failed_validation
MiniMaxH3ReferenceToVideo
Required input is missing: audio_vae
```

Classification: **INTEGRATION_FAIL / PRE-INFERENCE**.

No H3 sampling occurred. This gives no model-quality evidence and does not justify changing H0 resolution, sampling, seed, references or prompt.

### Root cause

The initial tooling omitted the audio VAE because H0 does not use or decode audio. In pinned ComfyUI v0.34.0 that is invalid: `MiniMaxH3ReferenceToVideo` declares `audio_vae` as required regardless of whether audio references are connected.

The official R2V workflow also includes this dependency.

## Corrected pinned H0 model set

1. `models/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors`
   - ~21GB;
   - SHA256 `9255f52b6677845ad238f20dfaafa94727053694127ab7f255c048f0f9365779`.
2. `models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
   - ~15.7GB;
   - SHA256 `35a88d51044231fe332301d7a62aa81e3f2cba62febeb446e2c1e3e0ef76f2c6`.
3. `models/vae/minimax_h3_video_vae_fp16.safetensors`
   - 5,207,808,496 bytes (~5.21GB);
   - SHA256 `7c1f131492e7eddacaac9069a61b81bdd39de5cc96561e677c5eab1cdce5e522`.
4. **`models/vae/minimax_h3_audio_vae_fp32.safetensors`**
   - **605,254,808 bytes (~605MB)**;
   - SHA256 `8e505d95dd1561d47abd43d4238fd40d9bb1ae9e147ed0a4cba778d76ae4db48`.

Corrected H0 H3 payload is approximately **42.5GB**.

The audio VAE is a required node-schema dependency only. H0 still supplies no audio reference and performs no audio decode/output.

## Explicitly excluded

Do not download:

- H3 FL2VA checkpoint;
- alternate Ref2VA quantizations;
- Turbo LoRA;
- style embeddings.

## H0 input preparation

Appearance:

`assets/source/characters/exilada/reference/exilada_master.png`

Prepared driver:

`ComfyUI/input/roguelite_h3/h0_driver_24fps_124f.mp4`

Driver normalization remains:

- exactly124 frames at24fps;
- no crop;
- no resize;
- no tracking/recentering/stabilization;
- audio removed;
- timestamp resampling only.

## H0 exact quality baseline — unchanged

- task `ref2va`;
- `448×800`;
-124 frames @24fps;
- `ref_image_size=match`;
-50 steps;
- `res_multistep` sampler;
- `beta` scheduler;
- seed0;
- H3 default sigma shifts video12/audio3;
- no Turbo;
- no negative-conditioning branch;
- fixed camera/full-body/topology stability requested in prompt;
- Picture1 = Exilada appearance;
- Video1 = motion only;
- audio VAE wired only because required by schema.

## Why 448×800 first

Runtime protagonist is ~128px tall. `448×800` is deliberately below a 768-short-edge source to test the smallest useful generation scale while preserving several-times supersampling for final sprite use.

Finite resolution ladder only after completed H0 evidence:

1. `448×800`;
2. `480×864` if specifically under-resolved;
3. `512×896` if still needed;
4. one 768-short-edge control only if necessary to separate resolution failure from model/task failure.

If motion/topology is excellent and identity alone weak, test `ref_image_size=max` before increasing output resolution.

## Dual-scale QA

Full-resolution hard checks:

- stable head/torso/two arms/two hands/two legs/two feet;
- no detached/duplicated/swapped/fused/disappearing limbs;
- stable torso/breast/hip anatomy;
- Exilada identity preserved;
- motion timing/weight follows driver;
- long hair/cloth dynamic but attached;
- restraints remain accessories, not flesh/limbs;
- no destructive global smear/ghost double.

Gameplay proxy:

`Z:\AI\MiniMaxH3\h0_gameplay_scale_proxy_frame160.mp4`

Downsampling may make minor texture noise/local blur irrelevant, but cannot excuse topology loss or identity drift.

## CURRENT OPERATOR ACTION — Runner48

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\48_run_minimax_h3_ref2va_h0_audio_vae_fix.ps1"
```

Runner48:

1. downloads/resumes the official audio VAE if absent;
2. verifies exact SHA256 and byte size;
3. starts pinned ComfyUI v0.34.0;
4. wires `audio_vae` to the Ref2VA node;
5. retains all H0 quality settings exactly;
6. submits the repaired graph.

If terminal prints:

```text
H3-H0: prompt_id=...
```

real H3 inference has started.

Expected proof after completion:

- `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- `Z:\AI\MiniMaxH3\h0_run_manifest.json`;
- `Z:\AI\MiniMaxH3\h0_api_prompt.json`;
- `Z:\AI\MiniMaxH3\h0_executor.log`;
- gameplay proxy when preview encoding succeeds.

## Failure classification

- download/hash/extract/version -> `INFRASTRUCTURE FAIL`;
- missing/changed node/API graph -> `INTEGRATION FAIL`;
- CUDA/DynamicVRAM/host-buffer/OOM/runtime crash -> `INFRASTRUCTURE FAIL` until diagnosed;
- completed video with poor character behavior -> `MODEL/TASK` or `CONFIGURATION` evidence according to defect.

No manual repair can convert a failed production route into a production PASS.

## Cleanup

- keep one Ref2VA quantization only;
- audio VAE is now part of the minimum active Ref2VA set;
- no FL2VA/Turbo/style assets unless a later explicit hypothesis requires them;
- preserve Wan W1L proof/results;
- remove paused Wan large checkpoint weights only after H3 is technically proven active enough that immediate return is unnecessary;
- keep SSD/Moore comparison evidence until explicit abandonment/final verdict.
