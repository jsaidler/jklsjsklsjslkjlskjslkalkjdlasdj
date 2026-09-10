# Runner63 — Qwen-Image-Edit-2511 FP8mixed atomic precision gate

Status date: **2026-09-10**

Status: **TECHNICAL PASS / PLANK IMPROVED / STRAP PRECISION FAIL / GLOBAL-PROMPT PRECISION HYPOTHESIS CLOSED**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

Runner63 tested Qwen-Image-Edit-2511 as the final global natural-language precision-edit hypothesis after:

- Klein Base proved coarse semantic editing but failed component localization;
- Qwen-Image-Edit-2509 improved source preservation/localization but still failed exact one-plank and one-strap facts.

The 2511 revision was selected because its official release targets better consistency and stronger geometric reasoning.

## Runtime

Workspace:

`Z:\AI\QwenImageEdit`

ComfyUI commit:

`6eba895f7d3615284da81e95bf49eaed4a5f7309`

Models:

- `qwen_image_edit_2511_fp8mixed.safetensors`
  - bytes `20,533,762,817`
  - SHA256 `c9fdc158e46d3b61ef75f21ae866ca2fe808bf4a53643120d1c1e87c19280a4e`
- `qwen_2.5_vl_7b_fp8_scaled.safetensors`
  - SHA256 `cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4`
- `qwen_image_vae.safetensors`
  - SHA256 `a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f`

Low-VRAM execution:

- RTX 3060 12 GB;
- 48 GB RAM;
- `--lowvram`;
- 1 GB VRAM reserve;
- Qwen2.5-VL encoder on CPU.

Graph parity:

- `TextEncodeQwenImageEditPlus`;
- `FluxKontextImageScale`;
- `FluxKontextMultiReferenceLatentMethod(index_timestep_zero)`;
- AuraFlow shift `3.1`;
- CFGNorm `1.0`;
- Euler/simple;
- CFG `4`;
- no Lightning.

## Bootstrap incidents

Two bootstrap failures occurred before model testing and are not model evidence:

1. PowerShell `$Args` helper collision caused `git.exe` to receive no fetch arguments; fixed by renaming to `$GitArgs` and using named parameters.
2. a transient `files.pythonhosted.org` connection reset interrupted dependency synchronization; Runner63 was hardened with outer retries, pip retries/timeouts and resumable environment reuse.

The final run completed successfully.

## Actual matrix

Source: Runner56 ruined gate, 1024×1024 outputs, seed 0.

### Plank / 20 steps

- elapsed: **401.095 s**;
- mean abs luma: **4.8265**;
- changed ratio >24: **0.018129**.

Visual: meaningful improvement over Qwen2509 and Klein. A narrow vertical opening is created in the left leaf and overall source preservation is strong. It is close to the requested one-plank fact, though nearby left-leaf topology/hardware still shifts enough that this is not treated as a universal precision proof by itself.

### Plank / 40 steps

- elapsed: **691.408 s**;
- mean abs luma: **4.9914**;
- changed ratio >24: **0.018307**.

Visual: essentially the same behavior class as 20 steps. The extra sampling cost does not produce a decisive precision gain.

### Strap / 20 steps

- elapsed: **375.293 s**;
- mean abs luma: **3.5249**;
- changed ratio >24: **0.014082**.

Visual: **FAIL**. Instead of breaking only the lower horizontal strap on the right leaf, the model creates a large replacement/transverse bar across the lower doorway region.

### Strap / 40 steps

- elapsed: **777.197 s**;
- mean abs luma: **3.7888**;
- changed ratio >24: **0.013060**.

Visual: **FAIL** again. More steps do not fix target interpretation/localization and retain the large-bar failure mode.

Total Runner63 matrix elapsed: **2270.227 s**.

Contact sheet SHA256:

`9d6910161591540d77a3e8b7629c7e431c04957ac04f664ee28b0a0176e85eec`

## Final verdict

**Qwen-Image-Edit-2511 is technically viable and substantially better at source preservation than Klein, and it materially improves the one-plank task, but global natural-language prompting alone does not satisfy production subcomponent precision.**

The visual contract required both one-plank and one-strap tasks to pass. The strap task fails decisively at both 20 and 40 steps.

Therefore:

- do **not** route unrestricted global Qwen2511 edits as `precision_structural_edit`;
- do **not** continue blind step/prompt tuning;
- retain Qwen2511 as the strongest semantic editor currently installed;
- move precision control to a perception/localization architecture.

## Next gate

Runner64:

`docs/RUNNER64_AUTOMATIC_LOCALIZATION_REGION_CONTROL_2026-09-10.md`

Architecture:

`semantic target -> Grounding DINO -> SAM2.1 -> contextual Qwen2511 crop edit -> deterministic automatic regional composite`

The user does not draw masks or boxes. Perception and region-control are part of the Studio pipeline.
