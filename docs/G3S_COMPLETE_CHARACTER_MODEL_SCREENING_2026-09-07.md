# G3S — Complete-character animation model screening

Status date: **2026-09-08**

Status: **CANONICAL / MINIMAX H3 REF2VA H0 BASE50 PASS_CANDIDATE AND PREFERRED QUALITY BASELINE / TURBO4 REJECTED / WAN PAUSED / FINAL PIXEL-ART RENDERER SCREENED SEPARATELY**

## Purpose

Select a production family that generates a coherent complete-character motion master from:

1. approved character appearance reference;
2. arbitrary real driving video for movement/performance.

The motion model must consume richer information than skeleton-only pose and automatically infer locomotion/action, soft-body response, hair inertia, cloth/material/wind behavior and restraints/accessories. Routine manual repair is forbidden.

Final runtime pixel-art reconstruction is explicitly a **separate downstream rendering gate**.

## Screening order

1. **MiniMax H3 Ref2VA — ACTIVE / H0 Base50 PASS_CANDIDATE and current preferred quality baseline.**
2. Wan-Animate-2 — paused after W1L, not exhausted.
3. SCAIL-2 — later only if H3 fails a future motion-production gate.

## Comparison protocol

- distinguish infrastructure, integration, configuration and model/task failures;
- fixed inputs/seeds unless a variable is intentionally changed;
- no seed fishing or manual rescue;
- successful inference is not automatically a quality PASS;
- pre-inference integration failures are zero model-quality evidence;
- faster settings do not replace the quality baseline unless they are visually equivalent.

## Wan compact history

- W0 local Base-BF16 integration passed with `--disable-pinned-memory`.
- W1 established useful painterly/motion language.
- W1F letterbox and W1G tracked/recentered framing are closed failures.
- W1H `512×912` with untouched driver solved dominant crop and became best Wan geometry baseline.
- W1I pose-end0.70 did not materially improve blur/structure.
- W1J/W1K prepared but never executed.
- W1L completed ref1.0 + pose0.80 +30 steps; Wan paused afterward.

## MiniMax H3 Base Ref2VA — H0 COMPLETE

Canonical procedure: `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`.

Integration incident: `docs/H3_H0_RUNNER47_AUDIO_VAE_INTEGRATION_FAIL_2026-09-08.md`.

Minimal Base stack:

- Ref2VA INT8 ConvRot diffusion ~21GB;
- Qwen3-VL NVFP4 AWQ encoder ~15.7GB;
- video VAE ~5.21GB;
- schema-required audio VAE ~605MB.

## H0 exact completed baseline — PREFERRED

- Picture1 = canonical Exilada master;
- Video1 = raw comparison driver, timestamp-resampled only;
- `448×800`;
- `124f@24fps`;
- `ref_image_size=match`;
- `50 steps`;
- `res_multistep/beta`;
- seed0;
- no spatial driver transforms;
- no Turbo/FL2VA/style embedding.

Evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s`;
- output SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`.

## H0 visual verdict

**PASS_CANDIDATE / FAMILY ADVANCES AS MOTION-MASTER CANDIDATE.**

Strengths:

- stable complete-body topology;
- no destructive global smear/ghost-double;
- coherent face/torso/limbs/body proportions/hair/costume language;
- visible hair and torn-cloth secondary motion;
- restraints remain accessory geometry;
- materially sharper motion than problematic Wan branches.

Residuals:

- chain detail still drifts somewhat;
- late right-foot crop follows driver/source envelope;
- H3 painterly appearance is intermediate rather than final runtime art.

`448×800` passes as motion-master generation size.

## Turbo4 / Runner49 — SETTING QUALITY FAIL

Runner49 tested the official Ref2V Turbo4 path with the H0 comparison structure.

The user visually rejected the 4-step result and explicitly requested returning to the original H0 Base50 settings.

Classification:

**MODEL/SETTING QUALITY FAIL FOR TURBO4; NOT A FAILURE OF THE H3 FAMILY.**

Therefore:

- Turbo4 is not production-default;
- Base50 is restored;
- exact Turbo4 elapsed time/prompt id/hash must not be invented if not recovered from local evidence;
- future speed work must prove Base50-equivalent quality.

Record: `docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`.

## Current H3 production stance

Quality-first motion generation stays at:

`448×800 / 124f@24fps / 50 steps / res_multistep-beta / seed0 / ref_image_size=match`

The ~75-minute cost is accepted for now rather than knowingly degrading the motion master.

Do not generate another long clip simply to prove downstream rendering. Reuse existing motion masters where possible.

## Existing H0 action

The H0 result is a **dance/gesture-like action**, not a walk.

It is the immediate downstream test source for final pixel-art reconstruction.

## Final-runtime art boundary

The project explicitly separates:

- H3 motion quality;
- action/frame extraction quality;
- final pixel-art rendering quality.

A beautiful H3 video is insufficient unless the runtime renderer succeeds. Conversely, failure of a downstream pixel-art renderer does not retroactively invalidate a good H3 motion master.

## Next model gate is downstream, not another motion family

Preferred first final pixel-art renderer candidate: **FLUX.1 Kontext [dev]**, pending local quality/hardware/license validation.

This is not part of the H3 motion-family screening itself.

The local authoring architecture and UI are defined in:

`docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`

## Cleanup

- keep Base H3 set;
- Turbo4 LoRA may be removed after preserving local rejection evidence;
- paused Wan large weights may be deleted while preserving W1H/W1L proof;
- keep SSD comparison evidence until explicit abandonment/final verdict.
