# Character Animation Production — Living Decision Record

Status date: **2026-09-07**

Status: **RAW-VIDEO DUAL-REFERENCE COMPLETE-CHARACTER GENERATION IS THE ACTIVE PRODUCTION CLASS. WAN-ANIMATE-2 BASE BF16 IS UNDER CONTROLLED EXHAUSTION. W0 PASSED; W1 PROVED RAW-VIDEO MOTION/SECONDARY RESPONSE BUT FAILED PRODUCTION APPEARANCE AT REFERENCE STRENGTH 1.0; W1A 1.5 IS ACTIVE. SCAIL-2 REMAINS NEXT ONLY AFTER WAN EXHAUSTS.**

Canonical screening/protocol:

`docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`

Canonical state:

`docs/PROJECT_STATE.md`

## Hard production constraints

The production animation pipeline must:

- use `assets/source/characters/exilada/reference/exilada_master.png` as complete appearance/state reference;
- accept a separate real driving video for movement/performance;
- allow the driver performer to differ completely in identity, clothing, hair and accessories;
- preserve Exilada identity, proportions, hair mass, clothing, scars/restraints and accessories;
- infer locomotion, jiggle/soft motion, hair inertia, cloth/material/wind response and restraint/accessory motion automatically;
- require no manual rigging, keyframing, simulation, masks, repainting, per-frame cleanup or hand compositing;
- allow fully automatic preprocessing/postprocessing;
- output complete visible frames ready for spritesheet packing;
- run reproducibly through scripted local tooling where practical.

## Runtime contract — LOCKED

