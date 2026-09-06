# G3S-B3B — Native 2D Body Source

Status date: **2026-09-06**

Gate status: **V3 REFERENCE-GUIDED PIXEL TRANSLATION SPIKE READY FOR RUN — REVIEW ONLY / NOT PRODUCTION PASS**

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

A user-supplied Grok turnaround is the **primary high-resolution body reference for B3B authoring**.

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

## V3 — reference-guided native-grid translation spike — READY FOR RUN

V3 is a **bounded visual spike**, not a production-source promotion.

Tooling:

- helper: `tools/structured-2d-character-pipeline/g3s_b3b_v3_reference_guided_translation.py`;
- runner: `tools/structured-2d-character-pipeline/13_run_g3s_b3b_v3_reference_guided_translation.ps1`;
- ready marker: `tools/structured-2d-character-pipeline/g3s_b3b_v3_spike_ready.json`.

The runner:

1. verifies the canonical approved body-reference marker;
2. locates the exact approved image by SHA256 in common user image folders;
3. uses only the approved 2D turnaround, never B3A/3D RGB or mask, for this visible-translation study;
4. isolates the approved front-three-quarter reference view;
5. normalizes to the locked `128 px` native body height;
6. creates a deterministic palette/cluster abstraction at the native grid;
7. explicitly removes the dark reference loincloth from body ownership by reconstructing the covered pelvic region in skin tones at native pixels;
8. emits a native guide, visual candidate, silhouette/gameplay preview and machine-readable result;
9. marks every output **REVIEW REQUIRED / NOT PRODUCTION PASS**.

### Critical boundary

The project rule rejecting simple high-resolution resize/quantize as a final Production Pixel Master remains in force.

Therefore V3 cannot be promoted automatically merely because the script succeeds. It exists to answer one bounded visual question: **can deterministic 2D reference-guided abstraction yield a native-grid body that actually reads as intentional modern pixel art rather than reduced illustration/filtering?**

If the answer is no, V3 closes as a visual failure and its candidate is not promoted. No model cleanup applies because V3 downloads no model weights.

If the answer is yes, the accepted native cluster language must then be frozen/re-authored as the persistent B3B production source and validated independently from the high-resolution reference.

## Current gate

**G3S-B3B V3 visual review is current.**

B4 hair, B5 clothing/accessories and G3S-C animation remain blocked until a replacement B3B production source passes.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\13_run_g3s_b3b_v3_reference_guided_translation.ps1"
```

Then STOP and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_v3_reference_guided\g3s_b3b_v3_contact_sheet.png`

or the complete console error.
