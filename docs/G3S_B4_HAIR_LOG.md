# G3S-B4 — Hair Layer

Status date: **2026-09-06**

Gate status: **OPEN/CURRENT — STATIC HAIR LAYER FAMILY NOT YET APPROVED**

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

## Hair depth architecture — LOCKED

The hair is **not one flat overlay**. It is a persistent 2D layer family with **at least two mandatory depth layers**:

1. **rear/back hair mass** — composited behind the body/head/shoulders;
2. **front hair mass** — composited in front of the body/head/shoulders where strands/masses cross the face, neck, chest or shoulders.

Canonical minimum composition:

`rear_hair -> body -> front_hair`

This front/back split is structural, not merely a contact-sheet convenience. It is required so long hair can wrap around the silhouette, cross shoulders/chest, survive animation and later respond to depth/secondary-motion guides without being baked into the body.

Additional side/intermediate hair pieces are allowed later if required by occlusion or secondary motion, but **two layers is the minimum valid B4 representation**.

Each hair layer must have stable semantic ownership and may later be subdivided into motion masses/segments without changing body ownership.

## Ownership rule

Hair is a separate persistent 2D layer family.

It may own:

- visible hair RGB/alpha/silhouette;
- mandatory rear/back and front hair masses;
- optional side/intermediate masses when needed;
- stable attachment to head/upper body;
- later secondary-motion segmentation/guide anchors;
- later wind/physics response metadata;
- layer-local depth/occlusion behavior.

It may not:

- replace body pixels permanently;
- require a censored or incomplete body beneath it;
- collapse all hair into one irreversible body-baked sprite;
- be regenerated independently per animation frame;
- use hidden-3D RGB/masks as final visible art;
- require manual frame-by-frame repainting by the user.

## First B4 deliverable

One **static front-three-quarter gameplay hair layer family** aligned to the promoted B3B V4 body base.

Review package must show:

1. body base alone;
2. rear/back hair layer alone on transparency;
3. front hair layer alone on transparency;
4. rear hair + body + front hair composite at enlarged nearest-neighbor review scale;
5. same composite at native `640×360` gameplay context;
6. explicit ownership/depth metadata for both mandatory hair layers;
7. optional extra side/intermediate pieces only if actually required.

## Visual PASS requirements

At native scale the hair must:

- immediately restore the Exilada's large dark silhouette anchor;
- read as very long/heavy/voluminous/messy rather than a generic bob/ponytail;
- preserve a severe adult sword-and-sorcery presence;
- maintain readable head/neck/shoulder/body separation;
- convincingly occupy both rear and front depth where the design requires it;
- avoid a single featureless black blob;
- avoid fine strand noise that collapses at 1×;
- use deliberate pixel clusters/value grouping;
- remain compatible with later deterministic secondary motion.

## Structural PASS requirements

- rear hair and front hair exist as separate transparent persistent assets/layers;
- body asset remains byte/pixel unchanged;
- stable anchor/ownership/depth metadata exists;
- composition order can reproduce `rear_hair -> body -> front_hair` deterministically;
- no clothing/restraint pixels are introduced;
- no hidden-3D visible ownership;
- no per-frame generative dependency;
- no manual user repainting dependency.

## Current exact action

Before writing a B4 production runner, inspect the canonical identity master and promoted body base together and implement the smallest valid **two-layer minimum** static hair representation: rear mass + front mass. Add further sublayers only if the silhouette/occlusion actually requires them.

No external paid API is authorized by default. PixelLab remains historical/closed for this project state.

No B5 clothing/restraints/accessories and no G3S-C layered motion begins before B4 PASS.
