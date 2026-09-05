# G3 Native Pixel Translation — Execution Log

Status date: **2026-09-04**

Gate: **G3 — deterministic hidden-3D to native-grid pixel-art feasibility**

Current status: **PASS TECHNICAL / PRODUCTION LOOK NOT APPROVED. G3R REQUIRED.**

## Purpose

G3 is the early visual kill switch. It exists specifically to prevent the project from spending days building detailed Exilada geometry, equipment and animation content before proving that the deterministic 3D backbone can produce a usable visible 2D pixel result.

G3 does not use the Exilada production model. It uses a deliberately simple stylized semantic humanoid proxy driven by the approved G2 real-motion rig.

Locked upstream baseline:

- G1: `640×360`, orthographic pitch `26 deg`, protagonist reference height `128 px`;
- G2: PASS using CMU `105_34 NormalWalk` with deterministic persistent topology.

## Tooling executed

- `tools/deterministic-character-pipeline/03_run_g3.ps1`
- `tools/deterministic-character-pipeline/g3_pixel_translation.py`

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3\g3_contact_sheet.png`

## Methods reviewed

### A — native flat semantic

Direct native semantic control. Useful for debug/masks but not a production-art candidate.

### B — palette-banded semantic

Material-specific discrete palette bands at native `640×360`. This was the strongest technical visual baseline in the first G3 pass.

### C — palette-banded 2× cluster

Coarser `320×180` semantic rendering displayed at `640×360` by nearest-neighbor scaling. It increased coarse clustering but did not by itself establish a production-quality pixel-art language.

## Visual QA result

G3 proved:

- deterministic hidden-3D motion/topology can become a stable native-grid 2D sprite;
- gait/topology continuity is preserved across sampled frames;
- semantic material families remain controllable;
- no diffusion or frame-by-frame reconstruction is required;
- the renderer can be changed independently of motion/topology.

However, none of A/B/C is approved as final production look.

Observed limitation:

- the result still reads primarily as a technical mannequin / processed low-detail 3D proxy;
- outline authority, cluster discipline and material-specific visual language are insufficient;
- therefore proceeding directly to detailed Exilada geometry would still carry unacceptable visual risk.

Decision:

**G3 passes as technical architecture evidence, but production rendering remains unproven. G4 is blocked.**

Canonical decision marker:

`tools/deterministic-character-pipeline/g3_technical_approval.json`

## Next gate

`G3R — renderer / style refinement`

Canonical log:

`docs/G3R_RENDERER_REFINEMENT_LOG.md`

G3R refines the visible deterministic pixel language before any Exilada production geometry is built.
