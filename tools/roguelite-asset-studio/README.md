# Roguelite Asset Studio — Foundation

This directory contains the UI-independent foundation and backend probes for the local generative asset production tool defined in `docs/ROGUELITE_ASSET_STUDIO.md`.

## Current files

- `asset_schema.json` — canonical asset/output/reference-role vocabulary.
- `model_registry.json` — current model adapters, hardware/licensing state, capabilities and active spike metadata.
- `asset_studio_core.py` — validates asset specs and routes them to compatible model families.
- `flux2_klein_t2i_probe.py` — Runner56 executor for the first generic static-generation backend feasibility test.
- `examples/exilada_master.json` — referenced Character Lab routing example.
- `examples/ruined_gate.json` — reference-free architecture-module routing example.

## Foundation status

Runner55 passed for both deliberately different cases:

- referenced playable character -> requires single/multi-reference editing;
- reference-free architecture module -> requires text-to-image.

`references: []` is valid for reference-free generation. A missing route is not a schema error.

## Current gate — Runner56

Runner:

`tools/structured-2d-character-pipeline/56_bootstrap_and_run_flux2_klein_4b_spike.ps1`

Record:

`docs/FLUX2_KLEIN_4B_ASSET_STUDIO_SPIKE_2026-09-08.md`

Runner56 creates an isolated `Z:\AI\Flux2Klein` runtime, pins ComfyUI, downloads only the exact verified FLUX.2 Klein 4B distilled FP8 + full Qwen3-4B + FLUX.2 VAE payload, and generates one reference-free `architecture_module` at 768×768 / 4 distilled steps.

The first test intentionally proves generic static generation outside character work. Passing T2I does not yet prove single/multi-reference editing or final project rendering language.

## Architecture boundary

The generic core deliberately does not contain:

- Gradio/UI widget semantics;
- Exilada-specific prompt semantics;
- one universal ComfyUI graph;
- runtime sprite-size assumptions.

Model-specific graph/download/runtime concerns live in replaceable adapters or controlled backend probes. The eventual Studio UI calls those contracts rather than constructing model graphs itself.

## Routing behavior

By default the router only returns installed/available adapters.

Use `--include-uninstalled` only for planning/evaluation. Candidate models in the registry must never be interpreted as installed merely because they are routable on paper.

FLUX.2 Klein remains `priority_candidate_not_installed` until actual Runner56 inference and subsequent editing validation pass.

## Next after Runner56 PASS

1. record technical/visual verdict;
2. create the generic Klein adapter for `text_to_image`;
3. validate `single_reference_edit` and `multi_reference_edit` with semantic reference roles;
4. then expose the adapter to Character Lab, Prop/Equipment and Environment workflows;
5. wrap H3 Ref2VA as the proven temporal character-motion adapter;
6. keep Kontext as R&D only unless its licensing role changes.
