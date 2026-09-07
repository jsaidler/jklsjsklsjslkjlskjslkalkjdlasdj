# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-07**

Gate status: **ACTIVE — EXACT UPSTREAM SSD BLOCKED / MOORE-COMPAT RUNNER 29 TECHNICAL PASS / VISUAL QA PENDING**

## Decision

The character-production target remains a conventional **2D spritesheet**: approved persistent frames arranged by action in rows/blocks or equivalent atlas regions, with metadata for timing, pivots, hitboxes and events as needed.

The active offline authoring investigation is based on Sprite Sheet Diffusion (SSD), using the complete Exilada master as appearance reference plus pose/motion guidance. Diffusion remains an authoring tool only; runtime remains ordinary spritesheet playback.

## Presentation/runtime lock retained

- elevated arcade beat'em-up / belt-scroller false 3D;
- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- first visible family screen-left/front-three-quarter;
- gameplay depth movement does not require north/south/isometric sprite families;
- runtime is ordinary spritesheet playback, not 3D, puppet assembly or diffusion.

## Local SSD environment / support — PASS

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

Validated:

- Miniconda PASS;
- env `ssd` PASS;
- Python `3.10.21`;
- pip `26.2.1`;
- RTX 3060 detected;
- Torch `2.0.1+cu118`;
- CUDA build `11.8`;
- upstream SSD inference import graph PASS;
- DWPose available and working in walk8 input preparation;
- FILM available, optional/not default;
- SD1.5 UNet, VAE and CLIP image encoder present;
- released SSD fine-tuned denoising/reference UNets present;
- AnimateAnyone baseline pose guider + motion module present.

## Canonical walk8 input — PREPARATION PASS

No manual pose folder is required.

The eight target states are the approved C1A walk cycle:

| Index | Source frame | Event | Support foot |
|---:|---:|---|---|
| 0 | 1588 | `left_contact` | left |
| 1 | 1598 | `left_down` | left |
| 2 | 1608 | `left_passing` | left |
| 3 | 1618 | `left_up` | left |
| 4 | 1628 | `right_contact` | right |
| 5 | 1638 | `right_down` | right |
| 6 | 1648 | `right_passing` | right |
| 7 | 1658 | `right_up` | right |

