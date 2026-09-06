# G3S-B4 — Hair Layer

Status date: **2026-09-06**

Gate status: **OPEN/CURRENT — STATIC HAIR LAYER NOT YET APPROVED**

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

The Exilada's hair is:

- black;
- very long;
- heavy;
- voluminous;
- messy;
- a primary silhouette anchor;
- materially consistent with deprivation/survival rather than salon styling.

Identity/design authority:

`assets/source/characters/exilada/reference/exilada_master.png`

The master defines hair identity and mass, but does not automatically own final gameplay hair pixels if it is not already at the production raster/pose.

## Ownership rule

Hair is a separate persistent 2D layer family.

It may own:

- visible hair RGB/alpha/silhouette;
- front/back hair masses;
- stable attachment to head/upper body;
- later secondary-motion segmentation/guide anchors;
- later wind/physics response metadata.

It may not:

- replace body pixels permanently;
- require a censored or incomplete body beneath it;
- be regenerated independently per animation frame;
- use hidden-3D RGB/masks as final visible art;
- require manual frame-by-frame repainting by the user.

## First B4 deliverable

One **static front-three-quarter gameplay hair layer** aligned to the promoted B3B V4 body base.

Review package must show:

1. body base alone;
2. hair layer alone on transparency;
3. body + hair composite at enlarged nearest-neighbor review scale;
4. body + hair at native `640×360` gameplay context;
5. front/back ownership split or equivalent depth metadata if required by the silhouette.

## Visual PASS requirements

At native scale the hair must:

- immediately restore the Exilada's large dark silhouette anchor;
- read as very long/heavy/voluminous/messy rather than a generic bob/ponytail;
- preserve a severe adult sword-and-sorcery presence;
- maintain readable head/neck/shoulder/body separation;
- avoid a single featureless black blob;
- avoid fine strand noise that collapses at 1×;
- use deliberate pixel clusters/value grouping;
- remain compatible with later deterministic secondary motion.

## Structural PASS requirements

- hair is a separate transparent asset/layer;
- body asset remains byte/pixel unchanged;
- stable anchor/ownership metadata exists;
- no clothing/restraint pixels are introduced;
- no hidden-3D visible ownership;
- no per-frame generative dependency;
- no manual user repainting dependency.

## Current exact action

Before writing a B4 production runner, inspect the canonical identity master and promoted body base together and choose the smallest valid hair-layer construction method that preserves true 2D visible ownership.

No external paid API is authorized by default. PixelLab remains historical/closed for this project state.

No B5 clothing/restraints/accessories and no G3S-C layered motion begins before B4 PASS.
