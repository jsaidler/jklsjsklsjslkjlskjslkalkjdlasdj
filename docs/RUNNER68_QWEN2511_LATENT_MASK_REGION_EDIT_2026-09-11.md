# Runner68 — Qwen2511 automatic latent-mask regional edit gate

Status date: **2026-09-11**

Status: **COMPLETE / TECHNICAL PASS / MASK CONTROL PASS / SEMANTIC OPERATION FAIL**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

Runner68 replaced Runner67's colored locator reference with native sampler control:

`Runner66 automatic target -> source crop -> automatic operation mask -> ImageToMask -> SetLatentNoiseMask(source latent) -> Qwen2511 -> deterministic final composite`.

Qwen received only the source crop as semantic visual conditioning. No red/colored locator image was supplied.

## Accepted prerequisites

Runner66 remained authoritative:

- one-plank automatic mask: PASS;
- lower-right strap automatic mask: PASS;
- no user-drawn mask/box.

Qwen runtime remained:

- `qwen_image_edit_2511_fp8mixed.safetensors`;
- ComfyUI commit `6eba895f7d3615284da81e95bf49eaed4a5f7309`;
- Qwen2.5-VL 7B FP8 on CPU;
- Qwen image VAE;
- low-VRAM / reserve 1 GB;
- AuraFlow shift 3.1;
- CFGNorm 1;
- Euler/simple;
- 20 steps;
- CFG 4;
- seed 0.

## Actual result

Runner68 completed technically for both operations.

### Plank

Approved/operation bbox:

`[358,295,388,644]`

Crop:

`[268,232,478,707]`

Qwen elapsed:

`481.612 s`

Difference metrics:

- mean absolute RGB: `0.109842`;
- changed ratio >Δ12: `0.001819`;
- changed ratio >Δ24: `0.000541`;
- inside-allowed changed ratio >Δ12: `0.059154`;
- outside-allowed changed ratio >Δ12: `0.0`.

Visual result: **FAIL**. The board remains present; the requested clean opening is not produced. Native latent masking constrains the region but Qwen is too conservative/semantic-edit oriented for this exact removal operation.

### Strap

Approved strap bbox:

`[456,549,550,592]`

Automatically derived central-40% operation bbox:

`[484,550,522,590]`

Crop:

`[353,485,653,656]`

Qwen elapsed:

`451.471 s`

Difference metrics:

- mean absolute RGB: `0.016693`;
- changed ratio >Δ12: `0.000263`;
- changed ratio >Δ24: `0.000080`;
- inside-allowed changed ratio >Δ12: `0.052066`;
- outside-allowed changed ratio >Δ12: `0.0`.

Visual result: **FAIL**. The central strap remains effectively continuous; the requested physical break is not created.

## What Runner68 proves

Accepted:

1. automatic perception/decomposition masks from Runner66;
2. native mask-to-latent alignment path;
3. no colored-guide leakage;
4. operation-aware strap submask generation;
5. deterministic final full-resolution containment;
6. outside-region preservation (`>Δ12 = 0.0` for both tasks).

Rejected:

- Qwen2511 as the exact mask-native removal/fill backend for this precision role.

The failure is not a perception regression and not a compositor failure. It is a semantic operation failure inside a correct edit region.

## Final classification

**TECHNICAL PASS / AUTOMATIC MASKS PASS / NATIVE LATENT MASK CONTROL PASS / OUTSIDE-REGION CONTAINMENT PASS / PLANK REMOVAL FAIL / STRAP BREAK FAIL / QWEN MASKED-PRECISION ROLE CLOSED.**

Qwen2511 remains useful as the strongest installed high-level semantic editor. Do not delete it and do not return to unrestricted global precision prompting.

## Next gate

The next branch replaces only the regional editor with a dedicated inpainting model while retaining the accepted automatic-mask contract.

Canonical next record:

`docs/RUNNER69_SDXL_INPAINT_PRECISION_2026-09-11.md`

Runner69 uses SDXL Inpainting 0.1 behind the exact same Runner66 masks and deterministic final composite.
