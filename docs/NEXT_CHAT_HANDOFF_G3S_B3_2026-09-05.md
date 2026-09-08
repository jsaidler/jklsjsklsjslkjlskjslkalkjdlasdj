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

W1 ref1.0: approved painterly/motion baseline, but old geometry caused crop and confounded structure assessment.

W1A ref1.5: user review found better body topology but more blur under the old `640×800` geometry.

W1F: whole-frame letterbox failed crop. Closed.

W1G: tracked/recentered raw driver worsened temporal anatomy/ghosting. **Closed; never return to synthetic camera-follow/tracker reframing.**

## Geometry rule — LOCKED

ComfyUI `WanAnimate2ToVideo` center-resizes `pose_video` to generation geometry.

- official driver `480×854`, aspect ≈0.5621;
- upstream default `720×1280`, aspect0.5625;
- old project `640×800`, aspect0.8.

Old geometry retained only ~70.3% of raw-driver height. Production rule: **keep raw driver untouched and match generation aspect to the driver.**

## W1H — GEOMETRY PASS / CURRENT BEST BASELINE

Runner 41 changed only `640×800 -> 512×912`, kept raw driver untouched and ref strength1.5.

- prompt `5299b50f-a38d-4cf1-b71e-7022319067d7`;
- elapsed `1672.46s`;
- SHA256 `84756f74af5f01aed8329b6a9b7b116149c6abcfd6e6349399c5de8ecf575af1`;
- estimated raw-driver retention `99.88%`.

Visual: catastrophic head/right-body crop resolved; body topology/coherence much better than W1G and generally better than W1A; hair/cloth remain dynamic. Residual destructive blur around frames ~8–10 and imperfect late chain/restraint topology remain. Some edge proximity comes from source performer traversal; solve with safer W2 footage, not tracking.

## W1I — POSE END 0.70 / NOT PREFERRED

Runner 42 changed only `pose_end_percent 1.00 -> 0.70` from W1H.

- prompt `5d4f23ed-f4bf-4b01-a13f-108b2bf31fe0`;
- elapsed `1526.52s`;
- SHA256 `9a9052f40221878ded69f61e452abeda87cfaa42bde475bb5e9809c04763d054`.

Frame-by-frame verdict: extremely close to W1H; fast-motion blur remains; no material topology/framing gain. Mixed sharpness proxies do not support a robust perceptual improvement. Classification: **valid configuration test, not preferred**. Return `pose_end_percent` to1.0.

## CURRENT GATE — RUNNER 43 / W1J REF1.0 ON CORRECTED GEOMETRY

Runner:

`tools/structured-2d-character-pipeline/43_run_wan_animate2_bf16_w1j_aspectmatched_ref10.ps1`

Executor:

`tools/wan-animate2-spike/run_w1j_ref10_aspectmatched.py`

Parent = exact W1H, not W1I.

Only changed axis:

`reference_image_strength 1.5 -> 1.0`

Everything else remains W1H: untouched raw driver, `512×912`, pose strength1.0, pose start0.0, pose end1.0, seed0, 20 steps, CFG1, Euler/simple, shift5, same Exilada ref/prompt, CLIP pose branch and negative prompt.

Why: the earlier 1.0-vs-1.5 comparison was confounded by the wrong `640×800` canvas. Test whether ref1.0 now keeps complete topology while recovering cleaner rendering.

Prefer ref1.0 only if destructive blur/ghosting falls materially without reintroducing missing/displaced anatomy, identity loss or weaker hair/cloth motion.

Expected:

- `Z:\AI\WanAnimate2\w1j_exilada_aspectmatched_ref10.mp4`
- `Z:\AI\WanAnimate2\w1j_run_manifest.json`
- `Z:\AI\WanAnimate2\w1j_api_prompt.json`
- `Z:\AI\WanAnimate2\w1j_executor.log`

## Exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\43_run_wan_animate2_bf16_w1j_aspectmatched_ref10.ps1"
```

## After W1J

1. choose ref1.5 or ref1.0 on corrected geometry;
2. separate approved 1980s / more torn / more exposed Exilada art gate;
3. W2 real walking driver with safe real margins;
4. W3 secondary-motion stress footage;
5. finite W4 variants only if justified;
6. gameplay-scale validation around128px.

## Cleanup

No new large model assets added. Keep active BF16 route, small proof/failure evidence and SSD comparison workspace until Wan verdict.
