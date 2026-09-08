# Character Animation Production — Living Decision Record

Status date: **2026-09-08**

Status: **RAW-VIDEO COMPLETE-CHARACTER GENERATION ACTIVE. WAN BASE BF16 UNDER CONTROLLED EXHAUSTION. W1 PAINTERLY LOOK APPROVED. W1H ASPECT-MATCHED RAW-DRIVER GEOMETRY PASSED AND IS CURRENT BEST BASELINE. W1I POSE-END 0.70 DID NOT MATERIALLY IMPROVE BLUR. W1J REF-1.0 RETEST ON CORRECTED GEOMETRY IS CURRENT.**

Canonical state: `docs/PROJECT_STATE.md`

## Hard production constraints

- complete Exilada reference + separate raw driving video;
- driver identity/clothing/hair may differ completely;
- infer body motion, soft response, hair inertia, cloth/material/wind and restraint/accessory dynamics automatically;
- no routine manual rigging/keyframing/sim repair/mask repair/repainting/compositing;
- final runtime uses complete precomposed spritesheet frames.

## Motion-source rule

Final production motion comes from real driving video consumed in a richer form than skeleton-only pose.

## Closed framing branches

- W1F whole-frame letterbox: generated crop remained; closed.
- W1G tracked/recentered driver: valid inference but ghosting/limb topology/temporal coherence worsened; closed.

Do not solve framing by synthetic frame-to-frame camera-follow transforms.

## Framing geometry rule — LOCKED FROM W1H

`WanAnimate2ToVideo` center-resizes/crops `pose_video` to requested generation geometry.

- raw driver `480×854`, aspect≈0.5621;
- upstream default `720×1280`, aspect0.5625;
- old W1/W1A `640×800`, aspect0.8.

Old geometry discarded ~29.7% of raw-driver height before pose conditioning. Correction: **leave raw driver untouched and match Wan generation aspect to driving video.**

## W1H — GEOMETRY PASS / CURRENT BEST BASELINE

Runner 41 changed only `640×800 -> 512×912`; raw driver untouched; ref strength1.5.

- prompt `5299b50f-a38d-4cf1-b71e-7022319067d7`;
- elapsed `1672.46s`;
- SHA256 `84756f74af5f01aed8329b6a9b7b116149c6abcfd6e6349399c5de8ecf575af1`;
- estimated pose-video retention `99.88%` vs W1A `70.26%`.

Visual: catastrophic crop resolved; complete-body retention and temporal anatomy materially better; hair/cloth remain dynamic. Residual destructive blur around fast-motion frames ~8–10 and imperfect chain/restraint topology remain.

## W1I — POSE END 0.70 / NOT PREFERRED

Runner 42 changed only `pose_end_percent 1.00 -> 0.70` from W1H.

- prompt `5d4f23ed-f4bf-4b01-a13f-108b2bf31fe0`;
- elapsed `1526.52s`;
- SHA256 `9a9052f40221878ded69f61e452abeda87cfaa42bde475bb5e9809c04763d054`.

Frame-by-frame: extremely close to W1H; fast-motion blur remains; no material topology/framing improvement. Mixed sharpness proxies do not establish a robust perceptual gain. Restore/retain `pose_end_percent=1.0`.

## W1J — CURRENT REF-STRENGTH RETEST

Runner:

`tools/structured-2d-character-pipeline/43_run_wan_animate2_bf16_w1j_aspectmatched_ref10.ps1`

Executor:

`tools/wan-animate2-spike/run_w1j_ref10_aspectmatched.py`

Parent = exact W1H.

Only changed axis:

`reference_image_strength 1.5 -> 1.0`

Everything else stays W1H: raw driver untouched, `512×912`, pose strength1.0, pose start0.0, pose end1.0, seed0, 20 steps, CFG1, Euler/simple, shift5, same reference/prompt/CLIP pose/negative.

Why: the earlier ref1.0-vs1.5 comparison happened under the incorrect `640×800` geometry. W1J determines whether ref1.0 can now keep full body topology while recovering cleaner rendering.

Prefer ref1.0 only if destructive blur/ghosting improves materially without missing/displaced anatomy, identity loss or weaker hair/cloth motion.

## Next sequence

1. W1J ref1.0 corrected-geometry comparison;
2. choose ref1.0 or ref1.5 technical baseline;
3. separate approved 1980s / more-torn / more-exposed Exilada art gate;
4. W2 real walking driver with safe real margins;
5. W3 secondary-motion stress footage;
6. finite W4 variants only if justified;
7. gameplay-scale validation around128px.

## Candidate order / cleanup

Wan first; SCAIL-2 only after documented Wan `EXHAUSTED_FAIL`. Do not accumulate large model variants. Keep small logs/manifests/results; W1F–W1J add no new large checkpoint.

## Immediate operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\43_run_wan_animate2_bf16_w1j_aspectmatched_ref10.ps1"
```
