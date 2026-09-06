# G3S — Structured 2D Visible Representation

Status date: **2026-09-06**

Gate status: **ACTIVE — B3 BODY BASE PASS/CLOSED / B4 HAIR CURRENT**

## Locked architecture

`real motion -> validated hidden rig -> projected joints/depth/sockets/guides -> persistent 2D pixel assets -> deterministic 2D transform/deformation -> depth-aware composition -> native sprite -> QA`

Hidden 3D owns motion/topology/sockets/contacts/depth/physics/semantic guides only. It does **not** own final visible character RGB, alpha or final sprite silhouette.

## Visible-ownership invariant — LOCKED

G3V is authoritative: direct visible 3D failed and was closed.

Therefore:

- 3D may guide anatomy, motion, topology, sockets, contacts, depth and occlusion;
- 3D may not be mechanically promoted into final visible sprite geometry;
- high-resolution 2D reference art may not be mechanically resized/quantized/traced and promoted as production sprite geometry;
- final character pixels are owned by persistent structured 2D assets;
- runtime/export uses sprites.

## Production constraints

- no per-frame diffusion as animation owner;
- no routine frame-by-frame repainting by the user;
- no required Blender/Aseprite/Spine GUI work by the user;
- no beauty-render shrink/pixel-filter route as final art;
- recurring work remains scriptable/headless;
- body, hair, clothing and accessories have separate ownership;
- a complete body exists under every removable layer.

## Model-discard cleanup rule — LOCKED

Whenever a model/route is declared FAIL/CLOSED/REJECTED and no longer required, include exact PowerShell cleanup commands for its model-specific files. Shared runtimes still in use are preserved.

Closed direct sprite-model routes remain Qwen-native, SD1.5, PixelLock and Alucard. Do not reopen model hunting without an explicit project decision.

## Correct staged character build — LOCKED

1. **B3 — complete body base**: adult female, hairless, complete under future layers, owned as native 2D sprite art. **PASS/CLOSED**.
2. **B4 — hair**: independent persistent 2D asset/layer family. **CURRENT**.
3. **B5 — clothing/restraints/accessories**: chest wrap, hip cloth, bindings, cuffs/shackles, chain segments and other equipment, each with independent ownership/state. **BLOCKED UNTIL B4 PASS**.
4. **G3S-C — layered motion proof**: hidden rig drives 2D deformation/ordering guides; exported/runtime result remains sprite-based. **BLOCKED UNTIL B3/B4/B5**.

## Nudity — LOCKED SYSTEMIC STATE

Nudity is a normal supported state, not a special variant. Runtime composition is:

`complete body base + optional hair + body-state overlays + zero or more garment/equipment/accessory layers`

No censor garment is structurally required. Presentation may be neutral, sensual, erotic, heroic, brutal or vulnerable according to scene intent.

## B3 — PASS/CLOSED

B3A V2 remains the validated adult-female hidden structural guide only.

B3B history:

- V1 — FAIL/CLOSED: hidden 3D mask owned final silhouette;
- V2 — FAIL/CLOSED: procedural/mannequin visual route;
- V3 — FAIL/CLOSED: high-resolution render mechanically reduced/quantized;
- V4 — PASS: user-locked pixel-art source view normalized with nearest-neighbor only and promoted unchanged.

Canonical production body base:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`

Promotion commit:

`2deb765c3980d586ef9747340bb48852dedca452`

Recorded production facts:

- `37×128` RGBA;
- visible standing height `128 px`;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- front-three-quarter elevated belt-scroller view;
- adult nude/hairless/barefoot body base;
- persistent 2D visible ownership.

Detailed body history:

- `docs/G3S_B3_NUDE_BODY_BASE_LOG.md`
- `docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`

## 128 px clarification — LOCKED

`128 px` is the target **visible standing body height** in the native `640×360` gameplay raster with the locked orthographic `26°` camera. It is not a universal source/frame canvas dimension. Hair, weapons and extreme animation bounds may use larger transparent frames while preserving this body scale.

## Current gate — B4 HAIR

Hair is now the only current visible-layer gate.

Canonical hair direction:

- very long;
- heavy;
- voluminous;
- messy black hair;
- primary silhouette anchor;
- separate from the body base;
- persistent across animation rather than regenerated independently per frame;
- eligible for deterministic secondary-motion/wind guides later;
- must preserve body visibility/ownership underneath.

The first B4 deliverable should establish one static gameplay-view hair layer aligned to the promoted B3B body base before any animation test.

No B5 clothing/restraints/accessories or G3S-C motion begins before B4 passes.
