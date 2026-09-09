# FLUX.2 Klein 4B — Roguelite Asset Studio local feasibility spike

Status date: **2026-09-09**

Status: **RUNNER56 PASS — LOCAL T2I TECHNICAL PASS + VISUAL CONTINUATION PASS / REFERENCE EDITING MOVED TO RUNNER57**

Canonical umbrella architecture: `docs/ROGUELITE_ASSET_STUDIO.md`.

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

Validate whether **FLUX.2 Klein 4B distilled FP8** can become the first generic static generation/editing backend for the Roguelite Asset Studio on the actual production workstation:

- Windows 11;
- RTX 3060 12 GB VRAM;
- 48 GB system RAM.

The first generated asset was deliberately a reference-free `architecture_module`, not a character, so the gate tested a generic Studio route rather than an Exilada-specific path.

## Exact runtime and payload — PROVEN

Workspace:

`Z:\AI\Flux2Klein`

Isolated ComfyUI:

`Z:\AI\Flux2Klein\ComfyUI_windows_portable`

Pinned ComfyUI commit:

`672ba9e5e388bd6bfac5ceef61f89ffdd9467200`

The runtime is independent of the existing H3 and Kontext workspaces.

Exact model payload:

1. `flux-2-klein-4b-fp8.safetensors`
   - 4,070,624,520 bytes
   - SHA256 `97ed34fe0567e436200f2faee3939b88f2b5d99f8af2a4dc16532c4245c0ccb6`
2. `qwen_3_4b.safetensors`
   - 8,044,982,048 bytes
   - SHA256 `6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a`
3. `flux2-vae.safetensors`
   - 336,211,292 bytes
   - SHA256 `868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3`

Total model payload: `12,451,817,860` bytes (~12.45 GB decimal / ~11.60 GiB).

The full Qwen3-4B encoder was intentionally used instead of an additional FP4 quantization so the first model-quality test did not change two variables at once.

## Runner56 controlled inference — ACTUAL RESULT

Runner:

`tools/structured-2d-character-pipeline/56_bootstrap_and_run_flux2_klein_4b_spike.ps1`

Executor:

`tools/roguelite-asset-studio/flux2_klein_t2i_probe.py`

Configuration:

- `asset_type=architecture_module`;
- `output_contract=static_master`;
- reference-free text-to-image;
- `768×768`;
- `4` distilled steps;
- CFG `1.0`;
- sampler `euler`;
- seed `0`.

Actual inference result:

- technical status: `INFERENCE_COMPLETE`;
- no OOM;
- no CUDA/runtime crash;
- all three file hashes verified;
- output decoded at exactly `768×768 RGB`;
- inference elapsed: **12.054 s**;
- output SHA256: `8ce5b54cf4f7ccabf3aee3583de9c76c8942115aed8592a9430b8ede68730a16`;
- prompt id: `e65a7d0c-f8a5-479b-9995-78cf8978d79f`.

Output:

`Z:\AI\Flux2Klein\spike\flux2_klein_4b_t2i_probe.png`

Manifest:

`Z:\AI\Flux2Klein\spike\flux2_klein_4b_t2i_manifest.json`

Executor log:

`Z:\AI\Flux2Klein\spike\flux2_klein_4b_t2i_executor.log`

## Technical verdict — PASS

Runner56 proved on the actual RTX 3060 12 GB machine that the installed distilled 4B stack can provide an interactive generic static-generation backend.

The ~12 s latency at 768×768 / 4 steps is fast enough to justify an interactive Asset Studio path. The 768×768 probe resolution is not a production-resolution lock.

## Visual continuation verdict — PASS, NOT ASSET APPROVAL

The ruined-gate output is a useful static authoring master for the next editing gate:

Strengths:

- coherent load-bearing architectural construction;
- complete isolated-object framing;
- strong readable silhouette;
- useful separation of stone, wood, iron, roots/moss and accumulated age;
- enough authored detail to support iterative revision;
- no catastrophic composition/text artifacts.

Known weaknesses in this particular candidate:

- too symmetrical overall;
- crack/damage distribution remains somewhat decorative;
- door and ironwork are cleaner/more orderly than the intended world language;
- the result can still read partly as polished generic fantasy/asset-store art rather than a unique Roguelite asset.

These weaknesses do **not** fail Runner56. They make this image a useful source for Runner57 because the next gate must prove that requested structural/material changes can be introduced by reference editing **without wholesale replacement of the approved identity**.

This image is not an approved shipping asset and does not prove the final pixel-art rendering language.

## Router promotion after Runner56

The machine-readable registry now marks `flux2_klein_4b_distilled` as:

`active_static_t2i_proven_edit_pending`

Active/routable capabilities:

- `text_to_image`;
- `interactive_concept`.

Planned but deliberately **not yet routable** until Runner57 passes:

- `single_reference_edit`;
- `multi_reference_edit`;
- `interactive_variant`.

This distinction prevents the router from claiming capabilities that have only been demonstrated by upstream documentation rather than the actual local runtime.

## Generic adapter implementation after PASS

The Runner56 proof has been promoted into UI-independent Studio code:

- `tools/roguelite-asset-studio/adapter_protocol.py`
- `tools/roguelite-asset-studio/flux2_klein_adapter.py`

The generic request contract carries asset type, output contract, prompt, dimensions/settings and ordered semantic references. The adapter translates that request into native ComfyUI model semantics. The future Studio UI therefore does not need to know about FLUX.2 graph nodes.

## Next gate — Runner57 reference editing

Runner:

`tools/structured-2d-character-pipeline/57_run_flux2_klein_reference_edit_gate.ps1`

Executor:

`tools/roguelite-asset-studio/flux2_klein_edit_gate.py`

Runner57 downloads **no new checkpoints**. It reuses the proven Runner56 runtime and runs two jobs:

1. **single-reference edit**
   - source role: `previous_approved_state`;
   - same gate identity/camera/construction must remain recognizable;
   - requested asymmetrical damage, harsher decay, corrosion and broken-door/material changes must appear.
2. **ordered two-reference edit**
   - Image 1 role: `structure` — authority for identity, silhouette, camera and construction;
   - Image 2 role: `material` — authority for harsher damage/material aging;
   - one coherent gate must result; no duplicated object and no incoherent averaging.

Both jobs retain the controlled `768×768`, 4-step, CFG 1.0, Euler, seed 0 test settings so only the reference-edit contract changes.

Runner57 technical PASS does not automatically activate editing in the router. Human visual review must also pass.
