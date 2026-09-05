# G3V Representative Visual Proxy — Execution Log

Status date: **2026-09-05**

Gate: **G3V — representative continuous human asset + deterministic pixel translation**

Current status: **ACTIVE / BODY RERUN READY WITH VALIDATED RETARGET.**

## Locked upstream baseline

- G0 automation: PASS;
- G1: `640×360`, orthographic `26 deg`, hero `128 px`;
- G2: CMU `105_34 NormalWalk`, topology/motion PASS;
- G3: native translation technical PASS, production look not approved;
- G3R: renderer-only mannequin refinement FAIL / CLOSED;
- G3V-R retarget preflight: **PASS / CLOSED**.

## Proven G3V infrastructure

- MPFB `2.0.17` loads headlessly from pinned verified archive;
- continuous female body + weighted `cmu_mb` rig are created;
- long hair, degraded cloth, restraints and bare feet render;
- accessory scale inflation is fixed through local-scale bake + rigid attachments;
- binary semantic masks validate skin/hair/cloth/metal;
- gait period is derived from G2 contacts: `80` frames at 120 fps;
- sampled phases: `1568,1588,1608,1628`;
- G1 camera/scale remain usable.

## Retarget blocker — RESOLVED

Earlier G3V body runs exposed two invalid motion-transfer shortcuts:

1. raw Blender `Action` copy froze the target pose;
2. raw per-frame `matrix_basis` copy produced phase changes but collapsed pelvis/legs/trunk.

G3V-R isolated the problem and measured:

- parent mismatches: `0`;
- mean rest-orientation delta: `83.1874 deg`;
- max rest-orientation delta: `180.0289 deg`.

Therefore the two rigs share naming/hierarchy but not compatible local/rest axes.

Accepted method:

**`DIRECTION_SPACE_FK`**

It transfers posed bone directions through world/target-armature space while preserving MPFB hierarchy, bone lengths, weights and roll/twist convention.

Measured preflight articulation:

- 4 unique poses;
- mean elbow/knee error: `0.0000 deg`;
- max elbow/knee error: `0.0001 deg`.

V3 then replaced the invalid rest-subtracted endpoint metric with `CHAIN_UNIT_DIRECTION_RMS`; the resulting source-vs-target skeleton sheet passed visual review with no limb duplication, no collapse and correct phase/left-right correspondence.

Canonical approval marker:

`tools/deterministic-character-pipeline/g3v_retarget_approval.json`

Canonical retarget log:

`docs/G3V_RETARGET_PREFLIGHT_LOG.md`

## Current body motion binding

`tools/deterministic-character-pipeline/g3v_motion_binding_patch.py`

now uses the accepted direction-space solver. Raw `Action`, raw `matrix_basis` and local-axis transfer are disabled as motion authority.

Expected body-run markers include:

- `G3V_MOTION_BINDING=DIRECTION_SPACE_FK_VALIDATED_G3V_R`
- `G3V_MOTION_LOCAL_AXIS_COPY=DISABLED`
- `G3V_MOTION_BINDING_MODE=VALIDATED_DIRECTION_SPACE_PER_FRAME`
- `G3V_MOTION_UNIQUE_POSES=...`
- `G3V_MOTION_UNIQUE_SKIN_MASKS=...`
- `G3V_MOTION_DIVERSITY_AUDIT=PASS`

## G3V visual kill switch — NEXT

The next run is the first body/pixel sheet eligible for the actual G3V decision.

Review order:

1. topology integrity: one head/torso, two arms/hands, two legs/feet;
2. real motion and grounding across the four gait phases;
3. coherent weighted body deformation;
4. stability of hair/cloth/restraints;
5. pixel-specific visual headroom.

If the technically coherent representative human still reads merely as conventional/low-resolution 3D made blocky, hidden 3D is rejected as owner of final visible character art while remaining the motion/topology/socket/physics backbone.

If it shows credible headroom toward intentional modern pixel art, G3V can PASS and G4 identity mapping may begin.

G4 remains blocked until this visual review.

## Exact next action

Run only:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\deterministic-character-pipeline\03c_run_g3v.ps1"
```

Then STOP. If it reaches `G3V: REVIEW REQUIRED`, share:

`Z:\AI\RogueliteCharacterPipeline\g3v\g3v_contact_sheet.png`

If it fails, share the complete console output. Do not start G4.
