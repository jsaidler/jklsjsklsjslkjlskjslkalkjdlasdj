# G3S-B — Persistent 2D Part Decomposition

Status date: **2026-09-05**

Gate status: **READY TO RUN**

## Why this gate exists

G3S-A1 V2 was visually rejected because the mouth patch became an artificial block rather than a believable small mouth. The user explicitly chose to continue with the planned structured-2D pipeline instead of spending another whole-character iteration on the face.

Canonical failure marker:

`tools/structured-2d-character-pipeline/g3s_a1_v2_failure.json`

The macro body/source is therefore accepted **provisionally for decomposition only**. The head/face remains unresolved and must become a replaceable persistent part.

## Locked production decisions

1. **The bad mouth does not block part decomposition.**
2. **Head/face is a replaceable part**, not something that must be fixed by repainting the entire character.
3. **Broken chain segments are not baked into the permanent body sprite.**
4. Broken chains are modeled as **initial accessories** with their own sockets/state.
5. G3S-C animation remains blocked until this decomposition is visually reviewed.
6. No image model is invoked by G3S-B.

## Source

G3S-B rebuilds the same pinned provenance scaffold from:

`Z:\AI\RogueliteCharacterPipeline\g3s_a_control\g3s_a_control_official_raw.png`

Pinned SHA256:

`ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e`

Native source construction remains:

- canvas: `128×128` RGBA;
- high-resolution subject bbox: `[582,40,814,705]`;
- provisional subject size: `43×122`;
- native placement: `[42,3]`;
- scaffold resampling: nearest-neighbor only;
- no generative inference.

The failed V2 mouth patch and authored chain-remnant pixels are **not** the decomposition authority.

## Persistent part set — V1

Specification:

`tools/structured-2d-character-pipeline/g3s_b_parts_spec_v1.json`

The V1 decomposition produces persistent parts for:

- hair back mass;
- head/face placeholder;
- screen-left upper arm;
- screen-left forearm;
- screen-left hand;
- screen-right upper arm;
- screen-right forearm;
- screen-right hand;
- screen-left thigh;
- screen-left shin;
- screen-left foot;
- screen-right thigh;
- screen-right shin;
- screen-right foot;
- torso/pelvis core;
- front cloth mass;
- front-left hair mass;
- front-right hair mass.

The current static image cannot safely determine anatomical left/right for every screen-side limb. Therefore V1 stores **screen-side identity** and marks anatomical side as unresolved until G3S-C binds each part to projected hidden-rig joints.

## Part metadata

Each extracted part stores:

- stable part ID;
- role;
- screen side;
- anatomical-side status;
- depth order for current static review;
- native canvas bounding box;
- persistent pivot in canvas coordinates;
- crop-local pivot;
- alpha pixel count;
- asset SHA256.

This metadata is emitted into:

`g3s_b_runtime_manifest.json`

## Broken chains — initial accessories

Chain segments are not part of the base body decomposition.

Initial accessory slots are created for:

- screen-left wrist;
- screen-right wrist;
- screen-left ankle;
- screen-right ankle.

Each slot stores a socket coordinate and:

- family: `broken_chain`;
- `baked_into_body = false`;
- art status: `NOT_AUTHORED`;
- initial state: `OPTIONAL_INITIAL_EQUIPMENT`.

This lets chain art be added/removed/damaged independently later without modifying body pixels.

The historical fact of captivity remains canonical. This change concerns production layering, not narrative continuity.

## Head/face state

`head_face` is deliberately marked:

`UNRESOLVED_REPLACEABLE_PART`

G3S-B does **not** claim that the current face is approved. The point of decomposition is precisely to make the face independently replaceable without touching torso, hair, clothing or animation ownership.

## Technical audit

The helper:

`tools/structured-2d-character-pipeline/g3s_b_decompose_v1.py`

must:

- rebuild the pinned 128×128 provisional scaffold deterministically;
- extract every named persistent part;
- hard-fail if a mandatory part is unexpectedly empty;
- preserve pivots/sockets;
- recompose the named parts plus audited residual pixels;
- require pixel-exact reconstruction of the provisional scaffold;
- expose residual coverage;
- generate a visual part overlay;
- generate a part atlas;
- generate pivot/socket diagnostics.

Pixel-exact recomposition proves the decomposition process itself is lossless. It does **not** prove that the part masks are artistically optimal; visual review remains authoritative.

## Review artifacts

Runner:

`tools/structured-2d-character-pipeline/09_run_g3s_b_decomposition.ps1`

Output workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_b_decomposition`

Expected artifacts:

- `g3s_b_source128.png`
- `g3s_b_recomposed.png`
- `g3s_b_part_overlay.png`
- `g3s_b_pivots_and_sockets.png`
- `g3s_b_parts_atlas.png`
- `g3s_b_contact_sheet.png`
- `g3s_b_runtime_manifest.json`
- `g3s_b_result.json`
- `parts/*.png`

## Visual review order

1. topology remains one head/torso, two arms/hands, two legs/feet;
2. no major anatomy is missing from persistent parts;
3. hands and feet have usable isolated assets;
4. head/face is isolated cleanly enough to replace later;
5. hair masses are separable from the body core;
6. front cloth mass is separable enough for later deformation;
7. pivots are plausible at neck/shoulder/elbow/wrist/hip/knee/ankle relationships;
8. chain sockets are plausible and chains are not treated as permanent body pixels;
9. decomposition does not introduce visible reconstruction differences.

## PASS / FAIL

**PASS** means the persistent-parts representation is structurally credible enough to attempt G3S-C four-phase walk proof.

**FAIL** means revise only the part specification/masks/pivots. Do not return to model search and do not repaint animation frames.

## Exact next action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\09_run_g3s_b_decomposition.ps1"
```

Then STOP and review:

`Z:\AI\RogueliteCharacterPipeline\g3s_b_decomposition\g3s_b_contact_sheet.png`
