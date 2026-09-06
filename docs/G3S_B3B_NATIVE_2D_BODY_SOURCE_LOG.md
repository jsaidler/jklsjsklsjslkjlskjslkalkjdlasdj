# G3S-B3B — Native 2D Body Source

Status date: **2026-09-06**

Gate status: **V4 PIXEL-REFERENCE NORMALIZATION RUNNER READY — REVIEW NEXT**

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

## V4 — LOCKED PIXEL-REFERENCE NORMALIZATION — CURRENT

Machine-readable specification:

`tools/structured-2d-character-pipeline/g3s_b3b_v4_direct_pixel_authoring_spec.json`

V4 now uses an important distinction that V3 did not have: **the user-locked source is itself pixel-art imagery.** Therefore the bounded review candidate may extract the existing front-three-quarter pixel-art view, key only the flat dark presentation background, and normalize its visible standing height to `128 px` using nearest-neighbor only.

This is not permission to revive render-to-pixel conversion. The high-resolution anatomy render remains forbidden as a visible sprite source.

### V4 implementation — READY

Helper:

`tools/structured-2d-character-pipeline/g3s_b3b_v4_extract_pixel_reference_candidate.py`

Runner:

`tools/structured-2d-character-pipeline/14_run_g3s_b3b_v4_pixel_reference_candidate.ps1`

Output directory:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_v4_pixel_reference`

The helper:

1. locates the exact locked JPEG by SHA256, including common user image folders;
2. verifies exact `1168×784` dimensions;
3. extracts the existing rightmost front-three-quarter pixel-art figure;
4. removes only the flat dark presentation background to alpha;
5. normalizes visible height to `128 px` with nearest-neighbor only;
6. does **not** synthesize a palette, repair anatomy, morph the silhouette or use hidden-3D RGB/masks;
7. generates native candidate, 4× review image, `640×360` gameplay preview and contact sheet.

This runner is **review-only**. It cannot automatically promote the candidate to production B3B.

## Current exact action

Run the V4 review runner exactly once and inspect/share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_v4_pixel_reference\g3s_b3b_v4_contact_sheet.png`

If the candidate reads well at native `1×` and in gameplay context, it can become the persistent B3B body source after validation metadata is added. If it collapses visually, close this normalization route without asking the user for another reference.

B4 hair, B5 clothing/accessories and G3S-C animation remain blocked until B3B passes.
