# G3S-B3B — Native 2D Body Source

Status date: **2026-09-05**

Gate status: **V2 FAIL/CLOSED VISUAL ROUTE — B3B REMAINS CURRENT**

## Canonical ownership rule

Hidden 3D remains motion/topology/reference infrastructure only. It does not own final visible RGB, alpha or sprite silhouette.

A valid B3B body source must itself own:

- final visible RGB;
- final alpha;
- final silhouette;
- native pixel clusters and value structure;
- adult-female anatomical readability;
- Exilada-compatible body proportions.

## V1 — FAIL/CLOSED ROUTE

V1 copied the projected B3A/MPFB mask into final sprite alpha/silhouette and then recolored it. That violated the G3V visible-ownership kill switch.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v1_route_failure.json`

## V2 — FAIL/CLOSED VISUAL ROUTE 2026-09-05

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_authored_body_v2\g3s_b3b_contact_sheet_v2.png`

V2 corrected the ownership boundary technically: the committed PNG, not B3A, owned RGB/alpha/silhouette. However the visual result is unacceptable and triggers the project's existing procedural-mannequin kill switch.

Observed failures:

- torso grossly oversized relative to head and legs;
- generic mannequin anatomy rather than Exilada-compatible lean/resilient proportions;
- blocky hands and feet with poor 1x readability;
- pelvis/thigh transition reads as assembled primitives rather than coherent anatomy;
- high-contrast banding creates a pseudo-3D mannequin look;
- pose/silhouette are stiff and unsuitable as a convincing production body base;
- no meaningful Exilada identity beyond generic adult-female markers;
- overall image does not read as intentional modern pixel-art character art.

Canonical failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v2_visual_failure.json`

Rejected V2 repo files were removed from `main` so they cannot be promoted or rerun accidentally:

- `assets/source/characters/exilada/body/g3s_b3b_body_base_source_v2.png`;
- `tools/structured-2d-character-pipeline/g3s_b3b_body_base_source_v2.json`;
- `tools/structured-2d-character-pipeline/g3s_b3b_validate_authored_body_v2.py`;
- `tools/structured-2d-character-pipeline/12_run_g3s_b3b_authored_body_v2.ps1`.

No model was downloaded by V2, so there are no model-weight files to remove.

## Image-generation body concept — REJECTED / NON-PRODUCTION 2026-09-05

A subsequent image-generation probe produced a bald nude female body sheet with multiple views and faux technical panels. It is **not** a B3B candidate and has no production authority.

Reason for rejection:

- body reads as a generic polished/fitness-model nude rather than the Exilada;
- anatomy/body language do not sufficiently reflect the locked Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell lineage;
- insufficient severe, physical, lived-in sword-and-sorcery character presence;
- silhouette and proportions do not preserve the Exilada's specific compact/lean/resilient identity;
- generated sheet is illustrative concept art, not verified native `128x128` authored pixel art;
- faux masks/landmarks/palette labels are presentation graphics, not trustworthy production metadata;
- therefore it cannot be promoted to body source, silhouette authority, mask authority or production evidence.

The only useful conclusion from this probe is negative: adult nudity itself is not the blocker; the blocker is obtaining production-quality Exilada-specific character art that satisfies the native-2D pipeline contract.

## Current gate

**B3B remains current.**

The next candidate must be actual character art, not a primitive/mannequin construction and not a generic generated nude sheet. It may use B3A only as anatomy/proportion/joint/scale reference and may use the canonical Exilada identity master as design reference. Final art still must remain sprite-owned and native-2D.

No hair, clothing or animation may begin until a B3B body source passes visual review.

## Next operator action

**No runner is currently approved.** Do not rerun V2.
