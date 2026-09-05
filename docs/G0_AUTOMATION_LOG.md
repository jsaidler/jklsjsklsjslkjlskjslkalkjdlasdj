# G0 Headless Automation — Execution Log

Status date: **2026-09-04**

Gate: **G0 — Blender headless automation**

Current status: **PASS.** The target machine successfully ran Blender 5.1.1 headlessly, created a scripted scene, saved a `.blend`, rendered a diagnostic PNG, emitted a machine-readable manifest and passed independent SHA256 verification.

## Validated environment

- Windows 11 Home Single Language `10.0.26200`
- Blender `5.1.1`
- Blender executable: `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`
- render engine used by the probe: `BLENDER_EEVEE`
- workspace: `Z:\AI\RogueliteCharacterPipeline`
- free workspace space observed at PASS run: `138.44 GB`

## PASS evidence

Generated successfully:

- `Z:\AI\RogueliteCharacterPipeline\g0\g0_probe.png`
- `Z:\AI\RogueliteCharacterPipeline\g0\g0_probe.blend`
- `Z:\AI\RogueliteCharacterPipeline\g0\g0_manifest.json`
- `Z:\AI\RogueliteCharacterPipeline\g0\g0_result.json`

Validated diagnostic PNG SHA256:

`bb8c938d6fe64a84de264a7c01824b1dabad27f3abd307485f706553b0d19d53`

Console markers:

- `G0_HEADLESS_PROBE=PASS`
- `G0_ENGINE=BLENDER_EEVEE`
- `G0: PASS`

## Tooling defects encountered and resolved

### 1. Native argument quoting

The first runner used `Start-Process -ArgumentList` as an array and Windows PowerShell split `D:\GOOGLE DRIVE\...` at spaces.

Resolution: paths are explicitly quoted when constructing the native Blender command line.

### 2. Windows PowerShell 5.1 stderr wrapping

Direct native invocation caused Blender stderr to be surfaced as `NativeCommandError`, producing alarming PowerShell output even when Blender itself succeeded.

The successful PASS run still showed this cosmetic wrapper noise because Blender emitted deprecation warnings after rendering.

Resolution after PASS: G0 launcher was hardened again to use `Start-Process` with one explicitly quoted argument string plus redirected stdout/stderr. This preserves paths containing spaces while preventing PowerShell 5.1 from turning benign native stderr into parent-shell `NativeCommandError` records.

### 3. Blender 5.x Eevee identifier

The original Python probe assumed `BLENDER_EEVEE_NEXT`. Blender 5.1.1 uses `BLENDER_EEVEE`.

Resolution: runtime engine probing now tries compatible identifiers rather than relying on a hard-coded Blender version boundary.

### 4. Deprecation warnings

Blender 5.1.1 warns that `World.use_nodes` and `Material.use_nodes` are expected to be removed in Blender 6.0. These warnings did **not** affect G0 PASS. Production tooling should avoid depending on deprecated APIs where practical, but they are not a blocker for G1.

## G0 decision

**PASS / CLOSED.**

The project has proven that the user does not need to operate Blender GUI. ChatGPT-authored PowerShell/Python tooling can drive Blender headlessly and produce deterministic artifacts/reports on the target machine.

No further G0 rerun is required for progression.

## Next gate

**G1 — camera/native gameplay scale.**

G1 compares a controlled 3×3 matrix at native `640×360`:

- camera pitch: `18° / 26° / 34°`;
- protagonist visible height target: `112 / 128 / 144 px`;
- same belt-scroller depth band, one protagonist proxy and five enemy proxies.

The output is a single contact sheet plus machine-readable metrics. G2 must not start until G1 is visually reviewed.
