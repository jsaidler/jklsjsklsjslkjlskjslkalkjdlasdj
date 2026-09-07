# G3S-C1 — Hidden Skeleton Walk Guide

Status date: **2026-09-07**

Gate status: **C1A MECHANICAL SKELETON GAIT PASS/CLOSED / C1C GAMEPLAY LOCOMOTION MASTER ACTIVE**

## Purpose

Canonical motion path:

`real motion -> hidden skeleton/rig -> pose/laterality/depth/contact/root control -> complete visible 2D pose assets -> sprite playback`

The hidden guide is skeletal control data only. It does not require or render a skinned human body.

## Closed history

C1A V1–V5 attempted to use a skinned MPFB body for hidden visual/depth guidance and are closed. V5 proved the skeleton remained coherent while the skin mesh exploded. V6 was superseded before meaningful execution after the architecture was corrected to skeleton-only control.

The first skeleton-only run then hit a technical camera-selection bug:

`RuntimeError: could not choose front-three-quarter camera with screen-left forward travel`

That failure is CLOSED/RESOLVED. Marker:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_camera_selection_failure.json`

No model/API/download/runtime was added by C1A; no cleanup applies.

## Approved C1A source

- motion: `CMU 105_34 NormalWalk`;
- armature: `G2_CANONICAL_RIG`;
- local blend: `Z:\AI\RogueliteCharacterPipeline\g2\g2_motion_topology.blend`;
- G2 approval: PASS.

No MPFB body or G3V body is used by current C1A.

## Approved C1A eight-state cycle

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

Original C1A camera/control baseline:

- `640×360`;
- orthographic;
- pitch `26°`;
- horizontal camera azimuth `45°` from measured travel heading;
- rig is not rotated to manufacture facing;
- maximum projected skeleton height approximately `128 px`;
- real forward travel normalized to the canonical screen-left family.

## What C1A actually approved

Approval file:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_walk_approval.json`

Reviewed artifacts supplied by the user:

- contact sheet SHA256 `672c8f9cb419cb8aa317447801931ce76da07b101b766c3f616bb2c25a39c2cd`;
- zoom GIF SHA256 `9a61ae7414be04ef4a89d8f83127e73d58e46da2075f37e23b7b048864286970`;
- projected root travel approximately `-43.77 px` screen-left.

C1A proved:

- coherent eight-state human gait;
- left/right progression;
- intact limb chains;
- support-foot progression;
- readable pelvis/trunk/leg relationship;
- laterality and near/far readability;
- screen-left directional family.

### Scope correction after visible runner 30

The approval was **mechanical**, not an animation-art-direction lock.

Runner 30 demonstrated that once pose registration is corrected, the visible authoring model responds much more strongly to the C1A phases, yet the resulting walk still lacks the naturality and gameplay-specific posture expected for the project.

Therefore:

- C1A remains PASS/CLOSED as a hidden human-gait sanity/control source;
- C1A is **not** the final production gameplay locomotion master;
- generic CMU `NormalWalk` is retained as phase/timing material, not sacred final pose language;
- the original `45°` horizontal camera azimuth is reopened for gameplay locomotion review because the belt-scroller needs a more lateral read.

This distinction supersedes any earlier wording implying C1A itself was the final visible-walk pose source.

## C1A implementation retained

- spec: `tools/structured-2d-character-pipeline/g3s_c1_skeleton_walk_spec.json`;
- exporter: `tools/structured-2d-character-pipeline/g3s_c1_export_skeleton_walk.py`;
- review builder: `tools/structured-2d-character-pipeline/g3s_c1_build_skeleton_walk_review.py`;
- runner: `tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`;
- workspace: `Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk`.

Do not rerun runner 21 as though it were the current production gate.

## Current gate — C1C gameplay locomotion master

Canonical document:

`docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`

The immediate question is now:

> Which mostly-lateral presentation makes the retained real gait read correctly for the elevated arcade belt-scroller before we author additional pose style?

Runner:

`tools/structured-2d-character-pipeline/31_run_g3s_c1c_gameplay_facing_audit.ps1`

Runner 31 uses the exact same real gait and samples but generates skeleton-only review packages at:

- `60°` azimuth from travel heading;
- `72°`;
- `84°`.

`90°` is pure side view in the current camera convention. The old C1A used `45°`.

This is deliberately skeleton-only. No SSD/diffusion run is authorized until the gameplay-facing choice is reviewed.

If a facing is selected but the motion remains too neutral, C1C will then author an additive gameplay locomotion treatment while retaining real gait timing/support phases.
