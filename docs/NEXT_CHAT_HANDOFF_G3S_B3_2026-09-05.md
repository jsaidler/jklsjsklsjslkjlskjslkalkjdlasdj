# Next-chat handoff — G3S structured character build

Status date: **2026-09-06**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
4. `docs/G3S_C0_BODY_MOTION_PROOF.md`
5. `docs/G3S_STRUCTURED_2D_VISIBLE_REPRESENTATION.md`
6. `docs/G3V_REPRESENTATIVE_VISUAL_PROXY_LOG.md`
7. `docs/G3S_B4_HAIR_LOG.md`
8. `docs/ANIMATION_PIPELINE.md`

Do not reconstruct state from chat memory if documents disagree.

## Living-document invariant

Every state-changing project action updates thematic docs, `PROJECT_STATE`, this handoff and commits before reporting completion.

Normal operator loop after an approved runner exists:

`git pull -> one documented PowerShell command -> inspect/share output`

## Canonical animation architecture — LOCKED

`real/captured motion -> hidden 3D rig -> full pose-specific 3D guide package -> selected gait/action events -> persistent native-2D pose assets -> deterministic timing/depth/composition -> sprite/runtime export -> QA`

Canonical lock:

`docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`

Hidden 3D owns motion/topology, anatomical side identity, near/far identity, full pose, foreshortening reference, contacts, root travel, depth/occlusion, sockets and semantic/body-part guides.

Hidden 3D does **not** own final visible RGB/alpha/silhouette. Hidden-3D render/mask/silhouette is guide/control data only.

Critical correction: C0 V1/V2 incorrectly reduced the hidden rig to projected joint deltas applied to one static sprite. Do not repeat that.

## Canonical body — LOCKED

B3B V4 is PASS/CLOSED / PROMOTED:

- `assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png`
- `37×128` RGBA;
- PNG SHA256 `702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858`;
- raw RGBA SHA256 `818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c`;
- canonical screen-facing: **LEFT**.

This is a static body identity/style anchor, not the sole source to be warped into every gait pose.

## Facing/laterality — LOCKED

- left-facing source family travels screen-left;
- do not mirror silently;
- screen-x is not anatomical left/right or near/far ownership in a 3/4 sprite;
- anatomical side and near/far identity come from the hidden 3D guide package.

## Hair — DEFERRED

B4 remains open and unapproved. Eventual minimum structure remains:

`rear_hair -> body -> front_hair`

Do not resume B4 automatically.

## Motion backbone — RETAINED / ACTIVE

- G2 = PASS using CMU `105_34 NormalWalk`;
- source rig = `G2_CANONICAL_RIG`;
- G3V-R = PASS using `DIRECTION_SPACE_FK`;
- validated phase frames = `1568, 1588, 1608, 1628`.

This backbone is correct and retained. G3V direct visible 3D rendering failed only as final visible art.

Retained hidden body/rig artifact:

`Z:\AI\RogueliteCharacterPipeline\g3v\g3v_representative_proxy.blend`

It is now used only as guide/control infrastructure.

## Closed visible routes

### Direct visible 3D

G3V direct visible translation = FAIL/CLOSED because output read as low-resolution 3D, not intentional pixel art.

Keep hidden 3D as guide/control infrastructure.

### C0 single-still deformation

V1 and V2 are FAIL/CLOSED.

V2 reviewed SHA256:

`6d6199aa7bc159cad344c8dbc31b52577f2c70bb70f674ab5216ea40db67fba3`

Failure marker:

`tools/structured-2d-character-pipeline/g3s_c0_v2_visual_failure.json`

Closed class:

`single B3B still -> projected joints -> cutout/chain/cage warp -> full walk`

Reason: one still lacks hidden surfaces, foreshortening and correct near/far anatomy for arbitrary gait poses.

`tools/structured-2d-character-pipeline/20_run_g3s_c0_body_walk_v2.ps1` is disabled.

## CURRENT gate — G3S-C1A HIDDEN-3D FULL-POSE GUIDE

C1A is implemented and runner-ready.

Purpose: export **one complete non-rest anatomical left-contact pose guide** from the retained hidden 3D backbone before any new visible pose pixels are authored.

Runner:

`tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`

Spec:

`tools/structured-2d-character-pipeline/g3s_c1_pose_guide_spec.json`

Support:

- `tools/structured-2d-character-pipeline/g3s_c1_export_hidden_pose_guide.py`
- `tools/structured-2d-character-pipeline/g3s_c1_build_pose_guide_review.py`

Workspace:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_hidden_pose_guide`

C1A outputs:

- continuous hidden-body neutral anatomy guide;
- silhouette reference;
- anatomical region/laterality pass;
- camera-space depth-band pass;
- projected skeleton overlay;
- machine-readable JSON with selected event/frame, anatomical sides, near/far, contact foot, root/pelvis, camera and phase metrics;
- five `96×160` guide crops;
- review contact sheet including the canonical B3B static identity/style anchor.

C1A explicitly validates:

- `DIRECTION_SPACE_FK` approval remains PASS;
- G3V direct visible route remains FAIL/CLOSED;
- canonical B3B hash remains unchanged;
- screen-left directional family has negative projected travel x;
- visible hidden-body guide height remains approximately `128 px` under G1 camera baseline.

All hidden-3D rendered outputs are **non-promotable guide evidence only**.

## Exact next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\21_run_g3s_c1_hidden_pose_guide.ps1"
```

Then share:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1_hidden_pose_guide\g3s_c1_contact_left_pose_guide_contact_sheet.png`

If the runner fails, share the complete console output.

Do **not** start C1B, resume hair or promote any 3D guide pixels before C1A visual review.

## Next after C1A PASS

C1B authors **one complete persistent native-2D left-contact body pose** using:

- C1A as pose/anatomy/laterality/near-far/occlusion control;
- B3B V4 as identity/body-style anchor.

C1B may not warp the static B3B still into the gait pose and may not quantize/recolor/crop the hidden-3D guide into final sprite art.

If one C1B pose passes, expand to the first eight-event left-facing walk family:

1. left contact;
2. left down/loading;
3. left passing;
4. left up;
5. right contact;
6. right down/loading;
7. right passing;
8. right up.

Runtime playback is standard sprite animation driven by motion-derived timing/contact/root metadata.

## Local state

- deterministic workspace: `Z:\AI\RogueliteCharacterPipeline`;
- embedded Python: `Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe`;
- retained hidden G3V body/rig blend as above;
- Blender remains the headless pose-guide host;
- C1A requires no image-generation model, paid API or new download;
- FLUX.2 is not used by C1A;
- no broad model search is open;
- PixelLab remains historical paid spike only and is not authorized.
