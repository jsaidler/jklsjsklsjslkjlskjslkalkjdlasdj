# Roguelite — Current Project State

Status date: **2026-09-06**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/GAME_VISION.md`
3. `docs/VISUAL_DIRECTION.md`
4. `docs/CHARACTERS.md`
5. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
6. `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`
7. `docs/PIXEL_ART_PRODUCTION.md`
8. `docs/ANIMATION_PIPELINE.md`
9. `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`
10. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
11. `docs/G3S_B2_LAYER_STACK_PREFLIGHT_LOG.md`
12. `docs/G3S_B3_NUDE_BODY_BASE_LOG.md`
13. `docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`
14. `docs/G3S_B4_HAIR_LOG.md`
15. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every project action that changes state must update the living documents before that action is reported complete.

Required sequence: perform/inspect -> update thematic docs -> update `PROJECT_STATE` -> update active handoff when applicable -> commit -> only then report completion/next action.

## Game identity — LOCKED

Systemic sword-and-sorcery action RPG with roguelite expedition structure, persistent fortress growth, protagonist meta-progression and a causal living world.

Presentation baseline: **elevated 2D belt-scroller / false 3D**.

Final visible language: **true modern pixel art at native gameplay raster**.

## Exilada identity — LOCKED

Canonical design master:

`assets/source/characters/exilada/reference/exilada_master.png`

Adult woman, approximately 162 cm, lean/functional/resilient anatomy, natural adult feminine proportions, olive-brown skin, severe mature face, very long heavy messy black hair, captivity history, bare feet, weaponless base.

Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell remain explicit visual references. Mature sensuality, erotic charge and adult nudity are legitimate parts of the visual language and are not automatically sanitized.

## Body-first rule — LOCKED

The production character owns a complete adult body base independent of hair, clothing and restraints.

## Hard operator constraint

The user does not perform routine Blender/Aseprite/rigging work and does not repaint frames manually. Normal production remains scriptable/headless.

Normal operator loop once a runner is approved:

`git pull -> one documented PowerShell command -> inspect/share output`

## Visible-ownership invariant — CRITICAL

Hidden 3D may own motion/topology/joints/sockets/depth/physics/guides but not final visible RGB/alpha/silhouette. Final visible art is owned by persistent native 2D pixel assets.

High-resolution render/reference art may not be mechanically pixelated into production art.

## Locked gameplay baseline

- native scene: `640×360`;
- orthographic camera;
- pitch: `26°`;
- protagonist visible standing height: approximately `128 px`.

## Gate order — CURRENT

- G0 automation — PASS/CLOSED
- G1 camera/native scale — PASS/CLOSED
- G2 real motion/topology — PASS/CLOSED
- G3 first native translation — TECHNICAL PASS / LOOK NOT APPROVED
- G3R primitive renderer refinement — FAIL/CLOSED
- G3V representative continuous human visual proxy — FAIL/CLOSED
  - G3V-R retarget preflight — PASS/CLOSED using `DIRECTION_SPACE_FK`
- **G3S structured 2D visible representation** ← ACTIVE
  - G3S-A source-model search — CLOSED
  - G3S-A1 facial/anatomy lock attempts — FAIL/CLOSED
  - G3S-B persistent part decomposition V1 — FAIL/CLOSED
  - G3S-B2 layer-stack preflight — PASS/CLOSED DIAGNOSTIC
  - G3S-B3 complete body base — **PASS/CLOSED**
    - B3A V1 — FAIL/CLOSED REVISION
    - B3A V2 — PASS/CLOSED structural adult-female guide
    - B3B V1 — FAIL/CLOSED ROUTE
    - B3B V2 — FAIL/CLOSED VISUAL ROUTE
    - B3B V3 — FAIL/CLOSED VISUAL AND METHOD ROUTE
    - B3B V4 — **PASS/CLOSED / PRODUCTION BODY BASE PROMOTED**
  - **G3S-B4 hair** ← CURRENT
    - B4A preflight — **PASS/CLOSED DIAGNOSTIC**
    - B4B V1 master-extraction route — **FAIL/CLOSED PRE-RUN METHOD**
    - **B4B V2 authored two-layer static candidate** ← RUNNER READY / REVIEW NEXT
  - G3S-B5 clothing/restraints/accessories — BLOCKED UNTIL B4 PASS
  - G3S-C layered walk proof — BLOCKED UNTIL B3/B4/B5

## Canonical production body base — LOCKED

Promotion commit:

`2deb765c3980d586ef9747340bb48852dedca452`

Canonical files:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`

