# G0 Headless Automation — Execution Log

Status date: **2026-09-04**

Gate: **G0 — Blender headless automation**

Current status: **PENDING RE-RUN AFTER FIXES.** Blender itself is installed and executable; failures observed so far were defects in project tooling, not a Blender installation failure.

## Target environment observed

- Windows 11 Home Single Language 10.0.26200
- Blender 5.1.1
- Blender executable: `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`
- workspace: `Z:\AI\RogueliteCharacterPipeline`

## Failure 1 — native argument quoting

Initial runner used `Start-Process -ArgumentList` with a Python script path under `D:\GOOGLE DRIVE\...`.

Windows PowerShell flattened/split the path at spaces, so Blender received `D:\GOOGLE` instead of the complete script path.

Resolution: replace `Start-Process -ArgumentList` with direct native invocation using PowerShell argument-array splatting.

## Failure 2 — Windows PowerShell native stderr handling

Second run reached the Python probe, but Windows PowerShell 5.1 converted Blender stderr into `NativeCommandError` while the wrapper had `$ErrorActionPreference = 'Stop'`. The wrapper therefore terminated before reporting Blender's real exit code and complete traceback.

Resolution:

- temporarily use `$ErrorActionPreference = 'Continue'` only around the native Blender invocation;
- preserve stdout/stderr logs;
- add Blender `--python-exit-code 1` so an uncaught Python exception deterministically fails the process.

## Failure 3 — Blender 5.x Eevee identifier

The Python probe hard-coded `BLENDER_EEVEE_NEXT` for Blender >=4.0. Blender 5.0 changed Eevee's render-engine identifier back to `BLENDER_EEVEE`, so Blender 5.1.1 raises an enum error when the old identifier is assigned.

Resolution: runtime-probe Eevee identifiers in this order:

1. `BLENDER_EEVEE`
2. `BLENDER_EEVEE_NEXT`

The script no longer assumes a version boundary.

## Current fixed tooling

- `tools/deterministic-character-pipeline/00_run_g0.ps1`
- `tools/deterministic-character-pipeline/g0_headless_probe.py`

Relevant commits:

- `262091a40a35797e833d9fcb9811435964a30fac` — native stderr handling / Python exit-code hardening
- `6f918fb6d9f9c4d20059e0a2599b218031ca3cf8` — Blender 5.x Eevee compatibility

## Next gate action

Re-run G0 once with the fixed tooling. Do not advance to G1 until the run produces `g0_probe.png`, `g0_manifest.json` and `g0_result.json` with `G0: PASS`.
