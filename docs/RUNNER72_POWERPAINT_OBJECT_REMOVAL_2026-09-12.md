# Runner72 — PowerPaint v2.1 / task-conditioned object-removal gate

Status date: **2026-09-12**

Status: **CURRENT SPECIALIST REMOVAL GATE / RUNTIME+PAYLOAD PASS / PROMPT-PATH FIXED / INFERENCE RETRY PENDING**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner72 exists

Runner71 proved that Big-LaMa is technically healthy, extremely fast and fully compatible with the accepted automatic-mask/compositor contract, but it failed the actual visual operation.

Runner71 classification:

**TECHNICAL PASS / VERY FAST / MASK+COMPOSITOR PASS / VISUAL OBJECT-REMOVAL FAIL.**

Actual behavior:

- plank: both tight and expanded variants reconstructed local wooden/door continuity instead of producing a true narrow opening;
- strap: both variants reconstructed/smoothed the local ferrage/door context instead of exposing a clean underlying-wood break;
- all variants preserved unrelated geometry through the deterministic final compositor (`outside_allowed_changed_ratio_gt_12 = 0.0`).

Runner71 therefore closes blind context-completion as the removal specialist for this hard gate. The accepted perception, masks, source contexts and final compositor are not reopened.

## New hypothesis

Runner72 tests **PowerPaint v2.1 / BrushNet** in its explicit `object removal` mode.

This is a materially different hypothesis from Big-LaMa and generic inpainting. PowerPaint learns task tokens for distinct inpainting functions. In the pinned native ComfyUI-BrushNet implementation, `object removal` uses:

- positive learned task conditioning: `P_ctxt`;
- negative learned task conditioning: `P_obj`;
- the user-facing positive conditioning remains available for scene/background intent;
- the user-facing negative conditioning can name the object that must not be reconstructed.

The upstream PowerPaint/ComfyUI-BrushNet guidance recommends `empty scene blur` in the positive prompt for difficult object-removal cases and an object description in the negative prompt.

This directly targets the failure mode seen in Big-LaMa: reconstructing the removed object because local texture continuity is the easiest solution.

## Integration choice

Use the native `nullquant/ComfyUI-BrushNet` implementation rather than the older standalone PowerPaint Diffusers demo.

Pinned custom-node commit:

`505d8ef917ddf3896afd1926770ecc9b099704e2`

Reasons:

- native ComfyUI graph;
- PowerPaint v2 support;
- current implementation uses ComfyUI's model-hook mechanism for improved compatibility;
- no separate legacy Python 3.9 application stack;
- supports `save_memory=max`, important for RTX 3060 12 GB;
- graph semantics are directly inspectable and versionable.

## Portable Python dependency isolation — PREFLIGHT PASS

The first Runner72 bootstrap attempted to create a dedicated `venv --system-site-packages` from the ComfyUI Windows embedded Python. The venv was created, but its interpreter did **not** inherit the portable runtime's Torch installation. The preflight failed exactly at:

`ModuleNotFoundError: No module named 'torch'`

No PowerPaint model payload had been downloaded yet. This was an integration failure, not a PowerPaint/model verdict.

That strategy is retired.

The corrected Runner72 keeps the proven embedded interpreter itself:

`Z:\AI\QwenImageEdit\ComfyUI_windows_portable\python_embeded\python.exe`

and installs only the BrushNet-specific version overrides into:

`Z:\AI\PowerPaint\pydeps`

using `pip --target --no-deps`:

- `diffusers==0.29.2`;
- `accelerate==0.31.0`;
- `peft==0.11.1`.

A project-owned launcher:

`tools/roguelite-asset-studio/python_overlay_launcher.py`

prepends that directory to `sys.path` **inside only the Runner72 process** before executing ComfyUI or the gate executor. This is deliberate: Windows embedded Python may ignore ordinary `PYTHONPATH` behavior through its `_pth` isolation rules.

Consequences:

- Torch continues to come from the already-proven portable runtime;
- Diffusers/Accelerate/PEFT come from the Runner72 overlay first;
- the Qwen portable site-packages are not modified or downgraded;
- the failed `Z:\AI\PowerPaint\venv` is deleted as Runner72-owned transient state;
- the import check still occurs before any multi-GB model download;
- the import probe asserts the exact three pinned overlay versions.