Recorded facts:

- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- dimensions `37×128`;
- visible standing height `128 px`;
- front-three-quarter elevated belt-scroller view;
- adult nude hairless barefoot body base;
- persistent 2D visible ownership;
- excludes hair, clothing, restraints, accessories and weapons.

## G3S-B4 hair — CURRENT

Canonical hair identity:

- black / nearly black;
- very long;
- heavy;
- voluminous;
- messy;
- primary silhouette anchor;
- deprivation/survival material language rather than styled glamour.

Hair is a separate persistent 2D layer family and must leave the B3 body asset unchanged underneath.

### Mandatory hair depth split — LOCKED

Minimum valid B4 representation:

1. `rear_hair` — behind body/head/shoulders/back;
2. `front_hair` — in front where hair crosses face/neck/chest/shoulders.

Minimum deterministic composition:

`rear_hair -> body -> front_hair`

Additional side/intermediate masses may be introduced only if later occlusion/secondary motion proves they are needed.

### B4A preflight — PASS/CLOSED DIAGNOSTIC

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4_hair_preflight\g3s_b4_hair_preflight_contact_sheet.png`

SHA256:

`efd8866a38be1ad54aa60f4f05249813b5abf1754ee0a318fcf92a45ff262d4f`

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b4a_preflight_approval.json`

The master is suitable as hair identity/mass inspiration, the body remains immutable, and `96×160` is adequate for the first static review.

### B4B V1 extraction route — FAIL/CLOSED PRE-RUN

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v1_extraction_route_failure.json`

Reason: the master does not show enough of the hair that falls behind the head, shoulders and back. Therefore valid `rear_hair` geometry cannot be extracted by splitting only visible master pixels.

The V1 runner was not executed by the user, produced no production art, downloaded no model and requires no cleanup.

### B4B V2 authored two-layer candidate — RUNNER READY

Spec:

`tools/structured-2d-character-pipeline/g3s_b4b_v2_authored_two_layer_hair_spec.json`

Helper:

`tools/structured-2d-character-pipeline/g3s_b4b_two_layer_hair_candidate.py`

Runner:

`tools/structured-2d-character-pipeline/17_run_g3s_b4b_two_layer_hair_candidate.ps1`

Output contact sheet:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair\g3s_b4b_contact_sheet.png`

V2 authors **new native-pixel geometry** for both layers. The canonical master is inspiration/reference only; its pixels are not copied, extracted, traced or split into final hair layers. `rear_hair` explicitly includes new back-hair coverage absent from the master. The runner uses no external paid API/model and performs no automatic promotion.

## Current exact action

Run exactly:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\17_run_g3s_b4b_two_layer_hair_candidate.ps1"
```

Then STOP and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair\g3s_b4b_contact_sheet.png`

Do not promote hair and do not start B5/G3S-C before B4B V2 review.

## Actual local AI disk/runtime state — LOCKED 2026-09-06

- only retained general local AI runtime: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable` (historical folder name; Qwen weights removed);
- deterministic workspace: `Z:\AI\RogueliteCharacterPipeline`;
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`;
- repository-only old spike code does not imply local model installation;
- PixelLab is historical external paid spike code only and is **not an active/authorized route**;
- Wan-Animate-2 must not be assumed installed without fresh verification;
- Qwen-native, SD1.5, PixelLock and Alucard remain closed;
- Blender/MPFB may remain only as hidden structural infrastructure.
