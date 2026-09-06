# G3S-C1 — Hidden Skeleton Walk Guide

Status date: **2026-09-06**

Gate status: **C1A SKELETON-ONLY EIGHT-STATE WALK PASS/CLOSED / C1B VISIBLE WALK PROOF CURRENT**

## Purpose

Canonical motion path:

`real motion -> hidden skeleton/rig -> pose/laterality/depth/contact/root control -> complete visible 2D pose assets -> sprite playback`

The hidden guide is skeletal control data only. It does not require or render a skinned human body.

## Closed history

C1A V1–V5 attempted to use a skinned MPFB body for hidden visual/depth guidance and are closed. V5 proved the skeleton remained coherent while the skin mesh exploded. V6 was superseded before meaningful execution after the architecture was corrected to skeleton-only control.

The first skeleton-only run then hit a technical camera-selection bug:

`RuntimeError: could not choose front-three-quarter camera with screen-left forward travel`

That failure is now **CLOSED/RESOLVED**. Marker:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_camera_selection_failure.json`

No model/API/download/runtime was added by C1A; no cleanup applies.

## Approved source

- motion: `CMU 105_34 NormalWalk`;
- armature: `G2_CANONICAL_RIG`;
- local blend: `Z:\AI\RogueliteCharacterPipeline\g2\g2_motion_topology.blend`;
- G2 approval: PASS.

No MPFB body or G3V body is used by current C1A.

## Approved eight-state cycle

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

Camera/control baseline:

- `640×360`;
- orthographic;
- pitch `26°`;
- front-three-quarter at `45°` from measured travel heading;
- rig is not rotated to manufacture facing;
- maximum projected skeleton height approximately `128 px`;
- real forward travel normalized to the canonical screen-left family.

## C1A approval

Approval file:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_walk_approval.json`

Reviewed artifacts supplied by the user:

- contact sheet SHA256 `672c8f9cb419cb8aa317447801931ce76da07b101b766c3f616bb2c25a39c2cd`;
- zoom GIF SHA256 `9a61ae7414be04ef4a89d8f83127e73d58e46da2075f37e23b7b048864286970`;
- projected root travel approximately `-43.77 px` screen-left.

Visual review PASS:

- coherent eight-state gait;
- left/right progression;
- intact limb chains;
- support-foot progression;
- readable pelvis/trunk/leg relationship;
- laterality and near/far readability;
- screen-left directional family.

C1A is therefore **PASS/CLOSED**. It approves only the hidden motion/control cycle, not final visible body art.

## C1A implementation retained

- spec: `tools/structured-2d-character-pipeline/g3s_c1_skeleton_walk_spec.json`;
- exporter: `tools/structured-2d-character-pipeline/g3s_c1_export_skeleton_walk.py`;
- review builder: `tools/structured-2d-character-pipeline/g3s_c1_build_skeleton_walk_review.py`;
- runner: `tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`;
- workspace: `Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk`.

## Current next gate — C1B

C1B now goes directly to a visible eight-frame Exilada walk proof using:

- the approved C1A skeleton cycle as pose/spatial control;
- canonical B3B V4 as visible identity/body-style anchor;
- no static-body warp;
- no hidden-3D RGB promotion;
- no hair/clothing/accessories yet.

Current C1B document:

`docs/G3S_C1B_VISIBLE_WALK_PROOF.md`
