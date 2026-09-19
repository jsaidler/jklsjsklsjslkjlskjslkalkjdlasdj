# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY CURATED PASS / SECONDARY CURATED PASS / SIENA GATE SAMPLING NEXT**

Continue the Local Video Studio in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are the canonical source of truth.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/run_behavior_tertiary_gate_candidates.ps1`;
6. `tools/video-studio/sample_behavior_gate_candidates.py`.

## Hard constraints

- 100% local/self-hosted;
- zero service cost;
- never upload João identity media to third parties;
- no SaaS/paid API/credits/subscriptions;
- no new large renderer;
- no new Python/DWPose/CUDA install while current route works;
- Wan S2V/H3/Hunyuan/HeyGen remain retired/historical;
- MuseTalk/LatentSync/TTS remain deferred.

## Goal

New text/audio must yield a new performance that looks, sounds and chiefly **moves/reacts like João**. Generic presenter motion is failure.

## Primary source — CURATED PASS

`VID_20260911_140124885.mp4`

Role: torso/hands/posture/gesture.

```text
123 total units
118 eligible
5 hard excluded
24.1–37.5 s excluded for held object / hand occlusion / prop interaction
```

## Secondary source — CURATED PASS

`VID_20260819_124008056.mp4`

Role: face/head/microexpression; body support only.

```text
119 base units
116 face eligible
116 head eligible
116 body-support eligible
hands retrieval disabled
generic whole-upper retrieval disabled
face/head median weight = 0.913145
body-support median weight = 0.519182
```

Classification: **SECONDARY SOURCE CURATED PASS**.

## Third source — SIENA_BRUTO

Canonical source:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\SIENA_BRUTO.mp4`

Expected duration: approximately **113.3 s**.

Role: alternate gesture/posture vocabulary, with explicit held-object/prop/occlusion handling.

Do not run full DWPose yet.

### Important rejected artifact

A contact sheet uploaded after the first SIENA sampler request was **not SIENA**. It visibly reused the secondary source: candidate timestamps extended to ~272 s and the image content matched `VID_20260819_124008056.mp4`.

Do not derive any SIENA gate decision from that sheet.

### Sampler integrity hardening

The sampler/runner now enforce source identity more visibly:

- every generated contact sheet has a top header with `SOURCE: <filename>` and duration;
- candidate manifest includes `source_name` and `duration_s`;
- SIENA runner requires `source_name == SIENA_BRUTO.mp4`;
- SIENA runner requires duration in the broad 100–130 s integrity band to catch accidental reuse of the 282 s secondary source or another file.

## Next exact action

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_tertiary_gate_candidates.ps1'
```

The terminal must show:

```text
Manifest source: SIENA_BRUTO.mp4
Manifest duration: ~113 s
SIENA CANDIDATE SAMPLER: PASS
```

Upload exactly:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO\gate_candidates\candidate_contact_sheet.jpg
```

Confirm visually that the JPG header says `SOURCE: SIENA_BRUTO.mp4` and shows the ~113 s duration before evaluating candidates.

## After correct SIENA contact-sheet review

1. choose clean SIENA 5 s gate;
2. identify visible prop/object/occlusion intervals;
3. run short DWPose gate only;
4. if visual gate passes, run full SIENA pose track;
5. build/inspect/curate SIENA with source-specific semantic exclusions;
6. build unified source-preserving multi-source library;
7. synthesize a new 4–5 s behavioral driver;
8. only then invoke installed Wan-Animate-2.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
