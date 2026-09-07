# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-07**

Gate status: **COMPLETE-CHARACTER PLAYABLE PROOF ACTIVE / EXACT UPSTREAM SSD BLOCKED / MOORE-COMPAT TECHNICALLY VIABLE**

## Runtime target — corrected/locked

The runtime target is conventional playback of **complete-character spritesheets**:

`complete authored frames -> complete-character spritesheet/atlas + metadata -> ordinary runtime playback`

Runtime construction of the visible character from body/hair/clothing/equipment layers is abolished. Offline authoring may internally use layers/rigs, but export is a fully composed character frame sequence.

## Initial Exilada reference

`assets/source/characters/exilada/reference/exilada_master.png`

For the current proof this master defines the entire initial visible character state. Hair, base clothing/bindings, restraints/shackles/chains and visible accessories are part of what must be animated, not stripped away for the production artifact.

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

Do not run the exact-upstream attempt again unless a trustworthy compatible custom pose-guider checkpoint becomes available or the project explicitly chooses to retrain it.

## Moore-compatible fallback

Working fallback:

`Moore-AnimateAnyone graph + baseline Moore pose guider/motion module + released SSD fine-tuned denoising/reference UNets`

Pinned Moore commit:

`a914ef38aae3733c2f02f29853dd0593372e0cc9`

This is explicitly not exact published SSD.

## Runner 29

Technical PASS / visual FAIL:

- weak phase differentiation;
- unstable lower legs/feet;
- detached accessory artifacts;
- insufficient locomotion.

## Runner 30

Runner 30 fixed a concrete pose-registration defect. Previous mapping from `640×360` to `512×512` stretched target geometry vertically by `1.7778×` relative to X. Uniform scaling + registration to the DWPose reference footprint materially improved pose response and lower-limb reconstruction.

The result still fell below production quality, but it proved two useful facts:

1. the Moore-compatible route can animate the complete master temporally;
2. corrected pose registration materially improves control.

Accessory/restraint instability remained visible, which is now treated correctly as a failure of complete-character temporal authoring rather than a future runtime-composition problem.

## Motion driver status

Runner 31 locked the gameplay facing at `72 deg`.

Runner 32 V1 remained generic.

Runner 33 V2 adds restrained feminine gameplay treatment but is not final locomotion approval. The user explicitly chose to generate the complete spritesheet now rather than keep micro-adjusting skeleton poses.

Therefore runner-33 V2 is the **provisional eight-frame motion driver** for the current full-master proof.

## CURRENT TEST — runner 34 complete-character spritesheet

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Packer:

`tools/structured-2d-character-pipeline/g3s_pack_complete_character_spritesheet.py`

Runner 34 intentionally tests the problem as a whole:

- appearance reference = full `exilada_master.png` initial state;
- target motion = 8-frame V2 guide at `72 deg`;
- inference = Moore-compatible SSD fallback;
- generation = `512×512`, 8 frames, 25 steps, CFG `3.5`, seed `42`, fp16;
- body movement and secondary motion are evaluated together;
- neutral connected background is removed after inference;
- output frames are stored as RGBA;
- eight full-character cells are packed 4×2 into a spritesheet;
- metadata records frame events, duration and stable pivot derived from reference-pose registration.

Expected output workspace:

`Z:\AI\SpriteSheetDiffusionSpike\exilada_initial_complete_walk8_playable_proof`

## What counts as secondary-motion success/failure

The temporal model is currently given one complete appearance reference plus body pose controls. It is therefore being asked to produce plausible temporal behavior for non-skeletal visible masses from its video prior.

That is deliberate. The proof asks whether this route can produce a coherent complete-character sequence in practice.

Judge:

- body locomotion;
- soft-tissue/jiggle response;
- hair inertia/shape continuity;
- base-cloth/binding response;
- shackles/chains/restraint attachment and motion;
- whole-character identity continuity.

If those secondary systems freeze, detach, change identity or migrate between anatomical sides, the complete-character route has failed that requirement. Do not excuse it as a missing runtime-layer system.

## Spritesheet artifact

The packer creates:

- eight transparent RGBA complete-character frames;
- `exilada_initial_walk8_complete_spritesheet.png`;
- playback GIF;
- metadata JSON;
- fixed cell geometry and pivot information.

This is a playable/visual proof artifact, not final pixel-art production approval.

## Variation strategy — later

Armor, equipment, accessories, damage and exposure still need scalable variation. The solution will be designed after the initial complete-character animation route is proven.

The only locked constraint is that final runtime character animation remains complete-frame playback; variation may use offline modular production or bounded precomposed state families, but not runtime construction of the character from interchangeable body/equipment layers.

## Cleanup

No cleanup. Existing SSD assets and environment are required for runner 34.
