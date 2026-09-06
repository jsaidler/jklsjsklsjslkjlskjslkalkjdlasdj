#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SCENE = (640, 360)
PANEL = (640, 360)
SHEET = (1920, 720)
CROP = (96, 160)

CHAINS = [
    ("head", "neck"),
    ("neck", "chest"),
    ("chest", "pelvis"),
    ("neck", "left_shoulder"),
    ("left_shoulder", "left_elbow"),
    ("left_elbow", "left_wrist"),
    ("neck", "right_shoulder"),
    ("right_shoulder", "right_elbow"),
    ("right_elbow", "right_wrist"),
    ("pelvis", "left_hip"),
    ("left_hip", "left_knee"),
    ("left_knee", "left_ankle"),
    ("left_ankle", "left_toe"),
    ("pelvis", "right_hip"),
    ("right_hip", "right_knee"),
    ("right_knee", "right_ankle"),
    ("right_ankle", "right_toe"),
]


def load_font():
    return ImageFont.load_default()


def panel_base(title: str):
    im = Image.new("RGB", PANEL, (14, 14, 18))
    d = ImageDraw.Draw(im)
    d.text((12, 10), title, fill=(235, 235, 240), font=load_font())
    return im


def identity_panel(body_path: Path):
    panel = panel_base("A CANONICAL B3B STATIC BODY / IDENTITY-STYLE ANCHOR / NOT POSE GUIDE")
    body = Image.open(body_path).convert("RGBA")
    if body.size != (37, 128):
        raise RuntimeError(f"canonical body dimensions changed: {body.size}")
    ground_y = 300
    d = ImageDraw.Draw(panel)
    d.rectangle((0, ground_y, PANEL[0], PANEL[1]), fill=(34, 28, 25))
    native_x = 110
    panel.paste(body, (native_x, ground_y - body.height), body)
    zoom = body.resize((body.width * 3, body.height * 3), Image.Resampling.NEAREST)
    zx = 350
    zy = max(30, ground_y - zoom.height)
    panel.paste(zoom, (zx, zy), zoom)
    d.text((native_x - 18, 316), "native 37x128", fill=(210, 210, 215), font=load_font())
    d.text((zx, 316), "3x inspection", fill=(210, 210, 215), font=load_font())
    return panel


def image_panel(path: Path, title: str):
    src = Image.open(path).convert("RGB")
    if src.size != SCENE:
        raise RuntimeError(f"guide image has wrong raster {src.size}: {path}")
    panel = panel_base(title)
    panel.paste(src, (0, 0))
    d = ImageDraw.Draw(panel)
    d.rectangle((0, 0, 640, 30), fill=(10, 10, 13))
    d.text((12, 10), title, fill=(235, 235, 240), font=load_font())
    return panel


def skeleton_overlay(neutral_path: Path, pose: dict):
    im = Image.open(neutral_path).convert("RGB")
    d = ImageDraw.Draw(im)
    joints = pose["joints"]

    def pt(name):
        j = joints.get(name)
        if not j:
            return None
        return (int(round(float(j["x"]))), int(round(float(j["y"]))))

    for a, b in CHAINS:
        pa, pb = pt(a), pt(b)
        if pa is None or pb is None:
            continue
        if a.startswith("left_") or b.startswith("left_"):
            color = (60, 150, 255)
        elif a.startswith("right_") or b.startswith("right_"):
            color = (255, 80, 65)
        else:
            color = (255, 220, 70)
        d.line((pa, pb), fill=color, width=2)

    for name, rec in joints.items():
        x = int(round(float(rec["x"])))
        y = int(round(float(rec["y"])))
        side = rec.get("anatomical_side")
        color = (60, 150, 255) if side == "left" else (255, 80, 65) if side == "right" else (255, 220, 70)
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=color)

    title = "E SKELETON/LATERALITY OVERLAY / BLUE=ANATOMICAL LEFT / RED=ANATOMICAL RIGHT"
    d.rectangle((0, 0, 640, 30), fill=(10, 10, 13))
    d.text((12, 10), title, fill=(235, 235, 240), font=load_font())
    return im


def bbox_from_silhouette(path: Path):
    im = Image.open(path).convert("RGB")
    pix = im.load()
    xs, ys = [], []
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = pix[x, y]
            if r + g + b > 180:
                xs.append(x)
                ys.append(y)
    if not xs:
        raise RuntimeError("silhouette guide contains no white foreground")
    return (min(xs), min(ys), max(xs) + 1, max(ys) + 1)


def crop_window(bbox):
    x0, y0, x1, y1 = bbox
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    left = cx - CROP[0] // 2
    top = cy - CROP[1] // 2
    left = max(0, min(SCENE[0] - CROP[0], left))
    top = max(0, min(SCENE[1] - CROP[1], top))
    return (left, top, left + CROP[0], top + CROP[1])


def save_crop(src: Image.Image, window, path: Path):
    crop = src.crop(window)
    if crop.size != CROP:
        raise RuntimeError(f"unexpected logical crop size: {crop.size}")
    crop.save(path)


