# G3S — Complete-character animation model screening

Status date: **2026-09-07**

Status: **CANONICAL / RAW-VIDEO MOTION CONTRACT LOCKED / WAN W0 PASS_BASELINE / W1 PAINTERLY DIRECTION APPROVED / W1A STRUCTURAL 1.5 BRANCH RETAINED / W1F WHOLE-FRAME LETTERBOX FAILED CROP / W1G TRACKED SUBJECT FRAMING ACTIVE / SCAIL-2 NEXT ONLY IF WAN EXHAUSTS**

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

Runner 37 proved:

- substantial cross-identity raw-video motion transfer;
- no cat identity/costume leakage;
- long black hair moves as a non-rigid mass;
- ragged hip cloth changes drape;
- coarse Exilada identity/state survives.

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

Manifest:

- `INFERENCE_COMPLETE`;
- elapsed `1912.32 s`;
- output SHA256 `2661d339f332a28ca25a3a03aa6a59ccd93a572751fb488de04540a764315bef`.

Current interpretation after user review:

- `1.5` appears to preserve **body structure/topology** better than `1.0`;
- `1.0` is cleaner/less ghosted in several phases;
- `1.5` introduces more destructive blur/ghosting;
- therefore `1.5` is retained as the **structural branch**, and blur must be tested separately rather than using anatomy loss as the price of sharpness.

Do not state simply that “1.5 lost”.

## W1F — fixed whole-frame safe framing 80% / CROP FAIL

Runner 39 retry completed validly after the OpenCV preflight correction.

Manifest facts:

- `INFERENCE_COMPLETE`;
- reference strength `1.0`;
- elapsed `1737.61 s`;
- source `480×854`, 337 frames @30 fps;
- whole source frame placed at `360×640` inside `640×800`, offset `(140,80)`;
- no source crop, no tracking/camera breathing.

Visual result:

**crop remains.** Head/hair still leave the top later and the character still reaches the right edge.

Conclusion:

- scaling/letterboxing the whole driver frame does not control generated-character margins sufficiently;
- do not spend runs on 70%/60%/50% whole-frame variants without a new mechanism.

## Native framing semantics relevant to W1G

Current ComfyUI `WanAnimate2ToVideo` resizes `pose_video` to requested width/height using `common_upscale(..., "area", "center")`.

The current project graph also sends the first driver frame through `CLIPVisionEncode(crop="center")` into `clip_vision_output_pose`.

Therefore W1G must control the **subject envelope**, not only canvas margins, and must keep that envelope safe inside both the `640×800` pose canvas and the center-square CLIP pose crop.

## W1G — CURRENT: tracked subject framing on reference-strength 1.5 branch

Runner:

`tools/structured-2d-character-pipeline/40_run_wan_animate2_bf16_w1g_subject_framing_ref15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1g_subject_framing_ref15.py`

Parent = exact completed W1A prompt. Thus `reference_image_strength=1.5` remains fixed and **driver geometry is the only experimental axis relative to W1A**.

### W1G v1 — PRE-INFERENCE FAIL

The initial W1G preprocessor used one temporal-activity union box across the first 37 frames. It aborted before inference with:

`automatic subject bbox covers almost the whole source frame (1.000)`

Classification: **PREPROCESSOR/INTEGRATION FAIL**. No Wan/model inference occurred.

This result is useful: temporal activity spans essentially the full source frame, so a global union confounds subject traversal/background activity with subject size. A single fixed affine transform is not a meaningful solution for this driver.

### W1G v2 — ACTIVE

The revised preprocessor:

- runs OpenCV built-in HOG person detection independently per frame;
- selects a temporally coherent performer box;
- interpolates missing detections;
- expands for head/hair/hands/feet safety;
- applies **smoothed translation only** frame-to-frame;
- keeps **one constant scale** over the complete analyzed sequence, preventing zoom/camera breathing;
- targets subject-envelope height ratio `0.48`, center x `300`, bottom y `620` on `640×800`;
- preflights minimum top/bottom/left/right margins;
- separately preflights the central square seen by `CLIPVisionEncode(crop="center")`;
- uses existing `cv2` + `numpy`, with no new detector checkpoint/model download.

If the HOG detector cannot produce enough credible boxes, v2 also aborts before Wan rather than falling back to the already-disproven global activity union.

Everything else remains W1A: Exilada reference/prompt, Base BF16 stack, 37 frames, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0, pose strength 1.0, reference strength 1.5, negative prompt and `--disable-pinned-memory`.

Success criterion:

1. complete head/hair/body stay inside generated frame;
2. W1A's stronger structural retention survives;
3. if so, **blur reduction is the next isolated variable**.

Expected evidence after a valid W1G v2 inference:

- `Z:\AI\WanAnimate2\w1g_exilada_subject_framed_ref15.mp4`;
- `Z:\AI\WanAnimate2\w1g_run_manifest.json`;
- `Z:\AI\WanAnimate2\w1g_api_prompt.json`;
- `Z:\AI\WanAnimate2\w1g_subject_driver_manifest.json`.

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
- W1G v2 tracked translation + constant scale + ref 1.5 — **CURRENT**.
- blur-reduction gate if W1G framing passes.
- art-direction gate.
- W2 target Internet walking driver.
- W3 secondary-motion stress video.
- W4 finite hypothesis-driven variants only if needed.

After W4 classify Wan as `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## Cleanup discipline

Keep only large files tied to active Wan hypotheses. Do not download duplicate quantizations/Distilled checkpoints in advance. Preserve small manifests/logs/results. Keep `Z:\AI\SpriteSheetDiffusionSpike` temporarily as comparison/fallback evidence until Wan reaches a production verdict.
