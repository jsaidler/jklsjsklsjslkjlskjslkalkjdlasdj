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

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI/model root: `Z:\AI`
- active Wan workspace: `Z:\AI\WanAnimate2`
- retained comparison workspace: `Z:\AI\SpriteSheetDiffusionSpike`
- retained character-pipeline workspace: `Z:\AI\RogueliteCharacterPipeline`
- `D:\AI` is stale/historical and must not be used by current tooling.

## Game / projection — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic-like gameplay camera;
- native raster `640×360`;
- pitch `26°`;
- protagonist about `128 px` tall;
- first locomotion family screen-left / mostly lateral-three-quarter;
- `72°` remains current screen-left facing baseline.

## Runtime / production architecture — LOCKED

Runtime consumes complete precomposed character frames/spritesheets only.

`complete appearance reference + raw driving video + automatic preprocessing -> complete animated frames -> automatic extraction/packing -> spritesheet/atlas + metadata -> ordinary sprite playback`

No visible runtime body/hair/clothing/equipment assembly. No routine manual rigging, keyframing, simulation repair, mask repair, repainting or hand compositing.

## Visual direction — UPDATED 2026-09-07

The earlier hard final-art modern-pixel-art requirement is superseded.

The Wan W1 Exilada output was explicitly approved as a highly desirable whole-game visual language.

Current preferred visible-art direction:

- painterly / illustrated 2D dark fantasy;
- explicit **1980s sword-and-sorcery charge**;
- active inspirations: **Heavy Metal, Conan, Red Sonja, Frank Frazetta, Julie Bell**;
- adult sensuality/nudity are legitimate and must not be sanitized by default;
- localized/restrained motion blur is allowed and may be aesthetically positive;
- blur becomes a defect when it destroys anatomy/topology/gameplay readability;
- Exilada initial state may later push toward more severely torn cloth and more body exposure, including possible partial breast exposure, while preserving the deprivation/captivity logic.

## Model exhaustion protocol — LOCKED

A single bad run does not kill a model family. Distinguish infrastructure, integration, configuration, blocked and model/task failures. Exhaust one meaningful model family before switching. Change one high-leverage variable at a time with fixed seed/input. No seed fishing and no manual rescue.

## Disk/model cleanup rule — LOCKED

Do not accumulate unused large checkpoints/materials. Keep only variants tied to active hypotheses. Preserve small manifests/logs/results. Do not delete the active family after one poor result.

## Candidate order

1. **Wan-Animate-2** — exhaust first.
2. **SCAIL-2** — only after documented Wan `EXHAUSTED_FAIL`.

Moore/AnimateAnyone pose-only and current Moore+SSD compatibility remain research evidence only. Exact public SSD remains independently `BLOCKED` by the absent custom SSD pose-guider checkpoint.

## Wan active Base-BF16 set

- `wan_animate_2_bf16.safetensors` ~32.8 GB
- `umt5_xxl_fp16.safetensors` ~11.4 GB
- `clip_vision_h.safetensors` ~1.26 GB
- `Wan2_1_VAE_bf16.safetensors` ~0.254 GB

Lower-precision/Distilled variants are not retained in advance.

## W0 — PASS_BASELINE

Runner 36 reproduced the official Base-BF16 route at `640×800`, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0.

Attempt 1 hit AIMDO `hostbuf_file_reader_read failed`; relaunching ComfyUI with only `--disable-pinned-memory` fixed the infrastructure issue.

## W1 — Exilada / reference strength 1.0

Runner 37 completed with the official driver and Exilada master.

Positive evidence:

- substantial cross-identity raw-video motion transfer;
- no cat identity/costume leakage;
- long black hair clearly moves as a non-rigid mass;
- hip cloth changes drape;
- painterly result explicitly approved as preferred art direction.

Technical problems:

- wrist restraints/chain largely disappear; ankle chain morphology drifts;
- some hand/foot blur/stretch and transient artifacts;
- late sequence cuts head/upper body;
- official driver is not sufficient to judge final walking/jiggle/wind quality.

## W1A — reference strength 1.5 / REVISED INTERPRETATION

Runner 38 changed only `reference_image_strength: 1.0 -> 1.5`.

Manifest:

- status `INFERENCE_COMPLETE`;
- elapsed `1912.32 s` (~31m52s);
- output SHA256 `2661d339f332a28ca25a3a03aa6a59ccd93a572751fb488de04540a764315bef`.

