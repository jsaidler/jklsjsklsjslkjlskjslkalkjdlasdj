# Local Video Studio — canonical architecture

Status date: **2026-09-18**  
Status: **ACTIVE LOCAL BEHAVIOR-COMPILER IMPLEMENTATION / WAN-ANIMATE-2 RENDERER REUSE LOCKED**

Canonical cross-chat state: `docs/PROJECT_STATE.md`.
Canonical execution policy: `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`.
Canonical behavioral route: `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`.

## Objective

Create short realistic videos of João without requiring a new camera recording for each publication.

Normal input:

`written dialogue + target scene + optional clothing/framing`

Persistent profile input:

`visual identity references + behavioral video profile + voice reference`

Target output:

`high-quality vertical MP4 that looks like João, sounds like João and moves/expresses itself like João`

Target program duration is up to approximately one minute, eventually assembled from short shots.

## Non-negotiable identity model

The profile has three distinct identity channels:

1. **visual identity** — appearance;
2. **voice identity** — voice/tone/accent;
3. **behavioral identity** — expressions, gestures, head motion, posture and delivery rhythm learned/reused from João's actual footage.

A renderer that receives only a static image plus audio may be useful as a visual benchmark, but it cannot satisfy the product requirement if it invents generic body language.

The project must not confuse `natural motion` with `João's motion`.

## Execution policy — LOCKED

All active production stages must run **locally/self-hosted**.

- no external hosted avatar/generation platform;
- no cloud/SaaS inference API;
- no subscriptions, paid credits or paid hosted generation;
- no paid local tool/model/license unless explicitly approved by João before any cost;
- personal video/voice/identity material stays local;
- web access may be used to research and download free/local code, models and documentation.

## Architecture rule

The product is an orchestrator, not a wrapper around one specific model.

The first behavior implementation is now concrete:

```text
Local Video Studio
        |
        +-- persistent João visual identity
        |
        +-- persistent João behavioral profile
        |      +-- real João RGB source spans
        |      +-- whole-body / hand pose descriptors
        |      +-- head / hand / body activity
        |      +-- motion energy
        |      +-- speech / pause / prosody descriptors
        |      +-- transition-friendly motion units
        |
new local speech/audio
        |
        +-- prosody windows
        +-- motion-unit retrieval
        +-- pose-continuity scoring
        +-- diversity / repetition penalty
        +-- conservative timing adjustment
        |
        v
NEW driving performance composed from João motion units
        |
        v
installed local Wan-Animate-2
        |
        +-- local lip-sync finishing later, if needed
        +-- local voice-clone/TTS integration later
        v
final MP4
```

The driver is a conditioning representation, not the final product. It must be newly assembled from multiple units rather than simply replaying a fixed source clip.

## Canonical production route — LOCKED FOR FIRST GATE

Use the **behavioral driver synthesis** route documented in `VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`, with the already-installed **Wan-Animate-2** as the first renderer gate.

This replaces the older unresolved statement that a new renderer candidate still had to be selected.

Static-image + audio generation is not enough for the final product.

The HeyGen / Avatar V branch is retired because it violates the local-only / zero-cost execution policy. Its earlier documentation remains historical only and must not drive current work.

## Behavioral source library

Three original videos are preserved locally as the canonical behavioral library:

- `SIENA_BRUTO.mp4` — alternate motion/look material;
- `VID_20260819_124008056.mp4` — close facial/microexpression material;
- `VID_20260911_140124885.mp4` — strongest upper-body behavioral source and **first extractor target**.

A 1080p H.264 derivative was also prepared locally from the last source. It is a generic local reference derivative despite its historical HeyGen-oriented filename.

## Behavior-profile implementation

The first behavior-profile infrastructure is versioned under `tools/video-studio/`:

- `inspect_local_behavior_tooling.ps1` — strict read-only Python/pose inventory;
- `behavior_profile_schema_v1.json` — persistent schema;
- `extract_behavior_profile.py` — first source analyzer and motion-unit segmenter.

### Schema contract

`behavior-profile/v1` keeps, per motion unit:

- source file/time range and original RGB span;
- initial/final pose;
- head activity;
- left/right/combined hand activity;
- body activity;
- motion energy;
- speech/pause context;
- available prosody;
- transition quality.

