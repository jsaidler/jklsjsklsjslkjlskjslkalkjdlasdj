# Next-chat handoff — G3S complete-character spritesheet production

Status date: **2026-09-08**

GitHub living docs are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VISUAL_DIRECTION.md`
3. `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`
4. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
5. `docs/ANIMATION_PIPELINE.md`
6. `docs/CHARACTERS.md`

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

W0: local BF16 baseline passed.

W1 ref 1.0: approved painterly/motion baseline; crop + chain/restraint + some limb artifacts remain.

W1A ref 1.5: **structural branch retained**. User review: body topology is better than 1.0, but blur/ghosting is worse. Preserve 1.5.

W1F: whole-frame letterboxing did not solve crop. Closed.

W1G: tracked/recentered driver produced a valid inference but materially worsened ghosting, elongated/unstable limbs and temporal anatomy. **Closed. Never return to synthetic camera-follow/tracker reframing.**

## Geometry discovery — LOCKED

Current ComfyUI `WanAnimate2ToVideo` center-resizes `pose_video` to requested generation geometry.

- raw official driver: `480×854`, aspect ≈ 0.5621;
- upstream Wan demo default: `720×1280`, aspect 0.5625;
- old W1/W1A canvas: `640×800`, aspect 0.8.

Old geometry retained only ~70.3% of raw-driver height before pose conditioning.

Production rule: **keep the raw driver untouched and match Wan generation aspect to the driver.**

## W1H — GEOMETRY PASS / BEST BASELINE

Runner 41 changed only `640×800 -> 512×912` relative to W1A, leaving the original raw driver untouched and ref strength at 1.5.

Completed:

- prompt id `5299b50f-a38d-4cf1-b71e-7022319067d7`;
- elapsed `1672.46 s`;
- SHA256 `84756f74af5f01aed8329b6a9b7b116149c6abcfd6e6349399c5de8ecf575af1`;
- target aspect `0.561404` vs raw driver `0.562061`;
- estimated pose-video retention `99.88%` vs W1A `70.26%`.

Full 37-frame visual verdict:

- catastrophic top/head/right-body crop is resolved;
- body topology and temporal coherence are materially better than W1G and generally better than W1A;
- long hair and cloth remain dynamic;
- later frames are clean/legible and preserve the approved painterly language;
- residual destructive blur remains mainly around fast-motion frames ~8–10;
- chain/restraint topology remains imperfect, especially late raised-hand chain mass;
- some lateral edge proximity follows the source performer traversal. Do **not** overfit this official driver with tracking; W2 production footage should be selected with safe real margins.

Classification: **W1H PASS for canvas/aspect hypothesis; current best Wan baseline.**

## CURRENT GATE — RUNNER 42 / W1I RESIDUAL BLUR

Runner:

`tools/structured-2d-character-pipeline/42_run_wan_animate2_bf16_w1i_pose_end70_ref15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1i_pose_end70_ref15.py`

Parent = exact W1H prompt.

Only changed axis:

`pose_end_percent 1.00 -> 0.70`

Rationale: native WanAnimate2ToVideo documentation says motion is mostly established early and explicitly gives ~0.7 as an example that can loosen fine detail while preserving choreography. This isolates residual blur without changing pose strength, prompt, seed, driver or model.

Everything else stays W1H: raw driver untouched, `512×912`, Exilada ref/prompt, BF16 stack, 37 frames, 16fps, 20 steps, CFG1, Euler/simple, shift5, seed0, pose strength1, pose start0, ref strength1.5, CLIP pose branch and negative prompt.

Expected:

- `Z:\AI\WanAnimate2\w1i_exilada_poseend70_ref15.mp4`
- `Z:\AI\WanAnimate2\w1i_run_manifest.json`
- `Z:\AI\WanAnimate2\w1i_api_prompt.json`
- `Z:\AI\WanAnimate2\w1i_executor.log`

Pass W1I only if destructive blur falls without sacrificing W1H topology, motion adherence, hair/cloth dynamics or framing.

## Exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\42_run_wan_animate2_bf16_w1i_pose_end70_ref15.ps1"
```

## After W1I

1. choose W1H or W1I as technical baseline;
2. separate approved 1980s / more torn / more exposed Exilada art gate;
3. W2 real walking driver with safe margins;
4. W3 secondary-motion stress footage;
5. finite W4 variants only if justified;
6. gameplay-scale validation around 128 px.

## Cleanup

No new large model assets added. Keep active BF16 route. Keep small W1G/W1H evidence and SSD comparison workspace until Wan verdict.
