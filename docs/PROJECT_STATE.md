# Roguelite — Current Project State

Status date: **2026-09-06**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/GAME_VISION.md`
3. `docs/VISUAL_DIRECTION.md`
4. `docs/CHARACTERS.md`
5. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
6. `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`
7. `docs/PIXEL_ART_PRODUCTION.md`
8. `docs/ANIMATION_PIPELINE.md`
9. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
10. `docs/G3S_B3_NUDE_BODY_BASE_LOG.md`
11. `docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`
12. `docs/G3S_B4_HAIR_LOG.md`
13. `docs/G3S_C0_BODY_MOTION_PROOF.md`
14. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every project action that changes state updates the thematic docs, this file and the active handoff before completion is reported.

Normal operator loop once a runner is approved:

`git pull -> one documented PowerShell command -> inspect/share output`

## Game / presentation — LOCKED

Systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a causal living world.

Presentation baseline: **elevated 2D belt-scroller / false 3D**.

Final visible language: **true modern pixel art at native gameplay raster**.

Native gameplay baseline:

- `640×360`;
- orthographic camera;
- pitch `26°`;
- protagonist standing body height approximately `128 px`.

## Visible-ownership invariant — CRITICAL

Hidden 3D may own motion/topology/joints/sockets/depth/physics/guides but **not** final visible RGB/alpha/silhouette. Final visible art is owned by persistent native 2D pixel assets.

No recurring Blender/Aseprite/rigging/manual frame repainting burden is placed on the user.

## Canonical Exilada body — PASS/CLOSED / LOCKED

Production body:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`
- promotion commit `2deb765c3980d586ef9747340bb48852dedca452`;
- dimensions `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`.

The body remains byte/pixel unchanged as the source asset. Hair, clothes, restraints and accessories are separate future owners.

## Motion infrastructure already approved

- G2 real motion/topology — **PASS/CLOSED**;
- motion source: CMU `105_34 NormalWalk`;
- source rig: `G2_CANONICAL_RIG`;
- G3V-R retarget preflight — **PASS/CLOSED**;
- validated method: `DIRECTION_SPACE_FK`;
- validated gait phase frames: `1568, 1588, 1608, 1628`.

## Hair — DEFERRED BY USER

B4 is **not approved** and is no longer the current gate.

The structural rule remains locked for later:

`rear_hair -> body -> front_hair`

B4 history includes failed extraction/procedural routes and the B4C FLUX.2 visual-adaptation review. No B4C pixels were promoted. On 2026-09-06 the user explicitly instructed to forget hair for now and show the doll moving. Hair work is therefore paused, not approved or closed.

## Gate order — CURRENT

- G0 automation — PASS/CLOSED
- G1 camera/native scale — PASS/CLOSED
- G2 real motion/topology — PASS/CLOSED
- G3/G3R/G3V visible 3D translation routes — CLOSED/REJECTED as final visible ownership
- G3S-B3 production body — **PASS/CLOSED**
- G3S-B4 hair — **DEFERRED / OPEN**
- **G3S-C0 body-only motion proof** ← **CURRENT**
  - C0 V1 rigid cutout/part rotation — **FAIL/CLOSED VISUAL DEFORMATION METHOD**
  - **C0 V2 continuous chain warp** — **RUNNER READY / REVIEW NEXT**
- G3S-B5 clothing/restraints/accessories — DEFERRED
- full G3S-C layered motion proof — still requires B4/B5 later

## G3S-C0 V1 — FAIL/CLOSED

Reviewed contact sheet:

`Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk\g3s_c0_body_walk_contact_sheet.png`

Reviewed SHA256:

`730afda6a541db4524671931892685bee7317d8324efe6c9b3eb0c62fbdd5cc4`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c0_v1_visual_failure.json`

V1 proved that approved real motion reaches the persistent 2D body, but its visible deformation method failed. Hard partitions into upper/lower limb slabs rotate independently, causing joint detachment and loop/arc-like broken leg-foot silhouettes in later stride frames.

**Closed method:** `nearest-segment hard partition + independent rigid per-part rotation`.

Do not iterate it with more overlap or more hand-tuned rigid pivots.

## G3S-C0 V2 — CURRENT

V2 retains:

- the exact promoted B3B body;
- the same CMU/G2 projected real-motion samples;
- hidden 3D as joints/depth only;
- no diffusion/model/API;
- no hidden-3D RGB;
- no automatic promotion.

V2 changes only the visible 2D deformation:

`real G2 walk -> projected joints/depth -> direction-space target skeleton -> six continuous body regions -> chain warp across joints -> depth-aware integer-grid composition -> GIF/contact-sheet review`

Continuous regions:

- head;
- torso;
- left/right arm;
- left/right leg.

Each complete arm/leg bends along its shoulder-elbow-wrist or hip-knee-ankle-toe chain. Pixels near joints blend adjacent segment mappings instead of splitting into independently rotated pieces.

Spec:

`tools/structured-2d-character-pipeline/g3s_c0_body_motion_spec_v2.json`

Runner:

`tools/structured-2d-character-pipeline/20_run_g3s_c0_body_walk_v2.ps1`

Supporting tools:

- `tools/structured-2d-character-pipeline/g3s_c0_extract_g2_motion.py`
- `tools/structured-2d-character-pipeline/g3s_c0_continuous_warp_v2.py`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk_v2`

Expected review outputs:

- `g3s_c0_v2_body_walk_in_place.gif`
- `g3s_c0_v2_body_walk_travel.gif`
- `g3s_c0_v2_contact_sheet.png`
- `g3s_c0_v2_zoom_contact_sheet.png`
- `g3s_c0_v2_report.json`

If V2 still cannot keep the body visually continuous, the next deformation class is an actual weighted 2D mesh/cage, not a return to rigid cutout parts.

## Current exact action

Run exactly:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\20_run_g3s_c0_body_walk_v2.ps1"
```

Then share:

- `Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk_v2\g3s_c0_v2_body_walk_in_place.gif`
- `Z:\AI\RogueliteCharacterPipeline\g3s_c0_body_walk_v2\g3s_c0_v2_zoom_contact_sheet.png`

If it fails, share the complete console output.

Do not resume hair automatically.

## Actual local state relevant to C0

- deterministic workspace: `Z:\AI\RogueliteCharacterPipeline`;
- retained embedded Python: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe`;
- Blender was already used successfully by G0/G1/G2;
- C0 requires the existing `Z:\AI\RogueliteCharacterPipeline\g2\g2_motion_topology.blend`;
- no AI model is required by C0.
