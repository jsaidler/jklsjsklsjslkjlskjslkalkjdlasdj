# G3S-B3B — Native 2D Body Source

Status date: **2026-09-05**

Gate status: **V2 AUTHORED NATIVE 2D SOURCE READY FOR USER REVIEW**

## Canonical correction retained

G3S-B3B V1 is FAIL/CLOSED because it copied the projected B3A/MPFB mask into the final sprite silhouette. Hidden 3D remains motion/topology/reference infrastructure only and does not own visible RGB, alpha or final silhouette.

## V2 implementation

V2 is a committed native `128×128` 2D pixel asset authored independently from the B3A rendered RGB, binary mask and projected silhouette.

Art authority:

`assets/source/characters/exilada/body/g3s_b3b_body_base_source_v2.png`

SHA256:

`0fc90ca6a86e3adceba4d8fe100eb0d8e8e06337d6820585c6e535515fdfab53`

Metadata:

`tools/structured-2d-character-pipeline/g3s_b3b_body_base_source_v2.json`

Validation/export tooling:

- `tools/structured-2d-character-pipeline/g3s_b3b_validate_authored_body_v2.py`
- `tools/structured-2d-character-pipeline/12_run_g3s_b3b_authored_body_v2.ps1`

## Ownership invariant

The committed 2D asset owns:

- final visible RGB;
- final alpha;
- final silhouette;
- native pixel clusters and value structure.

B3A is not sampled by the validator. It remains an already-approved structural reference and gate prerequisite only.

## Current measured source facts

- canvas: `128×128`;
- visible bbox: `[17, 0, 120, 127]`;
- visible height: `128 px`;
- visible width: `104 px`;
- opaque palette colors: `8`;
- binary alpha;
- hair pixels: `0`;
- clothing/binding pixels: `0`;
- restraint/chain pixels: `0`.

These facts do not constitute visual PASS. Native 1× review remains mandatory.

## PASS review

Review must judge the source itself, not the 3D guide:

1. adult female anatomy and readable complete body;
2. Exilada-compatible lean/resilient proportions;
3. coherent chest/pelvis/hands/feet at native 1×;
4. intentional modern pixel-art clusters rather than a procedural mannequin look;
5. useful neutral body-base pose for later 2D part authoring/deformation;
6. no hidden-3D visible ownership.

If V2 fails visual review, revise this committed 2D art asset directly. Do not return to projected-mask authoring and do not reopen model search.

## Exact next action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\12_run_g3s_b3b_authored_body_v2.ps1"
```

Then STOP and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_authored_body_v2\g3s_b3b_contact_sheet_v2.png`

or the complete console error.
