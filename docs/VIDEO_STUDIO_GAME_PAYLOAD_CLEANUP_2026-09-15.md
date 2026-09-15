# Video Studio — game-only local payload cleanup

Status date: **2026-09-15**  
Status: **ACTIVE CLEANUP POLICY**

## Decision

The Roguelite game is no longer an active objective. Local AI runtimes, checkpoints and working directories that existed only for game/sprite/character production should be removed when they have no plausible role in the current video-production architecture.

The cleanup is about reclaiming local disk space. Git history remains intact; rewriting repository history would add risk and would not materially help the `Z:\AI` storage problem.

## Safe delete set

The following roots are classified as game-only / retired and may be deleted completely:

- `Z:\AI\RogueliteAssetStudio`
- `Z:\AI\SpriteSheetDiffusionSpike`
- `Z:\AI\RogueliteCharacterPipeline`
- `Z:\AI\QwenImageEditSpike`
- `Z:\AI\Flux2RefControlSpike`

The last two are retired **spike runtimes**, not the active reusable image tools.

## Protected video / reusable set

Do not delete as part of game cleanup:

- `Z:\AI\WanAnimate2` — active Wan runtime; being reused for Wan2.2-S2V;
- `Z:\AI\MiniMaxH3` — video baseline/evidence and current João profile source assets;
- `Z:\AI\QwenImageEdit` — reusable for identity/look/scene still preparation;
- `Z:\AI\Flux2Klein` — reusable for identity/look/scene still preparation;
- `Z:\AI\FluxKontext` — general image/reference tool; not currently classified as game-only;
- `Z:\AI\VideoStudioRuns` — current project outputs and benchmark evidence.

General-purpose tools such as PowerPaint, LaMa or SDXL are **not** deleted by the first cleanup pass merely because they currently have no active role. They require a separate utility audit because they are not intrinsically game-only.

## Execution

Canonical script:

`tools/video-studio/cleanup_game_ai_payload.ps1`

Default execution is a dry run. It recursively measures the exact roots above and writes a report/JSON manifest under:

`tools/video-studio/reports/`

Actual deletion requires the explicit `-Execute` switch.

The script refuses paths outside `Z:\AI`, refuses to delete the AI root itself, and refuses game roots that are reparse points.

## Product focus after cleanup

The only active product is **personal video production**:

- João identity/profile assets;
- voice generation/reference;
- high-quality scene/look preparation;
- speech-driven video generation;
- renderer benchmarking;
- final video assembly and evidence.

Game-specific sprite, combat, character-layer, game-asset and game-runtime pipelines are historical only.
