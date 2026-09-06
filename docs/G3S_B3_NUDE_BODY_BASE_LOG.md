# G3S-B3 — Nude Body Base

Status date: **2026-09-06**

Gate status: **PASS/CLOSED — B3A STRUCTURAL GUIDE COMPLETE / B3B PRODUCTION BODY BASE PROMOTED**

## Why this gate exists

G3S-B2 proved that a complete persistent body cannot be recovered by subtracting hair/clothing from the composite master. The body must be authored independently and remain complete beneath every removable layer.

Measured B2 facts:

- source opaque pixels: `2974`;
- visible body pixels: `1538`;
- hair pixels: `826`;
- clothing pixels: `610`;
- hidden/unknown body pixels: `1205`.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b2_approval.json`

## Locked production order

1. complete adult body base, hairless and independent of clothing/equipment;
2. separate persistent hair asset/layer family;
3. separate clothing/bindings/cuffs/shackles/chains/accessories;
4. layered motion proof.

## Body ownership — LOCKED

The complete body base owns skin, final body silhouette, anatomical continuity and permanent body-side identity. It contains no hair, garment, binding, restraint or chain pixels. Nudity is a normal supported runtime state produced by omitting garment/equipment layers.

No censor layer is structurally required. Mature presentation may be neutral, sensual, erotic, heroic, vulnerable or brutal according to scene intent.

## Visible-ownership invariant — LOCKED

Hidden 3D may supply motion, topology, left/right identity, joints, sockets, depth/occlusion, physics and structural/anatomical reference. It may not own final visible RGB, alpha or final sprite silhouette.

## B3A history

- B3A V1 — FAIL/CLOSED REVISION: wrong MPFB gender polarity.
- B3A V2 — PASS/CLOSED: validated adult-female structural anatomy, complete geometry, zero forbidden layer objects and locked ~`128 px` visible gameplay scale.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3a_approval.json`

B3A remains structural reference only.

## B3B history

- V1 — FAIL/CLOSED: projected 3D mask owned final silhouette.
- V2 — FAIL/CLOSED: procedural/mannequin visual quality.
- V3 — FAIL/CLOSED: high-resolution render mechanically reduced/quantized.
- V4 — PASS: locked user-supplied pixel-art view normalized with nearest-neighbor only, then promoted unchanged.

Detailed history:

`docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`

## Approved references

Supporting high-resolution nude anatomy reference:

`assets/source/characters/exilada/reference/exilada_body_turnaround_nude_approved.jpg`

SHA256 `1e4b272c39f21cee0087e2aa6a5518fcc7a10c5ef47525ffcaff512ea07e8bbf`.

Final locked pixel-art visual reference marker:

`tools/structured-2d-character-pipeline/g3s_b3b_locked_visual_reference.json`

SHA256 `f2ba82dbcd759c55cbc1c70cf1100bd85a0319cf5fe53258e461406ba55cd08a`.

Do not reopen body-reference generation.

## 128 px clarification — LOCKED

`128 px` is the target visible standing body height at native `640×360` gameplay scale with the locked orthographic `26°` camera. It is not a universal frame/canvas limit.

## Canonical production body base — PASS

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
- adult nude hairless barefoot body base;
- front-three-quarter elevated belt-scroller view;
- persistent 2D visible ownership.

## Decision

**G3S-B3 = PASS/CLOSED.**

The project now has a complete persistent nude/hairless production body base at the locked gameplay scale.

## Next gate

**G3S-B4 — HAIR is OPEN/CURRENT.**

The hair must be authored as a separate persistent 2D layer family and must not modify or bake into the canonical body base.

B5 and G3S-C remain blocked until their prerequisite gates pass.
