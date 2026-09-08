# MiniMax H3 Ref2VA — local production screening and motion-master baseline

Status date: **2026-09-08**

Status: **CANONICAL / H0 BASE50 COMPLETE PASS_CANDIDATE / TURBO4 REJECTED / BASE50 RESTORED AS MOTION-MASTER QUALITY DEFAULT**

Canonical state: `docs/PROJECT_STATE.md`.

Current end-to-end workflow: `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`.

Turbo4 rejection record: `docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`.

Runner47 integration incident: `docs/H3_H0_RUNNER47_AUDIO_VAE_INTEGRATION_FAIL_2026-09-08.md`.

## Role of H3

MiniMax H3 Ref2VA is the **complete-character motion-master generator**.

Mapping:

- `<Picture 1>` -> target character appearance/identity/anatomy/clothing/hair;
- `<Video 1>` -> real movement/performance/timing/weight transfer.

H3 output may be painterly/raster. Final runtime art is downstream deliberate pixel-art reconstruction.

## Integration history

Runner46 prepared the dedicated ComfyUI v0.34.0 environment and H0 inputs.

Runner47 was rejected before inference because `MiniMaxH3ReferenceToVideo.audio_vae` is a required node input even without audio references. Classification: **INTEGRATION_FAIL / PRE-INFERENCE**. No prompt id, no sampling, no quality evidence.

Runner48 added only the official audio VAE dependency and completed the otherwise unchanged H0.

## Minimal Base Ref2VA model set

1. `models/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors` — ~21GB.
2. `models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` — ~15.7GB.
3. `models/vae/minimax_h3_video_vae_fp16.safetensors` — ~5.21GB.
4. `models/vae/minimax_h3_audio_vae_fp32.safetensors` — ~605MB; schema-required.

Base payload ~42.5GB.

## H0 exact completed quality baseline — LOCKED

- task Ref2VA;
- Picture1 = canonical Exilada master;
- Video1 = comparison driver, timestamp-resampled only;
- `448×800`;
- `124 frames @24fps`;
- `ref_image_size=match`;
- `50 steps`;
- `res_multistep`;
- `beta`;
- seed `0`;
- no crop/resize/tracking/recentering;
- no Turbo/FL2VA/style embedding.

Evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s` (~75m05s);
- canonical output `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`.

## H0 quality verdict

**PASS_CANDIDATE / PREFERRED CURRENT MOTION-MASTER QUALITY BASELINE.**

Observed:

- stable complete-body topology;
- no destructive whole-body smear/ghost-double;
- coherent face/torso/limbs/body proportions/hair/costume language;
- visible long-hair and torn-cloth secondary response;
- restraints remain accessory geometry;
- motion is structurally readable and materially sharper than problematic Wan branches.

Residuals:

- chain detail drifts somewhat in curve/length/attachment;
- late right-foot crop follows the driver's source envelope rather than observed anatomy collapse.

`448×800` passes as motion-master generation resolution.

## Proxy clarification

The 90×160 H0 whole-frame proxy is not a final runtime-art pipeline. It was only a silhouette/legibility diagnostic.

The existing H0 video itself is a **dance/gesture-like action**, not a walk.

It has already been used for basic frame extraction/raster sheet proof and is now the correct existing motion master for downstream pixel-art reconstruction testing.

## Temporal rule

Do not assume normal production should request only 8–12 H3 frames.

The currently proven regime is `124f@24fps`. Production therefore remains:

`124-frame Base50 motion master -> automatic action-frame distillation -> compact action set -> final pixel-art reconstruction`

Typical first final sets may be 8–16 frames, action-dependent.

## H0T / Runner49 Turbo4 — REJECTED FOR PRODUCTION QUALITY

The official 4-step Ref2V Turbo path was tested and visually rejected by the user.

The user explicitly requested returning to the H0 configuration that produced the preferred video.

Therefore:

- `50 steps + res_multistep/beta` is restored;
- Turbo4 is not the default production path;
- no claim of exact Turbo4 elapsed time, prompt id or output hash should be made unless recovered from local Runner49 evidence;
- future speed work must be a separate controlled hypothesis and must match Base50 quality.

The Turbo4 LoRA is no longer an active dependency after evidence preservation.

## Current downstream direction

Do **not** generate another long action merely to prove spritesheet rendering.

Immediate pipeline work uses the existing H0 dance/gesture video:

1. extract/select a coherent action frame set;
2. create automatic alpha/pivot/alignment;
3. install/validate FLUX.1 Kontext [dev] locally as the preferred first pixel-art renderer candidate;
4. reconstruct the selected set as deliberate high-quality pixel art;
5. split/pack final spritesheet + preview + atlas/manifest.

## H3 integration into future local UI

The local authoring interface will expose H3 as a locked production preset by default:

- Base Ref2VA;
-448×800;
-124f@24fps;
-50 steps;
- res_multistep/beta;
- seed0;
- ref_image_size=match.

Advanced controls may exist for controlled experiments, but normal jobs must not silently drift from the approved preset.

The interface will additionally accept character reference or text-generated reference, relative world scale, driver video and action preset. Those orchestration responsibilities are defined in `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`.

## Cleanup

- keep Base H3 set;
- Turbo4 LoRA may be deleted after preserving local output/log/manifest evidence;
- do not accumulate FL2VA/style/alternate quantizations without evidence;
- Wan large weights may be removed while preserving W1H/W1L proof/results;
- keep SSD comparison evidence until explicit abandonment/final verdict.
