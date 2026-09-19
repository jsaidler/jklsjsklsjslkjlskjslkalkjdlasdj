# Local Video Studio — Current Project State

Status date: **2026-09-19**

GitHub living documents are the canonical source of truth.

## Execution policy — LOCKED

- 100% local/self-hosted;
- zero service cost;
- no SaaS/cloud generation/training/inference;
- never upload João's video/voice/identity to third parties;
- no new large renderer while this route is active;
- no new Python/DWPose/CUDA install while the validated local route works;
- Wan S2V, H3, Hunyuan and HeyGen remain historical/retired;
- MuseTalk/LatentSync/CosyVoice remain deferred.

## Objective — LOCKED

Generate new video from new text/audio that looks, sounds and chiefly **moves/reacts like João**. Generic plausible presenter motion is failure.

## Canonical architecture

```text
multiple real João behavior videos
    -> local pose + motion + prosody
    -> per-source behavior-profile/v1 motion units
    -> optional aligned facial-behavior-profile/v1 sidecar
    -> source-specific semantic + role-aware quality curation
    -> unified source-preserving João motion library

new local speech/audio
    -> prosodic windows
    -> retrieve by source role + quality + continuity + diversity
    -> NEW driving performance from João's real movement vocabulary

new driving performance
    -> installed Wan-Animate-2
    -> local lip-sync later if needed
```

A single source video is never the final library, and different sources do not have interchangeable roles.

