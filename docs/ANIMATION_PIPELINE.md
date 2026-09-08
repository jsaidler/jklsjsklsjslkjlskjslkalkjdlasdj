# Character Animation Production — Living Decision Record

Status date: **2026-09-07**

Status: **RAW-VIDEO DUAL-REFERENCE COMPLETE-CHARACTER GENERATION IS THE ACTIVE PRODUCTION CLASS. WAN-ANIMATE-2 BASE BF16 REMAINS UNDER CONTROLLED EXHAUSTION. W0 PASSED; W1 PAINTERLY LOOK IS APPROVED; W1A 1.5 IS RETAINED AS THE STRONGER STRUCTURAL BRANCH; W1F WHOLE-FRAME SAFE FRAMING FAILED; W1G DETECTOR-AGNOSTIC SUBJECT FRAMING IS ACTIVE.**

Canonical state: `docs/PROJECT_STATE.md`

Canonical visual direction: `docs/VISUAL_DIRECTION.md`

Canonical model screening: `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`

## Hard production constraints

The pipeline must:

- use `assets/source/characters/exilada/reference/exilada_master.png` as complete appearance/state reference;
- accept a separate real driving video for movement/performance;
- allow the driver performer to differ completely in identity, clothing, hair and accessories;
- preserve Exilada identity, hair mass, clothing state and restraints as far as production quality requires;
- infer locomotion, body soft response, hair inertia, cloth/material/wind response and restraint/accessory motion automatically;
- require no routine manual rigging, keyframing, simulation repair, masks, repainting, per-frame cleanup or hand compositing;
- allow automatic preprocessing/postprocessing;
- output complete visible frames suitable for automatic spritesheet packing.

## Runtime contract — LOCKED

