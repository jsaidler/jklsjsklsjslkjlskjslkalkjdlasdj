# G3S — Structured 2D Visible Representation

Status date: **2026-09-05**

Gate status: **PLANNED / IMPLEMENTATION NEXT**

## Why G3S exists

G3V-R proved that real CMU motion can be transferred deterministically into the MPFB humanoid without topology collapse. The final G3V body rerun then proved that this technical backbone is stable enough to animate a representative human.

However the visual kill switch failed: the native semantic/palette output still reads as conventional 3D made coarse/blocky rather than intentional modern pixel art.

Therefore the project keeps hidden 3D only as infrastructure and moves ownership of the visible character to a structured 2D representation.

Canonical failure marker:

`tools/deterministic-character-pipeline/g3v_failure.json`

## Locked architectural decision

Hidden 3D may own:

- real motion;
- persistent topology and left/right identity;
- attachment sockets;
- root/contact data;
- physics proxies;
- depth/occlusion guides;
- semantic/body-part guides;
- secondary-motion driving data.

Hidden 3D may **not** own the final visible color image by direct render/palette translation.

The visible layer must instead be authored as persistent 2D pixel assets at gameplay scale and driven deterministically by the validated motion backbone.

## Target architecture

`real motion -> validated hidden rig -> projected 2D joints/depth -> persistent 2D pixel parts -> deterministic transform/deformation -> depth-aware composition -> native sprite -> QA`

The visible representation is a 2D asset system, not a frame generator.

## Production constraints

- no per-frame diffusion as animation owner;
- no routine frame-by-frame repainting;
- no generic high-resolution render followed by shrink/quantization;
- no bilinear filtering;
- no arbitrary bitmap rotations in the final raster without pixel-aware resampling rules;
- one-time source-art creation/decomposition is acceptable if it removes recurring frame-by-frame work;
- the user must not need to operate Blender/Aseprite/Spine or rig manually;
- normal production remains scriptable/headless.

## G3S-A — static source sprite gate

Before attempting animation, create **one approved gameplay-scale Exilada source sprite** in the locked G1 presentation family.

Required characteristics:

- visible height approximately `128 px` at native raster;
- lateral / slight 3/4 gameplay presentation compatible with the belt-scroller camera;
- lean adult female anatomy;
- severe readable head silhouette;
- dominant very long black hair mass;
- degraded asymmetric beige cloth;
- wrist and ankle restraints;
- bare feet;
- no weapon;
- true pixel clusters authored/readable at native 1×;
- no anti-aliased pseudo-pixel edges;
- recognizably derived from `exilada_master.png` without treating the master as final gameplay art.

### Source-art route

The previously paused Qwen-Image-Edit-2509 tooling may return **only as a constrained one-time static source-art candidate**, because the reason it was paused was inability to prove temporal consistency. G3S no longer asks it to generate animation frames.

Any generative candidate is subject to topology/identity QA once and is not accepted automatically. If Qwen cannot produce a genuinely native-looking pixel source sprite, it is rejected for this role as well.

No direct-frame Qwen animation is permitted.

## G3S-B — persistent part decomposition

Once one static source sprite is approved, decompose it into persistent 2D pieces, for example:

- head/face;
- torso/pelvis;
- upper/lower arms and hands per side;
- upper/lower legs and feet per side;
- large hair masses;
- degraded cloth pieces;
- wrist/ankle metal restraints.

Exact part count is determined by deformation quality, not by arbitrary symmetry.

Each part owns:

- stable ID;
- anatomical side where applicable;
- pivot / joint anchors;
- draw-depth rules;
- optional local deformation mesh;
- material/palette family;
- attachment inheritance.

## G3S-C — four-phase walk proof

Drive the persistent 2D parts from the already validated quarter-cycle motion frames:

`1568, 1588, 1608, 1628`

The first animation proof must preserve the authored pixels rather than regenerate them.

Allowed operations:

- integer translation;
- constrained pixel-aware rotation/warp;
- deterministic local mesh deformation;
- authored joint-cover patches;
- deterministic depth ordering from hidden-rig guides.

No frame may be independently redrawn by a diffusion model.

## G3S PASS criteria

G3S passes only if:

1. the static source sprite itself reads as intentional modern pixel art at 1×;
2. major topology remains one head/torso, two arms/hands and two legs/feet across all four gait phases;
3. left/right ownership remains stable;
4. motion phase/grounding still corresponds to G2/G3V-R;
5. hair, cloth and restraints remain persistent rather than migrating or regenerating;
6. joints do not open into obvious cutout gaps or rubbery bitmap deformation;
7. visible pixels retain authored cluster language through motion;
8. the workflow remains headless/reproducible after the one-time source asset is approved.

## Kill switch

If a persistent 2D cutout/mesh system cannot preserve high-quality native pixel art through the walk without obvious puppet artifacts, do not multiply content. Reassess the visible-animation representation before G4/G5.

## G4 rescope

The old G4 assumption — building an Exilada 3D production proxy for direct pixel rendering — is closed.

After G3S passes, G4 becomes **Exilada production 2D identity system**: approved source sprite/parts, palette/material families, hair/cloth/restraint variants, sockets/occlusion metadata and damage-ready layering.

## Immediate implementation target

The next executable work should target **G3S-A only**: one static source-sprite spike using the exact canonical `exilada_master.png`, with topology/identity/native-pixel QA before any 2D animation/decomposition work begins.