Canonical guide:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_guide.json`

Runner 28 V3 successfully reached real inference, which confirms the JSON path-control plane, DWPose reference-pose extraction and deterministic eight-target pose-map preparation work.

Correct input split:

`Exilada master --DWPose--> reference pose`

`approved C1A guide --deterministic OpenPose-style conversion--> 8 target pose maps`

## Runner 28 real inference result — BLOCKED / CLOSED

Runner:

`tools/structured-2d-character-pipeline/28_run_ssd_exilada_walk8.ps1`

The latest run reached:

`[INFER] Running SSD: 512x512, 8 target frames, 25 steps, CFG 3.5, fp16...`

Model initialization then failed at:

`pose_guider.load_state_dict(..., strict=True)`

The installed `pose_guider.pth` contains the original Moore/AnimateAnyone architecture keys:

- `conv_in.*`;
- `blocks.*`;
- `conv_out.*`.

Current SSD `models/pose_guider.py` instead defines a custom multi-scale architecture with keys including:

- `scale`;
- `conv_layers.*`;
- `conv_layers_1.*` through `conv_layers_4.*`;
- `final_proj.*`;
- `cross_attn1.*` through `cross_attn4.*`.

The state-dict mismatch is therefore structural, not a damaged file, CUDA problem, DWPose problem or path-transport issue.

The preceding warning that several SD1.5 UNet output-layer weights were unused was **not** the fatal error; execution continued until the pose-guider strict load.

### Public-release blocker — CONFIRMED

The SSD repository's current `inference.py` instantiates the custom multi-scale `PoseGuider(noise_latent_channels=320)` and loads `config.pose_guider_path` with `strict=True`.

SSD's modified `unet_3d.py` consumes a list of multi-scale pose features (`pose_cond_fea[0]` plus additional indexed features through down blocks). This is incompatible with the original Moore/AnimateAnyone PoseGuider, which returns a single pose feature tensor and whose UNet adds it only at the input stage.

The official SSD README links a pretrained-weight Drive, but the public release does not contain the required custom `pose_guider.pth`. Upstream GitHub issue **#3 — “Missing pose_guider.pth in released weights — inference cannot run as-is”** independently records exactly this blocker.

Therefore:

**Exact current-upstream SSD inference is not reproducible from the publicly released model set.**

The earlier project assumption that the baseline `patrolli/AnimateAnyone/pose_guider.pth` was a drop-in companion for the released SSD UNets was wrong and is now corrected in `ssd_model_manifest.json`.

Do not rename, reshape loosely, or load the baseline checkpoint with `strict=False` into SSD's custom PoseGuider. That would leave the custom pose network substantially random and would not constitute a valid SSD test.

## Released-model manifest — CORRECTED

Manifest:

`tools/structured-2d-character-pipeline/ssd_model_manifest.json`

Current revision:

`SSD_RELEASED_MODEL_SET_V2`

Status:

`EXACT_UPSTREAM_INFERENCE_BLOCKED_POSE_GUIDER_UNRELEASED`

The baseline AnimateAnyone pose guider is retained only as a **fallback-compatible Moore asset**, not as an exact SSD pose-guider checkpoint.

## Moore-compatible empirical salvage route — TECHNICAL PASS

Because the missing checkpoint prevents exact SSD inference, the bounded validation uses a technically coherent graph whose pose guider actually matches the available checkpoint:

`Moore-AnimateAnyone graph + baseline Moore PoseGuider/motion module + released SSD fine-tuned denoising/reference UNets`

This is **not** claimed to be the exact published SSD graph. It answers a narrower practical question: do the released SSD fine-tuned UNets still provide useful sprite-character generation when run in the compatible original AnimateAnyone graph they evolved from?

Pinned Moore source commit:

`a914ef38aae3733c2f02f29853dd0593372e0cc9`

Helper:

`tools/structured-2d-character-pipeline/g3s_ssd_moore_compat_walk8.py`

Runner:

`tools/structured-2d-character-pipeline/29_run_ssd_moore_compat_exilada_walk8.ps1`

### Runner 29 result — 2026-09-07

Execution reached the intended terminal marker:

`SSD-MOORE-COMPAT: OUTPUT READY FOR VISUAL QA`

Confirmed from the operator log:

- canonical Exilada master + C1A walk8 input package rebuilt successfully;
- pinned Moore source fetched/reset successfully;
- model loading completed;
- released SSD reference UNet loaded strictly;
- released SSD denoising UNet produced **0 unexpected keys** under the Moore graph;
- denoising load reported `588` missing keys under Moore's intended `strict=False` convention;
- those missing keys do not imply random weights: Moore `UNet3DConditionModel.from_pretrained_2d()` first loads the SD1.5 spatial weights and separately merges the motion-module checkpoint before the fine-tuned denoising checkpoint is overlaid;
- upstream SSD inference itself also loads `denoising_unet.pth` with `strict=False`, so partial overlay is part of the source model-loading design;
- pose guider loaded strictly using the matching baseline Moore architecture;
- generation completed: 8 frames, `512×512`, 25 steps, CFG `3.5`, seed `42`, fp16;
- diffusion completed `25/25` in approximately `42 s` on the RTX 3060;
- PNG frames, contact sheet, GIF and result marker were written.

Non-fatal warnings observed:

- unused SD1.5 `conv_norm_out` / `conv_out` weights during model initialization;
- Torch `TypedStorage` deprecation warning;
- future deprecation warning for direct `denoising_unet.in_channels` access.

None prevented inference or output generation.

Artifacts:

- `Z:\AI\SpriteSheetDiffusionSpike\exilada_walk8_moore_compat\frames`;
- `Z:\AI\SpriteSheetDiffusionSpike\exilada_walk8_moore_compat\exilada_walk8_moore_compat_contact_sheet.png`;
- `Z:\AI\SpriteSheetDiffusionSpike\exilada_walk8_moore_compat\exilada_walk8_moore_compat.gif`;
- `Z:\AI\SpriteSheetDiffusionSpike\ssd_exilada_walk8_moore_compat.json`.

Runner 29 is therefore **TECHNICAL PASS / OUTPUT READY**, not visual PASS.

## Current exact operator action — VISUAL QA

Share the existing contact sheet and GIF for review. Do not rerun or retune before examining them:

1. `Z:\AI\SpriteSheetDiffusionSpike\exilada_walk8_moore_compat\exilada_walk8_moore_compat_contact_sheet.png`
2. `Z:\AI\SpriteSheetDiffusionSpike\exilada_walk8_moore_compat\exilada_walk8_moore_compat.gif`

Visual QA must judge:

- Exilada identity persistence;
- anatomy/proportions;
- long hair consistency;
- cloth/shackles/chains consistency;
- pose obedience to C1A;
- temporal coherence;
- whether the output is useful enough to justify further spritesheet production.

No additional action family, resolution sweep, parameter tuning, FILM interpolation or spritesheet packing is authorized until this visual gate is closed.

## PASS semantics

A technical runner PASS is only output-ready status. Visual QA must judge:

- Exilada identity persistence;
- anatomy/proportions;
- long hair consistency;
- cloth/shackles/chains consistency;
- pose obedience;
- temporal coherence;
- whether output is useful enough to justify further spritesheet production.

If the visual result fails, diagnose the failure category first. Do not paper over architecture/state-dict mismatches with `strict=False` unless the source architecture itself explicitly requires it and the compatibility probe supports it.

## Exact SSD route status

Keep exact SSD marked **BLOCKED** unless one of the following happens:

- the authors release the custom multi-scale `pose_guider.pth`;
- a trustworthy mirror of that exact compatible checkpoint is found and hash/provenance are verified;
- the project deliberately chooses to retrain the missing custom pose guider/stage-1 stack, which would be a new project decision rather than a smoke test.

## Cleanup

SSD remains ACTIVE as an investigation and the released fine-tuned UNets are retained. No cleanup applies now.
