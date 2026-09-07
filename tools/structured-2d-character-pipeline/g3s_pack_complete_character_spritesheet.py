#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def fail(message: str) -> None:
    raise RuntimeError(message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def estimate_border_background(arr: np.ndarray) -> np.ndarray:
    top = arr[0, :, :]
    bottom = arr[-1, :, :]
    left = arr[:, 0, :]
    right = arr[:, -1, :]
    border = np.concatenate([top, bottom, left, right], axis=0).astype(np.float32)
    return np.median(border, axis=0)


def connected_background_mask(arr: np.ndarray, threshold: float = 34.0) -> tuple[np.ndarray, list[float]]:
    bg = estimate_border_background(arr)
    diff = arr.astype(np.float32) - bg[None, None, :]
    dist = np.sqrt(np.sum(diff * diff, axis=2))
    candidate = (dist <= threshold).astype(np.uint8)

    count, labels = cv2.connectedComponents(candidate, connectivity=8)
    if count <= 1:
        fail("background candidate has no connected components")

    border_labels = set(np.unique(labels[0, :]).tolist())
    border_labels.update(np.unique(labels[-1, :]).tolist())
    border_labels.update(np.unique(labels[:, 0]).tolist())
    border_labels.update(np.unique(labels[:, -1]).tolist())
    border_labels.discard(0)

    background = np.zeros(labels.shape, dtype=bool)
    for label in border_labels:
        background |= labels == label

    ratio = float(background.mean())
    if not 0.30 <= ratio <= 0.95:
        fail(f"background extraction ratio out of safety range: {ratio:.4f}")
    return background, [float(v) for v in bg.tolist()]


def main() -> int:
    if len(sys.argv) != 2:
        fail("usage: g3s_pack_complete_character_spritesheet.py <request.json>")

    req_path = Path(sys.argv[1]).resolve()
    req = read_json(req_path)

    result_marker = Path(req["result_marker"]).resolve()
    alignment_marker = Path(req["alignment_marker"]).resolve()
    output_root = Path(req["output_root"]).resolve()
    metadata_path = Path(req["metadata_path"]).resolve()
    master = Path(req["master"]).resolve()
    frame_duration_ms = int(req.get("frame_duration_ms", 83))

    for path in (result_marker, alignment_marker, master):
        if not path.is_file():
            fail(f"required spritesheet input missing: {path}")

    result = read_json(result_marker)
    alignment = read_json(alignment_marker)
    if result.get("status") != "PASS_OUTPUT_READY_FOR_VISUAL_QA":
        fail("SSD result marker is not ready for visual QA")
    if alignment.get("status") != "PASS":
        fail("pose-alignment marker is not PASS")

    frames = [Path(p).resolve() for p in result.get("frames", [])]
    if len(frames) != 8 or any(not p.is_file() for p in frames):
        fail("expected exactly eight generated complete-character frames")

    events = [str(row.get("event")) for row in alignment.get("poses", [])]
    if len(events) != 8:
        fail("alignment marker does not contain eight pose events")

    ref_bbox = alignment.get("reference_pose_bbox")
    if not isinstance(ref_bbox, list) or len(ref_bbox) != 4:
        fail("alignment marker reference bbox missing")
    pivot_x = (float(ref_bbox[0]) + float(ref_bbox[2])) * 0.5
    pivot_y = float(ref_bbox[3])

    output_root.mkdir(parents=True, exist_ok=True)
    rgba_dir = output_root / "frames_rgba"
    rgba_dir.mkdir(parents=True, exist_ok=True)

    rgba_frames: list[Image.Image] = []
    rgba_paths: list[str] = []
    extraction: list[dict] = []

    frame_w = frame_h = None
    for i, path in enumerate(frames):
        arr = np.array(Image.open(path).convert("RGB"), dtype=np.uint8)
        h, w = arr.shape[:2]
        if frame_w is None:
            frame_w, frame_h = w, h
        if (w, h) != (frame_w, frame_h):
            fail("generated frame dimensions are inconsistent")

        background, bg_color = connected_background_mask(arr)
        alpha = np.where(background, 0, 255).astype(np.uint8)
        rgba = np.dstack([arr, alpha])
        im = Image.fromarray(rgba, mode="RGBA")
        out = rgba_dir / f"frame_{i+1:03d}_{events[i]}.png"
        im.save(out)
        rgba_frames.append(im)
        rgba_paths.append(str(out))
        extraction.append({
            "index": i,
            "event": events[i],
            "estimated_background_rgb": bg_color,
            "transparent_ratio": float(background.mean()),
        })

    assert frame_w is not None and frame_h is not None
    columns, rows = 4, 2
    sheet = Image.new("RGBA", (frame_w * columns, frame_h * rows), (0, 0, 0, 0))
    frame_records = []
    for i, im in enumerate(rgba_frames):
        x = (i % columns) * frame_w
        y = (i // columns) * frame_h
        sheet.paste(im, (x, y), im)
        frame_records.append({
            "index": i,
            "event": events[i],
            "rect": [x, y, frame_w, frame_h],
            "pivot": [pivot_x, pivot_y],
            "duration_ms": frame_duration_ms,
        })

    sheet_path = output_root / "exilada_initial_walk8_complete_spritesheet.png"
    sheet.save(sheet_path)

    preview_bg = (80, 76, 74, 255)
    preview_frames = []
    for im in rgba_frames:
        bg = Image.new("RGBA", im.size, preview_bg)
        bg.alpha_composite(im)
        preview_frames.append(bg.convert("RGB"))
    gif_path = output_root / "exilada_initial_walk8_complete_spritesheet_preview.gif"
    preview_frames[0].save(
        gif_path,
        save_all=True,
        append_images=preview_frames[1:],
        duration=frame_duration_ms,
        loop=0,
        disposal=2,
        optimize=False,
    )

    metadata = {
        "gate": "G3S_COMPLETE_CHARACTER_SPRITESHEET_PLAYABLE_PROOF",
        "status": "PASS_OUTPUT_READY_FOR_PLAYABLE_VISUAL_QA",
        "character": "Exilada",
        "character_state": "initial",
        "reference_master": str(master),
        "complete_character_baked_per_frame": True,
        "runtime_character_layer_assembly": False,
        "secondary_motion_baked_in_frames": True,
        "secondary_motion_scope": [
            "body locomotion",
            "body soft-tissue/jiggle as produced by the temporal authoring model",
            "hair motion",
            "base-clothing motion",
            "bindings/restraints/shackles/chains/accessory motion visible in the master",
        ],
        "note": "This proof intentionally keeps the full master appearance in every authored frame. Equipment/armor variation strategy is a later offline-production decision; runtime layer assembly is not assumed.",
        "source_ssd_result": str(result_marker),
        "source_alignment": str(alignment_marker),
        "sheet": str(sheet_path),
        "preview_gif": str(gif_path),
        "frame_size": [frame_w, frame_h],
        "layout": [columns, rows],
        "frame_count": 8,
        "frame_duration_ms": frame_duration_ms,
        "frames_rgba": rgba_paths,
        "frames": frame_records,
        "background_extraction": extraction,
        "visual_qa_required": True,
        "production_approved": False,
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    print("G3S-COMPLETE-SPRITESHEET: PASS_OUTPUT_READY_FOR_PLAYABLE_VISUAL_QA")
    print(f"SHEET:    {sheet_path}")
    print(f"PREVIEW:  {gif_path}")
    print(f"RGBA:     {rgba_dir}")
    print(f"METADATA: {metadata_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"G3S-COMPLETE-SPRITESHEET: FAIL - {exc}")
        raise SystemExit(1)
