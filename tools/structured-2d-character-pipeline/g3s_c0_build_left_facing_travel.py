#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageDraw

SCENE = (640, 360)
GROUND_Y = 286


def scene_frame(logical: Image.Image, x_center: float) -> Image.Image:
    scene = Image.new("RGBA", SCENE, (18, 18, 21, 255))
    draw = ImageDraw.Draw(scene)
    draw.rectangle((0, GROUND_Y, SCENE[0], SCENE[1]), fill=(38, 31, 27, 255))
    bbox = logical.getchannel("A").getbbox()
    if bbox is None:
        raise RuntimeError("empty animated logical frame")
    crop = logical.crop(bbox)
    x = int(round(x_center - crop.width / 2))
    y = GROUND_Y - crop.height
    scene.alpha_composite(crop, (x, y))
    return scene


def save_gif(frames, path: Path, duration_ms: int = 83) -> None:
    pal = [
        f.convert("RGB").quantize(
            colors=256,
            method=Image.Quantize.FASTOCTREE,
            dither=Image.Dither.NONE,
        )
        for f in frames
    ]
    pal[0].save(
        path,
        save_all=True,
        append_images=pal[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
        optimize=False,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True)
    args = ap.parse_args()

    workspace = Path(args.workspace)
    logical_frames = []
    for i in range(8):
        p = workspace / f"g3s_c0_v2_body_frame_{i:02d}.png"
        if not p.is_file():
            raise FileNotFoundError(f"missing V2 logical frame: {p}")
        logical_frames.append(Image.open(p).convert("RGBA"))

    # Canonical B3B source faces screen-left. Travel must agree with visible facing.
    # Start on the right and move left; do not mirror the sprite or reverse gait phase order.
    start_x = 390.0
    end_x = 250.0
    travel = [
        scene_frame(lf, start_x + i * ((end_x - start_x) / 7.0))
        for i, lf in enumerate(logical_frames)
    ]

    out = workspace / "g3s_c0_v2_body_walk_travel.gif"
    save_gif(travel, out)
    print("G3S-C0 V2 travel direction corrected: canonical left-facing body now travels left")
    print(f"TRAVEL: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
