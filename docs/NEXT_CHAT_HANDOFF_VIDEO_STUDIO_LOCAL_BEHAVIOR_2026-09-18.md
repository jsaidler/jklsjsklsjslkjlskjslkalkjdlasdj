# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **PRIMARY CURATED PASS / SECONDARY CURATED PASS / SIENA CURATED PASS / UNIFIED LIBRARY PASS / FIRST DRIVER v1 NUMERIC FAIL / VISUAL DIAGNOSTIC NEXT**

Continue in GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`. GitHub living docs are canonical.

Read first:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. this file.

## Hard constraints

- 100% local/self-hosted, zero service cost;
- never upload João identity media to third parties;
- no SaaS/paid API/credits/subscriptions;
- no new large renderer;
- no new Python/DWPose/CUDA install while current CPU route works;
- Wan S2V/H3/Hunyuan/HeyGen remain retired/historical;
- MuseTalk/LatentSync/TTS remain deferred;
- no Wan-Animate-2 until a multi-source pose driver passes numeric + visual QA.

## Curated sources

### Primary
`VID_20260911_140124885.mp4` — torso/hands/gesture/posture.

```text
123 total
118 eligible
5 excluded
24.1–37.5 s / u0012-u0016 excluded
```

### Secondary
`VID_20260819_124008056.mp4` — face/head/microexpression; body support only.

```text
119 base units
116 face eligible
116 head eligible
116 body-support eligible
hands disabled
face/head median quality 0.913145
```

### SIENA
`SIENA_BRUTO.mp4` — alternate posture/head/coarse arm.

```text
49 total
12 hard excluded
37 clean
hands disabled
generic whole-upper disabled
```

Locked exclusions:

```text
4.6–10.3 s    u0003-u0004
18.7–24.7 s   u0009-u0010
43.7–55.7 s   u0021-u0025
67.9–74.0 s   u0031-u0033
```

SIENA pose-reliability weights are saturated at 1.0 and do not rank its clean units meaningfully.

## Unified library — PASS

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\joao_motion_library_v1.json`

```text
271 total units
primary 118
secondary 116
tertiary 37
```

Classification: **UNIFIED MULTI-SOURCE LIBRARY PASS**.

## First pose driver v1 — NUMERIC FAIL

Neutral 4.5 s / 24 fps / 108-frame QA synthesis, no target audio.

```text
base order primary -> tertiary
planner boundary continuity 0.528554
```

Selected provenance:

```text
window 0
base  primary:VID_20260911_140124885_u0114
hands primary:VID_20260911_140124885_u0114
face  secondary:VID_20260819_124008056_u0026

window 1
base  tertiary:SIENA_BRUTO_u0037
hands primary:VID_20260911_140124885_u0075
face  secondary:VID_20260819_124008056_u0105
```

Numeric QA v2:

```text
confidence-qualified OOB total = 0.161972
coarse_head OOB  = 0.000000
face OOB         = 0.000000
upper_body OOB   = 0.177083
left_hand OOB    = 0.417108
right_hand OOB   = 0.440917

transition q90 / non-transition q90:
body_head  6.1729x
face       3.1519x
left_hand  3.0979x
right_hand 1.5199x
```

Interpretation: **driver/compositor v1 fails numeric QA**. The source library remains valid. Exact boundary jump zero is a blending artifact, not continuity evidence. Hand roots attach exactly to wrists, but hand framing is unacceptable and the source transition is dynamically anomalous.

Wan-Animate-2 remains blocked.

## Next exact action

Upload the existing diagnostic preview:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver\behavioral_driver_pose_preview.mp4`

Use it to identify the visible failure mode before modifying synthesis.

Expected compositor-v2 direction:

- continuity-aware retrieval for base + face + hands;
- smoother transition evaluated across the full interval;
- in-frame hand/wrist room considered in candidate selection;
- keep current sources/library/renderer route unchanged;
- no DWPose re-extraction.

Final quality gate:

> “isso não apenas parece João; isso se move e reage como João.”
