# Runner50 — PowerShell parser failure before Kontext setup

Status date: **2026-09-08**

Classification: **INTEGRATION FAIL / PRE-INFERENCE**.

## Symptom

Initial execution of:

`tools/structured-2d-character-pipeline/50_run_flux_kontext_h0_dance12_pixelart_proof.ps1`

failed in the PowerShell parser before any model download, ComfyUI launch or FLUX Kontext inference.

PowerShell reported invalid variable references at the two strings:

- `"Hash-checking existing $Label: $Destination"`
- `"Downloading $Label: $Url"`

Because `:` immediately followed `$Label` inside an interpolated string, PowerShell attempted to parse it as a scoped/drive-style variable reference.

## Repair

Both strings were changed to explicitly delimit the variable name:

- `"Hash-checking existing ${Label}: $Destination"`
- `"Downloading ${Label}: $Url"`

No model settings, URLs, hashes, workspace paths, Kontext graph, H0 input, frame selection or sampling parameters were changed.

## Evidence boundary

This failure occurred before runtime setup and before inference. It provides **zero FLUX Kontext model-quality evidence**.

Runner50 should simply be pulled again and rerun unchanged after commit `300f39179ceb01d5689f6c5ba7cc52ca2aaf38d2` or later.
