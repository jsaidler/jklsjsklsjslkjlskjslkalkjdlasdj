# Roguelite — Current Project State

Status date: **2026-09-08**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VISUAL_DIRECTION.md`
3. `docs/H1S_MINIMAX_H3_SPRITESHEET_PRODUCTION_PASS_2026-09-08.md`
4. `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`
5. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
6. `docs/ANIMATION_PIPELINE.md`
7. `docs/CHARACTERS.md`
8. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`
9. `docs/H3_H0_RUNNER47_AUDIO_VAE_INTEGRATION_FAIL_2026-09-08.md`
10. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing action updates the thematic docs, this file and the active handoff before completion is reported.

## Local paths — LOCKED

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- active MiniMax H3 workspace: `Z:\AI\MiniMaxH3`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` is stale/historical.

## Game/runtime presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic-like gameplay camera;
- native raster `640×360`;
- pitch `26°`;
- protagonist about `128px` tall;
- first locomotion family screen-left / mostly lateral-three-quarter;
- current facing baseline `72°`;
- runtime consumes complete precomposed character sprites only.

No visible runtime body/hair/clothing/equipment layer assembly.

## Final visible-art target — UPDATED / LOCKED 2026-09-08

Final runtime character graphics return to **deliberate high-quality pixel art**.

The canonical Exilada reference is pixel-art based. H3 may reinterpret it into a painterly/raster video while solving motion, but that video is now classified as an **intermediate motion master**, not the final runtime art.

Final production chain:

`pixel-art Exilada reference + raw real driver -> H3 complete-character motion master -> automatic action/cycle distillation -> automatic segmentation/alignment -> high-quality pixel-art reconstruction -> transparent complete-character spritesheet/atlas + metadata -> ordinary sprite playback`

The exact pixel-art reconstruction model/tool is a separate production gate. The tiny H0 whole-frame proxy is retired as a production-art concept; it remains only historical legibility evidence.

The 1980s sword-and-sorcery lineage remains active: Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell. Adult sensuality/nudity remains legitimate.

## Complete-character production contract — LOCKED

The motion-generation system must combine a complete Exilada appearance reference with an arbitrary real driving video and automatically infer richer motion than a skeleton-only stream: locomotion/weight, soft response, long-hair inertia, cloth/material behavior and restraint/accessory dynamics.

Routine manual rigging, keyframing, mask repair, repainting, per-frame cleanup and hand compositing remain prohibited.

## Model-screening order

1. **MiniMax H3 Ref2VA — ACTIVE / H0 PASS_CANDIDATE as motion-master family.**
2. Wan-Animate-2 — **PAUSED AFTER W1L**, not exhausted.
3. SCAIL-2 — later only if H3 fails a later production gate.

## Wan compact record

- W0 local BF16 integration passed with `--disable-pinned-memory`.
- W1 established useful painterly/motion language.
- W1F letterbox and W1G tracked/recentered framing are closed failures.
- W1H `512×912` with untouched raw driver solved dominant crop and became best Wan geometry baseline.
- W1I pose-end0.70 did not materially improve blur/structure.
- W1J/W1K prepared but never executed.
- W1L completed ref1.0 + pose0.80 +30 steps; Wan paused afterward.

Preserve W1H/W1L proof/results. H3 has advanced enough that Wan large weights may be removed while proof remains.

## MiniMax H3 integration history

Canonical H3 procedure: `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`.

- Runner46 prepared pinned ComfyUI v0.34.0 and H0 inputs.
- Runner47 failed **before inference** because `MiniMaxH3ReferenceToVideo.audio_vae` is required even with no audio reference. Classification: `INTEGRATION_FAIL / PRE-INFERENCE`; zero quality evidence.
- Runner48 added only the official schema-required audio VAE and completed the unchanged H0.

Minimal Base Ref2VA payload:

- `minimax_h3_ref2va_pruned_int8_convrot.safetensors` ~21GB;
- `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` ~15.7GB;
- `minimax_h3_video_vae_fp16.safetensors` ~5.21GB;
- `minimax_h3_audio_vae_fp32.safetensors` ~605MB.

Base active payload ~42.5GB.

## H3 H0 / Runner48 — COMPLETE / PASS_CANDIDATE

Exact completed baseline:

- Base Ref2VA;
- Picture1 = canonical Exilada master;
- Video1 = same raw comparison driver, timestamp-resampled only;
- `448×800`;
-124f @24fps;
- `ref_image_size=match`;
-50 steps;
- `res_multistep/beta`;
- seed0;
- no spatial driver transforms;
- no Turbo/FL2VA/style embedding.

Evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s` (~75m05s);
- output `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`.

