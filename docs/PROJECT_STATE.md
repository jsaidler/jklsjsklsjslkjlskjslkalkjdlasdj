# Roguelite — Current Project State

Status date: **2026-09-08**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VISUAL_DIRECTION.md`
3. `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`
4. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
5. `docs/ANIMATION_PIPELINE.md`
6. `docs/CHARACTERS.md`
7. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing action updates the thematic docs, this file and the active handoff before completion is reported.

## Local paths — LOCKED

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- active Wan workspace: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` is stale/historical.

## Runtime / game presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic-like gameplay camera;
- native game raster `640×360`;
- pitch `26°`;
- protagonist about `128 px` tall;
- first locomotion family screen-left / mostly lateral-three-quarter;
- `72°` current screen-left baseline;
- runtime consumes **complete precomposed character sprites** only.

Production contract:

`complete appearance reference + raw driving video + automatic preprocessing -> complete animated frames -> automatic extraction/packing -> spritesheet/atlas + metadata -> ordinary sprite playback`

No routine manual rigging, keyframing, simulation repair, mask repair, repainting or hand compositing.

## Visual direction — LOCKED AFTER WAN W1

The earlier hard modern-pixel-art requirement is superseded. Current target:

- painterly / illustrated 2D dark fantasy;
- explicit 1980s sword-and-sorcery charge;
- Heavy Metal, Conan, Red Sonja, Frank Frazetta, Julie Bell lineage;
- adult sensuality/nudity legitimate;
- localized restrained blur may be positive;
- destructive blur/ghosting that erases anatomy/topology/readability is a defect;
- later Exilada art gate may use more severely torn cloth, more body exposure and possible partial breast exposure consistent with captivity/damage.

## Model order / cleanup — LOCKED

1. Wan-Animate-2 — exhaust first.
2. SCAIL-2 — only after documented Wan `EXHAUSTED_FAIL`.

Do not accumulate unused large checkpoints. Preserve small manifests/logs/results. Keep the active Wan BF16 route and SSD comparison evidence for now.

## Active Wan BF16 set

- `wan_animate_2_bf16.safetensors`
- `umt5_xxl_fp16.safetensors`
- `clip_vision_h.safetensors`
- `Wan2_1_VAE_bf16.safetensors`

`--disable-pinned-memory` remains the proven RTX 3060/ComfyUI infrastructure workaround.

## W0 — PASS_BASELINE

Runner 36 proved local Base-BF16 direct-driving integration.

## W1 — APPROVED VISUAL/MOTION BASELINE

Runner 37, Exilada + official raw driver, `reference_image_strength=1.0`.

Positive evidence: strong cross-identity motion transfer, non-rigid hair, cloth response, approved painterly look.

Open defects: crop, restraint/chain drift, some limb artifacts/blur.

## W1A — REF 1.5 / STRUCTURAL BRANCH RETAINED

Runner 38 changed only `reference_image_strength 1.0 -> 1.5`.

User review supersedes the earlier sharpness-weighted assistant verdict:

- `1.5` preserves body structure/topology better;
- `1.0` is cleaner in several phases;
- `1.5` introduces more destructive blur/ghosting;
- preserve `1.5` as the structural branch and solve blur separately.

## W1F — WHOLE-FRAME LETTERBOX / CROP FAIL

Runner 39 put the entire `480×854` raw driver inside a `640×800` canvas without temporal tracking. Generated crop remained. Do not iterate simple 70/60/50% letterbox variants.

## W1G — TRACKED DRIVER REFRAMING / CLOSED FAIL

Runner 40 eventually reached a valid Wan inference on the W1A ref-1.5 branch.

Final W1G v3.1 facts:

- detector-agnostic temporal-median foreground tracking;
- detected `29/37` analyzed frames;
- constant scale `0.420722...`;
- output safety margins passed after target bottom y was corrected to `580`;
- prompt id `e6d3e6a8-553d-4317-80b1-102881624276`;
- elapsed `1838.11 s`;
- output SHA256 `4450a4737f437aa80e3aef53c8fa66dfc5d4b103b0b41a70c4cc82c1856c30d0`.

Visual verdict from the generated video: **materially worse than W1/W1A**.

Observed failure class:

- stronger global ghosting/smearing;
- unstable/elongated body and limbs;
- detached/duplicated-looking extremities in motion phases;
- loss of the clean body coherence that motivated ref strength 1.5;
- framing still not reliably solved by the generated sequence.

Conclusion: **close the branch that modifies/retracks/repositions raw-driver pixels to solve framing.** Wan consumes the raw video as richer spatiotemporal conditioning; cancelling performer traversal with synthetic per-frame affine camera motion damages the signal. Do not continue tracker tuning.

Keep W1G mp4/log/manifests only as small failure evidence; no new large model assets were added.

## Root framing geometry discovered — IMPORTANT

Current ComfyUI `WanAnimate2ToVideo` center-resizes `pose_video` to the requested Wan width/height using `common_upscale(..., "area", "center")`.

Our official raw driver is `480×854`, aspect ≈ `0.5621`.

Upstream Wan-Animate-2's own demo defaults are `720×1280`, aspect `0.5625` — essentially the same portrait geometry.

But W0/W1/W1A were run at `640×800`, aspect `0.8`.

For a `480×854` source, a center crop to aspect `0.8` retains only about **70.3% of the source height**, discarding roughly **29.7% vertically** before pose conditioning. This is now the leading explanation for the inherited framing problem.

W1F avoided that crop by letterboxing but shrank the subject; W1G altered temporal geometry and damaged motion. The next test must therefore leave the raw driver untouched and fix the **generation canvas aspect**, not the driver.

## Runner 41 — CURRENT GATE: W1H RAW DRIVER + ASPECT-MATCHED CANVAS + REF 1.5

Runner:

`tools/structured-2d-character-pipeline/41_run_wan_animate2_bf16_w1h_aspect_matched_ref15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1h_aspect_matched_ref15.py`

Parent = exact W1A prompt.

Only experimental axis relative to W1A:

- Wan output geometry `640×800 -> 512×912`.

Why `512×912`:

- aspect ≈ `0.5614`, within ~0.12% of the `480×854` raw driver;
- almost no center-crop loss in the pose-video path;
- fewer total pixels than `640×800`, so it is not a heavier inference;
- keeps the raw driver **completely untouched** — no letterbox, tracking, translation cancellation or synthetic camera motion.

Everything else remains W1A:

- Exilada reference/prompt;
- original raw driver;
- BF16 model stack;
- 37 frames, 16 fps output, 20 steps;
- CFG 1.0, Euler/simple, shift 5.0, seed 0;
- pose strength 1.0;
- reference strength 1.5;
- CLIP pose branch unchanged;
- negative prompt unchanged.

Expected outputs:

- `Z:\AI\WanAnimate2\w1h_exilada_aspectmatched_ref15.mp4`
- `Z:\AI\WanAnimate2\w1h_run_manifest.json`
- `Z:\AI\WanAnimate2\w1h_api_prompt.json`
- `Z:\AI\WanAnimate2\w1h_executor.log`

Success criterion:

1. substantially better full-body framing than W1A;
2. no W1G-style temporal/anatomical degradation;
3. preserve W1A's stronger body-structure retention;
4. if framing passes, attack destructive blur as the next isolated axis.

## Exact current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\41_run_wan_animate2_bf16_w1h_aspect_matched_ref15.ps1"
```
