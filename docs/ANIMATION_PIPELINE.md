# Character Animation Production — Living Decision Record

Status date: **2026-09-08**

Status: **RAW-VIDEO COMPLETE-CHARACTER GENERATION ACTIVE. WAN BASE BF16 UNDER CONTROLLED EXHAUSTION. W1 PAINTERLY LOOK APPROVED. W1A REF-1.5 STRUCTURAL BRANCH RETAINED. W1F LETTERBOX CLOSED. W1G TRACKED RAW-DRIVER REFRAMING CLOSED FAIL. W1H ASPECT-MATCHED GENERATION CANVAS CURRENT.**

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

W1A ref 1.5: user review shows better body structure/topology than 1.0, but more destructive blur. Preserve ref 1.5 as structural branch; blur is a later isolated axis.

## W1F — CLOSED

Whole-frame safe letterboxing did not solve generated crop. Do not iterate safe-box percentages.

## W1G — VALID METHOD FAIL / CLOSED

Runner 40 final v3.1 produced a valid inference on ref 1.5 after all preflight guards passed.

Result: materially worse than W1/W1A — more ghosting/smearing, unstable/elongated limbs/body, detached/duplicated-looking extremities, weaker temporal coherence, framing still not reliably solved.

Conclusion: do not reframe raw driving footage with frame-to-frame tracking/affine camera-follow transforms. This corrupts the richer spatiotemporal signal Wan needs.

W1G is retained only as small failure evidence.

## Framing geometry root cause

Current `WanAnimate2ToVideo` uses center-resize/crop of `pose_video` to the requested output geometry.

- raw driver: `480×854`, aspect ≈ 0.5621;
- upstream Wan-Animate-2 demo default: `720×1280`, aspect 0.5625;
- W1/W1A canvas: `640×800`, aspect 0.8.

Center-cropping 480×854 to aspect 0.8 discards about 29.7% of source height. This is now the leading crop explanation.

The correction must happen in **generation-space aspect**, not by altering the driver.

## W1H — CURRENT

Runner:

`tools/structured-2d-character-pipeline/41_run_wan_animate2_bf16_w1h_aspect_matched_ref15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1h_aspect_matched_ref15.py`

Parent = exact W1A.

Only changed axis:

`width/height 640×800 -> 512×912`

Raw driver remains untouched.

512×912 is almost aspect-identical to 480×854 while using fewer total pixels than 640×800.

Everything else remains W1A: Exilada ref/prompt, raw driver, BF16 stack, 37 frames, 20 steps, CFG1, Euler/simple, shift5, seed0, pose strength1, ref strength1.5, CLIP pose branch and negative prompt.

Pass if:

1. full-body framing materially improves;
2. no W1G-style temporal/anatomical degradation;
3. W1A structural retention survives.

If W1H passes, next gate = destructive-blur reduction. After that, separate 1980s / more torn / more exposed Exilada art gate.

## Candidate order

Wan first; SCAIL-2 only after documented Wan `EXHAUSTED_FAIL`.

## Cleanup

Do not accumulate large model variants. Keep small logs/manifests/results. No large assets were added by W1G/W1H.

## Immediate operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\41_run_wan_animate2_bf16_w1h_aspect_matched_ref15.ps1"
```
