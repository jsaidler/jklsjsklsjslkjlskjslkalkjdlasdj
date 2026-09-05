# G2 Real Motion / Topology — Execution Log

Status date: **2026-09-04**

Gate: **G2 — real captured motion, persistent topology and sockets**

Current status: **PASS / CLOSED.**

## Locked G1 baseline

- native raster: `640×360`;
- orthographic pitch: `26 deg`;
- protagonist reference height: `128 px`.

## Motion source

- CMU Graphics Lab Motion Capture Database;
- BVH conversion by Bruce Hahne;
- trial `105_34` — `NormalWalk`;
- pinned mirror commit: `09a07f54f3bbb58797325f009282d0b2048a2871` from `una-dinosauria/cmu-mocap`;
- source BVH: `data/105/105_34.bvh`;
- 2209 frames at 120 fps (`Frame Time: .0083333`).

Usage basis: CMU states the original database is free for research and commercial projects worldwide; Bruce Hahne states no additional restrictions are placed on the BVH conversion.

## Tooling

- `tools/deterministic-character-pipeline/02_run_g2.ps1`
- `tools/deterministic-character-pipeline/g2_motion_topology.py`
- canonical approval marker: `tools/deterministic-character-pipeline/g2_approval.json`

## Validated result

The generated 12-frame contact sheet was reviewed across the complete sampled sequence.

PASS observations:

- normal major-limb topology persists across all reviewed samples;
- one head/torso, two arms and two legs remain visually coherent;
- left/right leg alternation is clear;
- the motion is based on real captured gait rather than manually invented key poses;
- the walk progresses naturally through distinct phases;
- the deterministic proxy remains one continuous character structure rather than independent generated frames;
- the accepted `26 deg / 128 px / 640×360` camera/scale remains usable for locomotion review.

This closes the architectural failure mode that killed the direct per-frame diffusion route: motion/topology are now owned by persistent deterministic structure.

## Scope boundary — still important

G2 does **not** prove:

- final pixel-art quality;
- Exilada identity;
- arbitrary cross-skeleton retargeting;
- final foot-lock cleanup for all locomotion clips;
- hair/cloth/chains/equipment;
- gore/damage;
- combat animation quality.

Cross-skeleton normalization remains an explicit validation before broad animation-library scaling.

## Next gate

**G3 — native pixel-translation feasibility.**

G3 is the early visual kill switch. A generic stylized semantic proxy driven by the approved G2 motion is compared under three deterministic render strategies before any detailed Exilada 3D geometry is built.

Do not start G4 until G3 is explicitly reviewed and recorded PASS.
