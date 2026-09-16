# Local Video Studio — HunyuanVideo-Avatar direct comparison

Date: **2026-09-16**  
Status: **PAYLOAD PREPARED / DRY-RUN PASS / DIRECT RENDER READY / WAN 20-STEP A/B PAUSED**

Canonical state: `docs/PROJECT_STATE.md`.

## Decision

After the first Wan2.2-S2V render, do **not** spend another ~1 hour on the 20-step Wan A/B before seeing whether a stronger avatar renderer can beat it.

The next comparison target is **HunyuanVideo-Avatar** using the same João reference image and the same recorded 4.5 s speech audio.

The Wan 20-step path is **paused, not rejected**. If Hunyuan is worse, return to Wan and run the proper 20-step quality baseline.

## Runtime strategy

Use:

**DeepBeepMeep WanGP -> Hunyuan Video Avatar 720p 13B -> quantized INT8 payload**.

WanGP is the practical implementation route for Windows 11 + RTX 3060 12 GB.

Runtime bootstrap validated on 2026-09-15:

- Python 3.11.14;
- Torch 2.10.0+cu130;
- CUDA 13.0 available;
- RTX 3060 detected;
- WanGP local footprint: **7.4 GB**.

## Payload preparation — PASS

Successful preparation run:

- report: `D:\GOOGLE DRIVE\DEV\Roguelite\tools\video-studio\reports\hunyuan_avatar_prepare_20260915_234228.txt`;
- manifest: `Z:\AI\WanGP\hunyuan_avatar_benchmark_prepare_manifest.json`;
- downloaded files: **26**;
- reused files: **0**;
- free space on `Z:` after payload: **40.63 GB**.

Validated critical payload:

- `hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — **12.486 GB** — PASS;
- `llava-llama-3-8b/llava-llama-3-8b-v1_1_vlm_quanto_int8.safetensors` — **8.785 GB** — PASS;
- `clip_vit_large_patch14/model.safetensors` — **1.593 GB** — PASS;
- `whisper-tiny/model.safetensors` — **0.141 GB** — PASS;
- `det_align/detface.pt` — **0.174 GB** — PASS;
- `hunyuan_video_custom_VAE_fp32.safetensors` — **0.918 GB** — PASS;
- `hunyuan_video_custom_VAE_config.json` — PASS.

Important correction retained: **Hunyuan Avatar uses the custom Hunyuan VAE**, not only the standard Hunyuan VAE.

Canonical preparation classification:

**HUNYUAN AVATAR: RUNTIME PASS / PAYLOAD PREPARED / DRY-RUN PASS / DIRECT RENDER READY.**

## Direct comparison inputs — LOCKED

Reuse exactly the Wan benchmark source assets:

- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_ref.png`
- `Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_test_4p5s.wav`

Pinned WanGP copies:

- `Z:\AI\WanGP\inputs\video_studio\hunyuan_avatar_benchmark\joao_hunyuan_avatar_ref.png`
- `Z:\AI\WanGP\inputs\video_studio\hunyuan_avatar_benchmark\joao_hunyuan_avatar_test_4p5s.wav`

Do not introduce CosyVoice yet. Do not change João's identity reference between engines. Do not upscale, face-retouch or otherwise post-process the first Hunyuan render in a way that hides renderer defects.

## WanGP programmatic interface verification — PASS

The current upstream WanGP interface was re-verified before creating the runner. The supported automation path is **not browser/Gradio automation** and does not require reverse-engineering an internal callback.

WanGP exposes `shared/api.py` with the supported single-task flow:

- `from shared.api import init`;
- `session = init(...)`;
- `session.list_model_metadata(...)` for model discovery;
- `session.get_default_settings(model_type)`;
- `session.get_model_schema(model_type)`;
- `session.get_model_availability(model_type)`;
- `session.submit_task(settings)`;
- `job.result()` for the structured result.

WanGP also supports `wgp.py --process settings.json`, but the Python API is preferable here because the benchmark runner can inspect the **installed runtime's** current model definition/defaults before submitting an expensive render.

The current WanGP settings contract confirms:

- reference image: `image_refs`;
- Hunyuan Avatar reference mode: `video_prompt_type="KI"`;
- primary speech audio: `audio_guide`;
- audio mode: `audio_prompt_type="A"`;
- output shape: `resolution`;
- frames: `video_length`;
- sampling: `num_inference_steps`, `guidance_scale`, `flow_shift`, `seed`;
- acceleration cache: `skip_steps_cache_type`, with empty string disabling TeaCache/MagCache.

The Hunyuan handler currently declares:

- architecture/base model type `hunyuan_avatar`;
- **25 fps**;
- `any_audio_prompt=True` and `returns_audio=True`;
- one image reference required;
- reference role `KI` (“Start Image”);
- default **129 frames**;
- guidance **7.5**;
- flow shift **5**;
- background removal off;
- 128-frame internal segment processing even if a shorter output is requested.

The common WanGP quality default remains **30 inference steps** for this model because the Avatar handler does not override `num_inference_steps`.

## First runner attempt — STOPPED BEFORE INFERENCE

