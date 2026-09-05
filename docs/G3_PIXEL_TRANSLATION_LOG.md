# G3 Native Pixel Translation — Execution Log

Status date: **2026-09-05**

Gate: **G3 — deterministic hidden-3D to native-grid pixel-art feasibility**

Current status: **PASS TECHNICAL / PRODUCTION LOOK NOT APPROVED. G3R CLOSED FAIL.**

## Purpose

G3 was the early visual kill switch intended to prevent detailed Exilada production work before proving that the deterministic 3D backbone could produce a usable visible 2D pixel result.

G3 did not use the Exilada production model. It used a deliberately simple stylized semantic humanoid proxy driven by the approved G2 real-motion rig.

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

- deterministic hidden-3D motion/topology can be rendered into a stable native-grid 2D sprite representation;
- semantic material families remain controllable;
- no diffusion or frame-by-frame reconstruction is required for that deterministic translation;
- the visible renderer can be changed independently of the approved G2 motion/topology backbone.

However, none of A/B/C was approved as final production look.

Observed limitation:

- the result still read primarily as a technical mannequin / processed low-detail 3D proxy;
- outline authority, cluster discipline and material-specific visual language were insufficient;
- therefore proceeding directly to detailed Exilada geometry still carried unacceptable visual risk.

Decision:

**G3 passes as technical architecture evidence, but production rendering remains unproven.**

Canonical decision marker:

`tools/deterministic-character-pipeline/g3_technical_approval.json`

## 2026-09-05 correction — old four-frame subset was not phase-diverse

G3 selected G2 sample indices `(0,3,6,9)`. G2 itself produced 12 evenly spaced samples across the selected real-motion window. During G3V semantic diagnostics, the inherited frame set was observed as:

`1563, 1612, 1661, 1710`

These are exactly 49 frames apart and produced identical semantic counts in G3V, revealing that the fixed every-third-sample selection can alias the captured walk period and repeatedly hit the same gait phase.

Therefore the earlier G3 wording **"gait/topology continuity is preserved across sampled frames"** was too strong for the four-frame G3 subset and is withdrawn.

What remains valid:

- G2's full 12-sample sequence and topology review remain the authoritative evidence for real motion and sequence continuity;
- G3's visual-style conclusion remains valid because it concerned the primitive proxy / pixel-translation language, not proof of four distinct gait phases;
- G3R's rejection of renderer-only refinement also remains valid for the same reason.

For G3V and later representative-character review, four frames are now selected from a **contact-derived measured gait period at quarter-cycle offsets**, not fixed G2 sample indices.

## Downstream status

G3R subsequently failed as a production-look route on the primitive mannequin. The active visual gate is now G3V, using a continuous MPFB human proxy plus deterministic semantic/pixel translation.
