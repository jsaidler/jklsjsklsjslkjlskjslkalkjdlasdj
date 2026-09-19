# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY CURATED PASS / SECONDARY CURATED PASS / SIENA REVIEW COMPLETE / UNIFIED LIBRARY BUILD NEXT / FIRST POSE DRIVER IMPLEMENTED**

Continue the Local Video Studio in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are canonical.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/run_behavior_finalize_library.ps1`;
6. `tools/video-studio/run_behavior_first_pose_driver.ps1`.

## Hard constraints

- 100% local/self-hosted, zero service cost;
- never upload João identity media to third parties;
- no SaaS/paid API/credits/subscriptions;
- no new large renderer;
- no new Python/DWPose/CUDA install while current CPU route works;
- Wan S2V/H3/Hunyuan/HeyGen remain retired/historical;
- MuseTalk/LatentSync/TTS remain deferred;
- no Wan-Animate-2 until first multi-source pose driver passes QA.

## Goal

New text/audio must yield a new performance that looks, sounds and chiefly **moves/reacts like João**. Generic presenter motion is failure.

## Source 1 — PRIMARY CURATED PASS

`VID_20260911_140124885.mp4` — canonical torso/hands/gesture/posture source.

```text
123 total
118 eligible
5 excluded
24.1–37.5 s / u0012-u0016 excluded for object/occlusion/prop interaction
```

## Source 2 — SECONDARY CURATED PASS

`VID_20260819_124008056.mp4` — canonical face/head/microexpression source; body support only.

```text
119 base units
116 face eligible
116 head eligible
116 body-support eligible
hands disabled
generic whole-upper disabled
face/head median weight 0.913145
```

## Source 3 — SIENA reviewed / curation implemented

`SIENA_BRUTO.mp4` — alternate posture/head/coarse-arm source.

```text
680 pose frames
0 fallback
49 behavior units
```

Reviewed exclusions:

```text
4.6–10.3 s    u0003-u0004   inserted graphic/still overlay
18.7–24.7 s   u0009-u0010   held print/photo/book
43.7–55.7 s   u0021-u0025   lens/camera foreground interaction
67.9–74.0 s   u0031-u0033   held purple card / face-body occlusion
```

Expected curation:

```text
49 total
12 hard excluded
37 clean
```

SIENA roles: head, posture, coarse_arm enabled on clean units with continuous pose quality. Hands and generic whole-upper remain disabled.

Versioned:

- `behavior_source_annotations_tertiary.json`
- `curate_tertiary_behavior_source.py`
- `run_behavior_tertiary_curation.ps1`

## Unified library — IMPLEMENTED

Schema: `joao-motion-library/v1`  
Builder: `build_unified_behavior_library.py`  
Runner: `run_behavior_finalize_library.ps1`

Role priorities:

```text
face: secondary only
head: secondary -> primary -> SIENA
posture: primary -> SIENA -> secondary support
coarse_arm: primary -> SIENA
hands: primary only
generic whole-upper: primary only
```

Semantic exclusions are applied before joining. Every unit keeps provenance, source timestamps, source paths, prosody, transitions, activity, pose boundaries and role-specific quality/priority.

## First multi-source pose driver — IMPLEMENTED / QA PENDING

Synthesizer: `synthesize_behavioral_pose_driver.py`  
Runner: `run_behavior_first_pose_driver.ps1`

First gate duration: 4–5 s, default 4.5 s / 24 fps.

Composition:

```text
base posture/coarse arms: primary + SIENA
hands: primary
face/microexpression: secondary
```

The synth does not concatenate RGB clips. It produces a single composite COCO-133 track:

- body-source changes aligned by shoulder similarity transform;
- short boundary blend;
- primary hand retargeting by wrist/forearm geometry;
- secondary face/head behavior retargeted by eye-line normalization plus relative displacement/roll/scale;
- per-frame provenance recorded.

Outputs:

```text
...\unified\first_driver\driver_plan.json
...\unified\first_driver\behavioral_driver_coco133.jsonl
...\unified\first_driver\behavioral_driver_pose_preview.mp4
```

With `-Audio <local path>`, target audio prosody/speech class participates in retrieval. Without audio, the tool is only a neutral synthesis QA spike.

## Next exact action

Run the library finalizer first:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_finalize_library.ps1'
```

Paste the complete terminal output.

Do not run the pose driver if library finalization fails.

After library PASS:

```powershell
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_first_pose_driver.ps1'
```

Preferably, when a real 4–5 s local target speech/audio file is available:

```powershell
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_first_pose_driver.ps1' -Audio '<LOCAL_AUDIO_PATH>'
```

Upload `behavioral_driver_pose_preview.mp4` for visual QA. Wan-Animate-2 remains blocked until that preview passes.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
