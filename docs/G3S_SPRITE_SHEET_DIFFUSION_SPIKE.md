# G3S — Sprite Sheet Diffusion validation spike

Status date: **2026-09-07**

Gate status: **ACTIVE — EXACT UPSTREAM SSD BLOCKED / RUNNER 29 TECHNICAL PASS + VISUAL FAIL / RUNNER 30 POSE-REGISTRATION DISCRIMINANT READY**

## Decision

The character-production target remains a conventional **2D spritesheet**: approved persistent frames arranged by action in rows/blocks or equivalent atlas regions, with metadata for timing, pivots, hitboxes and events as needed.

Diffusion is an offline authoring candidate only. Runtime remains ordinary spritesheet playback.

## Presentation/runtime lock retained

- elevated arcade beat'em-up / belt-scroller false 3D;
- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- first visible family screen-left/front-three-quarter;
- gameplay depth movement does not require north/south/isometric sprite families;
- runtime world translation/root movement is separate from sprite-frame playback.

## Local SSD environment / support — PASS

Workspace: `Z:\AI\SpriteSheetDiffusionSpike`

Validated:

- Miniconda / env `ssd` PASS;
- Python `3.10.21`;
- RTX 3060;
- Torch `2.0.1+cu118` / CUDA 11.8;
- DWPose available;
- FILM available but not default;
- SD1.5 UNet, VAE and CLIP image encoder present;
- released SSD denoising/reference UNets present;
- AnimateAnyone baseline pose guider + motion module present.

## Canonical walk8 source motion

No manual pose folder is required.

| Index | Source frame | Event | Support foot |
|---:|---:|---|---|
| 0 | 1588 | `left_contact` | left |
| 1 | 1598 | `left_down` | left |
| 2 | 1608 | `left_passing` | left |
| 3 | 1618 | `left_up` | left |
| 4 | 1628 | `right_contact` | right |
| 5 | 1638 | `right_down` | right |
| 6 | 1648 | `right_passing` | right |
| 7 | 1658 | `right_up` | right |

