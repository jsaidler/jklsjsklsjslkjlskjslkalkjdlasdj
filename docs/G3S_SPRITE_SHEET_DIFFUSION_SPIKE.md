# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-07**

Gate status: **RUNNER 34 COMPLETE-CHARACTER EXPORT PASS / POSE-ONLY TEMPORAL QUALITY FAIL / WAN-ANIMATE-2 ALREADY REJECTED / NEXT ROUTE UNSELECTED**

## Runtime target — LOCKED

The runtime target is conventional playback of **complete-character spritesheets**:

`complete authored frames -> complete-character spritesheet/atlas + metadata -> ordinary runtime playback`

Runtime construction of the visible character from body/hair/clothing/equipment layers is abolished. Offline authoring may internally use layers/rigs, but export is a fully composed character frame sequence.

## Initial Exilada reference

`assets/source/characters/exilada/reference/exilada_master.png`

For current work this master defines the entire initial visible character state. Hair, base clothing/bindings, restraints/shackles/chains and visible accessories are part of the animation requirement.

## Local SSD environment — PASS

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

Validated:

- env `ssd`, Python `3.10.21`;
- RTX 3060;
- Torch `2.0.1+cu118` / CUDA 11.8;
- DWPose;
- SD1.5 UNet/VAE/CLIP image encoder;
- released SSD denoising/reference UNets;
- baseline AnimateAnyone pose guider + motion module.

## Exact upstream SSD — BLOCKED

The current upstream SSD graph requires a custom multi-scale `pose_guider.pth` that was not publicly released. The available baseline Moore/AnimateAnyone pose-guider checkpoint has a different architecture.

Do not rerun exact-upstream SSD unless a trustworthy compatible custom checkpoint becomes available or the project deliberately chooses to retrain it.

## Moore-compatible fallback

Working fallback:

`Moore-AnimateAnyone graph + baseline Moore pose guider/motion module + released SSD fine-tuned denoising/reference UNets`

Pinned Moore commit:

`a914ef38aae3733c2f02f29853dd0593372e0cc9`

This is explicitly not exact published SSD.

## Runner history

### Runner 29

Technical PASS / visual FAIL:

- weak phase differentiation;
- unstable lower legs/feet;
- detached accessory artifacts;
- insufficient locomotion.

### Runner 30

Fixed a concrete target-pose registration defect: the prior `640×360 -> 512×512` mapping introduced `1.7778×` relative vertical stretch. Uniform scaling and registration to the reference footprint materially improved body pose response and lower-limb reconstruction.

### Runner 31–33

- runner 31 locked gameplay facing at `72 deg`;
- runner 32 V1 remained too generic;
- runner 33 V2 added restrained feminine projected body treatment but was still not final locomotion approval;
- V2 was retained as a provisional driver so a real full-character spritesheet could be produced immediately.

## Runner 34 complete-character playable proof — RESULT

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Packer:

`tools/structured-2d-character-pipeline/g3s_pack_complete_character_spritesheet.py`

Configuration:

- full `exilada_master.png` appearance reference;
- eight V2 poses at `72 deg`;
- Moore-compatible SSD fallback;
- `512×512`;
- 8 frames;
- 25 steps;
- CFG `3.5`;
- seed `42`;
- fp16.

### Technical/export result — PASS

Runner 34 successfully generated and packaged:

- eight complete-character frames;
- connected neutral-background removal;
- transparent RGBA outputs;
- a `4×2`, `2048×1024` spritesheet with `512×512` cells;
- playback GIF;
- metadata for ordinary complete-frame playback.

The spritesheet format itself is therefore no longer an unknown. The toolchain can generate a baked complete-character animation artifact.

### Visual/temporal result — FAIL for production motion

Useful positives:

- Exilada identity persists reasonably well;
- torso/face/hair design remains recognizable;
- broad body pose changes respond to the driver;
- complete-frame packing/alignment is stable enough to demonstrate runtime playback.

Failures:

- hair mass mostly frozen or locally warped; convincing lag/inertia absent;
- base cloth changes shape but does not read as controlled physical cloth motion;
- intentional jiggle/soft-tissue motion not reliably readable;
- wrist chain comparatively persistent but mostly static;
- ankle restraint/chain unstable, detaching/mutating into dark stepped shapes;
- lower legs/feet degrade under larger pose displacement;
- later phases become too similar and loop closure is weak.

This is a **temporal authoring failure**, not a failure of complete-character spritesheet architecture.

## Key diagnosis

The Moore-compatible route is controlled by body OpenPose geometry. That signal does not specify desired trajectories for hair, cloth, chains, soft tissue or other secondary masses.

The temporal prior alone is not reliable enough to invent those systems while preserving attachment ownership and physical continuity.

Do not spend the next iteration on broad CFG/seed/step/resolution tuning.

## Wan-Animate-2 — TESTED BEFORE THIS GATE / REJECTED / CLOSED

Wan-Animate-2 was already tested locally on 2026-09-04 with the official Base INT8 ConvRot checkpoint.

The run completed and was visually rejectable on its merits. It preserved Exilada identity and coarse anatomy better than some earlier direct-diffusion experiments, but failed the production gate because:

1. raw driving-video locomotion adherence was too weak;
2. output lost the required modern-pixel-art language and read as smooth painted/video diffusion.

Therefore direct raw-video conditioning is **not an untested solution** to runner 34's missing secondary-motion signal. The exact Wan route is already closed.

Do not revive it with a synthetic richer driver, seed/CFG tuning, reference-strength changes, prompt cosmetics or post-generation pixel filtering.

The isolated Wan model/runtime workspace was deleted after rejection. `tools/wan-animate2-spike/` remains source-level research history only.

## Erroneous runner-35 retry — WITHDRAWN

A 2026-09-07 proposed Wan retry ignored the prior rejection/cleanup record. The newly-created runner/helper files were deleted from `main`. There is no active runner 35.

## Next experiment class — OPEN, constrained

The next route must preserve the complete-character runtime architecture but be materially different from both:

- body-pose-only Moore+SSD;
- generic/raw-video Wan-Animate-2.

Required properties:

- explicit or inspectable motion control;
- coherent body/hair/cloth/jiggle/restraint motion;
- stable attachment ownership/topology;
- complete-frame output;
- native/discrete pixel/game-art preservation;
- scalability without routine manual frame-by-frame repair.

Historical post-Wan research found pixel-native skeleton/keyframe animation services and other explicit-control pixel-domain approaches more relevant than another generic video model, but no candidate is currently production-approved.

## Role of Moore-compatible SSD after runner 34

Do not classify the route as useless: it preserves the master identity better than several earlier visible routes and follows body pose to some degree.

Classify it correctly:

> **useful appearance/pose transfer evidence; insufficient as the sole complete-motion author when driven only by OpenPose body maps.**

## Variation strategy — later

Armor, equipment, accessories, damage and exposure still need scalable offline variation. Final runtime frames remain complete/precomposed.

## Cleanup

Retain runner-34 outputs and current SSD evidence while this branch is still diagnostically useful. Do not recreate deleted Wan assets/workspace without an explicit new model-level gate and materially different justification.
