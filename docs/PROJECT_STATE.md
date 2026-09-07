# Roguelite — Current Project State

Status date: **2026-09-07**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`
4. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
5. `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`
6. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
7. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing project action updates thematic docs, this file and the active handoff before completion is reported.

## Game / presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- first canonical locomotion family is screen-left / mostly lateral-three-quarter;
- `72 deg` azimuth from travel heading is locked as the first locomotion-facing baseline (`90 deg` = pure side).

## Runtime animation architecture — LOCKED

The runtime plays **complete precomposed character frames**:

`complete frames -> complete-character spritesheet PNG(s) + metadata -> ordinary sprite playback`

Runtime construction of the visible character from body/hair/clothing/equipment layers is **ABOLISHED/CLOSED**.

Every exported frame must already contain the whole visible state and all baked motion, including where present:

- body locomotion;
- soft-tissue/jiggle motion;
- hair motion;
- base clothing/bindings motion;
- shackles/chains/restraints/accessories motion;
- final occlusion among those elements.

Offline authoring may still be modular. Runtime composition may not be silently reintroduced.

## Canonical Exilada initial-state master

`assets/source/characters/exilada/reference/exilada_master.png`

The master is the **complete initial-state appearance reference** for the current animation work: body, hair, base clothing/bindings, shackles/chains/restraints and other visible initial details.

## Motion state

C1A remains a mechanical gait/control proof using `G2_CANONICAL_RIG` + CMU `105_34 NormalWalk` and eight contact/down/passing/up states.

Runner 31 locked `72 deg` facing.

Runner 32 V1 failed as final locomotion art direction because it remained generic.

Runner 33 V2 improved the projected body treatment but still was not accepted as the final Exilada walk. It was deliberately retained as a **provisional motion driver** so the project could test the actual complete-character spritesheet instead of continuing skeleton-only micro-adjustments.

## SSD / visible-authoring state

Exact upstream SSD remains **BLOCKED** because the public release omits the custom multi-scale `pose_guider.pth`.

The Moore-compatible fallback remains technically runnable:

`Moore-AnimateAnyone graph + baseline Moore pose guider/motion module + released SSD denoising/reference UNets`

Runner 29: technical PASS / visual FAIL.

Runner 30: fixed the `1.7778×` pose-registration distortion and materially improved pose response/lower-limb reconstruction.

## RUNNER 34 — COMPLETE-CHARACTER PLAYABLE PROOF: TECHNICAL/PACKAGING PASS, TEMPORAL QUALITY FAIL

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Packer:

`tools/structured-2d-character-pipeline/g3s_pack_complete_character_spritesheet.py`

Runner 34 successfully produced the requested artifact class:

- eight generated frames from the **complete** `exilada_master.png` state;
- transparent RGBA complete-character frames;
- one `4×2` spritesheet (`2048×1024`, `512×512` cells);
- preview GIF and metadata;
- stable enough cell framing/pivot to demonstrate ordinary spritesheet playback.

Therefore the following question is now answered **YES**:

> Can the current toolchain generate and package a complete-character baked spritesheet instead of runtime-assembled layers?

Yes. The export/packing architecture works.

### Runner 34 visible result

The current Moore+SSD pose-only temporal authoring route does **not** satisfy the complete-motion requirement:

- Exilada identity is retained surprisingly well across the sequence;
- broad body pose response is visible;
- hair mass remains recognizable but is largely frozen/warped rather than showing convincing inertial secondary motion;
- base cloth changes shape but does not yet behave as believable cloth motion;
- intentional soft-tissue/jiggle motion is not reliably readable;
- wrist chain is comparatively persistent but mostly static;
- ankle restraint/chain becomes unstable, detaches/mutates into dark stepped artifacts and merges with cloth/leg regions in the middle frames;
- lower-limb/foot topology still degrades in the most displaced phases;
- later frames converge toward similar standing poses, and loop closure remains weak.

This is a **route-level temporal FAIL**, not a spritesheet-format failure.

## Primary diagnosis after runner 34

The current driver supplies **body OpenPose geometry only**. It does not explicitly describe the desired trajectories or inertial behavior of hair, cloth, soft tissue, chains or other secondary masses.

The Moore/AnimateAnyone temporal prior is not sufficient to infer those systems reliably from the single complete master plus body pose maps.

Therefore further pure skeleton tweaking or CFG/seed/resolution sweeps are not the next discriminant.

## NEXT GATE — COMPLETE-MOTION DRIVER

The next visible-authoring experiment must provide **richer whole-character motion control** offline while preserving the complete-frame runtime architecture.

The motion driver must explicitly contain or constrain, at minimum:

- body pose and weight transfer;
- hair mass motion/inertia;
- base-cloth motion;
- shackles/chains/restraint motion;
- soft-tissue/jiggle motion where visually required;
- full moving silhouette/occlusion information.

A hidden modular rig, proxy, simulation or driving video is allowed as an **offline motion-control source**. It is not the final art and does not imply runtime layer assembly.

Appearance reference remains `exilada_master.png`; the new control source supplies richer motion, not a replacement design.

## Immediate QA artifact

A native-gameplay-scale preview of the runner-34 sheet should be judged at approximately `128 px` character height before deciding how much of the visible artifact survives at final scale.

## Historical / closed assumptions

- runtime visible-character layer assembly — ABOLISHED/CLOSED;
- visible 3D -> final pixel art — CLOSED;
- nearest-segment rigid partition — CLOSED;
- whole-body chain/cage warp — CLOSED;
- MPFB body as mandatory guide — CLOSED;
- exact-upstream SSD runner 28 — BLOCKED/CLOSED by unreleased pose-guider checkpoint.

## No cleanup

Retain SSD environment/models, runner-34 output and motion work. They are evidence and inputs for the next complete-motion-driver test.