### Current extractor boundary

The base extractor intentionally uses FFmpeg/ffprobe for media analysis and is independent of any particular pose library.

Without a real pose track it can be run only in explicit diagnostic mode and produces:

`status=incomplete_pose`

That status **cannot pass the behavior-profile gate**. A valid profile requires real pose descriptors from a selected local whole-body/hand backend.

### Local environment not yet resolved

The historical preflight's `Python 3.11: PASS / C:\Python314\python.exe / 3.14.3` line is invalid as proof of Python 3.11.

The new read-only inspector must run on the Windows machine before any Python pose dependency is selected. It also performs a bounded targeted search for reusable existing pose assets/runtimes before any download.

## Installed renderer state

Wan-Animate-2 reuse passed the 2026-09-18 local preflight:

- transformer: `Z:\AI\WanAnimate2\models\diffusion_models\wan_animate_2_bf16.safetensors` — 30.538 GiB;
- text encoder: `Z:\AI\WanAnimate2\models\text_encoders\umt5_xxl_fp16.safetensors` — 10.586 GiB;
- VAE: `Z:\AI\WanAnimate2\models\vae\Wan2_1_VAE_bf16.safetensors` — 0.236 GiB;
- native Animate-2 code: `Z:\AI\WanAnimate2\comfy\ldm\wan\model_animate2.py`.

No new large renderer download is justified before the behavior-profile gate.

## Wan2.2-S2V result and scope

Wan S2V was tested with static visual reference + speech audio.

It remains useful as historical evidence for visual likeness, anatomy stability, texture stability, lipsync and local runtime.

It does **not** validate behavioral identity because João's reference video was not used as behavior conditioning.

The reviewed 20-step result was visually close enough to João, but expressions and movements felt like another person and were caricatured.

Therefore do not resume prompt-only acting refinement as if it solved behavioral identity.

## H3 result and scope

MiniMax H3 remains a historical functional prototype and production visual-quality failure. Its autonomous motion is generic and therefore does not satisfy behavioral identity.

Do not resume H3 as the active renderer route.

## HunyuanVideo-Avatar local result

The local 720p / 129-frame / 30-step WanGP test timed out after about three hours at `0/30` because the RTX 3060 12 GB required severe block offload.

Classification:

**runtime functional / local quality path impractical / no visual verdict.**

Do not resume it as the next stage.

## Scene/look strategy

Do not require one model to solve identity, behavior, wardrobe, scene and voice simultaneously.

Preferred local route after behavioral identity passes:

1. persistent behavioral identity comes from the local behavior profile and composed driver;
2. visual look can come from a selected/generated local scene-specific look;
3. voice comes from the later local voice stage;
4. local renderer creates the performance;
5. multiple validated shots are assembled automatically.

## Existing orchestration prototype

`tools/video-studio/video_studio.py`, `index.html`, `config.example.json` and `start_video_studio.ps1` are the earlier H3-oriented prototype harness. They remain useful code/evidence but are **not the current production architecture**.

They must be refactored only after the short behavioral gate passes; there is no reason to spend time productizing the old H3 path now.

Longer-term adapter direction remains:

```text
RendererAdapter
  prepare_profile()
  prepare_motion_identity()
  submit_shot()
  poll()
  fetch_output()
  report_metadata()
```

## Development order — LOCKED

1. run the new read-only local tooling inspector;
2. resolve the actual Python interpreter and inventory reusable local pose tooling;
3. reuse existing whole-body/hand pose tooling if available;
4. if genuinely absent, specify the smallest required free/local dependency before any download;
5. produce a `status=complete` behavior profile for `VID_20260911_140124885.mp4`;
6. inspect the manifest/motion-unit inventory;
7. assemble a new ~4–5 s driver from several units using prosody + pose continuity + diversity;
8. run that short driver through the already-installed Wan-Animate-2;
9. approve/reject behavioral identity separately from visual identity;
10. only after a behavioral pass, integrate/finalize local voice and lip-sync;
11. then validate scene/look swaps;
12. only after a short-shot production pass, resume one-minute multi-shot automation.

Do not use an external paid service as a shortcut around local model limitations. Do not run Wan-Animate-2 before the complete behavior profile exists.