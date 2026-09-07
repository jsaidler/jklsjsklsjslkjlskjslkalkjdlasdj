#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

CANVAS_W = 384
CANVAS_H = 576
FPS = 16
FRAME_COUNT = 17
PLAYABLE_COUNT = 16
BG = (82, 78, 76)
SKIN = (148, 88, 58)
SKIN_DARK = (104, 59, 42)
HAIR = (18, 17, 18)
HAIR_HI = (35, 31, 31)
CLOTH = (159, 143, 115)
CLOTH_DARK = (111, 96, 76)
METAL = (61, 65, 66)
OUTLINE = (31, 27, 25)


def fail(msg: str) -> None:
    raise RuntimeError(msg)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def interp_joint(a: dict, b: dict, t: float) -> dict:
    return {"x": lerp(float(a["x"]), float(b["x"]), t), "y": lerp(float(a["y"]), float(b["y"]), t)}


def sample_cycle(frames: list[dict], sample_index: int) -> tuple[dict[str, dict], float]:
    # 16 evenly spaced samples across the 8-state loop: 0, 0.5, ... 7.5.
    phase = (sample_index % PLAYABLE_COUNT) * (len(frames) / PLAYABLE_COUNT)
    i0 = int(math.floor(phase)) % len(frames)
    i1 = (i0 + 1) % len(frames)
    t = phase - math.floor(phase)
    names = frames[i0]["joints"].keys()
    joints = {name: interp_joint(frames[i0]["joints"][name], frames[i1]["joints"][name], t) for name in names}
    return joints, phase


def map_pose(joints: dict[str, dict], scale: float, ground_y: float = 526.0) -> dict[str, tuple[float, float]]:
    lx, ly = float(joints["left_hip"]["x"]), float(joints["left_hip"]["y"])
    rx, ry = float(joints["right_hip"]["x"]), float(joints["right_hip"]["y"])
    pelvis_x = (lx + rx) * 0.5
    foot_y = max(float(joints["left_ankle"]["y"]), float(joints["right_ankle"]["y"]))
    out = {}
    for name, rec in joints.items():
        out[name] = (192.0 + (float(rec["x"]) - pelvis_x) * scale, ground_y + (float(rec["y"]) - foot_y) * scale)
    return out


def circle(draw: ImageDraw.ImageDraw, p: tuple[float, float], r: float, fill, outline=OUTLINE, width: int = 2) -> None:
    x, y = p
    draw.ellipse((x-r, y-r, x+r, y+r), fill=fill, outline=outline, width=width)


def thick_line(draw: ImageDraw.ImageDraw, pts: list[tuple[float, float]], fill, width: int) -> None:
    draw.line(pts, fill=OUTLINE, width=width+5, joint="curve")
    draw.line(pts, fill=fill, width=width, joint="curve")


def draw_chain(draw: ImageDraw.ImageDraw, anchor: tuple[float, float], phase: float, length: float, links: int, direction: float, lag: float) -> None:
    ax, ay = anchor
    prev = (ax, ay)
    for i in range(1, links + 1):
        u = i / links
        angle = direction + 0.22 * math.sin(phase * math.pi * 2 / 8 + i * 0.55) + lag * u
        x = ax + math.cos(angle) * length * u
        y = ay + math.sin(angle) * length * u + 4.0 * math.sin(i * 0.9 + phase)
        draw.line((prev, (x, y)), fill=OUTLINE, width=7)
        draw.line((prev, (x, y)), fill=METAL, width=3)
        circle(draw, (x, y), 4.0, METAL, outline=OUTLINE, width=2)
        prev = (x, y)


