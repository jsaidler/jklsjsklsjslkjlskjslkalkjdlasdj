# G3S-C1 — Hidden Skeleton Walk Guide

Status date: **2026-09-07**

Gate status: **C1A MECHANICAL SKELETON GAIT PASS/CLOSED / C1C 72 DEG GAMEPLAY WALK AUTHORING ACTIVE**

## Purpose

Canonical motion path:

`real motion -> hidden skeleton/rig -> gameplay-authored pose/laterality/depth/contact control -> complete visible 2D pose assets -> sprite playback`

The hidden guide is skeletal control data only. It does not require or render a skinned human body.

## Closed history

C1A V1–V5 attempted to use a skinned MPFB body for hidden visual/depth guidance and are closed. V5 proved the skeleton remained coherent while the skin mesh exploded. V6 was superseded before meaningful execution after the architecture was corrected to skeleton-only control.

The first skeleton-only run then hit a technical camera-selection bug. That failure is CLOSED/RESOLVED.

No model/API/download/runtime was added by C1A.

## Approved C1A source

- motion: `CMU 105_34 NormalWalk`;
- armature: `G2_CANONICAL_RIG`;
- local blend: `Z:\AI\RogueliteCharacterPipeline\g2\g2_motion_topology.blend`;
- G2 approval: PASS.

No MPFB body or G3V body is used by current C1A/C1C skeleton control.

## Approved C1A eight-state mechanical cycle

| Index | Source frame | Event | Support foot |
|---:|---:|---|---|
| 0 | 1588 | left_contact | left |
| 1 | 1598 | left_down | left |
| 2 | 1608 | left_passing | left |
| 3 | 1618 | left_up | left |
| 4 | 1628 | right_contact | right |
| 5 | 1638 | right_down | right |
| 6 | 1648 | right_passing | right |
| 7 | 1658 | right_up | right |

Review playback uses `83 ms` per state.

Original C1A camera/control sanity baseline:

- `640×360`;
- orthographic;
- pitch `26°`;
- horizontal camera azimuth `45°` from measured travel heading;
- maximum projected skeleton height approximately `128 px`;
- real forward travel normalized to screen-left.

## What C1A actually approved

C1A proved:

- coherent eight-state human gait timing;
- left/right progression;
- intact limb chains;
- support-foot progression;
- readable pelvis/trunk/leg relationship;
- laterality and near/far readability;
- screen-left directional family.

It was a **mechanical motion/control PASS**, not a final animation-art-direction lock.

Runner 30 later proved that once target-pose registration is corrected, visible authoring responds much more strongly to the C1A phases, but the resulting walk still lacks the naturality and gameplay-specific pose language expected for the project.

Therefore:

- C1A remains PASS/CLOSED as a hidden human-gait sanity/control source;
- generic CMU `NormalWalk` is retained as phase/timing/support material, not sacred final pose language;
- the old `45°` camera projection is historical/mechanical only.

## Runner 31 gameplay-facing audit — CLOSED

Runner 31 reprojected the same real gait at `60`, `72` and `84°` while keeping the rest of the camera/motion baseline fixed.

Decision:

- `60°` rejected as too frontal;
- `84°` rejected as too profile-thin for the first gameplay baseline;
- **`72°` selected as the gameplay locomotion facing baseline**.

In the current convention `90°` is pure side profile. `72°` preserves enough three-quarter body exposure while materially improving lateral gait readability.

## Current gate — C1C gameplay walk overlay V1

Canonical document:

`docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`

Runner:

`tools/structured-2d-character-pipeline/32_run_g3s_c1c_gameplay_walk_overlay_v1.ps1`

Helper:

`tools/structured-2d-character-pipeline/g3s_c1c_apply_gameplay_walk_overlay.py`

Runner 32 rebuilds a fresh `72°` raw skeleton baseline, then applies one deterministic gameplay authoring overlay while retaining the real gait timing/support order.

V1 controls:

- compact projected stride;
- reduced pelvis/root bob;
- mild forward upper-body intent;
- reduced casual arm pendulum;
- head stabilization.

This remains skeleton-only. No SSD/diffusion run is authorized until the gameplay walk itself passes.

## C1A implementation retained

- spec: `tools/structured-2d-character-pipeline/g3s_c1_skeleton_walk_spec.json`;
- exporter: `tools/structured-2d-character-pipeline/g3s_c1_export_skeleton_walk.py`;
- review builder: `tools/structured-2d-character-pipeline/g3s_c1_build_skeleton_walk_review.py`;
- original runner: `tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`;
- original workspace: `Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk`.

Do not rerun runner 21 as though it were the current production gate.
