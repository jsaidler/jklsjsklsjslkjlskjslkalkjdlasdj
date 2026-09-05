# G3V Representative Visual Proxy — Execution Log

Status date: **2026-09-05**

Gate: **G3V — representative continuous human asset + deterministic pixel translation**

Current status: **ACTIVE / MOTION-BINDING RERUN REQUIRED.**

## Purpose

G3V exists because G3/G3R proved that renderer tuning on a primitive mannequin cannot answer the production-art question. The gate asks whether a coherent continuous adult female human, with representative hair/cloth/restraints and driven by the approved real-motion backbone, can survive deterministic native-grid translation convincingly enough to justify Exilada identity work.

G4 remains blocked until G3V is both technically valid and visually reviewed.

## Locked upstream baseline

- G0 headless automation: PASS;
- G1: `640×360`, orthographic pitch `26 deg`, protagonist reference height `128 px`;
- G2: CMU `105_34 NormalWalk`, deterministic persistent topology/motion PASS;
- G3: deterministic native-raster translation technical PASS, production look not approved;
- G3R: renderer-only mannequin refinement FAIL / CLOSED.

## Current tooling

- `tools/deterministic-character-pipeline/03c_run_g3v.ps1`
- `tools/deterministic-character-pipeline/g3v_mpfb_bootstrap.py`
- `tools/deterministic-character-pipeline/g3v_bone_attachment_patch.py`
- `tools/deterministic-character-pipeline/g3v_geometry_phase_patch.py`
- `tools/deterministic-character-pipeline/g3v_semantic_masks.py`
- `tools/deterministic-character-pipeline/g3v_motion_binding_patch.py`
- `tools/deterministic-character-pipeline/g3v_representative_visual_proxy.py`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3v`

The user performs no Blender/MPFB GUI work.

## MPFB dependency

G3V pins MPFB `2.0.17`, validated archive SHA256:

`4f0a879d64a39bf646fbf5f53601ac678855da329d650617dca5737548239a87`

The runner loads the verified package directly inside one Blender background process rather than depending on Blender extension repository/preference state.

## Major runtime findings to date

### Extension/bootstrap failures — resolved

The first implementation incorrectly depended on extension activation surviving across Blender processes. That route was abandoned. Direct package bootstrap now works reliably and MPFB `base.obj` imports headlessly.

### Blank/semantic-pass failures — resolved

Early contact sheets could become review artifacts while visually blank. G3V now validates foreground and projected height before review. A stale `runpy`-namespace patch bug was also fixed by binding runtime replacements through `target_main.__globals__`.

### Binary semantic masks — resolved classifier ambiguity

Color classification was removed as the owner of semantic validation. G3V renders independent occlusion-aware masks for:

- skin;
- hair;
- cloth;
- metal.

When a semantic has zero visible pixels it is also rendered unoccluded. This distinguishes true occlusion from non-renderable/offscreen geometry.

### Old four-frame selection aliased the gait — resolved

The former fixed G2 sample subset `(0,3,6,9)` could land repeatedly on the same gait phase. G3V now derives the gait period from G2 foot-contact metadata.

Current measured period and phases:

- gait period: `80` frames at 120 fps;
- quarter-cycle frames: `1568,1588,1608,1628`.

G2's full 12-frame review remains the authoritative existing proof that the captured source motion itself is valid.

### Representative attachment inflation — resolved sufficiently to produce a visible human

A previous run reported sane body/skeleton physical heights but a 285 px semantic bbox and tens of thousands of cloth pixels. The fix now:

- bakes primitive local scale into mesh vertices;
- resets object scale to `(1,1,1)`;
- follows bones through explicit rigid relative matrices;
- disables inherited bone/parent scale;
- audits each attachment's world dimensions before rendering.

This correction produced the first non-blank coherent representative-human contact sheet.

## 2026-09-05 visual review of first coherent G3V contact sheet — TECHNICALLY INVALID

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3v\g3v_contact_sheet.png`

Frames shown:

`1568, 1588, 1608, 1628`

