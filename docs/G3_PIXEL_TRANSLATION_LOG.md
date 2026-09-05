# G3 Native Pixel Translation — Execution Log

Status date: **2026-09-04**

Gate: **G3 — deterministic hidden-3D to native-grid pixel-art feasibility**

Current status: **READY TO RUN.**

## Purpose

G3 is the early visual kill switch. It exists specifically to prevent the project from spending days building detailed Exilada geometry, equipment and animation content before proving that the deterministic 3D backbone can produce an acceptable visible 2D pixel result.

G3 does **not** use the Exilada production model. It uses a deliberately simple stylized semantic humanoid proxy driven by the already approved G2 real-motion rig.

Locked upstream baseline:

- G1: `640×360`, orthographic pitch `26 deg`, protagonist reference height `128 px`;
- G2: PASS using CMU `105_34 NormalWalk` with deterministic persistent topology.

Canonical G2 approval marker:

`tools/deterministic-character-pipeline/g2_approval.json`

## Tooling

- `tools/deterministic-character-pipeline/03_run_g3.ps1`
- `tools/deterministic-character-pipeline/g3_pixel_translation.py`

The runner consumes the local successful G2 artifacts:

- `Z:\AI\RogueliteCharacterPipeline\g2\g2_motion_topology.blend`
- `Z:\AI\RogueliteCharacterPipeline\g2\g2_manifest.json`

and writes G3 under:

`Z:\AI\RogueliteCharacterPipeline\g3`

## Semantic proxy

The generic test proxy contains persistent categories needed by later production:

- skin;
- cloth;
- large dark hair mass;
- metal attachment markers.

The proxy is generated procedurally from the G2 rig and is intentionally crude as conventional 3D. G3 judges the visible raster strategy, not character modeling skill.

## Three visual strategies compared

Four representative G2 motion frames are rendered through three rows:

### A — native flat semantic

`640×360`, object-color semantic regions, flat Workbench render.

Purpose: control/reference showing the direct native-raster deterministic geometry without a specialized pixel-value treatment.

### B — palette-banded semantic

`640×360`, material-specific three-band palettes. Lighting value is converted into discrete face-level palette decisions; Workbench itself remains flat so smooth 3D gradients are not the visible language.

Semantic palette families:

- skin;
- cloth;
- hair;
- metal.

Purpose: first serious deterministic pixel-renderer candidate.

### C — palette-banded 2× cluster density

Same deterministic palette-banded strategy rendered at `320×180` and displayed at `640×360` only with nearest-neighbor scaling.

This is not a high-resolution render shrunk into pixel art. It tests whether a deliberately coarser semantic grid produces stronger intentional pixel clusters at the accepted gameplay presentation.

## Hard rules

- no diffusion/generative repainting;
- no high-resolution beauty render followed by generic pixel filter;
- no bilinear scaling;
- no final Exilada geometry;
- no manual frame repaint;
- same G2 motion/topology drives every method;
- same accepted camera family drives every method.

## PASS / FAIL review

G3 can PASS only if at least one non-control method reads as a credible foundation for **intentional modern pixel art**, rather than merely low-resolution 3D.

Review order:

1. silhouette readability at 1× gameplay scale;
2. body-part separation through movement;
3. material separation: skin / cloth / hair / metal;
4. large coherent pixel/value clusters;
5. absence of smooth filtered-3D appearance;
6. temporal consistency across the four sampled gait phases;
7. whether the result is credible enough to justify proceeding to Exilada identity mapping.

If neither B nor C is visually credible, G3 FAILS and the visible hidden-3D renderer route is rejected **before** detailed Exilada production geometry. The G2 rig may still survive as motion/reference infrastructure while a structured 2D representation is evaluated.

## Expected review artifact

`Z:\AI\RogueliteCharacterPipeline\g3\g3_contact_sheet.png`

It is a `4 columns × 3 rows` comparison:

- columns = four real walk phases;
- row A = native flat control;
- row B = palette-banded native 1×;
- row C = palette-banded coarse 2× cluster candidate.

Do not start G4 until this sheet is visually reviewed and G3 is explicitly recorded PASS.
