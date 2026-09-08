# Character Animation Production — Living Decision Record

Status date: **2026-09-08**

Status: **RAW-VIDEO COMPLETE-CHARACTER GENERATION ACTIVE. WAN BASE BF16 UNDER CONTROLLED EXHAUSTION. W1 PAINTERLY LOOK APPROVED. W1A REF-1.5 STRUCTURAL BRANCH RETAINED. W1F LETTERBOX CLOSED. W1G TRACKED RAW-DRIVER REFRAMING CLOSED FAIL. W1H ASPECT-MATCHED RAW-DRIVER GEOMETRY PASSED AND IS THE CURRENT BEST BASELINE. W1I RESIDUAL-BLUR TEST CURRENT.**

Canonical state: `docs/PROJECT_STATE.md`

## Hard production constraints

- complete Exilada reference + separate raw driving video;
- driver identity/clothing/hair may differ completely;
- infer body motion, soft response, hair inertia, cloth/material/wind and restraint/accessory dynamics automatically;
- no routine manual rigging/keyframing/sim repair/mask repair/repainting/compositing;
- final runtime uses complete precomposed spritesheet frames.

## Motion-source rule

Final production motion comes from real driving video consumed in a richer form than skeleton-only pose.

## W1 / W1A

W1 ref 1.0: approved painterly visual/motion baseline, but crop, restraint drift and some limb artifacts remain.

W1A ref 1.5: user review shows better body structure/topology than 1.0, but more destructive blur. Preserve ref 1.5 as structural branch.

## W1F — CLOSED

Whole-frame safe letterboxing did not solve generated crop. Do not iterate safe-box percentages.

## W1G — VALID METHOD FAIL / CLOSED

Tracked/recentered raw-driver geometry produced a valid Wan inference but materially worsened ghosting, limb topology and temporal coherence.

Conclusion: do not use frame-to-frame tracking/affine camera-follow transforms to solve framing. Preserve the richer raw spatiotemporal signal.

## Framing geometry rule — LOCKED FROM W1H

Current `WanAnimate2ToVideo` center-resizes/crops `pose_video` to requested generation geometry.

- raw driver: `480×854`, aspect ≈ 0.5621;
- upstream Wan demo default: `720×1280`, aspect 0.5625;
- old W1/W1A canvas: `640×800`, aspect 0.8.

Old geometry discarded about 29.7% of raw-driver height before pose conditioning.

Correction: **leave raw driver untouched and match Wan generation aspect to the driving video.**

## W1H — GEOMETRY PASS / CURRENT BEST BASELINE

Runner 41 changed only:

`width/height 640×800 -> 512×912`

Raw driver remained untouched; ref strength stayed 1.5.

Completed run:

- prompt id `5299b50f-a38d-4cf1-b71e-7022319067d7`;
- elapsed `1672.46 s`;
- output SHA256 `84756f74af5f01aed8329b6a9b7b116149c6abcfd6e6349399c5de8ecf575af1`;
- estimated pose-video center-crop retention `99.88%` instead of W1A's `70.26%`.

Visual verdict over all 37 frames:

- catastrophic top/head/right-body crop is resolved;
- complete-body retention and temporal anatomy are materially better;
- W1G-style ghosting/elongation is gone;
- hair/cloth remain dynamic;
- later frames are cleaner and highly usable as a direction;
- residual destructive blur remains mainly in fast-motion frames ~8–10;
- chain/restraint topology remains imperfect;
- some lateral edge proximity follows the source performer's own traversal. Final production drivers should be selected with real safe margins rather than tracked/recentered in preprocessing.

Classification: **PASS for the canvas/aspect hypothesis; current best Wan baseline.**

## W1I — CURRENT BLUR ISOLATION

Runner:

`tools/structured-2d-character-pipeline/42_run_wan_animate2_bf16_w1i_pose_end70_ref15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1i_pose_end70_ref15.py`

Parent = exact W1H.

Only changed axis:

`pose_end_percent 1.00 -> 0.70`

Why: native WanAnimate2ToVideo documentation says motion is mostly established early and gives ~0.7 as an example that can loosen fine detail while preserving choreography. This is the least invasive native blur test.

Everything else remains W1H: raw driver, `512×912`, Exilada ref/prompt, BF16 stack, 37 frames, 20 steps, CFG1, Euler/simple, shift5, seed0, pose strength1, pose start0, ref strength1.5, CLIP pose branch and negative prompt.

Pass only if destructive blur falls **without** sacrificing W1H body topology, motion adherence, hair/cloth dynamics or framing.

After W1I: choose W1H or W1I as baseline, then separate 1980s / more-torn / more-exposed Exilada art gate; after that W2 real walking driver with safe margins and W3 secondary-motion stress footage.

## Candidate order

Wan first; SCAIL-2 only after documented Wan `EXHAUSTED_FAIL`.

## Cleanup

Do not accumulate large model variants. Keep small logs/manifests/results. W1F/W1G/W1H/W1I add no new large model checkpoint.

## Immediate operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\42_run_wan_animate2_bf16_w1i_pose_end70_ref15.ps1"
```