On 2026-09-16 the first execution reached WanGP initialization and stopped immediately with:

```text
wgp.py: error: unrecognized arguments: --teacache 0
```

This is a **runner/CLI compatibility error, not a Hunyuan renderer failure**. No model inference was submitted and no Hunyuan quality verdict exists yet.

Cause: the runner incorrectly passed `--teacache 0` as a WanGP startup CLI option. The installed/current WanGP startup parser does not expose that flag. TeaCache belongs to task settings through `skip_steps_cache_type`; an empty string disables step-skipping cache.

Patch applied in repository commit `7d77ce33c0d21b5259b8d21a2f8b95caf521197c`:

- removed `--teacache 0` from `shared.api.init(..., cli_args=...)`;
- retained `--profile 4` and `--attention sdpa` as supported startup flags;
- retained `skip_steps_cache_type=""` in the submitted task settings;
- manifest now records TeaCache as disabled through task settings rather than as a nonexistent CLI switch.

## Compatibility dry-run — PASS

The patched runner completed a zero-inference dry-run on 2026-09-16.

Evidence root:

`Z:\AI\VideoStudioRuns\hunyuan-avatar-gates\20260916_003617`

Validated directly against the installed WanGP runtime:

- WanGP v13.02 initialized successfully;
- profile 4 + SDPA initialized successfully;
- Hunyuan Avatar model discovery: **PASS**;
- model type: `hunyuan_avatar`;
- payload availability: `available`;
- reference mode: `KI`;
- audio mode: `A`;
- runtime default frames: **129**;
- runtime default steps: **30**;
- runtime default CFG: **7.5**;
- runtime default flow shift: **5**;
- dry-run result: **PASS — no generation submitted**.

The runtime also downloaded its own FFmpeg 9.0.1 essentials package during initialization. This was runtime setup activity, not model generation.

This closes the API/schema compatibility gate. There is no remaining reason to spend another preparation pass before the first renderer inference.

## First direct gate — LOCKED

Repository runner:

- `tools/video-studio/run_hunyuan_avatar_benchmark.ps1`
- `tools/video-studio/run_hunyuan_avatar_benchmark.py`

The first production-oriented gate is intentionally **720x1280 portrait**, not the lower-pixel Wan test resolution. The question is whether Hunyuan can deliver a publishable local result at its intended 720p class, not whether two engines produce identical pixel counts.

Locked first-run settings:

- Hunyuan Video Avatar 720p 13B;
- INT8 transformer/text encoder payload already prepared;
- 720x1280 portrait;
- 129 frames;
- native 25 fps;
- 30 steps;
- CFG 7.5;
- flow shift 5;
- seed 0;
- WanGP profile 4;
- SDPA attention for compatibility and to avoid an attention-backend quality confound;
- TeaCache disabled through `skip_steps_cache_type=""`;
- no temporal/spatial upscaling;
- no film grain;
- no audio post-processing;
- same 4.5 s real speech audio and same identity reference as Wan.

The runner first checks the local payload and `shared/api.py`, initializes WanGP, discovers the Avatar model by metadata, reads the installed defaults/schema/availability, validates that the installed runtime still exposes an image-reference mode containing `I` and an audio mode containing `A`, and only then submits generation.

Evidence root:

`Z:\AI\VideoStudioRuns\hunyuan-avatar-gates\<timestamp>\`

Expected evidence includes:

- `settings.json`;
- `model_search.json`;
- `model_metadata.json`;
- `model_defaults.json`;
- `model_schema.json`;
- `model_availability.json`;
- `runner.log`;
- `result.json` after inference;
- `manifest.json`;
- the generated video plus a stable benchmark copy.

The runner has a 180-minute watchdog by default and requests WanGP cancellation if that ceiling is reached. A timeout is a practicality failure for this local route, not an invitation to keep waiting blindly.

## Quality gate

The first render answers only:

> Is HunyuanVideo-Avatar materially closer to publishable João video than the completed Wan 10-step render?

Evaluate:

1. effective detail/resolution;
2. identity stability;
3. glasses/eyes/beard/hair;
4. mouth/teeth/jaw;
5. hands/arms/shoulders;
6. skin/clothing temporal stability;
7. naturalness of body performance;
8. AV sync;
9. runtime practicality;
10. overall publishability without manual repair.

## Decision after Hunyuan render

- **If Hunyuan clearly beats Wan 10-step:** promote Hunyuan and then integrate CosyVoice.
- **If Hunyuan is roughly tied:** compare runtime and resolution headroom before choosing.
- **If Hunyuan is worse:** stop Hunyuan tuning and return immediately to the controlled Wan 20-step FP8 A/B.
- **If Hunyuan OOMs or exceeds the runtime ceiling:** treat local practicality as failed and evaluate hosted/rented-GPU execution before destructive quality compromises.

Do not keep changing models without completing this controlled comparison.

## Immediate action

Preparation and compatibility validation are complete. **Do not rerun payload preparation or the dry-run.**

Next: pull `main` and execute exactly one full direct Hunyuan Avatar benchmark with the locked settings. No Hunyuan renderer result has been produced yet.
