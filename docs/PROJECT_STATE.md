# Roguelite — Current Project State

Status date: **2026-09-08**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`
3. `docs/FLUX_KONTEXT_PIXELART_LOCAL_SPIKE_2026-09-08.md`
4. `docs/RUNNER50_POWERSHELL_PARSE_FAIL_2026-09-08.md`
5. `docs/RUNNER50_CLIP_L_SHA256_PREFLIGHT_FAIL_2026-09-08.md`
6. `docs/VISUAL_DIRECTION.md`
7. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
8. `docs/ANIMATION_PIPELINE.md`
9. `docs/CHARACTER_PRODUCTION_PIPELINE.md`
10. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`
11. `docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`
12. `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`
13. `docs/CHARACTERS.md`
14. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing action updates the thematic docs, this file and the active handoff before completion is reported.

## Local paths — LOCKED

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- active MiniMax H3 workspace: `Z:\AI\MiniMaxH3`
- active FLUX Kontext renderer workspace: `Z:\AI\FluxKontext`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` is stale/historical.

## Game/runtime presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic-like gameplay camera;
- native raster `640×360`;
- pitch `26°`;
- protagonist about `128px` tall at baseline scale;
- first locomotion family screen-left / mostly lateral-three-quarter;
- current facing baseline `72°`;
- runtime consumes complete precomposed character sprites only.

No visible runtime body/hair/clothing/equipment layer assembly.

## Final visible-art target — LOCKED

Final runtime character graphics are **deliberate high-quality pixel art**.

H3/Wan painterly/raster video is an intermediate **motion master**, not the final runtime art. Simple downscale/nearest-neighbor/palette reduction is not accepted as the final rendering method.

Canonical production chain:

`character reference -> real action driver -> H3 complete-character motion master -> automatic action-frame distillation -> automatic alpha/pivot/alignment -> high-quality pixel-art reconstruction -> transparent complete-character spritesheet/atlas + metadata -> runtime`

The 1980s sword-and-sorcery lineage remains active: Heavy Metal, Conan, Red Sonja, Frank Frazetta and Julie Bell. Adult sensuality/nudity remains legitimate.

## All-local authoring target — LOCKED 2026-09-08

The project targets a **single local authoring workflow/interface** that can:

1. accept an existing character reference image **or** generate a local reference from a text description;
2. accept a numeric relative world scale for humans, creatures, monsters and bosses;
3. accept a real action reference video;
4. accept an action-type preset such as walk, jump, punch, kick, weapon attack, defense, hit, death, taunt/dance/gesture or custom;
5. run local motion generation, extraction, pixel-art reconstruction and packaging;
6. return the final spritesheet, preview, frames and metadata.

Canonical UI/workflow specification:

`docs/LOCAL_SPRITESHEET_AUTHORING_WORKFLOW.md`

Gradio is the current V1 UI scaffold choice **after the renderer stage is proven**.

## Relative character scale — CURRENT CONTRACT

`relative_scale=1.0` represents the baseline adult-human/Exilada scale, approximately `128px` visible height in the canonical gameplay composition.

Relative scale is explicit world/render metadata, not non-uniform image stretching. It influences target sprite height, cell/atlas dimensions and source-resolution policy for large creatures. Exact min/max range is still open.

## Motion model — MiniMax H3 Ref2VA ACTIVE

MiniMax H3 remains the selected motion-master family after H0.

H0 exact quality baseline:

- Base Ref2VA;
- Picture1 = canonical Exilada master;
- Video1 = raw comparison driver, timestamp-resampled only;
- `448×800`;
- `124f @24fps`;
- `ref_image_size=match`;
- `50 steps`;
- `res_multistep/beta`;
- seed `0`;
- no Turbo/FL2VA/style embedding;
- schema-required audio VAE wired, with no audio reference/decode in the current job.

Evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s` (~75m05s);
- output `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`.

Visual verdict: **PASS_CANDIDATE / preferred motion-master quality baseline.** Stable body topology, coherent hair/cloth motion and no destructive whole-body smear. Chain detail still drifts somewhat. Late right-foot crop follows the driver/source envelope.

`448×800` passes as the current motion-master generation size.

## Turbo4 / Runner49 — REJECTED FOR PRODUCTION QUALITY

