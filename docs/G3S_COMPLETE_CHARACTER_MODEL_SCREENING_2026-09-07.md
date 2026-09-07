# G3S — Complete-character animation model screening

Status date: **2026-09-07**

Status: **CANONICAL / RAW-VIDEO MOTION CONTRACT LOCKED / WAN W0 PASS_BASELINE / W1 PAINTERLY DIRECTION APPROVED / W1A 1.5 NOT PREFERRED / W1F SAFE-FRAMING ACTIVE / SCAIL-2 NEXT ONLY IF WAN EXHAUSTS**

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

A model reaches `EXHAUSTED_FAIL` only after finite controlled tests. Runtime/loader failures are infrastructure failures, not model-quality evidence. Change one high-leverage variable at a time with fixed seed/input. No seed fishing and no manual rescue.

## Wan Base-BF16 route

Canonical local set:

- `wan_animate_2_bf16.safetensors` ~32.8 GB;
- `umt5_xxl_fp16.safetensors` ~11.4 GB;
- `clip_vision_h.safetensors` ~1.26 GB;
- `Wan2_1_VAE_bf16.safetensors` ~0.254 GB.

Total ~45.7 GB. Lower-precision/Distilled variants are not retained in advance.

## W0 official baseline — PASS_BASELINE

Runner: `tools/structured-2d-character-pipeline/36_run_wan_animate2_bf16_w0.ps1`

Official demo1 reference + driver at `640×800`, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0.

Attempt 1 failed in ComfyUI AIMDO host-buffer streaming with `hostbuf_file_reader_read failed`; infrastructure only.

Attempt 2 changed only `--disable-pinned-memory` and completed successfully.

Visual result: substantial motion transfer, stable official-character identity/costume, no catastrophic topology collapse. Conclusion: local direct-driving Base-BF16 integration works.

## W1 Exilada + official driver — COMPLETE

Runner: `tools/structured-2d-character-pipeline/37_run_wan_animate2_bf16_w1_exilada.ps1`

Observed run:

- `INFERENCE_COMPLETE`;
- Exilada reference SHA256 `e8422ec9c7125eec8bf534e13cf0ceac9c2ade5e6e2f18cf26cd8f22e59755ab`;
- same official driver;
- Base BF16 stack unchanged;
- `640×800`, 37 frames, 16 fps, 20 steps;
- CFG 1.0, Euler/simple, shift 5.0, seed 0;
- pose/reference strengths 1.0;
- elapsed 1746.69 s (~29m07s);
- output SHA256 `2bbbf3bd0c5b0db46bc1e9d33abd003b7f3627c8fba7880f45d62724f6ab233f`.

### W1 positive evidence

- substantial cross-identity raw-video motion transfer;
- no visible cat identity/costume leakage;
- long black hair changes silhouette and trails through motion, proving non-rigid inference beyond skeleton-only control;
- ragged hip cloth changes drape;
- coarse Exilada identity/state remains recognizable.

### W1 remaining technical failures

- wrist restraint/chain information is largely lost; surviving ankle chain morphology is unstable;
- some hand/foot blur/stretch and transient artifacts occur;
- later head/upper-body crop follows the same framing tendency as W0 and is treated as a driver-framing problem;
- official driver does not decide walking/jiggle/strong cloth-wind quality.

### W1 visual-language reclassification — IMPORTANT

The previous classification of smooth/painterly output as an art-style failure is **withdrawn**.

The user explicitly approved the W1 painterly illustrated result as a highly desirable whole-game visual direction. The previous hard modern-pixel-art requirement is superseded in `docs/VISUAL_DIRECTION.md`.

Localized, restrained motion blur is allowed and may be aesthetically positive. It remains a defect only when it erases anatomy, topology or gameplay readability.

The art direction now deliberately includes an **1980s sword-and-sorcery charge** aligned with Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell.

## W1A reference strength 1.5 — COMPLETE / NOT PREFERRED

