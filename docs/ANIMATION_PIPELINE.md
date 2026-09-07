# Character Animation Production — Living Decision Record

Status date: **2026-09-07**

Status: **RAW-VIDEO DUAL-REFERENCE COMPLETE-CHARACTER GENERATION IS THE ACTIVE PRODUCTION CLASS. WAN-ANIMATE-2 BASE BF16 REMAINS UNDER CONTROLLED EXHAUSTION. W0 PASSED; W1 IS THE CURRENT PREFERRED VISUAL/MOTION BASELINE; W1A 1.5 IS NOT PREFERRED; W1F SAFE FRAMING IS ACTIVE.**

Canonical state: `docs/PROJECT_STATE.md`

Canonical visual direction: `docs/VISUAL_DIRECTION.md`

Canonical model screening: `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`

## Hard production constraints

The pipeline must:

- use `assets/source/characters/exilada/reference/exilada_master.png` as complete appearance/state reference;
- accept a separate real driving video for movement/performance;
- allow the driver performer to differ completely in identity, clothing, hair and accessories;
- preserve Exilada identity, hair mass, clothing state and restraints as far as production quality requires;
- infer locomotion, body soft response, hair inertia, cloth/material/wind response and restraint/accessory motion automatically;
- require no routine manual rigging, keyframing, simulation repair, masks, repainting, per-frame cleanup or hand compositing;
- allow automatic preprocessing/postprocessing;
- output complete visible frames suitable for automatic spritesheet packing.

## Runtime contract — LOCKED

