# G3S-C1B — Visible Exilada Walk Proof

Status date: **2026-09-06**

Gate status: **C1A PASS/CLOSED / C1B EIGHT-FRAME FLUX2 VISUAL PROOF RUNNER READY / REVIEW REQUIRED**

## Purpose

C1B is the first step that should finally show the Exilada herself moving rather than only hidden-control data.

Architecture remains:

`real mocap -> approved hidden skeleton cycle -> complete visible 2D redraw per gait state -> sprite playback`

C1B does **not** warp the static B3B body and does not expose/render a hidden human 3D body.

## C1A input — PASS

Approved hidden motion cycle:

`1588 left_contact -> 1598 left_down -> 1608 left_passing -> 1618 left_up -> 1628 right_contact -> 1638 right_down -> 1648 right_passing -> 1658 right_up`

Approval:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_walk_approval.json`

Reviewed evidence:

- contact sheet SHA256 `672c8f9cb419cb8aa317447801931ce76da07b101b766c3f616bb2c25a39c2cd`;
- zoom GIF SHA256 `9a61ae7414be04ef4a89d8f83127e73d58e46da2075f37e23b7b048864286970`;
- observed projected root travel approximately `-43.77 px` screen-left.

C1A passed coherent gait, left/right progression, support-foot progression, limb-chain integrity, pelvis/trunk/leg readability and directional-family sanity.

## Visible identity anchor

Canonical body remains unchanged:

`assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`

- `37×128` RGBA;
- bald adult nude body;
- screen-left front-three-quarter family;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`.

It is used only as identity/body-style conditioning. It is not deformed into the gait.

## Current C1B implementation

This is a bounded **visual animation proof**, not automatic production promotion.

It reuses the already-retained local FLUX.2 Klein stack at:

`Z:\AI\Flux2RefControlSpike`

Required existing model files:

- `flux-2-klein-base-4b-fp8.safetensors`;
- `qwen_3_4b.safetensors`;
- `flux2-vae.safetensors`.

No download and no paid API are permitted by this runner.

Each of the eight gait states receives two visual references:

1. exact B3B body identity/style reference on a `96×160` logical neutral canvas, integer-enlarged to `576×960` for model conditioning;
2. one clean skeleton-derived pose-control image generated from the approved C1A joint data.

The model must redraw a complete bald nude barefoot adult body for every state. It is explicitly forbidden to output hair, clothing, restraints, accessories or weapons at this gate.

## Current files

Spec:

`tools/structured-2d-character-pipeline/g3s_c1b_flux2_walk_spec.json`

Input preparation:

`tools/structured-2d-character-pipeline/g3s_c1b_prepare_flux2_walk_inputs.py`

Review builder:

`tools/structured-2d-character-pipeline/g3s_c1b_build_flux2_walk_review.py`

Runner:

`tools/structured-2d-character-pipeline/22_run_g3s_c1b_flux2_walk_visual_proof.ps1`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1b_flux2_walk_visual_proof`

## Expected outputs

Primary review artifacts:

- `g3s_c1b_exilada_walk_visual_proof.gif`;
- `g3s_c1b_exilada_walk_contact_sheet.png`;
- `g3s_c1b_review.json`;
- eight generated full-resolution candidate frames;
- eight `96×160` nearest-neighbor inspection reductions.

The reductions are review-only. They are **not** mechanically promoted into final native production art.

## PASS requirement

C1B visual proof passes only if the animation reads as one coherent woman across all eight states:

- recognizable continuity with B3B body proportions/style;
- adult bald nude body throughout;
- exactly two arms/two legs with connected plausible anatomy;
- no detached/duplicate/melted limbs;
- same screen-left elevated front-three-quarter family;
- gait progression follows the approved C1A skeleton;
- no frame catastrophically changes body type, view or identity;
- playback reads as a walk rather than eight unrelated poses.

## Promotion rule

Nothing produced by C1B is automatically a production sprite.

If the visual proof succeeds, the next action is to freeze/author the accepted eight-state native-2D body family without violating the existing rule against mechanically shrinking/quantizing arbitrary high-resolution art into final production assets.

Hair remains deferred and must not return during this body locomotion proof.