def draw_proxy(mapped: dict[str, tuple[float, float]], phase: float, frame_index: int) -> Image.Image:
    im = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
    draw = ImageDraw.Draw(im)

    # Deterministic secondary-motion phase. Character travels screen-left, so loose
    # masses lag screen-right. The driver is intentionally stylized and is motion
    # control only; it is never exported as visible game art.
    theta = 2.0 * math.pi * (frame_index % PLAYABLE_COUNT) / PLAYABLE_COUNT
    lag_x = 12.0 * math.sin(theta - 0.7)
    lag_y = 5.0 * math.sin(theta * 2.0 - 0.25)
    cloth_lag = 10.0 * math.sin(theta - 1.0)
    chest_jiggle = 3.0 * math.sin(theta * 2.0 - 0.9)

    head = mapped["head"]
    neck = mapped["neck"]
    ls, rs = mapped["left_shoulder"], mapped["right_shoulder"]
    lh, rh = mapped["left_hip"], mapped["right_hip"]
    pelvis = ((lh[0] + rh[0]) * 0.5, (lh[1] + rh[1]) * 0.5)

    # Rear hair mass: large, persistent, delayed relative to head/torso.
    hx, hy = head
    hair_poly = [
        (hx - 54 + lag_x * 0.4, hy - 19),
        (hx + 48 + lag_x * 0.2, hy - 14),
        (max(ls[0], rs[0]) + 45 + lag_x * 0.8, neck[1] + 60),
        (pelvis[0] + 44 + lag_x, pelvis[1] + 110 + lag_y),
        (pelvis[0] - 32 + lag_x * 0.7, pelvis[1] + 125 + lag_y),
        (min(ls[0], rs[0]) - 44 + lag_x * 0.5, neck[1] + 78),
    ]
    draw.polygon(hair_poly, fill=HAIR, outline=OUTLINE)
    for k in range(7):
        side = -1 if k % 2 == 0 else 1
        sx = hx + side * (20 + (k % 3) * 9)
        sy = hy + 8 + k * 5
        ex = pelvis[0] + side * (26 + k * 3) + lag_x * (0.6 + 0.08 * k)
        ey = pelvis[1] + 88 + k * 7 + lag_y
        draw.line((sx, sy, ex, ey), fill=HAIR_HI, width=8)

    # Body core.
    torso = [
        (ls[0], ls[1]), (rs[0], rs[1]),
        (rh[0] + 8, rh[1]), (lh[0] - 8, lh[1]),
    ]
    draw.polygon(torso, fill=SKIN, outline=OUTLINE)
    circle(draw, head, 22, SKIN)
    thick_line(draw, [neck, head], SKIN, 18)

    for side in ("left", "right"):
        shoulder = mapped[f"{side}_shoulder"]
        elbow = mapped[f"{side}_elbow"]
        wrist = mapped[f"{side}_wrist"]
        thick_line(draw, [shoulder, elbow, wrist], SKIN, 20)
        circle(draw, elbow, 10, SKIN)
        circle(draw, wrist, 9, SKIN)

        hip = mapped[f"{side}_hip"]
        knee = mapped[f"{side}_knee"]
        ankle = mapped[f"{side}_ankle"]
        toe = mapped[f"{side}_toe"]
        thick_line(draw, [hip, knee, ankle], SKIN, 29)
        circle(draw, knee, 14, SKIN)
        circle(draw, ankle, 11, SKIN)
        thick_line(draw, [ankle, toe], SKIN, 16)

    # Chest binding with a tiny delayed soft-tissue response.
    chest_y = (ls[1] + rs[1]) * 0.5 + 28 + chest_jiggle
    x0, x1 = sorted([ls[0], rs[0]])
    draw.rounded_rectangle((x0-10, chest_y-13, x1+12, chest_y+14), radius=7, fill=CLOTH, outline=OUTLINE, width=3)

    # Hip wrap and hanging strips. These visibly lag the pelvis to give Wan a
    # complete-silhouette motion signal instead of body-pose-only control.
    px, py = pelvis
    wrap = [
        (lh[0]-15, lh[1]-5), (rh[0]+17, rh[1]-3),
        (rh[0]+26+cloth_lag*0.35, py+65),
        (px+cloth_lag, py+112+lag_y),
        (lh[0]-25+cloth_lag*0.25, py+67),
    ]
    draw.polygon(wrap, fill=CLOTH, outline=OUTLINE)
    for off, length in [(-35, 88), (-14, 116), (8, 104), (28, 82)]:
        top = (px + off, py + 46)
        tip = (px + off + cloth_lag * (0.65 + abs(off)/100.0), py + length + 18 + lag_y)
        draw.polygon([(top[0]-9, top[1]), (top[0]+9, top[1]), (tip[0]+5, tip[1]), (tip[0]-5, tip[1])], fill=CLOTH_DARK, outline=OUTLINE)

    # Front hair strands cross the shoulders/torso with slightly less lag.
    for side in (-1, 1):
        sx = hx + side * 18
        sy = hy + 12
        ex = px + side * 33 + lag_x * 0.45
        ey = py + 46 + lag_y * 0.35
        draw.line((sx, sy, ex, ey), fill=OUTLINE, width=13)
        draw.line((sx, sy, ex, ey), fill=HAIR, width=9)

    # Shackles and explicit broken chains. Initial-state ownership is kept on the
    # left wrist and left ankle in this proxy test.
    lw = mapped["left_wrist"]
    la = mapped["left_ankle"]
    circle(draw, lw, 13, METAL, outline=OUTLINE, width=4)
    circle(draw, la, 15, METAL, outline=OUTLINE, width=4)
    draw_chain(draw, lw, phase, length=78, links=6, direction=1.74, lag=0.18*math.sin(theta-0.6))
    draw_chain(draw, la, phase, length=88, links=7, direction=2.90, lag=0.24*math.sin(theta-0.9))

    return im


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--guide", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    guide_path = Path(args.guide).resolve()
    out_root = Path(args.output).resolve()
    if not guide_path.is_file():
        fail(f"guide missing: {guide_path}")
    guide = read_json(guide_path)
    frames = guide.get("frames", [])
    if len(frames) != 8:
        fail(f"expected eight source gait states, got {len(frames)}")
    if abs(float(guide.get("camera", {}).get("azimuth_from_motion_heading_deg", -1)) - 72.0) > 0.01:
        fail("complete-motion driver requires the locked 72-degree guide")

    all_y = []
    for frame in frames:
        for name in ("head", "left_ankle", "right_ankle"):
            all_y.append(float(frame["joints"][name]["y"]))
    raw_height = max(all_y) - min(all_y)
    if raw_height <= 1:
        fail("invalid projected source height")
    scale = 438.0 / raw_height

    frames_dir = out_root / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    records = []
    proxy_frames = []
    for i in range(PLAYABLE_COUNT):
        joints, phase = sample_cycle(frames, i)
        mapped = map_pose(joints, scale)
        image = draw_proxy(mapped, phase, i)
        path = frames_dir / f"frame_{i:03d}.png"
        image.save(path)
        proxy_frames.append(image)
        records.append({"index": i, "phase": phase, "path": str(path)})

    # 17th frame duplicates the start so the driving clip carries an explicit
    # closure target. It is not part of the exported 16-frame spritesheet.
    closing_path = frames_dir / "frame_016.png"
    proxy_frames[0].save(closing_path)
    records.append({"index": 16, "phase": 8.0, "path": str(closing_path), "closure_duplicate": True})

    sheet = Image.new("RGB", (CANVAS_W * 5, CANVAS_H * 4), BG)
    for i, im in enumerate(proxy_frames + [proxy_frames[0]]):
        sheet.paste(im, ((i % 5) * CANVAS_W, (i // 5) * CANVAS_H))
    sheet_path = out_root / "complete_motion_driver_contact_sheet.png"
    sheet.save(sheet_path)

    gif_path = out_root / "complete_motion_driver_preview.gif"
    seq = proxy_frames + [proxy_frames[0]]
    seq[0].save(gif_path, save_all=True, append_images=seq[1:], duration=round(1000/FPS), loop=0, disposal=2, optimize=False)

    marker = {
        "gate": "G3S_COMPLETE_MOTION_DRIVER_V1",
        "status": "PASS_DRIVER_FRAMES_READY",
        "source_guide": str(guide_path),
        "canvas": [CANVAS_W, CANVAS_H],
        "fps": FPS,
        "frame_count": FRAME_COUNT,
        "playable_frame_count": PLAYABLE_COUNT,
        "closing_frame_duplicates_first": True,
        "driver_only_not_game_art": True,
        "secondary_motion_controls": ["rear/front hair lag", "hip-wrap cloth lag", "chest soft lag", "left wrist broken chain", "left ankle broken chain"],
        "frames": records,
        "contact_sheet": str(sheet_path),
        "preview_gif": str(gif_path),
    }
    marker_path = out_root / "complete_motion_driver.json"
    marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")

    print("G3S-COMPLETE-MOTION-DRIVER: PASS_DRIVER_FRAMES_READY")
    print(f"FRAMES: {frames_dir}")
    print(f"SHEET:  {sheet_path}")
    print(f"GIF:    {gif_path}")
    print(f"MARKER: {marker_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"G3S-COMPLETE-MOTION-DRIVER: FAIL - {exc}")
        raise SystemExit(1)
