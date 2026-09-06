# G3S-B4 — Hair Layer

Status date: **2026-09-06**

Gate status: **OPEN/CURRENT — TWO-LAYER HAIR PREFLIGHT RUNNER READY**

## Entry condition

G3S-B3/B3B is PASS/CLOSED.

Canonical body base:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`
- promotion commit `2deb765c3980d586ef9747340bb48852dedca452`;
- `37×128` RGBA;
- visible standing height `128 px`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`.

The body base is immutable input to B4. Hair must not be baked into or overwrite body ownership.

## Canonical hair identity

The Exilada's hair is black, very long, heavy, voluminous, messy and a primary silhouette anchor. It must read as deprivation/survival material, not salon styling.

Identity/design authority:

`assets/source/characters/exilada/reference/exilada_master.png`

The master defines hair identity/mass only. It is a local reference asset and is not currently tracked in GitHub; therefore B4 must inspect it through the local runner rather than pretend GitHub contains the pixels.

## Hair depth architecture — LOCKED

Hair is **not one flat overlay**. Minimum valid representation:

1. `rear_hair` — behind body/head/shoulders;
2. `front_hair` — in front where masses cross face/neck/chest/shoulders.

Minimum deterministic composition:

`rear_hair -> body -> front_hair`

Additional side/intermediate pieces are allowed later if required by occlusion or secondary motion, but two layers is the structural minimum.

## Ownership rule

Hair is a separate persistent 2D layer family. It may own visible hair RGB/alpha/silhouette, front/back masses, stable attachment/depth metadata and later secondary-motion anchors. It may not modify the body asset, collapse into one irreversible body-baked sprite, use hidden-3D RGB/masks as final visible art, require per-frame generation or require manual user repainting.

## First B4 production deliverable

One static front-three-quarter gameplay hair family aligned to the promoted B3B body:

- `rear_hair` transparent asset;
- `front_hair` transparent asset;
- body alone;
- each hair layer alone;
- deterministic composite;
- enlarged nearest-neighbor review;
- native `640×360` preview;
- stable ownership/depth metadata.

## B4A preflight — CURRENT

Before authoring final hair pixels, the canonical local master and immutable body must be inspected side-by-side because the master is not present in GitHub.

Helper:

`tools/structured-2d-character-pipeline/g3s_b4_hair_preflight.py`

Runner:

`tools/structured-2d-character-pipeline/16_run_g3s_b4_hair_preflight.ps1`

Output directory:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4_hair_preflight`

Primary review artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4_hair_preflight\g3s_b4_hair_preflight_contact_sheet.png`

The preflight:

1. verifies the promoted B3B body by file SHA, raw-RGBA SHA and exact `37×128` dimensions;
2. verifies the local canonical `exilada_master.png` exists and records its SHA/dimensions;
3. places the immutable body on a provisional shared `96×160` diagnostic canvas with ground anchor `y=152`;
4. shows the master, body and explicit `rear_hair -> body -> front_hair` depth contract in one contact sheet;
5. creates **no production hair pixels** and performs no automatic promotion.

The `96×160` canvas is provisional only. It may change after inspecting the actual master/body relationship.

## Visual PASS requirements for later hair candidate

At native scale hair must immediately restore the Exilada's large dark silhouette anchor; read as very long/heavy/voluminous/messy; preserve head/neck/shoulder/body readability; occupy front and rear depth convincingly; avoid both featureless black blobs and fine-strand noise; use deliberate pixel clusters/value grouping; and remain compatible with deterministic secondary motion.

## Structural PASS requirements for later hair candidate

- rear/front hair are separate transparent persistent assets;
- body asset remains byte/pixel unchanged;
- stable anchor/ownership/depth metadata exists;
- deterministic composition reproduces `rear_hair -> body -> front_hair`;
- no clothing/restraint pixels;
- no hidden-3D visible ownership;
- no per-frame generative dependency;
- no manual user repainting dependency.

## Current exact action

Run B4A preflight once and share the contact sheet. Only after inspecting that artifact should the first static two-layer hair candidate be authored.

No external paid API is authorized by default. PixelLab remains historical/closed. B5 and G3S-C remain blocked until B4 PASS.
