# G3S-B3 — Nude Body Base

Status date: **2026-09-05**

Gate status: **B3-A V2 PASS/CLOSED — B3-B V1 3D-MASK ROUTE FAIL/CLOSED — B3-B V2 AUTHORED NATIVE 2D SOURCE READY FOR REVIEW**

## Why this gate exists

G3S-B2 proved that the complete persistent body cannot be recovered by subtracting hair/clothing from the composite master. The body must therefore be authored independently and must remain complete beneath every removable layer.

Measured B2 facts:

- source opaque pixels: `2974`;
- visible body pixels: `1538`;
- hair pixels: `826`;
- clothing pixels: `610`;
- hidden/unknown body pixels: `1205`.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b2_approval.json`

## Locked production order

1. complete adult body base, hairless and independent of clothing/equipment;
2. separate persistent hair asset/layer family;
3. separate clothing/bindings/cuffs/shackles/chains/accessories;
4. layered motion proof.

No hair, clothing or animation begins before B3-B passes visually.

## Body ownership — LOCKED

The complete body base owns skin, silhouette, anatomical continuity and permanent body-side identity. It contains no hair, garment, binding, restraint or chain pixels. Nudity is a normal supported runtime state produced by omitting garment/equipment layers rather than reconstructing hidden body pixels.

The project does not impose blanket desexualization. Adult-body presentation may be neutral, sensual, erotic, heroic, vulnerable or brutal according to scene intent. Native gameplay scale limits microdetail, but no censor layer is structurally required.

## Visible-ownership invariant — LOCKED

G3V demoted hidden 3D from visible-image ownership.

Hidden 3D may supply motion, topology, left/right identity, joints, sockets, depth/occlusion, physics and structural/anatomical reference. It may not own final visible RGB, alpha or final sprite silhouette.

Consequently:

- a B3A render is reference only;
- a B3A binary mask is reference only;
- neither may be copied into final sprite coverage;
- recoloring/downsampling a 3D raster is not authored 2D art.

Final exported/runtime art remains sprite-based.

## B3-A V1 — FAIL/CLOSED REVISION

The first deterministic anatomy guide used `MPFB gender = 1.0`, which resolves male in the pinned MPFB semantics. This was a script revision error, not a rejection of MPFB as structural infrastructure.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3a_v1_failure.json`

No model cleanup command applies.

## B3-A V2 — PASS/CLOSED

The corrected structural guide validates:

- adult female phenotype;
- complete body geometry;
- female targets `21`, male targets `0`;
- adult targets `21`, minor targets `0`;
- zero hair/clothing/restraint/chain objects;
- visible height `128 px` at the locked gameplay camera/scale;
- guide-only art authority.

Approval marker:

`tools/structured-2d-character-pipeline/g3s_b3a_approval.json`

B3A is closed. Do not iterate MPFB appearance as final art.

## B3-B V1 — FAIL/CLOSED ROUTE

The first B3B implementation copied the B3A projected body mask into the final native alpha/silhouette and then procedurally colored it. Even without copying lit RGB, this left hidden 3D as visible silhouette owner and revived the rejected procedural-man­nequin authoring route.

Failure marker:

`tools/structured-2d-character-pipeline/g3s_b3b_v1_route_failure.json`

The invalid V1 script and runner were removed from `main`. No model was downloaded or discarded by this correction, so no cleanup command applies.

## B3-B V2 — AUTHORED NATIVE 2D SOURCE — READY FOR REVIEW

V2 changes the authority boundary completely: the final body source now exists as a committed native `128×128` 2D pixel asset authored independently from the B3A RGB, mask and projected silhouette.

Art authority:

`assets/source/characters/exilada/body/g3s_b3b_body_base_source_v2.png`

SHA256:

`0fc90ca6a86e3adceba4d8fe100eb0d8e8e06337d6820585c6e535515fdfab53`

Metadata:

`tools/structured-2d-character-pipeline/g3s_b3b_body_base_source_v2.json`

Validation/export tooling:

- `tools/structured-2d-character-pipeline/g3s_b3b_validate_authored_body_v2.py`
- `tools/structured-2d-character-pipeline/12_run_g3s_b3b_authored_body_v2.ps1`

Canonical dedicated log:

`docs/G3S_B3B_NATIVE_2D_BODY_SOURCE_LOG.md`

### V2 source ownership

The committed 2D asset owns:

- final visible RGB;
- final alpha;
- final silhouette;
- native pixel clusters/value structure.

The validator does not load or sample B3A rendered output. B3A is only an already-passed gate prerequisite and anatomical/scale reference.

### V2 measured source facts

- native canvas: `128×128`;
- visible bbox: `[17, 0, 120, 127]`;
- visible height: `128 px`;
- visible width: `104 px`;
- opaque palette colors: `8`;
- binary alpha;
- hair/clothing/binding/restraint/chain ownership: `0`.

These technical facts do not approve the art.

## B3-B visual PASS criteria

1. complete readable adult female body at native 1×;
2. independently authored 2D silhouette;
3. Exilada-compatible lean/resilient proportions;
4. coherent chest, pelvis, hands and feet;
5. intentional modern pixel-art clusters rather than low-resolution 3D or procedural mannequin appearance;
6. useful persistent body-base source for later structured 2D part/deformation work;
7. no hair/clothing/restraint/chain pixels;
8. no hidden-3D visible ownership;
9. readable gameplay preview at `640×360` / `128 px` body height.

If V2 fails visual review, revise the committed 2D art directly. Do not return to B3A mask copying and do not reopen sprite-model search.

## After B3-B PASS

Only then proceed to G3S-B4 hair, G3S-B5 clothing/restraints/accessories and G3S-C layered motion.

## Exact next action

```powershell
git -C "D:\GOOGLE DRIVE\DEV\Roguelite" pull --ff-only

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\12_run_g3s_b3b_authored_body_v2.ps1"
```

Then STOP and share:

`Z:\AI\RogueliteCharacterPipeline\g3s_b3b_authored_body_v2\g3s_b3b_contact_sheet_v2.png`

or the complete console error.
