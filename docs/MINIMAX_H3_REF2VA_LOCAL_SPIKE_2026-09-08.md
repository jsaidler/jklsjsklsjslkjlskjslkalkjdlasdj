# MiniMax H3 Ref2VA — local production screening and motion-master baseline

Status date: **2026-09-08**

Status: **CANONICAL / H0 COMPLETE PASS_CANDIDATE / H0T TURBO4 THROUGHPUT GATE CURRENT / H1-S WALK AFTER SPEED DECISION**

Canonical state: `docs/PROJECT_STATE.md`.

H1-S production definition: `docs/H1S_MINIMAX_H3_SPRITESHEET_PRODUCTION_PASS_2026-09-08.md`.

Runner47 integration incident: `docs/H3_H0_RUNNER47_AUDIO_VAE_INTEGRATION_FAIL_2026-09-08.md`.

## Role of H3 in the production architecture

MiniMax H3 Ref2VA is now screened as the **complete-character motion-master generator**.

It maps:

- `<Picture 1>` -> Exilada appearance/identity/anatomy/clothing/hair;
- `<Video 1>` -> real movement/performance/timing/weight transfer.

H3 output may be painterly/raster. Final runtime art is now a separate high-quality pixel-art reconstruction stage downstream of automatic action-frame extraction.

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

## H0 exact completed quality baseline

- task Ref2VA;
- Picture1 = canonical Exilada master;
- Video1 = comparison driver, timestamp-resampled only;
- `448×800`;
-124 frames @24fps;
- `ref_image_size=match`;
-50 steps;
- `res_multistep/beta`;
- seed0;
- no crop/resize/tracking/recentering;
- no Turbo/FL2VA/style embedding.

Evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s` (~75m05s);
- canonical output `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`.

## H0 quality verdict

**PASS_CANDIDATE / FAMILY ADVANCES.**

Observed:

- stable complete-body topology across the sequence;
- no destructive whole-body smear/ghost-double;
- coherent face/torso/limbs/body proportions/hair/costume language;
- visible long-hair and torn-cloth secondary response;
- restraints remain accessory geometry rather than becoming body parts;
- motion remains structurally readable and materially sharper than problematic Wan runs.

Residuals:

- chain detail drifts somewhat in curve/length/attachment;
- late right-foot crop follows the driver's source envelope rather than observed anatomy collapse.

`448×800` therefore passes as a motion-master generation resolution.

## Proxy clarification

The 90×160 H0 whole-frame proxy is **not** a final runtime-art pipeline and is retired as a production target. It was only a silhouette/legibility diagnostic.

Final runtime output must be reconstructed as deliberate high-quality pixel art after automatic action-frame extraction/alignment.

## Temporal-production correction

Do not assume production should reduce H3 generation itself to 8–12 frames.

Current H3 uses the `17k+5` temporal grid and documents a trained video range around `124–362` frames @24fps. The safe production baseline remains 124 frames until evidence shows a shorter window preserves quality.

Therefore:

`fast 124-frame motion master -> automatic action/cycle distillation -> ~12 selected sprite frames -> pixel-art reconstruction`

## Why throughput is now the immediate gate

H0 took ~75 minutes. That is acceptable for one quality spike but too slow for ordinary per-action iteration.

The next walking inference should **not** be another Base50 hour-long job until a practical throughput path is tested.

## H0T / Runner49 — CURRENT

The official ComfyUI R2V workflow exposes a Lightning/Turbo switch using:

- `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors`;
- LoRA strength `1.0`;
-4 steps.

Official LoRA evidence:

- size ~1.96GB;
- SHA256 `5b9ab5ade15d0775676d01a907268a69a1468dc6033b3b0d3ded5502f3ebb84c`.

Runner49 exact comparison:

- same H0 Picture1/Video1;
- same448×800;
- same124f@24fps;
- same `ref_image_size=match`;
- same seed0 and prompt;
- add Turbo4 LoRA strength1.0;
-4 steps;
- `res_multistep/simple`, matching the official template's Turbo switch path.

Runner:

`tools/structured-2d-character-pipeline/49_run_minimax_h3_ref2va_h0t_turbo4.ps1`

Expected evidence:

- `Z:\AI\MiniMaxH3\h0t_exilada_ref2va_448x800_124f_turbo4.mp4`;
- `Z:\AI\MiniMaxH3\h0t_run_manifest.json`;
- `Z:\AI\MiniMaxH3\h0t_api_prompt.json`;
- `Z:\AI\MiniMaxH3\h0t_executor.log`.

H0T passes only if speed improves materially **and** H0-level topology, identity, motion and secondary dynamics survive.

## H1-S walk after H0T

If Turbo4 passes, use it for the first real game walk motion master.

Driver:

- fixed camera;
- one adult full-body performer;
- screen-left travel;
- mostly lateral/slight3/4 near locked `72°`;
- safe real margins around head, feet and lateral motion;
- one clear gait cycle;
- performer appearance irrelevant.

A clean gait cycle may be automatically repeated/tiled to fill the proven124-frame H3 conditioning interval.

The generated124 frames are a motion master, not the final runtime walk.

## Action distillation / runtime frame target

First walk target: **12 unique frames** across one stable generated gait cycle.

Automatic downstream steps:

1. detect/select one coherent gait cycle;
2. distribute 12 frames across cycle phase/motion;
3. reject obvious crop/structural failure frames;
4. segment complete character including hair/cloth/chains;
5. align stable ground/pivot while preserving valid vertical bob;
6. build transparent high-resolution action strip/contact sheet;
7. send the whole selected set to the final pixel-art reconstruction gate.

No manual masks or per-frame repair.

## Final pixel-art target

Initial runtime review target:

- character ~128px tall;
-12 frames;
- cell192×192;
-4×3 sheet =768×576;
- transparent RGBA complete-character sprites;
- optional trimmed atlas + JSON frame/pivot/duration metadata.

The exact pixel-art reconstruction model/tool is not yet proven and must be validated separately.

## Cleanup

- keep Base H3 set;
- add only the official Ref2V Turbo4 LoRA for the explicit throughput hypothesis;
- do not accumulate FL2VA/style/alternate quantizations;
- Wan large weights may be removed while preserving W1H/W1L proof/results;
- keep SSD comparison evidence until explicit abandonment/final verdict.
