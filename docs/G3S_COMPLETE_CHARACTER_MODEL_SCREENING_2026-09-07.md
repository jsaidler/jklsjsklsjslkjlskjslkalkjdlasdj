# G3S — Complete-character animation model screening

Status date: **2026-09-07**

Status: **CANONICAL / RAW-VIDEO MOTION CONTRACT LOCKED / WAN W0 PASS_BASELINE / W1 PAINTERLY DIRECTION APPROVED / W1A STRUCTURAL 1.5 BRANCH RETAINED / W1F WHOLE-FRAME LETTERBOX FAILED CROP / W1G DETECTOR-AGNOSTIC SUBJECT FRAMING ACTIVE / SCAIL-2 NEXT ONLY IF WAN EXHAUSTS**

## Purpose

Select only model classes capable of generating the Exilada as a complete animated character from:

1. `exilada_master.png` for appearance/state;
2. arbitrary real driving video for movement/performance.

The model must consume richer information than a body skeleton and automatically infer locomotion, soft-body/jiggle, long-hair inertia, cloth/material/wind response and restraint/accessory dynamics. Routine manual repair is forbidden.

## Candidate ranking

1. **Wan-Animate-2 / Wan2.2-Animate-2-14B** — active exhaustion pass.
2. **SCAIL-2** — only after documented Wan `EXHAUSTED_FAIL`.
3. DreamActor-M2 — benchmark; no confirmed self-hostable production route.
4. Kling Motion Control — hosted comparator only.

Pose-only Moore/AnimateAnyone and current Moore+released-SSD-UNet compatibility remain research evidence, not final production candidates. Exact public SSD remains `BLOCKED` by the missing custom pose-guider checkpoint.

## Model exhaustion protocol — LOCKED

A model reaches `EXHAUSTED_FAIL` only after finite controlled tests. Runtime/loader/preprocessor failures are infrastructure/integration failures, not model-quality evidence. Change one high-leverage variable at a time with fixed seed/input. No seed fishing and no manual rescue.

## Wan Base-BF16 route

Canonical local set:

- `wan_animate_2_bf16.safetensors` ~32.8 GB;
- `umt5_xxl_fp16.safetensors` ~11.4 GB;
- `clip_vision_h.safetensors` ~1.26 GB;
- `Wan2_1_VAE_bf16.safetensors` ~0.254 GB.

Lower-precision/Distilled variants are not retained in advance.

## W0 official baseline — PASS_BASELINE

Runner 36 reproduced the official direct-driving path at `640×800`, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0.

Attempt 1 failed in AIMDO host-buffer streaming. Relaunching ComfyUI with only `--disable-pinned-memory` fixed the infrastructure issue.

Conclusion: the local Base-BF16 direct-driving integration works.

## W1 — Exilada / reference strength 1.0

Runner 37 proved substantial cross-identity raw-video motion transfer, no cat identity/costume leakage, non-rigid long-hair motion, hip-cloth drape changes and coarse Exilada identity/state retention.

Open technical issues:

- restraints/chains are unstable/incomplete;
- some hand/foot blur/stretch and transient artifacts occur;
- late head/upper-body crop;
- official driver is not sufficient to judge target walking/jiggle/wind.

### Visual-language reclassification

The W1 painterly illustrated result was explicitly approved as a highly desirable whole-game visual direction. Smooth/painterly rendering is no longer a failure by itself. Localized/restrained motion blur may be positive; destructive blur that erases anatomy/topology remains a defect.

The art direction deliberately includes an **1980s sword-and-sorcery charge** aligned with Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell.

## W1A — reference strength 1.5 / REVISED INTERPRETATION

Runner 38 changed only `reference_image_strength: 1.0 -> 1.5`.

Current interpretation after user review:

- `1.5` appears to preserve **body structure/topology** better than `1.0`;
- `1.0` is cleaner/less ghosted in several phases;
- `1.5` introduces more destructive blur/ghosting;
- therefore `1.5` is retained as the **structural branch**, and blur must be tested separately rather than using anatomy loss as the price of sharpness.

Do not state simply that “1.5 lost”.

## W1F — fixed whole-frame safe framing 80% / CROP FAIL

Runner 39 retry completed validly. The whole source frame was placed at `360×640` inside `640×800` with offset `(140,80)`, no source crop and no camera breathing.

Visual result: **crop remains**. Head/hair still leave the top later and the character still reaches the right edge.

Conclusion: scaling/letterboxing the whole driver frame does not control generated-character margins sufficiently. Do not spend runs on 70%/60%/50% whole-frame variants without a new mechanism.

## Native framing semantics relevant to W1G

Current ComfyUI `WanAnimate2ToVideo` resizes `pose_video` to requested width/height using `common_upscale(..., "area", "center")`.

