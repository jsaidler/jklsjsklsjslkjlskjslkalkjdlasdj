# G3S-B3B — Native 2D Body Source

Status date: **2026-09-06**

Gate status: **V4 FIXED REFERENCES LOCKED — NATIVE-PIXEL AUTHORING IMPLEMENTATION NEXT**

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

The user supplied a fully nude four-view Grok turnaround earlier in the B3B process.

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

It remains available as anatomy/proportion support, not production pixel art.

## Final user-supplied visual reference — LOCKED

The user explicitly ended the reference-acquisition loop and locked the currently available four-view body image as the **final visual reference to proceed from**.

Machine-readable marker:

`tools/structured-2d-character-pipeline/g3s_b3b_locked_visual_reference.json`

Recorded source facts:

- SHA256: `f2ba82dbcd759c55cbc1c70cf1100bd85a0319cf5fe53258e461406ba55cd08a`;
- dimensions: `1168×784`;
- format: JPEG;
- views: front, back, profile and front three-quarter;
- adult nude/hairless body reference;
- dark flat presentation background.

### User-interaction lock

From this point forward:

- do **not** ask the user to generate another body reference;
- do **not** ask the user to run another Grok prompt for the body;
- do **not** ask for another turnaround;
- do **not** reopen the body-reference search loop;
- the assistant/pipeline owns the work required to turn the already-available references into production pixel art.

The earlier high-resolution nude turnaround may remain as supporting anatomy evidence already available, but the newly locked four-view image is the user's final supplied visual reference.

## What `128 px` means — LOCKED

`128 px` is the **visible standing height of the protagonist at the locked native gameplay scale**, not a universal sprite-frame or source-canvas dimension.

G1 compared `112 / 128 / 144 px` at native `640×360` and locked `128 px` with the orthographic `26°` camera because it best balanced character readability with combat/walkable-screen composition.

Consequences:

- the standing body is reviewed at approximately `128 px` visible height;
- production animation frames may be wider/taller than `128×128`;
- reference images remain reference material and are never mechanically promoted into the final sprite.

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

V3 did not author pixel art. It isolated the three-quarter reference, reduced it mechanically to `128 px`, retained the reduced silhouette/mask, quantized colors and applied local cleanup. The result read as a tiny reduced render rather than authored modern pixel art.

V3 is closed. Nothing from its candidate is promoted into B3B. No model cleanup command applies because V3 downloaded no model weights.

## V4 — DIRECT NATIVE-PIXEL AUTHORING METHOD — CURRENT

Machine-readable specification:

`tools/structured-2d-character-pipeline/g3s_b3b_v4_direct_pixel_authoring_spec.json`

V4 keeps the core rule exposed by V3: **do not convert the reference into pixel art. Author the production body for the native pixel grid while using the fixed references only as visual/anatomical guidance.**

The previous V4 wording that depended on the user producing another Grok candidate is superseded.

### Fixed-reference authoring contract

- use the already-locked visual/body references only;
- no further user reference-generation burden;
- target front-three-quarter elevated belt-scroller gameplay view at approximately the locked `26°` pitch;
- target approximately `128 px` visible standing body height;
- body owner is adult, nude, hairless, barefoot, with no clothes/restraints/weapons;
- silhouette, anatomy simplification, value groups and pixel clusters must be intentionally authored for native gameplay readability;
- no antialiasing, smooth painterly gradients or render microtexture in the production sprite;
- no high-resolution resize/quantize/trace route;
- no procedural mannequin anatomy promoted as final art.

### Local tooling boundary

Local deterministic tooling may validate already-authored pixel art, key a flat background without altering the silhouette, measure bounds/scale, perform raster QA, generate 1×/gameplay previews and package/hash an accepted source.

It may not manufacture quality by mechanically pixelating a reference, repairing anatomy procedurally or shifting routine repainting onto the user.

## Current exact action

**The reference-gathering phase is closed.**

The next project action is to **select/implement a valid native-pixel authoring path from the fixed references and produce the first real B3B body candidate without asking the user for another image or prompt.**

No conversion runner is approved. No further Grok/body-reference request is part of the operator loop.

B4 hair, B5 clothing/accessories and G3S-C animation remain blocked until an authored B3B body source passes visual review.
