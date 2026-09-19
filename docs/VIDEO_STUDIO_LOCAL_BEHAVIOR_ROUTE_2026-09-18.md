# Local Video Studio — local behavioral-video route

Date: **2026-09-18**  
Updated: **2026-09-19**  
Status: **ACTIVE / PRIMARY CURATED PASS / SECONDARY CURATED PASS / SIENA GATE SAMPLING NEXT**

Canonical state: `docs/PROJECT_STATE.md`  
Execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`

## Problem

Static visual identity plus audio can make a person look like João while moving like someone else. The product requires João's behavioral identity: posture, head movement, hands, gesture timing, expressions and delivery rhythm. Generic plausible motion is insufficient.

## Selected architecture — LOCKED

```text
multiple real João behavior videos
    -> local pose + motion + prosody
    -> per-source behavior-profile/v1
    -> optional facial-behavior-profile/v1 sidecar
    -> semantic exclusions + role-specific continuous quality weights
    -> unified source-preserving motion-unit library

new local speech/audio
    -> prosodic windows
    -> retrieve by role + quality + continuity + diversity
    -> NEW João driving performance

new driving performance
    -> installed Wan-Animate-2
    -> local lip-sync later if needed
```

## Canonical sources and roles

- `VID_20260911_140124885.mp4` — primary torso/hands/posture/gesture;
- `VID_20260819_124008056.mp4` — primary face/head/microexpression;
- `SIENA_BRUTO.mp4` — alternate gesture/posture with explicit object/occlusion handling.

A single source is never the final João library, and sources must not be forced into one universal quality policy.

## Primary source — CURATED PASS

```text
123 total units
118 eligible
5 hard excluded
24.1–37.5 s excluded for held-object/prop interaction + hand occlusion
```

Primary policy:

- whole-upper gesture source;
- continuous group quality by head/body/left/right hand;
- semantic prop-specific spans can be globally excluded from generic retrieval.

## Secondary source — CURATED PASS

Full pose/profile/facial sidecar route passed.

```text
119 base units
116 face-usable units
accepted facial geometry 1576/1695 = 0.929794
```

Role-aware retrieval is now locked:

- **face/microexpression**: 116 eligible, weight = face quality;
- **head**: 116 eligible, weight = coarse head pose quality × face quality;
- **body_support**: 116 eligible, auxiliary only;
- **hands**: retrieval disabled;
- **generic whole-upper**: retrieval disabled;
- **global hard exclusions**: 0.

Observed role-weight distributions:

```text
face q10/median/q90 = 0.7649534 / 0.913145 / 0.9241892
head q10/median/q90 = 0.7649534 / 0.913145 / 0.9241892
body_support q10/median/q90 = 0.4351354 / 0.519182 / 0.5724356
```

Zero-face units `u0003`, `u0006`, `u0007` remain in the base profile but are not eligible for face/head retrieval. Sparse hands are expected and do not fail this source.

Classification: **SECONDARY SOURCE CURATED PASS**.

## Third source — SIENA_BRUTO route

Role: alternate gesture/posture vocabulary, with semantic handling of props, held objects and occlusions.

Do **not** jump directly to a full DWPose pass.

First:

1. sample several 5-second candidate windows;
2. select a clean gate with useful free gesture/posture and visible body/hands;
3. note obvious prop/object/occlusion spans separately;
4. run DWPose only on the selected 5-second gate;
5. inspect the overlay before any full extraction.

Versioned sampler:

`tools/video-studio/run_behavior_tertiary_gate_candidates.ps1`

It samples source frames only and writes:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\gate_candidates\candidate_contact_sheet.jpg
```

## Next

Run the SIENA candidate sampler, upload the contact sheet, choose the clean gate, then perform a short DWPose visual gate.

After SIENA passes and is curated:

1. preserve source IDs/timestamps/roles for all eligible units;
2. build unified source-preserving library;
3. retrieve with role-specific body/hand/head/face weights;
4. synthesize a new 4–5 s multi-source performance;
5. only then invoke installed Wan-Animate-2.

## Stop conditions

- no new large renderer;
- no DWPose/Python/CUDA reinstall while current route works;
- no source role forced into an inappropriate universal quality metric;
- no prop/object-specific motion accepted as generic behavior;
- no face-off-frame pathology accepted as microexpression data;
- no single-source final library;
- no Wan-Animate-2 before multi-source library/synthesis validation.

Quality criterion:

> this does not merely look like João; it moves and reacts like João.