The official Ref2V Turbo4 / 4-step experiment was run and visually rejected by the user.

The user explicitly prefers the original H0 Base50 result and requested returning to that configuration.

Therefore:

- Turbo4 is **not** the current gate;
- Turbo4 is **not** the default production path;
- Base50 is restored as canonical;
- do not invent Turbo4 elapsed time/prompt id/hash unless recovered from local evidence.

Record:

`docs/H3_H0T_TURBO4_QUALITY_REJECT_2026-09-08.md`

The Turbo LoRA may be removed after local output/log/manifest evidence is preserved.

## Temporal rule

Do not assume normal H3 production should generate only 8–12 frames.

The current H3 path is proven at `124f@24fps`. The normal pipeline therefore remains:

`124-frame Base50 motion master -> automatic action/cycle distillation -> compact final action set -> pixel-art reconstruction`

Final frame count is action-dependent, typically in the 8–16 range for first tests.

## Current-video spritesheet proof

The existing H0 video is a dance/gesture-like action, **not a walk**.

It has already been used to prove basic local frame extraction and raster spritesheet packing. Those sheets are diagnostic intermediates only; they are not final pixel art.

This same existing H0 video is the current input for the downstream pixel-art renderer proof because it avoids another ~75-minute H3 generation while testing the rest of the pipeline.

## Final pixel-art renderer — FLUX.1 Kontext [dev] ACTIVE SPIKE

**FLUX.1 Kontext [dev]** is the preferred first local model to validate for the final pixel-art reconstruction stage.

Canonical renderer spike:

`docs/FLUX_KONTEXT_PIXELART_LOCAL_SPIKE_2026-09-08.md`

Runner:

`tools/structured-2d-character-pipeline/50_run_flux_kontext_h0_dance12_pixelart_proof.ps1`

Executor:

`tools/flux-kontext-spike/run_h0_dance12_pixelart_proof.py`

### Runner50 parser incident — FIXED / ZERO MODEL EVIDENCE

The first local invocation of Runner50 failed in the PowerShell parser before any model download, ComfyUI launch or Kontext inference. Classification: **INTEGRATION FAIL / PRE-INFERENCE**.

Cause: PowerShell parsed `$Label:` as an invalid scoped/drive-style variable reference in two interpolated status strings.

Repair commit `300f39179ceb01d5689f6c5ba7cc52ca2aaf38d2` changed those occurrences to `${Label}:` only. No model/settings/workflow variable changed.

Incident record:

`docs/RUNNER50_POWERSHELL_PARSE_FAIL_2026-09-08.md`

### Separate local workspace

`Z:\AI\FluxKontext`

Runner50 clones only the already-proven pinned ComfyUI v0.34.0 runtime from the H3 portable installation while excluding H3 models/input/output/user data. The renderer therefore remains isolated without introducing another ComfyUI version.

Kontext server port: `8191`.

### First model payload — quality-first practical 12GB-VRAM set

- `flux1-dev-kontext_fp8_scaled.safetensors` ~11.9GB, SHA256 `630ba795ec64283b4230ea23cf79406c2c68b7c578229ed139f30043eadb30a2`;
- `clip_l.safetensors` ~246MB, SHA256 `660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c0c8576cd796491d9a6cdd`;
- `t5xxl_fp16.safetensors` ~9.79GB, SHA256 `6e480b09fae049a72d2a8c5fbccb8d3e92febeb233bbe9dfe7256958a9167635`;
- `ae.safetensors` ~335MB, SHA256 `afc8e28272cd15db3919bacdb6918ce9c1ed22e96cb12c4d5ed0fba823529e38`.

Total first renderer payload: about **22.3GB**.

The native FP8-scaled diffusion is the first practical official ComfyUI route for RTX 3060 12GB. T5 remains FP16 because the machine has 48GB system RAM and the project is quality-first. If completed evidence specifically implicates FP8 diffusion quality, full BF16 Kontext is the next controlled branch. GGUF/custom nodes are not installed before the native route is tested.

### Runner50 CLIP-L hash preflight incident — FIXED / ZERO MODEL EVIDENCE

