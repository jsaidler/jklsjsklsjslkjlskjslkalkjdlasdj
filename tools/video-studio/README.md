# Local Video Studio

This directory contains the active local tooling for the Video Studio project.

Canonical state: `../../docs/PROJECT_STATE.md`.  
Canonical route: `../../docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`.  
Canonical execution policy: `../../docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`.

## Current status

The active engineering problem is **behavioral identity**, not another static-image talking-avatar benchmark.

The required product must preserve three independent identities:

1. visual identity;
2. voice identity;
3. behavioral identity — João's real gesture language, posture, head motion, facial behavior and delivery rhythm.

The current route is fully local/self-hosted and zero-cost:

```text
João behavioral videos
    -> local pose + prosody analysis
    -> persistent motion-unit library

new local speech/audio
    -> prosody windows
    -> motion-unit selection
    -> pose continuity + diversity
    -> new driving performance built from João's real behavioral vocabulary

new driving performance
    -> already-installed Wan-Animate-2
    -> local lip-sync later if necessary
```

Do not substitute a fixed driving clip or generic autonomous motion for this architecture.

## Active first source

```text
Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4
```

This is the primary upper-body source for the first behavior profile.

## New behavior-profile tooling

### `inspect_local_behavior_tooling.ps1`

Strict read-only environment inspection.

It:

- resolves what `py -3.11` actually executes and verifies `sys.version_info`;
- inventories likely existing Python runtimes under selected local AI roots;
- reports useful installed packages where available;
- performs a bounded/no-download search for existing DWPose/whole-body/hand-pose tooling;
- writes local TXT/JSON reports under `reports/`.

It does **not** install, download, delete or perform a blind full-drive crawl.

Run from the repository root:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'

git pull --ff-only origin main

powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\inspect_local_behavior_tooling.ps1'
```

### `behavior_profile_schema_v1.json`

Persistent schema for `behavior-profile/v1`.

Each motion unit contains source/timing/RGB-span metadata plus start/end pose, head activity, hand activity, body activity, motion energy, speech/pause evidence, available prosody and transition descriptors.

### `extract_behavior_profile.py`

First renderer-independent behavior-profile extractor.

Base analysis uses local FFmpeg/ffprobe only:

- low-resolution grayscale frame-difference motion energy;
- local mono-audio RMS/dBFS and normalized energy;
- speech/pause evidence;
- short motion-unit segmentation that prioritizes pauses and low-motion transition points.

The pose backend is intentionally decoupled. The extractor accepts normalized JSONL pose frames:

```json
{"t": 1.234, "schema": "coco_wholebody_133", "keypoints": [[0.5, 0.3, 0.98]]}
```

Coordinates are normalized to `[0,1]`. For COCO WholeBody 133, the extractor derives head/body/left-hand/right-hand activity from the standard keypoint groups.

A normal gate run requires `--pose-track`.

The diagnostic flag:

```text
--allow-missing-pose
```

may be used only to inspect segmentation/prosody. Its manifest is marked:

```text
status=incomplete_pose
```

**`incomplete_pose` is not a valid behavioral-profile pass.**

Primary outputs are local and inspectable:

```text
manifest.json
motion_units.csv
```

Default output root for the primary source:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\
```

## Current gate

The immediate gate is not Wan rendering yet.

Required order:

1. run the local tooling inspector;
2. resolve the actual Python interpreter and local pose assets;
3. reuse existing compatible pose tooling if found;
4. if nothing suitable exists, enumerate the smallest required local dependency before downloading anything;
5. produce a `status=complete` manifest for the primary source;
6. inspect motion units and transition quality;
7. compose a new ~4–5 s driving performance from several units;
8. only then run the installed Wan-Animate-2 renderer.

MuseTalk, LatentSync and final voice-clone/TTS integration remain deferred until body/head behavior passes.

## Installed renderer state

Wan-Animate-2 is already installed and passed reuse preflight. Do **not** download VACE, Motion Mirror or another large renderer as the next step.

## Legacy H3 prototype files

The following files belong to the earlier MiniMax H3 prototype and remain as historical/useful orchestration code:

- `video_studio.py`;
- `index.html`;
- `config.example.json`;
- `start_video_studio.ps1`;
- `run_quality_gate.py` / `.ps1`;
- H3-related benchmark/preflight helpers.

H3 proved useful architecture and visual-identity behavior, but its production rendering and generic autonomous motion failed the current product requirement. These files are **not the active renderer route** and should not drive the next gate.

## Historical branches

Wan2.2-S2V, H3, HunyuanVideo-Avatar and HeyGen/Avatar-V records remain evidence only. Do not resume them as the next development step.

The active quality criterion remains:

> this does not merely look like João; it moves and reacts like João.
