# G3S-B3B — Native 2D Body Source

Status date: **2026-09-05**

Gate status: **BODY REFERENCE APPROVED — PIXEL-TRANSLATION CANDIDATE NEXT**

## Canonical ownership rule

Hidden 3D remains motion/topology/reference infrastructure only. It does not own final visible RGB, alpha or sprite silhouette. Final exported/runtime character art is owned by persistent native 2D sprite assets.

A valid B3B body source must own its own visible RGB, alpha, silhouette, native pixel clusters/value structure, adult-female anatomical readability and Exilada-specific physical presence.

## Closed B3B attempts

### V1 — FAIL/CLOSED ROUTE

V1 copied the projected B3A/MPFB mask into final sprite alpha/silhouette and recolored it. This violated the G3V visible-ownership kill switch.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v1_route_failure.json`

### V2 — FAIL/CLOSED VISUAL ROUTE

V2 corrected visible ownership technically but failed visually: oversized torso, generic procedural-mannequin anatomy, blocky hands/feet, crude pelvis/thigh transitions, pseudo-3D banding, stiff silhouette and absent Exilada identity.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v2_visual_failure.json`

Rejected V2 source/tooling was removed from `main`; no model weights were downloaded, so no cleanup command applies.

### Chat image-generation probe — REJECTED / NON-PRODUCTION

A bald nude body sheet generated in-chat was rejected as a generic polished/fitness-model body and as faux technical presentation rather than trustworthy production art or metadata. It has no production authority.

## Approved Exilada high-resolution body reference — PASS

A user-supplied Grok turnaround is now the **primary high-resolution body reference for B3B authoring**.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3b_body_reference_approval.json`

Recorded source:

- SHA256: `2773c199b3ff28ad5a72e33feb97201a9567a633f8466620084362fd9aae7474`;
- dimensions: `1168×784`;
- four coherent views: front, back, profile and front three-quarter;
- adult female;
- approximately 162 cm target identity;
- olive/brown skin;
- bald/hairless for body-reference purposes;
- bare feet;
- lean, functional, resilient anatomy;
- mature, severe, sensual, dangerous and lived-in presence;
- visually aligned with the locked **Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell** lineage.

This reference resolves the previous uncertainty about **which body B3B is translating**.

### Coverage note

The turnaround contains a minimal dark loincloth / tapa-sexo. It is only an occluding reference garment.

Locked consequences:

- it is not body geometry;
- it must not be baked into the permanent body base;
- final pelvic body pixels belong to B3B body ownership;
- any later loincloth/trap/garment belongs to B5 clothing/equipment layers;
- no censor garment is structurally required.

## B3B visual approval rule — LOCKED

Required first-glance reading:

**adult, attractive, sensual, strong, dangerous, severe and lived-in — beauty + hardness + survival — clearly within the project's sword-and-sorcery lineage.**

Automatic visual FAIL conditions include:

- mannequin/procedural-body appearance;
- generic fitness-model or character-creator reading;
- superhero/bodybuilder exaggeration;
- shortened/flattened proportions from misreading “compact”;
- weak chest/pelvis/thigh anatomy;
- poor hands/feet at native 1×;
- pseudo-3D or filtered-render appearance;
- sanitized/neutralized mature body language;
- no meaningful Exilada identity;
- failure to evoke Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell.

## Current gate — pixel-art visual translation candidate

The approved turnaround is **reference**, not final production pixel art. It must not simply be resized, quantized or pixel-filtered into B3B.

The next artifact is a **pixel-art visual translation candidate** built from the approved body direction. Its job is to prove that the body language and proportions survive the modern-pixel-art translation before a replacement production B3B native asset/runner is committed.

The candidate may use the approved turnaround and canonical Exilada master as visual references. It may not use B3A/3D projection as final silhouette authority.

No B4 hair, B5 clothing/accessories or G3S-C animation begins until a replacement B3B body source passes visual review.

## Next operator action

**No local B3B runner is currently approved.**

Create/review the pixel-art visual translation candidate first. After visual approval, establish the accepted native 2D production source and its deterministic validation/export tooling.
