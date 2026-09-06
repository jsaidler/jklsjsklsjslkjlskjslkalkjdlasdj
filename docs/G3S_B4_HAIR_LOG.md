# G3S-B4 — Hair Layer

Status date: **2026-09-06**

Gate status: **B4A PREFLIGHT PASS/CLOSED — B4B TWO-LAYER STATIC REVIEW RUNNER READY**

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

The master defines hair identity/mass. It is a local pixel-art reference asset and is not currently tracked in GitHub, so B4 operates on it locally and records its SHA through the preflight metadata.

## Hair depth architecture — LOCKED

Hair is **not one flat overlay**. Minimum valid representation:

1. `rear_hair` — behind body/head/shoulders;
2. `front_hair` — in front where masses cross face/neck/chest/shoulders.

Minimum deterministic composition:

`rear_hair -> body -> front_hair`

Additional side/intermediate pieces are allowed later if required by occlusion or secondary motion, but two layers is the structural minimum.

## Ownership rule

Hair is a separate persistent 2D layer family. It may own visible hair RGB/alpha/silhouette, front/back masses, stable attachment/depth metadata and later secondary-motion anchors. It may not modify the body asset, collapse into one irreversible body-baked sprite, use hidden-3D RGB/masks as final visible art, require per-frame generation or require manual user repainting.

## B4A preflight — PASS/CLOSED DIAGNOSTIC

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4_hair_preflight\g3s_b4_hair_preflight_contact_sheet.png`

Reviewed artifact SHA256:

`efd8866a38be1ad54aa60f4f05249813b5abf1754ee0a318fcf92a45ff262d4f`

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b4a_preflight_approval.json`

Result:

- canonical local master is suitable as the hair identity/mass source reference;
- promoted B3B V4 body remains immutable;
- the `96×160` shared review frame is adequate for the first static hair test;
- mandatory minimum depth order is confirmed as `rear_hair -> body -> front_hair`;
- B4 may proceed to a bounded two-layer static review candidate.

B4A created no production hair pixels and promoted nothing.

## B4B — TWO-LAYER STATIC HAIR CANDIDATE — RUNNER READY

Helper:

`tools/structured-2d-character-pipeline/g3s_b4b_two_layer_hair_candidate.py`

Runner:

`tools/structured-2d-character-pipeline/17_run_g3s_b4b_two_layer_hair_candidate.ps1`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair`

### Method

B4B is deliberately bounded and review-only.

It:

1. verifies the exact promoted B3B body hashes;
2. reads B4A preflight metadata and verifies that the canonical master has not changed since preflight;
3. isolates already-authored dark hair pixels from the canonical Exilada pixel-art master using bounded foreground/color/component analysis;
4. aligns that source hair mass to the shared `96×160` B4 working frame using body/skin anchors and nearest-neighbor scaling;
5. splits visible hair ownership into persistent `rear_hair` and `front_hair` candidates according to immutable body overlap;
6. composes deterministically as `rear_hair -> body -> front_hair`;
7. generates separate transparent layer PNGs, composite, native `640×360` gameplay preview, contact sheet and metadata;
8. does **not** promote or commit hair assets automatically.

### Important limitation

B4B uses only hair pixels already visible in the canonical master. It does **not** yet infer hidden rear-hair coverage behind the body and does not yet author secondary-motion segmentation. Those remain later structural work if the static visual candidate passes.

## B4B review package

The runner must produce:

- `g3s_b4b_rear_hair_candidate.png`;
- `g3s_b4b_front_hair_candidate.png`;
- `g3s_b4b_body_hair_composite.png`;
- `g3s_b4b_gameplay_preview.png`;
- `g3s_b4b_contact_sheet.png`;
- `g3s_b4b_two_layer_hair_candidate.json`.

Visual review must confirm:

- hair immediately restores the Exilada's large dark silhouette anchor;
- it reads as very long/heavy/voluminous/messy;
- front and rear masses surround the body convincingly;
- face/head/neck remain readable;
- there is no featureless black blob or fine strand noise collapse;
- source alignment does not create obviously misplaced hair geometry.

Structural review must confirm:

- rear and front layers both exist and are non-empty;
- body hashes remain canonical;
- composition order is deterministic;
- no external paid API/model is used;
- no automatic promotion occurs.

## Current exact action

Run B4B once and inspect/share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair\g3s_b4b_contact_sheet.png`

Do not promote hair and do not start B5/G3S-C until B4B visual/structural review is complete.
