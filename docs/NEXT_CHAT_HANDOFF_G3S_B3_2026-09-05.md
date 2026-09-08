# Next-chat handoff — G3S complete-character spritesheet production

Status date: **2026-09-07**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VISUAL_DIRECTION.md`
3. `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`
4. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
5. `docs/ANIMATION_PIPELINE.md`
6. `docs/CHARACTERS.md`

## Local paths — LOCKED

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- Wan: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` is stale/historical.

## Runtime / production contract — LOCKED

Final runtime uses complete-character spritesheets. Appearance comes from the Exilada master, movement comes from raw driving video, and production must automatically infer body dynamics, long-hair inertia, cloth/material response and restraints/accessories without routine manual repair.

## Visual direction — UPDATED 2026-09-07

The earlier hard final-art pixel-art requirement is superseded.

Current direction:

- painterly illustrated dark-fantasy 2D;
- deliberate **1980s sword-and-sorcery charge**;
- inspirations: **Heavy Metal, Conan, Red Sonja, Frank Frazetta, Julie Bell**;
- localized/restrained blur may be positive;
- destructive blur that erases anatomy/topology is not acceptable;
- adult sensuality/nudity must not be sanitized by default;
- later art-direction test: more severely torn cloth, more body exposure, possible partial breast exposure consistent with damage/state.

## Candidate order

1. Wan-Animate-2 — exhaust first.
2. SCAIL-2 — only after Wan reaches `EXHAUSTED_FAIL`.

## Active Wan Base-BF16 set

- `wan_animate_2_bf16.safetensors` ~32.8 GB
- `umt5_xxl_fp16.safetensors` ~11.4 GB
- `clip_vision_h.safetensors` ~1.26 GB
- `Wan2_1_VAE_bf16.safetensors` ~0.254 GB

## W0 — PASS_BASELINE

Runner 36 reproduced official Base BF16 at `640×800`, 37 frames, 16 fps, 20 steps, seed 0. `--disable-pinned-memory` is the proven infrastructure workaround.

## W1 — Exilada / ref 1.0

Strong raw-video motion, non-rigid hair/cloth response and approved painterly look. Problems: chain/restraint drift, some limb artifacts, destructive blur in places, and late crop.

## W1A — ref 1.5 / STRUCTURAL BRANCH RETAINED

Runner 38 changed only `reference_image_strength 1.0 -> 1.5`.

Revised interpretation after user review:

- `1.5` preserves body structure/topology better;
- `1.0` is cleaner in some phases;
- `1.5` has more destructive blur/ghosting;
- keep `1.5` as the structural branch and solve blur separately.

Do not summarize W1A as simply “1.5 lost”.

## W1F — whole-frame safe80 / COMPLETE / CROP FAIL

Runner 39 retry completed validly.

Manifest:

- ref strength 1.0;
- elapsed 1737.61 s;
- source 480×854 / 337 frames @30 fps;
- whole source placed 360×640 in 640×800 at offset `(140,80)`;
- no source crop or camera breathing.

Visual result: **crop remains**. Head/hair still leave top later; character still pushes right.

Conclusion: whole-frame letterbox margins do not map to equivalent Wan output margins. Do not waste time on simple 70%/60%/50% letterbox variants.

## Relevant native semantics

Current `WanAnimate2ToVideo` center-resizes `pose_video` to requested size. The project graph also feeds the first driver frame through `CLIPVisionEncode(crop="center")` into `clip_vision_output_pose`.

The normalizer therefore must control the **subject envelope itself** and keep it safe inside both the 640×800 pose canvas and the CLIP center square.

## CURRENT GATE — RUNNER 40 / W1G TRACKED SUBJECT FRAMING + REF 1.5

Runner:

`tools/structured-2d-character-pipeline/40_run_wan_animate2_bf16_w1g_subject_framing_ref15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1g_subject_framing_ref15.py`

Parent = exact completed W1A prompt, therefore reference strength remains 1.5. Relative to W1A, only driver geometry changes.

### W1G v1 — PRE-INFERENCE FAIL

The first subject-framing implementation used temporal-activity segmentation and one global activity union over the first 37 frames.

It aborted before inference with:

`automatic subject bbox covers almost the whole source frame (1.000)`

Classification: **PREPROCESSOR/INTEGRATION FAIL; no Wan inference.**

Interpretation: whole-frame temporal activity makes the global union meaningless for this clip. The safety guard worked and prevented wasting an inference.

### W1G v2 — CURRENT IMPLEMENTATION

The executor now:

- detects the performer independently per frame using OpenCV's built-in HOG person detector;
- selects a temporally coherent box;
- interpolates missed detections;
- expands for head/hair/hands/feet safety;
- smooths translation across time;
- uses **one constant scale** for the sequence, so there is no zoom/camera breathing;
- target envelope height ratio `0.48`;
- target center x `300`;
- target bottom y `620`;
- hard pre-inference margin guard on 640×800;
- hard guard for the CLIP center-square crop;
- no new detector checkpoint/model download.

If not enough credible person detections are found, the run aborts before Wan rather than reverting to the failed global-activity method.

Everything else remains W1A: Exilada reference/prompt, Base BF16 stack, 37 frames, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0, pose strength 1.0, ref strength 1.5, negative prompt and `--disable-pinned-memory`.

Expected outputs after a valid inference:

- `Z:\AI\WanAnimate2\w1g_exilada_subject_framed_ref15.mp4`
- `Z:\AI\WanAnimate2\w1g_run_manifest.json`
- `Z:\AI\WanAnimate2\w1g_api_prompt.json`
- `Z:\AI\WanAnimate2\w1g_subject_driver_manifest.json`

Success criterion: complete head/hair/body stay in frame while W1A's stronger structural retention survives. If this passes, **blur reduction is next**, before art-direction prompt changes.

## Exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\40_run_wan_animate2_bf16_w1g_subject_framing_ref15.ps1"
```

## After W1G

1. isolate blur reduction if framing passes;
2. separate 1980s/torn-clothing/body-exposure art-direction prompt test;
3. W2 Internet walking driver;
4. W3 secondary-motion stress footage;
5. finite W4 variants only if justified;
6. validate approved painterly language at actual ~128 px gameplay occupancy.

## Cleanup discipline

Unused large models/materials must not accumulate. Keep the active BF16 route while Wan is under exhaustion. Keep SSD comparison evidence temporarily until Wan reaches a production verdict.
