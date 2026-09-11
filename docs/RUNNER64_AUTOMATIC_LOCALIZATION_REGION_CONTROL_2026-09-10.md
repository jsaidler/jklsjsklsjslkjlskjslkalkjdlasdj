# Runner64 — Automatic localization + region-control gate

Status date: **2026-09-11**

Status: **COMPLETE / TECHNICAL PASS / PERCEPTION FAIL / REGIONAL COMPOSITOR PASS / QWEN REGIONAL SEMANTIC VERDICT INVALID**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner64 exists

Runner63 proved Qwen-Image-Edit-2511 technically viable on RTX 3060 12 GB but failed exact lower-right strap editing under an unrestricted global prompt. Runner64 tested an architectural alternative:

`semantic target -> automatic localization -> automatic segmentation -> contextual regional edit -> deterministic regional composite`

No user-drawn mask, manual box, repainting or per-asset retouching is part of the production contract.

## Stack

### Grounding DINO Tiny

- repo `IDEA-Research/grounding-dino-tiny`
- revision `a2bb814dd30d776dcf7e30523b00659f4f141c71`
- safetensors SHA256 `1a2412ef99bd74bcd3c2a246fa1e48581f8889a1300c9051974741314fc042f3`
- Apache-2.0

### SAM2.1 Hiera Small

- repo `facebook/sam2.1-hiera-small`
- revision `e07df6aa19f5c6545121551bf89957b7663ee715`
- safetensors SHA256 `0a4067b11ce1e23d5229203f11c718a823060d15a4b23fa2372a7d4b77cbbc60`
- Apache-2.0

### Qwen editor

- `qwen_image_edit_2511_fp8mixed.safetensors`
- 20 steps / CFG 4 / Euler/simple
- Qwen2.5-VL encoder on CPU
- ComfyUI low-VRAM runtime

## Harness correction before final run

The first Runner64 attempt completed localization and started Qwen ComfyUI, then failed before any Qwen prompt submission because `qwen2511_region_control_gate.py` passed the nonexistent keyword `timeout_seconds` to `QwenImageEdit2511Adapter`. The inherited constructor accepts `timeout_minutes`.

That harness mismatch was corrected before the final Runner64 run. It is not model evidence.

## Final technical run

The complete pipeline ran successfully and wrote:

- Grounding DINO candidate diagnostics;
- SAM2 masks/overlays;
- contextual crops;
- Qwen raw crop edits;
- deterministic regional composites;
- contact sheet;
- localization and regional manifests.

Total regional run time reported by the manifest: `1501.799 s`.

Qwen crop generation times:

- plank: `766.501 s`;
- strap: `734.090 s`.

Therefore Runner64 is a **technical PASS**.

## Visual review — perception FAIL

The visual review and localization manifest make the failure unambiguous.

### Plank task

Requested target: one vertical wooden plank in the door.

Selected Grounding DINO box:

`[62.7451, 540.7537, 329.1651, 704.2875]`

Detector label: `door`.

That box corresponds to the **lower-left stone pedestal**, not a wooden door plank.

SAM2 then segmented that wrong target with high internal confidence:

- predicted IoU `0.92298`;
- mask area ratio `0.04672`.

The resulting Qwen/composite output modifies the lower-left stone region. It is not evidence about Qwen's ability to remove the intended plank because Qwen never received the correct target.

### Strap task

Requested target: the lower-right horizontal iron door strap.

Selected Grounding DINO box:

`[543.9662, 513.4839, 696.7905, 621.7897]`

Detector label: `strap`.

That box corresponds to the **lower-right stone block**, not the iron strap.

SAM2 again segmented the wrong selected object cleanly:

- predicted IoU `0.95213`;
- mask area ratio `0.01900`.

The resulting regional edit is therefore also invalid as evidence about the intended strap operation.

## What actually passed visually

The deterministic regional-composite contract worked.

Difference metrics against the original:

### Plank final

- mean absolute RGB difference: `2.2121`;
- changed ratio above Δ12: `0.04229`;
- changed ratio above Δ24: `0.02582`;
- outside-allowed mean absolute difference: `0.000607`;
- outside-allowed changed ratio above Δ12: **`0.0`**.

### Strap final

- mean absolute RGB difference: `0.59067`;
- changed ratio above Δ12: `0.01072`;
- changed ratio above Δ24: `0.00651`;
- outside-allowed mean absolute difference: `0.000014`;
- outside-allowed changed ratio above Δ12: **`0.0`**.

So the compositor successfully prevents the global geometry drift seen in Runner63. It changed the wrong regions only because perception supplied wrong masks.

## Root cause

Runner64 searched for small subcomponents directly against the **entire gateway image** and then used side/vertical-zone/shape heuristics on those full-image detections.

This created a predictable failure mode:

- the left/lower selector preferred the left stone pedestal for `plank`;
- the right/lower selector preferred the right stone block for `strap`;
- SAM2 faithfully segmented the selected false positives.

The perception stack itself is technically healthy. The flat instance-selection strategy is not adequate for small components embedded inside a larger parent object.

## Final classification

**TECHNICAL PASS / FLAT FULL-IMAGE SUBCOMPONENT LOCALIZATION FAIL / SAM2 SEGMENTATION OF SELECTED BOX PASS / DETERMINISTIC REGIONAL COMPOSITOR PASS / QWEN REGIONAL SEMANTIC VERDICT INVALID.**

Do not spend additional Qwen generation time on Runner64 masks. Do not blame or replace Qwen on the basis of these outputs.

## Next gate — Runner65

Canonical next record:

`docs/RUNNER65_HIERARCHICAL_LOCALIZATION_2026-09-11.md`

Runner65 is perception-only:

`full image -> parent door grounding -> parent crop/upscale -> child component grounding -> SAM2 multi-candidate rerank -> visual review`

Key changes:

- localize the parent object first;
- search for components only inside the parent;
- upscale the parent crop before component grounding;
- lower component detection thresholds to improve recall;
- send up to ten component proposals through SAM2;
- rerank using containment, mask aspect, area and parent-relative spatial relation;
- fail closed when geometry is implausible;
- launch **no Qwen inference** until both masks are visually approved.

Runner65 reuses the exact Runner64 Grounding DINO Tiny and SAM2.1 cache. No new model download is required.

## Files/evidence

Runner64 localizer:

`tools/roguelite-asset-studio/automatic_region_localizer.py`

Regional editor/compositor:

`tools/roguelite-asset-studio/qwen2511_region_control_gate.py`

Runner:

`tools/structured-2d-character-pipeline/64_bootstrap_and_run_automatic_region_control.ps1`

Localization evidence:

`Z:\AI\RogueliteAssetStudio\localization\runner64_gate`

Regional evidence:

`Z:\AI\QwenImageEdit\automatic_region_control`

No Runner64 result activates `automatic_region_edit` as a production-routable capability. The perception layer must pass first.
