# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY CURATED PASS / SECONDARY CURATED PASS / SIENA C6 POSE GATE NEXT**

Continue the Local Video Studio in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are the canonical source of truth.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file;
5. `tools/video-studio/run_behavior_tertiary_gate_candidates.ps1`;
6. `tools/video-studio/run_behavior_tertiary_pose_gate.ps1`.

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

Verified contact-sheet source/duration:

```text
SOURCE: SIENA_BRUTO.mp4
duration = 113.313 s
8 candidate windows, 5 s each
```

Role: alternate gesture/posture vocabulary, with explicit held-object/prop/occlusion handling.

### Selected clean gate — C6

**C6 = 75.2–80.2 s**.

Selection rationale from the verified SIENA sheet:

- no held object;
- torso visible and stable;
- useful free arm/hand movement rather than a static pose;
- no graphic overlay crossing the subject;
- suitable for validating gesture/posture tracking before any full pass.

### Provisional semantic-suspect spans from the sheet

These are **review markers only**, not final exclusion boundaries:

- C1 around 5–10 s: inserted still-image/graphic overlays obscure the subject;
- C2 around 19–24 s: held print/book/photo interaction and hand occlusion;
- C4 around 47–52 s: lens/camera prop interaction with major foreground occlusion.

Do not convert these coarse sampled windows into canonical hard exclusions until the full SIENA inventory defines the real temporal boundaries.

### Next exact action — short DWPose gate only

Run:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'
git pull --ff-only origin main
powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_tertiary_pose_gate.ps1'
```

Defaults:

```text
window: 75.2–80.2 s
fps: 6
provider: CPUExecutionProvider
output track: ...\SIENA_BRUTO\selected_gate\pose_gate_c6_75p2_80p2_coco133.jsonl
overlay: ...\SIENA_BRUTO\selected_gate\pose_gate_c6_75p2_80p2_overlay.mp4
```

This runs DWPose only for 5 s and does not run Wan-Animate-2.

Upload the overlay MP4 and paste the summary. Evaluate body/arms/hands/posture and geometry before any full SIENA extraction.

## After SIENA C6 gate PASS

1. run full SIENA pose track;
2. build behavior profile and inventory;
3. use the full source/inventory to define exact semantic exclusions for overlays/objects/occlusions;
4. curate SIENA as alternate gesture/posture source;
5. build unified source-preserving multi-source library;
6. synthesize a new 4–5 s behavioral driver;
7. only then invoke installed Wan-Animate-2.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
