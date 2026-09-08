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

Runner 40 reached a valid Wan inference on the W1A ref-1.5 branch, but visual quality became materially worse.

Final W1G v3.1 facts:

- detector-agnostic temporal-median foreground tracking;
- detected `29/37` analyzed frames;
- constant scale `0.420722...`;
- output safety margins passed after target bottom y was corrected to `580`;
- prompt id `e6d3e6a8-553d-4317-80b1-102881624276`;
- elapsed `1838.11 s`;
- output SHA256 `4450a4737f437aa80e3aef53c8fa66dfc5d4b103b0b41a70c4cc82c1856c30d0`.

Visual failure class:

- stronger global ghosting/smearing;
- unstable/elongated body and limbs;
- detached/duplicated-looking extremities in motion phases;
- loss of the clean body coherence that motivated ref strength 1.5.

Conclusion: **driver tracking/repositioning is closed.** Do not continue synthetic per-frame affine camera-follow or trajectory cancellation.

## Root framing geometry — IMPORTANT

Current ComfyUI `WanAnimate2ToVideo` center-resizes `pose_video` to the requested Wan width/height using `common_upscale(..., "area", "center")`.

Official raw driver: `480×854`, aspect ≈ `0.5621`.

Upstream Wan-Animate-2 demo default: `720×1280`, aspect `0.5625`.

W0/W1/W1A canvas: `640×800`, aspect `0.8`.

For the `480×854` source, center-cropping to aspect `0.8` retains only about **70.3% of source height**, discarding roughly **29.7% vertically** before pose conditioning.

This explains the inherited top/body crop substantially better than the previous letterbox/tracker hypotheses.

## W1H — ASPECT-MATCHED RAW DRIVER / GEOMETRY PASS + NEW BEST BASELINE

Runner 41 changed only Wan generation geometry relative to W1A:

- `640×800 -> 512×912`;
- original raw driver untouched;
- reference strength stays `1.5`;
- all sampler/model/prompt/motion settings otherwise unchanged.

Completed evidence:

- status `INFERENCE_COMPLETE`;
- prompt id `5299b50f-a38d-4cf1-b71e-7022319067d7`;
- elapsed `1672.46 s`;
- output SHA256 `84756f74af5f01aed8329b6a9b7b116149c6abcfd6e6349399c5de8ecf575af1`;
- raw driver `480×854`, aspect `0.562061`;
- W1H canvas `512×912`, aspect `0.561404`;
- estimated pose-video center-crop retention improves from `70.26%` in W1A to `99.88%` in W1H.

Full 37-frame visual review:

- the previous catastrophic top/head/right-body crop is resolved;
- complete body is retained through the sequence to a degree not achieved by W1/W1A/W1F/W1G;
- body topology is materially more coherent than W1G and generally stronger than W1A;
- hair mass and cloth remain dynamic rather than rigid;
- later frames are substantially cleaner and more legible;
- residual destructive blur/smear remains mainly in the fast-motion phase around frames ~8–10;
- restraint/chain topology is still imperfect, including a loose/knotted chain-like mass near the raised hand in late frames;
- a few extremities approach/touch lateral frame edges because the **raw source performer itself traverses the frame**. Do not reintroduce tracking to overfit this official driver; final W2 drivers should be chosen with safer real-world margins.

Classification: **W1H = PASS for the canvas/aspect hypothesis and current best Wan production baseline.**

Policy learned: preserve the raw driver's spatial/temporal motion and choose a Wan generation canvas whose aspect closely matches the raw driver. Do not force arbitrary driving footage into the old `640×800` generation aspect.

## Runner 42 — CURRENT GATE: W1I RESIDUAL BLUR REDUCTION

Runner:

`tools/structured-2d-character-pipeline/42_run_wan_animate2_bf16_w1i_pose_end70_ref15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1i_pose_end70_ref15.py`

Parent = exact completed W1H prompt/geometry.

Only experimental axis relative to W1H:

- `pose_end_percent: 1.00 -> 0.70`.

Rationale:

- W1H already solved the dominant framing/aspect problem and reduced much of the destructive topology loss;
- residual blur is now concentrated in high-motion phases;
- native `WanAnimate2ToVideo` documentation states motion is mostly established early and explicitly gives `pose_end_percent≈0.7` as an example that can loosen fine detail while retaining choreography;
- this is therefore the least invasive native blur-control test before changing pose strength, prompt, seed or model.

Everything else remains W1H:

- original raw driver untouched;
- `512×912` aspect-matched canvas;
- Exilada reference/prompt;
- BF16 stack;
- 37 frames / 16 fps;
- 20 steps;
- CFG 1.0;
- Euler/simple;
- shift 5.0;
- seed 0;
- pose strength 1.0;
- pose start 0.0;
- reference strength 1.5;
- CLIP pose branch unchanged;
- negative prompt unchanged.

Expected outputs:

- `Z:\AI\WanAnimate2\w1i_exilada_poseend70_ref15.mp4`
- `Z:\AI\WanAnimate2\w1i_run_manifest.json`
- `Z:\AI\WanAnimate2\w1i_api_prompt.json`
- `Z:\AI\WanAnimate2\w1i_executor.log`

Success criterion: reduce destructive blur/ghosting in the fast-motion frames **without** losing W1H's body topology, raw-motion adherence, hair/cloth dynamics or framing behavior.

## Exact current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\42_run_wan_animate2_bf16_w1i_pose_end70_ref15.ps1"
```
