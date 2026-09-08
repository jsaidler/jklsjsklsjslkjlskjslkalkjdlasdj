# MiniMax H3 Ref2VA local production tooling

Status: **ACTIVE — H0 Base50 is the preferred motion-master quality baseline. Turbo4 was visually rejected and is no longer the production default. Final runtime art is a separate local pixel-art reconstruction stage.**

Canonical H3 procedure: `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`.

Canonical local authoring workflow: `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`.

Turbo4 rejection: `docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`.

## Paths

- project: `D:\GOOGLE DRIVE\DEV\Roguelite`
- H3 workspace: `Z:\AI\MiniMaxH3`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- `D:\AI` stale/invalid.

## H0 completed quality baseline — CURRENT DEFAULT

Base Ref2VA:

- `448×800`;
- `124f @24fps`;
- `50 steps`;
- `res_multistep/beta`;
- seed0;
- `ref_image_size=match`;
- no Turbo;
- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s`;
- output `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`.

Verdict: **PASS_CANDIDATE / preferred current motion-master quality baseline.**

## Final-art boundary

H3 output is not final runtime pixel art.

Current production chain:

`approved character reference + real driver + action metadata -> H3 Base50 motion master -> automatic action-frame distillation -> alpha/pivot/alignment -> FLUX.1 Kontext [dev] pixel-art reconstruction -> transparent spritesheet/atlas`

The existing H0 result is a **dance/gesture-like action**, not a walk, and is the immediate downstream renderer test source.

## Temporal rule

Do not default to generating only 8–12 H3 frames. The currently proven regime remains `124f@24fps`.

Generate the Base50 master, then distill an action-dependent compact runtime set, typically 8–16 frames for first tests.

## Tool files

### `prepare_h0_driver.py`

Builds the comparison driver at24fps/124f without spatial transforms.

### `run_h0_ref2va.py`

Base50 H0 executor.

### `run_h0_ref2va_audio_vae_required.py`

Runner48 integration wrapper adding the schema-required audio VAE.

### `run_h0t_ref2va_turbo4.py`

Historical Runner49 throughput experiment. Uses official Turbo4 LoRA, 4 steps and `res_multistep/simple`.

**Status: rejected for production quality by user visual review.** Keep only for historical comparison/evidence; do not use as default.

## Runner49 status

`tools/structured-2d-character-pipeline/49_run_minimax_h3_ref2va_h0t_turbo4.ps1`

This runner remains in the repository as test history.

Do not rerun it as the normal production path unless a future explicit comparison requires it.

Exact Turbo4 elapsed time/prompt id/output hash must not be invented if not recovered from local evidence.

After preserving local output/log/manifest evidence, the Turbo4 LoRA may be deleted to recover disk because it is not an active dependency.

## Local authoring UI direction

The finished workflow will be wrapped in a local UI defined by `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`.

The UI must support:

- existing reference image or locally generated text-described reference;
- relative world scale;
- real action-video upload;
- action-type preset/custom action;
- locked H3 Base50 production preset;
- downstream extraction/pixel-art rendering/packing;
- final spritesheet/preview/atlas/manifest outputs.

Gradio is the current V1 scaffold choice.

## Next technical gate

Do **not** generate another H3 action merely to test the downstream pipeline.

Install/validate **FLUX.1 Kontext [dev]** locally in a separate workspace and reuse the existing H0 dance/gesture video for the first final-style pixel-art spritesheet proof.

Kontext's open-weight license is non-commercial; commercial shipping later requires appropriate BFL licensing or a compatible renderer. SDXL/img2img remains fallback.

## Cleanup

Keep Base H3 files. Turbo4 LoRA may be removed after evidence preservation. Do not accumulate FL2VA/style/alternate quantizations without a specific hypothesis. Wan large weights may be removed while proof/results remain.
