# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-07**

Gate status: **RUNNER 34 COMPLETE-CHARACTER EXPORT PASS / POSE-ONLY TEMPORAL QUALITY FAIL / EXACT UPSTREAM SSD BLOCKED / RICHER COMPLETE-MOTION CONTROL REQUIRED**

## Runtime target — LOCKED

The runtime target is conventional playback of **complete-character spritesheets**:

`complete authored frames -> complete-character spritesheet/atlas + metadata -> ordinary runtime playback`

Runtime construction of the visible character from body/hair/clothing/equipment layers is abolished. Offline authoring may internally use layers/rigs, but export is a fully composed character frame sequence.

## Initial Exilada reference

`assets/source/characters/exilada/reference/exilada_master.png`

For the current work this master defines the entire initial visible character state. Hair, base clothing/bindings, restraints/shackles/chains and visible accessories are part of the animation requirement.

## Local environment — PASS

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

Configuration retained:

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

- Exilada identity persists reasonably well through the sequence;
- torso/face/hair design remains recognizable;
- broad body pose changes respond to the driver;
- complete-frame packing/alignment is stable enough to demonstrate runtime playback.

Failures against the locked complete-motion requirement:

- hair mass is mostly frozen or locally warped; convincing lag/inertia is absent;
- base cloth changes shape but does not read as controlled physical cloth motion;
- intentional jiggle/soft-tissue motion is not reliably readable;
- wrist chain is comparatively persistent but mostly static;
- ankle restraint/chain becomes unstable, detaches/mutates into dark stepped shapes and merges with cloth/leg regions in middle frames;
- lower legs/feet still degrade under larger pose displacement;
- later phases become too similar and loop closure is weak.

This is a **temporal authoring failure**, not a failure of complete-character spritesheet architecture.

## Key diagnosis

The Moore-compatible route is being controlled by body OpenPose geometry. That signal does not specify desired trajectories for hair, cloth, chains, soft tissue or other secondary masses.

The temporal prior alone is not reliable enough to invent those systems while preserving attachment ownership and physical continuity.

Therefore the project should not spend the next iteration on broad CFG/seed/step/resolution tuning. The missing information class is **whole-character motion control**.

## Next experiment class — richer complete-motion driver

The next route must continue using `exilada_master.png` as the appearance reference but supply a driving/control representation that includes or constrains more than the body skeleton.

Required motion information includes:

- body locomotion/weight transfer;
- hair mass movement and lag;
- cloth movement and lag;
- chain/restraint trajectories;
- soft-tissue/jiggle where required;
- full moving silhouette and occlusion relationships.

Potential offline control sources may include a hidden rig/proxy with deterministic secondary systems, a simulated proxy video, or another full driving-video representation. These are authoring controls only; final runtime remains complete spritesheet playback.

## Role of Moore-compatible SSD after runner 34

Do not classify the route as useless: it preserves the master identity better than several earlier visible routes and follows body pose to some degree.

But classify it correctly:

> **useful appearance/pose transfer evidence; insufficient as the sole complete-motion author when driven only by OpenPose body maps.**

A later test may still reuse its identity-preservation value if richer control can be injected, but pure pose-only reruns are not the priority.

## Gameplay-scale review

Runner-34 output must also be viewed at the locked approximate `128 px` gameplay character height. Some 512px defects may disappear while others remain structurally visible. This review is a presentation check, not a substitute for fixing attachment/secondary-motion failures.

## Variation strategy — later

Armor, equipment, accessories, damage and exposure still need scalable offline variation. Final runtime frames remain complete/precomposed.

## Cleanup

No cleanup. Retain runner-34 outputs, SSD assets and environment as evidence for the next complete-motion-driver experiment.