`complete generated frames -> complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

The runtime never assembles visible body/hair/clothing/equipment layers.

## No-manual rule — LOCKED

Allowed: automatic crop/resize/frame sampling, automatic segmentation/background removal/alpha cleanup, automatic spritesheet packing, scripted QA/metadata and scripted inference settings.

Disallowed as routine production work: manual rigging, keyframes, hair bones, cloth/chain simulation setup or repair, manual pose alignment, manual mask fixes, frame repainting and hand compositing/cleanup.

## Motion-source rule — LOCKED

Final production motion must come from **real driving video consumed in a richer form than body skeleton alone**. Internet footage is acceptable; costume matching is not required.

Pose/SMPL/mocap may remain diagnostics only and cannot be the sole production motion signal.

## Model-exhaustion protocol — LOCKED

Do not change model families after one ugly generation.

Before `EXHAUSTED_FAIL`:

1. reproduce official/reference behavior where practical;
2. validate local checkpoint/loader/input semantics;
3. test cross-identity in controlled stages;
4. change one high-leverage variable at a time;
5. keep seed/input fixed unless stochasticity itself is tested;
6. prohibit manual rescue;
7. require decisive failure to persist across a finite valid matrix.

## Historical research

RefControl, Qwen edit, hidden-rig and Moore/SSD work remain research evidence. Runner 34 proved complete-character generation/packing but its pose-only path does not satisfy the final raw-video contract. Exact public SSD remains separately `BLOCKED` by the absent custom pose-guider checkpoint.

## Current production-class candidate — Wan-Animate-2

Historical 2026-09-04 constrained Base INT8/UMT5 FP8 run at about `384×576`, 17 frames and seed 42 had weak locomotion transfer and smooth/painted output. That configuration failed but did not exhaust the model family.

## Canonical Base-BF16 set

- `wan_animate_2_bf16.safetensors` — ~32.8 GB;
- `umt5_xxl_fp16.safetensors` — ~11.4 GB;
- `clip_vision_h.safetensors` — ~1.26 GB;
- `Wan2_1_VAE_bf16.safetensors` — ~0.254 GB.

Total ~45.7 GB.

Lower-precision/Distilled variants are not retained unless a later controlled comparison explicitly needs them.

## Local workspace

Project repo: `D:\GOOGLE DRIVE\DEV\Roguelite`

AI root: `Z:\AI`

Wan workspace: `Z:\AI\WanAnimate2`

`D:\AI` is stale/historical and must not be used by current tooling.

## W0 — PASS_BASELINE

Official demo1 reference + raw driver, Base BF16, `640×800`, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0.

Attempt 1 hit ComfyUI AIMDO `hostbuf_file_reader_read failed`. Relaunching ComfyUI with only `--disable-pinned-memory` fixed the infrastructure issue.

W0 visual result proves meaningful raw-video motion transfer and stable official-character coherence in the local integration.

## W1 — Exilada / official driver / reference strength 1.0

Runner:

`tools/structured-2d-character-pipeline/37_run_wan_animate2_bf16_w1_exilada.ps1`

Result:

- `INFERENCE_COMPLETE`;
- same W0 driver and all execution settings;
- elapsed 1746.69 s;
- output shows substantial cross-identity motion transfer;
- long black hair visibly changes/trails through motion;
- ragged hip cloth changes drape;
- no visible cat/costume leakage.

However:

- output is smooth/painterly rather than required pixel/game-art;
- face/body/reference details drift;
- wrist restraints/chains largely disappear and ankle chain morphology is unstable;
- some hand/foot blur/stretch and transient artifacting remain.

Classification: **production-appearance CONFIGURATION FAIL with strong positive evidence that direct raw-video conditioning carries richer non-rigid dynamics than skeleton-only routes.**

## Native reference-strength control

Current ComfyUI `WanAnimate2ToVideo` exposes:

- `reference_image_strength` default 1.0; values above 1.0 tighten reference/appearance adherence;
- `pose_strength` separately controls driving-motion influence.

This is the correct next variable before changing driver or model family.

## W1A — CURRENT

Runner:

`tools/structured-2d-character-pipeline/38_run_wan_animate2_bf16_w1a_refstrength15.ps1`

Executor:

`tools/wan-animate2-spike/run_w1a_reference_strength.py`

Exact one-variable change:

`reference_image_strength 1.0 -> 1.5`

Held fixed:

- Exilada reference/prompt;
- official driver;
- Base BF16 stack;
- `640×800`, 37 frames, 16 fps, 20 steps;
- CFG 1.0, Euler/simple, shift 5.0, seed 0;
- pose strength 1.0;
- negative prompt;
- `--disable-pinned-memory`.

W1A QA order:

1. reference identity/body/face fidelity;
2. pixel/game-art preservation;
3. hair/clothing-layout persistence;
4. shackles/chains/accessory retention;
5. topology/artifacts;
6. motion-adherence loss, if any.

If appearance improves without unacceptable motion loss, continue a small reference-strength calibration inside Wan before W2. If not, choose the next native conditioning control from evidence.

## Wan sequence

- W0 official baseline — **PASS_BASELINE**;
- W1 Exilada / reference strength 1.0 — **CONFIGURATION FAIL for appearance, motion evidence positive**;
- W1A reference strength 1.5 — **CURRENT**;
- W2 target Internet walking driver after appearance conditioning is understood;
- W3 secondary-motion stress video;
- W4 only remaining finite hypothesis-driven variants.

## SCAIL-2 — NEXT ONLY IF WAN EXHAUSTS

Do not install SCAIL-2 while Wan still has meaningful untested native controls.

## Mandatory complete-sequence QA

Judge the whole sequence on Exilada identity/proportions, motion adherence/grounding, limb/hands/feet topology, hair persistence/inertia, cloth topology/material behavior, jiggle/soft response, chains/restraints/accessory coherence, driver leakage, stable camera/background for extraction, game-art readability near 128 px, automatic loop/segment/spritesheet suitability and zero manual repair.

## Cleanup discipline — LOCKED

Do not accumulate unused large model variants/materials. Keep only files tied to active hypotheses, preserve small logs/manifests/results, do not delete the current Wan BF16 route while under exhaustion, and keep SSD comparison evidence until a production verdict is reached.

## Immediate next operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\38_run_wan_animate2_bf16_w1a_refstrength15.ps1"
```
