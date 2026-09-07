# G3S — Complete-character animation model screening

Status date: **2026-09-07**

Status: **CANONICAL / RAW-VIDEO MOTION CONTRACT LOCKED / WAN W0 PASS_BASELINE / W1 APPEARANCE CONFIGURATION FAIL WITH POSITIVE MOTION EVIDENCE / W1A ACTIVE / FRAMING GATE NEXT / SCAIL-2 NEXT ONLY IF WAN EXHAUSTS**

## Purpose

Select only model classes capable of generating the Exilada as a complete animated character from two distinct references:

1. `exilada_master.png` owns appearance/state;
2. arbitrary real driving video owns movement/performance.

The model must consume richer information than a body skeleton and automatically infer locomotion, body soft response/jiggle, long-hair inertia, cloth/material/wind response and restraint/accessory dynamics. Routine manual repair is forbidden.

## Candidate ranking

1. **Wan-Animate-2 / Wan2.2-Animate-2-14B** — active exhaustion pass.
2. **SCAIL-2** — only after documented Wan `EXHAUSTED_FAIL`.
3. DreamActor-M2 — benchmark; no confirmed self-hostable production route.
4. Kling Motion Control — hosted comparator only.

Pose-only Moore/AnimateAnyone and current Moore+released-SSD-UNet compatibility route remain research evidence, not final production candidates. Exact public SSD remains `BLOCKED` by the missing custom pose-guider checkpoint.

## Model exhaustion protocol — LOCKED

A model reaches `EXHAUSTED_FAIL` only after finite controlled tests. Runtime/loader failures are infrastructure failures, not model-quality evidence. A valid but insufficient visual result is a configuration failure until meaningful native controls are exhausted. No seed fishing and no manual rescue.

## Wan Base-BF16 route

Canonical local set:

- `wan_animate_2_bf16.safetensors` ~32.8 GB;
- `umt5_xxl_fp16.safetensors` ~11.4 GB;
- `clip_vision_h.safetensors` ~1.26 GB;
- `Wan2_1_VAE_bf16.safetensors` ~0.254 GB.

Total ~45.7 GB. Lower-precision/Distilled variants are not retained in advance.

## W0 official baseline — PASS_BASELINE

Runner: `tools/structured-2d-character-pipeline/36_run_wan_animate2_bf16_w0.ps1`

Attempt 1 failed in ComfyUI AIMDO host-buffer streaming with `hostbuf_file_reader_read failed`; infrastructure only.

Attempt 2 added only `--disable-pinned-memory` and completed successfully with the official demo1 reference + driver at `640×800`, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0 and conditioning strengths 1.0.

Inference time ~1896.94 s (~31m37s).

Visual result: substantial motion transfer, stable cat/species identity and costume, no catastrophic topology collapse. Some blur/framing movement exists. Conclusion: **local direct-driving Base-BF16 integration works.**

## W1 Exilada + official driver — COMPLETE

Runner: `tools/structured-2d-character-pipeline/37_run_wan_animate2_bf16_w1_exilada.ps1`

Executor: `tools/wan-animate2-spike/run_w1_from_w0_prompt.py`

W1 kept movement/execution identical to W0 and changed the target appearance package to Exilada reference + matching appearance prompt.

Observed run facts:

- `INFERENCE_COMPLETE`;
- reference SHA256 `e8422ec9c7125eec8bf534e13cf0ceac9c2ade5e6e2f18cf26cd8f22e59755ab`;
- same official driver;
- Base BF16 stack unchanged;
- `640×800`, 37 frames, 16 fps, 20 steps;
- CFG 1.0, Euler/simple, shift 5.0, seed 0;
- pose/reference strengths 1.0;
- elapsed 1746.69 s (~29m07s);
- output SHA256 `2bbbf3bd0c5b0db46bc1e9d33abd003b7f3627c8fba7880f45d62724f6ab233f`.

### W1 positive evidence

