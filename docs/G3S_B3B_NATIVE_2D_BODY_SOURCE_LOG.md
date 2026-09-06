# G3S-B3B — Native 2D Body Source

Status date: **2026-09-06**

Gate status: **V3 NUDE-REFERENCE PIXEL TRANSLATION SPIKE — READY TO RERUN**

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

The user supplied a new **fully nude four-view Grok turnaround**. It supersedes the earlier covered body sheet as the primary high-resolution B3B body reference.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3b_body_reference_approval.json`

Canonical local path expected by the runner:

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
- visually aligned with Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell;
- complete pelvic body anatomy visible in the reference;
- no occluding loincloth/tapa-sexo.

Superseded covered reference SHA256:

`2773c199b3ff28ad5a72e33feb97201a9567a633f8466620084362fd9aae7474`

The covered reference remains historical evidence only. It is no longer the primary B3B anatomy source.

### Consequence of the nude reference

The previous need to infer/reconstruct pixels beneath a small covering disappears at the reference stage.

Locked consequences:

- the V3 helper must not synthesize or patch the pelvic region;
- no `repair_pelvis` or equivalent authored reconstruction is allowed/needed in the V3 review spike;
- body-base ownership remains independent of future clothes;
- later loincloths/garments still belong to B5, not to B3B.

## What `128 px` means — LOCKED

`128 px` is the **visible standing height of the protagonist at the locked native gameplay scale**, not a universal sprite-frame or source-canvas dimension.

G1 compared `112 / 128 / 144 px` at native `640×360` and locked `128 px` with the orthographic `26°` camera because it best balanced character readability with combat/walkable-screen composition.

Consequences:

- the standing body is normalized to approximately `128 px` visible height for native-scale review;
- production animation frames may be wider/taller than `128×128` to contain limbs, hair, weapons and extreme actions;
- the high-resolution turnaround remains high-resolution reference material.

## B3B visual approval rule — LOCKED

Required first-glance reading:

**adult, attractive, sensual, strong, dangerous, severe and lived-in — beauty + hardness + survival — clearly within the project's sword-and-sorcery lineage.**

Automatic visual FAIL conditions include mannequin/procedural-body appearance, generic fitness/character-creator reading, superhero/bodybuilder exaggeration, shortened/flattened proportions, weak chest/pelvis/thigh anatomy, poor hands/feet at native 1×, pseudo-3D/filtered-render appearance, sanitized mature body language, absent Exilada identity or failure to evoke Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell.

## V3 — nude-reference native-grid translation spike

V3 is a **bounded visual spike**, not a production-source promotion.

Tooling:

- helper: `tools/structured-2d-character-pipeline/g3s_b3b_v3_reference_guided_translation.py`;
- runner: `tools/structured-2d-character-pipeline/13_run_g3s_b3b_v3_reference_guided_translation.ps1`;
- ready marker: `tools/structured-2d-character-pipeline/g3s_b3b_v3_spike_ready.json`.

The helper/runner now:

- pin the new nude reference by SHA256;
- expect it at the canonical repo-local path above;
- use the front-three-quarter panel for the bounded native-scale review abstraction;
- do not use hidden-3D RGB/mask/silhouette;
- do not perform pelvic reconstruction;
- state explicitly that the output is review-only and cannot be promoted automatically.

### Critical boundary

The project rule rejecting simple high-resolution resize/quantize as a final Production Pixel Master remains in force.

V3 exists only to answer a bounded visual question: **does the approved body survive native 128 px abstraction well enough to inform authored pixel art, or does it still read as reduced illustration/filtering?**

If V3 fails visually, V3 closes and nothing is promoted. No model cleanup applies because V3 downloads no model weights.

If V3 passes as a visual study, the accepted cluster/silhouette language must then be established as an independently owned persistent B3B production asset rather than mechanically promoting the high-resolution reduction.

## Current gate

**G3S-B3B V3 visual review remains current.** B4 hair, B5 clothing/accessories and G3S-C animation remain blocked until a replacement B3B production source passes.

## Exact next operator action

One-time prerequisite: save the exact approved nude turnaround at:

`D:\GOOGLE DRIVE\DEV\Roguelite\assets\source\characters\exilada\reference\exilada_body_turnaround_nude_approved.jpg`

Expected SHA256:

`1e4b272c39f21cee0087e2aa6a5518fcc7a10c5ef47525ffcaff512ea07e8bbf`

Then run:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\13_run_g3s_b3b_v3_reference_guided_translation.ps1"
```

Then STOP and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_v3_reference_guided\g3s_b3b_v3_contact_sheet.png`

or the complete console error.
