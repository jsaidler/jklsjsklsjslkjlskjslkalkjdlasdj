# MiniMax H3 Ref2VA local spike tooling

Status: **ACTIVE — H0 completed as PASS_CANDIDATE; next gate is a game-relevant walking driver. Wan is paused after W1L.**

Canonical procedure: `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`.

Incident: `docs/H3_H0_RUNNER47_AUDIO_VAE_INTEGRATION_FAIL_2026-09-08.md`.

## Paths

- project: `D:\GOOGLE DRIVE\DEV\Roguelite`
- H3 workspace: `Z:\AI\MiniMaxH3`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- `D:\AI` stale/invalid.

## Integration history

Runner46 prepared the pinned H3 environment. Runner47 exposed a pre-inference omission: pinned `MiniMaxH3ReferenceToVideo` requires `audio_vae` even when no audio reference is used. Runner48 added only that dependency and completed the unchanged H0.

The Runner47 failure is historical integration evidence only; it is not a model-quality failure.

## Minimal active H3 set

- `minimax_h3_ref2va_pruned_int8_convrot.safetensors`
- `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- `minimax_h3_video_vae_fp16.safetensors`
- `minimax_h3_audio_vae_fp32.safetensors` — required schema dependency

Total ~42.5GB. No FL2VA checkpoint, Turbo LoRA, style embedding or alternate quantization.

## Tool files

### `prepare_h0_driver.py`

Outputs the same Wan comparison driver at24fps/124f with no crop/resize/tracking/recentering and no audio.

### `run_h0_ref2va.py`

Base H0 executor.

### `run_h0_ref2va_audio_vae_required.py`

Current Ref2VA integration wrapper. It wires the schema-required audio VAE, delegates the unchanged quality run to the base executor and annotates the manifest. Future manifests also record the audio VAE at top level.

## H0 completed baseline

- Base Ref2VA;
- Picture1 = Exilada appearance;
- Video1 = movement/performance;
- `448×800`;
-124 frames @24fps;
- `ref_image_size=match`;
-50 steps;
- `res_multistep`;
- `beta`;
- seed0;
- no Turbo;
- no audio reference/decode.

Completed prompt id: `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`.

Elapsed: `4504.8s`.

Canonical output:

`Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`

Gameplay proxy:

`Z:\AI\MiniMaxH3\h0_gameplay_scale_proxy_frame160.mp4`

## H0 verdict

**PASS_CANDIDATE / FAMILY ADVANCES.**

Visual review found stable body topology, no destructive whole-body smear, coherent hair/cloth secondary motion, readable restraints and strong gameplay-scale silhouette. Residual chain-detail drift remains. Late right-foot crop is treated as a driver/framing-envelope problem, not anatomy collapse.

`448×800` passes; do not increase resolution or use `ref_image_size=max` without a specific later failure.

## Next gate

Use a real game-relevant walking driver:

- fixed camera;
- one adult full-body performer;
- screen-left movement;
- mostly lateral/slight3/4 targeting the locked `72°` baseline;
- complete gait cycle;
- safe head/feet/lateral margins.

Keep H0 quality settings for the first walk test. After walking passes, stress hair/cloth/wind/restraints. Optimize speed/Turbo only later.

## Classification rule

API-schema/CUDA/DynamicVRAM/runtime failures are not model-quality failures. A completed video is judged at full resolution and gameplay scale.

## Cleanup

H3 is now proven active enough that paused Wan large weights may be deleted while preserving W1H/W1L proof/results. Keep the minimal H3 four-file set and do not accumulate alternate H3 variants without an explicit hypothesis.