def facts_panel(pose: dict, crop_box):
    panel = panel_base("F C1A CONTRACT / FULL HIDDEN-3D POSE GUIDE / NO FINAL 3D PIXELS")
    d = ImageDraw.Draw(panel)
    lines = [
        f"event: {pose['selected_event']}",
        f"source frame: {pose['selected_source_frame']}",
        f"retarget: {pose['retarget_method']}",
        f"direction family: {pose['direction_family']}",
        f"travel dx: {pose['travel_vector_screen_dx_px']:.3f}px (must be < 0)",
        f"contact foot: {pose['contact_foot']}",
        f"near anatomical side: {pose['near_anatomical_side']}",
        f"far anatomical side: {pose['far_anatomical_side']}",
        f"body height: {pose['camera']['measured_body_height_px']:.2f}px / target {pose['camera']['target_body_height_px']}px",
        f"logical guide crop: {crop_box[0]},{crop_box[1]} -> {crop_box[2]},{crop_box[3]} = 96x160",
        "",
        "LOCK: hidden 3D owns pose/laterality/depth/contact only.",
        "LOCK: these RGB/masks/silhouettes are GUIDE ONLY.",
        "LOCK: do not quantize/crop/promote them as final sprite art.",
        "NEXT AFTER REVIEW: author ONE persistent native-2D contact pose.",
    ]
    y = 50
    for line in lines:
        d.text((22, y), line, fill=(220, 220, 226), font=load_font())
        y += 20
    return panel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--body-reference", required=True)
    args = ap.parse_args()

    ws = Path(args.workspace)
    body_ref = Path(args.body_reference)
    pose_path = ws / "g3s_c1_contact_left_pose_guide.json"
    neutral = ws / "g3s_c1_contact_left_hidden3d_neutral.png"
    silhouette = ws / "g3s_c1_contact_left_silhouette_guide.png"
    regions = ws / "g3s_c1_contact_left_regions_guide.png"
    depth = ws / "g3s_c1_contact_left_depth_guide.png"
    for p in (body_ref, pose_path, neutral, silhouette, regions, depth):
        if not p.is_file():
            raise FileNotFoundError(p)

    pose = json.loads(pose_path.read_text(encoding="utf-8-sig"))
    if pose.get("gate") != "G3S-C1A" or pose.get("status") != "REVIEW_REQUIRED":
        raise RuntimeError("unexpected C1 pose-guide manifest")
    if pose.get("hidden_3d_visible_art_owner") is not False:
        raise RuntimeError("C1 ownership contract is not locked to guide-only")
    if float(pose.get("travel_vector_screen_dx_px", 0.0)) >= 0.0:
        raise RuntimeError("C1 pose guide is not left-facing/left-travel aligned")

    skel = skeleton_overlay(neutral, pose)
    skeleton_path = ws / "g3s_c1_contact_left_skeleton_overlay.png"
    skel.save(skeleton_path)

    bbox = bbox_from_silhouette(silhouette)
    window = crop_window(bbox)

    crop_sources = {
        "neutral": Image.open(neutral).convert("RGB"),
        "silhouette": Image.open(silhouette).convert("RGB"),
        "regions": Image.open(regions).convert("RGB"),
        "depth": Image.open(depth).convert("RGB"),
        "skeleton": skel,
    }
    crop_outputs = {}
    for name, im in crop_sources.items():
        path = ws / f"g3s_c1_contact_left_{name}_crop_96x160.png"
        save_crop(im, window, path)
        crop_outputs[name] = str(path)

    panels = [
        identity_panel(body_ref),
        image_panel(neutral, "B HIDDEN-3D NEUTRAL ANATOMY GUIDE / GUIDE ONLY"),
        image_panel(regions, "C ANATOMICAL REGION GUIDE / LEFT-RIGHT OWNERSHIP EXPLICIT"),
        image_panel(silhouette, "D POSE SILHOUETTE GUIDE / NOT FINAL SPRITE SILHOUETTE"),
        skel,
        facts_panel(pose, window),
    ]
    sheet = Image.new("RGB", SHEET, (12, 12, 15))
    for i, panel in enumerate(panels):
        x = (i % 3) * PANEL[0]
        y = (i // 3) * PANEL[1]
        sheet.paste(panel, (x, y))
    sheet_path = ws / "g3s_c1_contact_left_pose_guide_contact_sheet.png"
    sheet.save(sheet_path)

    pose["review_outputs"] = {
        "skeleton_overlay": str(skeleton_path),
        "logical_crop_box_640x360": list(window),
        "logical_crops_96x160": crop_outputs,
        "contact_sheet": str(sheet_path),
    }
    pose_path.write_text(json.dumps(pose, indent=2) + "\n", encoding="utf-8")

    print("G3S-C1A REVIEW PACKAGE READY")
    print(f"CONTACT SHEET: {sheet_path}")
    print(f"POSE JSON:     {pose_path}")
    print(f"LOGICAL CROP:  {window}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
