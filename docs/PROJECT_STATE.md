# Local Video Studio — Current Project State

Status date: **2026-09-18**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. `docs/VIDEO_STUDIO_DIRECTION_RESET_2026-09-15.md`
5. `docs/VIDEO_STUDIO.md`
6. `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`
7. `docs/VIDEO_STUDIO_WAN_S2V_BENCHMARK_2026-09-15.md`
8. `docs/VIDEO_STUDIO_HUNYUAN_AVATAR_BENCHMARK_2026-09-15.md`
9. `docs/VIDEO_STUDIO_H3_VALIDATION_2026-09-15.md`
10. `docs/VIDEO_STUDIO_AVATAR_V_BENCHMARK_2026-09-18.md` — historical/retired external branch only

## Living-document invariant — LOCKED

Every state-changing action updates the relevant thematic docs and this file. Changed decisions replace stale locks rather than coexisting ambiguously.

## Execution policy — LOCKED

The Video Studio is **local/self-hosted and zero-cost by default**.

Hard constraints:

- no external hosted generation/training/avatar platform;
- no SaaS/cloud inference API;
- no credit-based or subscription generation service;
- no paid tool/model/license unless João explicitly changes this rule in advance;
- do not upload João's personal video/voice/identity material to a third-party avatar/generation provider;
- internet use is allowed for research, documentation and downloading freely usable local code/model weights.

Canonical policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`.

The HeyGen Digital Twin / Avatar V route is **retired as invalid for this project**.

## Active objective — LOCKED

Build a local tool that lets João write dialogue, choose a scenario and optionally specify appearance/framing, then generate a realistic video of himself speaking the new text without recording a new performance.

A production pass requires three separate identities to remain João:

1. **visual identity** — face, body, glasses, beard, hair and overall appearance;
2. **voice identity** — cadence/timbre/accent from the local TTS/voice-clone stage;
3. **behavioral identity** — characteristic facial expressions, head movement, gesture language, posture and delivery rhythm learned/reused from João's actual video footage.

**Behavioral identity is a hard requirement. Generic plausible motion is not acceptable.**

Target program length: up to approximately one minute, eventually assembled from short shots.

## Behavioral source library — INVENTORY + VISUAL REVIEW PASS

Protected originals:

- `SIENA_BRUTO.mp4` — 113.313 s, 1080x1920, H.264 + AAC;
- `VID_20260819_124008056.mp4` — 282.574 s, 1920x1080, H.264 + AAC;
- `VID_20260911_140124885.mp4` — 300.352 s, 3840x2160, HEVC + AAC.

Local source roles:

- `VID_20260911_140124885.mp4` — strongest primary upper-body behavioral source;
- `VID_20260819_124008056.mp4` — strongest close facial/microexpression source;
- `SIENA_BRUTO.mp4` — alternate motion/look source with useful gesture coverage but foreground-object occlusions.

The prepared 1080p H.264 derivative under the historical `avatar_v` path remains only a generic local copy. No external upload is authorized.

## Local behavioral-route research — DECISION 2026-09-18

A monolithic open model that exactly matches the goal exists in research form: TAVR takes reference video + target scene + target audio, but its official local implementation requires a Hopper-class GPU with at least **80 GB VRAM** and FlashAttention 3. It is therefore rejected for the RTX 3060 12 GB machine.

Recent personalized gesture research such as PersonaGesture/PersonaGest closely matches the desired behavioral problem, but no dependable public implementation/checkpoint was found for immediate use.

ZeroEGGS is public and can generate speech-driven gestures in the style of example motion, but requires a 3D/BVH retargeting layer from João's videos. It remains an R&D fallback, not the first implementation.

MimicTalk and Style-Talking are useful personalized face/speaking-style branches, not complete upper-body gesture solutions.

Full research record: `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`.

## Selected local architecture — LOCKED FOR FIRST IMPLEMENTATION

The first implementation is a modular **behavioral driver synthesis** route:

```text
João behavioral videos
        |
        +--> local pose/prosody analysis
        +--> motion-unit library from João's own footage
        |