The next Runner50 attempt successfully downloaded and verified the ~11.9GB Kontext diffusion model, then downloaded `clip_l.safetensors`, but failed before inference because the repository contained the wrong expected CLIP-L SHA256.

Observed downloaded SHA256:

`660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c0c8576cd796491d9a6cdd`

Independent Hugging Face metadata confirms this is the correct hash for the standard 246MB FLUX CLIP-L file. The previous repository value omitted one `c0` sequence. Because the runner believed the valid download was corrupt, it deleted that CLIP-L file.

Classification: **INTEGRATION FAIL / PRE-INFERENCE / zero Kontext quality evidence**.

Repairs:

- PowerShell Runner50 expected hash corrected;
- Python executor expected hash corrected;
- remaining first-spike hashes independently rechecked before resume;
- already verified Kontext FP8 diffusion preserved and reusable;
- only CLIP-L must be downloaded again due to the false mismatch deletion.

Incident record:

`docs/RUNNER50_CLIP_L_SHA256_PREFLIGHT_FAIL_2026-09-08.md`

### Runner50 first proof contract

No new H3 inference.

Runner50 uses the existing H0 and deterministically selects frames:

`1, 12, 23, 35, 46, 57, 68, 79, 90, 102, 113, 124`

It automatically creates a square `1024×1024` action sheet with a centered `4×3` `256×256` grid, conditions Kontext on both the action sheet and canonical Exilada reference, runs a 20-step native Kontext edit, then outputs:

- full reconstructed square;
- working 4×3 grid;
- `768×576` `4×3` review sheet with `192×192` cells;
- automatic RGBA attempt;
- individual RGBA frames;
- GIF preview;
- manifest/prompt/log.

This deterministic frame selection tests the renderer only. Semantic cycle/action distillation remains a later stage.

### Renderer pass boundary

A successful API run is not enough. PASS requires:

- all 12 poses materially preserved;
- coherent Exilada identity/design;
- deliberate high-quality pixel-art reading;
- no destructive pose/topology rewrite;
- hair/cloth/restraint masses retained;
- usable gameplay-scale review;
- automatic alpha good enough to avoid routine manual masks.

### License caveat

The open-weight FLUX.1 Kontext [dev] release is non-commercial. It is acceptable for local technical validation, but commercial game shipping requires appropriate BFL commercial licensing or a renderer with compatible commercial terms.

SDXL/img2img remains a fallback if Kontext fails quality, hardware or licensing requirements.

## Character-reference generation from text — OPEN MODEL CHOICE

The interface must support local text-to-reference generation, but the exact model is **not yet locked**.

Current candidate families include SDXL-class and FLUX text-to-image models. Kontext [dev] is not being made the mandatory text-to-image generator because its intended open-weight role here is editing/reconstruction.

## Model-screening order

1. **MiniMax H3 Ref2VA — ACTIVE / Base50 quality baseline locked for motion masters.**
2. **FLUX.1 Kontext [dev] — ACTIVE renderer spike / Runner50 preflight hashes repaired, inference not yet evidenced.**
3. Wan-Animate-2 — paused after W1L, not exhausted.
4. SCAIL-2 — later only if H3 fails a future motion-production gate.

## Immediate implementation order

1. rerun **Runner50** after pulling the CLIP-L hash repair;
2. inspect the first H0 dance12 Kontext pixel-art sheet;
3. classify renderer result separately for layout/pose, identity, pixel-art quality, alpha and gameplay-scale readability;
4. if FP8-scaled Kontext is structurally good but visibly under-resolved, test full BF16 Kontext as the next controlled variable;
5. once the renderer passes, build the local Gradio orchestration UI around the proven H3 Base50 + Kontext stages;
6. then implement semantic action presets/distillation, text-reference generation and relative-scale creature cases;
7. only after downstream production is proven spend another Base50 H3 hour on a new action family.

## Cleanup

- keep the minimal Base H3 Ref2VA set;
- Turbo4 LoRA is no longer an active dependency and may be deleted after preserving local evidence;
- keep only the single active Kontext variant until evidence justifies BF16 or another renderer;
- do not add Kontext GGUF/custom-node variants before the native FP8-scaled route is judged;
- Wan large checkpoints may be removed while W1H/W1L evidence remains;
- keep SSD comparison evidence until explicit abandonment/final verdict.
