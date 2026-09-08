# Roguelite — Current Project State

Status date: **2026-09-08**

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

Every state-changing action updates the thematic docs, this file and the active handoff before completion is reported.

## Local paths — LOCKED

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- current Wan workspace: `Z:\AI\WanAnimate2`
- planned MiniMax H3 workspace: `Z:\AI\MiniMaxH3`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` is stale/historical.

## Runtime / game presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic-like gameplay camera;
- native game raster `640×360`;
- pitch `26°`;
- protagonist about `128 px` tall;
- first locomotion family screen-left / mostly lateral-three-quarter;
- `72°` current screen-left baseline;
- runtime consumes **complete precomposed character sprites** only.

Production contract:

`complete appearance reference + raw driving video + automatic preprocessing -> complete animated frames -> automatic extraction/packing -> spritesheet/atlas + metadata -> ordinary sprite playback`

No routine manual rigging, keyframing, simulation repair, mask repair, repainting or hand compositing.

## Visual direction — LOCKED

- painterly / illustrated 2D dark fantasy;
- explicit 1980s sword-and-sorcery charge;
- Heavy Metal, Conan, Red Sonja, Frank Frazetta, Julie Bell lineage;
- adult sensuality/nudity legitimate;
- localized restrained blur may be positive;
- destructive blur/ghosting that erases anatomy/topology/readability is a defect;
- later Exilada art gate may use more severely torn cloth, more body exposure and possible partial breast exposure consistent with captivity/damage.

## Complete-character production contract — LOCKED

The production model must combine the complete Exilada appearance reference with an arbitrary real driving video, consuming richer motion than a skeleton-only pose stream and automatically inferring locomotion, soft response, long-hair inertia, cloth/material behavior and restraint/accessory dynamics. Final runtime artifacts are complete precomposed sprite frames.

## Model-screening order — UPDATED / LOCKED 2026-09-08

1. **Finish W1L only.** It is already running and its evidence must be preserved.
2. **MiniMax H3 Base Ref2VA becomes the next active screening route immediately after W1L.**
3. Wan-Animate-2 becomes **PAUSED AFTER W1L**, not `EXHAUSTED_FAIL`.
4. SCAIL-2 remains a later candidate if H3 does not satisfy the production contract.

This supersedes the earlier rule that Wan had to reach `EXHAUSTED_FAIL` before another family could be screened.

## Wan history — compact canonical record

- W0 / Runner36: local Base-BF16 direct-driving integration PASS with `--disable-pinned-memory`.
- W1 / Runner37 ref1.0: approved painterly visual/motion language; crop, restraint and limb artifacts remained.
- W1A / Runner38 ref1.5: structurally stronger under the old geometry but more ghosted.
- W1F / Runner39: whole-frame letterbox did not solve crop; CLOSED.
- W1G / Runner40: tracked/recentered driver worsened ghosting and temporal anatomy; CLOSED. Never return to synthetic camera-follow/recentering.
- W1H / Runner41: changed only `640×800 -> 512×912` with untouched `480×854` raw driver and ref1.5. Major crop resolved; current best Wan geometry baseline. Prompt `5299b50f-a38d-4cf1-b71e-7022319067d7`, elapsed `1672.46s`, SHA256 `84756f74af5f01aed8329b6a9b7b116149c6abcfd6e6349399c5de8ecf575af1`.
- W1I / Runner42: `pose_end_percent 1.0 -> 0.70`; blur/structural failure materially unchanged; NOT PREFERRED.
- W1J / Runner43 and W1K / Runner44 were prepared but never executed; superseded before run.

## W1L / Runner45 — RUNNING NOW

Parent = exact completed W1H.

Compound configuration search:

- `reference_image_strength 1.5 -> 1.0`;
- `pose_strength 1.00 -> 0.80`;
- `steps 20 -> 30`;
- everything else remains W1H: raw driver untouched, `512×912`, pose window0–1, seed0, CFG1, Euler/simple, shift5, same Exilada reference/prompt/negative/CLIP pose branch.

Runner:

`tools/structured-2d-character-pipeline/45_run_wan_animate2_bf16_w1l_ref10_pose80_steps30.ps1`

Expected evidence:

- `Z:\AI\WanAnimate2\w1l_exilada_aspectmatched_ref10_pose80_steps30.mp4`
- `Z:\AI\WanAnimate2\w1l_run_manifest.json`
- `Z:\AI\WanAnimate2\w1l_api_prompt.json`
- `Z:\AI\WanAnimate2\w1l_executor.log`

Do not start another Wan run after W1L until the H3 spike is screened.

## MiniMax H3 Ref2VA — NEXT ACTIVE ROUTE

Reason: Ref2VA natively accepts multimodal references including images and videos, making it directly relevant to the project's `appearance reference + real driving video` contract.

Local-screening policy:

- use **Ref2VA only**; do not download FL2VA unless a later hypothesis specifically requires it;
- prefer the current ComfyUI-compatible pruned/quantized NVIDIA route suitable for RTX 3060 12 GB + 48 GB RAM;
- use DynamicVRAM/offloading as required;
- no H3 download/install while W1L is still running;
- preserve W1L evidence before any Wan cleanup.

## H3 resolution strategy — LOCKED FOR FIRST SPIKE

Runtime character height is about `128 px`, so full 768p-class generation is not automatically useful. Lower H3 generation resolution is deliberately part of the local production strategy, but **do not generate directly at 128 px**.

First H3 Ref2VA target:

- **`448×800`** portrait;
- both dimensions are multiples of 32, matching current Comfy H3 canvas constraints;
- aspect `0.56`, very close to the current raw driver `480×854` aspect ≈`0.562`;
- 358,400 output pixels versus 1,032,192 at `1344×768`, about **34.7%** of the spatial pixel/token load;
- H3 visual latent grid becomes approximately `28×50 = 1400` spatial cells versus `84×48 = 4032` at `1344×768`, also about **34.7%**.

This can substantially reduce spatial activation work and VRAM pressure, although it does not shrink the model weights or eliminate RAM/offload cost.

Fallback resolution ladder if `448×800` loses anatomy/identity/detail:

1. `480×864`;
2. `512×896`;
3. one 768-short-edge control only if needed to determine whether a defect is caused by low resolution.

Do not use `512×912` for H3 because H3 canvas dimensions should be multiples of 32.

## Gameplay-scale QA — REQUIRED

Every H3 candidate must be judged twice:

1. full generated resolution: anatomy, temporal topology, hair/cloth/restraint dynamics, identity and motion adherence;
2. automatic extracted/downsampled preview with character around `128 px` tall: gameplay readability and whether harmless high-frequency artifacts disappear.

Downsampling may make minor local blur irrelevant, but it cannot excuse missing/reordered body parts, topology changes, detached limbs, broken silhouette or identity drift.

## Cleanup

- Do not delete Wan assets while W1L is running.
- After W1L evidence is secured and H3 is installed/validated enough to become active, reevaluate whether the ~45.7 GB Wan BF16 route should be removed.
- Do not accumulate H3 FL2VA + Ref2VA variants; install only the selected Ref2VA route and required shared components.
- Preserve small manifests/logs/results.
- Keep SSD comparison evidence until explicit abandonment or final model verdict.
