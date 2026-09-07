# Next-chat handoff — G3S complete-character spritesheet production

Status date: **2026-09-07**

Purpose: exact continuation state. GitHub living documents are canonical.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`
3. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
4. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
5. `docs/ANIMATION_PIPELINE.md`
6. `docs/CHARACTERS.md`

## Local paths — LOCKED

Project repository: `D:\GOOGLE DRIVE\DEV\Roguelite`

AI/model root: `Z:\AI`

Current workspaces:

- `Z:\AI\RogueliteCharacterPipeline`
- `Z:\AI\SpriteSheetDiffusionSpike`
- Wan: `Z:\AI\WanAnimate2`

`D:\AI` is stale/historical.

## Runtime / character contract — LOCKED

Final runtime uses complete-character spritesheets. The production model receives Exilada appearance/state separately from arbitrary raw driving video and must automatically infer body dynamics, jiggle, long-hair inertia, cloth/material/wind response and restraints/accessories. Routine manual repair is forbidden.

## Candidate order

1. Wan-Animate-2 — exhaust first.
2. SCAIL-2 — only after Wan reaches `EXHAUSTED_FAIL`.

## Active Wan Base-BF16 model set

- `wan_animate_2_bf16.safetensors` ~32.8 GB
- `umt5_xxl_fp16.safetensors` ~11.4 GB
- `clip_vision_h.safetensors` ~1.26 GB
- `Wan2_1_VAE_bf16.safetensors` ~0.254 GB

Lower precision/Distilled variants are not retained in advance.

## Runner 35 — PASS

BF16 assets and native ComfyUI schemas are present under `Z:\AI\WanAnimate2`.

## Runner 36 / W0 — PASS_BASELINE

Official demo1 reference + raw driver completed at `640×800`, 37 frames, 16 fps, 20 steps, seed 0 using Base BF16. The first attempt hit `hostbuf_file_reader_read failed`; relaunching ComfyUI with only `--disable-pinned-memory` fixed the infrastructure issue.

Visual W0: meaningful raw-video motion transfer, stable official-character identity/costume, no catastrophic topology collapse.

## Runner 37 / W1 — COMPLETE

Evidence:

- `Z:\AI\WanAnimate2\w1_exilada_official_driver.mp4`
- `Z:\AI\WanAnimate2\w1_run_manifest.json`
- `Z:\AI\WanAnimate2\w1_api_prompt.json`

Diagnosis:

- strong cross-identity/raw-video motion transfer;
- long hair and hip cloth show inferred non-rigid motion;
- no cat appearance leakage;
- smooth/painterly art-language drift;
- face/body/reference-detail drift;
- restraint/chain loss/morphing;
- some hand/foot blur/stretch and a transient artifact;
- later head/upper-body crop follows the same tendency in W0, therefore treat it primarily as driver/framing behavior;
- official driver does not decide final walking/jiggle/wind performance.

Classification: **production-appearance CONFIGURATION FAIL with strong positive raw-video motion evidence. Wan remains active.**

## CURRENT GATE — RUNNER 38 / W1A REFERENCE STRENGTH 1.5

Runner:

`tools/structured-2d-character-pipeline/38_run_wan_animate2_bf16_w1a_refstrength15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1a_reference_strength.py`

One changed variable only:

`reference_image_strength: 1.0 -> 1.5`

Everything else remains exact W1: Exilada reference/prompt, official driver, Base BF16 stack, `640×800`, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0, pose strength 1.0, negative prompt and `--disable-pinned-memory`.

Expected output:

- `Z:\AI\WanAnimate2\w1a_exilada_refstrength15.mp4`
- `Z:\AI\WanAnimate2\w1a_run_manifest.json`
- `Z:\AI\WanAnimate2\w1a_api_prompt.json`

## NEXT GATE AFTER W1A — AUTOMATIC FRAMING/CROP NORMALIZATION

The crop must be solved before W2. Do not repair generated output after the fact.

Use the winning W1/W1A appearance setting, keep Wan/model/seed/settings unchanged, and change only the driving-video geometry through automatic preprocessing:

1. detect/track performer automatically;
2. derive a stable/smoothed full-clip subject box;
3. fit the whole visible body plus safety margin inside a fixed `640×800` canvas;
4. preserve aspect ratio;
5. pad/letterbox rather than destructive center-crop;
6. use constant or smoothly varying subject scale/center;
7. no manual masks, keyframes or per-frame crop corrections.

Success criterion: head and feet remain visible throughout while motion transfer remains materially intact.

If validated, this normalization becomes mandatory preprocessing for Internet driving clips.

## AFTER FRAMING — ART-DIRECTION PROMPT TEST

Only after the crop is controlled, test the approved visual refinement separately: stronger 1980s barbarian/sword-and-sorcery influence, more torn fabric and more body exposure. Do not mix this with the framing experiment.

## Exact operator action now

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\38_run_wan_animate2_bf16_w1a_refstrength15.ps1"
```

## Wan sequence

- W0: PASS_BASELINE.
- W1: appearance CONFIGURATION FAIL, motion evidence positive.
- W1A: CURRENT.
- framing/crop normalization: NEXT.
- art-direction prompt gate.
- W2: Internet walking driver.
- W3: secondary-motion stress footage.
- W4: finite high-leverage variants only.

## Cleanup discipline

Unused large models/materials must not accumulate. Keep the active BF16 route while Wan is being exhausted. Keep `Z:\AI\SpriteSheetDiffusionSpike` temporarily as comparison/fallback evidence until Wan reaches a useful production verdict.