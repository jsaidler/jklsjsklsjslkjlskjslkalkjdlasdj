# Character Animation Production — Living Decision Record

Status date: **2026-09-08**

Status: **MINIMAX H3 REF2VA H0 PASS_CANDIDATE AS MOTION MASTER. FINAL RUNTIME OUTPUT IS HIGH-QUALITY PIXEL ART. H0T TURBO4 THROUGHPUT GATE PRECEDES H1-S WALK PRODUCTION.**

Canonical state: `docs/PROJECT_STATE.md`.

Detailed H1-S production definition: `docs/H1S_MINIMAX_H3_SPRITESHEET_PRODUCTION_PASS_2026-09-08.md`.

## Hard production constraints

- complete Exilada appearance reference + separate real driving video;
- driver identity/clothing/hair may differ completely;
- infer locomotion, soft response, hair inertia, cloth/material/wind and restraint/accessory dynamics automatically;
- no routine manual rigging, keyframing, simulation repair, mask repair, repainting or hand compositing;
- runtime consumes complete precomposed sprite frames.

## Final rendering architecture — UPDATED

H3 is now treated as the **motion-master generator**, not the final visible-art renderer.

Production chain:

`pixel-art Exilada reference + real driver -> H3 complete-character motion master -> automatic action/cycle distillation -> automatic segmentation/alignment -> high-quality pixel-art reconstruction -> complete transparent spritesheet/atlas + metadata -> runtime playback`

The tiny H0 whole-frame proxy is historical legibility evidence only. It is not a production asset and does not define final game quality.

## Final visual target

Runtime sprites must be deliberate high-quality pixel art at roughly `128px` visible protagonist height, preserving the locked Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell sword-and-sorcery language.

H3 painterly output remains useful because it carries coherent anatomy, hair, cloth and material motion into the next stage.

## Wan record — PAUSED

- W1 established useful painterly/motion language.
- W1F and W1G are closed framing methods.
- W1H solved dominant crop with raw-driver geometry.
- W1I did not materially improve blur/structure.
- W1L completed ref1.0 + pose0.80 +30 steps; Wan paused afterward.

Preserve W1H/W1L proof. H3 has advanced enough that Wan large weights may be cleaned while results remain.

## Screening order

1. MiniMax H3 Ref2VA — active / H0 PASS_CANDIDATE as motion master;
2. Wan-Animate-2 — paused, not exhausted;
3. SCAIL-2 — later only if H3 fails a later production gate.

## H3 minimal local stack

Workspace: `Z:\AI\MiniMaxH3`.

Base Ref2VA set:

- `minimax_h3_ref2va_pruned_int8_convrot.safetensors`;
- `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`;
- `minimax_h3_video_vae_fp16.safetensors`;
- schema-required `minimax_h3_audio_vae_fp32.safetensors`.

Base payload ~42.5GB.

## H0 completed quality baseline

- `448×800`;
-124 frames @24fps;
- `ref_image_size=match`;
-50 steps;
- `res_multistep/beta`;
- seed0;
- canonical Exilada Picture1;
- raw comparison driver Video1 with timestamp resampling only.

Evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s`;
- output `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`.

Verdict: **PASS_CANDIDATE / family advances.** Stable body topology, coherent hair/cloth motion, no destructive whole-body smear. Chain details drift somewhat. Late crop follows the driver/source envelope.

## Temporal-production correction

Do not assume the normal H3 production route can simply generate 8–12 frames.

The current H3 implementation uses the model's valid `17k+5` frame grid and documents its trained video range around `124–362` frames at24fps. H0 therefore remains the proven temporal regime.

For production:

- generate a 124-frame motion master using a fast acceptable sampling path;
- extract only the useful action/cycle;
- distill to roughly 12 unique gameplay frames;
- pixel-art-render those selected frames.

Shorter H3 generation windows may be tested later as explicit optimization, not assumed safe now.

## CURRENT GATE — H0T / Runner49

H0 took ~75 minutes and is too slow for ordinary per-action iteration.

Before generating a new walking clip, benchmark the official Ref2V Turbo4 path on the exact same H0 inputs.

Runner49:

`tools/structured-2d-character-pipeline/49_run_minimax_h3_ref2va_h0t_turbo4.ps1`

Changes from H0:

- official `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors`;
- LoRA strength1.0;
- 4 steps;
- `res_multistep/simple`, following the official R2V template's Lightning/Turbo switch.

Unchanged:

- Picture1/Video1;
-448×800;
-124f@24fps;
- `ref_image_size=match`;
- seed0;
- prompt.

H0T must be compared directly to H0 for topology, identity, motion and secondary dynamics. Speed alone is not enough.

## H1-S walk motion master — after H0T decision

Use a fixed-camera full-body screen-left walk, mostly lateral/slight3/4 near the locked `72°` direction, with safe real margins and one clear gait cycle.

To remain inside the proven 124-frame H3 regime, a clean gait cycle may be automatically repeated/tiled through the conditioning interval.

The 124-frame result is a **motion master**, not a 124-frame runtime walk.

## Action distillation

First walk target: **12 unique sprite frames**.

Automatic stage must:

1. detect/select one coherent full gait cycle;
2. phase-distribute 12 useful frames;
3. reject obvious crop/structural failure frames;
4. segment complete character including hair/cloth/chains;
5. align a stable ground/pivot reference without deleting legitimate vertical motion;
6. output high-resolution transparent frames/contact sheet.

No manual masks or per-frame repair.

## Pixel-art reconstruction — separate gate

Selected frames then enter a dedicated pixel-art reconstruction stage with the canonical Exilada reference.

Preferred validation strategy is to present the whole selected action strip/contact sheet to the renderer so palette, silhouette and design remain coherent across frames rather than independently redrawing each frame.

Simple downscale/nearest-neighbor/palette quantization is only a cheap control and is not assumed sufficient for final quality.

## First runtime spritesheet target

- visible character height ~`128px`;
-12 unique walk frames;
- approximate art playback rate `12fps`, with timing controlled by gameplay metadata;
- transparent RGBA complete-character cells;
- initial review cell `192×192`;
-4×3 sheet = `768×576`;
- optional trimmed atlas + JSON pivots/durations for production.

## Cleanup

- keep minimal H3 Base set;
- Runner49 adds only the official ~1.96GB Ref2V Turbo4 LoRA for an explicit throughput hypothesis;
- do not add FL2VA/style/alternate quantizations without evidence;
- paused Wan large checkpoints may be removed while preserving W1H/W1L proof;
- keep SSD comparison evidence until explicit abandonment/final verdict.
