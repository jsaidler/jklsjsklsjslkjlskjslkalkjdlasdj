# MiniMax H3 Base Ref2VA — local production screening spike

Status date: **2026-09-08**

Status: **CANONICAL / H3 ACTIVE / RUNNER46 BOOTSTRAP NEXT / H0 BASE REF2VA DEFINED**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

Determine whether **MiniMax H3 Base Ref2VA** can satisfy the Roguelite complete-character production contract on the local Windows 11 / RTX 3060 12 GB / 48 GB RAM machine:

`Exilada appearance reference + arbitrary real driving video -> complete coherent animated character -> automatic gameplay-scale conversion -> spritesheet`

The model must preserve more than skeleton motion. It must generate coherent body locomotion, weight, soft response, long-hair inertia, cloth/material response and restraint/accessory dynamics without routine manual rigging, keyframing, repair, masks, repainting or hand compositing.

## Transition from Wan

Wan-Animate-2 is **PAUSED AFTER W1L**, not `EXHAUSTED_FAIL`.

The operator reported W1L complete on 2026-09-08. Runner46 independently requires the completed local W1L video, prompt and manifest before H3 bootstrap proceeds. W1L's visual verdict is not invented here; its evidence remains in `Z:\AI\WanAnimate2` for comparison.

Do not launch another Wan inference while H3 is the active screening route.

## Why Ref2VA

The official ComfyUI H3 R2V workflow uses `MiniMaxH3ReferenceToVideo` and supports image/video/audio references addressed in the prompt as `<Picture i>`, `<Video i>` and `<Audio i>`. This maps directly to the project contract:

- `<Picture 1>` = Exilada appearance/identity/anatomy/clothing/hair/art language;
- `<Video 1>` = movement/performance/timing/weight transfer only;
- the prompt explicitly tells H3 to ignore the driver's identity, body, clothing, hair, environment and style.

No FL2VA model is required for this spike.

## Pinned local stack

### ComfyUI

Pinned stable portable:

- release: **ComfyUI v0.34.0**;
- archive: `ComfyUI_windows_portable_nvidia.7z`;
- source: `https://github.com/Comfy-Org/ComfyUI/releases/download/v0.34.0/ComfyUI_windows_portable_nvidia.7z`;
- compressed size: about **2.15 GB**;
- SHA256: `ed57cc6b19ae3d83add1ecebfdd56b25e04e0008cf0fe9af43a4ad8797e2a24c`;
- workspace root: `Z:\AI\MiniMaxH3\ComfyUI_windows_portable`;
- H3 port: **8190**.

Rationale: use a dedicated pinned H3 environment rather than mutate the proven Wan environment. H0 uses ComfyUI's normal DynamicVRAM behavior. Do **not** carry Wan's `--disable-pinned-memory` workaround into H3 unless H3 itself produces evidence that it is required.

### Required H0 model files

Only these three large H3 files are downloaded:

1. `models/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors`
   - approximately **21 GB**;
   - SHA256 `9255f52b6677845ad238f20dfaafa94727053694127ab7f255c048f0f9365779`.
