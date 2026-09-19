# Local Video Studio — Current Project State

Status date: **2026-09-18**

Purpose: canonical cross-chat operational handoff. GitHub living documents are the source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_PREFLIGHT_2026-09-18.md`
5. `docs/NEXT_CHAT_HANDOFF_VIDEO_STUDIO_LOCAL_BEHAVIOR_2026-09-18.md`
6. `docs/VIDEO_STUDIO_DIRECTION_RESET_2026-09-15.md`
7. `docs/VIDEO_STUDIO.md`
8. `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`
9. `docs/VIDEO_STUDIO_WAN_S2V_BENCHMARK_2026-09-15.md`
10. `docs/VIDEO_STUDIO_HUNYUAN_AVATAR_BENCHMARK_2026-09-15.md`
11. `docs/VIDEO_STUDIO_H3_VALIDATION_2026-09-15.md`
12. `docs/VIDEO_STUDIO_AVATAR_V_BENCHMARK_2026-09-18.md` — historical/retired external branch only

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

## Behavioral source library — INVENTORY + VISUAL REVIEW + PREFLIGHT PASS

Protected originals:

- `SIENA_BRUTO.mp4` — 113.3 s, 1080x1920, H.264 + audio;
- `VID_20260819_124008056.mp4` — 282.6 s, 1920x1080, H.264 + audio;
- `VID_20260911_140124885.mp4` — 300.4 s, 3840x2160, HEVC + audio.

Local source roles:

- `VID_20260911_140124885.mp4` — strongest primary upper-body behavioral source;
- `VID_20260819_124008056.mp4` — strongest close facial/microexpression source;
- `SIENA_BRUTO.mp4` — alternate motion/look source with useful gesture coverage but foreground-object occlusions.

The prepared 1080p H.264 derivative under the historical `avatar_v` path remains only a generic local copy. No external upload is authorized.

## Local behavioral-route research — DECISION 2026-09-18

TAVR is architecturally close to the desired `reference video + target scene + target audio` problem, but its official implementation requires Hopper-class CUDA with at least 80 GB VRAM and FlashAttention 3, so it is rejected for the RTX 3060 12 GB machine.

PersonaGesture/PersonaGest closely matches the desired personalized co-speech gesture problem but had no dependable public implementation/checkpoint for immediate use.

ZeroEGGS remains an actionable future R&D fallback but introduces a BVH/3D retargeting layer.

MimicTalk/Style-Talking are useful face/speaking-style branches, not complete upper-body solutions.

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
        +--> local lip-sync finishing later, if needed
        v
final video
```

The driving performance is not one fixed source clip. It is newly assembled from João's actual recorded behavioral vocabulary. The first gate uses prosody + pose continuity; semantic transcript matching can be added later.

## Behavior-profile implementation — STARTED 2026-09-18

The first implementation block now exists under `tools/video-studio/`:

- `inspect_local_behavior_tooling.ps1` — read-only, bounded local inspection for the real Python interpreter and reusable pose tooling. It does **not** download, install, delete or perform a blind full-drive crawl;
- `behavior_profile_schema_v1.json` — persistent `behavior-profile/v1` contract for source metadata, RGB spans, pose endpoints, head/hand/body activity, motion energy, speech/pause, available prosody and transition quality;
- `extract_behavior_profile.py` — first renderer-independent extractor for the primary source `VID_20260911_140124885.mp4`.

The extractor deliberately separates the low-dependency analysis layer from the pose backend:

- visual motion energy: low-resolution grayscale frame-difference analysis through local FFmpeg;
- prosody v1: local mono PCM RMS/dBFS, normalized energy and speech/pause segmentation;
- cut policy: pauses + low motion have priority, with short motion-unit target duration;
- outputs: inspectable `manifest.json` and `motion_units.csv`;
- pose input: normalized JSONL pose track, currently backend-agnostic;
- a run without pose is allowed only with the explicit diagnostic flag `--allow-missing-pose` and is marked `status=incomplete_pose`;
- **`incomplete_pose` is not a behavior-gate pass and must never be treated as one.**

This code does not run Wan-Animate-2 and does not install any new model.

The next local execution must first run `inspect_local_behavior_tooling.ps1`. Python and global pose-tool availability remain **UNRESOLVED UNTIL THAT MACHINE-LOCAL REPORT EXISTS**.

## No-download local preflight — PASS 2026-09-18 23:45

Canonical result: `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_PREFLIGHT_2026-09-18.md`.

Raw local report:

`tools/video-studio/reports/local_behavior_route_preflight_20260918_234516.txt`

Result:

```text
BEHAVIOR SOURCES: PASS
WAN-ANIMATE-2 PAYLOAD: PASS
WAN-ANIMATE-2 NATIVE CODE: PASS
POSE TOOLING: NOT FOUND UNDER WAN ROOT
NEXT ROUTE GATE: BUILD BEHAVIOR PROFILE WITHOUT NEW LARGE RENDERER DOWNLOAD
```

