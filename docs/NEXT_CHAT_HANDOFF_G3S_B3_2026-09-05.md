# Next-chat handoff — G3S character spritesheet production

Status date: **2026-09-07**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
3. `docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`
4. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
5. `docs/G3S_C1_HIDDEN_POSE_GUIDE.md`
6. `docs/G1_CAMERA_SCALE_LOG.md`

## Locked production direction

- elevated arcade beat'em-up / belt-scroller false 3D;
- fixed `640×360` orthographic camera, pitch `26 deg`;
- protagonist about `128 px` tall;
- mostly lateral / three-quarter screen-left locomotion family;
- exact horizontal facing angle is currently under locomotion review;
- no isometric north/south character-family multiplication;
- final runtime = conventional deterministic spritesheet playback;
- runtime/world locomotion is separate from baked sprite root translation.

## C1A status — mechanical pass only

Retained source:

- `G2_CANONICAL_RIG`;
- CMU `105_34 NormalWalk`;
- eight approved phases `1588..1658`;
- existing guide `Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_guide.json`.

C1A still proves coherent human gait timing/support progression and intact skeletal chains. It is **not** the final gameplay locomotion master.

The old horizontal camera azimuth was `45 deg` from travel heading. This is now reopened because runner-30 visual output still reads too frontal/awkward for the belt-scroller.

## SSD status

Exact upstream SSD remains BLOCKED because the public release omits the custom multi-scale `pose_guider.pth` required by current upstream code.

Moore-compatible fallback remains technically runnable with the released SSD denoising/reference UNets plus baseline Moore pose guider/motion module.

### Runner 29

- technical PASS;
- visual FAIL;
- weak pose obedience;
- unstable feet/lower legs;
- detached accessory/ground artifacts.

### Runner 30

Runner:

`tools/structured-2d-character-pipeline/30_run_ssd_moore_compat_exilada_walk8_pose_aligned.ps1`

It fixed a real input defect: runner 29 had stretched C1A pose geometry vertically by `1.7778x` through independent `640x360 -> 512x512` axis normalization.

Runner 30 used uniform scale + DWPose-body registration and produced a **clear A/B improvement**:

- stronger pose articulation;
- better left/right differentiation;
- materially better leg/foot reconstruction.

But the user rejected the result as still far below the intended game quality:

- walk lacks naturality;
- pose language is not yet appropriate to the game;
- gait phases remain awkward;
- accessory/restraint artifacts persist.

Therefore runner 30 is a useful diagnostic correction but **not production PASS**.

Do not run SSD again yet.

## CURRENT GATE — G3S-C1C gameplay locomotion master

Canonical doc:

`docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`

Immediate runner:

`tools/structured-2d-character-pipeline/31_run_g3s_c1c_gameplay_facing_audit.ps1`

Runner 31 performs no diffusion. It rebuilds skeleton-only reviews of the same validated real gait at three camera azimuths:

- `60 deg` — 30 deg off pure profile;
- `72 deg` — 18 deg off pure profile;
- `84 deg` — 6 deg off pure profile.

Everything else stays fixed: same motion, same eight phases, `640x360`, pitch `26 deg`, target skeleton height about `128 px`.

Purpose: establish a game-appropriate mostly-lateral presentation before styling the gait itself.

## EXACT NEXT OPERATOR ACTION

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\31_run_g3s_c1c_gameplay_facing_audit.ps1"
```

Then share, from each of these directories, the contact sheet and preferably zoom GIF:

`Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_facing_audit\az60`

`Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_facing_audit\az72`

`Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_facing_audit\az84`

## Decision after runner 31

- choose one facing;
- choose an intermediate facing if needed;
- or reject all three.

If the selected facing still leaves the gait too neutral, the next skeleton-only gate will apply a deterministic gameplay locomotion overlay: shorter/clearer stride, controlled root bob, torso inclination, shoulder orientation, arm-swing/elbow treatment, head stabilization and foot-lift amplitude.

Only after the skeleton locomotion itself is approved should visible body authoring resume.

## Layering

Runner-30 restraint/accessory failures reinforce body-first locomotion validation. Hair, clothing, bindings, shackles/chains and secondary masses are downstream layer/authoring problems, not part of defining the base gait.

No cleanup applies. SSD assets are retained but computation is paused.
