#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SCENE = (640, 360)
BG = (14, 14, 18)
GROUND = (39, 33, 29)
CENTER = (238, 212, 78)
LEFT = (64, 154, 255)
RIGHT = (255, 84, 68)
TEXT = (232, 232, 238)
DIM = (165, 165, 175)


def font():
    return ImageFont.load_default()


def side_color(side: str):
    if side == "left":
        return LEFT
    if side == "right":
        return RIGHT
    return CENTER


def draw_frame(frame: dict, travel_shift: float = 0.0, label_prefix: str = "") -> Image.Image:
    im = Image.new("RGB", SCENE, BG)
    d = ImageDraw.Draw(im)
    joints = frame["joints"]

    def xy(name):
        j = joints[name]
        return (float(j["x"]) + travel_shift, float(j["y"]))

    ground_y = max(
        xy("left_ankle")[1], xy("left_toe")[1],
        xy("right_ankle")[1], xy("right_toe")[1]
    ) + 4
    ground_y = max(40, min(340, int(round(ground_y))))
    d.rectangle((0, ground_y, SCENE[0], SCENE[1]), fill=GROUND)
    d.line((0, ground_y, SCENE[0], ground_y), fill=(88, 77, 67), width=1)

    chains = sorted(frame["chains"], key=lambda row: float(row["mean_depth"]), reverse=True)
    for chain in chains:
        a = xy(chain["a"])
        b = xy(chain["b"])
        color = side_color(chain["anatomical_side"])
        width = 3 if chain["anatomical_side"] == "center" else 4
        d.line((a[0], a[1], b[0], b[1]), fill=color, width=width)

    for name, rec in joints.items():
        x = float(rec["x"]) + travel_shift
        y = float(rec["y"])
        color = side_color(rec.get("anatomical_side", "center"))
        r = 4 if name in ("pelvis", "head") else 3
        d.ellipse((x-r, y-r, x+r, y+r), fill=color)

    support = str(frame["support_foot"])
    ankle = xy(f"{support}_ankle")
    toe = xy(f"{support}_toe")
    for p in (ankle, toe):
        d.ellipse((p[0]-7, p[1]-7, p[0]+7, p[1]+7), outline=(245, 245, 245), width=2)

    title = f"{label_prefix}{frame['event']} | source {frame['frame']} | support {support}"
    d.rectangle((0, 0, SCENE[0], 28), fill=(8, 8, 11))
    d.text((10, 9), title, fill=TEXT, font=font())
    d.text((10, 40), f"near {frame['near_anatomical_side']} / far {frame['far_anatomical_side']}", fill=DIM, font=font())
    return im


def alpha_bbox_like(im: Image.Image):
    pix = im.load()
    xs, ys = [], []
    for y in range(28, im.height):
        for x in range(im.width):
            r, g, b = pix[x, y]
            if (r, g, b) not in (BG, GROUND) and not (r < 100 and g < 90 and b < 80):
                xs.append(x); ys.append(y)
    if not xs:
        return (160, 20, 480, 340)
    return (max(0, min(xs)-18), max(28, min(ys)-18), min(im.width, max(xs)+19), min(im.height, max(ys)+19))


def union_bbox(boxes):
    return (
        min(b[0] for b in boxes), min(b[1] for b in boxes),
        max(b[2] for b in boxes), max(b[3] for b in boxes)
    )


