# Runner58 — FLUX.2 Klein 4B edit-strength calibration

Status date: **2026-09-09**

Status: **COMPLETE / TECHNICAL PASS / PRODUCTION EDIT VISUAL FAIL**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

Runner58 exhausted the most plausible simple calibration of the already-installed **FLUX.2 Klein 4B distilled FP8** before changing branches.

Runner57 had already proven that single- and multi-reference editing execute technically. Runner58 asked whether stronger prompts plus 4/8/12-step calibration could make those edits useful for actual art direction.

No new checkpoint was introduced.

## Runtime

- workspace: `Z:\AI\Flux2Klein`
- ComfyUI commit: `672ba9e5e388bd6bfac5ceef61f89ffdd9467200`
- diffusion: `flux-2-klein-4b-fp8.safetensors`
- text encoder: `qwen_3_4b.safetensors`
- VAE: `flux2-vae.safetensors`
- output: 768×768
- CFG: 1.0
- sampler: Euler
- seed: 0 for edits

## Test design

### Single-reference matrix

Original ruined gate as `previous_approved_state`, at 4 / 8 / 12 steps.

Requested binary facts:

1. remove one entire vertical plank from the left door leaf;
2. remove one large top-left capstone/lintel block;
3. snap/partially remove the lower iron strap on the right door leaf;
4. strongly corrode surviving iron;
5. visibly warp/split/water-damage timber.

### Material authority

A separate reference board was generated containing severe rust, grime, damaged timber, fractured masonry, dirt, moss and roots.

### Multi-reference matrix

- Image 1 = `structure`: original gate;
- Image 2 = `material`: severe-decay material board;
- 4 / 8 / 12 steps.

The same structural edits were requested so that material transfer and edit obedience could be judged separately.

## Actual technical result — PASS

All seven jobs completed without OOM, graph failure or runtime crash.

Elapsed times:

- single 4: **16.130 s**
- single 8: **16.054 s**
- single 12: **24.036 s**
- material reference: **6.014 s**
- multi 4: **16.030 s**
- multi 8: **26.093 s**
- multi 12: **38.168 s**
- total matrix: **156.620 s**

Contact sheet SHA256:

`6025b4265918ffea7ea97369cd122384a4bc822e7c53d1965f9caa80e8a62aae`

## Difference metrics

### Single-reference

| steps | mean abs luma | changed >12 | changed >24 |
|---:|---:|---:|---:|
| 4 | 23.8699 | 0.857127 | 0.386804 |
| 8 | 27.6526 | 0.881953 | 0.794367 |
| 12 | 29.2693 | 0.887327 | 0.808146 |

Increasing steps clearly increases broad pixel drift/re-rendering.

### Multi-reference

| steps | mean abs luma | changed >12 | changed >24 |
|---:|---:|---:|---:|
| 4 | 12.0681 | 0.281148 | 0.042324 |
| 8 | 14.3251 | 0.351788 | 0.161229 |
| 12 | 15.3945 | 0.375287 | 0.203785 |

The second reference changes the result, but its practical influence remains weak relative to the source structure.

## Visual verdict — FAIL for production reference editing

### Single-reference

The 8/12-step outputs are visibly more re-rendered and show stronger rust/material change, but they still fail the important test: the requested binary structural facts are not reliably executed.

In particular, the outputs do not clearly and consistently deliver all of:

- a full-height missing door plank;
- a clearly missing large top-left capstone mass;
- the requested broken lower-right iron strap.

Therefore the high pixel-difference values do **not** constitute stronger semantic obedience.

### Multi-reference

The original identity/camera are preserved strongly, but the severe material board has too little authority. The outputs remain much closer to the original gate than to the requested material severity and again fail the explicit structural changes.

This is useful evidence: preservation is strong, but controllable transformation is insufficient for the Studio's production editor contract.

## Canonical conclusion

**FLUX.2 Klein 4B distilled remains accepted as the fast local T2I / concept-generation backend.**

Its single- and multi-reference paths are technically proven but **must not be routed as production editing capabilities** for the Roguelite Asset Studio.

Do not continue increasing distilled steps blindly. Runner58 shows that more steps create more image drift without solving the required edit-obedience problem.

## Next gate

Stay inside the same Apache-2.0 4B family before changing model families:

**Runner59 — FLUX.2 Klein 4B Base strong reference-edit gate.**

Rationale:

- Base is the non-distilled, higher-flexibility branch;
- official ComfyUI Base editing uses a materially different recipe (CFG 5 / full-step sampling / small-decoder VAE);
- it reuses the existing Qwen3-4B encoder;
- it adds only the Base diffusion checkpoint and `full_encoder_small_decoder.safetensors`;
- if Base also fails, the project has sufficient evidence to move editing to a stronger specialized editor rather than continuing to tune Klein distilled.
