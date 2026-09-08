# MiniMax H3 Ref2VA local spike tooling

Status: **ACTIVE — H3 Base Ref2VA is the current complete-character screening route. Runner46 prepares the pinned stack; Runner47 runs H0. Wan is paused after W1L.**

Canonical procedure: `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`.

## Paths

- project: `D:\GOOGLE DRIVE\DEV\Roguelite`
- H3 workspace: `Z:\AI\MiniMaxH3`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- `D:\AI` is stale/invalid.

## H0 stack

Pinned ComfyUI:

- `v0.34.0` NVIDIA Windows portable;
- dedicated H3 environment;
- port `8190`;
- default DynamicVRAM behavior;
- no custom nodes for H0.

Downloaded H3 files only:

- `minimax_h3_ref2va_pruned_int8_convrot.safetensors`
- `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- `minimax_h3_video_vae_fp16.safetensors`

No FL2VA checkpoint, no Turbo LoRA, no style embeddings, no audio VAE.

## Tool files

### `prepare_h0_driver.py`

Temporal normalizer for the same raw motion driver used by the Wan comparison branch.

- output 24 fps;
- exactly 124 frames;
- no spatial crop;
- no resize;
- no tracking/recentering/stabilization;
- audio removed;
- writes `h0_driver_manifest.json`.

### `run_h0_ref2va.py`

Builds the exact ComfyUI API graph for H0 and submits it.

H0 settings:

- Ref2VA Base;
- Picture1 = Exilada appearance;
- Video1 = movement/performance;
- `448×800`;
- 124 frames at 24 fps;
- `ref_image_size=match`;
- 50 steps;
- `res_multistep`;
- `beta` scheduler;
- seed0;
- no Turbo LoRA.

It writes:

- `h0_api_prompt.json`;
- `h0_run_manifest.json`;
- canonical H0 video;
- small whole-frame gameplay-scale proxy when PyAV encoding succeeds.

## Operator sequence

First:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\46_prepare_minimax_h3_ref2va.ps1"
```

Runner46 is **bootstrap/preflight only**. It downloads/verifies the selected files and validates the live H3/core node set. It does not infer.

After Runner46 PASS:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\47_run_minimax_h3_ref2va_h0.ps1"
```

## Classification rule

A download/CUDA/DynamicVRAM/API/runtime failure is not a model-quality failure. Preserve the exact Runner47 diagnostics and Comfy stdout/stderr and classify the failure layer first.

A completed video is also not automatically a production PASS. Review full-resolution body topology/identity/motion first, then the gameplay-scale proxy.

## Finite next branches

Only after H0 evidence:

- identity weak but motion/topology strong → try `ref_image_size=max`;
- anatomy under-resolved → `480×864`, then `512×896`, then at most one 768-short-edge control;
- do not blindly grid-search settings;
- do not download FL2VA unless a later explicit hypothesis requires that task family.

## Cleanup

Do not accumulate alternate H3 quantizations. Once H3 is technically proven active and the project chooses not to return immediately to Wan, clean the paused Wan large model weights while preserving W1L proof/results/manifests.