The project graph also sends the first driver frame through `CLIPVisionEncode(crop="center")` into `clip_vision_output_pose`.

Therefore W1G must control the **subject envelope**, not only canvas margins, and must keep that envelope safe inside both the `640×800` pose canvas and the center-square CLIP pose crop.

## W1G — CURRENT: subject framing on reference-strength 1.5 branch

Runner:

`tools/structured-2d-character-pipeline/40_run_wan_animate2_bf16_w1g_subject_framing_ref15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1g_subject_framing_ref15.py`

Parent = exact completed W1A prompt. Thus `reference_image_strength=1.5` remains fixed and **driver geometry is the only experimental axis relative to W1A**.

### W1G v1 — PRE-INFERENCE FAIL

A single temporal-activity union across the first 37 frames expanded to the whole frame and aborted with:

`automatic subject bbox covers almost the whole source frame (1.000)`

Classification: **PREPROCESSOR/INTEGRATION FAIL**. No Wan/model inference occurred.

### W1G v2 — PRE-INFERENCE FAIL / EXACT SUB-CAUSE NOT SURFACED

V2 used OpenCV HOG person detection per frame, interpolated misses, smoothed translation and one constant scale. The surfaced terminal excerpt ended in executor code 2 before any `W1G: prompt_id=...` appeared.

Because the terminal excerpt omitted the executor's specific `W1G: FAIL - ...` line, the exact v2 sub-cause is not asserted. Classification remains **PREPROCESSOR/INTEGRATION FAIL; no Wan inference**.

HOG-only detection is also conceptually too brittle for the production contract because drivers may use arbitrary subject appearance and non-upright poses. The HOG-only path is superseded.

### W1G v3 — ACTIVE

V3 is detector-agnostic for the current fixed-camera official baseline:

1. estimate temporal-median background from the first 37 frames;
2. segment foreground independently per frame;
3. choose/track the dominant coherent foreground component;
4. interpolate missing boxes;
5. expand for head/hair/hands/feet safety;
6. smooth translation only;
7. keep one constant scale, so no zoom/camera breathing;
8. target envelope height ratio `0.48`, center x `300`, bottom y `620` on `640×800`;
9. hard-check canvas and CLIP center-square margins before Wan;
10. use existing `cv2` + `numpy`, with no new detector checkpoint/model.

Runner 40 now also writes and surfaces:

`Z:\AI\WanAnimate2\w1g_executor.log`

so executor failures are no longer hidden behind unrelated ComfyUI stderr.

Everything else remains W1A: Exilada reference/prompt, Base BF16 stack, 37 frames, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0, pose strength 1.0, reference strength 1.5, negative prompt and `--disable-pinned-memory`.

Success criterion:

1. complete head/hair/body stay inside generated frame;
2. W1A's stronger structural retention survives;
3. if so, **blur reduction is the next isolated variable**.

Expected evidence after a valid W1G v3 inference:

- `Z:\AI\WanAnimate2\w1g_exilada_subject_framed_ref15.mp4`;
- `Z:\AI\WanAnimate2\w1g_run_manifest.json`;
- `Z:\AI\WanAnimate2\w1g_api_prompt.json`;
- `Z:\AI\WanAnimate2\w1g_subject_driver_manifest.json`;
- `Z:\AI\WanAnimate2\w1g_executor.log`.

## Art-direction gate — AFTER FRAMING/BLUR

Only after framing and destructive blur are controlled should the appearance prompt change toward the approved refinement:

- stronger 1980s sword-and-sorcery tone;
- more severely torn fabric;
- greater body exposure;
- possible partial breast exposure consistent with damaged clothing;
- preserve adult severe/sensual Exilada identity rather than a clean fantasy costume.

## Wan sequence

- W0 — **PASS_BASELINE**.
- W1 ref 1.0 — painterly visual/motion baseline, but crop/topology issues.
- W1A ref 1.5 — **structural branch retained; blur problem isolated**.
- W1F whole-frame safe80 — **CROP FAIL**.
- W1G v1 global activity union — **PRE-INFERENCE FAIL / no Wan inference**.
- W1G v2 HOG tracking — **PRE-INFERENCE FAIL / no Wan inference**.
- W1G v3 detector-agnostic foreground tracking + constant scale + ref 1.5 — **CURRENT**.
- blur-reduction gate if W1G framing passes.
- art-direction gate.
- W2 target Internet walking driver.
- W3 secondary-motion stress video.
- W4 finite hypothesis-driven variants only if needed.

After W4 classify Wan as `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## Cleanup discipline

Keep only large files tied to active Wan hypotheses. Do not download duplicate quantizations/Distilled checkpoints in advance. Preserve small manifests/logs/results. Keep `Z:\AI\SpriteSheetDiffusionSpike` temporarily as comparison/fallback evidence until Wan reaches a production verdict.
