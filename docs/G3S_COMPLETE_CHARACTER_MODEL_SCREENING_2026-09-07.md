# G3S — Complete-character animation model screening

Status date: **2026-09-07**

Status: **CANONICAL / RAW-VIDEO MOTION CONTRACT LOCKED / WAN-ANIMATE-2 W0 PASS_BASELINE / W1 EXILADA ACTIVE / SCAIL-2 NEXT OPEN LOCAL CANDIDATE**

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

A model reaches `EXHAUSTED_FAIL` only after finite controlled tests. Runtime/loader failures are infrastructure failures, not model-quality evidence. No seed fishing and no manual rescue.

## Wan Base-BF16 route

Canonical local set:

- `wan_animate_2_bf16.safetensors` ~32.8 GB;
- `umt5_xxl_fp16.safetensors` ~11.4 GB;
- `clip_vision_h.safetensors` ~1.26 GB;
- `Wan2_1_VAE_bf16.safetensors` ~0.254 GB.

Total ~45.7 GB. Lower-precision/Distilled variants are not retained in advance.

## W0 official baseline — PASS_BASELINE

Runner: `tools/structured-2d-character-pipeline/36_run_wan_animate2_bf16_w0.ps1`

Attempt 1 failed in ComfyUI AIMDO host-buffer streaming with `hostbuf_file_reader_read failed`; this was infrastructure only.

Attempt 2 added only `--disable-pinned-memory` and completed successfully with the official demo1 reference + driver at:

- `640×800`;
- 37 frames;
- 16 fps;
- 20 steps;
- CFG 1.0;
- Euler/simple;
- shift 5.0;
- seed 0;
- conditioning strengths 1.0.

Inference time was about 1896.94 seconds (~31m37s).

Visual diagnosis of the uploaded W0 output:

- complete subject remains coherent across the 37-frame sequence;
- substantial arm/body motion is transferred;
- cat face/species identity remains recognizable;
- uniform, red bow and pleated skirt remain materially persistent;
- no catastrophic extra-limb/topology collapse;
- some motion blur and framing/crop change are present but do not invalidate the baseline.

Conclusion: **the local direct-driving Base-BF16 integration works.**

Important limit: W0 does not establish project fitness because it does not stress Exilada identity, pixel-art preservation, very long hair, ragged cloth, body jiggle or restraints/chains.

## W1 — CURRENT: EXILADA CROSS-IDENTITY / OFFICIAL DRIVER

Runner: `tools/structured-2d-character-pipeline/37_run_wan_animate2_bf16_w1_exilada.ps1`

Executor: `tools/wan-animate2-spike/run_w1_from_w0_prompt.py`

W1 is mechanically derived from the exact successful W0 API prompt.

The official W0 positive text literally describes the official cat character, so the target appearance must change as a coherent package. W1 changes only:

1. reference image -> `exilada_master.png`;
2. positive target-appearance description -> matching canonical Exilada description;
3. output prefix.

Everything that owns movement/execution remains identical: official driver, model files, resolution, 37-frame window, fps, steps, CFG, sampler, scheduler, shift, seed, conditioning strengths and W0 negative prompt.

### W1 decisive QA

Judge:

1. Exilada face/body proportions and adult identity;
2. complete initial-state preservation from the master;
3. long black hair mass persistence and temporal inertia;
4. ragged chest/hip cloth topology and lag;
5. soft-body/jiggle response where motion warrants it;
6. shackles/chains staying attached and temporally plausible;
7. motion adherence to the official driver;
8. hands/feet/limb topology;
9. no leakage of the cat/driver appearance;
10. preservation of discrete modern pixel/game-art language rather than smooth painterly reinterpretation;
11. zero routine manual cleanup.

W1 does not yet decide walking suitability because the official driver is not the target locomotion clip. If W1 establishes identity/style/complete-state viability, advance to W2 with Internet walking footage.

## Wan exhaustion sequence

- W0 official baseline — **PASS_BASELINE**.
- W1 Exilada + official driver — **CURRENT**.
- W2 target Internet walking driver.
- W3 secondary-motion stress video.
- W4 finite hypothesis-driven variants only if needed.

After W4 classify Wan as `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## Cleanup discipline

Keep only large files tied to the active Wan hypothesis. Do not download duplicate quantizations/Distilled checkpoints in advance. Preserve small manifests/logs/results. Keep `Z:\AI\SpriteSheetDiffusionSpike` temporarily as comparison/fallback evidence until Wan reaches a production verdict.