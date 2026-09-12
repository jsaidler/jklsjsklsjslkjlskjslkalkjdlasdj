# Runner72 — PowerPaint / BrushNet runtime compatibility

Status date: **2026-09-12**

Status: **AUTOMATED COMPATIBILITY RETRY PREPARED / SCALED_FP8 FIX ADDED**

Canonical parent gate: `docs/RUNNER72_POWERPAINT_OBJECT_REMOVAL_2026-09-12.md`.

## User-operation invariant

The user does **not** apply manual patches to runtime dependencies or custom nodes. Any compatibility change required by the Asset Studio must be repository-owned, reproducible, automatically applied, verified, idempotent, and fail-closed.

## Evidence accumulated before the current retry

Runner72 already proved:

- portable Torch + process-local Diffusers/Accelerate/PEFT overlay: PASS;
- PowerPaint payload download + SHA validation: PASS;
- ComfyUI-BrushNet custom-node loading: PASS;
- Windows dropdown path mismatch: fixed by runtime `object_info` resolution;
- PowerPaint CLIP diagnostic: `200` current keys, `200` learned keys, `199` common keys, `0` shape mismatches;
- learned task-token tensors `P_ctxt`, `P_shape`, `P_obj`: all compatible at `[10,768]`;
- the same `add_tokens + load_state_dict(strict=False)` path succeeds when run by itself in the diagnostic process;
- `assign=True` compatibility load allowed the full Runner72 process to progress beyond the PowerPaint CLIP loader.

No visual/model-quality verdict exists yet. Every failure so far is runtime/custom-node integration.

## Compatibility layer

Project-owned patcher:

`tools/roguelite-asset-studio/apply_powerpaint_clip_loader_compat.py`

Wrapper:

`tools/structured-2d-character-pipeline/72_run_powerpaint_object_removal_compat.ps1`

The wrapper verifies the pinned `ComfyUI-BrushNet` commit, runs the guarded patcher, then launches the canonical Runner72. The user never edits runtime files manually.

### 1. PowerPaint CLIP load

The exact learned state is shape-compatible with the current ComfyUI CLIP, but ordinary copy-based `load_state_dict` failed in the full graph after the larger BrushNet stack was already resident.

The compatibility layer changes only the pinned upstream load from:

`load_state_dict(..., strict=False)`

to:

`load_state_dict(..., strict=False, assign=True)`

This avoids a second full parameter copy while preserving the already-proven tensor shapes/task embeddings.

### 2. `pick_operations(... scaled_fp8=...)` incompatibility

After the CLIP compatibility load succeeded, Runner72 reached the PowerPaint `model_update` path and failed at:

`TypeError: pick_operations() got an unexpected keyword argument 'scaled_fp8'`

The pinned `ComfyUI-BrushNet` commit calls:

`comfy.ops.pick_operations(... fp8_optimizations=fp8, scaled_fp8=...)`

while the shared pinned ComfyUI runtime used by the already-proven Asset Studio backends does not accept the `scaled_fp8` keyword.

This exact error is also a known ComfyUI-BrushNet compatibility failure reported upstream.

The project patch does **not** blindly remove the feature. It preserves upstream behavior first:

1. call `pick_operations` with `scaled_fp8`;
2. only if the exact `unexpected keyword argument 'scaled_fp8'` `TypeError` occurs, retry the same call without `scaled_fp8`;
3. any other `TypeError` propagates normally.

This keeps the patch compatible with runtimes that do support scaled FP8 while allowing the pinned shared ComfyUI runtime to proceed.

### 3. sampler-wrapper kwargs compatibility

The same upstream compatibility report identifies a companion failure where ComfyUI may pass additional sampler kwargs that the pinned BrushNet wrapper does not accept/forward.

The project patch therefore makes:

`brushNet_out_sample_wrapper(..., seed=None)`

accept:

`brushNet_out_sample_wrapper(..., seed=None, **kwargs)`

and forwards those kwargs to the wrapped executor. This is behavior-preserving when no extra kwargs exist and avoids another known API-shape incompatibility.

## Safety properties

The patcher is:

- pinned-commit guarded by the wrapper;
- exact-source guarded;
- idempotent through explicit markers;
- fail-closed on upstream drift;
- automatically applied;
- limited to the Runner72 custom-node checkout;
- does not alter the Qwen site-packages or the shared ComfyUI source;
- does not change model payloads or prompts;
- does not require any new download.

## Decision

The next valid Runner72 attempt must use the compatibility wrapper.

If another runtime incompatibility appears, preserve the exact failure and revise this automated layer. Do not ask the user to patch runtime files manually and do not classify PowerPaint visually until the four inference jobs actually complete.
