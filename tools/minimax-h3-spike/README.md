# MiniMax H3 Ref2VA local spike tooling

Status: **ACTIVE — H3 Base Ref2VA is the current complete-character screening route. Runner46 bootstrap/preflight PASSED; Runner47 runs H0 now. Wan is paused after W1L.**

Canonical procedure: `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`.

## Paths

- project: `D:\GOOGLE DRIVE\DEV\Roguelite`
- H3 workspace: `Z:\AI\MiniMaxH3`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- `D:\AI` is stale/invalid.

## Runner46 result — PASS

Operator result on 2026-09-08:

`RUNNER46-H3-PREP: PASS - H3 REF2VA H0 BOOTSTRAP READY`

Prepared/verified:

- `Z:\AI\MiniMaxH3\ComfyUI_windows_portable\ComfyUI`;
- `Z:\AI\MiniMaxH3\h3_bootstrap_manifest.json`;
- `Z:\AI\MiniMaxH3\h0_driver_manifest.json`;
- `Z:\AI\MiniMaxH3\h3_required_object_info.json`;
- selected ~41.9GB model payload only.

Classification: infrastructure/integration bootstrap PASS. No H3 model-quality inference happened in Runner46.

## H0 stack

Pinned ComfyUI:

- `v0.34.0` NVIDIA Windows portable;
- dedicated H3 environment;
- port `8190`;
- default DynamicVRAM behavior;
- no custom nodes for H0.

Installed H3 files only:

- `minimax_h3_ref2va_pruned_int8_convrot.safetensors`
- `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- `minimax_h3_video_vae_fp16.safetensors`

No FL2VA checkpoint, no Turbo LoRA, no style embeddings, no audio VAE.

## Tool files

### `prepare_h0_driver.py`

Temporal normalizer for the same raw motion driver used by the Wan comparison branch.

- output24fps;
- exactly124 frames;
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
-124 frames at24fps;
- `ref_image_size=match`;
-50 steps;
- `res_multistep`;
- `beta` scheduler;
- seed0;
- no Turbo LoRA.

It writes:

- `h0_api_prompt.json`;
- `h0_run_manifest.json`;
- canonical H0 video;
- small whole-frame gameplay-scale proxy when PyAV encoding succeeds.

## Current operator sequence

Runner46 is complete. Run Runner47:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\47_run_minimax_h3_ref2va_h0.ps1"
```

If the executor prints `H3-H0: prompt_id=...`, real H3 inference has started.

## Classification rule

A CUDA/DynamicVRAM/API/runtime failure is not a model-quality failure. Preserve the exact Runner47 diagnostics and Comfy stdout/stderr and classify the failure layer first.

A completed video is also not automatically a production PASS. Review full-resolution body topology/identity/motion first, then the gameplay-scale proxy.

## Finite next branches

Only after H0 evidence:

- identity weak but motion/topology strong → try `ref_image_size=max`;
- anatomy under-resolved → `480×864`, then `512×896`, then at most one768-short-edge control;
- do not blindly grid-search settings;
- do not download FL2VA unless a later explicit hypothesis requires that task family.

## Cleanup

Do not accumulate alternate H3 quantizations. Once H3 is technically proven active and the project chooses not to return immediately to Wan, clean the paused Wan large model weights while preserving W1L proof/results/manifests.
