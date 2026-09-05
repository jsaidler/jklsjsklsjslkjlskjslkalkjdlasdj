# G3V Representative Visual Proxy — Execution Log

Status date: **2026-09-05**

Gate: **G3V — representative continuous human asset + deterministic pixel translation**

Current status: **PAUSED AT G3V-R RETARGET PREFLIGHT V3. DO NOT RERUN BODY RENDER.**

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

That isolated the blocker to **retargeting between incompatible rest spaces**.

Rejected shortcuts:

1. copying the source Blender `Action` onto MPFB;
2. copying source `matrix_basis` directly into MPFB.

## Active sub-gate — G3V-R

Canonical log:

`docs/G3V_RETARGET_PREFLIGHT_LOG.md`

Runner:

`tools/deterministic-character-pipeline/03d_run_g3v_retarget_preflight.ps1`

Locked rest-rig facts:

- required parent mismatches: `0`;
- mean rest-orientation delta: `83.1874 deg`;
- max rest-orientation delta: `180.0289 deg`.

V1 local-axis transfer failed.

V2 then proved an important distinction:

- `DIRECTION_SPACE_FK` reproduced elbow/knee articulation essentially exactly: mean `0.0000 deg`, max `0.0001 deg`, 4 unique poses;
- MPFB's pose API remained much worse: mean `25.4032 deg`, max `44.3890 deg`;
- V2 still failed because the old endpoint metric compared motion relative to each rig's incompatible rest pose.

That endpoint metric is invalid under an ~83 deg mean rest-orientation mismatch and is now closed.

## G3V-R V3 — CURRENT

V3 keeps the successful axis-independent `DIRECTION_SPACE_FK` solver and replaces only the invalid endpoint test with a rest-independent chain-shape metric:

`CHAIN_UNIT_DIRECTION_RMS`

It compares normalized posed direction chains for torso, arms and legs, so target bone lengths/proportions remain owned by MPFB instead of being falsely penalized against the source rest skeleton.

No quality threshold was relaxed merely to obtain PASS.

G3V resumes only after V3:

1. passes numeric articulation/chain-shape validation;
2. produces source-vs-target skeleton contact sheet;
3. is visually confirmed to preserve gait phase, left/right alternation and topology without collapse.

Only then is the old G3V motion binding replaced and the body/pixel contact sheet rerun.

## G3V final kill switch

After retarget is valid, G3V can pass only if the representative human remains coherent through motion and its native-grid translation shows credible headroom toward intentional modern pixel art.

If a technically valid human still reads merely as low-resolution 3D, hidden 3D is rejected as owner of final visible character art while remaining the motion/topology/socket/physics backbone.

G4 remains blocked.
