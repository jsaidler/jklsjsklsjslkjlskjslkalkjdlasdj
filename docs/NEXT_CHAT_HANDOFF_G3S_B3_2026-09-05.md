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

W1A ref 1.5: **structural branch retained**. User review: body topology is better than 1.0, but blur/ghosting is worse. Preserve 1.5 and solve blur later.

W1F: whole-frame letterboxing did not solve crop. Closed.

## W1G — VALID METHOD FAIL / CLOSED

Runner 40 final v3.1 produced a valid Wan inference:

- detector-agnostic foreground tracking;
- 29/37 detections;
- constant scale 0.420722;
- target bottom y 580;
- all margin guards passed;
- prompt id `e6d3e6a8-553d-4317-80b1-102881624276`;
- elapsed 1838.11 s;
- output SHA256 `4450a4737f437aa80e3aef53c8fa66dfc5d4b103b0b41a70c4cc82c1856c30d0`.

Visual result: **worse than W1/W1A** — stronger ghosting/smearing, elongated/unstable limbs/body, detached/duplicated-looking extremities, degraded temporal coherence, framing still not reliably solved.

Conclusion: close all tracking/repositioning/affine manipulation of raw-driver pixels for framing. Wan is using the raw video as richer spatiotemporal conditioning; synthetic camera-follow motion damages that signal.

Keep W1G outputs/logs/manifests only as small failure evidence.

## Important geometry discovery

Current ComfyUI `WanAnimate2ToVideo` center-resizes `pose_video` to requested width/height.

Raw official driver: `480×854`, aspect ≈ 0.5621.

Upstream Wan-Animate-2 demo default: `720×1280`, aspect 0.5625.

Our W1/W1A canvas: `640×800`, aspect 0.8.

Center-cropping 480×854 to aspect 0.8 retains only ~70.3% of source height — about 29.7% vertical loss. This is now the leading framing explanation.

## CURRENT GATE — RUNNER 41 / W1H

Runner:

`tools/structured-2d-character-pipeline/41_run_wan_animate2_bf16_w1h_aspect_matched_ref15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1h_aspect_matched_ref15.py`

Parent = exact W1A prompt.

Only changed axis:

`Wan canvas 640×800 -> 512×912`

The original raw driver remains untouched.

Why 512×912:

- aspect ≈ 0.5614, nearly identical to 480×854 and upstream 720×1280;
- nearly eliminates pose-video center-crop loss;
- fewer pixels than 640×800;
- no tracking, letterbox, translation cancellation or synthetic camera motion.

Everything else stays W1A: Exilada ref/prompt, raw driver, BF16 stack, 37 frames, 16fps output, 20 steps, CFG1, Euler/simple, shift5, seed0, pose strength1, ref strength1.5, CLIP pose branch and negative prompt.

Expected:

- `Z:\AI\WanAnimate2\w1h_exilada_aspectmatched_ref15.mp4`
- `Z:\AI\WanAnimate2\w1h_run_manifest.json`
- `Z:\AI\WanAnimate2\w1h_api_prompt.json`
- `Z:\AI\WanAnimate2\w1h_executor.log`

Pass only if full-body framing materially improves without W1G-style temporal/anatomical degradation. If yes, blur reduction is next.

## Exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\41_run_wan_animate2_bf16_w1h_aspect_matched_ref15.ps1"
```

## After W1H

1. blur-reduction gate if framing passes;
2. separate 1980s / more torn / more exposed Exilada art gate;
3. W2 Internet walking driver;
4. W3 secondary-motion stress footage;
5. finite W4 variants if justified;
6. gameplay-scale validation around 128 px.

## Cleanup

No new large model assets added. Keep active BF16 route. Keep W1G small evidence and SSD comparison workspace until Wan verdict.
