# Next-chat handoff — G3S complete-character spritesheet production

Status date: **2026-09-08**

GitHub living docs are canonical.

## Paths

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- active H3: `Z:\AI\MiniMaxH3`
- paused Wan: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` invalid/stale.

## Read first

- `docs/PROJECT_STATE.md`
- `docs/VISUAL_DIRECTION.md`
- `docs/H1S_MINIMAX_H3_SPRITESHEET_PRODUCTION_PASS_2026-09-08.md`
- `docs/ANIMATION_PIPELINE.md`
- `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`

## Production contract — CURRENT

Final runtime pipeline is now explicitly:

`pixel-art Exilada reference + arbitrary real driver -> H3 complete-character motion master -> automatic action/cycle distillation -> automatic segmentation/alignment -> high-quality pixel-art reconstruction -> transparent complete-character spritesheet/atlas + metadata -> runtime playback`

No routine manual rigging/keyframing/mask repair/per-frame repainting/hand compositing.

## Final visible-art clarification — LOCKED 2026-09-08

Final runtime characters return to **deliberate high-quality pixel art**.

The H3/Wan painterly result is not discarded; it is reclassified as an intermediate motion/pictorial master. The tiny H0 whole-frame proxy is not a final-art path.

Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell and the mature 1980s sword-and-sorcery direction remain active.

## Wan — PAUSED

W1H is the best documented Wan geometry baseline. W1L completed ref1.0 + pose0.80 +30 steps. Preserve W1H/W1L videos/prompts/manifests/logs. H3 has progressed far enough that Wan large checkpoints may be cleaned when convenient.

## H3 H0 / Runner48 — COMPLETE / PASS_CANDIDATE

Base H0:

- Picture1 = canonical Exilada;
- Video1 = raw comparison driver, timestamp-resampled only;
-448×800;
-124f@24fps;
- `ref_image_size=match`;
-50 steps;
- `res_multistep/beta`;
- seed0;
- no Turbo/FL2VA/style embedding.

Evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s` (~75m05s);
- video `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`.

Visual verdict: **PASS_CANDIDATE / H3 family advances as motion-master candidate.** Stable body topology, coherent hair/cloth response and no destructive global smear. Chains still drift somewhat. Late foot crop follows driver/source envelope.

`448×800` passes for motion-master generation.

## Important temporal correction

Do **not** default to asking H3 for only8–12 generated frames.

Current H3 uses the `17k+5` temporal grid and documents the trained video range at approximately124–362 frames @24fps. Preserve the proven124-frame regime for now.

Production strategy:

`fast124-frame H3 master -> select/distill ~12 useful game frames -> pixel-art reconstruction`

Shorter H3 windows are a later optimization only.

## CURRENT GATE — Runner49 / H0T Turbo4

Do this **before** spending another long inference on a walking driver.

Runner49 benchmarks the official Ref2V Turbo4 route against the exact H0 inputs.

Only added model:

- `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors`;
- ~1.96GB;
- SHA256 `5b9ab5ade15d0775676d01a907268a69a1468dc6033b3b0d3ded5502f3ebb84c`.

Turbo configuration:

- LoRA strength1.0;
-4 steps;
- `res_multistep/simple`;
- same Picture1/Video1;
- same448×800;
- same124f@24fps;
- same `ref_image_size=match`;
- same seed0 and prompt.

Exact command:

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

If `H3-H0T: prompt_id=...` appears, real Turbo inference started.

Pass requires both substantial speed improvement and H0-level topology/identity/motion quality.

## H1-S after Runner49 decision

If Turbo4 passes, use it for the first actual game walk motion master.

Driver requirements:

- fixed camera;
- one adult full-body performer;
- screen-left travel;
- mostly lateral/slight3/4 near locked `72°`;
- safe head/feet/lateral margins;
- one clear gait cycle;
- performer identity/costume/body/hair irrelevant.

A clean gait cycle may be automatically repeated/tiled to fill the proven124-frame conditioning interval.

The generated124-frame H3 result is a **motion master**, not a124-frame runtime animation.

## Action distillation target

First walk runtime target:

-12 unique frames across one stable generated gait cycle;
- automatic cycle detection/phase selection;
- automatic segmentation including hair/cloth/chains;
- stable ground/pivot alignment;
- high-resolution transparent action strip;
- no manual frame cleanup.

## Final pixel-art target

Separate renderer gate after motion/action extraction:

- canonical Exilada pixel-art reference + selected action strip;
- deliberate high-quality pixel art, not a blurry miniaturized H3 frame;
- visible protagonist ~128px;
- initial cell192×192;
-4×3 / 12-frame review sheet =768×576;
- optional trimmed runtime atlas + JSON pivots/durations.

The exact final pixel-art renderer is **not yet proven**. Do not pretend H3 itself solved that stage.

## Cleanup

- keep Base H3 files and the single explicit Turbo4 LoRA while testing throughput;
- do not accumulate FL2VA/style/alternate quantizations;
- Wan large weights may be removed while proof/results remain;
- keep SSD comparison evidence until explicit abandonment/final verdict.
