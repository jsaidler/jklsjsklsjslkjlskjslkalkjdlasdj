# PixelLab explicit-skeleton spike — Exilada

Purpose: validate only the first half of the proposed production architecture:

`canonical Exilada -> automatic skeleton -> four explicit walk key poses -> PixelLab animate-with-skeleton -> automatic QA`

**Pixel Engine is intentionally not part of this spike.** It remains blocked until all four PixelLab key poses pass both the deterministic QA pre-gate and visual review.

## Why 128×128

PixelLab's current public API page prices `animate-with-skeleton` through 128×128, while the deeper tool/OpenAPI documentation also describes 256×256 support. This spike deliberately uses 128×128 to minimize cost and API ambiguity. It is a diagnostic canvas, not a final production resolution. If the Exilada loses too much authored detail at this scale, that is itself a valid rejection result.

## Fixed test contract

- Source: canonical `exilada_master.png`; never regenerated or redesigned.
- Canvas: 128×128.
- Seed: `20260904`.
- Palette: 24 exact frequent foreground colors extracted deterministically from the canonical master; the same palette image is sent for the whole request.
- Camera: `side`.
- Direction: `south-east`.
- One API generation request producing exactly four poses:
  1. left contact;
  2. left passing;
  3. right contact;
  4. right passing.
- Skeleton source: PixelLab `/v2/estimate-skeleton` on the normalized canonical master.
- Motion authoring: deterministic local transformation of that estimated skeleton; no video driver and no text-generated motion.
- Reference guidance: 1.1.
- Pose guidance: 3.0.
- No inpainting.
- No init-image repair loop.
- No manual skeleton corrections.
- No retries or seed search.

The script accepts both currently observed PixelLab keypoint coordinate conventions by detecting whether the estimator returned normalized or pixel coordinates, then writing the four poses back in the same convention.

## API cost

The run performs one animation call plus five skeleton-estimation calls (one reference + four output QA estimates). At PixelLab's public prices observed in September 2026 this should be roughly USD 0.04–0.05. The script reads the account balance first when the endpoint is available and refuses to start if it is below a conservative USD 0.06 budget.

## Authentication

Get the PixelLab secret token from the PixelLab account page. Do not commit it. `run_spike.ps1` prompts securely if `PIXELLAB_SECRET` is not already set in the PowerShell session.

## Run

```powershell
cd "D:\GOOGLE DRIVE\DEV\Roguelite"
git pull
cd tools\pixellab-skeleton-spike
Set-ExecutionPolicy -Scope Process Bypass
.\run_spike.ps1
```

No GPU installation is required; PixelLab inference runs in the cloud. The local venv contains only Requests, Pillow and NumPy.

## Files written to `D:\AI\PixelLabSkeletonSpike`

- `exilada_reference_128.png` — automatically cropped/background-isolated diagnostic reference; not a redesigned master.
- `palette.png`, `palette.json` — fixed palette guidance.
- `reference_skeleton.json/.png` — API-estimated rig.
- `target_pose_0..3.json/.png` — four deterministic walk poses.
- `frame_0..3.png` — PixelLab output frames.
- `frame_0..3_estimated_skeleton.json/.png` — skeletons re-estimated from outputs for pose QA.
- `contact_sheet.png` — reference + four outputs.
- `spike_manifest.json` — seed, route, palette, camera and no-retry policy.
- `qa_report.json`, `qa_report.md` — deterministic pre-gate.

## Automatic QA

The pre-gate rejects on any of these classes:

- pose mean error > 0.10 normalized image width/height;
- pose P90 error > 0.18;
- less than 80% of foreground pixels within RGB distance 18 of the fixed palette;
- excessive unique-color count;
- character foreground area outside 0.65–1.35× the normalized reference;
- character height outside 0.75–1.25× reference;
- excessive head color-distribution drift;
- excessive torso/clothing color-distribution drift;
- generated opposite-contact motion amplitude below 0.50× or above 1.80× the target skeleton amplitude.

These metrics are a deterministic pre-gate, not a claim that semantic identity can be perfectly measured numerically. Even a numeric PASS still requires visual inspection of `contact_sheet.png` against the canonical Exilada. **No failed frame may be manually repaired.**

## Stop rule

If the automatic report says `FAIL`, Pixel Engine is prohibited for this pipeline. If the report says `PASS` but visual review shows identity, anatomy, hair, clothing/chains or modern-pixel-art construction failed materially, reject PixelLab without tuning loops.

Only a clean four-frame PASS authorizes a separate Pixel Engine `/keyframes` spike.
