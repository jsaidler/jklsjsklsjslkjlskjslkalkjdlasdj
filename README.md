# Local Video Studio

This repository has been repurposed from the former Roguelite project.

The active objective is now a **local text-to-video studio** that generates short vertical videos of the user from written dialogue and a chosen scenario while preserving their visual identity and voice. Normal production runs locally on the existing Windows 11 / RTX 3060 12 GB setup through MiniMax H3 Ref2VA and ComfyUI.

Current validated relation:

```text
cropped identity references + voice reference + new text + target scene
→ MiniMax H3 Ref2VA
→ new talking video with autonomous motion and native generated audio
```

The user should not need to operate ComfyUI graphs for routine generation.

## Start here

Canonical state:

`docs/PROJECT_STATE.md`

Architecture:

`docs/VIDEO_STUDIO.md`

Validation record:

`docs/VIDEO_STUDIO_H3_VALIDATION_2026-09-15.md`

Active tool:

`tools/video-studio/`

On the current Windows installation:

```powershell
.\tools\video-studio\start_video_studio.ps1
```

Historical Roguelite/game documents and tools remain in the repository as evidence but are no longer canonical project direction.
