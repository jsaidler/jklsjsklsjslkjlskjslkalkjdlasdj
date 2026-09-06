# G3S-B4 — Hair Layer

Status date: **2026-09-06**

Gate status: **B4A PASS/CLOSED — B4B V1/V2/V3/V4 CLOSED — PROCEDURAL HAIR AUTHORING CLOSED — B4C REAL VISUAL ADAPTER RUNNER READY / REVIEW NEXT**

## Immutable entry condition

Canonical B3B production body:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`
- promotion commit `2deb765c3980d586ef9747340bb48852dedca452`;
- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`.

The body remains byte/pixel unchanged. Hair owns separate visible RGB/alpha/silhouette.

## Canonical hair identity

The Exilada's hair is black/nearly black, very long, heavy, voluminous, messy, wild and materially lived-in. `exilada_master.png` is an **identity/style/mass/material reference only**. Its pose, clothes, restraints and accessories are not production placement/template data.

## Hair depth architecture — LOCKED

Minimum deterministic composition:

`rear_hair -> body -> front_hair`

- `rear_hair`: persistent transparent mass behind head/neck/shoulders/back/body;
- `front_hair`: persistent transparent scalp/framing/locks in front where needed;
- one flat overlay is invalid;
- later side/intermediate sublayers are allowed only if real occlusion/secondary motion requires them.

## Closed B4B route history

### B4A — PASS/CLOSED DIAGNOSTIC

Reviewed contact sheet SHA256:

`efd8866a38be1ad54aa60f4f05249813b5abf1754ee0a318fcf92a45ff262d4f`

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b4a_preflight_approval.json`

B4A established the two-layer depth contract and the `96×160` review frame. It did not create production hair pixels.

### B4B V1 — FAIL/CLOSED PRE-RUN METHOD

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v1_extraction_route_failure.json`

Reason: the master does not contain enough hidden rear-hair information to recover a valid `rear_hair` by extraction.

### B4B V2 — FAIL/CLOSED VISUAL / STRUCTURAL PASS

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v2_visual_failure.json`

The two-layer ownership split passed, but the visual result failed as a centered curtain/bell with excessive front coverage, cape-like rear mass and repetitive lock rhythm.

### B4B V3 — FAIL/CLOSED VISUAL AND ALIGNMENT METHOD

Reviewed SHA256:

`9d922756f8815ea55cf55bed26d2bc0d24f51f93f89b3f47392126e027573f33`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v3_pose_mismatch_failure.json`

V3 authored hair in fixed master-like coordinates although master and production body use different poses.

### B4B V4 — FAIL/CLOSED VISUAL AND METHOD

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair\g3s_b4b_contact_sheet.png`

Reviewed SHA256:

`50dd663cbbeb0bb1a9865f2ac95daedc7990ceaf7a98ae6a968c8b7eacb4a8a5`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v4_pose_anchor_failure.json`

The V4 sheet reports `shoulder_span=6.36 px` for a `37 px`-wide body, proving the detector did not recover credible shoulder geometry. More fundamentally, head center/bounds, shoulder row/span, torso center and binary facing do not encode the actual 3/4 relationship of head tilt, shoulder slope, torso rotation, arm occlusion, back contour and local depth.

### Procedural route closure — LOCKED

The deterministic **Pillow polygon/line + heuristic-anchor hair-authoring route is closed**. Do not create another revision by adding more hand-tuned anchors, polygons, curves or procedural locks. Also do not return to master-pixel extraction or fixed master-pose geometry.

`tools/structured-2d-character-pipeline/17_run_g3s_b4b_two_layer_hair_candidate.ps1` is intentionally disabled.

No model/API was used by B4B V1-V4; no cleanup command applies.

## B4C — REAL VISUAL HAIR ADAPTER — CURRENT / RUNNER READY

User instruction `faça` reopens **only a narrow static B4 visual-adaptation use** of the already-retained local FLUX.2 workspace. This does **not** reopen the closed animation/refcontrol production route and does not start a new broad sprite-model search.

Machine-readable spec:

`tools/structured-2d-character-pipeline/g3s_b4c_flux2_visual_adapter_spec.json`

Input preparer:

`tools/structured-2d-character-pipeline/g3s_b4c_prepare_flux2_visual_adapter.py`

Review builder:

`tools/structured-2d-character-pipeline/g3s_b4c_build_flux2_visual_review.py`

Runner:

`tools/structured-2d-character-pipeline/18_run_g3s_b4c_flux2_visual_hair_adapter.ps1`

Expected workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4c_flux2_visual_adapter`

Expected review artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4c_flux2_visual_adapter\g3s_b4c_flux2_contact_sheet.png`

### Method

B4C is a **one-shot visual-capability gate**, not production promotion.

It:

1. verifies the exact canonical B3B body hashes;
2. uses the retained local `Z:\AI\Flux2RefControlSpike\ComfyUI_windows_portable` runtime only if its already-existing FLUX.2 Klein files are present;
3. downloads nothing and uses no paid API;
4. prepares image 1 from the exact B3B body on the `96×160` logical frame, enlarged by integer nearest-neighbor `6×` to `576×960`;
5. uses image 1 as authoritative body pose/proportion/scale/camera/placement reference;
6. uses the canonical master only as hair identity/style/material reference and explicitly forbids transfer of clothing, restraints, accessories and master pose;
7. asks the visual model to adapt the Exilada's very long heavy messy black hair to the **actual B3B body pose**, with dominant irregular rear mass and subordinate front framing;
8. produces one generated composite plus a contact sheet and a non-production `96×160` logical review sample;
9. performs no automatic promotion and does not create final `rear_hair`/`front_hair` assets yet.

### Why this intermediate gate exists

The repeated B4B failures show that it is wasteful to build another decomposition pipeline before proving that a visual author can actually understand the relationship between the approved body pose and the hair identity. B4C first tests that single capability.

If B4C visually passes, the next step is to use the same visual adapter in controlled rear/front passes and then persist separate native 2D `rear_hair` and `front_hair` assets. If it fails, the route is closed without touching the canonical body or B5/C.

### Runtime contract

Required existing local files inside `Z:\AI\Flux2RefControlSpike\ComfyUI_windows_portable\ComfyUI`:

- `models\diffusion_models\flux-2-klein-base-4b-fp8.safetensors`;
- `models\text_encoders\qwen_3_4b.safetensors`;
- `models\vae\flux2-vae.safetensors`.

The B4C runner **does not download missing files**. If any are absent, it stops and reports the exact missing paths.

## Current exact action

Run B4C once and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4c_flux2_visual_adapter\g3s_b4c_flux2_contact_sheet.png`

Do not promote hair and do not start B5/G3S-C before B4 passes.