def make_zoom(frames):
    boxes = [alpha_bbox_like(im) for im in frames]
    x0, y0, x1, y1 = union_bbox(boxes)
    w, h = x1-x0, y1-y0
    side = max(w, h, 160)
    cx, cy = (x0+x1)//2, (y0+y1)//2
    x0 = max(0, min(SCENE[0]-side, cx-side//2))
    y0 = max(0, min(SCENE[1]-side, cy-side//2))
    x1, y1 = x0+side, y0+side
    out = []
    for im in frames:
        crop = im.crop((x0, y0, x1, y1))
        out.append(crop.resize((side*2, side*2), Image.Resampling.NEAREST))
    return out


def save_gif(path: Path, frames, duration_ms: int):
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
        optimize=False,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--guide", required=True)
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--body-reference", required=True)
    args = ap.parse_args()

    guide_path = Path(args.guide)
    ws = Path(args.workspace)
    body_ref = Path(args.body_reference)
    if not guide_path.is_file():
        raise FileNotFoundError(guide_path)
    if not body_ref.is_file():
        raise FileNotFoundError(body_ref)
    ws.mkdir(parents=True, exist_ok=True)

    guide = json.loads(guide_path.read_text(encoding="utf-8-sig"))
    if guide.get("gate") != "G3S-C1A" or guide.get("revision") != "SKELETON_ONLY_WALK_CYCLE_V1":
        raise RuntimeError("unexpected C1 skeleton guide")
    if guide.get("skinned_human_mesh_used") is not False or guide.get("mpfb_body_used") is not False:
        raise RuntimeError("skeleton-only contract violated")
    frames_data = guide.get("frames", [])
    if len(frames_data) != 8:
        raise RuntimeError(f"expected 8 skeleton frames, got {len(frames_data)}")
    if float(guide.get("root_travel_total_dx_px", 0.0)) >= 0:
        raise RuntimeError("root travel is not screen-left")

    duration = int(guide.get("frame_duration_ms", 83))
    in_place = [draw_frame(row) for row in frames_data]
    total_dx = float(guide["root_travel_total_dx_px"])
    start_pad = min(100.0, max(36.0, abs(total_dx) * 0.45))
    travel = [draw_frame(row, start_pad + float(row["root_travel_dx_px"]), "TRAVEL | ") for row in frames_data]
    zoom = make_zoom(in_place)

    in_place_path = ws / "g3s_c1_skeleton_walk_in_place.gif"
    travel_path = ws / "g3s_c1_skeleton_walk_travel.gif"
    zoom_path = ws / "g3s_c1_skeleton_walk_zoom.gif"
    save_gif(in_place_path, in_place, duration)
    save_gif(travel_path, travel, duration)
    save_gif(zoom_path, zoom, duration)

    frame_paths = []
    for i, im in enumerate(in_place):
        path = ws / f"g3s_c1_skeleton_walk_{i:02d}_{frames_data[i]['event']}.png"
        im.save(path)
        frame_paths.append(str(path))

    cell_w, cell_h = 480, 270
    sheet = Image.new("RGB", (cell_w*4, cell_h*2 + 150), BG)
    for i, im in enumerate(in_place):
        thumb = im.resize((cell_w, cell_h), Image.Resampling.NEAREST)
        sheet.paste(thumb, ((i % 4)*cell_w, (i // 4)*cell_h))

    body = Image.open(body_ref).convert("RGBA")
    zoom_body = body.resize((body.width*2, body.height*2), Image.Resampling.NEAREST)
    y0 = cell_h*2 + 8
    sheet.paste(zoom_body, (18, y0), zoom_body)
    d = ImageDraw.Draw(sheet)
    d.text((112, y0+12), "B3B V4 = identity/body-style anchor only; NOT warped into these poses.", fill=TEXT, font=font())
    d.text((112, y0+34), "Blue = anatomical left | Red = anatomical right | white rings = support foot.", fill=DIM, font=font())
    d.text((112, y0+56), f"real CMU walk | total projected root travel {total_dx:.2f}px screen-left | {duration}ms/state", fill=DIM, font=font())
    d.text((112, y0+78), "This sheet validates the hidden motion skeleton. Visible anatomy remains native 2D.", fill=DIM, font=font())

    sheet_path = ws / "g3s_c1_skeleton_walk_contact_sheet.png"
    sheet.save(sheet_path)

    guide["review_outputs"] = {
        "frame_pngs": frame_paths,
        "in_place_gif": str(in_place_path),
        "travel_gif": str(travel_path),
        "zoom_gif": str(zoom_path),
        "contact_sheet": str(sheet_path),
    }
    guide_path.write_text(json.dumps(guide, indent=2) + "\n", encoding="utf-8")

    print("G3S-C1A SKELETON WALK REVIEW PACKAGE READY")
    print(f"IN PLACE: {in_place_path}")
    print(f"TRAVEL:   {travel_path}")
    print(f"ZOOM:     {zoom_path}")
    print(f"SHEET:    {sheet_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
