# MiniMax H3 Ref2VA local spike tooling

Status: **ACTIVE — Runner46 bootstrap passed; Runner47 exposed a pre-inference `audio_vae` integration omission; Runner48 is the current H0 gate. Wan is paused after W1L.**

Canonical procedure: `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`.

Incident: `docs/H3_H0_RUNNER47_AUDIO_VAE_INTEGRATION_FAIL_2026-09-08.md`.

## Paths

- project: `D:\GOOGLE DRIVE\DEV\Roguelite`
- H3 workspace: `Z:\AI\MiniMaxH3`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- `D:\AI` stale/invalid.

## Runner46

Bootstrap/install preflight passed and prepared the pinned ComfyUI environment, initial model files and inputs. It did not perform inference and did not prove the final graph had every required input.

## Runner47 incident

The first H0 prompt was rejected before `prompt_id`:

```text
MiniMaxH3ReferenceToVideo
Required input is missing: audio_vae
```

Classification: **INTEGRATION_FAIL / PRE-INFERENCE**. No H3 model-quality evidence exists from Runner47.

Pinned ComfyUI v0.34.0 requires `audio_vae` on the Ref2VA node even when H0 uses no audio reference and no audio decode.

## Corrected H0 stack

- `minimax_h3_ref2va_pruned_int8_convrot.safetensors`
- `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- `minimax_h3_video_vae_fp16.safetensors`
- `minimax_h3_audio_vae_fp32.safetensors` — required schema dependency, 605,254,808 bytes, SHA256 `8e505d95dd1561d47abd43d4238fd40d9bb1ae9e147ed0a4cba778d76ae4db48`

No FL2VA checkpoint, Turbo LoRA, style embedding or alternate quantization.

## Tool files

### `prepare_h0_driver.py`

Outputs the same Wan comparison driver at24fps/124f with no crop/resize/tracking/recentering and no audio.

### `run_h0_ref2va.py`

Original H0 executor. Historical Runner47 used it directly and exposed the missing required audio-VAE input.

### `run_h0_ref2va_audio_vae_required.py`

Integration-fix wrapper used by Runner48. It adds the audio-VAE loader/input to the otherwise unchanged H0 graph, then delegates the actual run to the base H0 executor. On success it annotates the manifest with the integration incident/fix.

## H0 quality settings — unchanged

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

## Current operator sequence

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\48_run_minimax_h3_ref2va_h0_audio_vae_fix.ps1"
```

Runner48 downloads/verifies only the missing official audio VAE if needed, launches the pinned server and submits the repaired graph.

If the executor prints `H3-H0: prompt_id=...`, real H3 inference has started.

## Classification rule

API-schema/CUDA/DynamicVRAM/runtime failures are not model-quality failures. A completed video is also not automatically a production PASS; review full-resolution topology/identity/motion and then gameplay scale.

## Finite next branches

Only after completed H0 evidence:

- identity weak but motion/topology strong -> `ref_image_size=max`;
- anatomy under-resolved -> `480×864`, then `512×896`, then at most one768-short-edge control;
- good H0 -> game-relevant walking/secondary-motion driver;
- do not blindly grid-search or download FL2VA without an explicit hypothesis.

## Cleanup

Audio VAE is now part of the minimal Ref2VA dependency set. Do not accumulate alternate H3 quantizations. Once H3 is technically proven active and immediate Wan return is unnecessary, clean paused Wan large weights while preserving W1L proof/results/manifests.
