# Local Video Studio — canonical architecture

Status date: **2026-09-18**  
Status: **ACTIVE ORCHESTRATION PROTOTYPE / PERSONAL-AVATAR BENCHMARK NEXT**

Canonical cross-chat state: `docs/PROJECT_STATE.md`.

## Objective

Create short realistic videos of João without requiring a new camera recording for each publication.

Normal input:

`written dialogue + target scene + optional clothing/framing`

Persistent profile input:

`visual identity references + behavioral video reference(s) + voice reference`

Target output:

`high-quality vertical MP4 that looks like João, sounds like João and moves/expresses itself like João`

Target program duration is up to approximately one minute, eventually assembled from short shots.

## Non-negotiable identity model

The profile has three distinct identity channels:

1. **visual identity** — appearance;
2. **voice identity** — voice/tone/accent;
3. **behavioral identity** — expressions, gestures, head motion, posture and delivery rhythm learned from João's actual footage.

A renderer that receives only a static image plus audio may be useful as a visual benchmark, but it cannot satisfy the product requirement if it invents generic body language.

The project must not confuse `natural motion` with `João's motion`.

## Architecture rule

The product is an **orchestrator**, not a wrapper around one specific model.

```text
Local Video Studio UI
        |
        v
persistent João profile
  visual identity/look references
  behavioral motion/reference video
  voice reference
        |
new script + scene + appearance + framing
        |
        +-- voice stage
        |      +-- final candidate still open; CosyVoice remains a local option
        |
        +-- optional scene/look preparation
        |      +-- Qwen / FLUX / future image backend
        |
        +-- personal-avatar render adapter
        |      +-- HeyGen Avatar V / Digital Twin — next production benchmark
        |      +-- Avatar IV Digital Twin — fallback
        |      +-- Wan2.2-S2V — local visual/structural baseline only
        |      +-- H3 — historical research baseline
        |      +-- HunyuanVideo-Avatar local — practicality fail on 12 GB
        |
        +-- evidence / timing / metadata
        +-- final assembly / captions
        v
final MP4
```

## Canonical production route

The direction recorded in `docs/VIDEO_STUDIO_DIRECTION_RESET_2026-09-15.md` is restored and locked:

> use a personal-avatar renderer trained/conditioned from João's actual footage.

The immediate benchmark is **HeyGen Avatar V / Digital Twin**.

Current official HeyGen material states that Avatar V learns a person's specific gestures, expressions and mannerisms from short reference video footage and can then generate new scripts while retaining that learned motion identity. This directly matches the missing requirement exposed by the Wan test.

References:

- `https://help.heygen.com/en/articles/14602974-avatar-v-is-now-available-on-heygen`
- `https://help.heygen.com/en/articles/14602997-how-to-get-the-best-results-with-avatar-v-in-heygen`
- `https://www.heygen.com/avatars/avatar-v`

## Existing footage

Existing João video footage is behavioral training/reference material, not merely a source from which to crop stills.

For the first Avatar V benchmark:

- use one uninterrupted segment with normal João delivery;
- keep face, upper body and characteristic gestures visible;
- preserve speaking audio in the reference footage;
- prefer a segment of at least about 15 seconds for Avatar V;
- do not fabricate a new performance reference unless existing footage is technically rejected or behaviorally unrepresentative.

The benchmark script must be **new text not spoken in the reference footage**. Otherwise the test cannot prove that the model learned a reusable behavioral identity rather than merely reproducing familiar motion.

## Wan2.2-S2V result and scope

Wan S2V was tested with static visual reference + speech audio.

That test remains useful for:

- visual likeness;
- anatomy stability;
- texture stability;
- lipsync;
- local runtime practicality.

It does **not** validate behavioral identity because João's reference video was not used as motion conditioning.

The reviewed 20-step result on 2026-09-18 was visually close enough to João, but expressions and movements felt like another person and were described as caricatured.

Therefore:

**Wan S2V is not the next product route. Do not spend more time on 720p, prompt-based acting control or extra sampling before the personal-avatar benchmark.**

## HunyuanVideo-Avatar local result

The local 720p / 129-frame / 30-step WanGP test timed out after about three hours at `0/30` because the RTX 3060 12 GB required severe block offload.

Classification:

**runtime functional / local quality path impractical / no visual verdict.**

## Scene/look strategy

Do not require one model to solve identity, behavior, wardrobe, scene and voice simultaneously.

Preferred route after the personal avatar passes:

1. persistent behavioral identity comes from the trained/video-conditioned avatar;
2. visual look can come from a selected/generated scene-specific look;
3. voice comes from the voice stage;
4. avatar renderer creates the performance;
5. multiple validated shots are assembled automatically.

This preserves behavior while allowing wardrobe and environment changes.

## Existing implementation

`tools/video-studio/` already provides orchestration infrastructure such as profile handling, shot splitting, serial jobs, FFmpeg assembly, manifests and evidence.

Refactor target:

```text
RendererAdapter
  prepare_profile()
  prepare_motion_identity()
  submit_shot()
  poll()
  fetch_output()
  report_cost_and_metadata()
```

The profile schema must make behavioral video explicit rather than optional/implicit.

## Development order — LOCKED

1. create/test João's Avatar V Digital Twin using existing footage;
2. generate a short new-script benchmark;
3. approve/reject **behavioral identity** separately from visual identity;
4. only if it passes, integrate Avatar V as a renderer adapter;
5. then finalize the voice/TTS stage;
6. then validate scene/look swaps without losing motion identity;
7. only after a short-shot production pass, resume one-minute multi-shot automation.

Do not return to generic local renderer tuning until the personal-avatar route has been tested.