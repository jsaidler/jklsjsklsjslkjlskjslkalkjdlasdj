# G3S-B3B — Native 2D Body Source

Status date: **2026-09-06**

Gate status: **V4 VISUAL PASS — PROMOTION RUNNER READY**

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

## Existing high-resolution nude anatomy reference — PASS / SUPPORTING REFERENCE

The earlier fully nude Grok turnaround remains anatomy/proportion support only.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3b_body_reference_approval.json`

Canonical local path:

`assets/source/characters/exilada/reference/exilada_body_turnaround_nude_approved.jpg`

SHA256:

`1e4b272c39f21cee0087e2aa6a5518fcc7a10c5ef47525ffcaff512ea07e8bbf`

It is not production pixel art and may not be used as visible sprite source.

## Final user-supplied visual reference — LOCKED

The user explicitly ended the reference-acquisition loop and locked the current four-view pixel-art body image as the final visual reference to proceed from.

Machine-readable marker:

`tools/structured-2d-character-pipeline/g3s_b3b_locked_visual_reference.json`

Recorded source facts:

- SHA256: `f2ba82dbcd759c55cbc1c70cf1100bd85a0319cf5fe53258e461406ba55cd08a`;
- dimensions: `1168×784`;
- format: JPEG;
- views: front, back, profile and front three-quarter;
- adult nude/hairless body;
- already presented as pixel-art imagery on a dark flat background.

### User-interaction lock

From this point forward:

- do **not** ask the user to generate another body reference;
- do **not** ask the user to run another Grok prompt for the body;
- do **not** ask for another turnaround;
- do **not** reopen the body-reference search loop;
- the assistant/pipeline owns the work required to turn the already-available references into production pixel art.

## What `128 px` means — LOCKED

`128 px` is the visible standing height at the locked native `640×360` gameplay scale. It is not a universal frame-canvas size.

## B3B visual approval rule — LOCKED

Required first-glance reading:

**adult, attractive, sensual, strong, dangerous, severe and lived-in — beauty + hardness + survival — clearly within the project's sword-and-sorcery lineage.**

Automatic visual FAIL conditions include mannequin/procedural-body appearance, generic fitness/character-creator reading, superhero/bodybuilder exaggeration, shortened/flattened proportions, weak chest/pelvis/thigh anatomy, poor hands/feet at native 1×, pseudo-3D/filtered-render appearance, sanitized mature body language, absent Exilada identity or failure to evoke Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell.

## V3 — FAIL/CLOSED VISUAL AND METHOD ROUTE

V3 started from the high-resolution render and reduced/quantized it. The result was a tiny reduced render rather than authored pixel art.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v3_visual_failure.json`

No model cleanup applies because V3 downloaded no model weights.

## V4 — LOCKED PIXEL-REFERENCE NORMALIZATION — VISUAL PASS

Machine-readable specification:

`tools/structured-2d-character-pipeline/g3s_b3b_v4_direct_pixel_authoring_spec.json`

Review helper:

`tools/structured-2d-character-pipeline/g3s_b3b_v4_extract_pixel_reference_candidate.py`

Review runner:

`tools/structured-2d-character-pipeline/14_run_g3s_b3b_v4_pixel_reference_candidate.ps1`

Reviewed contact sheet:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_v4_pixel_reference\g3s_b3b_v4_contact_sheet.png`

Contact-sheet SHA256:

`2b3ad85e956fdd432fe6cd52ac94d71afd30b5603b071681f81d2dbd8788a182`

Native candidate:

- dimensions: `37×128` RGBA;
- visible standing height: `128 px`;
- approved raw RGBA SHA256: `bd4a78e231b04dcaa75a2ae9ae2baeb2d5a1f99f9a3a49de1c86ee10eb98dde9`.

Visual approval marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v4_visual_approval.json`

### Review result

**VISUAL PASS for the nude/hairless body-base gate.**

The reviewed candidate:

- reads as intentional pixel-art imagery at the locked native scale rather than a reduced smooth render;
- preserves readable adult-female anatomy at `128 px` standing height;
- keeps face, chest, pelvis, legs, hands and feet distinguishable at gameplay scale;
- remains compatible with the locked Exilada body direction;
- provides a usable persistent 2D nude/hairless body layer;
- remains readable in the `640×360` gameplay preview.

This is approval of the **body base only**. Hair, clothing, restraints, accessories and animation remain separate gates.

## Promotion implementation — READY

Promotion helper:

`tools/structured-2d-character-pipeline/g3s_b3b_v4_promote_body_base.py`

Promotion runner:

`tools/structured-2d-character-pipeline/15_promote_g3s_b3b_v4_body_base.ps1`

The promotion step is deliberately non-artistic. It:

1. rebuilds the exact reviewed V4 candidate from the locked reference;
2. verifies `37×128` dimensions and the approved raw-RGBA digest;
3. refuses any pixel mismatch;
4. copies the exact approved pixels to the canonical production asset path;
5. writes provenance metadata;
6. commits/pushes only the promoted body PNG and metadata JSON.

Canonical target paths:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`

No anatomy, silhouette, palette or pixel-cluster changes are permitted during promotion.

## Current exact action

Run the promotion runner once. After the resulting production asset is confirmed in GitHub, mark **G3S-B3B PASS/CLOSED** and open **G3S-B4 hair**.

B5 clothing/accessories and G3S-C animation remain blocked until their preceding gates pass.