Positive findings:

- a coherent human silhouette is finally visible;
- skin, long dark hair, degraded cloth and metal restraints are all visually represented;
- the image no longer reads as a blank render or exploded accessory geometry;
- the representative source is materially richer than the primitive G3/G3R mannequin;
- the native pixel row is visually legible enough to make the final style kill switch meaningful once motion is valid.

Blocking finding:

**all four character images are byte-identical in the uploaded contact sheet.**

The distinct contact-derived frame numbers are real, but the MPFB character remains frozen in one pose. Therefore the sheet cannot validate deformation, gait, temporal continuity or attachment stability. G3V is not eligible for PASS and no aesthetic conclusion should be locked from this sheet yet.

Root cause boundary:

- G2 source motion is already validated across its full 12-frame sequence;
- contact-derived G3V frame selection is valid and distinct;
- the failure is between the animated `G2_CANONICAL_RIG` and `G3V_CMU_RIG`;
- assigning a copied Blender `Action` to the MPFB armature is not producing rendered pose changes reliably in this pipeline.

## Current motion-binding fix

`g3v_motion_binding_patch.py` removes the copied-Action path as the authority for G3V motion.

Before every final bbox/render evaluation it now:

1. locates `G2_CANONICAL_RIG` and `G3V_CMU_RIG`;
2. verifies the required CMU bone names on both;
3. verifies `G3V_BODY` has an Armature modifier bound to `G3V_CMU_RIG`;
4. disables the target rig Action;
5. explicitly copies each matching source pose bone `matrix_basis` into the MPFB target rig for the current frame;
6. updates the dependency graph;
7. records a pose signature from hands/knees/feet relative to hips.

The gate now refuses review unless:

- at least **3 distinct target-pose signatures** exist across the four sampled frames;
- target pose displacement is non-trivial;
- at least **3 distinct rendered skin-mask hashes** exist across the four sampled frames.

Expected markers:

- `G3V_MOTION_BINDING_MODE=EXPLICIT_PER_FRAME`
- `G3V_MOTION_BINDING=EXPLICIT_MATRIX_BASIS_FROM_G2`
- `G3V_TARGET_ACTION=DISABLED`
- `G3V_BODY_ARMATURE_MODIFIER=PASS`
- `G3V_MOTION_POSE_FRAME_1568=BOUND ...`
- `G3V_MOTION_UNIQUE_POSES=...`
- `G3V_MOTION_UNIQUE_SKIN_MASKS=...`
- `G3V_MOTION_DIVERSITY_AUDIT=PASS`

A contact sheet can no longer reach review while showing four identical poses.

## Representative asset scope

This is not finished Exilada geometry. The gate contains only enough visual structure to test architectural headroom:

- continuous female MPFB body;
- CMU-compatible weighted rig;
- long dark hair mass;
- asymmetric degraded cloth;
- wrist and ankle restraints;
- bare feet;
- semantic ownership for skin/hair/cloth/metal.

No detailed facial likeness, scars, gore, production garments, weapons or final secondary physics are required at G3V.

## PASS / FAIL criteria

G3V can PASS only if:

1. major topology is coherent: one head/torso, two arms/hands, two legs/feet;
2. the four sampled poses are genuinely distinct and correspond to the real captured gait;
3. weighted body deformation is visibly coherent;
4. hair/cloth/restraints remain structurally stable across those poses;
5. all representative semantic layers remain visible somewhere in the sequence;
6. the native-grid result shows credible headroom toward intentional modern pixel art rather than merely conventional 3D made blocky;
7. the complete flow remains headless/reproducible.

If a technically valid representative human still reads only as filtered/low-resolution 3D, hidden 3D is rejected as owner of the final visible character but remains the motion/topology/socket/physics backbone.

## Exact next action

Run only:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\deterministic-character-pipeline\03c_run_g3v.ps1"
```

Then STOP. If it reaches `G3V: REVIEW REQUIRED`, review the new `g3v_contact_sheet.png`. If it fails, use the console diagnostics; do not start G4.
