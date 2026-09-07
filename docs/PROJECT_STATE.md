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
8. `docs/ANIMATION_PIPELINE.md`

## Living-document invariant — LOCKED

Every state-changing project action updates thematic docs, this file and the active handoff before completion is reported.

Do not reconstruct a candidate route from memory when a prior rejection/cleanup exists in Git history or canonical docs.

## Model-discard cleanup rule — LOCKED

Whenever a model or model route is declared **FAIL/CLOSED/REJECTED** and that model is no longer required as an active dependency, the same response must include an exact PowerShell command that removes its downloaded model-specific files.

- Preserve small result images, JSON markers and logs as evidence unless explicitly asked to remove them.
- If the model shares a runtime that is still used elsewhere, delete only that model's weights/model-specific dependency files.
- If the model has an isolated dependency workspace and nothing else depends on it, the workspace may be removed recursively.
- Do not later assume a rejected isolated workspace still exists unless the user explicitly rebuilt it.

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
- soft-tissue/jiggle;
- hair motion;
- base clothing/bindings motion;
- shackles/chains/restraints/accessories motion;
- final occlusion.

Offline authoring may still be modular; runtime composition may not be silently reintroduced.

## Canonical Exilada initial-state master

`assets/source/characters/exilada/reference/exilada_master.png`

The master is the **complete initial-state appearance reference** for current animation work: body, hair, base clothing/bindings, shackles/chains/restraints and other visible initial details.

## Motion state

C1A remains mechanical gait/control infrastructure using `G2_CANONICAL_RIG` + CMU `105_34 NormalWalk` and eight contact/down/passing/up states.

- runner 31 locked `72 deg` facing;
- runner 32 V1 remained too generic;
- runner 33 V2 was not approved as final locomotion but remains usable as a provisional body-motion driver when testing complete-character authoring routes.

Do not block all visible spritesheet experimentation behind further skeleton-only micro-polish.

## Runner 34 — complete-character playable proof

Runner:

`tools/structured-2d-character-pipeline/34_run_exilada_complete_character_walk8_playable_proof.ps1`

Result: **technical/export PASS; temporal-authoring FAIL.**

Runner 34 proved that the toolchain can generate/package the requested runtime artifact class:

- eight frames from the complete `exilada_master.png` state;
- RGBA complete-character frames;
- `4×2`, `2048×1024` spritesheet with `512×512` cells;
- preview GIF and metadata;
- ordinary complete-frame runtime playback.

Therefore complete-character baked spritesheets are a valid runtime/export architecture.

Visible failures of the Moore+SSD pose-only authoring route:

- hair mostly frozen/warped rather than showing convincing inertia;
- cloth morphing rather than controlled cloth motion;
- jiggle/soft-tissue motion not deliberately readable;
- wrist chain mostly static;
- ankle chain/restraint detaching/mutating into dark stepped artifacts;
- lower legs/feet degrading on displaced phases;
- weak later-phase differentiation / weak loop closure.

Do not rescue runner 34 through CFG/seed/resolution sweeps.

## Wan-Animate-2 — TESTED / REJECTED / CLEANED UP — CLOSED

Wan-Animate-2 is **not a current candidate**.

Historical validation on **2026-09-04** used the official Base INT8 ConvRot route on the local RTX 3060 12 GB machine and completed successfully enough for visual evaluation.

Observed positives:

- Exilada identity remained recognizable;
- coarse face/body proportions were relatively stable;
- long black hair, worn beige clothing and captivity chains remained substantially present;
- no catastrophic extra-limb failure dominated the clip.

Decisive failures:

1. **motion transfer was too weak** — the driver visibly walked while the generated Exilada remained largely planted with only modest weight/limb change;
2. **the project art language was not preserved** — output read as smooth painted/video-diffusion imagery rather than intentional modern pixel art.

Result: **Wan-Animate-2 Base INT8 rejected as production animation foundation.**

Do not revisit this exact Wan route through a different synthetic driver, seed, CFG, stronger reference strength, prompt cosmetics or post-generation pixel filters. A future revisit requires a **materially different model/checkpoint/integration** with evidence of both strong locomotor adherence and native/discrete game-art preservation.

The isolated Wan runtime/model workspace was subsequently deleted as part of rejected-model cleanup. **Do not assume `D:\AI\WanAnimate2` exists.**

Repository tooling under `tools/wan-animate2-spike/` is research history only and must not be treated as an active workspace or production path.

## Erroneous 2026-09-07 runner-35 proposal — WITHDRAWN

A proposed Wan complete-motion retry was created on 2026-09-07 without first checking the recorded Wan rejection and cleanup history. That proposal was invalid.

The following newly-created retry files were removed from `main`:

- `tools/structured-2d-character-pipeline/35_run_exilada_wan_animate2_complete_motion_proof.ps1`;
- `tools/structured-2d-character-pipeline/g3s_build_complete_motion_driver_v1.py`;
- `tools/structured-2d-character-pipeline/g3s_pack_wan_complete_character_spritesheet.py`;
- `tools/wan-animate2-spike/build_workflow_complete_motion.py`.

No runner 35 is active.

## Current next-gate constraint

The next complete-character authoring route remains **UNSELECTED** after runner 34, but it must obey all of the following:

- final runtime artifact is the complete character baked into each frame;
- `exilada_master.png` remains the complete initial-state appearance reference unless explicitly superseded;
- body, hair, cloth, jiggle and restraints/chains must all move coherently in the exported animation;
- explicit/inspectable motion control is strongly preferred;
- native/discrete pixel/game-art preservation is required;
- no generic video-diffusion retry is approved merely because it accepts a richer driver;
- previously rejected routes must be checked before any new installation/download;
- no large model/workspace is downloaded until the candidate has a discriminating reason to succeed where prior routes failed.

The 2026-09-04 post-Wan research identified pixel-native / explicit-control classes such as skeleton-driven pixel renderers and pixel-animation/keyframe systems as more relevant than another generic video-diffusion model. Those candidates were research leads, not production approvals.

## Historical / closed assumptions

- runtime visible-character layer assembly — ABOLISHED/CLOSED;
- Wan-Animate-2 Base INT8 — REJECTED/CLOSED; isolated workspace deleted;
- visible 3D -> final pixel art — CLOSED;
- nearest-segment rigid partition — CLOSED;
- whole-body chain/cage warp — CLOSED;
- MPFB body as mandatory guide — CLOSED;
- exact-upstream SSD runner 28 — BLOCKED/CLOSED by unreleased pose-guider checkpoint.

## Retention / cleanup

Retain runner-34 outputs and currently active structured-motion/SSD evidence until their route decisions are explicitly closed.

Do not recreate deleted rejected-model workspaces without an explicit new gate and justification.
