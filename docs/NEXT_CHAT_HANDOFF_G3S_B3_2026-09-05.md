# Next-chat handoff — G3S structured character build

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
12. `docs/G3S_B4_HAIR_LOG.md`

Do not reconstruct state from chat memory if documents disagree.

## Living-document invariant — MANDATORY

Every state-changing project action must update thematic docs, `PROJECT_STATE`, this handoff when continuation changes, and commit before reporting completion.

## Locked architecture

Hidden 3D may own motion/topology/joints/sockets/depth/physics/guides, but persistent 2D pixel assets own final visible RGB/alpha/silhouette.

No high-resolution render/reference may be mechanically pixelated into final production art.

## Build order

1. complete adult hairless body base — **PASS/CLOSED**;
2. separate hair — **CURRENT**;
3. separate clothing/bindings/restraints/accessories — BLOCKED UNTIL HAIR PASS;
4. layered sprite animation driven by hidden-rig guides — BLOCKED UNTIL LAYERS READY.

## B3/B3B history

- B3A V1 — FAIL/CLOSED REVISION.
- B3A V2 — PASS/CLOSED structural guide.
- B3B V1 — FAIL/CLOSED 3D-mask-owned silhouette.
- B3B V2 — FAIL/CLOSED procedural/mannequin visual route.
- B3B V3 — FAIL/CLOSED reduced/quantized high-resolution render.
- final user-supplied four-view pixel-art visual reference — PASS / LOCKED / no more user generation.
- B3B V4 — **PASS/CLOSED / PRODUCTION BODY BASE PROMOTED**.

## Canonical production body base

Promotion commit:

`2deb765c3980d586ef9747340bb48852dedca452`

Canonical files:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`

Recorded facts:

- `37×128` RGBA;
- visible standing height `128 px`;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- adult nude/hairless/barefoot body base;
- front-three-quarter elevated belt-scroller view;
- persistent 2D visible ownership.

The body base must not be altered when B4/B5 layers are added.

## Fixed body references

Supporting high-resolution anatomy reference:

`assets/source/characters/exilada/reference/exilada_body_turnaround_nude_approved.jpg`

SHA256 `1e4b272c39f21cee0087e2aa6a5518fcc7a10c5ef47525ffcaff512ea07e8bbf`.

Final user-supplied pixel-art reference marker:

`tools/structured-2d-character-pipeline/g3s_b3b_locked_visual_reference.json`

SHA256 `f2ba82dbcd759c55cbc1c70cf1100bd85a0319cf5fe53258e461406ba55cd08a`.

Hard interaction lock: do not ask the user for another body image, another Grok prompt or another turnaround.

## G3S-B4 — HAIR CURRENT

Canonical hair direction:

- very long;
- heavy;
- voluminous;
- messy;
- black;
- primary silhouette anchor;
- deprivation/survival material language rather than groomed fantasy styling.

Hair is a **separate persistent 2D layer family**. It may not modify the canonical body asset or be baked into it.

### Mandatory front/back split

B4 has a locked minimum of **two persistent depth layers**:

1. `rear_hair` — composited behind the body/head/shoulders;
2. `front_hair` — composited in front where hair crosses face/neck/chest/shoulders.

Minimum composition:

`rear_hair -> body -> front_hair`

This split is structural and required for occlusion, long-hair silhouette, later animation, wind and secondary-motion ownership. Optional side/intermediate masses may be added later if needed, but a single flat hair overlay is invalid.

First B4 deliverable:

- static front-three-quarter `rear_hair` transparent asset;
- static front-three-quarter `front_hair` transparent asset;
- body alone;
- each hair layer alone;
- deterministic `rear_hair + body + front_hair` composite;
- enlarged nearest-neighbor review;
- native `640×360` gameplay preview;
- stable anchor/depth metadata.

Detailed log:

`docs/G3S_B4_HAIR_LOG.md`

## Exact next action

**No B4 runner is approved yet.**

Before asking the user to run anything, inspect the canonical `exilada_master.png` and promoted `exilada_body_base_b3b_v4.png` together, then implement the smallest valid static B4 review method with the mandatory two-layer minimum (`rear_hair` + `front_hair`).

Do not use PixelLab or another paid external API without explicit authorization. Do not reopen closed Qwen/SD1.5/PixelLock/Alucard sprite-model search.

## Actual local AI state

- only retained general local AI runtime: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable` (historical folder name; Qwen weights removed);
- deterministic workspace: `Z:\AI\RogueliteCharacterPipeline`;
- frozen RefControl evidence: `Z:\AI\Flux2RefControlSpike`;
- PixelLab is historical external paid spike code only and is not active/authorized;
- old Git tool directories do not prove installed models;
- do not assume Wan-Animate-2 installed;
- Qwen-native, SD1.5, PixelLock and Alucard remain closed.

## Operator/process rules

- read canonical docs before every project action;
- update docs before reporting state changes;
- no routine Blender/Aseprite/rigging work for the user;
- no manual frame-by-frame repainting burden;
- no additional body-reference requests;
- no new sprite-model search unless explicitly reopened;
- no B5/G3S-C before B4 PASS;
- include exact cleanup commands when a model route is closed and no longer needed;
- verify actual local runtime/disk state before naming installed tools.
