# G3S-B3B — Native 2D Body Source

Status date: **2026-09-06**

Gate status: **V3 FAIL/CLOSED — AUTHORED NATIVE-PIXEL BODY CANDIDATE NEXT**

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

The in-chat generated body sheet was rejected as generic/fitness-like and as faux technical presentation rather than trustworthy production art or metadata. It has no production authority.

## Approved Exilada high-resolution nude body reference — PASS

The user supplied a **fully nude four-view Grok turnaround**. It is the primary high-resolution B3B body reference.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3b_body_reference_approval.json`

Canonical local path:

`assets/source/characters/exilada/reference/exilada_body_turnaround_nude_approved.jpg`

Recorded source:

- SHA256: `1e4b272c39f21cee0087e2aa6a5518fcc7a10c5ef47525ffcaff512ea07e8bbf`;
- dimensions: `2048×1401`;
- views: front, back, profile and front three-quarter;
- adult female;
- approximately 162 cm target identity;
- olive/brown skin;
- bald/hairless for body-reference purposes;
- bare feet;
- natural feminine proportions, lean/functional/resilient;
- mature, severe, sensual, dangerous and lived-in;
- aligned with Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell;
- complete pelvic anatomy visible;
- no occluding garment.

The older covered turnaround remains historical evidence only.

## What `128 px` means — LOCKED

`128 px` is the **visible standing height of the protagonist at the locked native gameplay scale**, not a universal sprite-frame or source-canvas dimension.

G1 compared `112 / 128 / 144 px` at native `640×360` and locked `128 px` with the orthographic `26°` camera because it best balanced character readability with combat/walkable-screen composition.

Consequences:

- the standing body is reviewed at approximately `128 px` visible height;
- production animation frames may be wider/taller than `128×128`;
- the high-resolution turnaround remains reference material and is never mechanically promoted into the final sprite.

## B3B visual approval rule — LOCKED

Required first-glance reading:

**adult, attractive, sensual, strong, dangerous, severe and lived-in — beauty + hardness + survival — clearly within the project's sword-and-sorcery lineage.**

Automatic visual FAIL conditions include mannequin/procedural-body appearance, generic fitness/character-creator reading, superhero/bodybuilder exaggeration, shortened/flattened proportions, weak chest/pelvis/thigh anatomy, poor hands/feet at native 1×, pseudo-3D/filtered-render appearance, sanitized mature body language, absent Exilada identity or failure to evoke Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell.

## V3 — FAIL/CLOSED VISUAL AND METHOD ROUTE

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_v3_reference_guided\g3s_b3b_v3_contact_sheet.png`

Reviewed artifact SHA256:

`ded6e53cd5c36b106a7d7729534cd2f12241862a6f3b0e3a27b6e706ded08047`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v3_visual_failure.json`

### What V3 actually did

V3 did **not** author pixel art. It:

1. isolated the front-three-quarter figure from the approved high-resolution render;
2. reduced that figure mechanically to `128 px` visible height using image resampling;
3. retained the mechanically reduced reference mask/silhouette;
4. quantized the reduced colors;
5. applied local majority cleanup.

That is a reduced-render / resize-and-quantize study, not authored native pixel character art.

### Why V3 fails

The output visibly demonstrates the existing kill switch rather than solving B3B:

- it reads as a tiny reduced illustration/render;
- hands, feet and face collapse at native scale;
- anatomical masses are inherited from reduction rather than redesigned for the pixel grid;
- value structure remains render-like/noisy instead of intentional connected pixel clusters;
- the high-resolution reference mechanically owns the review silhouette;
- the method therefore does not test the actual missing capability: intentional native pixel-art authoring.

V3 is closed. Nothing from its candidate is promoted into B3B.

No model cleanup command applies because V3 downloaded no model weights and used only the existing Python/Pillow runtime.

## Current gate

**G3S-B3B authored native-pixel body candidate** is current.

The next candidate must begin as actual character pixel art. The approved nude turnaround may guide anatomy, proportions, body mass and identity, but it may **not** be resized, quantized, mechanically traced or used as direct final silhouette authority.

The valid next artifact is one deliberately authored gameplay-view body sprite whose visible standing height is approximately `128 px`, judged at native 1× and in `640×360` gameplay context.

No B3B runner is approved at this point. Do not rerun V3. B4 hair, B5 clothing/accessories and G3S-C animation remain blocked until an authored B3B body source passes visual review.
