# G3S-B4 — Hair Layer

Status date: **2026-09-06**

Gate status: **B4A PASS/CLOSED DIAGNOSTIC — B4B V1 EXTRACTION FAIL/CLOSED PRE-RUN — B4B V2 AUTHORED TWO-LAYER RUNNER READY**

## Entry condition

G3S-B3/B3B is PASS/CLOSED.

Canonical immutable body base:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json`
- promotion commit `2deb765c3980d586ef9747340bb48852dedca452`;
- `37×128` RGBA;
- visible standing height `128 px`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`.

The body is immutable input to B4. Hair may surround/occlude it through composition but may not overwrite its ownership.

## Canonical hair identity

The Exilada's hair is:

- black / nearly black;
- very long;
- heavy;
- voluminous;
- messy;
- a primary silhouette anchor;
- materially lived-in and compatible with deprivation/survival rather than salon styling.

Identity/design authority:

`assets/source/characters/exilada/reference/exilada_master.png`

The master is a **visual inspiration/reference** for hair identity, mass, material and framing. It is not a complete geometric source for the final hair layers.

## Hair depth architecture — LOCKED

Minimum valid representation:

1. `rear_hair` — persistent transparent layer behind body/head/shoulders/back;
2. `front_hair` — persistent transparent layer in front where hair crosses face/neck/chest/shoulders.

Minimum deterministic composition:

`rear_hair -> body -> front_hair`

Additional side/intermediate masses may be introduced later only if occlusion or secondary motion requires them. One flat hair overlay is invalid.

## Ownership rule

Hair owns its own visible RGB/alpha/silhouette and later its own secondary-motion anchors. It must not:

- modify the canonical body asset;
- be baked irreversibly into the body;
- use hidden-3D RGB/masks as final visible art;
- require per-frame generation;
- require manual frame-by-frame repainting by the user.

## B4A preflight — PASS/CLOSED DIAGNOSTIC

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4_hair_preflight\g3s_b4_hair_preflight_contact_sheet.png`

SHA256:

`efd8866a38be1ad54aa60f4f05249813b5abf1754ee0a318fcf92a45ff262d4f`

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b4a_preflight_approval.json`

The preflight confirmed:

- the local master is suitable as hair identity/mass inspiration;
- promoted B3B body remains immutable;
- shared review frame `96×160` is adequate for the first static test;
- minimum depth order is `rear_hair -> body -> front_hair`.

B4A created no production hair pixels.

## B4B V1 — MASTER EXTRACTION — FAIL/CLOSED PRE-RUN METHOD

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b4b_v1_extraction_route_failure.json`

The first B4B implementation attempted to isolate visible hair pixels from the master and split them into front/rear ownership according to body overlap.

That route is invalid because the master **does not contain sufficient visible information for the hair mass that falls behind the head, shoulders and back**. A valid `rear_hair` layer therefore cannot be recovered by extraction from the master.

Consequences:

- visible master hair pixels are not final hair geometry;
- rear coverage behind the body must be newly authored;
- front and rear layers must both be designed as new native-pixel assets;
- the master remains inspiration/reference only.

The V1 runner was not executed by the user. No production hair art was created. No model was downloaded; no cleanup command applies.

## B4B V2 — AUTHORED TWO-LAYER STATIC CANDIDATE — CURRENT / RUNNER READY

Machine-readable spec:

`tools/structured-2d-character-pipeline/g3s_b4b_v2_authored_two_layer_hair_spec.json`

Helper:

`tools/structured-2d-character-pipeline/g3s_b4b_two_layer_hair_candidate.py`

Runner:

`tools/structured-2d-character-pipeline/17_run_g3s_b4b_two_layer_hair_candidate.ps1`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair`

### V2 method

B4B V2 is a deterministic **native-pixel authoring spike**. It does not extract, trace or copy master hair pixels.

It:

1. verifies the exact promoted B3B body hashes and dimensions;
2. verifies the local master SHA still matches the B4A preflight source;
3. uses the master only as visual identity/mass inspiration in the review sheet;
4. authors a new `rear_hair` mass directly on the native `96×160` pixel grid, including new geometry behind head/neck/shoulders/back that is not visible in the master;
5. authors a new `front_hair` crown/framing/lock layer directly on the native grid;
6. uses a compact dark 8-color palette and broad locks/value groups rather than strand noise;
7. composes deterministically as `rear_hair -> immutable body -> front_hair`;
8. outputs separate transparent layers, composite, `640×360` gameplay preview, contact sheet and metadata;
9. performs no automatic promotion.

No external paid API or external generative model is used.

### Review package

Expected outputs:

- `g3s_b4b_rear_hair_candidate.png`;
- `g3s_b4b_front_hair_candidate.png`;
- `g3s_b4b_body_hair_composite.png`;
- `g3s_b4b_gameplay_preview.png`;
- `g3s_b4b_contact_sheet.png`;
- `g3s_b4b_two_layer_hair_candidate.json`.

### Visual PASS requirements

At native scale the candidate must:

- immediately restore the Exilada's large dark silhouette anchor;
- read as very long, heavy, voluminous and messy;
- show convincing rear mass behind head/shoulders/back;
- show front locks/masses framing face/neck/chest without erasing body readability;
- avoid a featureless black blob;
- avoid fine-strand noise that collapses at 1×;
- feel compatible with the canonical master rather than like unrelated generic hair;
- remain structurally suitable for later secondary-motion segmentation.

### Structural PASS requirements

- `rear_hair` and `front_hair` are separate non-empty transparent assets;
- composition order is deterministic;
- body hashes remain canonical;
- no master pixels are copied into the hair layers;
- no hidden-3D visible ownership;
- no external paid API/model;
- no automatic promotion;
- no manual user repainting dependency.

## Current exact action

Run B4B V2 once and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b4b_two_layer_hair\g3s_b4b_contact_sheet.png`

Do not promote hair and do not start B5/G3S-C until the B4B V2 visual/structural review is complete.
