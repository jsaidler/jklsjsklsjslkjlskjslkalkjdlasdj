# Runner71 — Big-LaMa automatic-mask object-removal gate

Status date: **2026-09-11**

Status: **PREPARED / CURRENT DEDICATED REMOVAL GATE**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner71 exists

Runner70 exhausted SDXL Inpainting 0.1 fairly. Running the same accepted automatic masks through the model at its 1024x1024 training regime did not produce the required structural operations.

Runner70 actual result:

### Plank

- model input `1024x1024` from an exact source-authoritative `512x512` context;
- elapsed `34.071 s`;
- inside-allowed changed ratio >Delta12 `0.316580`;
- outside-allowed changed ratio >Delta12 `0.0`;
- visual: the plank remained present; the region was retextured/deformed rather than becoming an opening.

### Strap

- model input `1024x1024` from an exact source-authoritative `512x512` context;
- elapsed `26.069 s`;
- inside-allowed changed ratio >Delta12 `0.165934`;
- outside-allowed changed ratio >Delta12 `0.0`;
- visual: the strap remained structurally continuous; no clean middle break exposing matching wood was produced.

Runner70 classification:

**TECHNICAL PASS / 1024 TRAINING-RESOLUTION PARITY PASS / OUTSIDE-REGION CONTAINMENT PASS / VISUAL OPERATION FAIL / SDXL INPAINTING HYPOTHESIS EXHAUSTED.**

The SDXL payload is therefore retired and Runner71 removes it only after confirming Runner69/70 evidence exists.

## New editor hypothesis

Runner71 changes only the regional removal backend.

Editor:

**Big-LaMa** — resolution-robust large-mask inpainting with Fourier convolutions.

Why this is a rational next specialist:

- it is specifically designed for object removal/inpainting rather than general semantic editing;
- it does not need a text prompt, eliminating another source of interpretation error;
- the accepted Runner66 masks already define exactly what must be removed;
- it is extremely lightweight compared with the previous diffusion backends;
- it is resolution-robust and can operate directly on the exact source-coordinate context;
- LaMa lineage is Apache-2.0.

The upstream project used by the gate is `enesmsahin/simple-lama-inpainting`, which loads the released Big-LaMa TorchScript model directly.

## Security/provenance note

TorchScript artifacts are executable/pickle-bearing. Runner71 therefore does **not** load an arbitrary `big-lama.pt`.

Pinned artifact:

- source: `https://github.com/enesmsahin/simple-lama-inpainting/releases/download/v0.1.0/big-lama.pt`
- bytes: `206134115`
- SHA256: `344c77bbcb158f17dd143070d1e789f38a66c04202311ae3a258ef66667a9ea9`

The runner refuses to execute a file with a different size or hash.

## Cleanup before the new gate

Preserve:

- Runner69 outputs/manifest/contact sheet;
- Runner70 outputs/manifest/contact sheet.

Then remove the retired SDXL payload, but only if the local file hashes exactly match the pinned artifacts:

- `sdxl_inpaint_0.1_fp16.safetensors`;
- `sd_xl_base_1.0.safetensors`.

This recovers approximately 12.1 GB before the ~196 MiB Big-LaMa download.

## Automatic control contract — unchanged

Runner71 keeps the accepted precision stack:

`semantic request -> hierarchy/perception -> SAM2/repeated-member decomposition -> Runner66 operation mask -> specialist removal backend -> deterministic full-resolution composite`.

No manual box or mask is introduced.

### Plank

- target: Runner66 exact one-plank mask;
- operation: remove the whole atomic board;
- desired fill: plausible narrow opening/background continuation;
- neighboring planks/hardware remain source-authoritative outside the allowed neighborhood.

### Strap

- target: Runner66 retained lower-right strap mask;
- operation: remove the central 40% only;
- desired fill: plausible underlying aged door/wood;
- outside strap ends survive.

## Cheap boundary matrix

Because LaMa is inexpensive, Runner71 does not jump models after one arbitrary mask edge setting. It tests two deterministic boundary variants for each operation:

- `tight`: small dilation around the semantic operation;
- `expanded`: larger but still local dilation to give the object-removal network more boundary context.

Four inference jobs total:

- plank/tight;
- plank/expanded;
- strap/tight;
- strap/expanded.

The semantic target itself never changes.

## Runtime

No ComfyUI server is used.

Runner71 reuses the already-installed embedded Python/PyTorch runtime under:

`Z:\AI\QwenImageEdit\ComfyUI_windows_portable\python_embeded\python.exe`

The model is loaded directly with pinned `torch.jit.load` and runs on CUDA when available.

Workspace:

`Z:\AI\LaMaInpaint`

Output root:

`Z:\AI\LaMaInpaint\runner71_object_removal_gate`

## Implementation

Adapter:

`tools/roguelite-asset-studio/lama_inpaint_adapter.py`

Executor:

`tools/roguelite-asset-studio/lama_object_removal_gate.py`

Runner:

`tools/structured-2d-character-pipeline/71_bootstrap_and_run_big_lama_object_removal.ps1`

## PASS criteria

Technical PASS:

- Runner66 and Runner70 evidence validate;
- retired SDXL payload is removed only by exact hash;
- Big-LaMa download size/hash validate;
- TorchScript loads on the local runtime;
- all four jobs complete;
- outputs/contact sheet/manifest are written;
- no manual mask/box and no ComfyUI server is used.

Visual PASS requires at least one mask variant per task.

### Plank

- exactly the atomic plank is absent;
- its region reads as an actual opening/background continuation;
- LaMa must not simply reconstruct another wooden board across the gap;
- neighboring components remain coherent.

### Strap

- central strap section is absent;
- the fill reads as underlying aged door/wood rather than a replacement metal bar;
- both outside strap ends remain.

### Preservation

The deterministic final composite must continue to keep unrelated source geometry authoritative.

## Decision after Runner71

If both tasks pass in at least one variant, promote Big-LaMa as the lightweight `automatic_region_object_removal` specialist. Keep prompt-driven semantic fill as a separate routing problem rather than forcing one backend to do both.

If LaMa preserves/reconstructs the removed object instead of producing a useful fill, retain the accepted perception/mask/compositor stack and test the next dedicated mask-native backend. Do not regress to manual masks or global prompt-only editing.