Canonical guide:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_guide.json`

Correct conceptual split:

`Exilada master --DWPose--> reference body pose`

`approved C1A guide --deterministic OpenPose-style conversion--> eight target body poses`

## Exact upstream SSD — BLOCKED

Runner 28 reached real model initialization but failed at strict loading of `pose_guider.pth`.

The public baseline checkpoint is Moore/AnimateAnyone architecture:

`conv_in / blocks / conv_out`

Current SSD code requires its unreleased custom multi-scale architecture:

`conv_layers* / final_proj / cross_attn* / scale`

SSD's modified UNet consumes multiple pose-feature scales, while Moore's original graph consumes one. The public SSD model release does not contain the required custom trained `pose_guider.pth`; upstream issue #3 documents the same blocker.

Therefore exact current-upstream SSD inference is **not reproducible from the public checkpoint set**. Do not run runner 28 again and do not load the baseline checkpoint loosely into SSD's custom PoseGuider.

Manifest status:

`EXACT_UPSTREAM_INFERENCE_BLOCKED_POSE_GUIDER_UNRELEASED`

## Moore-compatible salvage route

Fallback graph:

`Moore-AnimateAnyone graph + baseline Moore PoseGuider/motion module + released SSD fine-tuned denoising/reference UNets`

This is explicitly **not** the exact published SSD graph.

Pinned Moore source:

`a914ef38aae3733c2f02f29853dd0593372e0cc9`

## Runner 29 — TECHNICAL PASS

Runner:

`tools/structured-2d-character-pipeline/29_run_ssd_moore_compat_exilada_walk8.ps1`

Actual execution completed:

- canonical input rebuilt;
- Moore source pinned/reset;
- released SSD reference UNet loaded strictly;
- released SSD denoising UNet produced 0 unexpected Moore keys;
- 588 missing denoising keys were accepted under the intended partial overlay after SD1.5 + motion-module initialization;
- baseline Moore pose guider loaded strictly;
- 8 frames generated at `512×512`, 25 steps, CFG `3.5`, seed `42`, fp16;
- diffusion completed in about 42 s on RTX 3060;
- PNG frames, contact sheet, GIF and result marker were written.

Technical marker:

`PASS_OUTPUT_READY_FOR_VISUAL_QA`

## Runner 29 — VISUAL QA FAIL

The supplied contact sheet/GIF were reviewed against the intended eight-state C1A walk.

### Identity / appearance

Partial pass:

- Exilada's overall silhouette remained recognizable;
- long dark hair and core costume masses remained present;
- identity did not catastrophically drift.

But stability was achieved partly by keeping the body too close to a near-static reference pose.

### Anatomy / lower limbs

Fail:

- lower legs, ankles and feet became unstable across frames;
- foot/ground topology was not trustworthy;
- detached dark fragments appeared near the ground;
- the sequence was not suitable to freeze as production sprites.

### Pose obedience

Fail:

- frames 1–4 were too similar to one another;
- frames 5–8 were also insufficiently differentiated;
- contact/down/passing/up phases were not clearly readable;
- left/right support progression was weak.

### Temporal coherence

Insufficient:

- the sequence did not explode temporally;
- however, much of that apparent coherence came from under-articulation rather than a convincing walk cycle.

### Runner 29 decision

**TECHNICAL PASS / VISUAL FAIL.**

Do not expand to new actions, FILM, spritesheet packing or parameter sweeps from runner 29.

## Post-QA inspection found a concrete pose-preparation defect

The existing `g3s_ssd_prepare_walk8.py` maps the locked C1A `640×360` screen-space coordinates into a `512×512` pose canvas by normalizing X and Y independently:

```text
x' = (x / 640) * 512   -> X scale 0.8
y' = (y / 360) * 512   -> Y scale 1.422222...
```

Therefore target skeleton geometry receives a **1.777777...× relative vertical stretch** compared with horizontal geometry before it reaches the pose guider.

This also does not explicitly register target-body scale/position to the DWPose body footprint extracted from the Exilada master.

That is a stronger, testable explanation for runner 29's weak pose obedience than arbitrary CFG/seed tuning or a master crop.

## Runner 30 — single discriminating experiment

Purpose:

> Determine whether runner 29 failed primarily because the C1A target pose maps were spatially distorted/misregistered to the master reference body.

New helper:

`tools/structured-2d-character-pipeline/g3s_ssd_align_walk8_poses.py`

New runner:

`tools/structured-2d-character-pipeline/30_run_ssd_moore_compat_exilada_walk8_pose_aligned.ps1`

### What changes

Only target-pose spatial registration:

1. rebuild the same canonical Exilada + C1A baseline input;
2. measure the nonzero DWPose body bounding box extracted from the master;
3. reconstruct the eight target OpenPose maps directly from original `640×360` C1A joints using **one uniform scale**;
4. register pelvis X to the master-reference body center;
5. register the lowest ankle Y to the master-reference body bottom;
6. remove per-frame root travel so this test is an in-place sprite-authoring cycle; runtime translation remains separate;
7. hard-fail on clipping, duplicate pose maps or poor body-height registration;
8. emit a 3×3 pose-alignment review image before inference.

### What does NOT change

- Exilada master;
- Moore graph;
- released SSD denoising/reference UNets;
- baseline Moore pose guider;
- motion module;
- resolution `512×512`;
- frame count 8;
- 25 diffusion steps;
- CFG `3.5`;
- seed `42`;
- fp16;
- no FILM;
- no master crop;
- no resolution/CFG/seed sweep;
- no new action.

This makes runner 30 a clean A/B test against runner 29.

## Runner 30 technical outputs

Input/alignment artifacts:

- marker: `Z:\AI\SpriteSheetDiffusionSpike\ssd_exilada_walk8_pose_aligned_input.json`;
- pose review: `Z:\AI\SpriteSheetDiffusionSpike\exilada_walk8_pose_aligned_inputs\exilada_walk8_pose_alignment_review.png`.

Generated artifacts:

- frames: `Z:\AI\SpriteSheetDiffusionSpike\exilada_walk8_moore_compat_pose_aligned\frames`;
- contact sheet: `Z:\AI\SpriteSheetDiffusionSpike\exilada_walk8_moore_compat_pose_aligned\exilada_walk8_moore_compat_contact_sheet.png`;
- GIF: `Z:\AI\SpriteSheetDiffusionSpike\exilada_walk8_moore_compat_pose_aligned\exilada_walk8_moore_compat.gif`;
- result marker: `Z:\AI\SpriteSheetDiffusionSpike\ssd_exilada_walk8_moore_compat_pose_aligned.json`.

## Runner 30 decision rule — LOCKED

PASS requires a clear A/B improvement over runner 29 in **both**:

1. pose readability: distinct contact/down/passing/up phases with left/right alternation;
2. lower-limb integrity: stable leg/ankle/foot topology and believable ground contact;

while not materially degrading Exilada identity/proportions.

If runner 30 does not clearly improve those two failure classes, the Moore-compatible SSD salvage route is to be **closed**, rather than followed by uncontrolled tuning.

## Exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\30_run_ssd_moore_compat_exilada_walk8_pose_aligned.ps1"
```

Expected terminal marker:

`SSD-MOORE-POSE-ALIGNED: OUTPUT READY FOR A/B VISUAL QA`

Then share the pose-alignment review, generated contact sheet and GIF.

## Exact SSD future condition

Exact SSD remains blocked unless a trustworthy compatible custom pose-guider checkpoint becomes available or the project deliberately decides to retrain the missing custom pose stack.

## Cleanup

SSD remains active only through the bounded runner-30 discriminant. No cleanup applies before that A/B gate is closed.
