# Next-chat handoff — G3S complete-character spritesheet production

Status date: **2026-09-08**

GitHub living docs are canonical.

## Paths

- repo: `D:\GOOGLE DRIVE\DEV\Roguelite`
- active H3: `Z:\AI\MiniMaxH3`
- paused Wan: `Z:\AI\WanAnimate2`
- SSD comparison retained: `Z:\AI\SpriteSheetDiffusionSpike`
- `D:\AI` invalid/stale.

## Production contract

Complete Exilada appearance reference + arbitrary real driving video -> complete generated character frames -> automatic extraction/downsample/packing -> spritesheet. No routine manual rigging/keyframing/sim repair/mask repair/repainting/compositing.

## Art direction

Painterly illustrated 2D dark fantasy with explicit 1980s sword-and-sorcery charge: Heavy Metal, Conan, Red Sonja, Frank Frazetta, Julie Bell. Adult sensuality/nudity legitimate. Localized blur can be positive; destructive ghosting/anatomy loss is not.

## Wan — PAUSED

W1H remains the best documented Wan geometry baseline. W1I did not materially fix blur/structure. W1L completed ref1.0 + pose0.80 +30 steps. Preserve W1H/W1L videos/prompts/manifests/logs. H3 has now progressed far enough that Wan large checkpoints may be cleaned when convenient.

## MiniMax H3 Base Ref2VA — ACTIVE / PASS_CANDIDATE

Canonical procedure: `docs/MINIMAX_H3_REF2VA_LOCAL_SPIKE_2026-09-08.md`.

Runner47 incident: missing required `audio_vae`, classified pre-inference integration only. Runner48 repaired it without changing quality settings.

Minimal active H3 set:

- Ref2VA pruned INT8 ConvRot diffusion ~21GB;
- Qwen3-VL NVFP4 AWQ encoder ~15.7GB;
- video VAE ~5.21GB;
- schema-required audio VAE ~605MB.

Total ~42.5GB. No FL2VA/Turbo/style/alternate quantization installed.

## H0 / Runner48 — COMPLETE

Exact baseline:

- Picture1 = canonical Exilada;
- Video1 = same raw Wan comparison driver, timestamp-resampled only;
- `448×800`;
-124f @24fps;
- `ref_image_size=match`;
-50 steps;
- `res_multistep/beta`;
- seed0;
- no crop/resize/tracking/recentering;
- no audio reference/decode;
- no Turbo.

Evidence:

- prompt id `e5cf1c97-3ca6-4d5d-9411-641bc58cd464`;
- elapsed `4504.8s`;
- video `Z:\AI\MiniMaxH3\h0_exilada_ref2va_448x800_124f_base50.mp4`;
- SHA256 `ccdd4df03674ee325b6302f18e24b210ee3666ff2eb5f19dfa0877d647f93dd3`;
- gameplay proxy `Z:\AI\MiniMaxH3\h0_gameplay_scale_proxy_frame160.mp4`.

## H0 visual verdict

**PASS_CANDIDATE / H3 FAMILY ADVANCES.**

Frame-by-frame review of the uploaded output found:

- materially stable body topology through124 frames;
- no destructive global blur/ghost body;
- stable face/torso/limbs/body proportions/hair/costume language;
- long hair and torn cloth show secondary motion while staying attached;
- restraints remain accessory geometry;
- sharp readable anatomy during motion;
- excellent fit with the locked painterly dark-fantasy direction;
- gameplay-scale silhouette remains clear near the ~128px target.

Residuals:

- chains still drift somewhat in curve/length/attachment detail;
- late in the clip the right foot is partially cropped at the right frame edge; classify as driver/framing envelope, not topology collapse.

`448×800` therefore passes; do not raise resolution or switch to `ref_image_size=max` without new evidence.

## CURRENT NEXT GATE — H1 GAME-RELEVANT WALK

Do not run another nearby H0 configuration tweak.

Select/use a real walking driver with:

- one adult performer;
- full body visible throughout;
- fixed camera;
- continuous take;
- screen-left locomotion;
- mostly lateral/slight3/4, targeting locked `72°` facing;
- at least one complete gait cycle;
- safe head/feet/lateral margins;
- performer identity/costume/body/hair irrelevant.

Keep successful H0 quality settings for the first H1:

- `448×800`;
- Base50;
- `res_multistep/beta`;
- seed0;
- `ref_image_size=match`.

H1 pass requires a complete usable gait with H0-level topology, hair/cloth/restraint response and readable gameplay-scale silhouette.

After H1: secondary-motion/wind/restraint stress. Speed/Turbo only after quality is locked.

## Manifest note

The uploaded completed H0 manifest shows legacy top-level `audio_vae:null`, while its `integration_fix` block records the actual required audio VAE. The repaired wrapper has been corrected so future manifests populate the top-level field too. No rerun is needed for this metadata-only issue.

## Cleanup

- keep minimal H3 four-file set;
- paused Wan large checkpoint weights may now be removed, preserving W1H/W1L proof/results;
- do not accumulate H3 FL2VA/Turbo/alternate quantizations until a specific later hypothesis requires them;
- keep SSD comparison evidence until explicit abandonment/final verdict.
