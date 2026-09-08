# Next-chat handoff — G3S complete-character spritesheet production

Status date: **2026-09-08**

GitHub living docs are canonical.

## Paths

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- active H3: `Z:\AI\MiniMaxH3`
- paused Wan: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` invalid/stale.

## Production contract

Complete Exilada appearance reference + arbitrary real driving video -> complete generated character frames -> automatic extraction/downsample/packing -> spritesheet. No routine manual rigging/keyframing/sim repair/mask repair/repainting/compositing.

## Art direction

Painterly illustrated 2D dark fantasy with explicit 1980s sword-and-sorcery charge: Heavy Metal, Conan, Red Sonja, Frank Frazetta, Julie Bell. Adult sensuality/nudity legitimate. Localized blur can be positive; destructive ghosting/anatomy loss is not.

## Wan status — PAUSED AFTER W1L

W0 passed local BF16 integration. W1 established approved art/motion language. W1F letterbox and W1G tracked/recentered framing are closed. W1H `512×912` solved dominant crop while preserving raw driver and remains the best documented Wan geometry baseline. W1I pose-end0.70 did not materially improve blur/structure. W1J and W1K were prepared but never executed.

W1L / Runner45 changed ref1.5->1.0, pose1.0->0.8 and20->30 steps on W1H. The user reported W1L finished and explicitly chose to move to H3. **Do not invent a W1L visual verdict without the local output.** Runner46 verifies the local W1L manifest/video/prompt before H3 bootstrap.

Preserve W1L evidence in `Z:\AI\WanAnimate2`. Do not launch another Wan inference while H3 is active.

## DECISION LOCK — MINIMAX H3 BASE REF2VA ACTIVE

MiniMax H3 Base Ref2VA is now the active screening route. Wan is paused, not exhausted. SCAIL-2 is later only if H3 fails the complete-character contract.

Canonical H3 procedure:

`docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

## H3 pinned environment

Runner46 installs a dedicated environment under:

`Z:\AI\MiniMaxH3\ComfyUI_windows_portable`

Pinned:

- ComfyUI NVIDIA portable v0.34.0;
- port8190;
- normal DynamicVRAM behavior;
- no custom nodes for H0.

Only H0-required model payload:

- Ref2VA pruned INT8 ConvRot diffusion ~21GB;
- Qwen3-VL 32B MiniMax H3 NVFP4 AWQ encoder ~15.7GB;
- H3 video VAE FP16 ~5.21GB.

No FL2VA, Turbo LoRA, embeddings, alternate H3 quantizations or audio VAE.

## H0 exact baseline

- task: Base Ref2VA;
- `<Picture 1>` = Exilada appearance/identity/anatomy/clothing/hair/art language;
- `<Video 1>` = movement/performance/timing/weight transfer only;
- same raw Wan comparison driver, normalized to24fps/124f with **no crop/resize/tracking/recentering**;
- canvas `448×800`;
- 124 frames @24fps;
- `ref_image_size=match`;
- 50 steps;
- `res_multistep` sampler;
- `beta` scheduler;
- seed0;
- H3 default sigma shifts video12/audio3;
- no Turbo LoRA.

## CURRENT GATE — Runner46 bootstrap/preflight

Run:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\46_prepare_minimax_h3_ref2va.ps1"
```

Runner46:

1. verifies W1L evidence/status;
2. stops only the known managed Wan server to free RAM/VRAM;
3. checks disk/pagefile context;
4. downloads and SHA-verifies pinned ComfyUI + only three H0 model files;
5. copies canonical Exilada reference;
6. prepares same raw driver at24fps/124f without spatial transforms;
7. validates all required live H3/core nodes and stores `object_info` + system stats;
8. writes `h3_bootstrap_manifest.json`;
9. **does not infer**.

If Runner46 fails, classify download/hash/extract/node/API/DynamicVRAM layer before changing model settings.

## NEXT ONLY AFTER Runner46 PASS — Runner47 H0

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\47_run_minimax_h3_ref2va_h0.ps1"
```

Expected H0 proof:

- `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`
- `Z:\AI\MiniMaxH3\h0_run_manifest.json`
- `Z:\AI\MiniMaxH3\h0_api_prompt.json`
- `Z:\AI\MiniMaxH3\h0_executor.log`
- `Z:\AI\MiniMaxH3\h0_gameplay_scale_proxy_frame160.mp4` when preview encoding succeeds.

A completed inference is only a technical PASS. Review full-res anatomy/topology/identity/motion and then gameplay-scale readability.

## Finite H3 next decisions

- strong topology/motion but weak identity only -> test `ref_image_size=max` before increasing output size;
- under-resolved anatomy/detail -> `480×864`, then `512×896`, then at most one 768-short-edge control;
- good H0 -> advance to actual game-relevant walking/secondary-motion driver;
- major model/task failure after integration is proven -> diagnose once; do not blindly grid-search.

## Cleanup

- H3 H0 installs one Ref2VA quantization only;
- preserve W1L proof/results;
- once H3 is technically proven active and immediate Wan return is unnecessary, remove paused Wan large checkpoint weights while preserving small evidence/results;
- keep SSD comparison evidence until explicit abandonment/final verdict.
