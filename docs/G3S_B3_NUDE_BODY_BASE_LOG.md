# G3S-B3 — Nude Body Base

Status date: **2026-09-05**

Gate status: **B3A V2 PASS/CLOSED — B3B V1/V2 CLOSED — BODY REFERENCE APPROVED — PIXEL TRANSLATION NEXT**

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

No hair, clothing or animation begins before B3B passes visually.

## Body ownership — LOCKED

The complete body base owns skin, final body silhouette, anatomical continuity and permanent body-side identity. It contains no hair, garment, binding, restraint or chain pixels. Nudity is a normal supported runtime state produced by omitting garment/equipment layers.

No censor layer is structurally required. Mature presentation may be neutral, sensual, erotic, heroic, vulnerable or brutal according to scene intent.

## Visible-ownership invariant — LOCKED

G3V demoted hidden 3D from visible-image ownership. Hidden 3D may supply motion, topology, left/right identity, joints, sockets, depth/occlusion, physics and structural/anatomical reference. It may not own final visible RGB, alpha or final sprite silhouette.

A B3A render/mask is reference only and may not be mechanically promoted into final sprite coverage.

## B3A V1 — FAIL/CLOSED REVISION

Wrong MPFB gender polarity. Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3a_v1_failure.json`

## B3A V2 — PASS/CLOSED

Validated adult-female structural anatomy, complete geometry, zero forbidden layer objects and locked `128 px` gameplay scale.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3a_approval.json`

B3A remains structural reference only.

## B3B V1 — FAIL/CLOSED ROUTE

Copied the B3A projected mask into final alpha/silhouette. This violated visible ownership.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v1_route_failure.json`

## B3B V2 — FAIL/CLOSED VISUAL ROUTE

Ownership was technically 2D, but the art failed: procedural/mannequin anatomy, distorted proportions, poor hands/feet, crude pelvis/thigh transitions, pseudo-3D banding and absent Exilada identity.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v2_visual_failure.json`

Rejected V2 art/tooling was removed from `main`; no model cleanup applies.

## Approved high-resolution body reference — PASS

The current primary body reference is the user-approved Grok four-view turnaround.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3b_body_reference_approval.json`

Source identity:

- SHA256 `2773c199b3ff28ad5a72e33feb97201a9567a633f8466620084362fd9aae7474`;
- `1168×784`;
- front / back / profile / front-three-quarter;
- adult woman, approximately 162 cm identity;
- natural feminine proportions, lean/functional/resilient;
- severe, sensual, dangerous and lived-in;
- aligned with Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell.

The minimal dark loincloth/tapa-sexo visible in the reference is only an occluder. It has no body-base ownership and must not become a mandatory coverage layer. Final pelvic pixels belong to B3B; any later garment belongs to B5.

## B3B visual PASS criteria

A production body must:

1. read as a complete adult female body at native 1×;
2. preserve natural adult proportions and Exilada-specific body language;
3. read as attractive, sensual, severe, dangerous and lived-in — beauty + hardness + survival;
4. have coherent chest, pelvis, thighs, hands and feet;
5. read as intentional modern pixel art, not filtered 3D or procedural mannequin construction;
6. own its own 2D RGB/alpha/silhouette;
7. contain no hair/clothing/restraint/chain ownership;
8. remain readable at the locked `640×360` / ~`128 px` gameplay scale.

Automatic FAIL: generic fitness/character-creator body, superhero exaggeration, short/squat distortion, sanitized mature body language, poor anatomy or absent sword-and-sorcery/Exilada identity.

## Current exact action

Create and visually review the first **pixel-art translation candidate** from the approved high-resolution body direction.

The high-resolution turnaround must **not** simply be resized/quantized and declared production art. The candidate is a visual gate. After it passes, establish the replacement B3B native production source and deterministic validation/export tooling.

No local B3B runner is currently approved. B4/B5/G3S-C remain blocked.
