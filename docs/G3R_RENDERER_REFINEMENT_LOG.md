# G3R Renderer / Style Refinement — Execution Log

Status date: **2026-09-05**

Gate: **G3R — deterministic pixel renderer/style refinement**

Current status: **FAIL / CLOSED. Do not iterate more renderer-only variants on the primitive mannequin.**

## Why G3R existed

G3 proved that the deterministic hidden-3D backbone can become a stable native-grid sprite under real captured motion, but the first visible methods were not production art. G3R tested whether stronger palette bands, contour rules and cluster cleanup were enough to turn the same semantic proxy into an intentional modern pixel-art character.

Locked upstream baseline:

- native raster: `640×360`;
- orthographic pitch: `26 deg`;
- protagonist reference height: `128 px`;
- real source motion: approved G2 CMU `105_34 NormalWalk` sequence.

## Reviewed artifact

`Z:\AI\RogueliteCharacterPipeline\g3r\g3r_contact_sheet.png`

Compared four real walk phases through:

- **D — outlined 4-band**;
- **E — edge-preserving cluster**;
- **F — selective contour cluster**.

## Result

All three variants remain recognizably the same technical mannequin. D/E/F alter contour/value handling but do not create the missing authored information: human surface anatomy, believable silhouette design, face/head structure, real hair mass, cloth shape, restraints, material-specific form language or identity-bearing detail.

The central correction is architectural:

**post-processing cannot invent visual information that the source representation does not contain.**

The primitive G3 proxy was useful to prove motion/topology/raster determinism. It is not a valid proxy for judging whether a real character asset can produce the intended final pixel language.

Therefore:

- G3/G3R do **not** approve the current visible renderer as production art;
- G3R does **not** justify additional outline/cluster/palette tuning on the mannequin;
- G4 Exilada production geometry remains blocked;
- the G2 deterministic motion/topology backbone remains valid and retained.

## What was learned

Renderer-only refinement reached diminishing returns because the source mesh carried almost no authored form. The next test must add a representative continuous human surface and a minimal set of identity-bearing structures before judging the 3D→pixel translation again.

## Next gate — G3V representative visual proxy

The next visual kill switch is **G3V**, not another renderer variant.

G3V must use a script-created continuous human mesh with real body topology and rigging, while still avoiding expensive Exilada production work.

Current preferred candidate: **MakeHuman/MPFB core assets**, because MPFB exposes scriptable human creation/rig services and its core assets are permissively usable/CC0. The project will validate this headlessly before depending on it.

Minimal G3V representation:

1. lean adult female continuous body mesh;
2. real deformation rig/weights;
3. large long-hair mass;
4. simple degraded cloth mass;
5. wrist/ankle metal restraint markers;
6. bare feet;
7. approved G1 camera/scale;
8. one still plus a short sample of the approved real walk;
9. the deterministic pixel renderer applied to this materially richer source.

This is deliberately **not** the finished Exilada. It is only rich enough to answer the actual question: can a coherent human asset with intentional silhouette/material structure survive the hidden-3D→pixel translation?

## G3V kill switch

G3V fails the visible hidden-3D route if either:

- the representative human proxy still reads primarily as filtered/low-resolution 3D rather than intentional pixel art; or
- creating/rigging/retargeting the representative asset cannot be automated headlessly within the project's operator constraint.

If G3V fails, retain the deterministic 3D rig as motion/reference infrastructure only and move the visible character representation to a structured 2D solution. Do not build the Exilada production model first.
