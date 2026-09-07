# G3S — Animation Architecture Lock

Status date: **2026-09-07**

Status: **CANONICAL / COMPLETE-CHARACTER 2D SPRITESHEET RUNTIME / RAW-VIDEO DUAL-REFERENCE AUTHORING REQUIRED / NO MANUAL ANIMATION/CLEANUP / WAN-ANIMATE-2 BASE BF16 W0 ACTIVE**

## Presentation lock

The game uses an elevated arcade beat'em-up / belt-scroller false-3D presentation:

- fixed orthographic gameplay camera;
- native raster `640×360`;
- pitch `26 deg`;
- protagonist about `128 px` tall;
- first locomotion family screen-left and mostly lateral/three-quarter;
- intended first gameplay facing remains `72 deg` azimuth from travel heading.

## Final runtime representation — LOCKED

The runtime consumes **complete, already-composed character frames**:

`complete authored frames -> complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

Runtime visible-character assembly from body/hair/clothing/armor/accessory layers is abolished.

## Complete-frame motion requirement — LOCKED

Every valid exported animation must bake together, where present:

- body locomotion and weight transfer;
- soft-tissue/jiggle;
- hair inertia/follow-through;
- clothing/binding motion;
- material/wind response;
- shackles/chains/restraints/accessories;
- final occlusion changes.

## Initial Exilada state — LOCKED

Canonical appearance reference:

`assets/source/characters/exilada/reference/exilada_master.png`

It owns the entire initial visible state.

## Dual-reference authoring contract — LOCKED

Production animation requires two semantically separate sources:

1. **appearance:** complete Exilada master;
2. **movement:** arbitrary real driving video.

The driving performer may come from Internet footage and does not need matching costume, hair, body or identity.

The production model must consume motion information richer than a skeleton/body-pose sequence so it can exploit non-rigid temporal evidence for hair, cloth, soft-body response, wind and accessory dynamics.

## No-manual-production rule — LOCKED

Disallowed as required production steps:

- manual rigging/weight painting;
- manual keyframing;
- manual hair animation;
- manual cloth simulation setup/repair;
- manual chain animation;
- manual pose alignment;
- manual mask repair;
- per-frame repainting/retouching;
- hand compositing or cleanup.

Allowed: fully automatic preprocessing, segmentation, crop/resize, background removal, frame extraction, spritesheet packing, QA and metadata.

## Model-exhaustion rule — LOCKED

Do not change model families because one configuration produces a bad result.

`EXHAUSTED_FAIL` requires:

1. official/reference baseline reproduction where practical;
2. loader/checkpoint/input semantics validated;
3. controlled cross-identity/project tests;
4. meaningful high-leverage variants one at a time with fixed input/seed;
5. repeated decisive failure;
6. no manual rescue and no random seed fishing.

## Pose-only routes — research only for the final contract

Runner 34 proved complete-character export/packing/playback, but the current Moore/AnimateAnyone + released SSD-UNet compatibility route is body-pose-conditioned. It therefore cannot be the final complete-motion production foundation under the raw-video contract because the control signal discards the non-rigid dynamics we explicitly require.

Exact public SSD remains separately `BLOCKED` by the missing custom SSD pose-guider checkpoint.

## Raw-video candidate order — LOCKED

1. **Wan-Animate-2** — exhaust first.
2. **SCAIL-2** — next open/local candidate only after Wan reaches `EXHAUSTED_FAIL`.
3. DreamActor-M2 — benchmark until a self-hostable release exists.
4. Kling Motion Control — hosted benchmark only.

## Wan historical test — evidence only

The 2026-09-04 project test used a constrained Base INT8 / UMT5 FP8 setup around `384×576`, 17 frames and seed 42. It produced weak locomotion transfer and a smooth painted result.

That configuration failed, but it did not exhaust Wan-Animate-2.

## Wan checkpoint-quality lock — 2026-09-07

Hardware no longer selects the checkpoint.

Canonical W0 set:

- `wan_animate_2_bf16.safetensors` — ~32.8 GB;
- `umt5_xxl_fp16.safetensors` — ~11.4 GB;
- `clip_vision_h.safetensors` — ~1.26 GB;
- `Wan2_1_VAE_bf16.safetensors` — ~0.254 GB.

Total model payload: ~45.7 GB.

Not part of W0 and intentionally removed if found:

- Base INT8 ConvRot;
- Distilled BF16;
- Distilled INT8 ConvRot;
- LightX2V distillation LoRA;
- UMT5 FP8.

Those variants are downloaded later only if an explicit W4 comparison requires them.

## Hardware-concession order — LOCKED

If RTX 3060 12 GB + 48 GB RAM cannot execute the reference-quality W0 set, reduce execution one controlled variable at a time:

1. offload/cache strategy;
2. temporal frame window;
3. spatial resolution;
4. text-encoder precision if necessary;
5. main-model quantization only later as an explicit comparison.

Do not begin by replacing the Base BF16 main checkpoint.

## Runner 35 — CURRENT GATE

`tools/structured-2d-character-pipeline/35_prepare_wan_animate2_bf16_w0.ps1`

Runner 35 performs setup only:

- requires 70 GB free-space headroom;
- rebuilds/restores isolated `D:\AI\WanAnimate2`;
- removes superseded Wan-specific model/material variants;
- downloads only the ~45.7 GB BF16/FP16 W0 model set;
- downloads upstream demo1 `reference.png` + `template.mp4`;
- copies Exilada master for later W1;
- removes completed HF/Xet cache;
- launches ComfyUI headlessly;
- captures exact installed node schemas;
- stops before inference.

Expected marker:

`RUNNER35-WAN-BF16-PREP: PASS — READY TO AUTHOR W0 WORKFLOW`

The schema-first stop is mandatory so the W0 workflow is built against the actual fresh `WanAnimate2ToVideo` and loader contracts rather than stale template assumptions.

## W0–W4 sequence

- **W0:** official upstream reference + official driver;
- **W1:** same known-good driver/settings, replace only appearance with Exilada master;
- **W2:** clean real Internet walk clip;
- **W3:** real secondary-motion stress clip with body bounce/hair/cloth/wind;
- **W4:** finite documented variants only.

After W4: `PASS_CANDIDATE` or `EXHAUSTED_FAIL`.

## Cleanup discipline — LOCKED

Do not accumulate duplicate large checkpoints/materials.

- Keep only variants tied to an active test hypothesis.
- Remove superseded local model-specific material when no longer used.
- Preserve small logs/manifests/results.
- Do not delete the active Wan BF16 workspace because of one bad output.
- Keep SSD comparison evidence temporarily until Wan W0 is established or SSD research is explicitly abandoned.

## Closed routes / assumptions

- runtime visible-character layer assembly — CLOSED;
- body-pose-only animation as final complete-motion production solution — CLOSED;
- manual hidden-3D/2D secondary animation as required production method — CLOSED;
- hidden 3D render as final visible pixel art — CLOSED;
- independent unconstrained full-body redraw per frame — CLOSED;
- C0 nearest-segment hard partition — CLOSED;
- single-still whole-body chain/cage warp — CLOSED;
- MPFB skinned body as mandatory visible guide — CLOSED.

## Current validation question

> Can Wan-Animate-2 Base BF16, tested first on its official raw-video baseline and then through the finite no-manual W1–W4 matrix, preserve the complete Exilada while automatically transferring body and non-rigid secondary dynamics strongly enough for complete-character spritesheet production?
