# G3V Representative Visual Proxy — Execution Log

Status date: **2026-09-05**

Gate: **G3V — representative continuous human asset + deterministic pixel translation**

Current status: **FAIL / CLOSED — TECHNICAL BACKBONE RETAINED, DIRECT VISIBLE 3D ROUTE REJECTED.**

## Locked upstream baseline

- G0 automation: PASS;
- G1: `640×360`, orthographic `26 deg`, hero `128 px`;
- G2: CMU `105_34 NormalWalk`, topology/motion PASS;
- G3: native translation technical PASS, production look not approved;
- G3R: renderer-only mannequin refinement FAIL / CLOSED;
- G3V-R retarget preflight: PASS / CLOSED.

## What G3V did prove

- MPFB `2.0.17` loads headlessly from the pinned verified archive;
- a continuous adult female body and weighted `cmu_mb` rig can be created reproducibly;
- real CMU locomotion can be transferred with the validated `DIRECTION_SPACE_FK` method;
- the four quarter-cycle gait phases `1568,1588,1608,1628` are distinct and structurally coherent;
- major topology remains one head/torso, two arms/hands and two legs/feet;
- hair, degraded cloth and wrist/ankle restraints remain present as persistent representative structures;
- binary semantic masks for skin/hair/cloth/metal work;
- the locked G1 camera/scale remains usable.

## Retargeting result — PASS / RETAIN

G3V-R measured incompatible local/rest axes despite matching hierarchy:

- parent mismatches: `0`;
- mean rest-orientation delta: `83.1874 deg`;
- max rest-orientation delta: `180.0289 deg`.

Rejected retarget shortcuts:

- raw Blender `Action` copy;
- raw per-frame `matrix_basis` copy;
- local-axis `REST_COMPENSATED_FK`;
- MPFB pose API for this source/target pair.

Accepted method:

**`DIRECTION_SPACE_FK`**

Measured skeleton-preflight articulation:

- 4 unique poses;
- mean elbow/knee error: `0.0000 deg`;
- max elbow/knee error: `0.0001 deg`;
- V3 chain-shape metric passed;
- source-vs-target skeleton sheet passed visual topology/phase review.

Canonical approval marker:

`tools/deterministic-character-pipeline/g3v_retarget_approval.json`

This retarget remains part of the hidden production backbone.

## Final G3V body/pixel review — VISUAL KILL SWITCH FAIL

Reviewed artifact:

`Z:\AI\RogueliteCharacterPipeline\g3v\g3v_contact_sheet.png`

Frames:

`1568,1588,1608,1628`

### Topology / motion

PASS for gate scope:

- all four phases are genuinely distinct;
- no duplicated or missing major limbs are visible;
- no pelvis/leg/trunk collapse remains;
- left/right gait alternation is coherent;
- weighted body motion is materially more credible than the broken pre-retarget runs.

### Visible representation

FAIL:

- the upper row is recognizably a conventional simplified 3D human;
- the lower native semantic/palette row remains visibly derived from that same 3D form/shading logic;
- coarse palette bands and native-grid output do not become intentional authored modern pixel art;
- silhouettes/value clusters still read as blocky low-resolution 3D rather than a 2D pixel-specific visual language.

This is exactly the G3V kill-switch condition defined before the final rerun.

## Canonical decision

**G3V = FAIL / CLOSED.**

Do not add another renderer-only G3V refinement stage.

Hidden 3D is now explicitly **demoted from visible-image owner** and retained only for:

- real motion;
- persistent topology;
- left/right identity;
- sockets/attachments;
- depth/occlusion guides;
- physics;
- semantic/body-part guides;
- secondary-motion driving data.

The final visible color image must be owned by a structured 2D pixel representation.

Canonical failure marker:

`tools/deterministic-character-pipeline/g3v_failure.json`

## Next gate

**G3S — Structured 2D Visible Representation**

Canonical design:

`docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`

The next risk is no longer motion or retargeting. It is whether one approved native gameplay-scale Exilada pixel source can be represented as persistent 2D parts and animated deterministically from the hidden rig without per-frame generation or repainting.

The old G4 assumption — a detailed Exilada 3D proxy rendered directly into final pixels — is blocked and rescoped.
