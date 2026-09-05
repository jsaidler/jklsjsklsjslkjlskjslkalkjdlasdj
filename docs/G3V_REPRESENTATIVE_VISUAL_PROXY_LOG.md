# G3V Representative Visual Proxy — Execution Log

Status date: **2026-09-05**

Gate: **G3V — representative continuous human asset + deterministic pixel translation**

Current status: **PAUSED AT RETARGET SUB-GATE G3V-R. DO NOT RERUN BODY RENDER YET.**

## Purpose

G3V exists because G3/G3R proved that renderer tuning on a primitive mannequin cannot answer the production-art question. The gate asks whether a coherent continuous adult female human, with representative hair/cloth/restraints and driven by the approved real-motion backbone, can survive deterministic native-grid translation convincingly enough to justify Exilada identity work.

G4 remains blocked until G3V is technically valid and visually reviewed.

## Locked upstream baseline

- G0 headless automation: PASS;
- G1: `640×360`, orthographic pitch `26 deg`, protagonist reference height `128 px`;
- G2: CMU `105_34 NormalWalk`, deterministic persistent topology/motion PASS;
- G3: deterministic native-raster translation technical PASS, production look not approved;
- G3R: renderer-only mannequin refinement FAIL / CLOSED.

## Proven G3V infrastructure

The following parts are now established:

- pinned MPFB `2.0.17` loads directly in one Blender background process;
- MPFB `base.obj` imports headlessly;
- continuous female body and weighted `cmu_mb` rig are created;
- representative long hair, degraded cloth and wrist/ankle restraints render;
- accessory scale inheritance was removed using explicit rigid relative transforms and local-scale bake;
- binary semantic masks separate skin / hair / cloth / metal without color-classifier ambiguity;
- camera remains under the locked G1 presentation;
- gait phase selection derives from G2 foot-contact metadata rather than fixed sample indices;
- current measured gait period is `80` frames at 120 fps;
- current quarter-cycle phases are `1568,1588,1608,1628`.

## Runtime history — relevant conclusions

### Extension/bootstrap route

The original Blender-extension activation route was unreliable and caused multiple useless Blender launches. It was removed. MPFB is now loaded directly from the verified package inside a single background process.

### Blank and semantic-pass failures

Blank contact sheets and stale runtime patch binding were fixed. Binary masks later proved whether missing semantics were genuinely occluded or merely misclassified.

### Attachment inflation

A previous proxy build inflated cloth/accessory geometry enough to produce a 285 px bbox while the body itself was physically sane. This was traced to transform/scale handling. Proxy scale is now baked into mesh vertices and attachments follow bones through rigid matrices without inherited scale.

That correction produced the first coherent visible human proxy.

## First coherent contact sheet — technically invalid

The first coherent sheet showed the same character pose in all four columns even though frame numbers differed. This proved that copied Blender `Action` data was not animating the MPFB target rig correctly.

The next implementation explicitly copied source `matrix_basis` values per frame. That made the four poses visibly distinct, but the new sheet exposed a more serious retargeting error:

- frame phases now differ correctly;
- however pelvis/legs/trunk visibly collapse in later phases;
- the source G2 gait remains valid;
- therefore the failure is the mapping between source and target rest spaces, not motion source, camera, renderer, hair, cloth or pixel translation.

## Retargeting lesson — LOCKED

Matching bone names do **not** make two armatures interchangeable.

The failed shortcuts were:

1. copying the source `Action` onto the MPFB armature;
2. copying raw source `matrix_basis` transforms into the MPFB armature.

Neither operation compensates for differences in:

- rest pose;
- bone roll / local orientation;
- local coordinate bases;
- hierarchy details;
- target proportions.

Do not add more renderer or character-geometry patches until retargeting is independently proven.

## Active sub-gate: G3V-R — retarget preflight

Canonical log:

`docs/G3V_RETARGET_PREFLIGHT_LOG.md`

Tooling:

- `tools/deterministic-character-pipeline/03d_run_g3v_retarget_preflight.ps1`
- `tools/deterministic-character-pipeline/g3v_retarget_bootstrap.py`
- `tools/deterministic-character-pipeline/g3v_retarget_preflight.py`

The preflight is skeleton-only. It compares source and target rest rigs, evaluates MPFB's documented pose API and an explicit rest-compensated FK method, scores both numerically, chooses the better method and renders source-vs-target skeleton contact sheets.

This replaces iterative visual guessing with a bounded retarget benchmark.

## G3V PASS / FAIL criteria after G3V-R

G3V can PASS only if:

1. major topology is coherent: one head/torso, two arms/hands, two legs/feet;
2. four sampled poses are genuinely distinct and correspond to the real captured gait;
3. weighted body deformation remains coherent;
4. hair/cloth/restraints remain structurally stable across those poses;
5. all representative semantic layers remain visible somewhere in the sequence;
6. native-grid output shows credible headroom toward intentional modern pixel art rather than merely conventional 3D made blocky;
7. the complete flow remains headless/reproducible.

If a technically valid representative human still reads only as filtered/low-resolution 3D, hidden 3D is rejected as owner of final visible character art while remaining the motion/topology/socket/physics backbone.

## Exact next action

Run only:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\deterministic-character-pipeline\03d_run_g3v_retarget_preflight.ps1"
```

Then STOP. Share `Z:\AI\RogueliteCharacterPipeline\g3v_retarget\g3v_retarget_contact_sheet.png` if the runner reaches `REVIEW REQUIRED`; otherwise share the full console output.

Do **not** rerun `03c_run_g3v.ps1` and do not start G4 until G3V-R passes.
