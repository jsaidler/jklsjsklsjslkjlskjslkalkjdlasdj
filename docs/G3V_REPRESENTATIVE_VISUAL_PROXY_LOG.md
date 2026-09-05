# G3V Representative Visual Proxy — Execution Log

Status date: **2026-09-05**

Gate: **G3V — representative continuous human asset + deterministic pixel translation**

Current status: **PAUSED AT G3V-R RETARGET PREFLIGHT V2. DO NOT RERUN BODY RENDER.**

## Locked upstream baseline

- G0 automation: PASS;
- G1: `640×360`, orthographic `26 deg`, hero `128 px`;
- G2: CMU `105_34 NormalWalk`, topology/motion PASS;
- G3: native translation technical PASS, production look not approved;
- G3R: renderer-only mannequin refinement FAIL / CLOSED.

## Proven G3V infrastructure

- MPFB `2.0.17` loads headlessly from pinned verified archive;
- continuous female body + weighted `cmu_mb` rig are created;
- long hair, degraded cloth, restraints and bare feet render;
- accessory scale inflation is fixed through local-scale bake + rigid attachments;
- binary semantic masks validate skin/hair/cloth/metal;
- gait period is derived from G2 contacts: `80` frames at 120 fps;
- current phases: `1568,1588,1608,1628`;
- G1 camera/scale remain usable.

## Why G3V is paused

The first coherent body sheet showed one frozen pose across all four frames. Raw per-frame `matrix_basis` copying then produced visibly distinct phases, but later poses collapsed around pelvis/legs/trunk.

That means:

- source mocap is not the blocker;
- frame selection is not the blocker;
- MPFB rendering/weights exist;
- the blocker is **retargeting between incompatible rest spaces**.

Two shortcuts are therefore rejected:

1. copying the source Blender `Action` onto MPFB;
2. copying source `matrix_basis` directly into MPFB.

## Active sub-gate — G3V-R

Canonical log:

`docs/G3V_RETARGET_PREFLIGHT_LOG.md`

Runner:

`tools/deterministic-character-pipeline/03d_run_g3v_retarget_preflight.ps1`

V1 measured zero parent mismatches but very large rest-orientation differences:

- mean: `83.1874 deg`;
- max: `180.0289 deg`.

Its local-axis fallback failed with:

- mean joint-angle error: `25.0101 deg`;
- max angle error: `43.6810 deg`;
- endpoint RMS: `0.27541` body heights.

V1 is closed.

V2 now tests:

- context-correct MPFB pose API in actual Pose Mode;
- `DIRECTION_SPACE_FK`, which matches posed bone directions in world/target armature space while keeping MPFB hierarchy, bone lengths, weights and roll convention.

The canonical `03d` command is unchanged; bootstrap automatically routes to V2.

## G3V resume condition

Do not return to the body render until G3V-R:

1. passes numeric thresholds;
2. produces a source-vs-target skeleton sheet;
3. visually preserves gait phase, topology, knees/elbows and left/right alternation without collapse.

Only then replace the old motion binding and rerun G3V.

## G3V final kill switch

After retarget is valid, G3V can pass only if the representative human remains coherent through motion and its native-grid translation shows credible headroom toward intentional modern pixel art.

If a technically valid human still reads merely as low-resolution 3D, hidden 3D is rejected as owner of final visible character art while remaining the motion/topology/socket/physics backbone.

G4 remains blocked.
