# Roguelite — Current Project State

Status date: **2026-09-08**

Purpose: canonical cross-chat operational handoff. GitHub living documents are source of truth.

## Read first

1. `docs/PROJECT_STATE.md`
2. `docs/VISUAL_DIRECTION.md`
3. `docs/G3S_COMPLETE_CHARACTER_MODEL_SCREENING_2026-09-07.md`
4. `docs/G3S_ANIMATION_ARCHITECTURE_LOCK.md`
5. `docs/ANIMATION_PIPELINE.md`
6. `docs/CHARACTERS.md`
7. `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`
8. `docs/H3_H0_RUNNER47_AUDIO_VAE_INTEGRATION_FAIL_2026-09-08.md`
9. `docs/NEXT_CHAT_HANDOFF_G3S_B3_2026-09-05.md`

## Living-document invariant — LOCKED

Every state-changing action updates the thematic docs, this file and the active handoff before completion is reported.

## Local paths — LOCKED

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- AI root: `Z:\AI`
- active MiniMax H3 workspace: `Z:\AI\MiniMaxH3`
- paused Wan workspace: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` is stale/historical.

## Runtime / game presentation — LOCKED

- elevated 2D arcade beat'em-up / belt-scroller / false 3D;
- fixed orthographic-like gameplay camera;
- native game raster `640×360`;
- pitch `26°`;
- protagonist about `128 px` tall;
- first locomotion family screen-left / mostly lateral-three-quarter;
- `72°` current screen-left baseline;
- runtime consumes **complete precomposed character sprites** only.

Production contract:

`complete appearance reference + raw driving video + automatic preprocessing -> complete animated frames -> automatic extraction/packing -> spritesheet/atlas + metadata -> ordinary sprite playback`

No routine manual rigging, keyframing, simulation repair, mask repair, repainting or hand compositing.

## Visual direction — LOCKED

- painterly / illustrated 2D dark fantasy;
- explicit 1980s sword-and-sorcery charge;
- Heavy Metal, Conan, Red Sonja, Frank Frazetta, Julie Bell lineage;
- adult sensuality/nudity legitimate;
- localized restrained blur may be positive;
- destructive blur/ghosting that erases anatomy/topology/readability is a defect;
- later Exilada art gate may use more severely torn cloth, more body exposure and possible partial breast exposure consistent with captivity/damage.

## Model-screening order — LOCKED 2026-09-08

1. **MiniMax H3 Base Ref2VA — ACTIVE / PASS_CANDIDATE after H0.**
2. Wan-Animate-2 — **PAUSED AFTER W1L**, not exhausted.
3. SCAIL-2 — later only if H3 fails a later production gate.

## Wan compact record

- W0 local BF16 integration passed with `--disable-pinned-memory`.
- W1 established the approved painterly/motion language.
- W1A ref1.5 improved apparent topology but increased ghosting under old geometry.
- W1F letterbox and W1G tracked/recentered framing are closed failures.
- W1H `512×912` with untouched raw driver solved dominant crop and became best documented Wan geometry baseline.
- W1I pose-end0.70 did not materially improve blur/structure.
- W1J/W1K prepared but never executed.
- W1L completed ref1.0 + pose0.80 +30 steps; Wan paused afterward. Preserve proof/results. No W1L visual verdict was invented without review.

## MiniMax H3 Ref2VA — ACTIVE

Canonical procedure:

`docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`

### Runner46 bootstrap

Runner46 successfully installed the dedicated pinned ComfyUI v0.34.0 environment and prepared the H0 inputs. Runner47 then exposed one omitted schema dependency: `MiniMaxH3ReferenceToVideo.audio_vae` is required even when the experiment has no audio reference or audio decode.

Runner47 classification: **INTEGRATION_FAIL / PRE-INFERENCE**. No `prompt_id`, no sampling, zero model-quality evidence.

Runner48 added the official schema-required audio VAE and kept every H0 quality variable unchanged.

### Correct minimal Ref2VA local set

- `minimax_h3_ref2va_pruned_int8_convrot.safetensors` (~21GB)
- `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` (~15.7GB)
- `minimax_h3_video_vae_fp16.safetensors` (~5.21GB)
- `minimax_h3_audio_vae_fp32.safetensors` — 605,254,808 bytes, SHA256 `8e505d95dd1561d47abd43d4238fd40d9bb1ae9e147ed0a4cba778d76ae4db48`

Correct active H3 payload: about **42.5GB**. Audio VAE is a schema dependency only; H0 used no audio reference and produced no audio output.

## H3 H0 / Runner48 — COMPLETE / PASS_CANDIDATE

Exact completed baseline:

- task: Base Ref2VA;
- Picture1: canonical Exilada master;
- Video1: same raw Wan comparison driver, timestamp-resampled only;
- `448×800`;
- 124 frames @24fps;
- `ref_image_size=match`;
- 50 steps;
- `res_multistep` + `beta`;
- seed0;
- sigma shifts video12/audio3;
- no FL2VA, no Turbo LoRA, no style embedding;
- no crop/resize/tracking/recentering of the driver.

Completion evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s` (~75m05s);
- output SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`;
- canonical video `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- gameplay proxy `Z:\AI\MiniMaxH3\h0_gameplay_scale_proxy_frame160.mp4`.

