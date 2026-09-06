# Next-chat handoff — G3S structured character build

Status date: **2026-09-06**

Purpose: exact continuation state. GitHub living documents are canonical.

## Mandatory source of truth

Before acting, read:

1. `docs/PROJECT_STATE.md`
2. `docs/VISUAL_DIRECTION.md`
3. `docs/CHARACTERS.md`
4. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
5. `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`
6. `docs/PIXEL_ART_PRODUCTION.md`
7. `docs/ANIMATION_PIPELINE.md`
8. `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`
9. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
10. `docs/G3S_B3_NUDE_BODY_BASE_LOG.md`
11. `docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`
12. `docs/G3S_B4_HAIR_LOG.md`

Do not reconstruct state from chat memory if documents disagree.

## Living-document invariant — MANDATORY

Every state-changing project action must update thematic docs, `PROJECT_STATE`, this handoff when continuation changes, and commit before reporting completion.

## Locked architecture

Hidden 3D may own motion/topology/joints/sockets/depth/physics/guides, but persistent 2D pixel assets own final visible RGB/alpha/silhouette.

## Build order

1. complete adult hairless body base — **PASS/CLOSED**;
2. separate hair — **CURRENT**;
3. separate clothing/bindings/restraints/accessories — BLOCKED UNTIL HAIR PASS;
4. layered sprite animation driven by hidden-rig guides — BLOCKED UNTIL LAYERS READY.

## Canonical production body base

B3B V4 is **PASS/CLOSED / PRODUCTION BODY BASE PROMOTED**.

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`
- promotion commit `2deb765c3980d586ef9747340bb48852dedca452`;
- `37×128` RGBA;
- visible standing height `128 px`;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`.

The body must remain byte/pixel unchanged through B4/B5 composition.

## G3S-B4 — HAIR CURRENT

Canonical direction: black/nearly black, very long, heavy, voluminous, messy, wild and materially lived-in.

Mandatory composition:

`rear_hair -> body -> front_hair`

- `rear_hair` owns the dominant mass behind head/shoulders/back;
- `front_hair` is a smaller framing/crossing layer;
- one flat hair overlay is invalid.

## B4A preflight — PASS/CLOSED DIAGNOSTIC

Reviewed SHA256: `efd8866a38be1ad54aa60f4f05249813b5abf1754ee0a318fcf92a45ff262d4f`.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b4a_preflight_approval.json`

## B4B V1 — FAIL/CLOSED PRE-RUN METHOD

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v1_extraction_route_failure.json`

Reason: the master lacks sufficient hidden rear-hair information; valid rear geometry cannot be extracted from visible master pixels.

## B4B V2 — FAIL/CLOSED VISUAL / STRUCTURAL PASS

Reviewed contact sheet:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair\g3s_b4b_contact_sheet.png`

SHA256:

`73a9b53d35c158d78079039b4425c94028c8836e82b775ee0ce3e38b8d32a09d`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v2_visual_failure.json`

V2 proved the depth architecture but failed visually: centered curtain/bell silhouette, excessive front coverage, cape-like rear mass, repetitive equal-width lock/dread rhythm, buried face/head and insufficient asymmetry/hierarchy.

No model weights or paid API were used; no cleanup applies.

## B4B V3 — CURRENT / RUNNER READY

Spec:

`tools/structured-2d-character-pipeline/g3s_b4b_v3_authored_two_layer_hair_spec.json`

Helper:

`tools/structured-2d-character-pipeline/g3s_b4b_two_layer_hair_candidate.py`

Runner:

`tools/structured-2d-character-pipeline/17_run_g3s_b4b_two_layer_hair_candidate.ps1`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair`

V3 rules:

- master is identity/mass inspiration only;
- no master hair pixels are extracted, traced or copied;
- rear hair is dominant, asymmetric and irregular;
- front hair is sparse and lateral;
- center face/clavicle/chest/abdomen remain substantially readable;
- equal-width curtain/dread rhythm is removed;
- body remains exact/hash-verified B3B V4;
- no paid external API/model;
- no automatic promotion.

## Exact next operator action

Run exactly:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\17_run_g3s_b4b_two_layer_hair_candidate.ps1"
```

Then STOP and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair\g3s_b4b_contact_sheet.png`

Do not promote hair and do not start B5/G3S-C before V3 review.

## Actual local AI state

- only retained general local AI runtime: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable` (historical folder name; Qwen weights removed);
- deterministic workspace: `Z:\AI\RogueliteCharacterPipeline`;
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`;
- PixelLab is historical external paid spike code only and is not active/authorized;
- do not assume Wan-Animate-2 installed;
- Qwen-native, SD1.5, PixelLock and Alucard remain closed.

## Operator/process rules

- read canonical docs before every project action;
- update docs before reporting state changes;
- no routine Blender/Aseprite/rigging work for the user;
- no manual frame-by-frame repainting burden;
- no new body-reference requests;
- no B5/G3S-C before B4 PASS;
- include exact cleanup commands when a model route is closed and no longer needed;
- verify local runtime state before naming installed tools.
