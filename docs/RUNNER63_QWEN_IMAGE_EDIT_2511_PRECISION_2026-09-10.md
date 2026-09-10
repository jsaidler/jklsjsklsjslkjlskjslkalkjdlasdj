# Runner63 — Qwen-Image-Edit-2511 FP8mixed atomic precision gate

Status date: **2026-09-10**

Status: **PREPARED / CURRENT GATE**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner63 exists

Runner62 proved that native Qwen-Image-Edit-2509 FP8 is technically feasible on the target RTX 3060 12 GB / 48 GB RAM workstation using low-VRAM execution and CPU placement for the Qwen2.5-VL encoder.

It also materially improved preservation/localization compared with FLUX.2 Klein Base, but failed the exact structural-fact contract:

- the one-plank edit did not create the required narrow full-height one-plank opening;
- the one-strap edit reinterpreted the lower hardware/door-bottom area rather than isolating and breaking only the named strap.

Therefore 2509 is not the production structural editor.

Qwen-Image-Edit-2511 is the next same-family hypothesis because the official revision specifically targets lower image drift, better consistency and stronger geometric reasoning.

## Runtime strategy

Workspace remains:

`Z:\AI\QwenImageEdit`

Shared files from Runner62 are reused:

- `qwen_2.5_vl_7b_fp8_scaled.safetensors`
  - SHA256 `cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4`
- `qwen_image_vae.safetensors`
  - SHA256 `a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f`

New diffusion checkpoint only:

`qwen_image_edit_2511_fp8mixed.safetensors`

- bytes: `20,533,762,817`
- SHA256: `c9fdc158e46d3b61ef75f21ae866ca2fe808bf4a53643120d1c1e87c19280a4e`
- source: Comfy-Org Qwen-Image-Edit_ComfyUI
- license family: Apache-2.0

Runner63 first verifies that Runner62 manifest + outputs exist. It then removes the rejected 2509 diffusion checkpoint if its SHA256 is exactly the known Runner62 hash. This preserves evidence while avoiding model accumulation.

Net diffusion payload change is only about +103 MB because the old ~20.43 GB checkpoint is retired before the new ~20.53 GB checkpoint is installed.

## ComfyUI parity

Runner63 advances the isolated Qwen ComfyUI checkout to:

`6eba895f7d3615284da81e95bf49eaed4a5f7309`

This commit contains the current native Qwen 2511 graph support used by the adapter, including:

- `TextEncodeQwenImageEditPlus`;
- `FluxKontextImageScale`;
- `FluxKontextMultiReferenceLatentMethod`;
- `ModelSamplingAuraFlow`;
- `CFGNorm`;
- `KSampler`.

Current official 2511 semantics reproduced by the adapter:

- Qwen2.5-VL encoder type `qwen_image`, device CPU;
- first edit image scaled through `FluxKontextImageScale`;
- first scaled image VAE-encoded as the edit latent;
- positive and negative both use `TextEncodeQwenImageEditPlus`;
- both conditioning branches use `FluxKontextMultiReferenceLatentMethod(index_timestep_zero)`;
- `ModelSamplingAuraFlow` shift `3.1`;
- `CFGNorm` strength `1.0`;
- Euler;
- simple scheduler;
- denoise `1.0`;
- CFG `4.0`;
- no Lightning LoRA.

The official workflow notes 20 steps as the faster Comfy default and 40 steps as the higher-quality Qwen reference setting. Runner63 tests both so the 2511 precision hypothesis is not rejected from only one step regime.

## Low-VRAM execution

ComfyUI launch remains:

- `--lowvram`;
- `--reserve-vram 1.0`;
- `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`;
- Qwen2.5-VL encoder explicitly on CPU.

The intent is to test model capability on the actual workstation before considering a more aggressively quantized/Nunchaku path.

## Controlled precision matrix

The same original Runner56 ruined gate is used for all jobs.

### One-plank task

Two Qwen 2511 jobs:

- 20 steps;
- 40 steps.

Instruction:

- remove exactly one existing plank-width from the left door leaf;
- leave a narrow full-height dark opening;
- retain every neighboring plank;
- retain all hardware, masonry and right leaf.

### One-strap task

Two Qwen 2511 jobs:

- 20 steps;
- 40 steps.

Instruction:

- break only the lower horizontal strap on the right door leaf;
- remove a substantial middle segment;
- leave snapped/bent surviving ends;
- do not replace it with a larger bar;
- do not damage door planks or other hardware.

## Comparison sheet

For each task Runner63 displays:

`ORIGINAL -> KLEIN RUNNER61 -> QWEN2509 RUNNER62 -> QWEN2511 20 -> QWEN2511 40`

This makes the expected gain explicit: not merely more source preservation, but more exact compliance with the named structural fact.

## Outputs

Directory:

`Z:\AI\QwenImageEdit\qwen2511_precision_gate`

Expected files:

- `qwen2511_atomic_plank_steps20.png`
- `qwen2511_atomic_plank_steps40.png`
- `qwen2511_atomic_strap_steps20.png`
- `qwen2511_atomic_strap_steps40.png`
- `runner63_qwen2511_precision_contact_sheet.png`
- `runner63_qwen2511_precision_manifest.json`
- `runner63_executor.log`
- Python stdout/stderr logs
- ComfyUI stdout/stderr logs

## Technical PASS

All four jobs complete on the RTX 3060 12 GB with no OOM/runtime failure and write valid images/manifests.

Expected terminal line:

`RUNNER63-QWEN2511: PASS - TECHNICAL PRECISION MATRIX COMPLETE / VISUAL VERDICT PENDING`

## Visual PASS

At least one 20/40-step result for each task must satisfy the exact structural fact while preserving unrelated geometry.

### Plank

A single narrow full-height plank-width gap must be unmistakably present. The model must not leave the door effectively unchanged and must not remove/reconstruct most of the leaf.

### Strap

Only the named lower-right strap should be broken with a missing middle section and surviving snapped/bent ends. Other hardware and wooden geometry should remain substantially unchanged.

## Decision after Runner63

### Technical + visual PASS

Promote Qwen 2511 to the next Asset Studio validation stage:

1. multi-reference semantic-role separation;
2. Exilada Character Lab revision using identity/anatomy/style roles;
3. another non-character class;
4. generic Studio UI candidate/history/approval integration.

### Technical PASS / visual precision FAIL at both 20 and 40

Do not add more blind step tests. Move to a control architecture with automatic localization/region conditioning or another editing family. Routine manual masks remain outside the production contract.

### OOM/runtime failure

Do not interpret this as a semantic model failure. Evaluate a lower-memory 2511 implementation while preserving the current evidence.

## Runner

`tools/structured-2d-character-pipeline/63_bootstrap_and_run_qwen_image_edit_2511_precision.ps1`

Executor:

`tools/roguelite-asset-studio/qwen_image_edit_2511_precision_gate.py`

Adapter:

`tools/roguelite-asset-studio/qwen_image_edit_2511_adapter.py`
