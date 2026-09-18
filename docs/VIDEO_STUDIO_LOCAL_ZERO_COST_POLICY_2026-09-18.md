# Local Video Studio — local-only / zero-cost execution policy

Date: **2026-09-18**  
Status: **CANONICAL / LOCKED**

## User constraint

The Video Studio must not depend on external hosted generation/training platforms or paid tools/services.

This restates prior user constraints from the project:

- "você não poderia ter escolhido um serviço pago para isso";
- "não quero nada com custos";
- paid/hosted PixelLab-style routes were previously rejected in favor of local, free, self-hostable tools.

## Hard rules

1. **Generation, training, fine-tuning, avatar/profile construction, voice cloning and inference must run locally/self-hosted.**
2. **Do not upload João's personal video, voice or identity material to third-party generation/avatar providers.**
3. **Do not use SaaS/cloud inference APIs, credit-based generation services, subscriptions or paid hosted tools.**
4. **Do not select a paid local application/model/license without explicit new user approval. Default budget is zero.**
5. Internet access remains valid for research, documentation, source-code/model-weight discovery and downloading freely usable local components. Distribution/download hosting is not a runtime dependency.
6. A candidate is acceptable only if the production path remains usable without the external provider after installation/download.

## Consequence for current branch

The HeyGen Digital Twin / Avatar V branch is **retired as an invalid project route** because it is an external commercial hosted service. It must not be used for upload, training or rendering.

The locally prepared derivative:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\prepared\joao_heygen_digital_twin_primary_1080p_h264.mp4`

contains no external-service state and may be retained as a generic local 1080p H.264 behavioral-reference derivative. Its filename is historical only.

The three original behavioral videos remain the canonical source library and stay local.

## Next technical question

Select and validate a **local/self-hosted video-conditioned personalization route** that can consume João's real footage as behavioral identity, not merely a still image plus audio.

Required capabilities:

- use one or more real João videos as identity/performance reference;
- preserve visual identity;
- preserve or learn characteristic facial/head/body/gesture behavior;
- accept new speech/text/audio;
- generate new performance rather than replay a fixed driving clip;
- run locally on the current Windows 11 / RTX 3060 12 GB / 48 GB RAM machine, or use local CPU/RAM offload if runtime remains practical;
- zero paid-service dependency.

Do not resume static-image-only renderer optimization as a substitute for behavioral conditioning.