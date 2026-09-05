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
10. `docs/G3S_B2_LAYER_STACK_PREFLIGHT_LOG.md`
11. `docs/G3S_B3_NUDE_BODY_BASE_LOG.md`
12. `docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`

Do not reconstruct state from chat memory if documents disagree.

## Locked architecture

G3V rejected hidden 3D as visible-image owner. Hidden 3D may own motion/topology/joints/sockets/depth/physics/reference guides, but persistent 2D pixel assets own final visible RGB, alpha and silhouette. Runtime/export remains sprite-based.

Build order remains:

1. complete adult hairless 2D body base;
2. separate hair;
3. separate clothing/bindings;
4. separate cuffs/shackles/chains/accessories;
5. layered sprite animation driven by hidden rig guides.

Nudity is a normal supported state. The project does not impose blanket desexualization; mature adult-body framing may be neutral, sensual, erotic, heroic, vulnerable or brutal according to scene/state.

## Gate history

- G3S-B3A V1 — FAIL/CLOSED REVISION: wrong MPFB gender polarity.
- G3S-B3A V2 — PASS/CLOSED: corrected adult-female structural guide at locked `128 px` scale.
- G3S-B3B V1 — FAIL/CLOSED ROUTE: copied B3A projected mask into final sprite alpha/silhouette and procedurally colored it. This violated visible ownership.
- **G3S-B3B V2 — CURRENT / READY FOR USER VISUAL REVIEW.**

## B3B V2 — current exact state

The actual visible source is now a committed native `128×128` 2D pixel asset:

`assets/source/characters/exilada/body/g3s_b3b_body_base_source_v2.png`

SHA256:

`0fc90ca6a86e3adceba4d8fe100eb0d8e8e06337d6820585c6e535515fdfab53`

Metadata:

`tools/structured-2d-character-pipeline/g3s_b3b_body_base_source_v2.json`

Validator:

`tools/structured-2d-character-pipeline/g3s_b3b_validate_authored_body_v2.py`

Runner:

`tools/structured-2d-character-pipeline/12_run_g3s_b3b_authored_body_v2.ps1`

The validator does not load or sample B3A RGB, mask or projected silhouette. B3A is only an already-passed structural prerequisite/reference.

Technical facts:

- native `128×128`;
- visible height `128 px`;
- bbox `[17, 0, 120, 127]`;
- 8 opaque palette colors;
- binary alpha;
- final RGB/alpha/silhouette owned by committed 2D source;
- zero hair/clothing/binding/restraint/chain ownership.

This is not a visual PASS yet. User review must judge adult anatomy, Exilada-compatible proportions, chest/pelvis/hands/feet, native 1× readability and intentional pixel-art language. If it fails, revise the committed 2D asset directly; do not return to 3D-mask authoring or reopen model search.

## Exact next operator action

Verify the runner still exists in GitHub, then give only:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\12_run_g3s_b3b_authored_body_v2.ps1"
```

Then STOP and request only:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_authored_body_v2\g3s_b3b_contact_sheet_v2.png`

or the complete console error.

Do not start B4 hair, B5 clothing/accessories or G3S-C animation before B3B visual PASS.

## Operator/process rules

- read canonical docs before every material action;
- normal loop: `git pull -> one documented PowerShell command -> inspect/share output`;
- no routine Blender/Aseprite/rigging work for the user;
- no manual frame-by-frame repainting burden;
- no unrequested image generation;
- no new sprite-model search;
- if a model/route is declared FAIL/CLOSED/REJECTED and no longer active, include exact cleanup commands in the same response;
- update relevant living docs + `docs/PROJECT_STATE.md` after each material step.
