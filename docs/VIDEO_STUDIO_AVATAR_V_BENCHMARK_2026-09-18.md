# Local Video Studio — HeyGen Avatar V branch

Date: **2026-09-18**  
Status: **RETIRED / INVALID PROJECT ROUTE / HISTORICAL ONLY**

Canonical project state: `docs/PROJECT_STATE.md`.
Canonical execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`.

## Why this branch is retired

HeyGen Avatar V / Digital Twin is an external commercial hosted service. The project constraints require local/self-hosted execution and no paid generation/service dependency.

Therefore:

- do not upload João's source footage to HeyGen;
- do not create a HeyGen Digital Twin;
- do not buy credits or subscriptions;
- do not use Avatar V as a production benchmark or fallback.

The earlier recommendation to make HeyGen the next renderer benchmark was a project-state error and is superseded.

## What remains useful from this branch

The source-library work remains valid because it was done locally and did not depend on HeyGen.

### Original behavioral sources

- `SIENA_BRUTO.mp4` — 113.313 s, 1080x1920, H.264 + AAC;
- `VID_20260819_124008056.mp4` — 282.574 s, 1920x1080, H.264 + AAC;
- `VID_20260911_140124885.mp4` — 300.352 s, 3840x2160, HEVC + AAC.

### Local source-role review

- `VID_20260911_140124885.mp4` — strongest upper-body behavioral source;
- `VID_20260819_124008056.mp4` — strongest close facial/microexpression source;
- `SIENA_BRUTO.mp4` — alternate motion/look source with useful gesture coverage and foreground-object occlusions.

### Local derivative

The file:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\prepared\joao_heygen_digital_twin_primary_1080p_h264.mp4`

was prepared locally before the external-route error was caught. It is simply a full-duration 1080p H.264/AAC derivative of the strongest behavioral source. It may be retained for local experiments; its filename is historical only.

The `avatar_v` directory name is likewise historical. Do not infer permission to use Avatar V from the path name.

## Preserved technical lesson

The behavioral-identity diagnosis remains correct:

> a model that receives only a still image plus audio does not know João's characteristic expressions, gestures, head timing, posture or delivery rhythm.

The correct next renderer must use real João video as behavioral conditioning or learned personal motion identity.

## Replacement benchmark requirement

The replacement benchmark must be local/self-hosted and zero-cost by default.

It must test:

1. real video-conditioned personal identity;
2. new Portuguese speech/audio not copied from the source performance;
3. visual identity;
4. behavioral identity;
5. practical runtime on Windows 11 / RTX 3060 12 GB / 48 GB RAM;
6. no hosted-service dependency.

No further work should be done on the HeyGen branch.