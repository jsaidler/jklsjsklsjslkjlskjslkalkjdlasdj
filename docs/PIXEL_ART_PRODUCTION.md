# Pixel Art Production — Living Document

Status: **true modern pixel art remains the final gameplay target. The direct hidden-3D -> visible pixel-renderer route failed at G3V and is closed. Hidden 3D remains motion/topology/guide infrastructure only. The active production architecture is persistent structured 2D pixel assets animated/deformed from hidden rig guides, with runtime/export remaining sprite-based.**

Canonical end-to-end roadmap:

`docs/CHARACTER_PRODUCTION_PIPELINE.md`

Current visible-representation gate:

`docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`

## Core distinction

The project uses two visual reference layers:

1. **Identity master** — who the Exilada is.
2. **Production Pixel Master / persistent 2D production assets** — how she exists on the actual gameplay pixel grid.

Identity master:

`assets/source/characters/exilada/reference/exilada_master.png`

It must not be converted into the final sprite merely by resize, quantization or a superficial pixel-style postprocess.

## Locked visual target

Final gameplay art uses **true modern pixel art**:

- deliberate native-grid construction;
- readable silhouettes and connected pixel clusters;
- controlled palette/value grouping;
- material separation through authored 2D shapes/layers;
- stable animation at actual gameplay scale;
- mature, severe, physical sword-and-sorcery presentation;
- no dependence on illustrative microtexture.

References such as Conan, Frank Frazetta, Heavy Metal, Red Sonja and Julie Bell inform physicality, mass and adult fantasy shape language; they are translated into gameplay raster design rather than copied as paintings.

## Visible-ownership invariant — LOCKED AFTER G3V

G3V proved that even technically correct continuous 3D anatomy + semantic/palette translation still read as low-resolution 3D.

Therefore hidden 3D is **demoted from visible-image ownership**.

Hidden 3D may provide:

- motion;
- persistent topology;
- left/right identity;
- projected joints;
- sockets/attachments;
- depth/occlusion guides;
- physics;
- semantic/anatomical guides;
- secondary-motion driving data.

Hidden 3D may **not** provide the final visible sprite by mechanically promoting its render or projection.

Final visible RGB, alpha, silhouette, pixel clusters, palette/value grouping and edge treatment are owned by persistent 2D pixel assets.

Runtime/export remains sprite-based.

## Rejected final-art routes

### High-resolution image generation -> resize/quantize

**FAIL/CLOSED as final Production Pixel Master route.**

High-resolution generation may remain useful for concept/identity/reference work, but it cannot establish final pixel clusters, palette, gameplay readability or temporal raster stability.

### Conventional 3D beauty render -> generic pixel filter

**FAIL/CLOSED.**

A hidden 3D rig may own topology/motion, but a smooth conventional render merely downsampled/pixelated is not sufficient.

### 3D semantic/mask projection -> recolored final sprite

**FAIL/CLOSED after G3V and B3B V1 correction.**

Even if lit RGB is not copied, using a projected 3D mask directly as final sprite alpha/silhouette still leaves 3D as visible-image owner.

A 3D mask may be used only as a guide/reference/sanity check, not as the final 2D shape template.

### Primitive Python/Pillow artistic mannequin authoring

**FAIL visually as final character drawing.**

Python remains valid for deterministic raster processing, palette checks, masks, QA, packing, metadata and explicit operations on already-authored 2D assets. It must not invent the final human silhouette/anatomy procedurally and call that production art.

## Gameplay projection and scale

Locked baseline:

- elevated 2D belt-scroller / false 3D;
- native scene raster `640×360`;
- orthographic camera;
- pitch `26 deg`;
- protagonist reference height approximately `128 px`.

Pixel art is judged at native 1× and in gameplay context.

## Active production architecture — G3S

`real motion -> validated hidden rig -> projected joints/depth/sockets/guides -> persistent native 2D pixel assets -> deterministic 2D deformation/composition -> sprite/runtime export -> QA`

The crucial distinction is that the hidden rig provides control data while the persistent 2D assets provide visible art.

### Persistent 2D ownership

The character is assembled from persistent 2D assets/layers:

1. complete nude/hairless body base;
2. hair;
3. underlayers/soft clothing;
4. outer clothing;
5. armor;
6. restraints/accessories;
7. weapons/tools;
8. body/material state overlays;
9. transient VFX.