### Visual review verdict

The uploaded full H0 video and 90×160 gameplay proxy were reviewed frame-by-frame.

**PASS_CANDIDATE / FAMILY ADVANCES.**

Observed strengths:

- materially stable body topology across the 124 frames;
- no destructive whole-body ghosting/double-exposure smear of the kind that blocked Wan;
- face, torso, limbs, body proportions, hair mass and costume language remain highly coherent across the sequence;
- long hair and torn cloth show visible secondary response while staying attached;
- chains/restraints remain recognizably accessory geometry rather than turning into flesh/limbs;
- frames remain sharp enough that hands/feet/torso stay readable during motion;
- the painterly dark-fantasy result is strongly compatible with the locked art direction;
- at the ~128px gameplay use case the silhouette and pose remain clearly readable.

Residual defects / cautions:

- chain length/curve/attachment detail is not perfectly invariant; it still drifts somewhat frame to frame, though far less destructively than Wan;
- the character approaches the right canvas edge late in the clip and the right foot becomes partially cropped in the final portion. This is a **framing/driver-envelope issue**, not observed topology collapse;
- H0 proves internal temporal identity stability, but exact master-image fidelity should still be judged alongside the canonical reference when art finalization begins.

### Resolution decision

`448×800` **passes this screening gate**. Do not increase to `480×864`/`512×896` merely because higher resolution is available. The current source already survives the gameplay-scale reduction well. `ref_image_size=max` is also deferred because H0 does not show an obvious identity-collapse problem that justifies its extra cost.

## NEXT GATE — H3 H1 GAME-RELEVANT WALK DRIVER

The next H3 test is no longer another nearby H0 setting tweak. Use a real walking/performance video appropriate to the game:

- one adult subject;
- full body visible throughout;
- fixed camera;
- continuous take;
- leftward locomotion / mostly lateral or slight 3/4, targeting the locked `72°` screen-left baseline;
- at least one complete gait cycle;
- adequate head/feet/lateral margin so the driver itself does not force crop;
- costume/identity/body/hair of the performer are irrelevant;
- retain H0 quality baseline first: `448×800`, Base50, `res_multistep/beta`, seed0, `ref_image_size=match`.

Only after a game-relevant walk passes should we stress secondary dynamics/wind/restraints and then test faster production settings such as Turbo if needed.

## Throughput note

H0 took `4504.8s` for 124 frames (~36.3s/generated frame). This is not directly comparable to Wan because frame count/resolution/sampler differ, but it is acceptable for an offline quality baseline. Do not optimize speed before the game-relevant walk gate is proven.

## Manifest metadata correction

The uploaded H0 manifest contains legacy top-level `audio_vae: null` from the base executor, while its `integration_fix` block correctly records `minimax_h3_audio_vae_fp32.safetensors`. The repaired wrapper has now been corrected so future manifests write the schema-required audio VAE at top level as well. This metadata issue does not affect the completed H0 video.

## Cleanup

- H3 is now technically and visually proven active enough that immediate return to Wan is not required.
- Wan **large checkpoints may now be removed** to recover disk, while preserving W1L/W1H videos, prompts, manifests and logs.
- keep the four-file minimal H3 Ref2VA set while H3 remains active;
- do not accumulate FL2VA/Turbo/alternate quantizations until an explicit later hypothesis requires them;
- keep SSD comparison evidence until explicit abandonment/final model verdict.