- substantial cross-identity motion transfer survives;
- no visible cat identity/costume leakage;
- long black hair mass changes silhouette and trails through motion rather than staying rigid, demonstrating non-rigid inference beyond body skeleton alone;
- ragged hip cloth changes drape with pose/motion;
- coarse Exilada package remains recognizable: adult woman, olive/brown skin, very long dark hair, minimal beige wraps, barefoot state, wounds/wear and at least one ankle restraint/chain.

### W1 failures

- art language is smooth/painterly, not the required discrete modern pixel/game-art appearance, despite explicit prompt wording;
- face/body details drift and become more generic/muscular/illustrative than the approved target;
- wrist restraint/chain information is largely lost and surviving ankle chain morphology is unstable;
- some hand/foot blur/stretch and a transient detached artifact occur;
- later head/upper-body crop follows the same framing tendency already visible in W0, so treat it as driver/framing behavior rather than Exilada-specific identity failure;
- this driver does not decisively test target locomotion, strong jiggle or stress-level cloth/wind dynamics.

Classification:

**W1 = motion/raw-video-class positive evidence + production-appearance `CONFIGURATION FAIL`.**

Do not reject Wan.

## Native reference-strength control — decisive current variable

Current native ComfyUI `WanAnimate2ToVideo` documents `reference_image_strength` with default `1.0` and states that values above `1.0` tighten generated-frame attention to the reference image latent. `pose_strength` is a separate control for driving-motion influence.

## W1A — CURRENT: reference strength 1.5

Runner:

`tools/structured-2d-character-pipeline/38_run_wan_animate2_bf16_w1a_refstrength15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1a_reference_strength.py`

Exact one-variable change from completed W1:

`reference_image_strength 1.0 -> 1.5`

Everything else remains fixed, including Exilada reference/prompt, official driver, Base BF16 stack, `640×800`, 37 frames, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0, pose strength 1.0, negative prompt and `--disable-pinned-memory`.

Judge W1A against W1 on face/body/reference identity, art-language preservation, hair/clothing/accessory persistence, topology/artifact rate and motion loss.

## Framing/crop gate — LOCKED NEXT AFTER W1A

Crop is a hard production blocker. Do not attempt to repair it after generation by cropping/repositioning the result; missing pixels cannot be recovered.

Because W0 and W1 show the same late-frame crop tendency despite unrelated reference characters, the primary hypothesis is **driving-video geometry/framing**, not target-character identity.

After W1A chooses the better reference strength, perform a dedicated one-variable framing test with that winning appearance configuration. Automatically preprocess the same driver before Wan by:

- detecting/tracking the performer over the clip;
- deriving a temporally stable/smoothed subject envelope;
- fitting the full visible body plus safety margin inside fixed `640×800`;
- preserving aspect ratio;
- padding/letterboxing instead of destructive center-cropping;
- keeping subject scale and center constant or smoothly varying;
- using no manual masks/keyframes/per-frame crop edits.

Success criterion: head and feet remain inside the generated frame throughout motion without materially weakening motion transfer or increasing topology drift.

If validated, this automatic framing normalization becomes mandatory preprocessing for arbitrary Internet drivers.

## Art-direction prompt gate — AFTER FRAMING

Only after framing is controlled should we change the appearance prompt toward the approved aesthetic refinement: stronger 1980s barbarian/sword-and-sorcery influence, more torn fabric and more body exposure. Keep that test separate from framing and reference-strength calibration.

## Wan exhaustion sequence

- W0 official baseline — **PASS_BASELINE**.
- W1 Exilada + official driver, reference strength 1.0 — **CONFIGURATION FAIL for production appearance; motion evidence positive**.
- W1A reference strength 1.5 — **CURRENT**.
- framing/crop normalization gate — **NEXT**.
- art-direction prompt gate.
- W2 target Internet walking driver.
- W3 secondary-motion stress video.
- W4 finite hypothesis-driven variants only if needed.

After W4 classify Wan as `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## Cleanup discipline

Keep only large files tied to the active Wan hypothesis. Do not download duplicate quantizations/Distilled checkpoints in advance. Preserve small manifests/logs/results. Keep `Z:\AI\SpriteSheetDiffusionSpike` temporarily as comparison/fallback evidence until Wan reaches a production verdict.