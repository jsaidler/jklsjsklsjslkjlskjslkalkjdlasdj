# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-07**

Gate status: **RUNNER 34 EXPORT PASS / MOORE+SSD RETAINED RESEARCH ONLY / EXACT SSD BLOCKED / WAN-ANIMATE-2 BASE BF16 IS THE ACTIVE PRODUCTION-CLASS GATE**

## Runtime target — LOCKED

The runtime target remains conventional playback of **complete-character spritesheets**:

`complete authored frames -> complete-character spritesheet/atlas + metadata -> ordinary runtime playback`

Runtime visible-character layer assembly is abolished.

## Initial Exilada reference

`assets/source/characters/exilada/reference/exilada_master.png`

This defines the complete initial visible state.

## SSD/Moore environment — RETAINED RESEARCH

Workspace:

`Z:\AI\SpriteSheetDiffusionSpike`

Validated historical environment includes Moore/AnimateAnyone components, released SSD reference/denoising UNets and pose/motion tooling.

Do **not** treat this workspace as the current production gate.

## Exact upstream SSD — BLOCKED

The released public SSD weights available to the project do not include the custom SSD pose-guider checkpoint required by the exact published graph.

Therefore exact published SSD has not been reproduced locally.

Correct classification: `BLOCKED`, not model-family visual rejection.

## Moore-compatible fallback

Historical runnable reconstruction:

`Moore AnimateAnyone graph + Moore baseline pose guider/motion module + released SSD reference/denoising UNets`

This is not exact published SSD.

## Critical integration lesson — runner 30

An earlier pose preprocessing path introduced a `1.7778×` relative vertical distortion when mapping 640×360 control geometry into 512×512.

Fixing that materially improved pose response and lower-limb reconstruction. This remains important evidence that local preprocessing/integration can masquerade as model limitation.

## Runner 34 — retained result

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Runner 34 proved:

- complete-character generation/packing architecture works;
- RGBA complete frames can be exported;
- complete-character spritesheet/runtime playback works;
- identity can persist reasonably under the tested Moore+SSD hybrid.

Visible quality remained inadequate in hair, cloth, jiggle, chains, feet and loop coherence.

## Why this branch is no longer the active production gate

The production contract changed materially on 2026-09-07.

The final model must receive:

1. complete Exilada appearance reference;
2. **raw real driving video** carrying richer motion information than a skeleton.

It must automatically infer non-rigid dynamics including hair, cloth, jiggle, wind/material and restraints/accessories without manual animation/cleanup.

The current Moore/AnimateAnyone path is body-pose-conditioned, so even if further tuning improved locomotion, it does not satisfy the final information contract as the primary production author.

Therefore the previously planned Moore-baseline-vs-SSD exhaustion audit is **paused/superseded as the immediate production gate**. It may be revisited only as research or if the production contract changes.

## Active production-class route

Wan-Animate-2 is now active because it directly consumes the reference image and raw driving video.

Current preparation runner:

`tools/structured-2d-character-pipeline/35_prepare_wan_animate2_bf16_w0.ps1`

Canonical W0 model set is Base BF16 + UMT5 FP16 + CLIP Vision H + Wan VAE BF16, about 45.7 GB total.

## Cleanup decision

Do not delete `Z:\AI\SpriteSheetDiffusionSpike` **yet**.

Reason:

- it contains comparison/evidence material that may still be useful while Wan W0 has not been established;
- the project previously deleted a workspace too early and later needed to revisit the model question.

Once Wan W0 is established and the project explicitly decides SSD research will not be revisited, delete the large SSD model/runtime material while retaining only small manifests/logs/result evidence.

Do not download any additional SSD/Moore weights while Wan is the active gate.
