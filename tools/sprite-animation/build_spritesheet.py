from __future__ import annotations

import argparse
import json
from pathlib import Path
from PIL import Image


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract one stable 8-frame cycle from an animated WebP and pack it.")
    ap.add_argument("input", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--cycle", type=int, default=1, choices=(0, 1, 2), help="Use middle cycle by default")
    ap.add_argument("--frames-per-cycle", type=int, default=8)
    args = ap.parse_args()

    im = Image.open(args.input)
    frames = []
    i = 0
    while True:
        try:
            im.seek(i)
        except EOFError:
            break
        frames.append(im.convert("RGBA").copy())
        i += 1

    start = args.cycle * args.frames_per_cycle
    end = start + args.frames_per_cycle
    if len(frames) < end:
        raise SystemExit(f"Need at least {end} frames, got {len(frames)}")
    selected = frames[start:end]

    w = max(f.width for f in selected)
    h = max(f.height for f in selected)
    sheet = Image.new("RGBA", (w * len(selected), h), (0, 0, 0, 0))
    for j, frame in enumerate(selected):
        sheet.alpha_composite(frame, (j * w, 0))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output)
    manifest = {
        "source": str(args.input),
        "frame_count": len(selected),
        "frame_width": w,
        "frame_height": h,
        "columns": len(selected),
        "rows": 1,
        "fps": 8,
        "cycle_source": args.cycle,
        "anchor": {"x": w // 2, "y": h - 1},
    }
    args.output.with_suffix(".json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {args.output} and manifest")


if __name__ == "__main__":
    main()