new local João speech audio
        |
        +--> prosody windows
        +--> retrieve João motion units
        +--> pose-continuity + diversity scoring
        +--> assemble a NEW João driving performance
        |
        +--> installed Wan-Animate-2 renderer
        |
        +--> local lip-sync finishing if needed
        v
final video
```

The driving performance is not one fixed source clip. It is newly assembled from João's actual recorded behavioral vocabulary. This deliberately avoids asking a generic model to invent João's gesture language.

Semantic transcript matching can be added later; the first gate uses prosody + pose continuity to test the core behavior-preservation hypothesis.

## Wan-Animate-2 — PRIORITY RENDERER REUSE

Current Wan-Animate-2 directly consumes a driving video and is designed to transfer the performer's movement and facial expression while preserving a reference character.

The project already has a large `wan_animate_2_bf16.safetensors` payload under `Z:\AI\WanAnimate2` from earlier work.

Therefore:

**DO NOT DOWNLOAD VACE/MOTION MIRROR OR ANOTHER LARGE RENDERER BEFORE AUDITING AND EXHAUSTING THE INSTALLED WAN-ANIMATE-2 ROUTE.**

Motion Mirror/Wan2.1-VACE remains a fallback. Its 1.3B backend can fit roughly 8–9 GB VRAM on Windows, but requires about another 20 GB model cache and explicitly trades away identity fidelity. It is not the next download.

## Lip-sync finishing — DEFERRED UNTIL BEHAVIOR GATE

Wan-Animate-2 will copy mouth/expression information from the synthesized driver, whose original mouth movement will not necessarily match the new audio.

A separate local lip-sync pass is therefore expected later.

Current candidates:

- MuseTalk 1.5 — Windows-supported, MIT code/model-use terms, tested on low-VRAM GPUs;
- LatentSync 1.5 — local audio-conditioned lip sync, about 8 GB minimum VRAM.

Do not download these yet. First prove that the body/head behavioral driver survives Animate-2.

## Voice stage

CosyVoice or another local voice-clone/TTS component remains separate and local. It will eventually supply the target audio analyzed by the behavior compiler and used by the lip-sync stage.

## Wan2.2-S2V — DIAGNOSTIC BASELINE

20-step result:

**VISUAL IDENTITY PASS/NEAR-PASS / BEHAVIORAL IDENTITY NOT TESTED / PRODUCTION FAIL FOR THE ACTUAL PRODUCT.**

Reason: static image + audio gave the model no João behavior reference.

## HunyuanVideo-Avatar — LOCAL PRACTICALITY FAIL

The 720x1280 / 129-frame / 30-step WanGP path timed out after about 3 hours at `0/30` because of severe transformer offload on RTX 3060 12 GB.

Classification:

**FUNCTIONAL RUNTIME PASS / NO VISUAL VERDICT / LOCAL PRACTICALITY FAIL.**

## H3 conclusion

**H3 LOCAL: FUNCTIONAL PASS / PRODUCTION VISUAL QUALITY FAIL / PAUSED AS FINAL RENDERER.**

## Quality gate — LOCKED

A production candidate must pass both visual quality and personal-performance quality. The human reviewer must be able to say:

> this does not merely look like João; it moves and reacts like João.

Generic presenter choreography, exaggerated expressions, plausible-but-uncharacteristic gestures or a different delivery rhythm are production failures even when facial identity is excellent.

## Immediate next action — LOCKED

Run the no-download preflight:

`tools/video-studio/preflight_local_behavior_route.ps1`

It must determine before any installation/download:

1. whether the existing `wan_animate_2_bf16.safetensors` payload is still present;
2. whether the local ComfyUI runtime already contains native `model_animate2.py` support;
3. whether DWPose/whole-body pose tooling is already reusable locally;
4. whether the three behavioral originals are intact;
5. current GPU/driver/Python/free-disk state;
6. whether any retired Hunyuan payload remains reclaimable if later storage is required.

The preflight performs **no downloads, no installs and no deletions**.

If Animate-2 payload + native runtime + behavioral source library pass, the next coding step is to build the local behavior-profile/motion-unit extractor. No new large renderer download is allowed before this gate.
