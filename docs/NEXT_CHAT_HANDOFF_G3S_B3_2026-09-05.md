# Next-chat handoff — G3S-B3 Body Base

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

Do not reconstruct state from chat memory if documents disagree.

## Locked architecture

Hidden 3D may own motion/topology/joints/sockets/depth/physics/reference guides, but persistent 2D pixel assets own final visible RGB, alpha and silhouette. Runtime/export remains sprite-based.

Build order:

1. complete adult hairless body base;
2. separate hair;
3. separate clothing/bindings;
4. separate cuffs/shackles/chains/accessories;
5. layered sprite animation driven by hidden-rig guides.

Nudity is a normal supported state. The project does not impose blanket desexualization.

## Gate history

- B3A V1 — FAIL/CLOSED REVISION: wrong MPFB gender polarity.
- B3A V2 — PASS/CLOSED: adult-female structural guide at locked ~`128 px` visible standing scale.
- B3B V1 — FAIL/CLOSED ROUTE: copied B3A projected mask into final silhouette.
- B3B V2 — FAIL/CLOSED VISUAL ROUTE: procedural/mannequin body and poor pixel-art quality.
- covered Grok body turnaround — PASS historical reference / SUPERSEDED.
- **fully nude Grok four-view turnaround — PASS / APPROVED PRIMARY BODY REFERENCE / NOT PRODUCTION ART.**
- **B3B V3 nude-reference native-grid review spike — CURRENT / READY TO RERUN.**

## Approved nude body reference

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3b_body_reference_approval.json`

Canonical expected local path:

`assets/source/characters/exilada/reference/exilada_body_turnaround_nude_approved.jpg`

Source identity:

- SHA256 `1e4b272c39f21cee0087e2aa6a5518fcc7a10c5ef47525ffcaff512ea07e8bbf`;
- `2048×1401`;
- four views: front/back/profile/front-three-quarter;
- adult woman, ~162 cm identity;
- natural adult feminine proportions, lean/functional/resilient;
- olive/brown skin, bald/hairless for body-reference purposes, barefoot;
- mature, severe, sensual, dangerous and lived-in;
- aligned with Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell;
- fully nude with pelvic anatomy visible and no occluding garment.

The old covered reference SHA `2773c199b3ff28ad5a72e33feb97201a9567a633f8466620084362fd9aae7474` is superseded as the primary anatomy source.

No synthetic pelvic reconstruction is required or permitted in V3.

## 128 px clarification

`128 px` is the **visible standing body height** in the locked `640×360` gameplay view with orthographic `26°` camera. It is not a universal `128×128` frame limit. Animation frames may have larger transparent bounds while preserving the same body scale.

## Current exact gate

Run/review the **B3B V3 nude-reference native-grid visual spike**.

Runner:

`tools/structured-2d-character-pipeline/13_run_g3s_b3b_v3_reference_guided_translation.ps1`

Helper:

`tools/structured-2d-character-pipeline/g3s_b3b_v3_reference_guided_translation.py`

Rules:

- V3 uses the approved nude 2D reference only;
- no hidden-3D RGB/mask/silhouette visible ownership;
- no synthetic pelvis repair;
- no simple high-res resize/quantize accepted as production art;
- V3 output is review-only and cannot be promoted automatically;
- no hair/clothing/restraints in the body owner;
- review at intended native-scale reading before any production promotion.

## Exact next operator action

One-time prerequisite: place the exact approved nude turnaround at:

`D:\GOOGLE DRIVE\DEV\Roguelite\assets\source\characters\exilada\reference\exilada_body_turnaround_nude_approved.jpg`

Expected SHA256:

`1e4b272c39f21cee0087e2aa6a5518fcc7a10c5ef47525ffcaff512ea07e8bbf`

Then run:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\13_run_g3s_b3b_v3_reference_guided_translation.ps1"
```

Then STOP and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_v3_reference_guided\g3s_b3b_v3_contact_sheet.png`

or the complete console error.

## Operator/process rules

- read canonical docs before every material action;
- no routine Blender/Aseprite/rigging work for the user;
- no manual frame-by-frame repainting burden;
- no new sprite-model search;
- no B4/B5/G3S-C before B3B PASS;
- if a model/route is declared FAIL/CLOSED/REJECTED and no longer active, include exact cleanup commands in the same response;
- update relevant living docs + `docs/PROJECT_STATE.md` after each material step.
