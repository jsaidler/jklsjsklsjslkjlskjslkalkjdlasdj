# G3R Renderer / Style Refinement — Execution Log

Status date: **2026-09-04**

Gate: **G3R — deterministic pixel renderer/style refinement**

Current status: **READY TO RUN.**

## Why G3R exists

G3 proved that the deterministic hidden-3D backbone can become a stable native-grid sprite under the real captured walk, but the first visible methods were not approved as production art.

Observed G3 result:

- topology/motion continuity remained stable;
- direct native semantic translation works;
- palette-banded translation is a viable technical baseline;
- the visible result still reads as a technical mannequin / processed low-detail 3D rather than a finished intentional pixel-art character;
- therefore G4 Exilada identity geometry must not start yet.

Canonical G3 technical marker:

`tools/deterministic-character-pipeline/g3_technical_approval.json`

## Locked upstream baseline

- native raster: `640×360`;
- orthographic camera pitch: `26 deg`;
- protagonist reference height: `128 px`;
- real source motion: approved G2 CMU `105_34 NormalWalk` sequence.

## Tooling

- `tools/deterministic-character-pipeline/03b_run_g3r.ps1`
- `tools/deterministic-character-pipeline/g3r_renderer_refinement.py`

Workspace output:

`Z:\AI\RogueliteCharacterPipeline\g3r`

## Refinement methods

Four representative real-walk frames are processed through three deterministic methods at native `640×360`:

### D — outlined 4-band

- four discrete value bands per material family;
- skin / cloth / hair / metal remain semantically separate;
- deterministic one-pixel exterior outline;
- no anti-aliasing, bilinear scaling or generative repainting.

### E — edge-preserving cluster

- starts from D;
- applies 2×2 majority clustering only to fully interior pixels;
- native silhouette/edge pixels are preserved;
- purpose is to increase coherent value clusters without turning the whole sprite into a coarse nearest-neighbor downsample.

### F — selective contour cluster

- starts from E;
- adds directional lower/right silhouette darkening while retaining material color on other edge regions;
- tests whether a selective contour reads more intentionally drawn than a uniform outline.

## Automated diagnostics

For every sampled frame G3R records:

- foreground pixel count;
- character bounding box;
- count of tiny disconnected foreground islands <=2 px;
- output hashes;
- exact method metadata.

These diagnostics are QA support only. Visual approval remains required.

## Hard constraints

- no Exilada production geometry yet;
- no diffusion or generative repainting;
- no high-resolution beauty render followed by generic pixel filter;
- no manual frame repaint;
- no bilinear scaling;
- same G2 topology/motion and same G1 camera/scale baseline for every method.

## PASS / FAIL rule

G3R can PASS only if at least one refined method is credible enough as the **production rendering foundation** for G4 identity mapping at 1× gameplay scale.

PASS requires:

1. stable readable silhouette;
2. coherent pixel clusters rather than incidental raster noise;
3. useful separation of skin / cloth / hair / metal;
4. contour treatment that looks deliberate rather than generic filtered 3D;
5. stable appearance across the four gait phases;
6. enough visual headroom to justify mapping Exilada identity next.

If all three methods still read as technical processed 3D, do **not** start G4. The next decision must change the visible representation strategy while retaining the proven deterministic motion/topology backbone where useful.

## Expected review artifact

`Z:\AI\RogueliteCharacterPipeline\g3r\g3r_contact_sheet.png`

It is a `4 columns × 3 rows` comparison:

- columns = four real walk phases;
- row D = outlined 4-band;
- row E = edge-preserving cluster;
- row F = selective contour cluster.

Stop after review artifact generation. Do not start G4 automatically.
