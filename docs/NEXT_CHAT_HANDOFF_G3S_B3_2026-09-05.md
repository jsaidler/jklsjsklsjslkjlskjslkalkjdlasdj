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

Canonical hair direction:

- black / nearly black;
- very long;
- heavy;
- voluminous;
- messy;
- primary silhouette anchor;
- deprivation/survival rather than groomed fantasy styling.

### Mandatory depth split — LOCKED

Minimum representation:

`rear_hair -> body -> front_hair`

- `rear_hair`: behind head/neck/shoulders/back/body;
- `front_hair`: in front where hair crosses face/neck/chest/shoulders;
- one flat overlay is invalid;
- extra sublayers may be added later only if needed for occlusion/secondary motion.

## B4A preflight — PASS/CLOSED DIAGNOSTIC

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4_hair_preflight\g3s_b4_hair_preflight_contact_sheet.png`

SHA256 `efd8866a38be1ad54aa60f4f05249813b5abf1754ee0a318fcf92a45ff262d4f`.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b4a_preflight_approval.json`

The local master is suitable as hair identity/mass inspiration and the shared `96×160` frame is adequate for the first static review.

## B4B V1 master extraction — FAIL/CLOSED PRE-RUN

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v1_extraction_route_failure.json`

The master does not show enough of the rear hair over/behind the back. Therefore a correct `rear_hair` owner cannot be recovered by isolating visible master pixels and splitting by body overlap.

V1 was not run by the user. No production art/model was created or downloaded; no cleanup applies.

## B4B V2 authored two-layer static candidate — CURRENT / RUNNER READY

Spec:

`tools/structured-2d-character-pipeline/g3s_b4b_v2_authored_two_layer_hair_spec.json`

Helper:

`tools/structured-2d-character-pipeline/g3s_b4b_two_layer_hair_candidate.py`

Runner:

`tools/structured-2d-character-pipeline/17_run_g3s_b4b_two_layer_hair_candidate.ps1`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair`

V2 rules:

- master is inspiration/identity reference only;
- no master hair pixels are extracted, traced, copied or split into final layers;
- `rear_hair` and `front_hair` are newly authored at native pixel resolution;
- rear layer includes new coverage behind head/shoulders/back absent from the master;
- body is exact hash-verified immutable B3B V4;
- no paid external API or external model;
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

Do not promote hair and do not start B5/G3S-C before B4B V2 review.

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
