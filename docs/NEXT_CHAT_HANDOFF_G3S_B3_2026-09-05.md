# Next-chat handoff — G3S complete-character spritesheet production

Status date: **2026-09-08**

GitHub living docs are canonical.

## Paths

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- Wan: `Z:\AI\WanAnimate2`
- planned H3: `Z:\AI\MiniMaxH3`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` invalid/stale.

## Production contract

Complete Exilada appearance reference + arbitrary real driving video -> complete generated character frames -> automatic extraction/downsample/packing -> spritesheet. No routine manual rigging/keyframing/sim repair/mask repair/repainting/compositing.

## Art direction

Painterly illustrated 2D dark fantasy with explicit 1980s sword-and-sorcery charge: Heavy Metal, Conan, Red Sonja, Frank Frazetta, Julie Bell. Adult sensuality/nudity legitimate. Localized blur can be positive; destructive ghosting/anatomy loss is not.

## Wan status

W0 passed local BF16 integration. W1 established approved art/motion language. W1F letterbox and W1G tracked/recentered framing are closed. W1H `512×912` solved dominant crop while preserving raw driver and remains the best Wan geometry baseline. W1I pose-end0.70 did not materially improve blur/structure. W1J and W1K were prepared but never executed.

## CURRENT RUN — W1L / Runner45

The user is currently running:

`tools/structured-2d-character-pipeline/45_run_wan_animate2_bf16_w1l_ref10_pose80_steps30.ps1`

Compound changes from W1H:

- ref strength1.5 ->1.0;
- pose strength1.0 ->0.8;
- steps20 ->30.

Everything else remains W1H. Preserve:

- `Z:\AI\WanAnimate2\w1l_exilada_aspectmatched_ref10_pose80_steps30.mp4`
- `Z:\AI\WanAnimate2\w1l_run_manifest.json`
- `Z:\AI\WanAnimate2\w1l_api_prompt.json`
- `Z:\AI\WanAnimate2\w1l_executor.log`

Do not interrupt W1L and do not launch another Wan run afterward before H3 screening.

## DECISION LOCK 2026-09-08 — MINIMAX H3 NEXT

After W1L completes, **pause Wan-Animate-2 and switch active screening to MiniMax H3 Base Ref2VA**. Wan is paused, not `EXHAUSTED_FAIL`.

SCAIL-2 moves behind H3 and is only screened later if H3 does not satisfy the complete-character contract.

Reason: H3 Ref2VA accepts image and video references directly, matching the required Exilada appearance + real driver architecture.

## H3 first local spike

Planned workspace: `Z:\AI\MiniMaxH3`.

Initial canvas: **`448×800`**.

Rules:

- use Ref2VA only; do not download FL2VA;
- both output dimensions multiples of32;
- keep aspect close to raw portrait driver;
- exploit lower spatial resolution because final runtime character is only ~128px tall;
- do not generate directly at128px;
- evaluate both full source frames and an automatically downsampled ~128px character preview.

Resolution escalation only if necessary:

`448×800 -> 480×864 -> 512×896 -> one 768-short-edge control`

The lower canvas reduces latent/activation work but not model-weight size or all RAM/offload cost.

## Immediate next action when W1L finishes

1. inspect W1L video + manifest and record verdict;
2. mark Wan paused after W1L;
3. audit local ComfyUI H3 node/version compatibility;
4. enumerate exact H3 Ref2VA assets, sizes, disk/RAM requirements and cleanup before downloading;
5. build the smallest safe RTX3060-12GB Ref2VA runner at `448×800`;
6. generate full-resolution and ~128px gameplay QA previews automatically.

## Cleanup

Do not delete Wan weights during W1L. Once W1L evidence is secured and H3 is proven active, reevaluate removal of the Wan BF16 set. Avoid duplicate H3 quantizations/task families. Preserve small logs/manifests and SSD comparison evidence until explicit abandonment/final verdict.
