# MiniMax H3 Ref2VA local production tooling

Status: **ACTIVE — H0 is PASS_CANDIDATE as motion master. Runner49/H0T Turbo4 is the current throughput-quality gate. H1-S walk follows only after the speed path is accepted. Final runtime art is separate high-quality pixel-art reconstruction.**

Canonical H3 procedure: `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`.

H1-S production definition: `docs/H1S_MINIMAX_H3_SPRITESHEET_PRODUCTION_PASS_2026-09-08.md`.

## Paths

- project: `D:\GOOGLE DRIVE\DEV\Roguelite`
- H3 workspace: `Z:\AI\MiniMaxH3`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- `D:\AI` stale/invalid.

## H0 completed quality baseline

Base Ref2VA:

-448×800;
-124f @24fps;
-50 steps;
- `res_multistep/beta`;
- seed0;
- `ref_image_size=match`;
- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s`;
- output `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`.

Verdict: **PASS_CANDIDATE**. H3 is a strong complete-character motion-master candidate.

## Final-art boundary

H3 output is not the final runtime pixel art.

Current production chain:

`pixel-art Exilada reference + real driver -> H3 motion master -> automatic action/cycle distillation -> segmentation/alignment -> high-quality pixel-art reconstruction -> transparent spritesheet/atlas`

The old tiny whole-frame proxy is historical QA only.

## Temporal rule

Do not default to generating only8–12 H3 frames. Current H3 uses the `17k+5` temporal grid and documents its trained range around124–362 frames @24fps.

Generate a fast124-frame master, then distill ~12 runtime frames.

## Tool files

### `prepare_h0_driver.py`

Builds the comparison driver at24fps/124f without spatial transforms.

### `run_h0_ref2va.py`

Historical Base50 H0 executor.

### `run_h0_ref2va_audio_vae_required.py`

Runner48 integration wrapper adding the schema-required audio VAE.

### `run_h0t_ref2va_turbo4.py`

Runner49 throughput executor. Uses exact H0 inputs but applies the official Ref2V Turbo4 LoRA at strength1.0,4 steps and `res_multistep/simple`.

Writes:

- `h0t_exilada_ref2va_448x800_124f_turbo4.mp4`;
- `h0t_run_manifest.json`;
- `h0t_api_prompt.json`.

The manifest records wall-clock speedup versus completed H0.

## Runner49

Runner:

`tools/structured-2d-character-pipeline/49_run_minimax_h3_ref2va_h0t_turbo4.ps1`

It downloads/verifies only:

- `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors`;
- ~1.96GB;
- SHA256 `5b9ab5ade15d0775676d01a907268a69a1468dc6033b3b0d3ded5502f3ebb84c`.

Exact command:

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\49_run_minimax_h3_ref2va_h0t_turbo4.ps1"
```

If `H3-H0T: prompt_id=...` appears, real Turbo inference started.

## H0T pass criterion

Speed alone is insufficient. Compare H0T directly with H0 for:

- complete body topology;
- identity/body/hair/costume coherence;
- motion adherence;
- hair/cloth/restraint secondary motion;
- destructive blur/ghosting.

Use Turbo for H1-S only if quality remains acceptable.

## H1-S after H0T

Game-relevant walk driver: fixed camera, full-body screen-left, mostly lateral/slight3/4 near72°, safe real margins and one clean gait cycle.

Keep the proven124-frame temporal regime; a clean gait cycle may be tiled/repeated through the reference interval.

Distill one stable generated cycle to ~12 unique runtime frames, then run the separate pixel-art reconstruction gate.

## Runtime target

First walk:

- ~128px visible character;
-12 unique frames;
-192×192 cells;
-4×3 review sheet =768×576;
- transparent RGBA;
- optional trimmed atlas + JSON pivots/durations.

## Cleanup

Keep Base H3 files plus the single explicit Turbo4 LoRA while evaluating throughput. Do not accumulate FL2VA/style/alternate quantizations without a specific hypothesis. Wan large weights may be removed while proof/results remain.
