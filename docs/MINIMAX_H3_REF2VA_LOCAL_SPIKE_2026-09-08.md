# MiniMax H3 Ref2VA — historical game-motion spike

Original spike date: **2026-09-08**  
Superseded as active project direction: **2026-09-15**  
Status: **HISTORICAL EVIDENCE / NOT CURRENT PRODUCTION CONTRACT**

Current canonical state: `docs/PROJECT_STATE.md`.  
Current H3 role: `docs/VIDEO_STUDIO.md`.  
Current personal-video validation: `docs/VIDEO_STUDIO_H3_VALIDATION_2026-09-15.md`.

## Supersession notice

This document originally defined MiniMax H3 as the Roguelite complete-character motion-master generator. The game has since been abandoned as the active project objective. Any statements below about sprites, Exilada, motion-master generation, runtime art or game-specific Turbo rejection are retained only as historical evidence.

They do **not** override the 2026-09-15 Local Video Studio decisions.

In particular, the old finding **"Turbo4 rejected for production quality"** applied to a demanding game-motion-master task. It must not be generalized to the current talking-video task. The new personal-video tests directly validated the 4-step Ref2V Turbo path for identity + voice + autonomous speaking motion + new scenario, and that path is now the first Video Studio production default.

## Historical role

MiniMax H3 Ref2VA was evaluated as a complete-character motion-master generator:

- `<Picture 1>` supplied target character appearance/identity/anatomy/clothing/hair;
- `<Video 1>` supplied real movement/performance/timing/weight transfer;
- H3 output was intended to feed downstream sprite reconstruction.

## Historical minimal Base payload

1. `minimax_h3_ref2va_pruned_int8_convrot.safetensors` — ~21 GB.
2. `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` — ~15.7 GB.
3. `minimax_h3_video_vae_fp16.safetensors` — ~5.21 GB.
4. `minimax_h3_audio_vae_fp32.safetensors` — ~605 MB.

This payload remains useful and is now reused by the Video Studio.

## Historical H0 Base50 result

The game-motion baseline completed with:

- task: Ref2VA;
- 448×800;
- 124 frames @ 24 fps;
- `ref_image_size=match`;
- 50 steps;
- `res_multistep` / `beta`;
- seed 0;
- no Turbo LoRA;
- output: `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- output SHA256: `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`;
- elapsed: ~4504.8 s (~75m05s).

Historical visual verdict: **PASS_CANDIDATE** for the game motion-master hypothesis, with stable body topology, coherent complete-body motion and visible secondary hair/cloth response.

## Historical Turbo4 result

A later 4-step game-motion test was visually rejected relative to the H0 Base50 result, so the old game pipeline restored Base50 as its preferred quality baseline.

That rejection is task-specific and has been superseded for the active project by the 2026-09-15 personal-video validation.

## What remains relevant today

The old spike established several facts that still matter:

- the RTX 3060 12 GB machine can execute the H3 INT8 Ref2VA stack locally;
- the H3 video and audio VAEs are valid local dependencies;
- `res_multistep` is a working sampler family;
- 24 fps is the H3 temporal contract;
- local API-driven ComfyUI orchestration is viable;
- infrastructure/integration failures should not be misclassified as model-quality failures.

Everything specific to sprite authoring, Exilada, action-frame distillation or game runtime presentation is historical only.
