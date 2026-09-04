# Pixel Art Production — Living Document

Status: **true modern pixel art remains the final gameplay target. Direct high-resolution diffusion -> resize/quantize remains rejected. The active production plan now validates a deterministic hidden-rig -> native semantic passes -> pixel-specific renderer route before building the Exilada production model or animation library.**

Canonical end-to-end roadmap:

`docs/CHARACTER_PRODUCTION_PIPELINE.md`

## Core distinction

The project uses two visual reference layers:

1. **Identity master** — who the Exilada is.
2. **Production Pixel Master** — how she exists on the actual gameplay pixel grid.

Identity master:

`assets/source/characters/exilada/reference/exilada_master.png`

It must not be converted into the final sprite merely by resize, quantization or a superficial pixel-style postprocess.

## Locked visual target

Final gameplay art uses **true modern pixel art**:

- deliberate native-grid construction;
- readable silhouettes and connected pixel clusters;
- controlled palette/value grouping;
- material separation through authored/render-rule shapes;
- stable animation at actual gameplay scale;
- mature, severe, physical sword-and-sorcery presentation;
- no dependence on illustrative microtexture.

References such as Conan, Frank Frazetta, Heavy Metal and Julie Bell inform physicality, mass and adult fantasy shape language; they are translated into gameplay raster design rather than copied as paintings.

## Rejected final-art routes

### High-resolution image generation -> resize/quantize

**FAIL as final Production Pixel Master route.**

High-resolution generation may remain useful for concept/identity/reference work, but it cannot establish final pixel clusters, palette, gameplay readability or temporal raster stability.

### Conventional 3D beauty render -> generic pixel filter

**FAIL as final-art definition.**

A hidden 3D rig may own topology/motion, but a smooth conventional render merely downsampled/pixelated is not sufficient.

### Primitive Python/Pillow artistic authoring

**FAIL visually as character drawing.**

Python remains valid for deterministic semantic raster processing, palette logic, masks, QA, packing and export. Under the new plan Python does not invent anatomy or draw a mannequin; it processes stable rig-derived semantic data.

## Gameplay projection and scale dependency

Locked baseline:

**elevated 2D belt-scroller / false 3D**

Before the final pixel renderer or Production Pixel Master is designed, G1 of `CHARACTER_PRODUCTION_PIPELINE.md` must determine the real native pixel density from a representative gameplay composition.

Provisional scene raster:

**640 × 360** — test value only, not locked.

Candidate protagonist heights such as 112 / 128 / 144 px remain comparison samples only.

The final renderer must be tuned to the chosen gameplay scale; pixel art cannot be designed correctly in isolation from screen occupancy and combat composition.

## Planned native-raster translation architecture

Primary candidate:

`hidden deterministic rig -> exact-density semantic passes -> pixel-specific renderer -> indexed native sprite`

### Rig-derived semantic inputs

At the exact pixel density established by gameplay-scale testing, the hidden 3D production structure will provide:

- silhouette/coverage;
- body-part ID;
- material ID;
- view-space normals;
- depth;
- stable UV/detail masks;
- attachment/socket metadata;
- optional unlit diagnostic reference.

These are machine-readable construction inputs, not a final smooth 3D artwork.

### Pixel-specific renderer rules

The visible sprite is constructed directly on the target grid using:

- discrete indexed palette ramps per material;
- large connected value clusters before small accents;
- controlled silhouette/edge treatment rather than a universal black sticker outline;
- material-specific shape/value language for hair, skin, cloth and metal;
- stable UV-anchored persistent details such as scars/tears where they remain legible;
- no smooth-gradient dependence;
- no automatic dithering as default;
- no random speckling/texture noise;
- no bilinear filtering;
- no antialiasing baked into production sprites;
- no arbitrary rotation of finished bitmaps.

Initial Exilada guidance remains approximately **24–32 visible base colors**, excluding transparency and optional runtime state data. This is guidance, not a quota.

## Why this is not simply filtered 3D

The visual route passes only if its result reads as deliberate pixel art at native 1×.

The distinction is structural:

- 3D supplies topology, projection, occlusion and semantic/material information;
- the final visible colors/edges/value bands are chosen by pixel-specific discrete rules at the final raster;
- there is no accepted intermediate conventional high-resolution beauty frame that is merely reduced afterward.

If the result still reads as low-resolution/filtered 3D, **G3 fails and the visible renderer is abandoned before a detailed Exilada model is built**.

## Production Pixel Master — revised definition

No Production Pixel Master is currently approved.

