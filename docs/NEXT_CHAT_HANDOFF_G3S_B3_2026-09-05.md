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

W1H remains the best documented Wan geometry baseline. W1I did not materially fix blur/structure. W1L completed with ref1.0 + pose0.80 +30 steps. Preserve W1L evidence; do not invent its visual verdict without reviewing the local video. Do not launch another Wan inference while H3 is active.

## MiniMax H3 Base Ref2VA — ACTIVE

Canonical procedure:

`docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

Incident record:

`docs/H3_H0_RUNNER47_AUDIO_VAE_INTEGRATION_FAIL_2026-09-08.md`

## Runner46

Runner46 successfully installed/verifed the pinned H3 environment, three initial model files, inputs, object-info and normalized driver. That is an infrastructure bootstrap pass, but it did **not** prove the final API graph was complete.

## Runner47 — FAILED BEFORE INFERENCE

User terminal:

```text
HTTP 400
prompt_outputs_failed_validation
MiniMaxH3ReferenceToVideo
Required input is missing: audio_vae
```

Classification: **INTEGRATION_FAIL / PRE-INFERENCE PROMPT VALIDATION**.

Important:

- no `prompt_id`;
- no H3 denoising;
- no model-quality evidence;
- do not change resolution/prompt/sampling because of this failure.

Root cause: in pinned ComfyUI v0.34.0, `MiniMaxH3ReferenceToVideo.audio_vae` is a required input even when no audio reference is used.

## Corrected minimal H3 dependency set

Existing:

- Ref2VA pruned INT8 ConvRot diffusion ~21GB;
- Qwen3-VL NVFP4 AWQ encoder ~15.7GB;
- video VAE ~5.21GB.

Additional required schema dependency:

- `minimax_h3_audio_vae_fp32.safetensors`;
- 605,254,808 bytes (~605MB);
- SHA256 `8e505d95dd1561d47abd43d4238fd40d9bb1ae9e147ed0a4cba778d76ae4db48`.

Corrected H0 payload ~42.5GB.

Audio VAE is only wired to satisfy Ref2VA schema. H0 still has no audio reference and no audio decode/output.

## H0 quality baseline — unchanged

- Base Ref2VA;
- Picture1 = Exilada appearance;
- Video1 = same raw Wan driver normalized to24fps/124f with no spatial transforms;
- `448×800`;
-124f @24fps;
- `ref_image_size=match`;
-50 steps;
- `res_multistep` + `beta`;
- seed0;
- no FL2VA/Turbo/embedding;
- no audio reference/decode.

## CURRENT GATE — Runner48

Run:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\48_run_minimax_h3_ref2va_h0_audio_vae_fix.ps1"
```

Runner48 downloads/verifies only the missing official audio VAE, wires it to the Ref2VA node, and re-submits the otherwise unchanged H0.

If terminal reaches:

```text
H3-H0: prompt_id=...
```

actual H3 inference has started. Leave it running unless Comfy reports a new execution error.

Expected successful proof:

- `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`
- `Z:\AI\MiniMaxH3\h0_run_manifest.json`
- `Z:\AI\MiniMaxH3\h0_api_prompt.json`
- `Z:\AI\MiniMaxH3\h0_executor.log`
- `Z:\AI\MiniMaxH3\h0_gameplay_scale_proxy_frame160.mp4` when preview encoding succeeds.

## After Runner48

If inference completes:

1. inspect full-res anatomy/topology/identity/motion;
2. inspect gameplay proxy;
3. only then choose the smallest next branch.

Finite decisions:

- strong topology/motion but weak identity -> `ref_image_size=max`;
- under-resolved anatomy/detail -> `480×864`, then `512×896`, then at most one 768-short-edge control;
- good H0 -> game-relevant walking/secondary-motion driver;
- major model/task failure after integration proven -> diagnose once, not endless tuning.

## Cleanup

- keep audio VAE while H3 Ref2VA is active;
- do not accumulate FL2VA/Turbo/alternate quantizations;
- preserve W1L proof/results;
- remove paused Wan large checkpoint weights only after H3 is technically proven active enough that immediate return is unnecessary;
- keep SSD comparison evidence until explicit abandonment/final verdict.
