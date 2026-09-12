# Runner71 — Big-LaMa automatic-mask object-removal gate

Status date: **2026-09-12**

Status: **COMPLETE / TECHNICAL PASS / VISUAL OBJECT-REMOVAL FAIL**

Canonical project state: `docs/PROJECT_STATE.md`.

## Why Runner71 existed

Runner70 exhausted SDXL Inpainting 0.1 fairly: even at its `1024x1024` training-resolution regime, the model reinterpreted/reconstructed the masked regions instead of performing the required physical removals.

Runner71 changed only the removal backend while preserving the accepted automatic masks, source contexts and deterministic compositor.

Editor:

**Big-LaMa** via the pinned `enesmsahin/simple-lama-inpainting` TorchScript artifact.

Pinned artifact:

- `big-lama.pt`;
- bytes `205803670`;
- SHA256 `7ba7aa7ac37a4d41fdbbeba3a2af7ead18058552997e3a3cd1a3b2210c9e6b4c`;
- Apache-2.0 LaMa lineage.

## Control contract

`Runner66 approved automatic target -> Runner71 tight/expanded operation mask -> Big-LaMa -> deterministic full-resolution composite`

No prompt, manual mask, manual box or repaint was used.

The gate reused the same `512x512` source-authoritative contexts later used for direct backend comparison.

## Actual technical result

Classification:

**TECHNICAL PASS / VERY FAST / MASK+COMPOSITOR PASS / VISUAL OBJECT-REMOVAL FAIL.**

All four jobs completed on CUDA.

Total gate time: `7.478 s`.

### Plank / tight

- inference: `1.676 s`;
- inside-allowed changed ratio >Delta12: `0.275328`;
- outside-allowed changed ratio >Delta12: `0.0`.

### Plank / expanded

- inference: `2.870 s`;
- inside-allowed changed ratio >Delta12: `0.276856`;
- outside-allowed changed ratio >Delta12: `0.0`.

### Strap / tight

- inference: `0.094 s`;
- inside-allowed changed ratio >Delta12: `0.125950`;
- outside-allowed changed ratio >Delta12: `0.0`.

### Strap / expanded

- inference: `0.092 s`;
- inside-allowed changed ratio >Delta12: `0.156337`;
- outside-allowed changed ratio >Delta12: `0.0`.

The deterministic compositor therefore continued to satisfy the exact containment contract.

## Visual verdict

### Plank — FAIL

Both mask-boundary variants reconstructed plausible **door/wood continuity** through the target rather than producing the required empty one-board opening. The model reacted locally but solved the missing region as texture/context completion instead of object removal.

### Strap — FAIL

Both variants reconstructed/smoothed local ferrage/door continuity. Neither produced a clearly absent center section with aged wood exposed beneath while preserving the two outside strap ends.

The tight/expanded matrix therefore rules out a simple mask-edge explanation.

## Architectural conclusion

Big-LaMa is a useful lightweight context-completion inpainter, but it is **not routable as the project's exact automatic object-removal specialist** for this contract.

The result does not reopen:

- Grounding DINO/SAM2 hierarchy;
- Runner66 repeated-element decomposition;
- operation-specific automatic masks;
- deterministic full-resolution composition.

Those components remain accepted. Only the regional removal backend changes.

## Cleanup

Runner71 manifest/contact sheet/generated evidence is retained.

`big-lama.pt` is rejected for production routing and Runner72 removes it only after validating preserved Runner71 evidence and its exact SHA256.

## Next gate

Runner72:

`docs/RUNNER72_POWERPAINT_OBJECT_REMOVAL_2026-09-12.md`

PowerPaint v2.1 / BrushNet is a materially different hypothesis because it has an explicit learned `object removal` task using `P_ctxt`/`P_obj` conditioning rather than blind local context completion.