Visual verdict: **PASS_CANDIDATE / family advances.** Stable body topology, coherent hair/cloth motion, no destructive whole-body smear. Chain detail still drifts somewhat. Late right-foot crop follows the source/driver envelope and is not treated as anatomy collapse.

`448×800` passes as a motion-master generation size.

## Production-speed correction

H0 proves quality but ~75 minutes per ordinary action is not an acceptable production iteration loop.

Important temporal correction: do **not** assume H3 should simply generate only 8–12 frames. The current node uses the H3 `17k+5` temporal grid and documents the trained video range at approximately `124–362` frames @24fps.

Production strategy therefore becomes:

`fast 124-frame H3 motion master -> select/distill roughly 12 game frames -> pixel-art reconstruction`

Shorter-than-trained H3 windows may be tested later only as an explicit optimization.

## CURRENT GATE — H0T / Runner49

Before spending another long inference on a new walking driver, benchmark the official Ref2V Turbo4 path against the exact completed H0 inputs.

New tooling:

- `tools/minimax-h3-spike/run_h0t_ref2va_turbo4.py`
- `tools/structured-2d-character-pipeline/49_run_minimax_h3_ref2va_h0t_turbo4.ps1`

Runner49 adds only the official Turbo hypothesis:

- `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` ~1.96GB;
- SHA256 `5b9ab5ade15d0775676d01a907268a69a1468dc6033b3b0d3ded5502f3ebb84c`;
- LoRA strength1.0;
-4 steps;
- `res_multistep/simple` according to the official workflow's Lightning/Turbo switch.

Unchanged from H0:

- Picture1/Video1;
-448×800;
-124f@24fps;
- `ref_image_size=match`;
- seed0;
- same prompt.

H0T must materially reduce wall clock **without** sacrificing H0-level topology/identity/motion quality.

Exact operator command:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\49_run_minimax_h3_ref2va_h0t_turbo4.ps1"
```

Expected evidence:

- `Z:\AI\MiniMaxH3\h0t_exilada_ref2va_448x800_124f_turbo4.mp4`
- `Z:\AI\MiniMaxH3\h0t_run_manifest.json`
- `Z:\AI\MiniMaxH3\h0t_api_prompt.json`
- `Z:\AI\MiniMaxH3\h0t_executor.log`

## H1-S after throughput decision

If H0T quality passes, use Turbo4 for the first game-relevant walk motion master.

Driver contract:

- fixed camera;
- one adult performer;
- whole body visible throughout;
- screen-left travel;
- mostly lateral/slight3/4 near the locked `72°` facing;
- safe real head/foot/lateral margins;
- one clear gait cycle;
- performer identity/costume/body/hair irrelevant.

A clean gait cycle may be automatically tiled/repeated to fill the proven 124-frame H3 conditioning regime.

## Action distillation / spritesheet target

First walk target:

- 12 unique frames;
- automatically selected across one stable generated gait cycle;
- automatic segmentation including hair/cloth/chains;
- stable ground/pivot alignment while preserving valid body bob;
- transparent high-resolution action strip before final rendering.

Final pixel-art review sheet target:

- visible protagonist ~128px tall;
- cell `192×192`;
- grid `4×3`;
- sheet `768×576`;
- transparent complete-character RGBA;
- optional trimmed atlas + JSON pivots/durations.

The final pixel-art reconstruction stage is **not yet proven** and is the next art-production problem after a practical H3 motion-master throughput path is locked.

## Cleanup

- keep the minimal Base Ref2VA set;
- Runner49 adds only one ~1.96GB official Turbo4 LoRA tied to the explicit speed hypothesis;
- do not add FL2VA/style/alternate quantizations without evidence;
- Wan large checkpoints may be removed while preserving W1H/W1L results;
- keep SSD comparison evidence until explicit abandonment/final verdict.
