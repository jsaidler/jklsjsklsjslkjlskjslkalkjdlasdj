# Roguelite Asset Studio — Foundation

This directory contains the UI-independent foundation of the local generative asset production tool defined in `docs/ROGUELITE_ASSET_STUDIO.md`.

## Current files

- `asset_schema.json` — canonical asset/output/reference-role vocabulary.
- `model_registry.json` — current model adapters, hardware/licensing state and task capabilities.
- `asset_studio_core.py` — validates asset specs and routes them to compatible model families.
- `examples/exilada_master.json` — Character Lab example.
- `examples/ruined_gate.json` — non-character architecture-module example.

## What this layer deliberately does not contain

- Gradio/UI widgets;
- Exilada-specific prompt semantics;
- ComfyUI graph definitions;
- checkpoint download logic;
- model installation logic;
- runtime sprite-size assumptions.

Those concerns live in replaceable model adapters or UI surfaces.

## Validate a spec

From PowerShell with any Python 3 installation:

```powershell
python .\tools\roguelite-asset-studio\asset_studio_core.py `
  .\tools\roguelite-asset-studio\examples\exilada_master.json `
  --include-uninstalled
```

The same command with `ruined_gate.json` must produce a different capability requirement and compatible route set, proving that the router is not character-specific.

## Routing behavior

By default the router only returns installed/available adapters.

Use `--include-uninstalled` only for planning/evaluation. Candidate models in the registry must never be interpreted as installed merely because they are routable on paper.

## Next implementation layer

Add an adapter protocol with implementations for:

1. installed MiniMax H3 Ref2VA;
2. installed FLUX.1 Kontext R&D runtime;
3. FLUX.2 Klein 4B only after its controlled local feasibility/install spike passes.

The eventual Studio UI will call those adapter contracts rather than constructing model-specific ComfyUI graphs itself.