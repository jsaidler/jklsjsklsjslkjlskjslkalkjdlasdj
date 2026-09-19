# Local Video Studio — local behavioral-video route

Date: **2026-09-18**  
Updated: **2026-09-19**  
Status: **ACTIVE / PRIMARY CURATED PASS / SECONDARY FACIAL GATE PASS / SECONDARY FULL POSE NEXT**

Canonical state: `docs/PROJECT_STATE.md`  
Execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`

## Problem

Static visual identity plus audio can make a person look like João while moving like someone else. The product requires João's behavioral identity: posture, head movement, hands, gesture timing, expressions and delivery rhythm. Generic plausible motion is insufficient.

## Selected architecture — LOCKED

```text
multiple real João behavior videos
    -> local pose + motion + prosody
    -> per-source profiles
    -> semantic/manual exclusions + continuous group-quality weights
    -> facial/microexpression descriptors where supported
    -> unified source-preserving motion-unit library

new local speech/audio
    -> prosodic windows
    -> retrieve units across sources
    -> pose continuity + diversity + quality/source weighting
    -> NEW João driving performance

new driving performance
    -> installed Wan-Animate-2
    -> local lip-sync later if needed
```

## Canonical sources

- `VID_20260911_140124885.mp4` — primary torso/hands/posture/gesture;
- `VID_20260819_124008056.mp4` — facial/head/microexpression;
- `SIENA_BRUTO.mp4` — alternate gesture/posture with explicit object/occlusion handling.

A single source is never the final João library.

## Primary source — CURATED PASS

Primary pose/profile/inventory/curation route passed.

Final primary curation:

```text
123 total units
118 eligible
5 hard excluded
24.1–37.5 s excluded for held-object/prop interaction + hand occlusion
```

Eligible units retain continuous quality weights by head/body/left hand/right hand rather than a blind global confidence reject.

## Secondary source — FACIAL/HEAD GATE PASS

Canonical gate:

**C3 = 83.6–88.6 s** from `VID_20260819_124008056.mp4`.

The uploaded 30-frame / 6 fps overlay was inspected frame-by-frame.

Observed:

- face landmarks 23–90 remain attached to brows, eyes, nose and lips;
- mouth-shape changes track coherently;
- brow/eye landmarks remain stable through expression changes;
- head landmarks move smoothly;
- no gross topology jump or subject switch;
- upper torso remains coherent enough to anchor the facial sequence.

Whole-body/hand lines crossing the face in QA are visual clutter from off-frame groups, not failure of facial tracking.

Classification: **SECONDARY C3 FACIAL/HEAD VISUAL GATE PASS**.

## Facial representation — REQUIRED BEFORE SECONDARY PROFILE

Current behavior-profile v1 `head_motion` uses keypoints 0–4. That captures gross head motion but is too coarse for the second source's role.

The gate now provides direct evidence that facial landmarks **23–90** are usable.

Locked consequence:

- full secondary pose extraction may proceed immediately, because all 133 points are retained;
- do not build the secondary behavior profile with only the old head descriptor;
- after the full pose track passes, add facial/microexpression descriptors from 23–90;
- the extension must be additive/backward-compatible with the primary source;
- expression descriptors should attempt to separate local facial deformation from whole-head translation/scale instead of merely measuring the centroid of all face points.

Potential descriptor families to implement/validate after full pose extraction include normalized mouth opening/width, eye openness, brow/eye relation and translation/scale-normalized facial-shape activity. Do not lock numerical thresholds before measuring the real full-track distributions.

## Secondary full pose extraction — NEXT

Versioned:

`tools/video-studio/run_behavior_pose_full_secondary.ps1`

Defaults:

- full `VID_20260819_124008056.mp4`;
- 6 fps;
- long side 960;
- CPU provider;
- normalized original COCO WholeBody 133 ordering;
- facial points 23–90 preserved;
- summary with geometry, fallback and aggregate confidence;
- no Wan-Animate-2.

After its summary passes, implement/validate facial descriptors **before** secondary profile construction.

## Downstream

1. run full secondary pose extraction;
2. extend/validate facial descriptors from landmarks 23–90;
3. build/inspect/curate secondary profile with face/head source-role weighting;
4. validate/process `SIENA_BRUTO.mp4` with source-specific exclusions;
5. unify all eligible source-preserving units;
6. retrieve with source-role + group-quality weighting;
7. synthesize a new 4–5 s multi-source performance;
8. only then invoke installed Wan-Animate-2.

## Stop conditions

- no new large renderer;
- no DWPose/Python/CUDA reinstall while current route works;
- no low-relative-coverage tag treated blindly as rejection;
- no prop/object-specific motion accepted as generic behavior;
- no second-source profile that throws away validated facial landmarks 23–90;
- no single-source final library;
- no Wan-Animate-2 before multi-source library/synthesis validation.

Quality criterion:

> this does not merely look like João; it moves and reacts like João.
