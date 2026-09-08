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

## W1 / W1A

W1 ref1.0 established the approved painterly/motion language but had crop, restraint and limb artifacts.

W1A ref1.5 looked structurally stronger than 1.0 but also more ghosted. That old comparison happened under the original `640×800` geometry and must not be treated as a clean final identity-vs-blur verdict.

## W1F / W1G — CLOSED

- W1F whole-frame letterbox did not solve generated crop.
- W1G tracked/recentered raw driver produced a valid inference but materially worsened ghosting, elongated/unstable limbs and temporal anatomy.

Do not return to safe-box percentage iteration or synthetic frame-to-frame camera-follow/recentering.

## Geometry finding from W1H — EMPIRICALLY LOCKED FOR THE COMFY PATH

Current ComfyUI `WanAnimate2ToVideo` center-resizes/crops `pose_video` to requested generation geometry.

Raw official driver: `480×854`, aspect ≈ `0.5621`.

The old project canvas `640×800` has aspect `0.8`; for this driver that center-crop geometry retains only ~70.3% of source height.

W1H changed only the generation canvas to `512×912` (aspect ≈0.5614), leaving the raw driver untouched, and estimated pose-video retention became `99.88%`.

Important upstream correction: the Wan repository itself contains **different example defaults** — the YAML has `640×800`, while the demo CLI exposes `720×1280`. Therefore do **not** claim one upstream default proves the aspect rule. The rule is retained because the Comfy preprocessing semantics plus the W1H empirical result support it.

Production rule: preserve raw-driver pixels/trajectory and choose generation geometry whose aspect is compatible with the driver. Do not fix framing by altering temporal trajectory.

## W1H — GEOMETRY PASS / CURRENT BEST BASELINE

Runner 41:

- `640×800 -> 512×912` only;
- raw driver untouched;
- ref strength1.5;
- prompt `5299b50f-a38d-4cf1-b71e-7022319067d7`;
- elapsed `1672.46s`;
- SHA256 `84756f74af5f01aed8329b6a9b7b116149c6abcfd6e6349399c5de8ecf575af1`.

Visual verdict:

- dominant head/top/right-body crop resolved;
- complete-body retention and temporal anatomy materially better;
- hair/cloth remain dynamic;
- residual destructive blur/smear remains mainly around fast-motion frames ~8–10;
- multiple structural changes still occur during those motion phases;
- restraint/chain topology remains imperfect.

Classification: **W1H = geometry PASS and current best technical baseline, but not yet production-quality.**

## W1I — POSE END 0.70 / NOT PREFERRED

Runner 42 changed only `pose_end_percent 1.00 -> 0.70`.

- prompt `5d4f23ed-f4bf-4b01-a13f-108b2bf31fe0`;
- elapsed `1526.52s`;
- SHA256 `9a9052f40221878ded69f61e452abeda87cfaa42bde475bb5e9809c04763d054`.

Frame-by-frame output stayed extremely close to W1H. High-motion blur and structural deformation remained. Classification: **valid configuration test / not preferred**. Return pose end to1.0.

## W1J REF1.0 — SUPERSEDED BEFORE EXECUTION

Runner 43 exists as a prepared ref-strength-only test, but the user correctly identified that the remaining failure is too large and includes both heavy blur and structural deformation. Lowering only `reference_image_strength` is therefore no longer the next gate.

Do not run Runner 43 unless later evidence specifically requires an isolated ref-strength comparison.

## Runner 44 — CURRENT GATE: W1K POSE STRENGTH 0.80

Runner:

`tools/structured-2d-character-pipeline/44_run_wan_animate2_bf16_w1k_pose_strength80_ref15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1k_pose_strength80_ref15.py`

Parent = exact W1H.

Only experimental axis relative to W1H:

- `pose_strength: 1.00 -> 0.80`.

Everything else stays W1H:

- raw driver untouched;
- `512×912`;
- reference strength1.5;
- pose start0.0 / pose end1.0;
- seed0;
- 20 steps;
- CFG1.0;
- Euler/simple;
- shift5.0;
- same Exilada reference/prompt/negative/CLIP pose branch.

Why this is a better next test than ref1.0 alone:

- the remaining defect is concentrated in motion phases;
- ComfyUI documents `pose_strength` as the direct scale of the pose video's influence;
- the Animate-2 model path directly scales pose-branch values when pose strength differs from1.0;
- W1I showed that merely ending the pose branch earlier does not help;
- a moderate 20% reduction tests whether over-forced motion conditioning is causing both smear and anatomy distortion without discarding choreography outright.

Pass W1K only if destructive blur **and** structural deformation fall materially while choreography, identity, long-hair motion and cloth dynamics remain acceptable.

If W1K fails decisively, next high-leverage axis is **sampling quality/steps**, not another blind reference-strength tweak.

## Exact current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\44_run_wan_animate2_bf16_w1k_pose_strength80_ref15.ps1"
```
