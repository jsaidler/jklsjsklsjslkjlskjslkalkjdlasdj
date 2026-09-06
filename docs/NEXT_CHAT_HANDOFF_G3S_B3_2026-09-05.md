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

## G3S-B4 — HAIR CURRENT

Canonical hair: black/nearly black, very long, heavy, voluminous, messy, wild, lived-in.

Mandatory composition:

`rear_hair -> body -> front_hair`

## B4 history

- B4A preflight — **PASS/CLOSED DIAGNOSTIC**.
- B4B V1 master extraction — **FAIL/CLOSED PRE-RUN**: master lacks hidden rear-hair information.
- B4B V2 authored two-layer — **FAIL/CLOSED VISUAL / STRUCTURAL PASS**: centered curtain/cape, too much front coverage.
- B4B V3 authored two-layer — **FAIL/CLOSED VISUAL AND ALIGNMENT METHOD**.

### V3 root cause — IMPORTANT

Reviewed SHA256:

`9d922756f8815ea55cf55bed26d2bc0d24f51f93f89b3f47392126e027573f33`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v3_pose_mismatch_failure.json`

V3 authored hair in fixed master-like canvas coordinates. The master and production B3B body are in different poses, so crown, rear mass and front locks could not align correctly even though two-layer ownership was structurally valid.

Do **not** return to fixed master-pose hair geometry.

## B4B V4 — CURRENT / RUNNER READY

Spec:

`tools/structured-2d-character-pipeline/g3s_b4b_v4_pose_anchored_hair_spec.json`

Helper:

`tools/structured-2d-character-pipeline/g3s_b4b_pose_anchored_hair_candidate.py`

Runner:

`tools/structured-2d-character-pipeline/17_run_g3s_b4b_two_layer_hair_candidate.ps1`

V4 measures pose anchors directly from the actual canonical B3B body alpha/silhouette:

- head center/bounds;
- shoulder row/span;
- torso center;
- facing bias.

Both new hair layers are authored relative to those production-pose anchors. The master is identity/style/material inspiration only and its pose coordinates do not drive placement.

The V4 contact sheet explicitly includes the body-alone view with detected anchors, then rear layer, front layer, composite and native `640×360` preview.

No paid API/model. No automatic promotion.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\17_run_g3s_b4b_two_layer_hair_candidate.ps1"
```

Then share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair\g3s_b4b_contact_sheet.png`

Do not promote hair and do not start B5/G3S-C before V4 visual review.

## Actual local AI state

- retained general local runtime: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable`;
- deterministic workspace: `Z:\AI\RogueliteCharacterPipeline`;
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`;
- PixelLab is historical paid spike only, not active/authorized;
- Qwen-native, SD1.5, PixelLock and Alucard remain closed.
