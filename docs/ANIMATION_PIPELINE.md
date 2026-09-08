# Character Animation Production — Living Decision Record

Status date: **2026-09-08**

Status: **COMPLETE-CHARACTER RAW-VIDEO GENERATION ACTIVE. MINIMAX H3 BASE REF2VA H0 IS PASS_CANDIDATE. NEXT GATE IS GAME-RELEVANT WALK. WAN IS PAUSED.**

Canonical state: `docs/PROJECT_STATE.md`.

Detailed H3 procedure: `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`.

## Hard production constraints

- complete Exilada appearance reference + separate real driving video;
- driver identity/clothing/hair may differ completely;
- infer locomotion, soft response, hair inertia, cloth/material/wind and restraint/accessory dynamics automatically;
- no routine manual rigging, keyframing, simulation repair, mask repair, repainting or hand compositing;
- runtime consumes complete precomposed sprite frames.

## Visual direction

Painterly illustrated dark fantasy with explicit 1980s sword-and-sorcery charge: Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell. Adult sensuality/nudity is legitimate. Localized motion blur may be positive; global smear, anatomy loss and topology drift are defects.

## Wan record — PAUSED

- W1 established approved painterly/motion language.
- W1F letterbox and W1G tracked/recentered framing are closed failures.
- W1H `512×912` with untouched raw driver solved dominant crop and improved temporal body coherence.
- W1I pose-end0.70 did not materially improve heavy blur/structure.
- W1L completed ref1.0 + pose0.80 +30 steps; Wan paused afterward.

Preserve W1H/W1L proof. H3 has now advanced enough that Wan large weights may be cleaned while proof remains.

## Screening order

1. MiniMax H3 Base Ref2VA — active / H0 PASS_CANDIDATE;
2. Wan-Animate-2 — paused, not exhausted;
3. SCAIL-2 — later only if H3 fails a later production gate.

## H3 architecture

`<Picture 1> Exilada appearance + <Video 1> real movement/performance -> complete generated character video -> automatic extraction/downsample/packing -> spritesheet`

The prompt treats Picture1 as the only appearance/identity/anatomy/clothing/hair/art-language source and Video1 as movement/timing/weight-transfer only.

## Minimal H3 local stack

Workspace: `Z:\AI\MiniMaxH3`.

- ComfyUI Windows NVIDIA portable v0.34.0;
- Ref2VA pruned INT8 ConvRot diffusion;
- Qwen3-VL NVFP4 AWQ encoder;
- video VAE;
- schema-required H3 audio VAE.

Total model payload ~42.5GB. Audio VAE is required by the Ref2VA node but H0 uses no audio reference and does not decode/output audio.

No FL2VA, Turbo, style embedding or alternate Ref2VA quantization is active.

## H0 completed baseline

- `448×800`;
-124 frames @24fps;
- `ref_image_size=match`;
-50 steps;
- `res_multistep/beta`;
- seed0;
- canonical Exilada as Picture1;
- same raw Wan comparison driver as Video1, timestamp-resampled only;
- no spatial driver transforms;
- no Turbo.

Evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s`;
- output `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- gameplay proxy `Z:\AI\MiniMaxH3\h0_gameplay_scale_proxy_frame160.mp4`.

## H0 quality verdict

**PASS_CANDIDATE / FAMILY ADVANCES.**

The uploaded full output and proxy show:

- materially stable full-body topology;
- no destructive whole-body ghosting/smear;
- stable face/torso/limbs/body proportions/hair/costume language;
- visible coherent hair and torn-cloth secondary motion;
- restraints remain accessories rather than morphing into body parts;
- sharp enough anatomy for motion readability;
- strong compatibility with the locked painterly dark-fantasy art direction;
- clear gameplay-scale silhouette near the ~128px runtime target.

Residuals:

- chain details drift somewhat;
- right foot becomes partially cropped at the right edge late in the clip; treat as driver/framing envelope rather than topology collapse.

## Resolution policy

`448×800` passes. Do not raise output resolution or use `ref_image_size=max` unless a later test produces a specific under-resolution/identity failure.

This validates the production hypothesis that source generation can be materially smaller than the model's usual 768-short-edge regime because runtime sprites are ~128px tall.

## NEXT GATE — H1 WALK

Use a real fixed-camera full-body walk with safe margins, screen-left mostly lateral/slight3/4, targeting the locked `72°` locomotion baseline and containing at least one complete gait cycle.

Keep H0 settings initially:

- `448×800`;
- Base50;
- `res_multistep/beta`;
- seed0;
- `ref_image_size=match`.

H1 must prove usable locomotion timing/weight transfer, H0-level topology, secondary hair/cloth/restraint response and gameplay-scale readability. Only after H1 passes should the pipeline stress wind/restraints/secondary dynamics and later optimize speed/Turbo.

## Dual-resolution QA — REQUIRED

Every candidate is evaluated at source scale and gameplay scale. Downsampling may erase harmless texture noise/local blur but cannot excuse topology loss, missing limbs, broken silhouette or identity drift.

## Cleanup

- keep only minimal active H3 Ref2VA files;
- paused Wan large checkpoint weights may now be removed while preserving W1H/W1L videos/prompts/manifests/logs;
- do not accumulate H3 FL2VA/Turbo/style/alternate quantizations without an explicit later hypothesis;
- keep SSD comparison evidence until explicit abandonment/final verdict.
