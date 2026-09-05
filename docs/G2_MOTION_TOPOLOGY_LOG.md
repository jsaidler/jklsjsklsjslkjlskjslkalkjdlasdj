# G2 Real Motion / Topology — Execution Log

Status date: **2026-09-04**

Gate: **G2 — real captured motion, persistent topology and sockets**

Current status: **READY TO RUN.**

## Scope

G2 deliberately does not use Exilada art or the final pixel renderer. It proves that real captured locomotion can be processed headlessly into a persistent diagnostic rig under the accepted G1 camera/scale baseline.

Locked G1 baseline:

- native raster: `640×360`;
- orthographic pitch: `26 deg`;
- protagonist reference height: `128 px`.

## Motion source

First source:

- CMU Graphics Lab Motion Capture Database;
- BVH conversion by Bruce Hahne;
- trial `105_34` — `NormalWalk`;
- pinned mirror commit: `09a07f54f3bbb58797325f009282d0b2048a2871` from `una-dinosauria/cmu-mocap`;
- source BVH: `data/105/105_34.bvh`;
- 2209 frames at 120 fps (`Frame Time: .0083333`).

Usage basis: CMU states the original database is free for research and commercial projects worldwide; Bruce Hahne states no additional restrictions are placed on the BVH conversion.

The runner downloads the file automatically from the pinned commit and records the local SHA256/provenance.

## G2 automation

Tooling:

- `tools/deterministic-character-pipeline/02_run_g2.ps1`
- `tools/deterministic-character-pipeline/g2_motion_topology.py`

The runner:

1. requires recorded G0 PASS and canonical `g1_baseline.json` PASS;
2. downloads/validates the pinned real walk source;
3. starts Blender 5.1 headlessly;
4. enables Blender's official BVH importer on demand in factory mode;
5. imports the full real motion;
6. verifies named major bones and left/right identity;
7. automatically searches the capture for a ~1.5 s straight locomotion window rather than guessing key poses/frame numbers;
8. creates a persistent baked diagnostic clone of the skeleton/action;
9. aligns travel laterally for the belt-scroller camera;
10. creates stable left/right limb proxy objects and named hand/foot socket markers;
11. estimates foot-contact frames/ground reference;
12. renders 12 samples across the selected sequence;
13. writes `g2_manifest.json`, `.blend`, source provenance and `g2_result.json`;
14. builds `g2_contact_sheet.png` for sequence-level visual QA.

## Important scope boundary

This first G2 validates **real motion + persistent topology + deterministic baking on an identical skeleton**. It does not claim arbitrary cross-skeleton retargeting is solved.

Cross-skeleton normalization remains an explicit required validation before animation-library/character production scaling. It cannot be silently assumed from this spike.

## G2 review order

1. topology: one head/torso, exactly two arms/hands and two legs/feet across all samples;
2. natural gait / phase progression;
3. grounding and foot behavior;
4. left/right limb identity;
5. stable hand/foot sockets;
6. body proportion stability;
7. usefulness under the locked `26 deg / 128 px / 640×360` presentation.

G2 remains `REVIEW_REQUIRED` until the generated contact sheet and metrics are inspected. G3 must not start automatically.