## Canonical sources

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\`

1. `VID_20260911_140124885.mp4` — 300.352 s — torso/hands/posture/gesture primary;
2. `VID_20260819_124008056.mp4` — 282.574 s — head/face/microexpression;
3. `SIENA_BRUTO.mp4` — 113.313208 s — alternate posture/arm/head vocabulary with explicit prop/occlusion handling.

## Local pose stack — PASS

```text
Z:\AI\WanGP\env_uv\Scripts\python.exe          Python 3.11.14
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx
```

Validated provider: `CPUExecutionProvider`. CUDA ORT remains intentionally unrepaired because its EP reported missing `cublasLt64_13.dll` while CPU is functional.

## Primary source — CURATED PASS

`VID_20260911_140124885.mp4`

```text
full pose frames: 1801
fallback: 0/1801
mean keypoint score: 0.7549247491
behavior-profile/v1: complete
motion units: 123
curated eligible: 118
hard excluded: 5
```

Manual generic-behavior exclusion: **24.1–37.5 s = `u0012`–`u0016`** for held object / hand occlusion / prop interaction.

Role: primary torso/hands/posture/gesture source.

Classification: **PRIMARY SOURCE CURATED PASS**.

## Secondary source — CURATED PASS

`VID_20260819_124008056.mp4`

Role: **face/head/microexpression**, body support only.

```text
full pose: 1695 frames @ 6 fps
fallback: 1/1695
base units: 119
facial units usable with >=2 accepted frames: 116
face eligible: 116
head eligible: 116
body-support eligible: 116
hands retrieval: disabled
generic whole-upper retrieval: disabled
```

Facial quality policy remains locked: landmarks 23–90, eye-line normalization, roll removal, inter-eye scale, source-relative 3×IQR static-geometry audit, temporal jumps review-only.

```text
accepted facial geometry: 1576/1695 = 0.929794
face/head median weight: 0.913145
body-support median weight: 0.519182
```

Classification: **SECONDARY SOURCE CURATED PASS**.

## Third source — SIENA PROFILE / INVENTORY PASS

`SIENA_BRUTO.mp4`

Validated short gate: **C6 = 75.2–80.2 s**, PASS for torso/posture/head/coarse-arm motion. Hands were visibly unstable near the lower frame boundary and are not promoted to retrieval.

Full pose:

```text
duration: 113.313208 s
geometry: 1080x1920 display / rotation 0 / analysis 540x960
frames: 680 @ 6 fps
detector fallback: 0/680
mean keypoint score: 0.6698323212
provider: CPUExecutionProvider
```

Behavior profile / inventory:

```text
status: complete
motion units: 49
coverage: 0.0 -> 113.313 s
pose snapshots valid: 49/49
head activity: 48/49
body activity: 49/49
left hand activity: 49/49
right hand activity: 49/49
combined hand activity: 49/49
speech classes: mixed=39, speech=10
unit duration min/median/max: 0.800/2.200/3.800 s
```

The activity counters above do **not** establish hand suitability. The reviewed visual sheet remains authoritative for the source role.

### SIENA reviewed semantic exclusions — LOCKED

Full inventory review established exact motion-unit-aligned exclusions:

```text
4.6–10.3 s    u0003-u0004   graphic/still-image overlay + subject occlusion
18.7–24.7 s   u0009-u0010   held print/photo/book + prop interaction + hand occlusion
43.7–55.7 s   u0021-u0025   lens/camera foreground interaction + major occlusion
67.9–74.0 s   u0031-u0033   purple held card + face/body occlusion
```

Result expected from role-aware curation:

```text
49 total units
12 global hard excluded
37 semantically clean units
```

SIENA retrieval role policy — LOCKED:

- `head`: enabled on clean units, continuous coarse-head pose quality;
- `posture`: enabled on clean units, continuous body pose quality;
- `coarse_arm`: enabled on clean units, continuous body pose quality; motion speed remains a matching feature rather than a reliability multiplier;
- `left_hand`, `right_hand`, `both_hands`: retrieval disabled;
- `generic_whole_upper`: retrieval disabled.

Versioned:

- `tools/video-studio/behavior_source_annotations_tertiary.json`;
- `tools/video-studio/curate_tertiary_behavior_source.py`;
- `tools/video-studio/run_behavior_tertiary_curation.ps1`.

## Unified João motion library — IMPLEMENTED / LOCAL BUILD NEXT

Versioned builder:

`tools/video-studio/build_unified_behavior_library.py`

Output schema:

`joao-motion-library/v1`

The library preserves source file, source role, unit ID, timestamps, source video/pose-track references, speech/prosody, transition metrics, motion/activity descriptors, pose boundary snapshots, role-specific quality weights and role priority tiers.

Locked source-role priorities:

```text
face:       secondary only, tier 0
head:       secondary tier 0 -> primary tier 1 -> SIENA tier 2
posture:    primary tier 0 -> SIENA tier 1 -> secondary body-support tier 2
coarse_arm: primary tier 0 -> SIENA tier 1
hands:      primary only
generic whole-upper: primary only
```

The library does not flatten source-specific quality into one generic score. Semantic exclusions are applied before library construction.

One-shot local runner:

`tools/video-studio/run_behavior_finalize_library.ps1`

It:

1. materializes reviewed SIENA role-aware curation;
2. verifies expected `49 / 12 / 37` SIENA state;
3. joins the three curated sources into `joao-motion-library/v1`;
4. validates that required retrieval roles have at least one candidate.

No DWPose and no Wan-Animate-2 are invoked.

## Immediate next action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_finalize_library.ps1'
```

Expected unified artifact:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\joao_motion_library_v1.json
```

Paste the complete terminal output before first behavioral-driver synthesis.

## Behavioral-driver synthesis policy — NEXT GATE

The first 4–5 s driver must be genuinely multi-source rather than a concat of arbitrary RGB clips:

- face/microexpression: secondary source;
- hands: primary source;
- posture/coarse arm: primary + SIENA diversity;
- source IDs/timestamps remain preserved;
- semantic-excluded units are unavailable;
- continuity and prosody compatibility are explicit retrieval features;
- the first driver is validated in pose/behavior space before any Wan-Animate-2 render.

Do not invoke Wan-Animate-2 until the unified library and first synthesized driver both pass their local QA gates.

## Progress-output policy — LOCKED

Long local passes must emit visible progress. `extract_dwpose_track.py` reports initialization and frequent heartbeats; do not leave long-running terminal tasks silent.

## Quality gate — LOCKED

> this does not merely look like João; it moves and reacts like João.