After G1 scale and G3 renderer feasibility pass, a low-detail Exilada production proxy is mapped into the same system.

The first static native-grid Exilada image that passes user review for:

- silhouette;
- long black hair mass;
- adult lean anatomy;
- severe presence;
- skin/hair/cloth/metal separation;
- controlled clusters/palette;
- recognizability against `exilada_master.png`;
- absence of filtered-3D appearance;

becomes the **Production Pixel Master**.

It is therefore generated by the accepted deterministic production representation, not painted as an unrelated one-off asset and not obtained by shrinking the identity master.

## Temporal pixel-art gate

A convincing still is insufficient.

Before an animation library is produced, the same renderer must survive a stress pack containing:

- locomotion;
- an extreme/high-energy action;
- an impact/compressed/recovery action.

QA examines:

- silhouette readability;
- limb separation;
- one-frame orphan-pixel noise;
- material-cluster stability;
- sprite-bound overflow;
- contact/action readability;
- whether frame sampling feels intentionally animated rather than smoothly rendered 3D.

Mocap can be resampled/baked to a lower sprite cadence, but frame selection must respect contacts and motion error rather than using only a blind `every Nth frame` rule.

## Character identity priorities at gameplay scale

1. dominant long black hair mass;
2. adult lean/compact anatomy;
3. severe physical presence;
4. clear skin/hair value separation;
5. asymmetrical degraded beige cloth;
6. readable limbs and grounded bare feet;
7. restraint-history markers where legible;
8. facial microdetail last.

Weapons remain variable equipment, not identity anchors.

## Persistent detail and accessory strategy

Details that must remain on the same body side are encoded structurally rather than redrawn per frame:

- scars/tears: stable UV/material masks or geometry where useful;
- shackles: separate socketed objects;
- chains: persistent endpoint-connected structures;
- hair: rigged large geometry masses with deterministic secondary motion;
- cloth: persistent mesh/secondary structures;
- weapons/equipment: named rig sockets.

This prevents the frame-to-frame migrations observed in diffusion experiments.

## Modular equipment pixel strategy

The preferred scalable route is not to pre-render every possible equipment combination.

Plan:

- render base character and equipment through the same rig/camera/pixel renderer;
- export depth/occlusion or front/back ordering information from the deterministic scene;
- compose equipment modularly with correct per-frame occlusion;
- validate one representative weapon/restraint combination before an equipment catalog is created.

If depth-aware modular composition is impractical in the game runtime, G6 must discover that early and choose a controlled front/back-layer or offline-composite family solution before content multiplication.

## Systemic visual state

The pixel pipeline must expose stable material/body masks so causal world state does not require reauthoring frames.

Planned examples:

- blood/injury;
- dirt/mud;
- wetness;
- frost/burn;
- material wear;
- selected persistent scars;
- weather/lighting palette variation.

If normal data is retained for runtime lighting, lighting must resolve through discrete palette/value rules rather than smooth non-pixel gradients.

## Runtime integrity

Final production sprites must use:

- nearest-neighbor scaling;
- stable/integer positioning where required for raster stability;
- no bilinear filtering;
- no antialiased transform bake;
- no arbitrary rotation of finished bitmaps;
- stable world scale across frames.

## Automated QA / export role

Python and other CLI tooling may automatically validate:

- dimensions;
- palette membership/count;
- alpha integrity;
- singleton pixel noise thresholds;
- silhouette-area discontinuities;
- material/part discontinuities;
- attachment continuity;
- bounds overflow;
- loop closure;
- deterministic hashes.

The pipeline must automatically generate native-1× previews/contact sheets/debug masks so the user's job is visual approval, not software operation.

## Current decision / next gate

**LOCKED:** final visible art remains true modern pixel art.

**LOCKED:** `exilada_master.png` remains the high-detail identity/design master, not the final sprite.

**LOCKED:** direct high-res generation -> resize/quantize is rejected.

**LOCKED:** conventional beauty-render -> generic pixel filter is rejected.

**LOCKED:** hidden deterministic 3D may own topology/motion internally.

**ACTIVE VISUAL CANDIDATE:** exact-density semantic passes -> purpose-built native pixel renderer.

**ANTI-WASTE RULE:** G3 must prove this visual translation on a cheap generic proxy **before** a detailed Exilada model or animation library is built.

**NEXT IMPLEMENTATION SEQUENCE:** G0 headless automation -> G1 camera/scale -> G2 real motion/topology -> G3 native-pixel renderer proof.
