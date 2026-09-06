# G3S — Animation Architecture Lock

Status date: **2026-09-06**

Status: **CANONICAL / LOCKED — SKELETON-ONLY C1A EIGHT-STATE WALK RUNNER READY**

## Final production architecture

`real/captured motion -> hidden skeleton/rig -> pose/laterality/depth/contact/root guide data -> persistent native-2D pose assets -> deterministic sprite playback -> QA`

The hidden 3D is a **skeleton/armature**, not a hidden character render.

### Hidden skeleton owns

- real motion and skeletal topology;
- complete bone/joint transforms for each sampled state;
- anatomical left/right identity;
- near/far chain identity from camera-space depth;
- bone-chain foreshortening;
- contact/support-foot timing;
- pelvis/root travel;
- sockets and attachment transforms;
- secondary-motion driving data.

### Hidden skeleton does not own or require

- a skinned human body mesh;
- detailed 3D anatomy;
- final RGB or alpha;
- final sprite silhouette;
- final pixel-art clusters/value language.

Simple lines/capsules may be rendered only as debug visualization of bone data.

## Closed routes

The following remain closed:

- hidden 3D render -> final visible pixel art;
- single B3B still -> projected joints -> cutout/warp/cage -> full gait;
- MPFB skinned body as mandatory pose/anatomy/silhouette/depth guide.

The B3B V4 body remains the approved visible identity/body-style anchor. It is not stretched into new gait poses.

## C1A — eight-state skeleton walk cycle

The user explicitly prioritized seeing motion rather than stopping at another single-pose proof. C1A therefore exports the complete first walk cycle in one pass from the already-approved `G2_CANONICAL_RIG` and CMU `105_34 NormalWalk` motion.

States:

1. `1588` — left contact;
2. `1598` — left down;
3. `1608` — left passing;
4. `1618` — left up;
5. `1628` — right contact;
6. `1638` — right down;
7. `1648` — right passing;
8. `1658` — right up.

The guide camera is orthographic `640×360`, pitch `26°`, front-three-quarter at `45°` relative to the actual root-travel heading. The rig is not rotated to manufacture facing; the camera side is chosen so real forward root travel projects screen-left. Maximum projected skeleton height is calibrated to approximately `128 px`.

C1A records full bone matrices, projected joints, per-chain depths/lengths, anatomical laterality, near/far ownership, support foot, ground distance and real projected root travel for all eight states.

Current runner:

`tools/structured-2d-character-pipeline/21_run_g3s_c1_hidden_pose_guide.ps1`

Current spec:

`tools/structured-2d-character-pipeline/g3s_c1_skeleton_walk_spec.json`

No MPFB body, image-generation model, paid API or new download is used.

## C1B — visible body animation source

After the eight-state skeleton motion is visually confirmed, C1B authors the **eight persistent native-2D body poses** needed for the first left-facing walk family, using:

- the C1A skeleton cycle as spatial/motion control;
- B3B V4 as identity/body-style anchor.

The user is not expected to draw or repair frames manually. C1B may use an explicitly approved offline source-authoring tool, but accepted outputs become frozen native-2D assets; no per-frame generation occurs at runtime.

C1B may not revive the static-still warp route and may not promote a hidden-3D render as final sprite art.

## Runtime

Once the eight native-2D body states exist, gameplay playback is ordinary sprite animation using motion-derived timing/contact/root metadata. Hair, clothing, restraints and equipment remain separate persistent layers and are added after the body walk source is viable.
