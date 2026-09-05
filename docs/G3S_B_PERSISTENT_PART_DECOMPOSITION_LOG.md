# G3S-B — Persistent 2D Part Decomposition

Status date: **2026-09-05**

Gate status: **FAIL / CLOSED — superseded by G3S-B2 layer-stack preflight**

## Intent

G3S-B V1 attempted to decompose the provisional 128×128 Exilada scaffold into persistent parts with stable pivots, screen-side identity and chain sockets.

It followed G3S-A1 V2, whose mouth patch was visually rejected. The head/face was therefore deliberately treated as replaceable, while broken chains were moved out of the body and into accessory slots.

## Technical result

The V1 run completed and passed its technical audit:

- source alpha pixels: `2974`;
- covered by named parts: `2895`;
- residual pixels: `79`;
- residual fraction: `0.026564`;
- exact recomposition: `true`;
- max channel difference: `0`.

Result evidence:

- `g3s_b_contact_sheet.png`;
- `g3s_b_parts_atlas.png`;
- `g3s_b_runtime_manifest.json`;
- `g3s_b_result.json`.

## Visual / architecture verdict — FAIL

Visual review exposed a deeper ownership error that the exact-recomposition test could not detect.

The decomposition was **lossless but architecturally wrong**:

- several limb/body parts still contained clothing or bindings;
- the `hair_back` / front-hair masks included non-hair body/clothing pixels;
- clothing was not consistently an overlay over a complete body;
- the body did not exist independently underneath clothing;
- the body did not exist independently underneath hair.

This violates the canonical layer contract already defined in `docs/CHARACTER_LAYER_DAMAGE_SYSTEM.md`, where the complete body base exists under removable clothing and hair is a separate persistent secondary system.

Canonical failure marker:

`tools/structured-2d-character-pipeline/g3s_b_v1_failure.json`

## Locked correction

The production ownership model is now explicit:

1. `body_base` — complete persistent unclothed anatomy;
2. `hair` — separate persistent secondary-motion family;
3. `clothing` — separate removable/damageable overlay family;
4. `restraints/chains` — separate socketed accessories;
5. `surface_state` — later overlays attached to their actual owner.

The Exilada may begin gameplay wearing minimal cloth/bindings and possibly broken restraints, but those are **equipped initial layers**, not pixels baked into the permanent body base.

## Consequence for animation

G3S-C is blocked.

Before any four-phase animation proof, the pipeline must first prove correct ownership separation and then create the body pixels currently hidden under clothing/hair.

Next gates:

- **G3S-B2 — Layer Stack Preflight**: separate visible body/hair/clothing diagnostically and map missing underbody zones;
- **G3S-B3 — Body Base Completion**: produce a complete persistent body under all removable layers;
- only then return to G3S-C animation.

## Exact next action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\10_run_g3s_b2_layer_stack_preflight.ps1"
```

Then STOP and review:

`Z:\AI\RogueliteCharacterPipeline\g3s_b2_layer_stack\g3s_b2_contact_sheet.png`

No model was discarded by this gate, so there is no model-file cleanup command associated with this FAIL.
