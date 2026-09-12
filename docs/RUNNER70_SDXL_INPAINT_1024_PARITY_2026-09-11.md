# Runner70 — SDXL Inpainting 0.1 / 1024 training-resolution parity gate

Status date: **2026-09-11**

Status: **COMPLETE / TECHNICAL PASS / VISUAL FAIL / SDXL INPAINTING EXHAUSTED**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner70 existed

Runner69 proved that SDXL Inpainting 0.1 was technically healthy and mask-native, but it ran on `256x512` and `384x256` crops even though the model was trained at `1024x1024`. Runner70 therefore changed only model-input geometry before rejecting the backend.

Unchanged:

- SDXL Inpainting 0.1 FP16 UNet;
- SDXL Base 1.0 CLIP/VAE authority;
- Runner66 automatic masks;
- plank full atomic operation;
- strap central-40-percent break operation;
- 30 steps;
- CFG 6.0;
- DPM++ 2M / Karras;
- denoise 1.0;
- seed 0;
- deterministic full-resolution composite;
- no manual box or mask.

Changed:

1. exact `512x512` source-authoritative context around each target;
2. joint source+mask upscale to `1024x1024`;
3. native `InpaintModelConditioning` at 1024;
4. generated result downsampled back to the exact 512 source coordinates;
5. deterministic composite into the untouched full source.

## Actual Runner70 result

Manifest:

`Z:\AI\SDXLInpaint\runner70_1024_parity_gate\runner70_sdxl_1024_manifest.json`

Contact sheet:

`Z:\AI\SDXLInpaint\runner70_1024_parity_gate\runner70_sdxl_1024_contact_sheet.png`

Total elapsed: `62.217 s`.

### Plank

- source context: `[117,214,629,726]` = `512x512`;
- model input: `1024x1024`;
- elapsed: `34.071 s`;
- inside-allowed changed ratio >Delta12: `0.316580`;
- outside-allowed changed ratio >Delta12: `0.0`.

Visual verdict:

**FAIL.** The selected plank remains present. The model changes/retextures/deforms the masked board region but does not create a clean narrow opening/background continuation. Training-resolution parity removes the strongest Runner69 shiny artifact but does not execute the requested structural removal.

### Strap

- source context: `[247,256,759,768]` = `512x512`;
- model input: `1024x1024`;
- elapsed: `26.069 s`;
- inside-allowed changed ratio >Delta12: `0.165934`;
- outside-allowed changed ratio >Delta12: `0.0`.

Visual verdict:

**FAIL.** The lower-right strap remains structurally continuous. The generated patch is conservative and does not create a clear missing middle section exposing coherent matching wood.

## What passed

- 1024 parity execution;
- local RTX 3060 12 GB feasibility;
- automatic masks;
- source/mask alignment;
- deterministic region containment;
- zero >Delta12 changes outside the allowed region.

## What failed

The backend still does not perform either hard physical operation after the only major unresolved confound — training resolution — was removed.

Classification:

**TECHNICAL PASS / TRAINING-RESOLUTION PARITY PASS / AUTOMATIC MASK PASS / OUTSIDE-REGION CONTAINMENT PASS / VISUAL OPERATION FAIL / SDXL INPAINTING HYPOTHESIS EXHAUSTED.**

## Decision

Do not add more arbitrary prompt/step tuning to SDXL Inpainting 0.1 for this role.

Preserve Runner69/70 outputs and manifests. Under the project cleanup rule, remove the provisional SDXL Inpainting UNet and SDXL Base checkpoint only after evidence validation, then test the next specialist behind the exact same accepted Runner66 masks and deterministic compositor.

The next canonical gate is:

`docs/RUNNER71_BIG_LAMA_OBJECT_REMOVAL_2026-09-11.md`

Runner71 tests lightweight Big-LaMa as an object-removal specialist and changes no perception/mask/compositor assumptions.