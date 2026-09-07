# G3S-C1B — Visible Exilada Walk Proof

Status date: **2026-09-06**

Gate status: **C1A PASS/CLOSED / C1B FLUX2 PER-FRAME REDRAW FAIL/CLOSED / SEGMENTED 2D SKELETAL PUPPET CURRENT**

## Purpose

C1B exists to show the Exilada herself moving while preserving one persistent visible character.

Approved hidden motion remains:

`real mocap -> approved hidden skeleton cycle`

The visible side has now been corrected to:

`persistent native-2D body parts -> bind to hidden skeleton -> project/transform/depth-sort -> composite sprite`

## C1A input — PASS

Approved cycle:

`1588 left_contact -> 1598 left_down -> 1608 left_passing -> 1618 left_up -> 1628 right_contact -> 1638 right_down -> 1648 right_passing -> 1658 right_up`

Approval:

`tools/structured-2d-character-pipeline/g3s_c1a_skeleton_walk_approval.json`

Reviewed evidence:

- contact sheet SHA256 `672c8f9cb419cb8aa317447801931ce76da07b101b766c3f616bb2c25a39c2cd`;
- zoom GIF SHA256 `9a61ae7414be04ef4a89d8f83127e73d58e46da2075f37e23b7b048864286970`;
- projected root travel approximately `-43.77 px` screen-left.

C1A remains valid.

## Canonical visible identity

`assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`

- `37×128` RGBA;
- bald adult nude body;
- screen-left front-three-quarter family;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`.

The canonical file remains unchanged.

## Flux2 per-frame redraw — FAIL/CLOSED

The reviewed visual proof generated a complete new body independently for every gait state.

Reviewed output:

- GIF SHA256 `edc4216172a578948bef61967d3773377499c2ce5e7053867fdf75c4f41d99ee`;
- contact sheet SHA256 `8df1d1bfc281c6cc97c26faef47dba1cec44330d2348d6daaa6f4877b41beb4e`.

Observed failure:

- face/identity changed across frames;
- skin tone and shading changed;
- breast/waist/shoulder/body proportions changed;
- camera/silhouette family drifted;
- pixel-art treatment drifted;
- playback reads as several different women rather than one persistent Exilada.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c1b_flux2_visual_failure.json`

Closed method:

`approved skeleton pose -> independent generative full-body redraw per frame`

The old runner is intentionally disabled:

`tools/structured-2d-character-pipeline/22_run_g3s_c1b_flux2_walk_visual_proof.ps1`

No new model/runtime was installed by this gate. The pre-existing FLUX2 stack remains retained for unrelated bounded experiments; no cleanup applies.

## CURRENT — segmented persistent 2D skeletal puppet

Canonical architecture:

`approved C1A skeleton -> persistent 2D body-part atlas -> anatomical pivots/bindings -> projected bone position/rotation/length -> camera-space depth order -> composited native-2D body frame`

Detailed document:

`docs/G3S_C1B_SEGMENTED_PUPPET.md`

Spec:

`tools/structured-2d-character-pipeline/g3s_c1b_segmented_puppet_spec.json`

Initial persistent parts:

- head/neck;
- torso;
- pelvis;
- left/right upper arm;
- left/right forearm;
- left/right hand;
- left/right thigh;
- left/right shin;
- left/right foot.

### Critical difference from C0 V1

The current method may not repeat `nearest-segment hard partition + independent rigid rotation`.

It requires explicit pivots, deliberate hidden overlap under joints, continuous torso/pelvis connection, skeleton-driven depth order, and small reusable orientation/foreshortening variants only where one flat part is insufficient.

Those variants are frozen persistent assets, never independent full-body frame redraws.

## Next implementation

The next runner must produce:

- segmented native-2D body-part atlas;
- pivot/binding manifest;
- eight body-only walk frames driven by C1A;
- in-place GIF;
- travel GIF;
- contact sheet with optional skeleton overlay.

PASS requires one recognizable persistent Exilada body through the entire cycle with intact joints, stable proportions/identity and correct screen-left locomotion.

Hair remains deferred.