Runner: `tools/structured-2d-character-pipeline/38_run_wan_animate2_bf16_w1a_refstrength15.ps1`

Uploaded manifest confirms:

- same W1 reference/driver/model/seed/sampler/settings;
- only `reference_image_strength 1.0 -> 1.5` plus output prefix changed;
- elapsed 1912.32 s (~31m52s);
- output SHA256 `2661d339f332a28ca25a3a03aa6a59ccd93a572751fb488de04540a764315bef`.

Direct visual comparison against W1:

- no material improvement in face/body identity, clothing layout or restraint retention;
- painterly rendering remains the same overall language;
- several phases show more blur/ghosting and weaker limb definition;
- crop tendency remains unchanged because the driver is unchanged;
- motion survives but the tradeoff is worse than W1.

Classification:

**W1A is a valid diagnostic but `reference_image_strength=1.5` is not preferred.**

Current preferred conditioning returns to **W1 reference strength 1.0**. Do not escalate reference strength further before solving framing.

## W1F — CURRENT: automatic safe-framing proof

Runner:

`tools/structured-2d-character-pipeline/39_run_wan_animate2_bf16_w1f_safe_framing80.ps1`

Executor:

`tools/wan-animate2-spike/run_w1f_safe_framing.py`

W1F branches from the preferred W1 prompt, not W1A.

One changed diagnostic axis: **driver framing**.

Automatic preprocessing:

- preserve the whole original raw driver frame;
- fit it inside a fixed centered 80% safe box on a `640×800` canvas;
- add stable margins using a fixed background colour estimated from source-frame corners;
- no destructive crop;
- no temporal tracking/camera breathing;
- no manual alignment.

Everything else remains W1: Exilada reference/prompt, Base BF16 stack, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0, pose strength 1.0, reference strength 1.0 and negative prompt.

Hypothesis: containing the raw driver inside a fixed safe canvas will keep generated head/hair/body away from frame edges without weakening motion quality materially.

Expected evidence:

- `Z:\AI\WanAnimate2\w1f_exilada_safe_framing80.mp4`;
- `Z:\AI\WanAnimate2\w1f_run_manifest.json`;
- `Z:\AI\WanAnimate2\w1f_api_prompt.json`;
- `Z:\AI\WanAnimate2\w1f_safe_driver_manifest.json`.

Success criterion: complete head/hair/body remain safely inside the generated frame through the sequence without unacceptable scale loss, motion weakening or new topology drift.

If validated, this safe-framing policy becomes mandatory preprocessing for arbitrary Internet drivers, with later detector/tracker refinement only if needed for more difficult footage.

## Art-direction prompt gate — AFTER W1F

Only after framing is controlled should the appearance prompt change toward the approved refinement:

- stronger 1980s sword-and-sorcery tone;
- more severely torn fabric;
- greater body exposure;
- possible partial breast exposure consistent with damaged clothing;
- preserve adult severe/sensual Exilada identity rather than a clean fantasy costume.

Keep this separate from framing and reference-strength diagnostics.

## Wan exhaustion sequence

- W0 official baseline — **PASS_BASELINE**.
- W1 Exilada + official driver, ref strength 1.0 — **preferred current visual/motion baseline; technical crop/restraint issues remain**.
- W1A ref strength 1.5 — **NOT PREFERRED**.
- W1F safe-framing 80% — **CURRENT**.
- art-direction prompt gate.
- W2 target Internet walking driver.
- W3 secondary-motion stress video.
- W4 finite hypothesis-driven variants only if needed.

After W4 classify Wan as `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## Cleanup discipline

Keep only large files tied to the active Wan hypothesis. Do not download duplicate quantizations/Distilled checkpoints in advance. Preserve small manifests/logs/results. Keep `Z:\AI\SpriteSheetDiffusionSpike` temporarily as comparison/fallback evidence until Wan reaches a production verdict.
