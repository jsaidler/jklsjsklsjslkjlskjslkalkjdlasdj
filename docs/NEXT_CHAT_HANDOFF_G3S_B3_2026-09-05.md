# Next-chat handoff — G3S structured character build

Status date: **2026-09-06**

Purpose: exact continuation state. GitHub living documents are canonical.

## Mandatory source of truth

Read `docs/PROJECT_STATE.md` first, then `docs/G3S_B4_HAIR_LOG.md` and the other G3S/visual pipeline docs. Do not reconstruct state from chat memory if documents disagree.

## Living-document invariant — MANDATORY

Every state-changing project action updates thematic docs, `PROJECT_STATE`, this handoff when continuity changes, and commits before reporting completion.

## Canonical production body base

B3B V4 is **PASS/CLOSED / PROMOTED**:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`
- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`.

Body remains byte/pixel unchanged through B4/B5.

## G3S-B4 — HAIR CURRENT / OPEN

Canonical hair: black/nearly black, very long, heavy, voluminous, messy, wild, lived-in.

Mandatory composition:

`rear_hair -> body -> front_hair`

## B4 history

- B4A preflight — **PASS/CLOSED DIAGNOSTIC**.
- B4B V1 master extraction — **FAIL/CLOSED PRE-RUN**: master lacks hidden rear-hair information.
- B4B V2 authored two-layer — **FAIL/CLOSED VISUAL / STRUCTURAL PASS**: centered curtain/cape, too much front coverage.
- B4B V3 authored two-layer — **FAIL/CLOSED VISUAL AND ALIGNMENT METHOD**: fixed master-like coordinates ignored the actual production pose.
- B4B V4 pose-anchored authored two-layer — **FAIL/CLOSED VISUAL AND METHOD**.

## B4B V4 failure — IMPORTANT

Reviewed contact sheet SHA256:

`50dd663cbbeb0bb1a9865f2ac95daedc7990ceaf7a98ae6a968c8b7eacb4a8a5`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v4_pose_anchor_failure.json`

The V4 contact sheet itself proves the anchor detector is not reliable: it reports `shoulder_span=6.36 px` for the canonical `37 px`-wide body. More fundamentally, a few scalar anchors cannot encode the 3/4 anatomy needed for hair placement: head tilt, shoulder slope, torso rotation, arm occlusion, back contour and local depth are missing.

### Closed route — DO NOT REOPEN

The **Pillow polygon/line + heuristic body-anchor hair-authoring route is closed**.

Do not create a V5 by adding more manually tuned anchors, polygons, curves or procedural locks. Also do not return to master-pixel extraction or fixed master-pose coordinates.

The valid structural contract remains:

`rear_hair -> immutable body -> front_hair`

The master remains identity/style/material reference only.

Runner `tools/structured-2d-character-pipeline/17_run_g3s_b4b_two_layer_hair_candidate.ps1` is intentionally disabled.

No model/API was used by V4; no cleanup applies.

## Exact continuation state

**B4 remains OPEN. There is currently NO approved B4 runner.**

The next method must use real visual 2D authoring/adaptation to the actual canonical B3B body pose and output separate persistent `rear_hair` and `front_hair` assets.

Do not start B5 or G3S-C before B4 passes.

## Actual local AI state

- retained general local runtime: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable`;
- deterministic workspace: `Z:\AI\RogueliteCharacterPipeline`;
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`;
- PixelLab is historical paid spike only, not active/authorized;
- Qwen-native, SD1.5, PixelLock and Alucard remain closed.