2. `models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
   - approximately **15.7 GB**;
   - SHA256 `35a88d51044231fe332301d7a62aa81e3f2cba62febeb446e2c1e3e0ef76f2c6`.
3. `models/vae/minimax_h3_video_vae_fp16.safetensors`
   - `5,207,808,496` bytes, approximately **5.21 GB**;
   - SHA256 `7c1f131492e7eddacaac9069a61b81bdd39de5cc96561e677c5eab1cdce5e522`.

H0 model payload is therefore approximately **41.9 GB** before ComfyUI itself and generated evidence. A first clean bootstrap should have roughly **48 GB minimum free**; **55–60 GB free is preferred** so downloads, extraction, logs and output do not run against the filesystem limit.

### Explicitly excluded from H0

Do **not** download:

- any H3 FL2VA diffusion checkpoint;
- alternate BF16/FP8/INT8 Ref2VA checkpoints;
- `minimax_h3_ref2v_turbo_4step...` LoRA;
- style embeddings;
- audio VAE.

The H3 audio stream exists internally, but H0 decodes video only. Audio is irrelevant to the sprite-production decision, so `minimax_h3_audio_vae_fp32.safetensors` is deliberately omitted.

## Upstream workflow evidence

Runner46 stores a pinned copy of the official ComfyUI workflow:

`Z:\AI\MiniMaxH3\official_video_minimax_h3_r2v_pinned.json`

Pinned `Comfy-Org/workflow_templates` commit:

`7c25a3c586484601f94b7e8f8b14c23b2c95a096`

The upstream template specifies:

- `MiniMaxH3ReferenceToVideo`;
- Ref2VA-specific diffusion weights;
- `res_multistep` sampler;
- reference tags such as `<Picture 1>` and `<Video 1>`;
- `ref_image_size=match|max` semantics;
- `beta` or `normal` as preferable schedulers to `simple` for reference-heavy prompts.

H0 chooses **`beta`** and does not use Turbo.

## H0 input preparation

### Appearance

Source remains canonical:

`assets/source/characters/exilada/reference/exilada_master.png`

Runner46 copies it to:

`ComfyUI/input/roguelite_h3/exilada_master.png`

No redraw or appearance preprocessing is performed.

### Motion

For a direct family comparison, H0 starts with the **same raw source driver recorded by W1H**.

MiniMax H3 expects reference-video frames at 24 fps. Runner46 therefore calls:

`tools/minimax-h3-spike/prepare_h0_driver.py`

The normalizer:

- reads the exact W1H raw source driver;
- outputs exactly **124 frames at 24 fps**;
- performs **no crop**;
- performs **no resize**;
- does not stabilize/recenter/track the subject;
- removes audio because H0 is motion-only;
- uses timestamp resampling only.

Prepared driver:

`ComfyUI/input/roguelite_h3/h0_driver_24fps_124f.mp4`

Evidence:

`Z:\AI\MiniMaxH3\h0_driver_manifest.json`

## H0 exact inference baseline

H0 is a **Base Ref2VA accuracy baseline**, not a speed/Turbo test.

- task: `ref2va`;
- output geometry: **448×800**;
- frame count: **124**;
- FPS: **24**;
- duration: ~5.17 s;
- `ref_image_size`: **match**;
- inference steps: **50**;
- sampler: **res_multistep**;
- scheduler: **beta**;
- seed: **0**;
- video sigma shift: **12** from H3 model defaults;
- audio sigma shift: **3** from H3 model defaults;
- no Turbo LoRA;
- no negative-conditioning branch;
- fixed camera/full-body/topology stability requested in prompt.

The 50-step / video-shift12 / audio-shift3 choice matches the current reference-accuracy regime used for MiniMax H3 Base rather than a distilled/Turbo shortcut.

## Why 448×800 first

The runtime protagonist is roughly 128 px tall. A 768-short-edge source is not automatically justified if a smaller H3 canvas preserves the information needed by the final sprite.

`448×800`:

- is valid on the H3 32-pixel canvas grid;
- has aspect `0.56`, close to the current portrait driver;
- is 358,400 pixels;
- has a H3 visual latent grid of `28×50 = 1400` spatial cells;
- is about 34.7% of the spatial cell count of `1344×768` (`84×48 = 4032`).

This reduces spatial activation/token work but **does not shrink the model weights** and does not eliminate RAM/offload cost.

H0 is intentionally below the usual 768-short-edge regime. That is an experiment, not an assumption that lower is always better.

## Finite resolution ladder

Do not grid-search resolutions indefinitely.

If H0 fails specifically because anatomy/identity is under-resolved:

1. `448×800` — H0;
2. `480×864`;
3. `512×896`;
4. one 768-short-edge control only if needed to distinguish low-resolution failure from model/task failure.

If motion/topology is already excellent and **identity alone** is weak, test `ref_image_size=max` before increasing output resolution. `max` keeps substantially more reference-image information but is expected to be slower because reference tokens remain active through sampling.

## Dual-scale QA

H0 is reviewed twice.

### Full generated scale

Hard checks:

- one stable head/torso/two arms/two hands/two legs/two feet;
- no detached, duplicated, swapped, fused or disappearing limbs;
- stable torso/breast/hip anatomy;
- identity remains recognizably Exilada;
- motion timing/weight comes from the driver;
- long hair and cloth respond dynamically without becoming detached geometry;
- shackles/chain fragments remain accessories rather than morphing into flesh/limbs;
- no destructive whole-body smear/ghost double.

### Gameplay-scale proxy

The H0 executor automatically creates:

`Z:\AI\MiniMaxH3\h0_gameplay_scale_proxy_frame160.mp4`

This downsizes the whole portrait frame to about 160 px high. If the generated character occupies roughly 80% of the frame, the character appears near the game's ~128 px target. This is a **perceptual proxy**, not final segmentation/alpha extraction.

Downsampling may make tiny texture noise or restrained local motion blur irrelevant. It cannot excuse topology changes, missing body parts, broken silhouette or identity loss.

## Failure classification

A bad local run is not automatically a H3 model failure.

- download/hash/extract/version problems → `INFRASTRUCTURE FAIL`;
- missing/changed Comfy nodes or invalid API graph → `INTEGRATION FAIL`;
- DynamicVRAM/CUDA/host-buffer/OOM/runtime crash → `INFRASTRUCTURE FAIL` until diagnosed;
- successful inference with bad character behavior → `MODEL/TASK` or `CONFIGURATION` evidence depending on defect;
- low-resolution anatomy failure that disappears at the finite higher-resolution control → configuration/resolution failure, not family failure.

No manual repair can convert a failed production route into a production PASS.

## Operational sequence

### Gate 46 — prepare/bootstrap only

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\46_prepare_minimax_h3_ref2va.ps1"
```

