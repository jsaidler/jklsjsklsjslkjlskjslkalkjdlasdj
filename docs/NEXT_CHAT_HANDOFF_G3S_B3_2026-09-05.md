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

Project repo: `D:\GOOGLE DRIVE\DEV\Roguelite`

AI root: `Z:\AI`

Current workspaces:

- `Z:\AI\RogueliteCharacterPipeline`
- `Z:\AI\SpriteSheetDiffusionSpike`
- `Z:\AI\WanAnimate2`

`D:\AI` is stale/historical.

## Runtime / production contract — LOCKED

Final runtime uses complete-character spritesheets. Appearance comes from the Exilada master, movement comes from raw driving video, and production must automatically infer body dynamics, long-hair inertia, cloth/material response and restraints/accessories without routine manual repair.

## Visual direction — UPDATED 2026-09-07

The earlier hard final-art pixel-art requirement is superseded.

The user explicitly approved the Wan W1 **painterly illustrated 2D** result as a highly desirable whole-game look.

Current direction:

- painterly dark-fantasy 2D;
- deliberate **1980s sword-and-sorcery charge**;
- inspirations: **Heavy Metal, Conan, Red Sonja, Frank Frazetta, Julie Bell**;
- localized/restrained motion blur may be positive;
- adult sensuality/nudity must not be sanitized by default;
- Exilada initial state should later test more severely torn cloth, more body exposure and possible partial breast exposure consistent with clothing damage.

Exact tear/exposure geometry is not yet canonized.

## Candidate order

1. Wan-Animate-2 — exhaust first.
2. SCAIL-2 — only after Wan reaches `EXHAUSTED_FAIL`.

## Active Wan Base-BF16 model set

- `wan_animate_2_bf16.safetensors` ~32.8 GB
- `umt5_xxl_fp16.safetensors` ~11.4 GB
- `clip_vision_h.safetensors` ~1.26 GB
- `Wan2_1_VAE_bf16.safetensors` ~0.254 GB

Lower precision/Distilled variants are not retained in advance.

## W0 — PASS_BASELINE

Runner 36 completed official demo1 Base BF16 at `640×800`, 37 frames, 16 fps, 20 steps, seed 0. First attempt hit AIMDO `hostbuf_file_reader_read failed`; `--disable-pinned-memory` fixed the infrastructure issue.

## W1 — COMPLETE / CURRENT PREFERRED VISUAL-MOTION BASELINE

Runner 37, Exilada + official driver, `reference_image_strength=1.0`.

Observed positives:

- strong raw-video motion transfer;
- no cat leakage;
- long hair and hip cloth show non-rigid secondary motion;
- coarse Exilada identity survives;
- user explicitly approved the painterly look.

Technical issues still open:

- restraint/chain loss/morphing;
- some limb blur/stretch/artifacts;
- later head/upper-body crop inherited from driver framing;
- official driver cannot decide target walking/jiggle/wind quality.

Localized, measured blur is not automatically a defect anymore.

## W1A — COMPLETE / 1.5 NOT PREFERRED

Runner 38 changed only:

`reference_image_strength: 1.0 -> 1.5`

Uploaded result/manifest:

- `INFERENCE_COMPLETE`;
- elapsed `1912.32 s` (~31m52s);
- output SHA256 `2661d339f332a28ca25a3a03aa6a59ccd93a572751fb488de04540a764315bef`.

Direct comparison against W1:

- no material identity/clothing/restraint improvement;
- several phases have more blur/ghosting and weaker limb definition;
- crop remains;
- no better overall tradeoff.

Conclusion: **return to W1 `reference_image_strength=1.0` as current preferred balance.**

## CURRENT GATE — RUNNER 39 / W1F AUTOMATIC SAFE FRAMING RETRY

Runner:

`tools/structured-2d-character-pipeline/39_run_wan_animate2_bf16_w1f_safe_framing80.ps1`

Executor:

`tools/wan-animate2-spike/run_w1f_safe_framing.py`

W1F branches from W1, not W1A.

Only changed experimental axis: driver framing.

The preprocessor:

- preserves the entire original raw driver frame;
- contains it inside a fixed centered **80% safe box** on `640×800`;
- adds stable margins;
- does not crop the subject;
- does not use temporal tracking/camera breathing;
- requires no manual alignment.

Everything else remains exact W1: Exilada reference/prompt, Base BF16 stack, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0, pose strength 1.0, reference strength 1.0, negative prompt and `--disable-pinned-memory`.

### Attempt 1 — INFRASTRUCTURE/PREFLIGHT FAIL

Terminal excerpt reached healthy ComfyUI startup and then:

`RUNNER39-WAN-W1F: FAIL - W1F safe-framing inference exited with code 2`

Do not count this against Wan or the framing hypothesis.

The W1F executor is the first active route to import `cv2` for deterministic video preprocessing; the bootstrap did not explicitly guarantee OpenCV and Runner 39 did not preflight it.

Runner 39 has now been hardened to:

- test `import cv2, numpy` before the W1F run;
- install only `opencv-python-headless>=4.10,<5` into the isolated Wan Python environment if `cv2` is absent;
- verify the import again;
- then start ComfyUI and rerun the exact same W1F experiment.

No Wan/model/sampler/seed/framing parameter changed in this correction.

Expected outputs after a valid retry:

- `Z:\AI\WanAnimate2\w1f_exilada_safe_framing80.mp4`
- `Z:\AI\WanAnimate2\w1f_run_manifest.json`
- `Z:\AI\WanAnimate2\w1f_api_prompt.json`
- `Z:\AI\WanAnimate2\w1f_safe_driver_manifest.json`

Success criterion: complete head/hair/body stay safely inside frame without unacceptable subject shrinkage, motion weakening or new topology drift.

## AFTER W1F

1. lock framing policy;
2. run a separate art-direction prompt test for **1980s sword-and-sorcery + more torn/exposing cloth**;
3. W2 Internet walking driver;
4. W3 secondary-motion stress footage;
5. W4 finite high-leverage variants only if still justified;
6. validate the approved painterly language at actual ~128 px gameplay occupancy in the belt-scroller scene.

## Exact operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\39_run_wan_animate2_bf16_w1f_safe_framing80.ps1"
```

## Cleanup discipline

Unused large models/materials must not accumulate. Keep the active BF16 route while Wan is being exhausted. Keep `Z:\AI\SpriteSheetDiffusionSpike` temporarily as comparison/fallback evidence until Wan reaches a useful production verdict.
