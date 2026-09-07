# Roguelite — Current Project State

Status date: **2026-09-07**

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

Every state-changing project action updates thematic docs, this file and the active handoff before completion is reported.

## Local path topology — LOCKED

Project repository: `D:\GOOGLE DRIVE\DEV\Roguelite`

AI/model root: `Z:\AI`

Retained workspaces:

- `Z:\AI\RogueliteCharacterPipeline`
- `Z:\AI\SpriteSheetDiffusionSpike`
- active Wan workspace: `Z:\AI\WanAnimate2`

`D:\AI` is stale/historical and must not be used by current tooling.

## Game / projection — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic-like gameplay camera;
- native raster `640×360`;
- pitch `26°`;
- protagonist about `128 px` tall;
- first locomotion family screen-left / mostly lateral-three-quarter;
- `72°` remains current screen-left facing baseline.

## Runtime / production architecture — LOCKED

Final runtime consumes complete precomposed character frames/spritesheets only.

`complete appearance reference + raw driving video + automatic preprocessing -> complete animated frames -> automatic extraction/packing -> spritesheet/atlas + metadata -> ordinary sprite playback`

No visible runtime body/hair/clothing/equipment assembly.

No routine manual rigging, keyframing, simulation repair, mask repair, repainting or hand compositing.

## Visual direction — MAJOR UPDATE 2026-09-07

The previous hard requirement that final visible gameplay art be deliberate modern pixel art is **superseded**.

The Wan W1 Exilada output was explicitly approved by the user as a highly desirable whole-game visual language.

Current preferred visible-art direction:

- painterly / illustrated 2D dark fantasy;
- explicit **1980s sword-and-sorcery charge**;
- active inspiration lineage: **Heavy Metal, Conan, Red Sonja, Frank Frazetta, Julie Bell**;
- adult sensuality/nudity are legitimate and must not be sanitized by default;
- localized, restrained motion blur is allowed and may be aesthetically positive;
- production still requires temporal coherence, silhouette readability, automatic reproducibility and actual gameplay-scale validation.

For the Exilada, the desired initial-state direction may push the present master toward **more severely torn cloth and more exposed body, including possible partial breast exposure**, while keeping the deprivation/captivity logic. Exact tear/exposure geometry is not yet canonized.

Canonical details: `docs/VISUAL_DIRECTION.md` and `docs/CHARACTERS.md`.

## Model exhaustion protocol — LOCKED

A single bad run does not kill a model family. Distinguish infrastructure, integration, configuration, blocked and model/task failures. Exhaust one relevant model family before switching. Change one meaningful variable at a time with fixed seed/input. No seed fishing and no manual rescue.

## Disk/model cleanup rule — LOCKED

Do not accumulate unused large checkpoints/materials. Keep only variants tied to active hypotheses. Preserve small manifests/logs/evidence. Do not delete the active family after one poor result.

## Current candidate order

1. **Wan-Animate-2** — exhaust first.
2. **SCAIL-2** — only after documented Wan `EXHAUSTED_FAIL`.

Moore/AnimateAnyone pose-only and current Moore+SSD compatibility route remain research evidence only for the final raw-video contract. Exact public SSD remains independently `BLOCKED` by the absent custom SSD pose-guider checkpoint.

## Wan active Base-BF16 set

- `wan_animate_2_bf16.safetensors` ~32.8 GB
- `umt5_xxl_fp16.safetensors` ~11.4 GB
- `clip_vision_h.safetensors` ~1.26 GB
- `Wan2_1_VAE_bf16.safetensors` ~0.254 GB

Total ~45.7 GB.

Lower-precision/Distilled variants are not retained in advance.

## Runner 35 — PREPARATION PASS

`tools/structured-2d-character-pipeline/35_prepare_wan_animate2_bf16_w0.ps1`

BF16 assets installed and native ComfyUI schema captured under `Z:\AI\WanAnimate2`.

## Runner 36 — W0 OFFICIAL BASELINE PASS

Official demo1 reference + raw driver, Base BF16, `640×800`, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0.

Attempt 1 hit `hostbuf_file_reader_read failed` inside ComfyUI AIMDO host-buffer streaming; infrastructure only.

Attempt 2 changed only `--disable-pinned-memory` and completed successfully.

Classification: **PASS_BASELINE**.

## Runner 37 — W1 EXILADA COMPLETE

