# Next-chat handoff — G3S complete-character spritesheet production

Status date: **2026-09-08**

GitHub living docs are canonical.

## Paths

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- Wan: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` invalid/stale.

## Production contract

Complete Exilada appearance from `exilada_master.png` + raw driving video. Final runtime uses complete precomposed spritesheets. No routine manual rigging/keyframing/sim repair/mask repair/repainting/compositing.

## Visual direction

Painterly illustrated dark fantasy with explicit 1980s sword-and-sorcery charge: Heavy Metal, Conan, Red Sonja, Frank Frazetta, Julie Bell. Adult sensuality/nudity legitimate. Localized blur can be positive; destructive ghosting/anatomy loss is not.

## Wan state

- W0: local BF16 route passed.
- W1 ref1.0: approved painterly/motion language, but old geometry crop/restraint/limb issues.
- W1A ref1.5: structurally stronger but blurrier under old geometry.
- W1F letterbox: closed fail.
- W1G tracked/recentered driver: closed valid method fail; do not return to synthetic camera-follow/recentering.

## Geometry rule from W1H

Current ComfyUI `WanAnimate2ToVideo` center-resizes/crops `pose_video` to generation geometry.

Raw driver is `480×854`; old project canvas was `640×800`, producing substantial vertical center-crop in the Comfy path. W1H changed only the generation canvas to `512×912`, left the raw driver untouched, and materially improved full-body retention.

Upstream correction: Wan's repository exposes different example defaults (`640×800` in YAML, `720×1280` in demo CLI). Do not claim a single upstream default proves the aspect rule. The production rule is retained from Comfy semantics + W1H empirical success: **keep raw driver untouched and use compatible generation aspect.**

## W1H — GEOMETRY PASS / BEST CURRENT BASELINE

Runner 41:

- `512×912`;
- ref strength1.5;
- raw driver untouched;
- prompt `5299b50f-a38d-4cf1-b71e-7022319067d7`;
- elapsed `1672.46s`;
- SHA256 `84756f74af5f01aed8329b6a9b7b116149c6abcfd6e6349399c5de8ecf575af1`.

Visual: major crop solved, body retention/coherence much better, hair/cloth remain dynamic. However fast-motion frames still show **strong destructive blur plus structural deformation**, and chain/restraint topology is imperfect. W1H is not production quality yet.

## W1I — POSE END 0.70 / NOT PREFERRED

Runner 42 changed only `pose_end_percent 1.00 -> 0.70`.

Result remained extremely close to W1H; blur and structural problems persisted. Return pose end to1.0.

## W1J — REF1.0 ONLY / SUPERSEDED BEFORE RUN

Runner 43 exists but is **not current**. User correctly rejected spending a full run on lowering only `reference_image_strength`, because the remaining failure is broader than identity tightness.

Do not run Runner43 unless later evidence specifically requires an isolated ref-strength test.

## CURRENT GATE — RUNNER 44 / W1K POSE STRENGTH 0.80

Runner:

`tools/structured-2d-character-pipeline/44_run_wan_animate2_bf16_w1k_pose_strength80_ref15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1k_pose_strength80_ref15.py`

Parent = exact W1H.

Only changed axis:

`pose_strength 1.00 -> 0.80`

Everything else stays W1H: raw driver untouched, `512×912`, ref1.5, pose window0.0–1.0, seed0,20 steps,CFG1,Euler/simple,shift5,same reference/prompt/negative/CLIP pose branch.

Why: remaining failure is motion-phase smear + anatomy deformation. ComfyUI defines pose strength as the direct scale of pose-video influence, and the Animate-2 model path scales pose-branch values directly. W1I already showed that ending the pose branch earlier did not help.

Pass only if blur **and structural deformation** fall materially while choreography, identity, hair and cloth dynamics remain acceptable.

If W1K fails, next axis = sampling quality/steps rather than another blind reference-strength change.

## Exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\44_run_wan_animate2_bf16_w1k_pose_strength80_ref15.ps1"
```

## Cleanup

No new large model assets. Keep active BF16 route, small proof/failure evidence and SSD comparison workspace until Wan verdict.