### Actual corrected preflight result

Command:

`tools/structured-2d-character-pipeline/72_preflight_powerpaint_runtime.ps1`

Result on **2026-09-12**:

`RUNNER72-PREFLIGHT: PASS - BASE TORCH + ISOLATED POWERPAINT OVERLAY VERIFIED`

`No PowerPaint model payload was downloaded by this preflight.`

This proves the corrected process-local overlay can simultaneously import:

- the proven base portable Torch runtime;
- `diffusers==0.29.2`;
- `accelerate==0.31.0`;
- `peft==0.11.1`.

## Windows dropdown-path validation failure — FIXED

The first full Runner72 attempt after the runtime preflight successfully progressed through:

- shared ComfyUI startup;
- ComfyUI-BrushNet custom-node loading;
- model payload download + hash validation;
- API readiness;
- first prompt submission.

The prompt was rejected **before inference** because the adapter sent canonical POSIX-style relative model ids:

- `powerpaint/diffusion_pytorch_model.safetensors`;
- `powerpaint/pytorch_model.bin`.

The pinned custom node builds its dropdown values from `get_files_with_extension()`. On Windows, the exact advertised values were:

- `powerpaint\\diffusion_pytorch_model.safetensors`;
- `powerpaint\\pytorch_model.bin`.

ComfyUI validates dropdown strings literally, so equivalent filesystem paths with a different separator were rejected.

This is a harness/platform-path failure, **not a PowerPaint inference or model-quality result**.

Fix committed in:

`tools/roguelite-asset-studio/powerpaint_brushnet_adapter.py`

The adapter now:

1. queries each relevant node's `/object_info` schema;
2. normalizes slash direction only for matching against the canonical Asset Studio model id;
3. stores and submits the **exact runtime-advertised dropdown string**;
4. therefore remains portable across Windows/POSIX separator conventions.

Because this failure occurred after the four large payloads had already been downloaded and validated, the retry must reuse them by hash and proceed directly toward the first valid inference; no multi-GB redownload is expected.

No visual verdict exists yet.

## Model payload

### Stable Diffusion 1.5 base

`v1-5-pruned-emaonly.safetensors`

- bytes: `4265146304`;
- SHA256: `6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa`;
- license: CreativeML OpenRAIL-M.

Used as the SD1.5 MODEL/CLIP/VAE authority required by PowerPaint.

### PowerPaint v2.1 BrushNet

`PowerPaint_Brushnet/diffusion_pytorch_model.safetensors`

- bytes: `3544366408`;
- SHA256: `530f2886ef5bcdf199269ec344155a517639ba64219b85eeb23fd86aab93147f`;
- source: `JunhaoZhuang/PowerPaint-v2-1`;
- license: Apache-2.0.

### PowerPaint learned text encoder

`PowerPaint_Brushnet/pytorch_model.bin`

- bytes: `492401329`;
- SHA256: `73709b4360ca06ef990a67d090e8d81a4310943d67a88845653fc4e9f7f26b65`;
- source: `JunhaoZhuang/PowerPaint-v2-1`;
- license: Apache-2.0 model repository.

### SD1.5 FP16 CLIP encoder

`text_encoder/model.fp16.safetensors`

- bytes: `246144864`;
- SHA256: `77795e2023adcf39bc29a884661950380bd093cf0750a966d473d1718dc9ef4e`.

Total new model payload is approximately **8.55 GB** and is now locally present/validated from the first full attempt.

## Cleanup

Runner71 generated evidence is preserved.

The Big-LaMa model is removed only after:

1. Runner71 manifest reports technical completion;
2. Runner71 contact sheet exists and its SHA256 matches the manifest;
3. local `big-lama.pt` matches the pinned SHA256.

If the first Runner72 preflight already removed Big-LaMa before the venv import failure, the corrected runner treats its absence as the expected already-cleaned state.

PowerPaint files are kept only if the backend proves useful; the project does not accumulate failed checkpoints speculatively.

## Automatic control contract — unchanged

`semantic request -> accepted perception/decomposition -> Runner66 operation mask -> Runner71 tight/expanded boundary variant -> PowerPaint object-removal backend -> deterministic full-resolution composite`

No manual mask, box or per-asset repaint is introduced.

Runner72 intentionally reuses the exact Runner71 `512x512` source contexts and exact tight/expanded masks. This gives a direct backend comparison.

