#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def fail(msg: str) -> None:
    raise RuntimeError(msg)


def estimate_border_background(arr: np.ndarray) -> np.ndarray:
    border = np.concatenate([arr[0], arr[-1], arr[:, 0], arr[:, -1]], axis=0).astype(np.float32)
    return np.median(border, axis=0)


def connected_background_mask(arr: np.ndarray, threshold: float = 42.0) -> tuple[np.ndarray, list[float]]:
    bg = estimate_border_background(arr)
    diff = arr.astype(np.float32) - bg[None, None, :]
    dist = np.sqrt(np.sum(diff * diff, axis=2))
    candidate = (dist <= threshold).astype(np.uint8)
    count, labels = cv2.connectedComponents(candidate, connectivity=8)
    if count <= 1:
        fail("no connected background components")
    border_labels = set(np.unique(labels[0]).tolist()) | set(np.unique(labels[-1]).tolist())
    border_labels |= set(np.unique(labels[:, 0]).tolist()) | set(np.unique(labels[:, -1]).tolist())
    border_labels.discard(0)
    bgmask = np.zeros(labels.shape, dtype=bool)
    for label in border_labels:
        bgmask |= labels == label
    ratio = float(bgmask.mean())
    if not 0.20 <= ratio <= 0.97:
        fail(f"background extraction ratio out of range: {ratio:.4f}")
    return bgmask, [float(v) for v in bg.tolist()]


def bbox_from_alpha(alpha: np.ndarray):
    ys, xs = np.where(alpha > 0)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames-dir", required=True)
    ap.add_argument("--master", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--source-video", required=True)
    args = ap.parse_args()

    frames_dir = Path(args.frames_dir).resolve()
    master = Path(args.master).resolve()
    out_root = Path(args.output).resolve()
    source_video = Path(args.source_video).resolve()
    for path in (frames_dir, master, source_video):
        if not path.exists():
            fail(f"required input missing: {path}")

    frame_paths = sorted(frames_dir.glob("frame_*.png"))
    if len(frame_paths) < 17:
        fail(f"expected at least 17 Wan output frames, got {len(frame_paths)}")
    frame_paths = frame_paths[:16]

    out_root.mkdir(parents=True, exist_ok=True)
    rgba_dir = out_root / "frames_rgba"
    rgba_dir.mkdir(parents=True, exist_ok=True)

    rgba_frames = []
    rgba_paths = []
    extraction = []
    bboxes = []
    frame_w = frame_h = None
    for i, path in enumerate(frame_paths):
        arr = np.array(Image.open(path).convert("RGB"), dtype=np.uint8)
        h, w = arr.shape[:2]
        if frame_w is None:
            frame_w, frame_h = w, h
        if (w, h) != (frame_w, frame_h):
            fail("Wan frames have inconsistent dimensions")
        bgmask, bg_color = connected_background_mask(arr)
        alpha = np.where(bgmask, 0, 255).astype(np.uint8)
        rgba = np.dstack([arr, alpha])
        im = Image.fromarray(rgba, mode="RGBA")
        out = rgba_dir / f"frame_{i:03d}.png"
        im.save(out)
        rgba_frames.append(im)
        rgba_paths.append(str(out))
        bbox = bbox_from_alpha(alpha)
        bboxes.append(bbox)
        extraction.append({"index": i, "estimated_background_rgb": bg_color, "transparent_ratio": float(bgmask.mean()), "bbox": bbox})

    assert frame_w is not None and frame_h is not None
    columns, rows = 4, 4
    sheet = Image.new("RGBA", (frame_w * columns, frame_h * rows), (0, 0, 0, 0))
    for i, im in enumerate(rgba_frames):
        sheet.paste(im, ((i % columns) * frame_w, (i // columns) * frame_h), im)
    sheet_path = out_root / "exilada_initial_walk16_wan_complete_spritesheet.png"
    sheet.save(sheet_path)

    # Full-resolution review GIF on neutral background.
    preview_frames = []
    for im in rgba_frames:
        bg = Image.new("RGBA", im.size, (82, 78, 76, 255))
        bg.alpha_composite(im)
        preview_frames.append(bg.convert("RGB"))
    preview_path = out_root / "exilada_initial_walk16_wan_complete_preview.gif"
    preview_frames[0].save(preview_path, save_all=True, append_images=preview_frames[1:], duration=62, loop=0, disposal=2, optimize=False)

    # Gameplay-scale proof. A single scale from the tallest visible bbox is used
    # for all frames; no per-frame recentering/rescaling is allowed.
    visible_heights = [(b[3] - b[1] + 1) for b in bboxes if b]
    if not visible_heights:
        fail("no visible character bboxes after background extraction")
    max_h = max(visible_heights)
    scale = 128.0 / max_h
    scaled_w = max(1, round(frame_w * scale))
    scaled_h = max(1, round(frame_h * scale))
    game_frames = []
    for im in rgba_frames:
        sprite = im.resize((scaled_w, scaled_h), Image.Resampling.NEAREST)
        canvas = Image.new("RGBA", (640, 360), (31, 31, 34, 255))
        ground_y = 292
        from PIL import ImageDraw
        d = ImageDraw.Draw(canvas)
        d.rectangle((0, ground_y, 639, 359), fill=(49, 44, 39, 255))
        d.line((0, ground_y, 639, ground_y), fill=(105, 94, 80, 255), width=1)
        x = 320 - scaled_w // 2
        y = ground_y - scaled_h + round(54 * scale)
        canvas.alpha_composite(sprite, (x, y))
        game_frames.append(canvas.convert("RGB"))
    game_path = out_root / "exilada_initial_walk16_wan_gameplay_128px.gif"
    game_frames[0].save(game_path, save_all=True, append_images=game_frames[1:], duration=62, loop=0, disposal=2, optimize=False)

    metadata = {
        "gate": "G3S_WAN_ANIMATE2_COMPLETE_MOTION_SPRITESHEET_PROOF",
        "status": "PASS_OUTPUT_READY_FOR_VISUAL_QA",
        "character": "Exilada",
        "state": "initial",
        "reference_master": str(master),
        "source_wan_video": str(source_video),
        "complete_character_baked_per_frame": True,
        "runtime_character_layer_assembly": False,
        "frame_count": 16,
        "source_driver_frame_count": 17,
        "source_driver_closure_frame_dropped": True,
        "fps": 16,
        "frame_duration_ms": 62.5,
        "frame_size": [frame_w, frame_h],
        "layout": [columns, rows],
        "sheet": str(sheet_path),
        "preview_gif": str(preview_path),
        "gameplay_128px_preview_gif": str(game_path),
        "frames_rgba": rgba_paths,
        "background_extraction": extraction,
        "production_approved": False,
        "visual_qa_required": True,
    }
    metadata_path = out_root / "exilada_initial_walk16_wan_complete_spritesheet.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    print("G3S-WAN-COMPLETE-SPRITESHEET: PASS_OUTPUT_READY_FOR_VISUAL_QA")
    print(f"SHEET:    {sheet_path}")
    print(f"PREVIEW:  {preview_path}")
    print(f"GAMEPLAY: {game_path}")
    print(f"METADATA: {metadata_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"G3S-WAN-COMPLETE-SPRITESHEET: FAIL - {exc}")
        raise SystemExit(1)
