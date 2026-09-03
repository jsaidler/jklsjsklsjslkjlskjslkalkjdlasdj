from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

# OpenPose BODY_18 order used by Moore-AnimateAnyone / Sprite-Sheet-Diffusion.
JOINTS = [
    "nose", "neck",
    "r_shoulder", "r_elbow", "r_wrist",
    "l_shoulder", "l_elbow", "l_wrist",
    "r_hip", "r_knee", "r_ankle",
    "l_hip", "l_knee", "l_ankle",
    "r_eye", "l_eye", "r_ear", "l_ear",
]

LIMBS = [
    (1, 2), (1, 5), (2, 3), (3, 4),
    (5, 6), (6, 7), (1, 8), (8, 9),
    (9, 10), (1, 11), (11, 12), (12, 13),
    (1, 0), (0, 14), (14, 16), (0, 15), (15, 17),
]

COLORS = [
    (255, 0, 0), (255, 85, 0), (255, 170, 0), (255, 255, 0),
    (170, 255, 0), (85, 255, 0), (0, 255, 0), (0, 255, 85),
    (0, 255, 170), (0, 255, 255), (0, 170, 255), (0, 85, 255),
    (0, 0, 255), (85, 0, 255), (170, 0, 255), (255, 0, 255),
    (255, 0, 170), (255, 0, 85),
]

# Eight canonical walk poses. The first is the contact pose and is repeated
# three times by default so the motion module sees its native 24-frame window.
# Coordinates are normalized to the generation canvas and deliberately omit
# face/hand detail: the C++ port's RTX-3060 notes report better identity this way.
FRAMES = [
    # contact A
    {"bob": 0.000, "r_knee": (0.585, 0.700), "r_ankle": (0.660, 0.900),
     "l_knee": (0.435, 0.720), "l_ankle": (0.345, 0.895),
     "r_elbow": (0.455, 0.405), "r_wrist": (0.420, 0.535),
     "l_elbow": (0.585, 0.405), "l_wrist": (0.625, 0.515)},
    # down A
    {"bob": 0.020, "r_knee": (0.575, 0.725), "r_ankle": (0.625, 0.900),
     "l_knee": (0.455, 0.735), "l_ankle": (0.375, 0.895),
     "r_elbow": (0.465, 0.420), "r_wrist": (0.435, 0.545),
     "l_elbow": (0.575, 0.420), "l_wrist": (0.610, 0.530)},
    # passing A
    {"bob": 0.005, "r_knee": (0.545, 0.705), "r_ankle": (0.555, 0.895),
     "l_knee": (0.475, 0.655), "l_ankle": (0.505, 0.805),
     "r_elbow": (0.485, 0.420), "r_wrist": (0.470, 0.535),
     "l_elbow": (0.555, 0.405), "l_wrist": (0.585, 0.505)},
    # up A
    {"bob": -0.015, "r_knee": (0.520, 0.700), "r_ankle": (0.505, 0.895),
     "l_knee": (0.505, 0.625), "l_ankle": (0.555, 0.770),
     "r_elbow": (0.520, 0.405), "r_wrist": (0.535, 0.510),
     "l_elbow": (0.525, 0.405), "l_wrist": (0.545, 0.500)},
    # contact B
    {"bob": 0.000, "r_knee": (0.435, 0.720), "r_ankle": (0.345, 0.895),
     "l_knee": (0.585, 0.700), "l_ankle": (0.660, 0.900),
     "r_elbow": (0.585, 0.405), "r_wrist": (0.625, 0.515),
     "l_elbow": (0.455, 0.405), "l_wrist": (0.420, 0.535)},
    # down B
    {"bob": 0.020, "r_knee": (0.455, 0.735), "r_ankle": (0.375, 0.895),
     "l_knee": (0.575, 0.725), "l_ankle": (0.625, 0.900),
     "r_elbow": (0.575, 0.420), "r_wrist": (0.610, 0.530),
     "l_elbow": (0.465, 0.420), "l_wrist": (0.435, 0.545)},
    # passing B
    {"bob": 0.005, "r_knee": (0.475, 0.655), "r_ankle": (0.505, 0.805),
     "l_knee": (0.545, 0.705), "l_ankle": (0.555, 0.895),
     "r_elbow": (0.555, 0.405), "r_wrist": (0.585, 0.505),
     "l_elbow": (0.485, 0.420), "l_wrist": (0.470, 0.535)},
    # up B
    {"bob": -0.015, "r_knee": (0.505, 0.625), "r_ankle": (0.555, 0.770),
     "l_knee": (0.520, 0.700), "l_ankle": (0.505, 0.895),
     "r_elbow": (0.525, 0.405), "r_wrist": (0.545, 0.500),
     "l_elbow": (0.520, 0.405), "l_wrist": (0.535, 0.510)},
]


