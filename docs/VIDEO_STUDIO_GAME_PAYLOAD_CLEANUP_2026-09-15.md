# Video Studio — game-only cleanup policy

Status date: **2026-09-15**  
Status: **ACTIVE CLEANUP POLICY**

## Decision

The Roguelite game is no longer an active objective. Anything that exists **only** for game/sprite/character production should be removed from the active local environment and from the repository working tree.

The only active product is **personal video production**.

Git history is intentionally preserved. Old Roguelite material does not remain in `main`, but can still be recovered from historical commits if ever needed.

## Local AI payload — safe delete set

The following roots are classified as game-only / retired and may be deleted completely:

- `Z:\AI\RogueliteAssetStudio`
- `Z:\AI\SpriteSheetDiffusionSpike`
- `Z:\AI\RogueliteCharacterPipeline`
- `Z:\AI\QwenImageEditSpike`
- `Z:\AI\Flux2RefControlSpike`

The last two are retired **spike runtimes**, not the active reusable image tools.

Canonical script:

`tools/video-studio/cleanup_game_ai_payload.ps1`

Default execution is a dry run. Actual deletion requires `-Execute`.

## Protected video / reusable local set

Do not delete as part of game cleanup:

- `Z:\AI\WanAnimate2` — active Wan runtime; being reused for Wan2.2-S2V;
- `Z:\AI\MiniMaxH3` — video baseline/evidence and current João profile source assets;
- `Z:\AI\QwenImageEdit` — reusable for identity/look/scene still preparation;
- `Z:\AI\Flux2Klein` — reusable for identity/look/scene still preparation;
- `Z:\AI\FluxKontext` — general image/reference tool; not currently classified as game-only;
- `Z:\AI\VideoStudioRuns` — current project outputs and benchmark evidence.

General-purpose tools such as PowerPaint, LaMa or SDXL are not part of the first delete set merely because they currently have no active role. They require a separate utility audit because they are not intrinsically game-only.

## Repository cleanup — ACTIVE

`main` should no longer carry the old game project as working-tree content.

Canonical repository cleanup tool:

`tools/video-studio/cleanup_repository_to_video_studio.ps1`

Keep policy after cleanup:

- `.gitignore`
- `README.md`
- `docs/PROJECT_STATE.md`
- `docs/VIDEO_STUDIO*.md`
- `tools/video-studio/**`

Everything else currently tracked in the old repository working tree is retired Roguelite-era material and is removed from `main` by the cleanup script.

This includes:

- `assets/**` game character/sprite assets;
- game design and gameplay documents;
- Exilada/character-layer documents;
- sprite/pixel-art logs and pipelines;
- old game-era runner logs;
- old non-Video-Studio tool directories.

The deletion is a normal Git commit, **not a history rewrite**. Therefore:

- the active checkout becomes focused on Video Studio;
- old material stops cluttering the current repository;
- historical commits still retain the game work.

The repository cleanup script is dry-run by default. `-Execute -Push` performs `git rm`, commits the cleanup and pushes `main` after checking that the branch is `main` and there are no tracked local modifications.

## Product focus after cleanup

The active repository exists only for:

- João identity/profile assets and their management;
- voice generation/reference;
- high-quality scene/look preparation;
- speech-driven video generation;
- renderer benchmarking;
- final video assembly, manifests and evidence.

Game-specific sprite, combat, character-layer, gameplay, game-asset and game-runtime pipelines are historical only.
