# G3V Representative Visual Proxy — Gate Plan

Status date: **2026-09-05**

Gate: **G3V — representative continuous human asset + deterministic pixel translation**

Current status: **PLANNED / IMPLEMENTATION NEXT.**

## Purpose

G3V exists because G3/G3R proved that renderer tuning on a primitive capsule/mannequin cannot answer the production-art question. The next test must introduce enough real authored form to make visual judgement meaningful without yet investing in the finished Exilada.

Question to answer:

**Can a coherent continuous human asset with representative silhouette/material structure, driven by the approved deterministic motion backbone, produce a convincing native-grid pixel result through a fully headless pipeline?**

## Locked upstream facts

- G0 headless automation: PASS;
- G1 camera/scale: PASS — `640×360`, orthographic pitch `26 deg`, protagonist reference height `128 px`;
- G2 real motion/topology: PASS — CMU `105_34 NormalWalk`;
- G3 native translation: technical PASS only; visible look not approved;
- G3R renderer-only refinement: FAIL / CLOSED.

## Representative asset strategy

Preferred first candidate: **MakeHuman/MPFB 2.x core human system**.

Reasons for testing it:

- continuous human basemesh rather than capsule segments;
- scriptable human creation in Blender;
- scriptable built-in rig creation/weight loading;
- parameterized macro body attributes suitable for a lean adult female proxy;
- core asset licensing compatible with project use;
- Blender 5.1.1 is above MPFB2's minimum Blender requirement.

The project will not assume MPFB is production-approved until headless creation, rigging and reuse actually pass locally.

## Minimal G3V character

This is not the final Exilada model. It must contain only enough structure to test the real visual hypothesis:

1. continuous lean adult female body mesh;
2. deformation rig and weights;
3. large long dark hair mass as persistent geometry;
4. one simple asymmetric degraded cloth piece;
5. wrist and ankle restraint/metal markers on named sides;
6. bare feet;
7. simple material IDs: skin / hair / cloth / metal;
8. stable body-part and attachment metadata.

No scars, gore, detailed garments, weapons, facial likeness or production-grade hair are required yet.

## Motion integration

G3V must reuse the already approved real walk basis. The first implementation may use one of two headless-safe methods:

A. retarget the approved CMU walk to the representative human rig; or
B. if the MPFB rig is deliberately made compatible with the canonical motion skeleton, bake equivalent transforms through an explicit scripted bone map.

Whichever route is chosen must be reproducible and may not require GUI retargeting.

## Visual outputs

At minimum:

- one representative still at native `640×360` / `26 deg` / ~`128 px` character height;
- four walk phases from the same asset;
- flat semantic/debug render;
- deterministic pixel-render result using material-aware palette bands and contour rules;
- silhouette/mask diagnostics;
- contact sheet at native review scale;
- manifest with source/license/provenance, body parameters, rig mapping, renderer configuration and output hashes.

## PASS criteria

G3V can PASS only if all are true:

1. human anatomy/silhouette reads as a coherent person rather than a technical mannequin;
2. the representative hair/cloth/restraint masses remain structurally stable;
3. the result at native 1× has a credible path toward intentional modern pixel art;
4. the image is not merely a conventional 3D render made blocky by reduction;
5. motion deformation remains coherent across sampled walk phases;
6. the complete build/rig/motion/render process is headless and reproducible;
7. the result contains enough visual headroom to justify beginning actual Exilada identity mapping.

## FAIL / kill switch

If a materially richer continuous human asset still reads as filtered/low-resolution 3D, the project stops trying to make hidden 3D own the final visible character image.

In that case:

- retain hidden 3D for motion, topology, sockets, physics reference and semantic guides;
- move the final visible character to a structured 2D representation driven by those deterministic guides;
- do not spend time building a detailed Exilada 3D production model first.

## Operator constraint

The user must not install/configure/operate MPFB or Blender manually as a normal requirement. Tooling must own dependency acquisition/configuration and execute through one documented PowerShell command once the gate implementation is ready.