### Installed Wan-Animate-2 — REUSE PASS

- transformer: `Z:\AI\WanAnimate2\models\diffusion_models\wan_animate_2_bf16.safetensors` — 30.538 GiB;
- text encoder: `Z:\AI\WanAnimate2\models\text_encoders\umt5_xxl_fp16.safetensors` — 10.586 GiB;
- VAE: `Z:\AI\WanAnimate2\models\vae\Wan2_1_VAE_bf16.safetensors` — 0.236 GiB;
- native model code: `Z:\AI\WanAnimate2\comfy\ldm\wan\model_animate2.py`.

**No new large renderer download is justified.** VACE/Motion Mirror remains fallback only.

### Pose tooling gap

No DWPose whole-body model was found **under `Z:\AI\WanAnimate2`**. The preflight did not prove global absence under all `Z:\AI` roots.

The new `inspect_local_behavior_tooling.ps1` performs the required targeted/no-download search over likely existing AI runtimes. Its result, not the older Wan-root-only scan, decides whether a small pose dependency is actually missing.

If pose tooling is genuinely absent and a DWPose-class dependency is needed, exact file/source/license/size/destination must be enumerated before download.

### Python resolution warning

The older report printed:

`Python 3.11: PASS / C:\Python314\python.exe / 3.14.3`

This is inconsistent. Python 3.11 is **not validated** by that line.

The new strict inspector checks `sys.version_info` from the executable actually resolved by `py -3.11`, inventories explicit local candidates and refuses to label a candidate as Python 3.11 unless the interpreter itself reports `3.11`.

No Python installation/reinstallation has been authorized or performed.

### Disk pressure

At preflight time:

- Z: free: **22.32 GB**;
- Z: used: **424.80 GB**.

Retired reclaimable payload still present:

`Z:\AI\WanGP\ckpts\hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — **12.486 GiB**.

Do not delete it reflexively; it remains only the first obvious reclaimable large payload if a later storage requirement justifies cleanup.

## Wan2.2-S2V — DIAGNOSTIC BASELINE

20-step result:

**VISUAL IDENTITY PASS/NEAR-PASS / BEHAVIORAL IDENTITY NOT TESTED / PRODUCTION FAIL FOR THE ACTUAL PRODUCT.**

Reason: static image + audio gave the model no João behavior reference.

Do not return to prompt-only acting refinement as a substitute for behavioral conditioning.

## HunyuanVideo-Avatar — LOCAL PRACTICALITY FAIL

The 720x1280 / 129-frame / 30-step WanGP path timed out after about 3 hours at `0/30` because of severe transformer offload on RTX 3060 12 GB.

Classification:

**FUNCTIONAL RUNTIME PASS / NO VISUAL VERDICT / LOCAL PRACTICALITY FAIL.**

## H3 conclusion

**H3 LOCAL: FUNCTIONAL PASS / PRODUCTION VISUAL QUALITY FAIL / PAUSED AS FINAL RENDERER.**

## Lip-sync and voice — DEFERRED

MuseTalk/LatentSync remain deferred until body/head behavior survives the renderer gate.

CosyVoice or another local voice-clone/TTS stage remains separate and deferred for final integration. Existing local speech audio may be used to engineer the behavior compiler first.

## Quality gate — LOCKED

A production candidate must pass both visual quality and personal-performance quality. The human reviewer must be able to say:

> this does not merely look like João; it moves and reacts like João.

Generic presenter choreography, exaggerated expressions, plausible-but-uncharacteristic gestures or a different delivery rhythm are production failures even when facial identity is excellent.

## Immediate next action — LOCKED

Continue the first **behavior-profile / motion-unit extractor** gate. Schema and base extractor now exist; the machine-local environment must be resolved before pose integration.

Required order from this state:

1. run the versioned read-only `tools/video-studio/inspect_local_behavior_tooling.ps1` on the Windows machine;
2. record the exact interpreter reached by `py -3.11` and any verified Python 3.11 candidate;
3. reuse any whole-body/hand pose tooling found by the targeted local search;
4. only if no suitable local pose tooling exists, enumerate the smallest required dependency before any download;
5. connect the selected local pose backend to the normalized JSONL pose-track contract;
6. run `extract_behavior_profile.py` against `VID_20260911_140124885.mp4` with real pose data;
7. inspect `manifest.json` and `motion_units.csv`; only `status=complete` with credible pose/activity descriptors can pass this profile gate;
8. after profile validation, synthesize a new ~4–5 s driving performance from several João motion units;
9. only then run the short installed Wan-Animate-2 gate.

Do not download another large renderer. Do not install lip-sync tooling before behavior passes. Do not run Wan-Animate-2 yet.

Next-chat handoff: `docs/NEXT_CHAT_HANDOFF_VIDEO_STUDIO_LOCAL_BEHAVIOR_2026-09-18.md`.
