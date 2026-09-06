# Next-chat handoff — G3S-B3 Body Base

Status date: **2026-09-05**

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
- B3A V2 — PASS/CLOSED: adult-female structural guide at locked `128 px` scale.
- B3B V1 — FAIL/CLOSED ROUTE: copied B3A projected mask into final silhouette.
- B3B V2 — FAIL/CLOSED VISUAL ROUTE: procedural/mannequin body and poor pixel-art quality.
- high-resolution Grok body turnaround — **PASS / APPROVED BODY REFERENCE / NOT PRODUCTION ART**.
- **B3B pixel-art visual translation candidate — CURRENT NEXT ARTIFACT.**

## Approved body reference

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3b_body_reference_approval.json`

Source identity:

- SHA256 `2773c199b3ff28ad5a72e33feb97201a9567a633f8466620084362fd9aae7474`;
- `1168×784`;
- four views: front/back/profile/front-three-quarter;
- adult woman, ~162 cm identity;
- natural adult feminine proportions, lean/functional/resilient;
- olive/brown skin, bald/hairless for body-reference purposes, barefoot;
- mature, severe, sensual, dangerous and lived-in;
- aligned with Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell.

Do not reinterpret the body as short/squat/flattened because of prior use of the word “compact”.

The minimal dark loincloth/tapa-sexo in the reference is an **occluder only**. It has no body ownership and must not become a permanent censor layer. Final B3B pelvic pixels belong to the body owner; any later loincloth belongs to B5.

## Current exact gate

Create/review a **pixel-art visual translation candidate** from the approved body direction.

Rules:

- candidate must preserve adult natural proportions and sword-and-sorcery body language;
- no generic fitness/character-creator look;
- no procedural mannequin;
- no 3D-mask silhouette ownership;
- no simple high-res resize/quantize accepted as production art;
- no hair/clothing/restraints in the body owner;
- review at intended native-scale reading before production promotion.

The visual candidate is not automatically B3B production authority. After it passes, establish the accepted native 2D source and deterministic validation/export tooling.

## Operator/process rules

- read canonical docs before every material action;
- no routine Blender/Aseprite/rigging work for the user;
- no manual frame-by-frame repainting burden;
- no new sprite-model search;
- no B4/B5/G3S-C before B3B PASS;
- if a model/route is declared FAIL/CLOSED/REJECTED and no longer active, include exact cleanup commands in the same response;
- update relevant living docs + `docs/PROJECT_STATE.md` after each material step.
