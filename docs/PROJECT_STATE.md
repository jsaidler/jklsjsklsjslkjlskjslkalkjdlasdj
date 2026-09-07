# Roguelite — Current Project State

Status date: **2026-09-07**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`
3. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
4. `docs/G3S_C1C_GAMEPLAY_LOCOMOTION_MASTER.md`
5. `docs/G3S_SPRITE_SHEET_DIFFUSION_SPIKE.md`
6. `docs/ANIMATION_PIPELINE.md`
7. `docs/CHARACTERS.md`
8. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing project action updates thematic docs, this file and the active handoff before completion is reported.

## Local path topology — LOCKED

Project repository: `D:\GOOGLE DRIVE\DEV\Roguelite`

AI/model root: `Z:\AI`

Retained workspaces:

- `Z:\AI\RogueliteCharacterPipeline`
- `Z:\AI\SpriteSheetDiffusionSpike`
- active Wan workspace: `Z:\AI\WanAnimate2`

`D:\AI` is stale/historical and must not be used by current tooling.

## Runtime / production architecture — LOCKED

Final runtime consumes complete precomposed character frames/spritesheets only. No runtime body/hair/clothing/equipment layer assembly.

The complete-character generation contract is:

1. `exilada_master.png` owns complete appearance/state;
2. arbitrary real driving video owns motion/performance;
3. the production model must consume richer information than a body skeleton and automatically infer locomotion, soft-body/jiggle, long-hair inertia, cloth/material response, wind and restraint/accessory behavior;
4. no routine manual keyframing, rigging, simulation, masks, repainting, frame cleanup or hand compositing is allowed.

## Model exhaustion protocol — LOCKED

A single bad run does not kill a model family. Distinguish infrastructure, integration, configuration and model/task failures. Exhaust one relevant family before switching. Change one high-leverage variable at a time with fixed seed/input. No random seed fishing and no manual rescue.

## Disk/model cleanup rule — LOCKED

Do not accumulate unused large checkpoints/materials. Keep only variants tied to an active diagnostic hypothesis. Preserve small manifests/logs/evidence. Do not delete the active family after one poor result.

## Current candidate order

1. **Wan-Animate-2** — exhaust first.
2. **SCAIL-2** — only after Wan reaches documented `EXHAUSTED_FAIL`.

Moore/AnimateAnyone pose-only and the current Moore+SSD compatibility route remain research evidence only for the final raw-video contract. Exact public SSD remains independently `BLOCKED` by the absent custom SSD pose-guider checkpoint.

## Wan canonical Base-BF16 model set

- `wan_animate_2_bf16.safetensors` — ~32.8 GB
- `umt5_xxl_fp16.safetensors` — ~11.4 GB
- `clip_vision_h.safetensors` — ~1.26 GB
- `Wan2_1_VAE_bf16.safetensors` — ~0.254 GB

Total ~45.7 GB.

Base INT8, Distilled BF16/INT8, LightX2V distillation LoRA and UMT5 FP8 are not retained for the active Base-BF16 route.

## Runner 35 — PREPARATION PASS

`tools/structured-2d-character-pipeline/35_prepare_wan_animate2_bf16_w0.ps1`

Result: **PASS**. BF16 assets installed and native ComfyUI schema captured under `Z:\AI\WanAnimate2`.

## Runner 36 — W0 OFFICIAL BASELINE PASS

`tools/structured-2d-character-pipeline/36_run_wan_animate2_bf16_w0.ps1`

Attempt 1 failed in ComfyUI AIMDO host-buffer streaming with `RuntimeError: hostbuf_file_reader_read failed`; infrastructure only.

Attempt 2 changed one execution variable only: ComfyUI launched with `--disable-pinned-memory`.

Result: **PASS_BASELINE**.

Successful W0 facts:

- official demo1 reference + official raw driver;
- Base BF16 + UMT5 FP16 + CLIP Vision H + VAE BF16;
- `640×800`, 37 frames, 16 fps;
- 20 steps, CFG `1.0`, Euler/simple, shift `5.0`, seed `0`;
- pose/reference strengths `1.0`;
- elapsed ~`1896.94 s` (~31m37s).

Visual W0: substantial motion transfer, stable cat/species identity and costume, no catastrophic topology collapse. Some blur/framing movement exists but integration is credible.

## Runner 37 — W1 EXILADA CROSS-IDENTITY COMPLETE

Runner: `tools/structured-2d-character-pipeline/37_run_wan_animate2_bf16_w1_exilada.ps1`

Executor: `tools/wan-animate2-spike/run_w1_from_w0_prompt.py`

Observed manifest:

- status `INFERENCE_COMPLETE`;
- Exilada reference SHA256 `e8422ec9c7125eec8bf534e13cf0ceac9c2ade5e6e2f18cf26cd8f22e59755ab`;
- same official W0 driver;
- Base BF16 stack unchanged;
- `640×800`, 37 frames, 16 fps, 20 steps;
- CFG 1.0, Euler/simple, shift 5.0, seed 0;
- pose strength 1.0;
- reference-image strength 1.0;
- elapsed `1746.69 s` (~29m07s);
- output SHA256 `2bbbf3bd0c5b0db46bc1e9d33abd003b7f3627c8fba7880f45d62724f6ab233f`.

### W1 visual diagnosis — MOTION/RAW-VIDEO CLASS PASS, PRODUCTION APPEARANCE CONFIGURATION FAIL

Positive evidence:

- cross-identity raw-video motion transfer is clearly substantial;
- no cat identity/costume leaks into the Exilada;
- long black hair is not frozen: its silhouette and trailing mass change over time, demonstrating inferred non-rigid secondary response beyond a skeleton-only driver;
- ragged hip cloth changes drape with pose/motion;
- the general Exilada package survives at coarse level: adult woman, brown/olive skin, long black hair, minimal beige wraps, barefoot state, wounds/wear and at least one ankle restraint/chain remain recognizable.

Current failures:

- output is smooth/painterly rather than the required discrete modern pixel/game-art language, despite the explicit positive prompt;
- face and body details drift; proportions become more generically muscular/illustrative than the approved target;
- restraints/accessories are incomplete: wrist restraint/chain information largely disappears and the surviving ankle chain morphs;
- some hand/foot blur/stretching and one detached transient artifact are visible;
- complete framing is not reliable in this official driver: later frames crop the head/upper body. The same crop trend exists in W0, so this is inherited driver/framing behavior rather than an Exilada-specific failure;
- the official cat driver is not suitable to judge target locomotion, jiggle or strong cloth/wind stress conclusively.

Therefore W1 does **not** reject Wan. It proves the correct model class is operational but shows that appearance/reference adherence at native strength `1.0` is not production-ready.

## Native reference-strength finding — HIGH-LEVERAGE CONTROL

The installed/current native ComfyUI `WanAnimate2ToVideo` schema documents:

- `reference_image_strength` default `1.0`;
- values above `1.0` tighten generated-frame attention to the reference latent and reduce appearance drift;
- `pose_strength` separately owns driving-motion influence.

This gives a direct one-variable diagnostic for the exact W1 failure before changing driver/model family.

## Runner 38 — CURRENT GATE: W1A REFERENCE STRENGTH 1.5

Runner:

`tools/structured-2d-character-pipeline/38_run_wan_animate2_bf16_w1a_refstrength15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1a_reference_strength.py`

W1A is derived from the exact completed W1 prompt and changes exactly one model-conditioning variable:

`reference_image_strength: 1.0 -> 1.5`

Everything else is held fixed:

- Exilada reference image and positive prompt;
- official W0/W1 driver;
- Base BF16 / UMT5 FP16 / CLIP Vision H / VAE BF16;
- `640×800`, 37 frames, 16 fps;
- 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0;
- pose strength 1.0;
- negative prompt;
- `--disable-pinned-memory` runtime workaround.

Hypothesis: a moderate native reference-strength increase should tighten identity, hair/clothing/accessory persistence and possibly preserve more of the reference art language without materially damaging motion transfer.

Expected outputs:

- `Z:\AI\WanAnimate2\w1a_exilada_refstrength15.mp4`
- `Z:\AI\WanAnimate2\w1a_run_manifest.json`
- `Z:\AI\WanAnimate2\w1a_api_prompt.json`

After W1A, compare directly against W1 strength 1.0.

## Framing/crop gate — LOCKED FOR IMMEDIATELY AFTER W1A

The crop is a production blocker and must be solved before W2. It must **not** be "fixed" by cropping or repositioning the generated output after inference, because lost head/body pixels cannot be recovered that way.

Evidence from W0 and W1 indicates the same late-frame crop trajectory with two completely different target characters, so treat framing primarily as a property of the driving-video geometry/input contract.

After W1A establishes which reference strength is preferable, run a dedicated one-variable framing test using that winning appearance setting. The driving video will be automatically normalized before Wan:

1. detect/track the performer automatically over the whole clip;
2. derive a temporally stable/smoothed subject box rather than a per-frame jittering crop;
3. fit the **entire visible body plus safety margin** inside a fixed `640×800` canvas;
4. preserve aspect ratio and use padding/letterboxing instead of destructive center-cropping;
5. keep constant or smoothly varying subject scale/center so the model never receives a driver whose head/feet leave the conditioning canvas;
6. no manual masks, keyframes, crop fixes or per-frame intervention.

This automatic driver-framing normalization is allowed by the production contract and will be mandatory for arbitrary Internet drivers if validated.

Only after the crop/framing gate is solved do we run the planned art-direction prompt experiment (1980s barbarian/sword-and-sorcery influence, more torn fabric/body exposure) and then W2 target walking footage.

## Wan exhaustion sequence

- **W0** official baseline — **PASS_BASELINE**.
- **W1** Exilada + official driver at reference strength 1.0 — **CONFIGURATION FAIL for production appearance; motion/secondary-response evidence positive**.
- **W1A** same W1 with reference strength 1.5 — **CURRENT**.
- **FRAMING GATE** — automatic full-body driver normalization, immediately after W1A.
- **ART-DIRECTION PROMPT GATE** — after framing is controlled.
- **W2** target Internet walking driver.
- **W3** secondary-motion stress footage.
- **W4** finite high-leverage variants only if still needed.

After W4: `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## SSD retention

Keep `Z:\AI\SpriteSheetDiffusionSpike` for now as comparison/fallback evidence. Do not delete it while Wan remains under active exhaustion.

## Exact current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\38_run_wan_animate2_bf16_w1a_refstrength15.ps1"
```