## Test matrix

Four jobs:

- plank / tight;
- plank / expanded;
- strap / tight;
- strap / expanded.

All use:

- `function = object removal`;
- fitting `1.0`;
- BrushNet scale `1.0`;
- start `0`;
- end `10000`;
- `save_memory = max`;
- seed `0`;
- 20 steps;
- CFG `7.5`;
- Euler / normal;
- denoise `1.0`.

### Plank text conditioning

Positive:

`empty scene blur, narrow empty opening through the medieval doorway, neutral background visible through the missing board`

Negative:

`wooden plank, vertical board, replacement wood, extra board, continuous door`

### Strap text conditioning

Positive:

`empty scene blur, aged dark wooden door surface visible where the iron is removed`

Negative:

`iron strap, hinge strap, metal bar, rivets, replacement metal, continuous iron`

These prompts do not localize the edit. Location remains fully mask-authoritative.

## Native graph

The graph mirrors the pinned ComfyUI-BrushNet PowerPaint object-removal example:

1. `CheckpointLoaderSimple` — SD1.5 base;
2. `BrushNetLoader` — PowerPaint v2.1 BrushNet / FP16;
3. `PowerPaintCLIPLoader` — SD1.5 FP16 CLIP + learned PowerPaint text encoder;
4. `LoadImage` source;
5. `LoadImage` mask + `ImageToMask`;
6. base `CLIPTextEncode` positive/negative;
7. `PowerPaint(function=object removal)`;
8. `KSampler`;
9. `VAEDecode`;
10. `SaveImage`.

## Runtime

Shared ComfyUI code commit remains:

`6eba895f7d3615284da81e95bf49eaed4a5f7309`

PowerPaint uses isolated port `8194`.

Workspace:

`Z:\AI\PowerPaint`

Dependency overlay:

`Z:\AI\PowerPaint\pydeps`

Output root:

`Z:\AI\PowerPaint\runner72_object_removal_gate`

## Implementation

Adapter:

`tools/roguelite-asset-studio/powerpaint_brushnet_adapter.py`

Executor:

`tools/roguelite-asset-studio/powerpaint_object_removal_gate.py`

Portable dependency launcher:

`tools/roguelite-asset-studio/python_overlay_launcher.py`

Runtime-only preflight:

`tools/structured-2d-character-pipeline/72_preflight_powerpaint_runtime.ps1`

Runner:

`tools/structured-2d-character-pipeline/72_bootstrap_and_run_powerpaint_object_removal.ps1`

## PASS criteria

Technical PASS requires:

- Runner71 evidence validates;
- rejected Big-LaMa payload is removed only by exact hash, or is already absent after the first verified cleanup;
- shared ComfyUI commit validates;
- ComfyUI-BrushNet is pinned at the exact tested commit;
- base portable interpreter independently imports Torch;
- process-local dependency overlay imports Torch + exact pinned Diffusers/Accelerate/PEFT versions;
- no Qwen site-package downgrade/modification occurs;
- all four model files validate by size + SHA256;
- `BrushNetLoader`, `PowerPaintCLIPLoader` and `PowerPaint` load through ComfyUI;
- model dropdown values are resolved from runtime `object_info` rather than guessed path separators;
- all four jobs complete;
- contact sheet + manifest + deterministic composites are written.

The runtime/import, payload-installation and custom-node-loading portions of this technical gate are already **PASS**. First valid inference remains pending after the Windows dropdown-path fix.

Visual PASS requires at least one boundary variant per task.

### Plank

- one actual atomic plank disappears;
- result reads as a real narrow opening/background continuation;
- no replacement plank/board appears;
- neighboring boards/hardware stay coherent.

### Strap

- central strap section disappears;
- plausible aged wood is visible underneath;
- both external strap ends survive;
- no replacement/continuous metal bar appears.

### Preservation

Unrelated source geometry remains source-authoritative through the deterministic compositor.

## Decision after Runner72

If both hard operations pass, promote PowerPaint as the first task-conditioned `automatic_region_object_removal` specialist and move to semantic multi-reference role separation before Character Lab.

If it fails, preserve the accepted perception/mask/compositor stack and the Runner72 evidence, clean the failed PowerPaint payload, and evaluate the next removal-specific backend. Do not return to global prompt-only editing or manual masks.