def skeleton(frame: dict[str, object]) -> list[tuple[float, float] | None]:
    bob = float(frame["bob"])
    pts: dict[str, tuple[float, float] | None] = {
        "nose": (0.555, 0.145 + bob),
        "neck": (0.520, 0.245 + bob),
        "r_shoulder": (0.485, 0.285 + bob),
        "l_shoulder": (0.545, 0.285 + bob),
        "r_hip": (0.495, 0.525 + bob),
        "l_hip": (0.545, 0.525 + bob),
        # No face landmarks: intentionally None for stylized character stability.
        "r_eye": None, "l_eye": None, "r_ear": None, "l_ear": None,
    }
    for key in ("r_elbow", "r_wrist", "l_elbow", "l_wrist",
                "r_knee", "r_ankle", "l_knee", "l_ankle"):
        x, y = frame[key]  # type: ignore[misc]
        pts[key] = (float(x), float(y) + bob)
    return [pts[name] for name in JOINTS]


def draw_pose(points: list[tuple[float, float] | None], width: int, height: int) -> Image.Image:
    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    stick = max(2, round(4 * width / 512))
    radius = max(2, round(4 * width / 512))

    # SSD/Moore draw limbs at 60% of the joint color, then full-color joints.
    for (a, b), color in zip(LIMBS, COLORS):
        p1, p2 = points[a], points[b]
        if p1 is None or p2 is None:
            continue
        xy = [(round(p1[0] * width), round(p1[1] * height)),
              (round(p2[0] * width), round(p2[1] * height))]
        limb_color = tuple(round(c * 0.6) for c in color)
        draw.line(xy, fill=limb_color, width=stick * 2, joint="curve")

    for point, color in zip(points, COLORS):
        if point is None:
            continue
        x, y = round(point[0] * width), round(point[1] * height)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    return img


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "poses" / "walk")
    ap.add_argument("--width", type=int, default=512)
    ap.add_argument("--height", type=int, default=768)
    ap.add_argument("--cycles", type=int, default=3, help="3 cycles = 24 frames, native motion-module window")
    args = ap.parse_args()
    if args.width % 8 or args.height % 8:
        raise SystemExit("width and height must be multiples of 8")
    if args.cycles < 1:
        raise SystemExit("cycles must be >= 1")

    args.output.mkdir(parents=True, exist_ok=True)
    for old in args.output.glob("*.png"):
        old.unlink()

    metadata = []
    idx = 0
    for cycle in range(args.cycles):
        for local, frame in enumerate(FRAMES):
            pts = skeleton(frame)
            filename = f"{idx:02d}.png"
            draw_pose(pts, args.width, args.height).save(args.output / filename)
            metadata.append({"frame": idx, "cycle": cycle, "walk_frame": local,
                             "pose": filename, "keypoints": pts})
            idx += 1

    (args.output / "poses.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Wrote {idx} pose frames to {args.output}")


if __name__ == "__main__":
    main()
