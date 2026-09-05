# G3S-B2 — Layer Stack Preflight

Status date: **2026-09-05**

Gate status: **READY TO RUN**

## Why this gate exists

G3S-B V1 passed its technical recomposition audit but failed architectural visual review.

The V1 result proved that the provisional 128×128 source could be partitioned and recomposed pixel-exactly, but the masks were not valid production ownership boundaries:

- body parts still contained clothing/bandage pixels;
- hair masks contained non-hair pixels;
- the body did not exist completely underneath clothing;
- the body did not exist completely underneath hair;
- this violated the already-canonical layer stack in `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`.

Canonical failure marker:

`tools/structured-2d-character-pipeline/g3s_b_v1_failure.json`

## Canonical correction — LOCKED

The structured-2D character must use the same ownership model already defined for the systemic damage/equipment architecture:

1. **Body base** — complete persistent unclothed anatomy, independent of all removable layers.
2. **Hair** — separate persistent secondary-motion layer family.
3. **Clothing** — separate removable/damageable overlay layer family.
4. **Restraints/chains** — separate accessories attached to sockets.
5. **Surface states** — later overlays on the correct owner layer.

The initial character may visually begin with cloth/bindings/accessories equipped, but those pixels must not be authored into the permanent body base.

## What G3S-B2 does

G3S-B2 is a **preflight**, not final body authoring.

It rebuilds the same pinned provisional source and separates the currently visible composite into diagnostic ownership families:

- `body_visible_incomplete`;
- `hair`;
- `clothing`.

It then recomposes those three layers and requires an exact pixel match to the provisional source.

Most importantly, it overlays a magenta diagnostic on body regions that are currently hidden by hair/clothing and therefore still need real body-base pixels.

G3S-B2 deliberately does **not** invent those hidden pixels. A fake skin-color fill would only create another technical mannequin problem.

## Input

Pinned design/scaffold control:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control\g3s_a_control_official_raw.png`

SHA256:

`ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e`

## Tooling

Specification:

`tools/structured-2d-character-pipeline/g3s_b2_layer_stack_spec_v1.json`

Helper:

`tools/structured-2d-character-pipeline/g3s_b2_layer_stack_preflight.py`

Runner:

`tools/structured-2d-character-pipeline/10_run_g3s_b2_layer_stack_preflight.ps1`

Output workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_b2_layer_stack`

Expected artifacts:

- `g3s_b2_source128.png`
- `g3s_b2_body_visible_incomplete.png`
- `g3s_b2_hair_layer.png`
- `g3s_b2_clothing_layer.png`
- `g3s_b2_recomposed.png`
- `g3s_b2_unresolved_underbody.png`
- `g3s_b2_contact_sheet.png`
- `g3s_b2_layer_manifest.json`
- `g3s_b2_result.json`

## Review order

1. body-visible layer contains no obvious hair masses;
2. body-visible layer contains no obvious garment masses;
3. hair layer contains hair, not torso/limb chunks;
4. clothing layer contains the initial cloth/bindings as overlays;
5. exact recomposition matches the source;
6. magenta unresolved-body map correctly exposes where hidden body pixels are still missing;
7. no attempt is made to start animation with an incomplete body base.

## PASS meaning

PASS does **not** mean the body base is finished.

PASS means the ownership architecture is now correct and the missing-underlayer problem is explicitly bounded. The next gate is:

**G3S-B3 — Body Base Completion**

That gate must produce a complete persistent body base under clothing/hair before G3S-C animation starts.

## Kill switch

If diagnostic material separation is too contaminated to support ownership decisions, revise only the segmentation/specification. Do not return to another generative sprite model and do not start animation.

## Exact next action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\10_run_g3s_b2_layer_stack_preflight.ps1"
```

Then STOP and review:

`Z:\AI\RogueliteCharacterPipeline\g3s_b2_layer_stack\g3s_b2_contact_sheet.png`

Do not run G3S-C.