Initial automated/assistant reading over-weighted sharpness and called 1.0 preferable. **User visual review corrected this.**

Current interpretation:

- `1.5` appears to preserve **body structure/topology** better; fewer body parts are lost or displaced;
- `1.0` is cleaner/less ghosted in some phases;
- `1.5` carries more destructive blur/ghosting;
- therefore `1.5` remains the **structural branch to preserve**, while blur becomes a separate later axis.

Do not collapse the tradeoff into a single “1.5 lost” verdict.

## W1F — fixed whole-frame safe framing 80% / VALID FAIL FOR CROP

Runner 39 retry completed successfully after OpenCV preflight was fixed.

Manifest facts:

- status `INFERENCE_COMPLETE`;
- driver: `wan_animate2_w1f/official_demo1_template_safe80.mp4`;
- reference strength `1.0`;
- elapsed `1737.61 s`;
- source `480×854`, 337 frames @30 fps;
- entire source frame placed at `360×640` inside `640×800`, offset `(140,80)`;
- no source-frame crop or temporal camera breathing.

Visual verdict:

**W1F did NOT solve generated framing.** Head/hair still leave the top later in the sequence and the character still pushes into the right edge.

Conclusion:

- merely letterboxing/scaling the whole driver frame is insufficient;
- Wan does not preserve those whole-frame margins as equivalent generated-character margins;
- do not waste runs by trying only 70%/60%/50% whole-frame letterbox variants.

## Native framing semantics discovered

Current ComfyUI `WanAnimate2ToVideo` preprocesses `pose_video` to the requested width/height with `common_upscale(..., "area", "center")`.

The current W0/W1/W1A/W1F graph also feeds the first driver frame through `CLIPVisionEncode(crop="center")` into `clip_vision_output_pose`.

Therefore the next driver normalizer must control the **subject envelope itself** and must keep that envelope safely inside both:

1. the `640×800` pose-video canvas; and
2. the central square seen by the pose CLIPVision path.

## Runner 40 — CURRENT GATE: W1G SUBJECT FRAMING ON STRUCTURAL 1.5 BRANCH

Runner:

`tools/structured-2d-character-pipeline/40_run_wan_animate2_bf16_w1g_subject_framing_ref15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1g_subject_framing_ref15.py`

W1G branches from the exact completed **W1A** prompt, so `reference_image_strength=1.5` remains unchanged. Relative to W1A, the only experimental axis is driver geometry.

Automatic subject-framing v1:

- analyzes the first 37 source frames with temporal-activity segmentation;
- derives one global moving-subject envelope;
- expands it to include static body/head/feet margin;
- applies **one fixed affine transform for the whole clip** — no per-frame camera breathing;
- targets subject-envelope height ratio `0.48`, center x `300`, bottom y `620` on `640×800`;
- hard-fails before inference if top/bottom/side margins are unsafe;
- separately hard-checks that the subject envelope survives the center-square CLIPVision crop;
- requires only existing `cv2` + `numpy`; no new detector checkpoint/model is downloaded.

Everything else remains W1A:

- Exilada reference/prompt;
- Base BF16 + UMT5 FP16 + CLIP Vision H + VAE BF16;
- 37 frames, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0;
- pose strength 1.0;
- reference strength 1.5;
- negative prompt;
- `--disable-pinned-memory`.

Expected evidence:

- `Z:\AI\WanAnimate2\w1g_exilada_subject_framed_ref15.mp4`
- `Z:\AI\WanAnimate2\w1g_run_manifest.json`
- `Z:\AI\WanAnimate2\w1g_api_prompt.json`
- `Z:\AI\WanAnimate2\w1g_subject_driver_manifest.json`

Success criterion: complete head/hair/body remain in frame while W1A's stronger body-structure retention survives. If so, **blur reduction becomes the next isolated axis**.

## Sequence after W1G

1. if framing passes, isolate blur reduction while preserving the W1A/W1G structural branch;
2. then run the separate approved 1980s / more severely torn / more exposed Exilada art-direction test;
3. W2 clean real Internet walking driver;
4. W3 secondary-motion stress driver;
5. finite W4 variants only if evidence still justifies them;
6. validate the painterly rendering at actual ~128 px gameplay occupancy.

## Exact current operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\40_run_wan_animate2_bf16_w1g_subject_framing_ref15.ps1"
```