The body exists completely under every removable layer.

### 2D animation role of hidden rig

The rig may drive:

- part transforms;
- deformation guides;
- left/right identity;
- depth ordering;
- socket positions;
- contacts/root motion;
- secondary-motion targets.

But the final rendered frame is composed from the persistent 2D sprites/assets, not from a visible 3D render.

## Production Pixel Master — current definition

No final Production Pixel Master is yet approved.

The first approved native gameplay-scale Exilada body/character representation must be a genuine 2D pixel asset whose visible silhouette and pixel language are independently authored in 2D.

It is judged at 1× on:

- silhouette;
- adult anatomy;
- hair mass when present;
- palette/value grouping;
- cluster quality;
- recognizability against `exilada_master.png`;
- absence of low-resolution/filtered 3D appearance;
- suitability for persistent part decomposition and deterministic 2D animation.

## Current body-source gate — G3S-B3

The current build order is:

1. complete adult nude/hairless body sprite source;
2. separate hair asset;
3. separate clothing/bindings/restraints/accessories;
4. layered motion proof.

### B3A

B3A V2 passed as an adult-female MPFB anatomy guide only.

Its render, mask and projected silhouette are not final art.

### B3B V1 correction

A first B3B implementation was rejected because it copied the projected B3A mask directly into the final `128×128` alpha/silhouette and procedurally colored it.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v1_route_failure.json`

The rejected script/runner were removed before user execution.

The corrected B3B method has not yet been implemented.

## Temporal pixel-art gate

A convincing still is insufficient.

After body/hair/clothing ownership is correct, the same persistent 2D representation must survive a motion proof and later a stress pack containing:

- locomotion;
- an extreme/high-energy action;
- an impact/compressed/recovery action.

QA examines:

- silhouette readability;
- limb separation;
- stable part ownership;
- one-frame orphan-pixel noise;
- material-cluster stability;
- sprite-bound overflow;
- contact/action readability;
- whether motion feels intentionally sprite-animated rather than like low-resolution rendered 3D.

## Character identity priorities at gameplay scale

1. dominant long black hair mass when hair is present;
2. adult lean/compact anatomy;
3. severe physical presence;
4. clear skin/hair value separation;
5. asymmetrical degraded beige cloth when equipped;
6. readable limbs and grounded bare feet;
7. restraint-history markers where legible;
8. facial microdetail last.

Weapons remain variable equipment, not identity anchors.

## Persistent detail and accessory strategy

Details that must remain on the same body side are encoded structurally rather than redrawn per frame:

- scars/marks: body-owned 2D masks/details where useful;
- shackles: separate socketed 2D equipment assets;
- chains: persistent endpoint-connected accessory structures rendered/composed as 2D assets;
- hair: persistent large 2D masses with deterministic secondary-motion guides;
- cloth: persistent 2D pieces/layers;
- weapons/equipment: named rig sockets driving 2D asset placement.

## Systemic visual state

The pixel pipeline must expose stable body/material masks so causal world state does not require reauthoring frames.

Planned examples:

- blood/injury;
- dirt/mud;
- wetness;
- frost/burn;
- material wear;
- selected persistent scars;
- weather/lighting palette variation.

## Runtime integrity

Final production sprites must use:

- nearest-neighbor scaling;
- stable/integer positioning where required for raster stability;
- no bilinear filtering;
- no antialiased transform bake;
- no arbitrary rotation of finished bitmaps unless a specifically validated pixel-safe deformation path is used;
- stable world scale across frames.

## Automated QA / export role

Python and other CLI tooling may automatically validate:

- dimensions;
- palette membership/count;
- alpha integrity;
- singleton pixel noise thresholds;
- silhouette-area discontinuities;
- part discontinuities;
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

**LOCKED:** direct 3D projection/mask -> recolored final sprite is rejected.

**LOCKED:** hidden deterministic 3D may own motion/topology/guides internally but not final visible silhouette/RGB.

**ACTIVE:** persistent structured 2D sprites/assets own final visible character art.

**NEXT:** define the corrected G3S-B3B method for one genuine native `128×128` nude/hairless 2D body source before writing or running another authoring script.