Observed run:

- same official driver/model stack/settings as W0;
- Exilada master reference;
- `reference_image_strength=1.0`;
- elapsed `1746.69 s` (~29m07s);
- output SHA256 `2bbbf3bd0c5b0db46bc1e9d33abd003b7f3627c8fba7880f45d62724f6ab233f`.

Positive evidence:

- substantial cross-identity raw-video motion transfer;
- no cat identity/costume leakage;
- long black hair clearly moves as a non-rigid mass;
- hip cloth changes drape;
- coarse Exilada identity/state survives.

Remaining technical problems:

- wrist restraints/chain largely disappear; ankle chain morphology drifts;
- some hand/foot blur/stretch and transient artifacts;
- later frames crop head/upper body because the official driver framing pushes the character to edges;
- official driver is not suitable to judge target walking/jiggle/strong cloth/wind conclusively.

Important visual reclassification:

The smooth/painterly language is **no longer counted as a failure**. The user explicitly approved it as the preferred art direction. Localized, measured blur is allowed.

## Runner 38 — W1A reference strength 1.5 COMPLETE

Uploaded W1A evidence confirms:

- status `INFERENCE_COMPLETE`;
- same Exilada reference/driver/model/seed/sampler/settings as W1;
- only `reference_image_strength: 1.0 -> 1.5` plus output prefix changed;
- elapsed `1912.32 s` (~31m52s);
- output SHA256 `2661d339f332a28ca25a3a03aa6a59ccd93a572751fb488de04540a764315bef`.

Visual comparison against W1:

- no material improvement in identity, clothing-layout or restraint retention;
- painterly appearance remains essentially the same class;
- several motion phases show **more blur/ghosting and weaker limb definition**;
- framing/crop tendency remains because the driver is unchanged;
- motion is still present, but the tradeoff is not better than W1.

Classification:

**W1A = valid controlled diagnostic, but `reference_image_strength=1.5` is not preferred.**

Current preferred conditioning balance returns to **W1 `reference_image_strength=1.0`**.

No need to keep escalating reference strength before fixing framing.

## Runner 39 — CURRENT GATE: W1F AUTOMATIC SAFE FRAMING

Runner:

`tools/structured-2d-character-pipeline/39_run_wan_animate2_bf16_w1f_safe_framing80.ps1`

Executor:

`tools/wan-animate2-spike/run_w1f_safe_framing.py`

W1F branches from the preferred W1 prompt (`reference_image_strength=1.0`) and changes only driver framing:

- preserve the entire original raw driver frame;
- fit it inside a fixed centered **80% safe box** on a `640×800` canvas;
- add stable margins;
- no crop, no temporal tracking/camera breathing, no manual alignment.

Everything else stays W1:

- Exilada reference/prompt;
- Base BF16 + UMT5 FP16 + CLIP Vision H + VAE BF16;
- 37 frames, 16 fps, 20 steps;
- CFG 1.0, Euler/simple, shift 5.0, seed 0;
- pose strength 1.0;
- reference strength 1.0;
- negative prompt;
- `--disable-pinned-memory`.

Hypothesis: inherited head/body edge cropping can be eliminated by safe-framing the raw driver before Wan without materially reducing motion quality or causing camera breathing.

Expected evidence:

- `Z:\AI\WanAnimate2\w1f_exilada_safe_framing80.mp4`
- `Z:\AI\WanAnimate2\w1f_run_manifest.json`
- `Z:\AI\WanAnimate2\w1f_api_prompt.json`
- `Z:\AI\WanAnimate2\w1f_safe_driver_manifest.json`

## Sequence after W1F

1. compare W1 vs W1F and lock a framing policy;
2. test the approved **1980s / more severely torn / more exposed Exilada** appearance direction without mixing it into the framing diagnostic;
3. W2 clean real Internet walking driver;
4. W3 secondary-motion stress driver;
5. finite W4 variants only if evidence still justifies them;
6. validate preferred painterly rendering at actual ~128 px gameplay occupancy in the belt-scroller scene.

After W4 classify Wan as `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## SSD retention

Keep `Z:\AI\SpriteSheetDiffusionSpike` temporarily as comparison/fallback evidence while Wan remains under active exhaustion.

## Exact current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\39_run_wan_animate2_bf16_w1f_safe_framing80.ps1"
```
