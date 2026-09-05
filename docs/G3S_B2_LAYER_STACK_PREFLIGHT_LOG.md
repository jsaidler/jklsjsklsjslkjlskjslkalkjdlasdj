# G3S-B2 — Layer Stack Preflight

Status date: **2026-09-05**

Gate status: **PASS / CLOSED — DIAGNOSTIC ONLY**

## Why this gate existed

G3S-B V1 passed pixel-exact recomposition but failed architectural review because body, hair and clothing ownership were mixed.

B2 was created only to expose the ownership problem without inventing hidden body pixels.

## Result

The diagnostic succeeded technically and visually for its intended purpose.

Measured result:

- exact recomposition: **PASS**;
- source opaque pixels: `2974`;
- visible body pixels: `1538`;
- hair pixels: `826`;
- clothing pixels: `610`;
- hidden/unknown body pixels under hair/clothing: **`1205`**.

These values are preserved in the user-generated B2 result/manifest and in:

`tools/structured-2d-character-pipeline/g3s_b2_approval.json`

## Critical conclusion — LOCKED

The composite source **cannot** be turned into a complete body by subtracting hair and clothing.

The magenta unresolved map correctly shows that large portions of anatomy simply do not exist in the composite pixels. Those regions must be authored as a dedicated body asset.

Therefore B2 does **not** feed its extracted `body_visible_incomplete`, `hair` or `clothing` images directly into production.

They are evidence/diagnostics only.

## Correct production staging — LOCKED

1. **G3S-B3 — complete nude body base, hairless and without clothing/restraints.**
2. **G3S-B4 — hair as a separate persistent asset/layer family.**
3. **G3S-B5 — clothing, bindings, cuffs/shackles and chains as independent overlays/accessories.**
4. **G3S-C — layered four-phase walk proof.**

This order replaces the earlier idea of carving production layers out of the composite master.

## Nudity implication

Because the body base is complete and independent, nudity is a normal state of the runtime character rather than a special sprite variant.

`nude = body base (+ optional hair/body-state overlays) with garment/equipment layers omitted`

No hidden anatomy is reconstructed at runtime.

## What remains useful from B2

B2 remains valuable because it proved:

- the current composite contains insufficient underbody data;
- clothing/hair subtraction is not a production solution;
- body-first authoring is mandatory;
- animation must remain blocked until the body base exists.

## Next gate

**G3S-B3 — Nude Body Base**

Canonical plan:

`docs/G3S_B3_NUDE_BODY_BASE_LOG.md`

Do not run G3S-C.
