# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-07**

Gate status: **PAUSED AFTER RUNNER 30 — EXACT UPSTREAM SSD BLOCKED / MOORE-COMPAT TECHNICALLY VIABLE / VISIBLE OUTPUT STILL BELOW PRODUCTION / GAMEPLAY LOCOMOTION ART-DIRECTION GATE ACTIVE**

## Decision

The final character-production target remains conventional persistent 2D animation assets:

`approved frames -> spritesheet/atlas + metadata -> ordinary runtime playback`

Diffusion remains an offline authoring candidate only. Runtime does not depend on it.

The current SSD/Moore-visible route is **paused**, not approved for production expansion. Do not continue parameter sweeps while the hidden gameplay locomotion itself is still undefined.

## Presentation/runtime lock retained

- elevated arcade beat'em-up / belt-scroller false 3D;
- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- mostly lateral / three-quarter visible family;
- exact horizontal locomotion-facing angle currently reopened under C1C review;
- runtime root/world translation remains separate from sprite-frame playback.

## Local SSD environment / support — PASS

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

Validated:

- env `ssd`, Python `3.10.21`;
- RTX 3060;
- Torch `2.0.1+cu118` / CUDA 11.8;
- DWPose available;
- FILM available but not default;
- SD1.5 UNet, VAE and CLIP image encoder present;
- released SSD denoising/reference UNets present;
- baseline AnimateAnyone pose guider + motion module present.

## Exact upstream SSD — BLOCKED

Runner 28 reached real model initialization but failed because the public model release does not include the custom trained multi-scale `pose_guider.pth` required by current SSD code.

Available baseline checkpoint architecture:

`Moore/AnimateAnyone conv_in / blocks / conv_out`

Current SSD PoseGuider architecture:

`conv_layers* / final_proj / cross_attn* / scale`

The graphs are structurally different. Exact current-upstream SSD inference is not reproducible from the public checkpoint set.

Do not run runner 28 again and do not fake compatibility by loading the baseline checkpoint loosely into SSD's custom PoseGuider.

Manifest status:

`EXACT_UPSTREAM_INFERENCE_BLOCKED_POSE_GUIDER_UNRELEASED`

## Moore-compatible salvage graph

Fallback:

`Moore-AnimateAnyone graph + baseline Moore pose guider/motion module + released SSD fine-tuned denoising/reference UNets`

Pinned Moore commit:

`a914ef38aae3733c2f02f29853dd0593372e0cc9`

This is explicitly **not** exact published SSD.

## Runner 29 — TECHNICAL PASS / VISUAL FAIL

Runner:

`tools/structured-2d-character-pipeline/29_run_ssd_moore_compat_exilada_walk8.ps1`

Technical result:

- 8 frames at `512×512`;
- 25 steps;
- CFG `3.5`;
- seed `42`;
- fp16;
- 0 unexpected Moore keys from SSD denoising checkpoint;
- 588 missing keys accepted under the intended SD1.5 + motion-module initialization followed by partial checkpoint overlay;
- reference UNet and baseline Moore pose guider loaded successfully.

Visual result failed production use:

- poor C1A phase differentiation;
- weak pose obedience;
- unstable lower legs/ankles/feet;
- detached dark accessory/ground artifacts;
- insufficient locomotion despite moderate identity persistence.

## Runner 30 — pose-registration discriminant

Runner:

`tools/structured-2d-character-pipeline/30_run_ssd_moore_compat_exilada_walk8_pose_aligned.ps1`

Runner 30 isolated and corrected a concrete runner-29 input defect. The earlier target-pose conversion mapped the locked `640×360` C1A coordinates to `512×512` with independent axis scales:

- X `0.8`;
- Y `1.4222...`;
- relative vertical stretch `1.7778×`.

Runner 30 instead:

- rebuilt target poses from the original C1A joints using one uniform geometry scale;
- registered target skeleton body scale/position to the DWPose reference-body footprint;
- removed baked root travel for in-place authoring;
- kept master/model/weights/resolution/steps/CFG/seed/fp16 unchanged.

## Runner 30 visual QA — DIAGNOSTIC IMPROVEMENT / PRODUCTION FAIL

The user-supplied runner-30 contact sheet/GIF showed a clear improvement over runner 29:

- pose articulation became much more visible;
- left/right progression improved;
- leg/foot reconstruction was materially better;
- therefore pose-scale registration was a real failure source.

However the result remains **far below the intended game quality**:

- walking lacks convincing naturality;
- pose/body presentation is not yet tuned to the elevated belt-scroller's locomotion language;
- several gait phases remain awkward rather than polished;
- the complete master still produces unstable dangling restraints/accessory fragments;
- the sequence is not suitable to freeze as production sprites.

Runner 30 is therefore **not a production PASS**. It is retained as a useful diagnostic proof that corrected pose geometry materially improves control.

## New diagnosis

After runner 30, the remaining problem cannot be treated as an image-model parameter problem alone.

C1A was approved as a **mechanical gait sanity proof** using generic CMU `105_34 NormalWalk` and a `45 deg` camera azimuth from travel heading. That does not mean it is the correct art-directed locomotion for the final game.

The project was asking the visible authoring model to solve two things simultaneously:

1. follow a pose sequence;
2. invent the missing gameplay animation style.

Runner 30 improved #1 enough to expose #2.

Do not use CFG/seed/resolution/FILM sweeps to compensate for an unapproved locomotion master.

## Current gate outside SSD — G3S-C1C gameplay locomotion master

Canonical document:

`docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`

Current runner:

`tools/structured-2d-character-pipeline/31_run_g3s_c1c_gameplay_facing_audit.ps1`

Runner 31 executes no diffusion. It compares the same validated human gait at `60`, `72` and `84 deg` azimuth from travel heading to find an appropriate mostly-lateral belt-scroller presentation before any gait styling is added.

No SSD rerun is authorized until C1C approves the base gameplay locomotion pose family.

## Layering implication

Runner 30's detached/restraint artifacts reinforce the broader body-first production rule. The gait should be defined and validated on the body first; hair, clothing, bindings, shackles/chains and secondary masses remain downstream layer/authoring problems.

This does not yet prove which visible body-authoring model will win. It does prove that a monolithic complete-master walk is not an acceptable substitute for motion design and layer stability.

## Future SSD condition

The Moore-compatible route may be revisited **only after** C1C provides an approved gameplay locomotion guide. At that point the next fair visible test should prioritize body motion rather than asking the complete accessory-heavy master to solve every layer at once.

Exact upstream SSD remains blocked unless a trustworthy compatible custom pose-guider checkpoint becomes available or the project deliberately chooses to retrain the missing custom pose stack.

## Cleanup

No cleanup yet. Existing SSD downloads remain useful evidence/assets, but no new SSD computation is current work.