`complete generated frames -> complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

No visible runtime body/hair/clothing/equipment assembly.

## Motion-source rule — LOCKED

Final production motion comes from **real driving video consumed in a richer form than body skeleton alone**. Internet footage is acceptable; costume matching is not required.

Pose/SMPL/mocap may remain diagnostics only.

## Model-exhaustion protocol — LOCKED

Do not switch model families after a single ugly result.

Before `EXHAUSTED_FAIL`:

1. reproduce official/reference behavior where practical;
2. validate local checkpoint/loader/input semantics;
3. test cross-identity in controlled stages;
4. change one high-leverage variable at a time;
5. keep seed/input fixed unless stochasticity itself is tested;
6. prohibit manual rescue;
7. require decisive failure across a finite valid matrix.

## Historical research

RefControl, Qwen edit, hidden-rig and Moore/SSD work remain research evidence. Runner 34 proved complete-character generation/packing but its pose-only path does not satisfy the final raw-video contract. Exact public SSD remains `BLOCKED` by the absent custom pose-guider checkpoint.

## Active Wan Base-BF16 set

- `wan_animate_2_bf16.safetensors` ~32.8 GB;
- `umt5_xxl_fp16.safetensors` ~11.4 GB;
- `clip_vision_h.safetensors` ~1.26 GB;
- `Wan2_1_VAE_bf16.safetensors` ~0.254 GB.

Total ~45.7 GB.

Lower-precision/Distilled variants are not retained unless a later controlled comparison explicitly needs them.

## Local workspace

Project repo: `D:\GOOGLE DRIVE\DEV\Roguelite`

Wan workspace: `Z:\AI\WanAnimate2`

`D:\AI` is stale/historical.

## W0 — PASS_BASELINE

Runner 36 reproduced the official raw-video path at `640×800`, 37 frames, 16 fps, 20 steps, seed 0. The first attempt hit AIMDO `hostbuf_file_reader_read failed`; adding only `--disable-pinned-memory` resolved the infrastructure issue.

## W1 — CURRENT PREFERRED VISUAL/MOTION BASELINE

Runner 37 used Exilada + the official driver at `reference_image_strength=1.0`.

Positive evidence:

- substantial cross-identity motion transfer;
- long black hair clearly moves as a non-rigid mass;
- ragged hip cloth changes drape;
- no cat identity/costume leakage;
- coarse Exilada state survives.

Technical issues:

- wrist restraints/chains are not stable enough;
- some hand/foot blur/stretch and transient artifacts;
- later head/body crop inherited from driver framing;
- official driver does not decide target walking/jiggle/wind quality.

### Visual-language decision

The W1 painterly/illustrated 2D look was explicitly approved by the user as the preferred whole-game direction.

Therefore **smooth/painterly output is not a failure by itself anymore**. The former hard modern-pixel-art acceptance criterion is superseded by `docs/VISUAL_DIRECTION.md`.

Localized, restrained motion blur is allowed and may improve the animation, provided it does not erase anatomy/topology/readability.

The visible direction now deliberately includes an **1980s sword-and-sorcery charge** aligned with Heavy Metal / Conan / Red Sonja / Frank Frazetta / Julie Bell.

## W1A — reference strength 1.5 COMPLETE / NOT PREFERRED

Runner 38 changed only `reference_image_strength 1.0 -> 1.5`.

Uploaded run:

- `INFERENCE_COMPLETE`;
- elapsed 1912.32 s;
- output SHA256 `2661d339f332a28ca25a3a03aa6a59ccd93a572751fb488de04540a764315bef`.

Direct W1 vs W1A comparison:

- no material identity/clothing/restraint improvement;
- more blur/ghosting in several movement phases;
- weaker limb definition in those phases;
- crop unchanged;
- no superior overall tradeoff.

Conclusion: return to **W1 reference strength 1.0** as the current preferred balance.

## W1F — CURRENT SAFE-FRAMING GATE

Runner:

`tools/structured-2d-character-pipeline/39_run_wan_animate2_bf16_w1f_safe_framing80.ps1`

Executor:

`tools/wan-animate2-spike/run_w1f_safe_framing.py`

W1F branches from the exact W1 prompt and changes only the geometry of the raw driving input:

- preserve the full original frame;
- contain it inside a fixed centered 80% safe box on a `640×800` canvas;
- add stable margins;
- no destructive crop;
- no temporal tracking/camera breathing;
- no manual alignment.

Everything else remains W1: Exilada reference/prompt, BF16 stack, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0, pose strength 1.0, reference strength 1.0, negative prompt and `--disable-pinned-memory`.

Success criterion: full head/hair/body remain safely inside generated frame without unacceptable subject shrinkage, motion weakening or new topology problems.

If this simple fixed-safe-box transform works, it is preferable to a more complex tracker because it is deterministic and cannot introduce camera breathing. Detector/tracker refinement is reserved for future Internet clips that truly need it.

## Art-direction prompt gate — AFTER W1F

Once framing is controlled, test separately:

- stronger 1980s sword-and-sorcery language;
- more severely torn chest/hip cloth;
- greater body exposure;
- possible partial breast exposure consistent with damaged fabric;
- preserve severe adult Exilada identity and captivity/deprivation logic.

Do not mix this with the framing diagnostic.

## Wan sequence

- W0 official baseline — **PASS_BASELINE**;
- W1 Exilada / ref strength 1.0 — **CURRENT PREFERRED BASELINE**;
- W1A ref strength 1.5 — **NOT PREFERRED**;
- W1F safe framing 80% — **CURRENT**;
- art-direction prompt gate;
- W2 target Internet walking driver;
- W3 secondary-motion stress video;
- W4 finite remaining hypothesis-driven variants.

## SCAIL-2 — NEXT ONLY IF WAN EXHAUSTS

Do not install SCAIL-2 while Wan still has meaningful untested production controls.

## Mandatory complete-sequence QA

Judge identity/proportions, motion adherence/grounding, limb/hands/feet topology, hair persistence/inertia, cloth behavior, jiggle/soft response, chains/restraints/accessory coherence, driver leakage, safe framing/background extraction, readability near 128 px, automatic loop/segment/spritesheet suitability and zero manual repair.

## Cleanup discipline — LOCKED

Do not accumulate unused large model variants/materials. Preserve small logs/manifests/results. Keep the active Wan BF16 route while under exhaustion. Keep SSD comparison evidence until a production verdict is reached.

## Immediate operator action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\39_run_wan_animate2_bf16_w1f_safe_framing80.ps1"
```