Runner46:

1. verifies W1L completion evidence;
2. stops only the known managed Wan Comfy process to free RAM/VRAM;
3. verifies disk/pagefile context;
4. downloads/verifies/extracts pinned ComfyUI v0.34.0;
5. downloads/verifies only the three H0 model files;
6. stores the pinned official H3 R2V workflow;
7. prepares Exilada + 24fps/124f driver inputs;
8. starts ComfyUI only for node/schema/system preflight;
9. captures required `object_info` and system stats;
10. stops that preflight server;
11. writes `h3_bootstrap_manifest.json`.

**Runner46 performs no H3 inference.**

### Gate 47 — H0 inference

Only after Runner46 reports PASS:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\47_run_minimax_h3_ref2va_h0.ps1"
```

Expected proof files:

- `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- `Z:\AI\MiniMaxH3\h0_run_manifest.json`;
- `Z:\AI\MiniMaxH3\h0_api_prompt.json`;
- `Z:\AI\MiniMaxH3\h0_executor.log`;
- `Z:\AI\MiniMaxH3\h0_gameplay_scale_proxy_frame160.mp4` when the preview encoder succeeds.

Inference completion means only **technical execution PASS**. Production quality remains a human visual gate.

## Cleanup policy

- H3 H0 installs only one Ref2VA quantization and one encoder/VAE set.
- `.part` files are resumable during download; corrupt completed files are deleted rather than retained.
- no FL2VA/Turbo/style assets are accumulated.
- Wan W1L video/manifests remain evidence.
- once H3 is proven technically active and we decide not to return to Wan immediately, remove the paused Wan **large checkpoint set** while preserving small proof files/results; do not delete it prematurely during H3 bootstrap failure diagnosis.
- SSD/Moore comparison evidence remains until explicit abandonment/final model verdict.

## H3 H0 decision after output

Classify H0 using the smallest next action that tests the observed failure:

- **strong motion/topology + weak identity only** → `ref_image_size=max`;
- **under-resolved anatomy/detail** → next resolution rung;
- **good full-res but artifacts vanish at gameplay scale** → keep lower resolution and advance to a walking/secondary-motion driver;
- **major topology/motion failure despite successful integration** → diagnose prompt/reference semantics once, then determine whether H3 is unsuitable rather than endlessly tuning nearby values.
