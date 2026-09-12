# Runner72 — PowerPaint CLIP runtime compatibility

Status date: **2026-09-12**

Status: **AUTOMATED COMPATIBILITY RETRY PREPARED**

Canonical parent gate: `docs/RUNNER72_POWERPAINT_OBJECT_REMOVAL_2026-09-12.md`.

## User-operation invariant

The user does **not** apply manual patches to runtime dependencies or custom nodes. Any compatibility change required by the Asset Studio must be repository-owned, reproducible, automatically applied, verified, and fail-closed.

## Evidence before this compatibility retry

Runner72 already proved:

- portable Torch + process-local Diffusers/Accelerate/PEFT overlay: PASS;
- PowerPaint payload download + SHA validation: PASS;
- ComfyUI-BrushNet custom-node loading: PASS;
- Windows dropdown path mismatch: fixed by runtime `object_info` resolution;
- PowerPaint CLIP diagnostic: `200` current keys, `200` learned keys, `199` common keys, `0` shape mismatches;
- learned task-token tensors `P_ctxt`, `P_shape`, `P_obj`: all compatible at `[10,768]`;
- the same `add_tokens + load_state_dict(strict=False)` path succeeds when run by itself in the diagnostic process.

The full Runner72 workflow still terminates inside `pp_text_encoder.load_state_dict(...)` after the larger PowerPaint/BrushNet stack is already resident. This is therefore treated as a runtime integration/memory-copy failure, not a model-quality verdict.

## Automated compatibility strategy

Project-owned patcher:

`tools/roguelite-asset-studio/apply_powerpaint_clip_loader_compat.py`

It only modifies the pinned upstream source when the exact expected line is present. It replaces the ordinary copy-based:

`load_state_dict(..., strict=False)`

with:

`load_state_dict(..., strict=False, assign=True)`

so the already-compatible learned tensors are assigned into the module without a second full parameter copy. This is intended to reduce the transient memory/copy pressure that exists in the complete graph but not in the isolated diagnostic.

The patcher is:

- idempotent;
- exact-source guarded;
- fail-closed on upstream drift;
- automatically applied; no user editing is required.

Wrapper:

`tools/structured-2d-character-pipeline/72_run_powerpaint_object_removal_compat.ps1`

The wrapper verifies the pinned `ComfyUI-BrushNet` commit, applies the guarded compatibility patch, and launches the canonical Runner72.

## Decision

The next valid Runner72 attempt must use the compatibility wrapper. If the loader still fails, preserve the exact new failure and revise the automated compatibility layer; do not ask the user to edit `brushnet_nodes.py` manually and do not treat the failure as a PowerPaint visual verdict.