`complete generated frames -> complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

No visible runtime body/hair/clothing/equipment assembly.

## Motion-source rule — LOCKED

Final production motion comes from **real driving video consumed in a richer form than body skeleton alone**. Internet footage is acceptable; costume matching is not required.

Pose/SMPL/mocap may remain diagnostics only.

## Model-exhaustion protocol — LOCKED

Do not switch model families after a single ugly result. Before `EXHAUSTED_FAIL`, reproduce official behavior, validate checkpoint/loader/input semantics, test cross-identity in controlled stages, change one high-leverage variable at a time, keep seed/input fixed unless stochasticity itself is tested, prohibit manual rescue and require decisive failure across a finite valid matrix.

## Active Wan Base-BF16 set

- `wan_animate_2_bf16.safetensors` ~32.8 GB;
- `umt5_xxl_fp16.safetensors` ~11.4 GB;
- `clip_vision_h.safetensors` ~1.26 GB;
- `Wan2_1_VAE_bf16.safetensors` ~0.254 GB.

Lower-precision/Distilled variants are not retained unless a later controlled comparison explicitly needs them.

## W0 — PASS_BASELINE

Runner 36 reproduced the official raw-video path at `640×800`, 37 frames, 16 fps, 20 steps, seed 0. The first attempt hit AIMDO `hostbuf_file_reader_read failed`; adding only `--disable-pinned-memory` resolved the infrastructure issue.

## W1 — APPROVED VISUAL/MOTION BASELINE

Runner 37 used Exilada + the official driver at `reference_image_strength=1.0`.

Positive evidence: substantial cross-identity motion transfer, non-rigid long-hair motion, ragged hip-cloth drape changes, no cat identity/costume leakage and coarse Exilada-state retention.

Technical issues: restraint/chain instability, some hand/foot blur/stretch and transient artifacts, later head/body crop, and insufficient driver coverage for final walking/jiggle/wind quality.

### Visual-language decision

The W1 painterly/illustrated 2D look was explicitly approved as the preferred whole-game direction. Localized, restrained motion blur is allowed when it does not erase anatomy/topology/readability. The visible direction deliberately includes an **1980s sword-and-sorcery charge** aligned with Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell.

## W1A — reference strength 1.5 / STRUCTURAL BRANCH RETAINED

User review supersedes the earlier sharpness-weighted verdict:

- `1.5` preserves body structure/topology better than `1.0`;
- `1.0` is cleaner in some phases;
- `1.5` adds more destructive blur/ghosting;
- keep `1.5` as the structural branch and solve blur independently.

## W1F — WHOLE-FRAME SAFE80 / CROP FAIL

Runner 39 retry completed validly. The entire `480×854` source frame was placed at `360×640` inside `640×800` with offset `(140,80)`, no source crop and no temporal camera breathing.

Visual verdict: **generated crop remained**. Head/hair still leave the top later and the character still pushes into the right edge.

Conclusion: whole-frame letterboxing is not a sufficient framing mechanism. Do not iterate 70%/60%/50% letterbox-only variants.

## Native framing semantics

Current `WanAnimate2ToVideo` center-resizes `pose_video` to the requested size. The graph also feeds the first driver frame through `CLIPVisionEncode(crop="center")` into `clip_vision_output_pose`.

The framing preprocessor therefore must control the **performer/subject envelope itself**, not only canvas margins, while keeping that envelope safe in both the `640×800` pose canvas and the center-square CLIP pose crop.

## W1G — CURRENT SUBJECT-FRAMING GATE ON REF 1.5

Runner:

`tools/structured-2d-character-pipeline/40_run_wan_animate2_bf16_w1g_subject_framing_ref15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1g_subject_framing_ref15.py`

Parent is the exact completed W1A prompt, so `reference_image_strength=1.5` remains unchanged.

### W1G v1 — PRE-INFERENCE FAIL

A global temporal-activity union expanded to the whole frame (`1.000`) and aborted before Wan. Classification: **PREPROCESSOR/INTEGRATION FAIL**.

### W1G v2 — PRE-INFERENCE FAIL

HOG-person tracking also exited before any `W1G: prompt_id=...`. The surfaced excerpt did not contain the specific executor failure line, so the exact sub-cause is not asserted. HOG-only detection is superseded as too semantically brittle for arbitrary driving footage.

### W1G v3 — ACTIVE

The revised framing method:

- estimates a temporal-median background over the first 37 frames;
- segments moving foreground independently per frame;
- tracks the dominant coherent foreground component without assuming a human/animal class;
- interpolates missed detections;
- expands boxes for head/hair/hands/feet safety;
- follows **translation only** with temporal smoothing;
- uses **one constant scale** for all frames, preventing zoom/camera breathing;
- target envelope height ratio `0.48`, center x `300`, bottom y `620` on `640×800`;
- hard-checks top/bottom/side margins before Wan;
- separately hard-checks CLIP center-square margins;
- downloads no detector checkpoint/model.

Runner 40 now tees executor stdout/stderr to `Z:\AI\WanAnimate2\w1g_executor.log` and prints that log on failure.

Everything else remains W1A: Exilada reference/prompt, BF16 stack, 37 frames, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0, pose strength 1.0, reference strength 1.5, negative prompt and `--disable-pinned-memory`.

Success criterion: full head/hair/body remain safely inside generated frame while the stronger W1A structural retention survives.

## Blur gate — AFTER W1G FRAMING PASS

If W1G solves crop while retaining body structure, the next isolated axis is **destructive blur reduction**. Preserve framing and `reference_image_strength=1.5` while testing only native controls that can plausibly reduce ghosting without sacrificing topology.

## Art-direction prompt gate — AFTER FRAMING/BLUR

Once framing and destructive blur are controlled, test separately stronger 1980s sword-and-sorcery language, more severely torn chest/hip cloth, greater body exposure, possible partial breast exposure consistent with damaged fabric, and preserve severe adult Exilada identity/captivity logic.

## Wan sequence

- W0 official baseline — **PASS_BASELINE**;
- W1 Exilada / ref strength 1.0 — **approved visual/motion baseline**;
- W1A ref strength 1.5 — **STRUCTURAL BRANCH RETAINED**;
- W1F safe framing 80% — **CROP FAIL**;
- W1G v1 global activity union — **PRE-INFERENCE FAIL**;
- W1G v2 HOG tracking — **PRE-INFERENCE FAIL**;
- W1G v3 detector-agnostic foreground tracking + constant scale + ref 1.5 — **CURRENT**;
- blur-reduction gate;
- art-direction prompt gate;
- W2 target Internet walking driver;
- W3 secondary-motion stress video;
- W4 finite remaining hypothesis-driven variants.

## SCAIL-2 — NEXT ONLY IF WAN EXHAUSTS

Do not install SCAIL-2 while Wan still has meaningful untested production controls.

## Cleanup discipline — LOCKED

Do not accumulate unused large model variants/materials. Preserve small logs/manifests/results. Keep the active Wan BF16 route while under exhaustion. Keep SSD comparison evidence until a production verdict is reached.

## Immediate operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\40_run_wan_animate2_bf16_w1g_subject_framing_ref15.ps1"
```
