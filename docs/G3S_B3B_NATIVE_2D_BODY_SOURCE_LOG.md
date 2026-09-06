# G3S-B3B — Native 2D Body Source

Status date: **2026-09-06**

Gate status: **PASS/CLOSED — V4 PRODUCTION BODY BASE PROMOTED**

## Canonical ownership rule

Hidden 3D remains motion/topology/reference infrastructure only. It does not own final visible RGB, alpha or sprite silhouette. Final exported/runtime character art is owned by persistent native 2D sprite assets.

A valid B3B body source owns its own visible RGB, alpha, silhouette, native pixel clusters/value structure, adult-female anatomical readability and Exilada-specific physical presence.

## Closed attempts

### V1 — FAIL/CLOSED ROUTE

V1 copied the projected B3A/MPFB mask into final sprite alpha/silhouette and violated the G3V visible-ownership rule.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v1_route_failure.json`

### V2 — FAIL/CLOSED VISUAL ROUTE

V2 was technically 2D-owned but visually failed: procedural/mannequin anatomy, poor proportions, crude pelvis/thigh transitions, weak hands/feet, pseudo-3D banding and absent Exilada identity.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v2_visual_failure.json`

### V3 — FAIL/CLOSED VISUAL AND METHOD ROUTE

V3 mechanically reduced/quantized a high-resolution render and produced a miniaturized render rather than authored pixel art.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v3_visual_failure.json`

No model cleanup applies to V1/V2/V3 because these B3B routes downloaded no model weights.

## Locked references

### Supporting high-resolution nude anatomy reference

`assets/source/characters/exilada/reference/exilada_body_turnaround_nude_approved.jpg`

SHA256:

`1e4b272c39f21cee0087e2aa6a5518fcc7a10c5ef47525ffcaff512ea07e8bbf`

Role: anatomy/proportion support only; never visible sprite source.

### Final user-supplied pixel-art visual reference

Marker:

`tools/structured-2d-character-pipeline/g3s_b3b_locked_visual_reference.json`

Source facts:

- SHA256 `f2ba82dbcd759c55cbc1c70cf1100bd85a0319cf5fe53258e461406ba55cd08a`;
- `1168×784` JPEG;
- front/back/profile/front-three-quarter;
- adult nude/hairless body;
- pixel-art imagery on a flat dark presentation background.

User-interaction lock remains: do not reopen body-reference acquisition or ask for another Grok/body turnaround.

## B3B V4 — PASS

V4 extracted the existing front-three-quarter pixel-art view from the locked reference, removed only the flat presentation background and normalized visible standing height to `128 px` using nearest-neighbor only.

No anatomy repair, silhouette morphing, palette synthesis, smoothing, hidden-3D RGB/mask use or render-to-pixel conversion was performed.

Reviewed contact sheet:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_v4_pixel_reference\g3s_b3b_v4_contact_sheet.png`

Recorded contact-sheet SHA256:

`2b3ad85e956fdd432fe6cd52ac94d71afd30b5603b071681f81d2dbd8788a182`

Approved local candidate:

- dimensions `37×128` RGBA;
- visible standing height `128 px`;
- authoritative raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`.

Visual approval marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v4_visual_approval.json`

## Promotion history

The first promotion attempt correctly refused a mismatch because the expected digest had been measured from an assistant-side reconstruction rather than the user's actual local candidate.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v4_promotion_hash_mismatch.json`

The corrected promotion runner used the actual local candidate digest, did not regenerate V4, verified exact dimensions/raw RGBA/alpha height and copied the exact candidate pixels unchanged.

## Canonical production body base — PROMOTED

Git commit:

`2deb765c3980d586ef9747340bb48852dedca452`

Canonical files:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`

Recorded production facts:

- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- dimensions `37×128`;
- visible standing height `128 px`;
- view `front-three-quarter elevated belt-scroller`;
- state `adult nude hairless barefoot body base`;
- visible ownership `persistent 2D pixel asset`;
- excludes hair, clothing, restraints, accessories and weapons.

## Decision

**G3S-B3B = PASS/CLOSED.**

The complete persistent nude/hairless body base now exists as a canonical production 2D pixel asset. It is the body owner beneath all later removable layers.

## Next gate

**G3S-B4 — HAIR is OPEN/CURRENT.**

Hair must be a separate persistent 2D asset/layer family. It must preserve the Exilada's very long, heavy, voluminous, messy black hair as a primary silhouette anchor while keeping the body base unchanged underneath.

B5 clothing/restraints/accessories remains blocked until B4 passes. G3S-C layered motion remains blocked until B3/B4/B5 are ready.
