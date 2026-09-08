# Character Animation Production — Living Decision Record

Status date: **2026-09-08**

Status: **RAW-VIDEO COMPLETE-CHARACTER GENERATION ACTIVE. WAN BASE BF16 UNDER CONTROLLED EXHAUSTION. W1H IS THE BEST CURRENT GEOMETRY BASELINE. W1I POSE-END 0.70 DID NOT HELP. W1J REF-ONLY RETEST IS SUPERSEDED BEFORE RUN. W1K POSE-STRENGTH 0.80 IS CURRENT.**

Canonical state: `docs/PROJECT_STATE.md`

## Hard production constraints

- complete Exilada reference + separate raw driving video;
- driver identity/clothing/hair may differ completely;
- infer body motion, soft response, hair inertia, cloth/material/wind and restraint/accessory dynamics automatically;
- no routine manual rigging/keyframing/sim repair/mask repair/repainting/compositing;
- final runtime uses complete precomposed spritesheet frames.

## Motion-source rule

Final production motion comes from real driving video consumed in a richer form than skeleton-only pose.

## Closed branches

- W1F whole-frame letterbox: crop remained.
- W1G tracked/recentered driver: valid inference but ghosting/limb topology/temporal coherence worsened.
- W1I pose_end0.70: valid but perceptually almost unchanged from W1H.

Do not solve framing by synthetic frame-to-frame camera-follow transforms.

## Geometry rule from W1H

Current ComfyUI center-resizes/crops pose video to generation geometry. W1H proved that changing the generation canvas from `640×800` to `512×912` while leaving the raw `480×854` driver untouched materially improves full-body retention.

Upstream Wan examples contain conflicting dimensions (`640×800` YAML vs `720×1280` demo CLI), so aspect matching is retained as an empirical Comfy-path rule, not as a claim about one canonical upstream default.

## W1H — BEST CURRENT BASELINE

- raw driver untouched;
- `512×912`;
- ref1.5;
- prompt `5299b50f-a38d-4cf1-b71e-7022319067d7`;
- elapsed `1672.46s`;
- SHA256 `84756f74af5f01aed8329b6a9b7b116149c6abcfd6e6349399c5de8ecf575af1`.

Result: major crop resolved and temporal body coherence improved, but fast-motion phases still show **heavy smear plus structural deformation**. Chain/restraint topology remains imperfect. W1H is not production quality yet.

## W1J — SUPERSEDED BEFORE RUN

Runner43 ref1.0-only test remains available as small tooling but is not current. Lowering only reference strength does not target the main remaining motion-phase failure strongly enough to justify a full run now.

## W1K — CURRENT

Runner:

`tools/structured-2d-character-pipeline/44_run_wan_animate2_bf16_w1k_pose_strength80_ref15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1k_pose_strength80_ref15.py`

Only changed variable from W1H:

`pose_strength 1.00 -> 0.80`

Everything else remains W1H: raw driver,512×912,ref1.5,pose window0–1,seed0,20 steps,CFG1,Euler/simple,shift5,same Exilada reference/prompt/negative/CLIP pose branch.

Reason: ComfyUI defines pose strength as the direct scale of pose-video influence, and the Animate-2 model path directly scales pose-branch values. This is the first test that directly reduces motion forcing while preserving the whole temporal pose window.

Pass only if **both** destructive blur and structural deformation improve materially while choreography, identity, long-hair motion and cloth dynamics remain acceptable.

If W1K fails decisively, next technical axis = sampling quality/steps.

## Immediate operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\44_run_wan_animate2_bf16_w1k_pose_strength80_ref15.ps1"
```

## Candidate order / cleanup

Wan first; SCAIL-2 only after documented Wan `EXHAUSTED_FAIL`. Do not accumulate large model variants. W1K adds no large checkpoint.
